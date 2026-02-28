import time, random, math, threading
from pyo import *
import launchpad_py as launchpad

"""
Stochastic Field: Launchpad Interface Mapping
===========================================================

--- TOP CONTROL BUTTONS ---
[0] Key Down       : Decrements global root note (C, C#, etc.)
[1] Key Up         : Increments global root note
[2] Scale Down     : Cycles backward through the SCALES_DICT
[3] Scale Up       : Cycles forward through the SCALES_DICT
[4] Reverb Mode    : Cycles through Small Room, Medium Hall, and Large Hall
[5] Migration      : Toggles random agent displacement (Active units jump to empty slots)
[6] Vol Down       : Decrements master fader gain by 0.05
[7] Vol Up         : Increments master fader gain by 0.05

--- SIDE CONTROL BUTTONS ---
[0] Panic Reset   : Fades master out, clears all active agents, then restores volume
[1] Delay Cycle    : Cycles delay timings: OFF -> 1/4 -> 1/8 -> 1/16
[2] Chorus Cycle   : Cycles chorus settings: OFF -> SUBTLE -> MOD -> DEEP
[3] Next Sound     : Cycles to the next FM Synth Profile (e.g., Glass Pluck, Bamboo FM)
[4] Prev Sound     : Cycles to the previous FM Synth Profile
[5] System Off     : Initiates a 4-second fade out and shuts down the server

--- 8x8 GRID ---
- Interaction      : Toggle action. Press to activate a Cell Agent; press again to deactivate
- Panning          : X/Y position calculates gain across 4 output channels (Quadraphonic)
- Tuning/Speed     : Position determines octave offset, scale note, and playback frequency
- Visuals          : Dim color = Ready; Bright color = Triggering; Red = Scale Root
"""

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio' 
BUFFER_SIZE = 512 

# --- 1. Launchpad Setup ---
mode = None
lp = launchpad.Launchpad()
if lp.Check(0, "Mini"):
    lp.Open(); mode = "Mk1"
    TOP_BTNS = [200, 201, 202, 203, 204, 205, 206, 207]
    SIDE_BTNS = [8, 24, 40, 56, 72, 88, 104, 120]
    SIDE_POWER_BTN = 104 
    VOL_BTNS = [206, 207] 
    SIDE_DELAY_BTN = 24  
    SIDE_CHORUS_BTN = 40 
    SIDE_NEXT_SOUND = 72; SIDE_PREV_SOUND = 88
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(); mode = "Mk2"
    TOP_BTNS = [104, 105, 106, 107, 108, 109, 110, 111]
    SIDE_BTNS = [89, 79, 69, 59, 49, 39, 29, 19]
    SIDE_POWER_BTN = 29 
    VOL_BTNS = [110, 111] 
    SIDE_DELAY_BTN = 79  
    SIDE_CHORUS_BTN = 69 
    SIDE_NEXT_SOUND = 49; SIDE_PREV_SOUND = 39
else:
    exit("Launchpad not detected.")
lp.Reset()

# --- 2. Audio Setup ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE,winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()


# --- 3. Global State ---
running = True
is_fading_out = False
reverb_mode = 0 
sound_profile_idx = 0
migration_active = False 
last_migration_tick = 0
BPM = 120
BEAT_TIME = (60.0 / BPM) * 16.0 

# FX State
delay_times = [0.0, 60.0/BPM, 30.0/BPM, 15.0/BPM]
delay_cycle_idx = 0
chorus_cycle_idx = 0 
chorus_settings = [{"depth":0, "fb":0}, {"depth":1, "fb":0.1}, {"depth":3, "fb":0.3}, {"depth":5, "fb":0.5}]
fx_colors = [(0,0), (0,63), (63,63), (63,0)] # Off, Blue, Cyan, Red

# --- 4. Profiles & Scales ---
SOUND_PROFILES = [
    {"name": "V7.4 Pulse", "bell": (3.5, 12), "mid": (1.0, 1.5), "bass": (1.0, 0.8)},
    {"name": "Glass Pluck", "bell": (7.1, 5), "mid": (2.0, 1.2), "bass": (1.0, 0.5)},
    {"name": "Digital Marimba", "bell": (1.618, 2), "mid": (1.0, 0.5), "bass": (0.5, 1)},
    {"name": "Crystal Tine", "bell": (11.0, 8), "mid": (4.0, 2.0), "bass": (2.0, 1.0)},
    {"name": "Bamboo FM", "bell": (5.0, 1.5), "mid": (2.0, 0.8), "bass": (0.5, 2)},
    {"name": "Sine Perc", "bell": (1.0, 0.2), "mid": (1.0, 0.1), "bass": (1.0, 0.05)},
    {"name": "Bells in Rain", "bell": (13.5, 10), "mid": (2.1, 3), "bass": (1.0, 1.5)},
    {"name": "Woody FM", "bell": (2.12, 4), "mid": (1.5, 2.5), "bass": (0.7, 5)},
    {"name": "Tiny Prisms", "bell": (9.0, 15), "mid": (3.0, 4), "bass": (1.0, 2)}
]

SCALES_DICT = {
    "Chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Harmonic Series": [0, 3.86, 7.02, 9.69, 12, 14.04, 15.86, 17.51, 19.02, 20.41, 21.69, 22.88, 24],
    "Partch Otonality": [0, 2.04, 3.86, 4.98, 7.02, 8.84, 10.88, 12, 14.04, 15.86, 16.98, 19.02, 20.84, 22.88, 24, 26],
    "Partch Utonality": [0, 1.12, 3.16, 4.98, 7.02, 8.14, 9.96, 12, 13.12, 15.16, 16.98, 19.02, 20.14, 21.96, 24, 25.12],
    "Major": [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26],
    "Minor": [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24, 26],
}
SCALE_NAMES = list(SCALES_DICT.keys())
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
target_scale_idx, root_note = 0, 0

COLOR_MAP_BRIGHT = {"Chromatic": (63,63) if mode=="Mk2" else (3,3), "Harmonic Series": (63,15) if mode=="Mk2" else (3,1), "Partch Otonality": (0,63) if mode=="Mk2" else (0,3), "Partch Utonality": (40,63) if mode=="Mk2" else (2,3), "Major": (63,40) if mode=="Mk2" else (3,2), "Minor": (20,20) if mode=="Mk2" else (1,1)}
COLOR_MAP_DIM = {k: (max(1, v[0]//6), max(1, v[1]//6)) for k, v in COLOR_MAP_BRIGHT.items()}
COLOR_ROOT_BRIGHT, COLOR_ROOT_DIM = ((63,0), (12,0)) if mode=="Mk2" else ((3,0), (1,0))

rev_inputs = [Sig(0) for _ in range(4)]
delays = [Delay(rev_inputs[i], delay=0.1, feedback=0.35, mul=0.5) for i in range(4)]
chorus_inputs = [delays[i] + (rev_inputs[i] * 0.5) for i in range(4)]
choruses = [Chorus(chorus_inputs[i], depth=0, feedback=0, bal=0.5) for i in range(4)]
reverbs = [Freeverb(choruses[i], size=0.2, damp=0.1, bal=1.0).out(i) for i in range(4)]

master_fader = Fader(fadein=4.0, fadeout=4.0, dur=0, mul=0.6).play()
master_port = Port(master_fader, 0.1, 0.1)

# --- 5. Helpers ---
def get_quadrant_info(x, y):
    if y < 3: octv = 1.5 if x < 4 else 0.5
    elif 3 <= y <= 4: octv = 0.5 if x < 4 else -0.5
    else: octv = -1.0 if x < 4 else -1.5
    speed = 1.0 + (3.0 * (1.0 - (math.sqrt((x%4 - 1.5)**2 + (y%4 - 1.5)**2) / 2.12)))
    return octv, (x < 4), speed, (x%4) + ((y%4)*4)

def lp_led_raw(bid, r, g):
    try:
        if mode == "Mk2": lp.LedCtrlRaw(bid, int(r), int(g), 0)
        else: lp.LedCtrlRaw(bid, int(r), int(g))
    except: pass

def lp_led_grid(x, y, r, g):
    bid = (7-y)*10+x+11 if mode=="Mk2" else y*16+x
    lp_led_raw(bid, r, g)

def get_xy_from_raw(bid):
    if mode == "Mk1":
        x, y = bid % 16, bid // 16
        if x < 8 and y < 8: return x, y
    else:
        r, c = bid // 10, bid % 10
        if 1 <= r <= 8 and 1 <= c <= 8: return c-1, 8 - r
    return None

def update_ui():
    for i in range(4): 
        color = (0,20) if i%2==0 else (0,63)
        lp_led_raw(TOP_BTNS[i], color[0], color[1])

    if reverb_mode == 0: lp_led_raw(TOP_BTNS[4], 0, 63) if mode=="Mk2" else lp_led_raw(TOP_BTNS[4], 0, 3)
    elif reverb_mode == 1: lp_led_raw(TOP_BTNS[4], 63, 63) if mode=="Mk2" else lp_led_raw(TOP_BTNS[4], 3, 3)
    else: lp_led_raw(TOP_BTNS[4], 63, 0) if mode=="Mk2" else lp_led_raw(TOP_BTNS[4], 3, 0)

    lp_led_raw(TOP_BTNS[5], 63, 63) if migration_active else lp_led_raw(TOP_BTNS[5], 0, 0)
    
    vol = master_fader.mul
    v_col = (0,63) if vol < 0.4 else ((63,63) if vol < 0.7 else (30,0))
    for b in VOL_BTNS: lp_led_raw(b, v_col[0], v_col[1])

    # Side Button LEDs (Delay & Chorus)
    lp_led_raw(SIDE_DELAY_BTN, fx_colors[delay_cycle_idx][0], fx_colors[delay_cycle_idx][1])
    lp_led_raw(SIDE_CHORUS_BTN, fx_colors[chorus_cycle_idx][0], fx_colors[chorus_cycle_idx][1])

    lp_led_raw(SIDE_BTNS[0], 0, 63); lp_led_raw(SIDE_POWER_BTN, 0, 63)
    lp_led_raw(SIDE_NEXT_SOUND, 0, 63); lp_led_raw(SIDE_PREV_SOUND, 0, 63)

def update_reverb_settings():
    for rv in reverbs:
        if reverb_mode == 0: rv.size = 0.2; rv.damp = 0.1
        elif reverb_mode == 1: rv.size = 0.6; rv.damp = 0.4
        else: rv.size = 0.95; rv.damp = 0.8
    modes = ["Small room", "Medium hall", "Large hall"]
    print(f"REVERB: {modes[reverb_mode]}")

# --- 6. Agent Logic ---
class CellAgent:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = False
        self.last_tick = 0
        self.assigned_prof_idx = 0
        self.assigned_scale_idx = 0
        self.assigned_root = 0
        self.current_div = 1
        self.env = Adsr(attack=0.005, decay=0.15, sustain=0, release=0.1, mul=0.4)
        self.mod_env = Adsr(attack=0.002, decay=0.1, sustain=0, release=0.05)
        self.car = None
        self.qid = (0 if x < 4 and y < 4 else (1 if x >= 4 and y < 4 else (2 if x < 4 and y >= 4 else 3)))
        self.octave_off, self.is_even, self.speed_mult, self.note_idx = get_quadrant_info(x, y)

    def activate(self, force_interval=None):
        self.active = True
        self.assigned_prof_idx = sound_profile_idx
        self.assigned_scale_idx = target_scale_idx
        self.assigned_root = root_note
        base_div = force_interval if force_interval else (random.choice([1,2,4]) if self.is_even else random.choice([1,3,5]))
        self.current_div = base_div
        self.interval = (BEAT_TIME / base_div) / self.speed_mult
        self.apply_tuning()
        self.refresh_led()

    def refresh_led(self):
        if not self.active: return
        s_name = SCALE_NAMES[self.assigned_scale_idx]
        is_root = (SCALES_DICT[s_name][self.note_idx % len(SCALES_DICT[s_name])] == 0)
        lp_led_grid(self.x, self.y, *(COLOR_ROOT_DIM if is_root else COLOR_MAP_DIM[s_name]))

    def apply_tuning(self, source="Manual"):
        scale_list = SCALES_DICT[SCALE_NAMES[self.assigned_scale_idx]]
        freq = 220 * (2**((scale_list[self.note_idx % len(scale_list)] + self.assigned_root + (self.octave_off * 12))/12.0))
        prof = SOUND_PROFILES[self.assigned_prof_idx]
        ratio, index = prof["bell"] if self.octave_off >= 1.0 else (prof["bass"] if self.octave_off <= -1.0 else prof["mid"])
        if self.car: self.car.stop()
        self.mod = Sine(freq=freq * ratio, mul=self.mod_env * index * freq)
        self.car = Sine(freq=freq + self.mod, mul=self.env)
        nx, ny = self.x/7.0, self.y/7.0
        gains = [(1-nx)*(1-ny), nx*(1-ny), (1-nx)*ny, nx*ny]
        for i in range(4): (self.car * gains[i] * master_port).out(i)
        rev_inputs[self.qid].value = self.car * 0.2 * master_port

    def deactivate(self):
        self.active = False
        rev_inputs[self.qid].value = 0
        if self.car: self.car.stop()
        lp_led_grid(self.x, self.y, 0, 0)

    def update(self, now):
        if not self.active: return
        if now - self.last_tick >= self.interval:
            self.last_tick = now
            self.env.play(); self.mod_env.play()
            s_name = SCALE_NAMES[self.assigned_scale_idx]
            is_root = (SCALES_DICT[s_name][self.note_idx % len(SCALES_DICT[s_name])] == 0)
            color_b = COLOR_ROOT_BRIGHT if is_root else COLOR_MAP_BRIGHT[s_name]
            lp_led_grid(self.x, self.y, color_b[0], color_b[1])
            threading.Timer(0.1, self.refresh_led).start()

agents = [CellAgent(x, y) for y in range(8) for x in range(8)]
last_scale_transition = 0

# --- 7. Main Loop ---
update_ui()
try:
    print("--- SERVER STARTED ---")
    while running:
        current_time = time.time()
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            if bid == SIDE_POWER_BTN and state > 0:
                print("FADING OUT..."); is_fading_out = True; master_fader.stop()
                threading.Timer(4.1, lambda: globals().update(running=False)).start()
            elif bid == SIDE_BTNS[0] and state > 0:
                print("PANIC RESET..."); master_fader.stop()
                threading.Timer(4.0, lambda: [a.deactivate() for a in agents] + [master_fader.play()]).start()
            elif bid == SIDE_DELAY_BTN and state > 0:
                delay_cycle_idx = (delay_cycle_idx + 1) % 4
                for d in delays:
                    d.delay = delay_times[delay_cycle_idx] if delay_times[delay_cycle_idx] > 0 else 0.001
                    d.mul = 0.5 if delay_times[delay_cycle_idx] > 0 else 0.0
                print(f"DELAY: {['OFF', '1/4', '1/8', '1/16'][delay_cycle_idx]}")
                update_ui()
            elif bid == SIDE_CHORUS_BTN and state > 0:
                chorus_cycle_idx = (chorus_cycle_idx + 1) % 4
                cfg = chorus_settings[chorus_cycle_idx]
                for c in choruses: c.depth = cfg["depth"]; c.feedback = cfg["fb"]
                print(f"CHORUS: {['OFF', 'SUBTLE', 'MOD', 'DEEP'][chorus_cycle_idx]}")
                update_ui()
            elif bid == TOP_BTNS[4] and state > 0:
                reverb_mode = (reverb_mode + 1) % 3; update_reverb_settings(); update_ui()
            elif bid == TOP_BTNS[5] and state > 0:
                migration_active = not migration_active; update_ui()
                print(f"MIGRATION: {'ON' if migration_active else 'OFF'}")
            elif bid in [SIDE_NEXT_SOUND, SIDE_PREV_SOUND] and state > 0:
                sound_profile_idx = (sound_profile_idx + (1 if bid == SIDE_NEXT_SOUND else -1)) % len(SOUND_PROFILES)
                print(f"TARGET SOUND: {SOUND_PROFILES[sound_profile_idx]['name']}")
            elif bid in VOL_BTNS and state > 0:
                change = 0.05 if bid == VOL_BTNS[1] else -0.05
                master_fader.mul = max(0, min(1, master_fader.mul + change))
                print(f"VOLUME: {int(master_fader.mul * 100)}%"); update_ui()
            elif bid in TOP_BTNS[0:4] and state > 0:
                if bid in TOP_BTNS[0:2]: 
                    root_note += (1 if bid == TOP_BTNS[1] else -1)
                    print(f"ROOT: {NOTE_NAMES[root_note % 12]}")
                else: 
                    target_scale_idx = (target_scale_idx + (1 if bid == TOP_BTNS[3] else -1)) % len(SCALE_NAMES)
                    print(f"SCALE: {SCALE_NAMES[target_scale_idx]}")
                update_ui()
            else:
                coords = get_xy_from_raw(bid)
                if coords and state > 0:
                    idx = coords[1]*8 + coords[0]
                    if not agents[idx].active: agents[idx].activate()
                    else: agents[idx].deactivate()

        # STAGGERED TRANSITION (RESTORED)
        outdated = [a for a in agents if a.active and (a.assigned_prof_idx != sound_profile_idx or a.assigned_scale_idx != target_scale_idx or a.assigned_root != root_note)]
        if outdated and current_time - last_scale_transition > 0.1:
            lucky = random.choice(outdated)
            lucky.assigned_prof_idx, lucky.assigned_scale_idx, lucky.assigned_root = sound_profile_idx, target_scale_idx, root_note
            lucky.apply_tuning(source="Transition")
            lucky.refresh_led()
            last_scale_transition = current_time

        if migration_active and current_time - last_migration_tick > (BEAT_TIME * 0.5):
            last_migration_tick = current_time
            active_ones = [a for a in agents if a.active]
            if active_ones:
                a = random.choice(active_ones)
                empty = [ag for ag in agents if not ag.active]
                if empty:
                    dest = random.choice(empty); div = a.current_div
                    print(f"[MIGRATION] Displacing from ({a.x},{a.y}) to ({dest.x},{dest.y})")
                    a.deactivate(); dest.activate(force_interval=div)

        for a in agents: a.update(current_time)
        time.sleep(0.002)
finally:
    running = False; s.stop(); lp.Reset(); lp.Close()
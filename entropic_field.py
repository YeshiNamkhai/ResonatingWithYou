import sys
import time
import random
import threading
from pyo import *
import launchpad_py as launchpad

"""
Entropic field
======================================================================================
This script creates a chaotic motion of cells, initially stacked in two columns. 
You can select the initial layout, default to left which works also in stereo, 
when top or bottom, which goes from bright to dull tone or opposite, 
only works with 4 speakers; you may also experiment with reverb, delay and speed. 
Entropy increases and the cells move for about 4 minutes, reaching the opposite side.
======================================================================================
- Top Buttons 0-1: Scale Selection (Cycle SCALES_DICT, Green/Amber)
- Top Buttons 2-3: Position Selection (Cycle LEFT/RIGHT/TOP/BOTTOM, Amber)
- Top Buttons 6-7: Main Volume (Amber 60%, Adjusts user_vol)

- Side Button 0: Start Sequence (Locks Setup Mode, Red/Green)
- Side Button 1: Reverb Toggle (Cycle 0.0-0.7 Mix, Green/Amber/Red)
- Side Button 2: Filter Toggle (Schumann Resonance 7.83Hz, Green/Amber)
- Side Button 3: Delay Toggle (Temporal Delay 0.1s-0.2s, Green/Amber)
- Side Button 6: EXIT / POWER OFF (Blue/Cyan - Matched to test_speakers)

======================================================================================
Example of default scale (Partch Otonality)

[Y]  TOP of Grid (High Pitch)
   0 |  10/4    11/4    3/1     13/4* ...  <-- Higher Harmonics
   1 |  8/4     9/4     10/4    11/4    ...  
   2 |  6/4     7/4     8/4     9/4     ...  
   3 |  4/4     5/4     6/4     7/4     ...  <-- Degree 0 (Root 1/1)
   4 |  2/1     9/4     10/4    11/4    ...  
   5 |  7/4     8/4     9/4     10/4    ...  
   6 |  5/4     6/4     7/4     8/4     ...  
   7 |  1/1     5/4     6/4     7/4     ...  <-- Root (4/4)
     +--------------------------------------
 [X]    0        1       2       3      RIGHT (+1 Degree)
"""

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio'
BUFFER_SIZE = 1024 

# --- 1. Launchpad Setup ---
lp = launchpad.Launchpad()
mode = "MK1"
if lp.Check(0, "mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(0, "mk2"); mode = "MK2"
    SIDE_START_BTN = 89 
    SIDE_REV_BTN = 79    
    SIDE_FILT_BTN = 69   
    SIDE_DLY_BTN = 59    
    SIDE_POWER_BTN = 29  
    TOP_BTNS = [104, 105, 106, 107, 108, 109, 110, 111]
elif lp.Check(0):
    lp.Open(0); mode = "MK1"
    SIDE_START_BTN = 8 
    SIDE_REV_BTN = 24  
    SIDE_FILT_BTN = 40  
    SIDE_DLY_BTN = 56   
    SIDE_POWER_BTN = 120 
    TOP_BTNS = [200, 201, 202, 203, 204, 205, 206, 207]
else:
    sys.exit("No Launchpad detected.")
lp.Reset()

# --- 2. Audio Setup ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()

# --- 3. Configuration & Palette ---
SCALES_DICT = {
    "Chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "Indian Bhairav": [0, 1.12, 3.86, 4.98, 7.02, 8.14, 10.88],
    "Partch Otonality": [0, 2.04, 3.86, 4.98, 7.02, 8.84, 10.88],
    "Partch Utonality": [0, 1.12, 3.16, 4.98, 7.02, 8.14, 9.96],
    "Partch Diamond": [0, 1.51, 1.65, 1.82, 2.04, 2.31, 2.67, 3.18, 3.47, 3.86, 4.35, 4.98, 5.51, 6.49, 7.02, 7.65, 8.14, 8.53, 8.84, 9.33, 9.69, 9.96, 10.18, 10.35, 10.49, 10.88, 11.44],
    "Young Lamonte": [0, 1.14, 3.86, 4.98, 7.02, 8.14, 10.88],
    "31-TET Pure": [0, 1.93, 3.87, 5.03, 6.96, 8.90, 10.83],
    "Bohlen-Pierce": [0, 1.46, 2.92, 4.38, 5.84, 7.30, 8.76, 10.22, 11.68],
    "Carlos Alpha": [0, 0.78, 1.56, 2.34, 3.12, 3.90, 4.68, 5.46, 6.24, 7.02],
    "Gamelan Slendro": [0, 2.4, 4.8, 7.2, 9.6],
    "Random 1": sorted([0] + [round(random.uniform(0.5, 11.5), 2) for _ in range(6)]),
}
SCALE_NAMES = list(SCALES_DICT.keys())
POS_NAMES = ["LEFT", "RIGHT", "TOP", "BOTTOM"]

COLOR_MAP = {
"Chromatic": (63, 63, 63) if mode=="MK2" else (3,3),
    "Indian Bhairav": (63, 10, 0) if mode=="MK2" else (3,1),
    "Partch Otonality": (0, 63, 0) if mode=="MK2" else (0,3),
    "Partch Utonality": (63, 0, 30) if mode=="MK2" else (3,1),
    "Partch Diamond": (63, 40, 0) if mode=="MK2" else (3,2),
    "Young Lamonte": (30, 0, 63) if mode=="MK2" else (1,1),
    "31-TET Pure": (0, 63, 63) if mode=="MK2" else (0,2),
    "Bohlen-Pierce": (63, 0, 63) if mode=="MK2" else (3,0),
    "Carlos Alpha": (63, 63, 0) if mode=="MK2" else (3,2),
    "Gamelan Slendro": (0, 15, 63) if mode=="MK2" else (1,3),
    "Random 1": (20, 63, 20) if mode=="MK2" else (1,2),
}

# --- 4. Logic State ---
cells = []
running = True
setup_mode = True
lock = threading.Lock()
sel_scale_idx, sel_pos_idx = 2, 0
last_led_state = set()

MAX_VOICES = 16 

global_harms_base = Sig(1)
base_port = Port(global_harms_base, risetime=0.1, falltime=0.1)
global_harms_range = Sig(0)
range_port = Port(global_harms_range, risetime=0.1, falltime=0.1)
user_vol = Sig(0.6)
fade_vol = Sig(0)
fade_port = Port(fade_vol, risetime=0.1, falltime=0.1)
master_gain = user_vol * fade_port

rev_levels = [0.0, 0.3, 0.5, 0.7]
rev_gains = [1.0, 1.05, 1.15, 1.35] 
rev_idx = 1 
global_rev_bal = Sig(rev_levels[rev_idx])
global_rev_comp = Sig(rev_gains[rev_idx])
rev_port = Port(global_rev_bal, risetime=0.1, falltime=0.1)
comp_port = Port(global_rev_comp, risetime=0.1, falltime=0.1)

filt_idx = 0 
filt_rates = [0.0, 7.83, 15.66] 
filt_base_rate = Sig(0)

dly_idx = 0
dly_times = [0.0, 0.2, 0.1]
dly_time_sig = Sig(0)
dly_feed = Sig(0.4)

class GridVoice:
    def __init__(self, voice_idx):
        self.freq = Sig(0); self.gate = Sig(0)
        self.amp = Port(self.gate, 0.5, 2.0) 
        self.lfo = Sine(freq=random.uniform(0.025, 0.1), mul=0.5, add=0.5)
        self.harms = global_harms_base + (self.lfo * global_harms_range)
        self.osc = Blit(freq=self.freq, harms=self.harms, mul=self.amp * 0.1)
        self.v_rate = filt_base_rate * random.uniform(0.99, 1.01)
        self.f_lfo = LFO(freq=self.v_rate, type=1, mul=2200, add=400)
        self.filt_obj = MoogLP(self.osc, freq=self.f_lfo, res=0.7, mul=2.5)
        self.is_moving_gate = Sig(0)
        self.moving_port = Port(self.is_moving_gate, risetime=0.02, falltime=0.25)
        self.sig_source = (self.osc * (1 - self.moving_port)) + (self.filt_obj * self.moving_port)
        self.pan_x = Sig(0.5); self.pan_y = Sig(0.5)
        self.ch_tl = (self.sig_source * (1 - self.pan_x) * (1 - self.pan_y) * master_gain)
        self.ch_tr = (self.sig_source * self.pan_x * (1 - self.pan_y) * master_gain)
        self.ch_bl = (self.sig_source * (1 - self.pan_x) * self.pan_y * master_gain)
        self.ch_br = (self.sig_source * self.pan_x * self.pan_y * master_gain)
        self.dly_tl = Delay(self.ch_tl * self.moving_port, delay=dly_time_sig, feedback=dly_feed)
        self.dly_tr = Delay(self.ch_tr * self.moving_port, delay=dly_time_sig, feedback=dly_feed)
        self.dly_bl = Delay(self.ch_bl * self.moving_port, delay=dly_time_sig, feedback=dly_feed)
        self.dly_br = Delay(self.ch_br * self.moving_port, delay=dly_time_sig, feedback=dly_feed)
        self.rev_tl = Freeverb(self.ch_tl + self.dly_tl, size=0.8, damp=0.5, bal=rev_port, mul=comp_port).out(0)
        self.rev_tr = Freeverb(self.ch_tr + self.dly_tr, size=0.8, damp=0.5, bal=rev_port, mul=comp_port).out(1)
        self.rev_bl = Freeverb(self.ch_bl + self.dly_bl, size=0.8, damp=0.5, bal=rev_port, mul=comp_port).out(2)
        self.rev_br = Freeverb(self.ch_br + self.dly_br, size=0.8, damp=0.5, bal=rev_port, mul=comp_port).out(3)

    def update(self, x, y, pitch, effect_active):
        self.freq.value = midiToHz(pitch)
        self.pan_x.value = x / 7.0; self.pan_y.value = y / 7.0
        self.gate.value = 1
        self.is_moving_gate.value = 1 if (effect_active and (filt_idx > 0 or dly_idx > 0)) else 0

voice_pool = [GridVoice(i) for i in range(MAX_VOICES)]

# --- 5. Helpers ---
def get_pitch(x, y):
    root = 48
    scale = SCALES_DICT[SCALE_NAMES[sel_scale_idx]]
    degree = x + ((7 - y) * 2)
    octave = degree // len(scale)
    return root + scale[int(degree % len(scale))] + (octave * 12)

def set_top_led(idx, r, g, b):
    if mode == "MK2": lp.LedCtrlRaw(TOP_BTNS[idx], r, g, b)
    else: lp.LedCtrlRaw(TOP_BTNS[idx], 3 if r>0 else 0, 3 if g>0 else 0)

def update_leds():
    global last_led_state
    curr = set()
    if setup_mode:
        if sel_pos_idx == 0: 
            for y in range(8): curr.add((0,y)); curr.add((1,y))
        elif sel_pos_idx == 1: 
            for y in range(8): curr.add((6,y)); curr.add((7,y))
        elif sel_pos_idx == 2: 
            for x in range(8): curr.add((x,0)); curr.add((x,1))
        elif sel_pos_idx == 3: 
            for x in range(8): curr.add((x,6)); curr.add((x,7))
        color = (0, 15, 63) if mode=="MK2" else (0,3)
    else:
        with lock:
            for c in cells: curr.add((c['x'], c['y']))
        color = COLOR_MAP.get(SCALE_NAMES[sel_scale_idx], (63, 63, 0))

    for (x, y) in (last_led_state - curr):
        if mode == "MK2": lp.LedCtrlRaw(11+x+(7-y)*10, 0, 0, 0)
        else: lp.LedCtrlXY(x, y, 0, 0)
    for (x, y) in (curr - last_led_state):
        if mode == "MK2": lp.LedCtrlRaw(11+x+(7-y)*10, *color)
        else: lp.LedCtrlXY(x, y, *color)
    last_led_state = curr
    
    if setup_mode:
        set_top_led(0,0,63,0); set_top_led(1,0,63,0)
        set_top_led(2,63,63,0); set_top_led(3,63,63,0)
        if mode == "MK2": lp.LedCtrlRaw(SIDE_START_BTN, 63, 0, 0)
        else: lp.LedCtrlRaw(SIDE_START_BTN, 3, 0)
    else:
        for i in range(4): set_top_led(i, 0, 0, 0)
        if mode == "MK2": lp.LedCtrlRaw(SIDE_START_BTN, 0, 63, 0)
        else: lp.LedCtrlRaw(SIDE_START_BTN, 0, 3)
    
    vol = user_vol.value
    if vol < 0.4: v_col = (0, 63, 0) if mode == "MK2" else (0, 3)     
    elif vol >= 0.7: v_col = (63, 0, 0) if mode == "MK2" else (3, 0)     
    else: v_col = (63, 35, 0) if mode == "MK2" else (3, 2)    
    set_top_led(6, *v_col); set_top_led(7, *v_col)
    
    # Power Button Color matching test_speakers.py
    if mode == "MK2": lp.LedCtrlRaw(SIDE_POWER_BTN, 10, 10, 63)
    else: lp.LedCtrlRaw(SIDE_POWER_BTN, 1, 3)

    if filt_idx == 0: f_col = (0, 0, 0)
    elif filt_idx == 1: f_col = (0, 63, 0) if mode == "MK2" else (0, 3) 
    else: f_col = (63, 35, 0) if mode == "MK2" else (3, 2)
    if mode == "MK2": lp.LedCtrlRaw(SIDE_FILT_BTN, *f_col)
    else: lp.LedCtrlRaw(SIDE_FILT_BTN, f_col[0], f_col[1])

    if dly_idx == 0: d_col = (0, 0, 0)
    elif dly_idx == 1: d_col = (0, 63, 0) if mode == "MK2" else (0, 3)
    else: d_col = (63, 35, 0) if mode == "MK2" else (3, 2)
    if mode == "MK2": lp.LedCtrlRaw(SIDE_DLY_BTN, *d_col)
    else: lp.LedCtrlRaw(SIDE_DLY_BTN, d_col[0], d_col[1])

    curr_rev = rev_levels[rev_idx]
    if curr_rev == 0.0: r_col = (0, 0, 0)
    elif curr_rev == 0.3: r_col = (0, 63, 0) if mode == "MK2" else (0, 3)
    elif curr_rev == 0.5: r_col = (63, 35, 0) if mode == "MK2" else (3, 2)
    else: r_col = (63, 0, 0) if mode == "MK2" else (3, 0)
    if mode == "MK2": lp.LedCtrlRaw(SIDE_REV_BTN, *r_col)
    else: lp.LedCtrlRaw(SIDE_REV_BTN, r_col[0], r_col[1])

# --- 6. Sequence ---
def main_loop():
    global running, setup_mode, cells
    while running and setup_mode:
        update_leds(); time.sleep(0.1)
    
    if not running: return
    
    if sel_pos_idx == 0: cells = [{'x':x,'y':y} for x in range(2) for y in range(8)]
    elif sel_pos_idx == 1: cells = [{'x':x,'y':y} for x in range(6,8) for y in range(8)]
    elif sel_pos_idx == 2: cells = [{'x':x,'y':y} for y in range(2) for x in range(8)]
    else: cells = [{'x':x,'y':y} for y in range(6,8) for x in range(8)]

    print(f"| GENESIS | Scale: {SCALE_NAMES[sel_scale_idx]} | Origin: {POS_NAMES[sel_pos_idx]} |")

    SCHUMANN_TICK = 0.128
    steps = 160
    print(">>> FADING IN: Initializing voice harmonics and volume ramp...")
    for i in range(steps):
        if not running: break
        p = i / steps
        fade_vol.value = p
        global_harms_base.value = 1 + (4 * p)
        with lock:
            for idx, c in enumerate(cells):
                if idx < MAX_VOICES: voice_pool[idx].update(c['x'], c['y'], get_pitch(c['x'], c['y']), False)
        update_leds(); time.sleep(SCHUMANN_TICK)

    start_time = time.time()
    print(">>> STEADY STATE: Cellular movement and entropy active (4-minute cycle).")
    while running and (time.time() - start_time < 240):
        global_harms_range.value = 40 * ((time.time() - start_time) / 240)
        with lock:
            effect_voice_idx = random.randint(0, min(len(cells), MAX_VOICES) - 1)
            for idx, c in enumerate(cells):
                moved = False
                if random.random() < 0.05:
                    c['x'] = max(0, min(7, c['x'] + random.choice([-1, 0, 1])))
                    c['y'] = max(0, min(7, c['y'] + random.choice([-1, 0, 1])))
                    moved = True
                if idx < MAX_VOICES: 
                    voice_pool[idx].update(c['x'], c['y'], get_pitch(c['x'], c['y']), (moved and idx == effect_voice_idx))
        update_leds(); time.sleep(SCHUMANN_TICK)

    print(">>> FADING OUT: Reducing harmonic complexity and master gain.")
    curr_range = global_harms_range.value
    for i in range(steps):
        if not running: break
        inv_p = 1.0 - (i / steps)
        fade_vol.value = inv_p
        global_harms_base.value = 1 + (4 * inv_p)
        global_harms_range.value = curr_range * inv_p
        update_leds(); time.sleep(SCHUMANN_TICK)
    running = False

def input_listener():
    global running, setup_mode, sel_scale_idx, sel_pos_idx, rev_idx, filt_idx, dly_idx
    while running:
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            if state > 0:
                if bid == SIDE_POWER_BTN:
                    print("[SYSTEM] KILL SWITCH TRIGGERED: Shutting down safely.")
                    running = False
                
                if bid == SIDE_FILT_BTN:
                    filt_idx = (filt_idx + 1) % 3
                    filt_base_rate.value = filt_rates[filt_idx]
                    print(f"[FX] SCHUMANN FILTER MODE: {filt_idx} (Rate: {filt_rates[filt_idx]}Hz)")
                    update_leds()

                if bid == SIDE_DLY_BTN:
                    dly_idx = (dly_idx + 1) % 3
                    dly_time_sig.value = dly_times[dly_idx]
                    print(f"[FX] TEMPORAL DELAY MODE: {dly_idx} (Time: {dly_times[dly_idx]}s)")
                    update_leds()

                if bid == SIDE_REV_BTN:
                    rev_idx = (rev_idx + 1) % len(rev_levels)
                    global_rev_bal.value = rev_levels[rev_idx]
                    global_rev_comp.value = rev_gains[rev_idx] 
                    print(f"[FX] REVERB MIX: {rev_levels[rev_idx]} | GAIN COMP: {rev_gains[rev_idx]}x")
                    update_leds()

                if setup_mode and bid == SIDE_START_BTN:
                    print("[SYSTEM] Setup locked. Commencing sequence.")
                    setup_mode = False
                    update_leds()

                if setup_mode and bid in TOP_BTNS:
                    idx = TOP_BTNS.index(bid)
                    if idx == 0: sel_scale_idx = (sel_scale_idx - 1) % len(SCALE_NAMES)
                    elif idx == 1: sel_scale_idx = (sel_scale_idx + 1) % len(SCALE_NAMES)
                    elif idx == 2: sel_pos_idx = (sel_pos_idx - 1) % 4
                    elif idx == 3: sel_pos_idx = (sel_pos_idx + 1) % 4
                    if setup_mode:
                        print(f"[SETUP] Selection: {SCALE_NAMES[sel_scale_idx]} | Start Pos: {POS_NAMES[sel_pos_idx]}")
                    update_leds()
                
                is_vol_down = (mode == "MK1" and bid == 206) or (mode == "MK2" and bid == 110)
                is_vol_up = (mode == "MK1" and bid == 207) or (mode == "MK2" and bid == 111)
                if is_vol_down: 
                    user_vol.value = max(0, user_vol.value - 0.1)
                    print(f"[AUDIO] Master Volume Decreased: {round(user_vol.value, 1)}")
                    update_leds()
                elif is_vol_up: 
                    user_vol.value = min(1.0, user_vol.value + 0.1)
                    print(f"[AUDIO] Master Volume Increased: {round(user_vol.value, 1)}")
                    update_leds()
        time.sleep(0.01)

t_logic = threading.Thread(target=main_loop); t_input = threading.Thread(target=input_listener)
t_logic.start(); t_input.start()

try:
    while running: time.sleep(0.5)
except KeyboardInterrupt:
    running = False
finally:
    s.stop()
    time.sleep(0.1) 
    lp.Reset(); lp.Close(); sys.exit()
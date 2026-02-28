import sys
import time
import random
import threading
import queue
from pyo import *
import launchpad_py as launchpad

"""
Quadraphonic Harmonic Synth V2
==============================
- Top Button 0: Key Up (Increments root note)
- Top Button 1: Key Down (Decrements root note)
- Top Button 2: Scale Up (Cycles through 20+ musical scales)
- Top Button 3: Scale Down (Cycles through 20+ musical scales)
- Top Button 4: Harmonics Up (Momentary increase for Blit oscillator)
- Top Button 5: Harmonics Down (Momentary decrease for Blit oscillator)
- Top Button 6: Main Volume Down (Decrements master gain)
- Top Button 7: Main Volume Up (Increments master gain)

- Side Button 0: Reverb Cycle (OFF -> LOW -> MED -> HIGH)
- Side Button 1: Delay Cycle (OFF -> LOW -> MED -> HIGH)
- Side Button 2: Arpeggiator (ON/OFF)
- Side Button 3: Drum Machine (OFF -> GREEN: Even -> AMBER: Odd -> RED: Silenced)
- Side Button 4: Octave Up (Shifts grid pitch +3 octaves)
- Side Button 5: Octave Down (Shifts grid pitch -3 octaves)
- Side Button 6: Exit (Stops server and shuts down)

- 8x8 Grid: Note trigger with Quad Panning (X/Y position determines output channel gain)
"""

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio' 
BUFFER_SIZE = 512 

# --- LAUNCHPAD DETECTION ---
lp = launchpad.Launchpad()
mode = "MK1"
if lp.Check(0, "mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(0, "mk2"); mode = "MK2"
    SIDE_POWER_BTN = 29  # 7th button down on MK2 side
elif lp.Check(0):
    lp.Open(0); mode = "MK1"
    SIDE_POWER_BTN = 104 # 7th button down on MK1 side (Row 6, ID 8+6*16)
else:
    sys.exit("No Launchpad detected.")

lp.Reset()

print(mode)
lp_lock = threading.Lock()

# --- PYO SETUP ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE,winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()

# --- 20 MUSICAL SCALES ---
SCALES = {
    "Major": [0, 2, 4, 5, 7, 9, 11], "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Indian Bhairav": [0, 1.12, 3.86, 4.98, 7.02, 8.14, 10.88],
    "Indian Marwa": [0, 1.12, 3.86, 5.90, 7.02, 9.06, 10.88],
    "Chinese Pentatonic": [0, 2.04, 3.86, 7.02, 9.06],
    "Ligeti Micro": [0, 0.5, 2.5, 3.5, 6.5, 7.5, 10.5],
    "Spectral": [0, 2.04, 3.86, 5.51, 7.02, 8.41, 9.69, 10.88],
    "Partch Otonality": [0, 2.04, 3.86, 4.98, 7.02, 8.84, 10.88],
    "Japanese Hirajoshi": [0, 2.04, 3.16, 7.02, 8.14],
    "Japanese In Sen": [0, 1.12, 4.98, 7.02, 8.14],
    "Dorian": [0, 2, 3, 5, 7, 9, 10], "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11], "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Locrian": [0, 1, 3, 5, 6, 8, 10], "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
    "Melodic Minor": [0, 2, 3, 5, 7, 9, 11], "Pentatonic Maj": [0, 2, 4, 7, 9],
    "Pentatonic Min": [0, 3, 5, 7, 10], "Blues": [0, 3, 5, 6, 7, 10],
    "Whole Tone": [0, 2, 4, 6, 8, 10], "Acoustic": [0, 2, 4, 6, 7, 9, 10],
    "Altered": [0, 1, 3, 4, 6, 8, 10], "Phrygian Dom": [0, 1, 4, 5, 7, 8, 10],
    "Hungarian Min": [0, 2, 3, 6, 7, 8, 11], "Double Harm": [0, 1, 4, 5, 7, 8, 11]
}

def init_random_scale():
    count = random.randint(5, 8)
    scale = [0]
    while len(scale) < count:
        val = random.uniform(0.8, 11.5)
        if all(abs(val - x) > 0.5 for x in scale):
            scale.append(val)
    scale.sort()
    name = f"Rnd Micro {random.randint(100, 999)}"
    SCALES[name] = scale

init_random_scale()
SCALE_NAMES = list(SCALES.keys())
KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# --- GLOBAL & AUDIO STATE ---
cur_key, cur_scale, octave_offset = 0, 0, 0
active_voices = {}
held_pitches = set()
running = True
harms_up_held = False
harms_down_held = False
arp_active = False
drum_mode = 0 
drum_beats = 16

# --- QUAD AUDIO CHAIN ---
MAX_VOICES = 16
harms_sig = Sig(value=5)
harms_port = Port(harms_sig, risetime=0.5, falltime=0.5)

voices_osc = []
voices_env = []
voices_gains = [] 
voices_outs = []  

for _ in range(MAX_VOICES):
    env = Adsr(attack=0.1, decay=0.3, sustain=0.6, release=0.8, dur=0, mul=0.2)
    osc = Blit(freq=100, harms=harms_port, mul=env)
    gains = [Sig(0) for _ in range(4)]
    ports = [Port(g, 0.05, 0.05) for g in gains]
    outs = [osc * p for p in ports]
    voices_osc.append(osc)
    voices_env.append(env)
    voices_gains.append(gains)
    voices_outs.append(outs)

quad_buses = [Mix([v[i] for v in voices_outs], voices=1) for i in range(4)]

# --- DRUM SYNTH SECTION (Lower Amplitude) ---
d_env = Adsr(attack=0.001, decay=0.1, sustain=0, release=0.05, dur=0.15, mul=0.04)
d_bd = Sine(freq=55, mul=d_env)
d_noise = Noise(mul=d_env)
d_snare = Resonx(d_noise, freq=1200, q=4)
d_hh = ButHP(d_noise, freq=6000)
d_fm = CrossFM(carrier=1000, ratio=1.4, ind1=12, mul=d_env) 
d_mix = Mix([d_bd, d_snare, d_hh, d_fm], voices=1)

# Quad LFO for Drums
d_lfo_pan = [d_mix * Sine(freq=0.15, phase=i/4.0, mul=0.5, add=0.5) for i in range(4)]

# --- EFFECTS (DELAY -> REVERB) ---

# 1. DELAY (WITH NATURAL TAIL FADE)
delay_time_sig = Sig(0.0075) 
delay_feed_sig = Sig(0.55)
delay_feed_port = Port(delay_feed_sig, 0.2, 0.2)
delay_input_mix = Sig(0) 
delay_input_port = Port(delay_input_mix, 0.2, 0.2) # Ramps input to delay

# Mix Grid + Drum LFO before delay
combined_to_delay = [(quad_buses[i] + d_lfo_pan[i]) for i in range(4)]

delays = [Delay(combined_to_delay[i] * delay_input_port, delay=delay_time_sig, feedback=delay_feed_port, mul=1.0) for i in range(4)]
delay_to_reverb = [combined_to_delay[i] + delays[i] for i in range(4)]

# 2. REVERB
rev_mix_sig = Sig(0)
rev_mix_port = Port(rev_mix_sig, risetime=0.5, falltime=0.5)
rev_size_sig = Sig(0.5)
reverbs = [Freeverb(delay_to_reverb[i], size=rev_size_sig, damp=0.5, bal=rev_mix_port) for i in range(4)]

# Master Volume
master_vol = Sig(0.6)
master_vol_port = Port(master_vol, 0.1, 0.1)
amp_scale = Min(harms_port / 5.0, 2.0)

GLOBAL_BOOST = 2.0 
amp_final = master_vol_port * amp_scale * GLOBAL_BOOST

final_outs = [(reverbs[i] * amp_final).out(i) for i in range(4)]

voice_ptr = 0

# --- HELPER FUNCTIONS ---
fx_states = [0, 0, 0, 0] 
led_queue = queue.Queue()
led_cache = {}

def led_worker():
    while True:
        func, args = led_queue.get()
        try: func(*args)
        except Exception as e: print(f"LED Error: {e}")
        led_queue.task_done()

t_led = threading.Thread(target=led_worker); t_led.daemon = True; t_led.start()

def clear_all_leds():
    with lp_lock:
        lp.ButtonFlush()
        if mode == "MK2":
            for i in range(11, 112): lp.LedCtrlRaw(i, 0, 0, 0)
        else:
            for i in range(128): lp.LedCtrlRaw(i, 0, 0)
        led_cache.clear()

def get_quad_gains(x, y_logical):
    nx = x / 7.0; ny = (7 - y_logical) / 7.0 
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def get_pitch(x, y_logical):
    return 36 + cur_key + x + (y_logical * 5) + (octave_offset * 12)

def get_led_color(pitch, pad_id):
    if pad_id in active_voices or pitch in held_pitches:
        return (63, 63, 63) if mode == "MK2" else (3, 3)
    rel_pitch = (pitch - cur_key) % 12
    scale = SCALES[SCALE_NAMES[cur_scale]]
    closest = min(scale, key=lambda x: abs(x - rel_pitch))
    if abs(closest - rel_pitch) < 0.5:
        if abs(closest) < 0.1: return (63, 0, 0) if mode == "MK2" else (3, 0)
        return (0, 63, 0) if mode == "MK2" else (0, 3)
    return (0, 0, 0)

def update_pad_immediate(x, y_logical):
    if mode == "MK2": pad_id = (y_logical + 1) * 10 + (x + 1)
    else: pad_id = ((7 - y_logical) * 16) + x
    pitch = get_pitch(x, y_logical)
    col = get_led_color(pitch, pad_id)
    with lp_lock:
        if pad_id in led_cache and led_cache[pad_id] == col: return
        if mode == "MK2": lp.LedCtrlRaw(pad_id, col[0], col[1], col[2])
        else: lp.LedCtrlRaw(pad_id, col[0], col[1])
        led_cache[pad_id] = col

def queue_pad_update(x, y_logical): led_queue.put((update_pad_immediate, (x, y_logical)))

def refresh_grid_immediate():
    for y_logical in range(8):
        for x in range(8): update_pad_immediate(x, y_logical)
        time.sleep(0.003) 
    with lp_lock:
        for i in range(4):
            state = fx_states[i]
            if i == 0: # Reverb
                if mode == "MK2":
                    col = [(0,0,0),(0,63,0),(63,63,0),(63,0,0)][state] 
                    lp.LedCtrlRaw(89 - (i * 10), *col)
                else:
                    col = [(0,0),(0,3),(3,3),(3,0)][state] 
                    lp.LedCtrlRaw(8 + (i * 16), col[0], col[1])
            elif i == 1: # Delay
                if mode == "MK2":
                    col = [(0,0,0), (0,30,0), (63,40,0), (63,0,0)][state] 
                    lp.LedCtrlRaw(89 - (i * 10), *col)
                else:
                    col = [(0,0), (0,1), (3,1), (3,0)][state] 
                    lp.LedCtrlRaw(8 + (i * 16), col[0], col[1])
            elif i == 2: # Arpeggiator
                col = (0, 63, 0) if arp_active else (0, 0, 0)
                if mode == "MK2": lp.LedCtrlRaw(89 - (i * 10), *col)
                else: lp.LedCtrlRaw(8 + (i * 16), 0 if not arp_active else 3, 0)
            elif i == 3: # Drum Machine
                d_col = [(0,0,0), (0,63,0), (63,63,0), (63,0,0)][drum_mode] if mode == "MK2" else [(0,0), (0,3), (3,3), (3,0)][drum_mode]
                if mode == "MK2": lp.LedCtrlRaw(89 - (i * 10), *d_col)
                else: lp.LedCtrlRaw(8 + (i * 16), d_col[0], d_col[1])
        for i in range(4, 6):
            if octave_offset == 0: col = (0, 63, 0) if mode == "MK2" else (0, 3)
            else: col = (63, 20, 0) if mode == "MK2" else (3, 1)
            if mode == "MK2": lp.LedCtrlRaw(89 - (i * 10), *col)
            else: lp.LedCtrlRaw(8 + (i * 16), col[0], col[1])
        if mode == "MK2": lp.LedCtrlRaw(SIDE_POWER_BTN, 10, 10, 63)
        else: lp.LedCtrlRaw(SIDE_POWER_BTN, 1, 3)
    
    h_val = int(harms_sig.value)
    with lp_lock:
        if mode == "MK2":
            h_col = (0,63,0) if h_val<20 else (63,63,0) if h_val<40 else (63,0,0)
            lp.LedCtrlRaw(104+4, *h_col); lp.LedCtrlRaw(104+5, *h_col)
        else:
            h_col = (0,3) if h_val<20 else (3,3) if h_val<40 else (3,0)
            lp.LedCtrlRaw(200+4, *h_col); lp.LedCtrlRaw(200+5, *h_col)
    
    vol = master_vol.value
    with lp_lock:
        if mode == "MK2":
            v_col = (0,63,0) if vol<0.4 else (63,63,0) if vol<0.7 else (63,0,0)
            lp.LedCtrlRaw(104+6, *v_col); lp.LedCtrlRaw(104+7, *v_col)
        else:
            v_col = (0,3) if vol<0.4 else (3,3) if vol<0.7 else (3,0)
            lp.LedCtrlRaw(200+6, *v_col); lp.LedCtrlRaw(200+7, *v_col)

def refresh_grid(): led_queue.put((refresh_grid_immediate, ()))

def update_pitch_leds(target_pitch):
    for y in range(8):
        for x in range(8):
            if get_pitch(x, y) == target_pitch: queue_pad_update(x, y)

def apply_immediate_transpose():
    """Recalculates frequency for all currently active voices."""
    for pid, v_idx in active_voices.items():
        if mode == "MK2": x, y_log = (pid % 10) - 1, (pid // 10) - 1
        else: x, y_log = pid % 16, 7 - (pid // 16)
        pitch = get_pitch(x, y_log)
        scale = SCALES[SCALE_NAMES[cur_scale]]
        rel_pitch = (pitch - cur_key) % 12
        closest = min(scale, key=lambda x: abs(x - rel_pitch))
        if abs(closest - rel_pitch) < 0.5:
            voices_osc[v_idx].setFreq(midiToHz(pitch - rel_pitch + closest))
        else:
            voices_osc[v_idx].setFreq(midiToHz(pitch))

def play_note(pad_id, x, y_logical):
    global voice_ptr
    pitch = get_pitch(x, y_logical); scale = SCALES[SCALE_NAMES[cur_scale]]
    rel_pitch = (pitch - cur_key) % 12; closest = min(scale, key=lambda x: abs(x - rel_pitch))
    if abs(closest - rel_pitch) < 0.5: voices_osc[voice_ptr].setFreq(midiToHz(pitch - rel_pitch + closest))
    else: voices_osc[voice_ptr].setFreq(midiToHz(pitch))
    gains = get_quad_gains(x, y_logical)
    for i in range(4): voices_gains[voice_ptr][i].value = gains[i]
    voices_env[voice_ptr].play(); active_voices[pad_id] = voice_ptr
    voice_ptr = (voice_ptr + 1) % MAX_VOICES; held_pitches.add(pitch); update_pitch_leds(pitch)

def stop_note(pad_id, x, y_logical):
    pitch = get_pitch(x, y_logical)
    if pad_id in active_voices: voices_env[active_voices[pad_id]].stop(); del active_voices[pad_id]
    still_held = any(get_pitch((pid%10-1 if mode=="MK2" else pid%16), (pid//10-1 if mode=="MK2" else 7-(pid//16))) == pitch for pid in active_voices)
    if not still_held and pitch in held_pitches: held_pitches.remove(pitch)
    update_pitch_leds(pitch)

# --- ARPEGGIATOR THREAD ---
def arpeggiator_loop():
    arp_ptr = 0
    arp_octave = 0
    direction = 1
    while running:
        if arp_active and held_pitches:
            sorted_held = sorted(list(held_pitches))
            pitch = sorted_held[arp_ptr % len(sorted_held)]
            final_pitch = pitch + (arp_octave * 12)
            # Default to green delay speed (0.2s) if delay is OFF
            current_speed = delay_time_sig.value if fx_states[1] > 0 else 0.2
            for v_idx in range(MAX_VOICES):
                voices_osc[v_idx].setFreq(midiToHz(final_pitch))
            arp_ptr += 1
            arp_octave += direction
            if abs(arp_octave) >= 3: direction *= -1
            time.sleep(current_speed)
        else:
            time.sleep(0.1)

t_arp = threading.Thread(target=arpeggiator_loop); t_arp.daemon = True; t_arp.start()

# --- DRUM MACHINE THREAD ---
def drum_loop():
    step = 0
    while running:
        if drum_mode > 0:
            # Silence mode (Red) logic
            is_silent = (drum_mode == 3 and random.random() < 0.25)
            
            if not is_silent:
                # Random repetition for Even (Green) or Odd (Amber)
                reps = random.randint(1, 4) if drum_mode in [1, 2] else 1
                inst = random.randint(0, 11)
                
                for _ in range(reps):
                    if step >= 16: break # Keep strictly to 16 beats
                    
                    if inst == 0: d_bd.freq = random.choice([50, 55, 60]); d_env.play()
                    elif inst == 1: d_snare.mul = 0.2; d_env.play()
                    elif inst == 2: d_hh.mul = 0.15; d_env.play()
                    elif inst == 3: d_fm.carrier = 220; d_env.play()
                    elif inst == 4: d_fm.carrier = 4000; d_env.play()
                    elif inst == 5: d_fm.carrier = 800; d_env.play()
                    elif inst == 6: d_fm.carrier = 140; d_env.play()
                    elif inst == 7: d_hh.mul = 0.08; d_env.play()
                    elif inst == 8: d_snare.mul = 0.4; d_env.play()
                    
                    step = (step + 1) % 16
                    time.sleep(delay_time_sig.value if fx_states[1] > 0 else 0.2)
            else:
                step = (step + 1) % 16
                time.sleep(delay_time_sig.value if fx_states[1] > 0 else 0.2)
        else:
            time.sleep(0.1)

t_drum = threading.Thread(target=drum_loop); t_drum.daemon = True; t_drum.start()

clear_all_leds(); refresh_grid()

def launchpad_listener():
    global cur_key, cur_scale, harms_sig, running, octave_offset, harms_up_held, harms_down_held, arp_active, drum_mode, drum_beats
    while running:
        if harms_up_held:
            harms_sig.value = min(60, harms_sig.value + 1.0)
            print(f"Harmonics: {int(harms_sig.value)} | Vol: {round(master_vol.value, 2)} | Key: {KEYS[cur_key]} | Scale: {SCALE_NAMES[cur_scale]}")
            refresh_grid(); time.sleep(0.1)
        if harms_down_held:
            harms_sig.value = max(5, harms_sig.value - 1.0)
            print(f"Harmonics: {int(harms_sig.value)} | Vol: {round(master_vol.value, 2)} | Key: {KEYS[cur_key]} | Scale: {SCALE_NAMES[cur_scale]}")
            refresh_grid(); time.sleep(0.1)

        with lp_lock: ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            is_top = (200 <= bid <= 207) if mode == "MK1" else (104 <= bid <= 111)
            if is_top:
                idx = (bid - 200) if mode == "MK1" else (bid - 104)
                if state > 0:
                    if idx == 0: cur_key = (cur_key + 1) % 12; apply_immediate_transpose()
                    elif idx == 1: cur_key = (cur_key - 1) % 12; apply_immediate_transpose()
                    elif idx == 2: cur_scale = (cur_scale + 1) % len(SCALE_NAMES)
                    elif idx == 3: cur_scale = (cur_scale - 1) % len(SCALE_NAMES)
                    elif idx == 4: harms_up_held = True
                    elif idx == 5: harms_down_held = True
                    elif idx == 6: master_vol.value = max(0.0, master_vol.value - 0.05)
                    elif idx == 7: master_vol.value = min(1.0, master_vol.value + 0.05)
                    
                    if idx in [0,1,2,3,6,7]:
                        print(f"Key: {KEYS[cur_key]} | Scale: {SCALE_NAMES[cur_scale]} | Volume: {round(master_vol.value, 2)}")
                        refresh_grid()
                else:
                    if idx == 4: harms_up_held = False
                    elif idx == 5: harms_down_held = False

            side_idx = (8 - (bid // 10)) if (mode == "MK2" and bid % 10 == 9) else (bid // 16) if (mode == "MK1" and bid % 16 == 8) else -1
            if side_idx == 0 and state > 0:
                fx_states[0] = (fx_states[0] + 1) % 4
                rev_mix_sig.value = [0.0, 0.3, 0.5, 0.65][fx_states[0]]
                rev_size_sig.value = [0.5, 0.4, 0.7, 0.95][fx_states[0]]
                print(f"Reverb: {['OFF', 'LOW', 'MED', 'HIGH'][fx_states[0]]} | Mix: {rev_mix_sig.value} | Size: {rev_size_sig.value}")
                refresh_grid()
            elif side_idx == 1 and state > 0:
                fx_states[1] = (fx_states[1] + 1) % 4
                delay_input_mix.value = [0.0, 0.3, 0.45, 0.6][fx_states[1]] 
                delay_time_sig.value = [0.0075, 0.2, 0.4, 1.0][fx_states[1]] 
                delay_feed_sig.value = [0.55, 0.6, 0.7, 0.8][fx_states[1]]
                print(f"Delay: {['OFF', 'LOW', 'MED', 'HIGH'][fx_states[1]]} | Time: {delay_time_sig.value}s | Feedback: {delay_feed_sig.value} | Input: {delay_input_mix.value}")
                refresh_grid()
            elif side_idx == 2 and state > 0:
                arp_active = not arp_active
                print(f"Arpeggiator: {'ON' if arp_active else 'OFF'}")
                refresh_grid()
            elif side_idx == 3 and state > 0:
                drum_mode = (drum_mode + 1) % 4
                print(f"Drums: {['OFF', 'GREEN (Even)', 'AMBER (Odd)', 'RED (Silence)'][drum_mode]}")
                refresh_grid()
            elif (side_idx == 4 or side_idx == 5) and state > 0:
                octave_offset = min(3, octave_offset + 1) if side_idx == 4 else max(-3, octave_offset - 1)
                apply_immediate_transpose()
                print(f"Octave: {octave_offset}"); refresh_grid()
            elif bid == SIDE_POWER_BTN and state > 0: 
                print("Power button pressed. Exiting..."); running = False
            elif not is_top:
                if mode == "MK2" and bid % 10 != 9: x, y_log = (bid % 10) - 1, (bid // 10) - 1
                elif mode == "MK1" and bid % 16 < 8: x, y_log = bid % 16, 7 - (bid // 16)
                else: x, y_log = -1, -1
                if 0 <= x < 8 and 0 <= y_log < 8:
                    if state > 0: play_note(bid, x, y_log)
                    else: stop_note(bid, x, y_log)
        time.sleep(0.001)

t = threading.Thread(target=launchpad_listener); t.daemon = True; t.start()
try:
    while running: time.sleep(0.1)
except KeyboardInterrupt: print("\nKeyboard Interrupt detected."); running = False
finally:
    if t.is_alive(): t.join()
    clear_all_leds(); lp.Close(); s.stop(); s.shutdown(); print("\nSynth stopped.")
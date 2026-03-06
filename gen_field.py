import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
Generative Field (Walker Logic)
====================================================================================
This script creates walker logic to navigate a stochastic soundscape, where four 
independent algorithmic agents move across an 8x8 grid to trigger and spatialize sound.
====================================================================================
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Button 4: Delay Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Button 5: Reverb Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Buttons 6-7: Main Volume (Amber 60%, Red at Peak)

- Side Buttons 0-3: Toggle Algorithmic Walkers (Markov, Brownian, Fractal, Genetic)
- Side Buttons 4-6: Speed Selectors (Half, Normal, Double Schumann Speed)
- Side Button 7: EXIT / POWER OFF (Blue/Cyan on Mk2, 2-sec Fade Out on press)
"""

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio'
BUFFER_SIZE = 512 

# --- 1. Launchpad Setup & Hardware Detection ---
mode = None
lp = launchpad.Launchpad()
lp_opened = False
if lp.Check(0, "Mini"):
    if lp.Open():
        mode = "Mk1"; lp_opened = True
        print("--- System: Launchpad Mk1/S/Mini detected ---")
        SOLO_BTNS = [200, 201, 202, 203] 
        VOL_BTNS = [206, 207] 
        DELAY_BTN = 204 
        REVERB_BTN = 205 
        EXIT_PWR_BTN = 120 
        SIDE_BTNS = [8, 24, 40, 56, 72, 88, 104] 
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2()
    if lp.Open():
        mode = "Mk2"; lp_opened = True
        print("--- System: Launchpad Mk2 detected ---")
        SOLO_BTNS = [104, 105, 106, 107] 
        VOL_BTNS = [110, 111] 
        DELAY_BTN = 108 
        REVERB_BTN = 109 
        EXIT_PWR_BTN = 19 
        SIDE_BTNS = [89, 79, 69, 59, 49, 39, 29] 

if not lp_opened:
    exit("Launchpad not detected. Please connect device.")

lp.Reset()

# --- 2. Audio Server Configuration ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()

# --- 3. Audio Engine & Synthesis Blocks (HEAVY GAIN STAGING) ---
sustain_mod = Sig(0.1) 
master_vol = Sig(0.6) 
master_vol_port = Port(master_vol, 4.0, 4.0)

# Generator Multipliers: Increased for saturated presence
fm_f = Sig(440); markov_v = FM(carrier=fm_f, ratio=[0.5, 0.51], index=10, mul=0.6)
br_f = Sig(220); brownian_v = MoogLP(LFO(freq=br_f, type=3, mul=0.7), freq=1200, res=0.5)
fr_f = Sig(880); fractal_v = Reson(PinkNoise(mul=0.15), freq=fr_f, q=10, mul=3.8) 
ge_f = Sig(110); genetic_v = LFO(freq=ge_f, type=1, sharp=0.5, mul=0.6)

gens = [markov_v, brownian_v, fractal_v, genetic_v]
gen_gains = [[Sig(0) for _ in range(4)] for _ in range(4)]
gen_ports = [[Port(sig, 0.05, sustain_mod) for sig in row] for row in gen_gains]
solo_sines = [Sine(freq=440, mul=0).out(i) for i in range(4)]

delay_fb = Sig(0.4); delay_t = Sig(0.25); rev_size = Sig(0.4) 

# --- 4. Quadrophonic Signal Matrix (Aggressive Mix) ---
for i in range(4):
    chan_mix = sum([gens[j] * gen_ports[j][i] for j in range(4)])
    chan_delay = Delay(chan_mix, delay=delay_t, feedback=delay_fb)
    chan_rev_wet = Freeverb(chan_mix + chan_delay, size=rev_size, damp=0.5, bal=1.0)
    
    # Mix Stage: Bumped to 0.75 Dry/Delay + 0.3 Reverb
    # This will push the Tanh harder for a thicker sound
    mix_stage = (chan_mix + chan_delay) * 0.75 + (chan_rev_wet * 0.3)
    final_sig = Tanh(mix_stage * master_vol_port)
    final_sig.out(i)

print("--- Audio Engine: High-Gain Logic Active (Saturated Mix) ---")

# --- 5. Helper Functions ---
def get_quad_gains(x, y):
    nx, ny = x / 7.0, (y - 1) / 7.0
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def lp_led_raw(bid, r, g, b=0):
    if not lp_opened: return
    if mode == "Mk2": lp.LedCtrlRaw(bid, int(r * 21), int(g * 21), int(b * 21))
    else: lp.LedCtrl(bid, r, g)

def lp_led_grid(x, y, r, g, b=0):
    bid = y * 16 + x if mode == "Mk1" else (7 - y) * 10 + x + 11
    lp_led_raw(bid, r, g, b)

def update_vol_leds():
    v = master_vol.value
    print(f"--- System: Master Volume at {v:.2f} ---")
    v_col = (0, 3) if v < 0.4 else (3, 3) if v < 0.7 else (2, 0) if v < 0.9 else (3, 0)
    for btn in VOL_BTNS: lp_led_raw(btn, *v_col)

# --- 6. State Management ---
schumann_base = 7.83
current_speed = schumann_base 
grid_occupancy = [0.0] * 64
walkers = [random.randint(0,63) for _ in range(4)]
active_algos = [False] * 4
rev_level = 1; delay_mode = 1; is_fading = False

OTONAL_ROOT = 27.5 
ALGO_NAMES = ["Markov", "Brownian", "Fractal", "Genetic"]
ALGO_COLS_BRIGHT = [(0,3,0), (3,3,0), (3,0,0), (0,3,3)]
ALGO_COLS_DIM = [(0,1,0), (1,1,0), (1,0,0), (0,1,1)]

def full_reset_sequence():
    global grid_occupancy, active_algos, is_fading, walkers, rev_level, delay_mode
    is_fading = True
    print("--- SEQUENCE: CAPACITY REACHED. RESETTING SYSTEM ---")
    master_vol_port.value = 0 
    time.sleep(4.1)
    for r in gen_gains:
        for s_sig in r: s_sig.value = 0
    grid_occupancy = [0.0] * 64; active_algos = [False] * 4
    walkers = [random.randint(0,63) for _ in range(4)]
    rev_level = 1; delay_mode = 1; rev_size.value = 0.4; delay_fb.value = 0.4
    if lp_opened:
        try:
            lp.Reset(); update_vol_leds()
            for btn in SOLO_BTNS: lp_led_raw(btn, 0, 3)
            for i, b in enumerate(SIDE_BTNS):
                lp_led_raw(b, *(ALGO_COLS_DIM[i] if i < 4 else (3,3) if i==5 else (0,1)))
            lp_led_raw(DELAY_BTN, 0, 3); lp_led_raw(REVERB_BTN, 0, 3)
            if mode == "Mk2": lp.LedCtrlRaw(EXIT_PWR_BTN, 10, 10, 63)
            else: lp_led_raw(EXIT_PWR_BTN, 1, 3)
        except: pass 
    master_vol_port.value = master_vol.value
    is_fading = False
    print("--- SEQUENCE: RESET COMPLETE ---")

# --- 7. Main Loop ---
try:
    print("--- Initialization: Setting Launchpad Default State ---")
    update_vol_leds()
    for btn in SOLO_BTNS: lp_led_raw(btn, 0, 3)
    for i, b in enumerate(SIDE_BTNS):
        lp_led_raw(b, *(ALGO_COLS_DIM[i] if i < 4 else (3,3) if i==5 else (0,1)))
    lp_led_raw(DELAY_BTN, 0, 3); lp_led_raw(REVERB_BTN, 0, 3)
    if mode == "Mk2": lp.LedCtrlRaw(EXIT_PWR_BTN, 10, 10, 63)
    else: lp_led_raw(EXIT_PWR_BTN, 1, 3)  
    
    last_step = time.time()
    while True:
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            if bid == EXIT_PWR_BTN and state > 0:
                print("--- System: Initiating 2s Fade Out and Shutdown ---")
                master_vol_port.value = 0
                time.sleep(2.0)
                break
            
            if not is_fading:
                if bid in SOLO_BTNS:
                    idx = SOLO_BTNS.index(bid)
                    solo_sines[idx].mul = 0.25 if state > 0 else 0
                    lp_led_raw(bid, 3 if state > 0 else 0, 0)
                    if state > 0: print(f"--- Audio: Solo Channel {idx} Active ---")
                
                if bid in SIDE_BTNS and state > 0:
                    idx = SIDE_BTNS.index(bid)
                    if idx < 4:
                        active_algos[idx] = not active_algos[idx]
                        lp_led_raw(bid, *(ALGO_COLS_BRIGHT[idx] if active_algos[idx] else ALGO_COLS_DIM[idx]))
                        print(f"--- Walker: {ALGO_NAMES[idx]} {'Enabled' if active_algos[idx] else 'Disabled'} ---")
                    elif idx in [4,5,6]:
                        speeds = ["Half", "Normal", "Double"]
                        current_speed = [schumann_base/2, schumann_base, schumann_base*2][idx-4]
                        print(f"--- Clock: Speed set to {speeds[idx-4]} ({current_speed:.2f} Hz) ---")
                        for i in range(4, 7): lp_led_raw(SIDE_BTNS[i], (3 if i-4 == idx-4 else 0), (idx-4+1 if i-4 == idx-4 else 1))
                
                if bid == REVERB_BTN and state > 0:
                    rev_level = (rev_level + 1) % 4
                    rev_size.value = [0, 0.4, 0.6, 0.85][rev_level]
                    lp_led_raw(bid, *[(1,1), (0,3), (3,3), (3,0)][rev_level])
                    print(f"--- FX: Reverb Level {rev_level} (Size: {rev_size.value}) ---")
                
                if bid == DELAY_BTN and state > 0:
                    delay_mode = (delay_mode + 1) % 4
                    vals = [(0, 0, (1,1)), (0.4, 0.25, (0,3)), (0.6, 0.5, (3,3)), (0.8, 0.125, (3,0))]
                    delay_fb.value, delay_t.value = vals[delay_mode][0], vals[delay_mode][1]
                    lp_led_raw(bid, *vals[delay_mode][2])
                    print(f"--- FX: Delay Mode {delay_mode} (FB: {delay_fb.value}) ---")
                
                if bid in VOL_BTNS and state > 0:
                    master_vol.value = max(0.0, min(1.0, master_vol.value + (-0.05 if VOL_BTNS.index(bid) == 0 else 0.05)))
                    update_vol_leds()

        if not is_fading and time.time() - last_step > (1.0 / current_speed):
            curr_time = time.time()
            occ_count = sum(1 for x in grid_occupancy if x > 0)
            sustain_mod.value = 0.1 + (occ_count / 64.0) * 3.9
            
            if occ_count >= 64: threading.Thread(target=full_reset_sequence).start()
            
            for i in range(4):
                if active_algos[i]:
                    move = random.choice([-1, 1, -8, 8])
                    walkers[i] = (walkers[i] + move) % 64
                    grid_occupancy[walkers[i]] = curr_time 
                    gx, gy = walkers[i] % 8, walkers[i] // 8
                    lp_led_grid(gx, gy, *ALGO_COLS_BRIGHT[i])
                    
                    time_diff = curr_time - grid_occupancy[walkers[i]]
                    harmonic = 8 + gx + (gy * 8)
                    
                    slope_comp = 1.0 if i == 2 else 1.0 / math.sqrt(harmonic/8) 
                    algo_amp = max(0.05, 1.0 - (time_diff * 0.2)) * slope_comp
                    [fm_f, br_f, fr_f, ge_f][i].value = OTONAL_ROOT * harmonic
                    
                    g_vals = get_quad_gains(gx, gy + 1)
                    for ch in range(4): gen_gains[i][ch].value = g_vals[ch] * algo_amp
            
            last_step = time.time()
        time.sleep(0.002)

except KeyboardInterrupt: pass
finally:
    s.stop(); s.shutdown(); lp.Reset(); lp.Close()
    print("--- System Offline ---")
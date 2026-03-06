import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
Formalized music
==================================================================================
This script retraces the main stages of Iannis Xenakis's text, arranging the iconic 
sounds in conflict with each other in quadraphonic sound, as is predictable, according 
to game theory; the grid is occupied with known statistical models and algorithms.
==================================================================================
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Button 4: Delay Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Button 5: Reverb Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Buttons 6-7: Main Volume (Amber 60%, Red at Peak)

- Side Buttons 0-3: Toggle Stochastic Engines (Markov, Analog, GENDYN, Poisson)
- Side Buttons 4-6: Density Selectors (Half, Normal, Double Density)
- Side Button 7: EXIT / POWER OFF (Blue/Cyan, 2-sec Fade Out on press)
"""

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio'
BUFFER_SIZE = 512 

# --- 1. Launchpad Setup ---
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

# --- 3. Xenakis Vector Synthesis (Recalibrated Red Engine) ---
sustain_mod = Sig(0.1) 
master_vol = Sig(0.6)
master_vol_port = Port(master_vol, 4.0, 4.0)

# Sound Sources: Red engine (vector_gendyn) reduced from 3.8 to 2.6
vector_stochastic = Sig(440); logic_markov = FM(carrier=vector_stochastic, ratio=[0.5, 0.51], index=10, mul=0.6)
vector_analogique = Sig(220); analogique_v = MoogLP(LFO(freq=vector_analogique, type=3, mul=0.7), freq=1200, res=0.5)
vector_gendyn = Sig(880); gendyn_v = Reson(PinkNoise(mul=0.15), freq=vector_gendyn, q=10, mul=2.6) 
vector_achorripsis = Sig(110); achorripsis_v = LFO(freq=vector_achorripsis, type=1, sharp=0.5, mul=0.6)

xenakis_sets = [logic_markov, analogique_v, gendyn_v, achorripsis_v]

spatial_matrix = [[Sig(0) for _ in range(4)] for _ in range(4)]
spatial_ports = [[Port(sig, 0.05, sustain_mod) for sig in row] for row in spatial_matrix]

solo_sines = [Sine(freq=440, mul=0).out(i) for i in range(4)]

delay_fb = Sig(0.4); delay_t = Sig(0.25); rev_size = Sig(0.4) 

# --- 4. Quadrophonic Signal Matrix ---
for i in range(4):
    set_union = sum([xenakis_sets[j] * spatial_ports[j][i] for j in range(4)])
    chan_delay = Delay(set_union, delay=delay_t, feedback=delay_fb)
    chan_rev_wet = Freeverb(set_union + chan_delay, size=rev_size, damp=0.5, bal=1.0)
    
    # Mix Stage: Using 0.7 Dry/Delay + 0.25 Reverb for better balance
    mix_stage = (set_union + chan_delay) * 0.7 + (chan_rev_wet * 0.25)
    
    final_sig = Tanh(mix_stage * master_vol_port)
    final_sig.out(i)

print("--- Audio Engine Started: Red Generator Calibrated for Balanced Mix ---")

# --- 5. Formalized Music Helper Functions ---
STRATEGIC_PAYOFF = [[0.1, 0.5, 0.9], [0.4, 0.1, 0.2], [0.8, 0.3, 0.1]] 
current_state_k = 1

def boolean_intersection(set_a, set_b):
    return (set_a % 8 == set_b % 8) or (set_a // 8 == set_b // 8)

def sieve_theory(n, modules):
    for m, shift in modules:
        if n % m == shift: return True
    return False

def quantize_to_sieve(root, index, modules):
    search_idx = int(index)
    for offset in range(32):
        if sieve_theory(search_idx + offset, modules): return root * (search_idx + offset)
        if sieve_theory(search_idx - offset, modules): return root * (search_idx - offset)
    return root * search_idx

def cauchy_dist(a): 
    return a * math.tan(math.pi * (random.random() - 0.5))

def poisson_density(mu):
    l, k, p = math.exp(-mu), 0, 1
    while p > l: k += 1; p *= random.random()
    return k - 1

MARKOV_TRANSITION = [[0.1, 0.7, 0.2], [0.4, 0.2, 0.4], [0.2, 0.7, 0.1]]
def markov_step(state):
    r, cumulative = random.random(), 0
    for next_state, prob in enumerate(MARKOV_TRANSITION[state]):
        cumulative += prob
        if r <= cumulative: return next_state
    return state

def calculate_spatial_vector(x, y):
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

# --- 6. Stochastic State Management ---
schumann_base = 7.83
stochastic_density = schumann_base 
grid_occupancy = [0.0] * 64
glissandi_points = [random.randint(0,63) for _ in range(4)]
active_stochastic_states = [False] * 4
rev_level = 1; delay_mode = 1; is_fading = False

OTONAL_ROOT = 27.5 
ALGO_COLS_BRIGHT = [(0,3,0), (3,3,0), (3,0,0), (0,3,3)]
ALGO_COLS_DIM = [(0,1,0), (1,1,0), (1,0,0), (0,1,1)]

def total_entropy_reset():
    global grid_occupancy, active_stochastic_states, is_fading, glissandi_points
    is_fading = True
    print("--- SEQUENCE: CAPACITY REACHED. RESETTING SYSTEM ---")
    master_vol_port.value = 0 
    time.sleep(4.1)
    for r in spatial_matrix:
        for s_sig in r: s_sig.value = 0
    grid_occupancy = [0.0] * 64; active_stochastic_states = [False] * 4
    glissandi_points = [random.randint(0,63) for _ in range(4)]
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
    
    last_event = time.time(); rhythm_sieve = 0
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
                        active_stochastic_states[idx] = not active_stochastic_states[idx]
                        lp_led_raw(bid, *(ALGO_COLS_BRIGHT[idx] if active_stochastic_states[idx] else ALGO_COLS_DIM[idx]))
                        print(f"--- Engine: Engine {idx} {'Enabled' if active_stochastic_states[idx] else 'Disabled'} ---")
                    elif idx in [4,5,6]:
                        speeds = ["Half", "Normal", "Double"]
                        stochastic_density = [schumann_base/2, schumann_base, schumann_base*2][idx-4]
                        print(f"--- Clock: Density set to {speeds[idx-4]} ({stochastic_density:.2f} Hz) ---")
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

        if not is_fading and time.time() - last_event > (1.0 / stochastic_density):
            rhythm_sieve += 1
            if sieve_theory(rhythm_sieve, [(3, 0), (4, 0)]):
                curr_t = time.time()
                occ_count = sum(1 for x in grid_occupancy if x > 0)
                sustain_mod.value = 0.1 + (occ_count / 64.0) * 3.9
                
                if occ_count >= 64: threading.Thread(target=total_entropy_reset).start()
                
                for i in range(4):
                    if active_stochastic_states[i]:
                        interact = boolean_intersection(glissandi_points[i], glissandi_points[(i+1)%4])
                        strategy_mod = STRATEGIC_PAYOFF[i%3][random.randint(0,2)] if interact else 1.0
                        
                        glissandi_points[i] = (glissandi_points[i] + random.choice([-1, 1, -8, 8])) % 64
                        grid_occupancy[glissandi_points[i]] = curr_t 
                        gx, gy = glissandi_points[i] % 8, glissandi_points[i] // 8
                        lp_led_grid(gx, gy, *ALGO_COLS_BRIGHT[i])
                        
                        h_idx = (8 + gx + (gy * 8)) * strategy_mod
                        slope_comp = 1.0 if i == 2 else 1.0 / math.sqrt(h_idx/8)
                        algo_amp = max(0.05, 1.0 - ((curr_t - grid_occupancy[glissandi_points[i]]) * 0.2)) * slope_comp
                        
                        if i == 0: vector_stochastic.value = quantize_to_sieve(OTONAL_ROOT, h_idx, [(3,0), (5,0)])
                        elif i == 1: 
                            current_state_k = markov_step(current_state_k)
                            vector_analogique.value = quantize_to_sieve(OTONAL_ROOT, [8, 25, 49][current_state_k] + (h_idx % 16), [(4,0), (7,1)])
                        elif i == 2: 
                            raw_f = abs(vector_gendyn.value + cauchy_dist(100)) % 2000
                            vector_gendyn.value = quantize_to_sieve(OTONAL_ROOT, raw_f/OTONAL_ROOT, [(11,0), (13,0)])
                        elif i == 3: vector_achorripsis.value = OTONAL_ROOT * (h_idx + poisson_density(2))
                        
                        g_vals = calculate_spatial_vector(gx, gy + 1)
                        for ch in range(4): spatial_matrix[i][ch].value = g_vals[ch] * algo_amp
            
            last_event = time.time()
        time.sleep(0.002)

except KeyboardInterrupt: pass
finally:
    s.stop(); s.shutdown(); lp.Reset(); lp.Close()
    print("--- System Offline: All Formalized Processes Stopped ---")
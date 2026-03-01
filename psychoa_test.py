import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
Experiential psychoacoustics test
============================================================

- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red)
- Top Button 5: EXIT / POWER OFF (Index 5)
- Top Buttons 6-7: Adjust Master Volu

- Side Button 0: Toggles Auto-Scan (Pink Noise, Green LED)
- Side Button 1: Toggles Manual Mode (Sine Wave, Green LED)
- Side Button 2: Toggles Ascending Shepherd (Amber)
- Side Button 3: Toggles Descending Shepherd (Yellow)
- Side Button 4: Toggles Risset Accelerando (Blue)
- Side Button 5: Toggles Risset Decelerando (Cyan)
- Side Button 6: Doppler Illusion (Cycle: Low -> Mid -> High -> Off)
- Side Button 7: Binaural Beats (Cycle: 36Hz -> 72Hz -> 108Hz -> Off)

"""
AUDIO_DEVICE = 10
AUDIO_HOST = 'asio' 
BUFFER_SIZE = 512 

# --- 1. Launchpad Setup ---
mode = None
lp = launchpad.Launchpad()
if lp.Check(0, "Mini"):
    lp.Open(); mode = "Mk1"
    print("--- System: Launchpad Mk1/S/Mini detected ---")
    SOLO_BTNS = [200, 201, 202, 203] 
    EXIT_PWR_BTN = 205
    VOL_BTNS = [206, 207] 
    SIDE_BTNS = [8, 24, 40, 56, 72, 88, 104, 120] 
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(); mode = "Mk2"
    print("--- System: Launchpad Mk2 detected ---")
    SOLO_BTNS = [104, 105, 106, 107] 
    EXIT_PWR_BTN = 109
    VOL_BTNS = [110, 111] 
    SIDE_BTNS = [89, 79, 69, 59, 49, 39, 29, 19] 
else:
    exit("Launchpad not detected.")
lp.Reset()

# --- 2. Audio Server ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE,winhost=AUDIO_HOST)
s.setOutputDevice(10)
s.deactivateMidi()
s.boot().start()

# --- 3. Audio Engine ---
noise = PinkNoise(mul=0.2)
sine = Sine(freq=440, mul=0.2)

# --- Shepherd Engine ---
shep_gate = Sig(0)
shep_phasor = Phasor(freq=0.05, mul=1) 
shep_pos = shep_phasor * shep_gate
shep_oscillators = []
for i in range(12):
    raw_pos = (shep_pos + (i / 12.0)) % 1.0
    freq_sig = Sig(110) * Pow(2, raw_pos * 10) 
    amp_mask = Cos(raw_pos * math.pi * 2 - math.pi, mul=0.5, add=0.5)
    shep_oscillators.append(Sine(freq=freq_sig, mul=amp_mask * 0.15))
shep_sum = sum(shep_oscillators)

# --- Risset Engine ---
risset_gate = Sig(0)
risset_phasor = Phasor(freq=0.04, mul=1) 
risset_pos = risset_phasor * risset_gate
env_table = CosTable([(0,0), (1000,1), (4000, .5), (8192,0)])
risset_pulses = []
for i in range(12):
    r_pos = (risset_pos + (i / 12.0)) % 1.0
    pulse_freq = Sig(0.5) * Pow(2, r_pos * 4) 
    r_amp = Cos(r_pos * math.pi * 2 - math.pi, mul=0.5, add=0.5)
    click = Metro(time=1.0/pulse_freq).play()
    strike = TrigEnv(click, table=env_table, dur=0.15, mul=r_amp)
    # Using Reson (Resonant Filter) instead of BPF to avoid the NameError
    filt_noise = Reson(PinkNoise(mul=strike), freq=600, q=2)
    risset_pulses.append(filt_noise)
risset_sum = sum(risset_pulses) * 0.6

# --- Doppler Engine (Cycling Frequencies) ---
dopp_gate = Sig(0)
dopp_depth = Sig(0)
dopp_freq_mod = Sine(freq=0.5, mul=dopp_depth, add=440) 
doppler_sine = Sine(freq=dopp_freq_mod, mul=dopp_gate * 0.3)

# --- Binaural Engine ---
bin_gate = Sig(0)
bin_carrier = Sig(220)
bin_beat = 4     
bin_oscs = [
    Sine(freq=bin_carrier, mul=bin_gate * 0.1),            
    Sine(freq=bin_carrier + bin_beat, mul=bin_gate * 0.1), 
    Sine(freq=bin_carrier, mul=bin_gate * 0.1),            
    Sine(freq=bin_carrier + bin_beat, mul=bin_gate * 0.1)  
]

# Control signals
noise_gains = [Sig(0) for _ in range(4)]
noise_ports = [Port(sig, 0.05, 0.05) for sig in noise_gains]
sine_gains = [Sig(0) for _ in range(4)]
sine_ports = [Port(sig, 0.05, 0.05) for sig in sine_gains]
shep_scan_gains = [Sig(0) for _ in range(4)]
shep_scan_ports = [Port(sig, 0.05, 0.05) for sig in shep_scan_gains]
risset_gains = [Sig(0) for _ in range(4)]
risset_ports = [Port(sig, 0.05, 0.05) for sig in risset_gains]
dopp_scan_gains = [Sig(0) for _ in range(4)]
dopp_scan_ports = [Port(sig, 0.05, 0.05) for sig in dopp_scan_gains]

master_vol = Sig(0.6) 
master_vol_port = Port(master_vol, 0.1, 0.1)

for i in range(4):
    out = ((noise * noise_ports[i]) + (sine * sine_ports[i]) + \
           (shep_sum * shep_scan_ports[i]) + (risset_sum * risset_ports[i]) + \
           (doppler_sine * dopp_scan_ports[i]) + bin_oscs[i]) * master_vol_port
    out.out(i)

print("--- Audio Engine Started ---")

# --- 4. Helper Functions ---
def get_quad_gains(x, y):
    nx, ny = x / 7.0, (y - 1) / 7.0
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def lp_led_raw(bid, r, g, b=0):
    if mode == "Mk2": lp.LedCtrlRaw(bid, int(r * 21), int(g * 21), int(b * 21))
    else: lp_led_raw(bid, r, g)

def lp_led_grid(x, y, r, g, b=0):
    bid = y * 16 + x if mode == "Mk1" else (7 - y) * 10 + x + 11
    lp_led_raw(bid, r, g, b)

def get_xy_from_raw(bid):
    if mode == "Mk1":
        x, y = bid % 16, bid // 16
        if x < 8 and y < 8: return x, y
    else:
        r, c = bid // 10, bid % 10
        if 1 <= r <= 8 and 1 <= c <= 8: return c - 1, 8 - r
    return None

def update_vol_leds():
    vol = master_vol.value
    print(f"--- Volume: {vol:.2f} ---")
    v_col = (0, 3) if vol < 0.4 else (3, 3) if vol < 0.7 else (2, 0) if vol < 0.9 else (3, 0)
    for btn in VOL_BTNS: lp_led_raw(btn, *v_col)

# --- 5. State Management ---
scan_active = manual_active = shep_asc_active = shep_des_active = r_acc_active = r_dec_active = False
dopp_mode = 0 # 0: Off, 1: 20Hz Depth, 2: 60Hz, 3: 120Hz
bin_mode = 0 
pressed_top_btns = set()
pressed_grid_cells = set() 

for btn in SOLO_BTNS + SIDE_BTNS: lp_led_raw(btn, 0, 3)
update_vol_leds()
if mode == "Mk2": lp.LedCtrlRaw(EXIT_PWR_BTN, 10, 63, 10) 
else: lp_led_raw(EXIT_PWR_BTN, 1, 3)

# --- 6. Main Loop ---
try:
    print("--- Starting V2 Loop ---")
    shep_step_interval = 1.0 / 7.83 
    last_step_time = time.time()
    grid_idx = -1
    scan_gains = shep_gains = r_gains = dopp_gains = [0.0] * 4
    last_side_states = {btn: 0 for btn in SIDE_BTNS}

    while True:
        current_time = time.time()
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            if bid == EXIT_PWR_BTN and state > 0: break 
            
            if bid in SIDE_BTNS:
                idx = SIDE_BTNS.index(bid)
                if state > 0 and last_side_states[bid] == 0:
                    if idx == 0: scan_active = not scan_active
                    elif idx == 1: manual_active = not manual_active
                    elif idx == 2: shep_asc_active, shep_des_active = not shep_asc_active, False; shep_phasor.freq = 0.05
                    elif idx == 3: shep_des_active, shep_asc_active = not shep_des_active, False; shep_phasor.freq = -0.05
                    elif idx == 4: r_acc_active, r_dec_active = not r_acc_active, False; risset_phasor.freq = 0.04
                    elif idx == 5: r_dec_active, r_acc_active = not r_dec_active, False; risset_phasor.freq = -0.04
                    elif idx == 6: 
                        dopp_mode = (dopp_mode + 1) % 4
                        dopp_depth.value = [0, 20, 60, 120][dopp_mode]
                        print(f"--- Doppler: Mode {dopp_mode} ---") if dopp_mode > 0 else print("--- Doppler: Off ---")
                    elif idx == 7: 
                        bin_mode = (bin_mode + 1) % 4
                        bin_carrier.value = [0, 36, 72, 108][bin_mode]
                        print(f"--- Binaural: {bin_carrier.value} Hz ---") if bin_mode > 0 else print("--- Binaural: Off ---")
                    
                    shep_gate.value = 1 if (shep_asc_active or shep_des_active) else 0
                    risset_gate.value = 1 if (r_acc_active or r_dec_active) else 0
                    dopp_gate.value = 1 if dopp_mode > 0 else 0
                    bin_gate.value = 1 if bin_mode > 0 else 0
                    
                    for i, b in enumerate(SIDE_BTNS):
                        act_list = [scan_active, manual_active, shep_asc_active, shep_des_active, r_acc_active, r_dec_active, (dopp_mode > 0), (bin_mode > 0)]
                        act = act_list[i] if i < len(act_list) else False
                        if i < 4: lp_led_raw(b, (3 if act else 0), (0 if act else 3))
                        elif i == 4: lp_led_raw(b, 0, 0, 3 if act else 1)
                        elif i == 5: lp_led_raw(b, 0, 3 if act else 1, 3 if act else 1)
                        elif i == 6: lp_led_raw(b, 3 if act else 1, 0, 0)
                        elif i == 7: lp_led_raw(b, 3 if act else 1, 0, 3 if act else 1)
                last_side_states[bid] = state

            elif bid in SOLO_BTNS:
                if state > 0: pressed_top_btns.add(bid); lp_led_raw(bid, 3, 0)
                else: 
                    if bid in pressed_top_btns: pressed_top_btns.remove(bid)
                    lp_led_raw(bid, 0, 3)

            elif bid in VOL_BTNS:
                if state > 0:
                    idx = VOL_BTNS.index(bid)
                    master_vol.value = max(0.0, min(1.0, master_vol.value + (-0.05 if idx == 0 else 0.05)))
                    update_vol_leds()
            
            else:
                coords = get_xy_from_raw(bid)
                if coords and manual_active:
                    gx, gy = coords
                    if state > 0: pressed_grid_cells.add((gx, gy)); lp_led_grid(gx, gy, 0, 3)
                    else:
                        if (gx, gy) in pressed_grid_cells: pressed_grid_cells.remove((gx, gy)); lp_led_grid(gx, gy, 0, 0)

        if (scan_active or shep_asc_active or shep_des_active or r_acc_active or r_dec_active or dopp_mode > 0):
            if current_time - last_step_time >= shep_step_interval:
                if grid_idx >= 0:
                    px, py = grid_idx % 8, grid_idx // 8
                    if (px, py) not in pressed_grid_cells: lp_led_grid(px, py, 0, 0)
                is_rev = shep_asc_active or r_acc_active
                grid_idx = (grid_idx - 1) % 64 if is_rev else (grid_idx + 1) % 64
                sx, sy = grid_idx % 8, grid_idx // 8
                if scan_active: scan_gains = get_quad_gains(sx, sy + 1)
                if shep_asc_active or shep_des_active: shep_gains = get_quad_gains(sx, sy + 1)
                if r_acc_active or r_dec_active: r_gains = get_quad_gains(sx, sy + 1)
                if dopp_mode > 0: dopp_gains = get_quad_gains(sx, sy + 1)
                
                lp_led_grid(sx, sy, 
                    (3 if shep_asc_active or shep_des_active or dopp_mode > 0 else 0), 
                    (3 if scan_active else 0), 
                    (3 if r_acc_active or r_dec_active else 0))
                last_step_time = current_time

        manual_gains = [0.0] * 4
        if manual_active and pressed_grid_cells:
            for (mx, my) in pressed_grid_cells:
                gains = get_quad_gains(mx, my + 1)
                for i in range(4): manual_gains[i] = max(manual_gains[i], gains[i])

        for i in range(4):
            noise_gains[i].value = (scan_gains[i] if scan_active else 0)
            shep_scan_gains[i].value = (shep_gains[i] if shep_asc_active or shep_des_active else 0)
            risset_gains[i].value = (r_gains[i] if r_acc_active or r_dec_active else 0)
            dopp_scan_gains[i].value = (dopp_gains[i] if dopp_mode > 0 else 0)
            sine_gains[i].value = 1.0 if (len(SOLO_BTNS) > i and SOLO_BTNS[i] in pressed_top_btns) else manual_gains[i]
            
        time.sleep(0.005)

except KeyboardInterrupt: pass
finally:
    s.stop(); s.shutdown(); lp.Reset(); lp.Close()
    print("--- Goodbye ---")
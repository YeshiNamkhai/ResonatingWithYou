import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
4-Channel Audio & Grid Test V2
==============================
- Side Button 0: Toggles Auto-Scan (Pink Noise, Green LED)
- Side Button 1: Toggles Manual Mode (Sine Wave, Green LED on press)
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Buttons 6-7: Main Volume (Amber 60%)
- Side Button 6: Exit
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
    TOP_BTNS = [200, 201, 202, 203] # Top row 0-3
    VOL_BTNS = [206, 207] # Top row 6-7
    SIDE_BTNS = [8, 24] # Side buttons 0 (Row 0) and 1 (Row 1)
    EXIT_BTN = 207
    SIDE_POWER_BTN = 104 # Side button 6
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(); mode = "Mk2"
    print("--- System: Launchpad Mk2 detected ---")
    TOP_BTNS = [104, 105, 106, 107] # Top row 0-3
    VOL_BTNS = [110, 111] # Top row 6-7
    SIDE_BTNS = [89, 79] # Side buttons 0 (Top) and 1 (Below)
    EXIT_BTN = 111
    SIDE_POWER_BTN = 29 # Side button 6
else:
    exit("Launchpad not detected.")
lp.Reset()

# --- 2. Audio Server ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()

# --- 3. Audio Engine ---
# Source 1: Pink Noise (Grid Scan)
noise = PinkNoise(mul=0.2)
# Source 2: Sine Wave (Manual Mode & Top Buttons)
sine = Sine(freq=440, mul=0.2)

# Control signals
noise_gains = [Sig(0) for _ in range(4)]
noise_ports = [Port(sig, 0.05, 0.05) for sig in noise_gains]

sine_gains = [Sig(0) for _ in range(4)]
sine_ports = [Port(sig, 0.05, 0.05) for sig in sine_gains]

# Master Volume
master_vol = Sig(0.6)
master_vol_port = Port(master_vol, 0.1, 0.1)

# Route to outputs
outputs = []
for i in range(4):
    out = ((noise * noise_ports[i]) + (sine * sine_ports[i])) * master_vol_port
    out.out(i)
    outputs.append(out)

print("--- Audio Engine Started ---")

# --- 4. Helper Functions ---
def get_quad_gains(x, y):
    # x in 0..7, y in 1..8 (1 is top row)
    nx = x / 7.0
    ny = (y - 1) / 7.0
    # 0=TL, 1=TR, 2=BL, 3=BR
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def lp_led_raw(bid, r, g):
    if mode == "Mk2":
        lp.LedCtrlRaw(bid, int(r * 21), int(g * 21), 0)
    else:
        lp.LedCtrlRaw(bid, r, g)

def lp_led_grid(x, y, r, g):
    if mode == "Mk1":
        bid = y * 16 + x
    else: # Mk2
        bid = (7 - y) * 10 + x + 11
    lp_led_raw(bid, r, g)

def get_xy_from_raw(bid):
    """Returns (x, y) 0-7, 0-7 from raw button ID. Returns None if not grid."""
    if mode == "Mk1":
        x = bid % 16
        y = bid // 16
        if x < 8 and y < 8: return x, y
    else: # Mk2
        # Mk2 IDs: 11-18, 21-28 ... 81-88
        r = bid // 10
        c = bid % 10
        if 1 <= r <= 8 and 1 <= c <= 8:
            return c - 1, 8 - r
    return None

# --- 5. State Management ---
scan_active = False
manual_active = False
pressed_top_btns = set()
pressed_grid_cells = set() # Stores (x,y) of manually held grid buttons

# Initialize Control LEDs (Green)
for btn in TOP_BTNS: lp_led_raw(btn, 0, 3)
for btn in SIDE_BTNS: lp_led_raw(btn, 0, 3)
lp_led_raw(EXIT_BTN, 0, 3)

if mode == "Mk2": lp.LedCtrlRaw(SIDE_POWER_BTN, 10, 10, 63)
else: lp_led_raw(SIDE_POWER_BTN, 1, 3)

def update_vol_leds():
    vol = master_vol.value
    if vol < 0.4: v_col = (0, 3)      # Green
    elif vol < 0.7: v_col = (3, 3)    # Amber
    elif vol < 0.9: v_col = (2, 0)    # Red
    else: v_col = (3, 0)              # Intense Red
    for btn in VOL_BTNS:
        lp_led_raw(btn, *v_col)

update_vol_leds()

# --- 6. Main Loop ---
try:
    print("--- Starting V2 Loop ---")
    
    step_interval = 4.0 / 64.0
    last_step_time = time.time() - step_interval
    grid_idx = -1
    
    # Current calculated gains
    scan_gains = [0.0] * 4
    manual_gains = [0.0] * 4
    
    # Button state tracking for toggles
    last_side_states = {btn: 0 for btn in SIDE_BTNS}

    while True:
        current_time = time.time()
        
        # --- Input Handling ---
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            
            # Exit
            #if bid == EXIT_BTN and state > 0:
            #    break
            
            if bid == SIDE_POWER_BTN and state > 0:
                break
            
            # Side Buttons (Toggles)
            if bid in SIDE_BTNS:
                idx = SIDE_BTNS.index(bid)
                # Toggle on press only
                if state > 0 and last_side_states[bid] == 0:
                    if idx == 0: # Side 0: Scan Toggle
                        scan_active = not scan_active
                        # Update LED: Red if Active, Green if Idle
                        col = (3, 0) if scan_active else (0, 3)
                        lp_led_raw(bid, *col)
                        if not scan_active:
                            # Clear scan LED if stopping
                            if grid_idx >= 0:
                                px, py = grid_idx % 8, grid_idx // 8
                                lp_led_grid(px, py, 0, 0)
                                grid_idx = -1
                                
                    elif idx == 1: # Side 1: Manual Toggle
                        manual_active = not manual_active
                        # Update LED: Red if Active, Green if Idle
                        col = (3, 0) if manual_active else (0, 3)
                        lp_led_raw(bid, *col)
                        if not manual_active:
                            # Clear any manual LEDs
                            for (gx, gy) in pressed_grid_cells:
                                lp_led_grid(gx, gy, 0, 0)
                            pressed_grid_cells.clear()
                            
                last_side_states[bid] = state

            # Top Buttons (Momentary)
            elif bid in TOP_BTNS:
                if state > 0:
                    pressed_top_btns.add(bid)
                    lp_led_raw(bid, 3, 0) # Red when pressed
                else:
                    if bid in pressed_top_btns: pressed_top_btns.remove(bid)
                    lp_led_raw(bid, 0, 3) # Green when released

            # Volume Buttons
            elif bid in VOL_BTNS:
                if state > 0:
                    idx = VOL_BTNS.index(bid)
                    if idx == 0: # Vol -
                        master_vol.value = max(0.0, master_vol.value - 0.05)
                    else: # Vol +
                        master_vol.value = min(1.0, master_vol.value + 0.05)
                    print(f"Master Volume: {master_vol.value:.2f}")
                    update_vol_leds()

            # Grid Buttons (Manual Mode)
            else:
                coords = get_xy_from_raw(bid)
                if coords:
                    gx, gy = coords
                    if manual_active:
                        if state > 0:
                            pressed_grid_cells.add((gx, gy))
                            lp_led_grid(gx, gy, 0, 3) # Green
                        else:
                            if (gx, gy) in pressed_grid_cells:
                                pressed_grid_cells.remove((gx, gy))
                                lp_led_grid(gx, gy, 0, 0)

        # --- Logic: Scan ---
        # Scan runs if Side 0 is Active AND no Top buttons are held (Pause feature)
        is_paused = len(pressed_top_btns) > 0
        
        if scan_active and not is_paused:
            if current_time - last_step_time >= step_interval:
                # Clear prev
                if grid_idx >= 0:
                    px, py = grid_idx % 8, grid_idx // 8
                    # Only turn off if not currently held in manual mode
                    if (px, py) not in pressed_grid_cells:
                        lp_led_grid(px, py, 0, 0)
                
                grid_idx = (grid_idx + 1) % 64
                sx, sy = grid_idx % 8, grid_idx // 8
                
                # Calculate gains
                scan_gains = get_quad_gains(sx, sy + 1)
                
                # Light up
                lp_led_grid(sx, sy, 0, 3)
                last_step_time = current_time
        elif not scan_active or is_paused:
            # If paused or stopped, silence scan noise
            scan_gains = [0.0] * 4
            if is_paused: last_step_time = current_time # Prevent jump on resume

        # --- Logic: Manual ---
        manual_gains = [0.0] * 4
        if manual_active and pressed_grid_cells:
            # If multiple cells pressed, we could average them or just pick last.
            # Let's sum/max them. For simplicity, take the last added one or max.
            # To support chords properly requires more complex audio logic.
            # Here we just take the "latest" or max amplitude for each channel.
            for (mx, my) in pressed_grid_cells:
                gains = get_quad_gains(mx, my + 1)
                for i in range(4):
                    manual_gains[i] = max(manual_gains[i], gains[i])

        # --- Audio Update ---
        for i in range(4):
            # Noise is driven by Scan
            noise_gains[i].value = scan_gains[i]
            
            # Sine is driven by Manual Grid OR Top Buttons
            target_sine = manual_gains[i]
            
            # Top buttons override/add to sine (Solo channel)
            if TOP_BTNS[i] in pressed_top_btns:
                target_sine = 1.0
            
            sine_gains[i].value = target_sine
            
        time.sleep(0.005)

except KeyboardInterrupt:
    pass
finally:
    for sig in noise_gains + sine_gains: sig.value = 0
    s.stop()
    s.shutdown()
    time.sleep(0.5)
    lp.Reset()
    lp.Close()
    print("--- Goodbye ---")

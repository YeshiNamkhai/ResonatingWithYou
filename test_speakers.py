import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
4-Channel Audio & Grid Test
============================================================
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Button 4: Toggles Auto-Scan (Pink Noise, Green/Red)
- Top Button 5: Toggles Manual Mode (Sine Wave, Green/Red)
- Top Buttons 6-7: Main Volume (Amber 60%)

- Side Button 6: EXIT / POWER OFF (Blue/Cyan)

============================================================
The soundstage is arranged in quadraphonic fashion, ideally 
using four identical speakers: 
Ch0 --> Spk1, Ch1 --> Spk2, Ch2 --> Spk3, Ch3 --> Spk4; 
interpolation takes place between cells, for intermediate values.
```
    1          FRONT Speakers             2     
     +-----------------------------------+ 
     |  (0,0)                     (7,0)  |
     |          <-------------->         |
     |      ^                       ^    |
     |      |                       |    |
     |      |        8x8 GRID       |    |
     |      |                       |    |
     |      v                       v    |
     |          <-------------->         |
     |  (0,7)                     (7,7)  |
     +-----------------------------------+  
    3          REAR speakers              4

============================================================
get_quad_gains(x, y)

       (0,0)  nx = x / 7.0  (1,0)
         TL ----------------- TR
          |        |          |
          |     (nx, ny)      |  ny = (y - 1) / 7.0
          |        |          |
         BL ----------------- BR
       (0,1)                (1,1)

============================================================
RAW MODE MK1
+---+---+---+---+---+---+---+---+ 
|200|201|202|203|204|205|206|207| < or 0..7 with LedCtrlAutomap()
+---+---+---+---+---+---+---+---+   

+---+---+---+---+---+---+---+---+  +---+
|  0|...|   |   |   |   |   |  7|  |  8|
+---+---+---+---+---+---+---+---+  +---+
| 16|...|   |   |   |   |   | 23|  | 24|
+---+---+---+---+---+---+---+---+  +---+
| 32|...|   |   |   |   |   | 39|  | 40|
+---+---+---+---+---+---+---+---+  +---+
| 48|...|   |   |   |   |   | 55|  | 56|
+---+---+---+---+---+---+---+---+  +---+
| 64|...|   |   |   |   |   | 71|  | 72|
+---+---+---+---+---+---+---+---+  +---+
| 80|...|   |   |   |   |   | 87|  | 88|
+---+---+---+---+---+---+---+---+  +---+
| 96|...|   |   |   |   |   |103|  |104|
+---+---+---+---+---+---+---+---+  +---+
|112|...|   |   |   |   |   |119|  |120|
+---+---+---+---+---+---+---+---+  +---+

============================================================
RAW MODE MK2
+---+---+---+---+---+---+---+---+ 
|104|   |106|   |   |   |   |111|
+---+---+---+---+---+---+---+---+ 

+---+---+---+---+---+---+---+---+  +---+
| 81|   |   |   |   |   |   |   |  | 89|
+---+---+---+---+---+---+---+---+  +---+
| 71|   |   |   |   |   |   |   |  | 79|
+---+---+---+---+---+---+---+---+  +---+
| 61|   |   |   |   |   | 67|   |  | 69|
+---+---+---+---+---+---+---+---+  +---+
| 51|   |   |   |   |   |   |   |  | 59|
+---+---+---+---+---+---+---+---+  +---+
| 41|   |   |   |   |   |   |   |  | 49|
+---+---+---+---+---+---+---+---+  +---+
| 31|   |   |   |   |   |   |   |  | 39|
+---+---+---+---+---+---+---+---+  +---+
| 21|   | 23|   |   |   |   |   |  | 29|
+---+---+---+---+---+---+---+---+  +---+
| 11|   |   |   |   |   |   |   |  | 19|
+---+---+---+---+---+---+---+---+  +---+

============================================================
X/Y MODE
  0   1   2   3   4   5   6   7      8   
+---+---+---+---+---+---+---+---+ 
|0/0|1/0|   |   |   |   |   |   |         0
+---+---+---+---+---+---+---+---+ 

+---+---+---+---+---+---+---+---+  +---+
|0/1|   |   |   |   |   |   |   |  |   |  1
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |   |   |   |  |   |  2
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |5/3|   |   |  |   |  3
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |   |   |   |  |   |  4
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |   |   |   |  |   |  5
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |4/6|   |   |   |  |   |  6
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |   |   |   |  |   |  7
+---+---+---+---+---+---+---+---+  +---+
|   |   |   |   |   |   |   |   |  |8/8|  8
+---+---+---+---+---+---+---+---+  +---+

============================================================
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
    TOP_BTNS = [200, 201, 202, 203] 
    SCAN_CTRL_BTNS = [204, 205] 
    VOL_BTNS = [206, 207] 
    SIDE_BTNS = [8, 24, 40, 56, 72, 88, 104, 120] 
    EXIT_PWR_BTN = 104 
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(); mode = "Mk2"
    print("--- System: Launchpad Mk2 detected ---")
    TOP_BTNS = [104, 105, 106, 107] 
    SCAN_CTRL_BTNS = [108, 109] 
    VOL_BTNS = [110, 111] 
    SIDE_BTNS = [89, 79, 69, 59, 49, 39, 29, 19] 
    EXIT_PWR_BTN = 29 
else:
    exit("Launchpad not detected.")
lp.Reset()

# --- 2. Audio Server ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()

# --- 3. Audio Engine ---
noise = PinkNoise(mul=0.2)
sine = Sine(freq=440, mul=0.2)

noise_gains = [Sig(0) for _ in range(4)]
noise_ports = [Port(sig, 0.05, 0.05) for sig in noise_gains]
sine_gains = [Sig(0) for _ in range(4)]
sine_ports = [Port(sig, 0.05, 0.05) for sig in sine_gains]

master_vol = Sig(0.6)
master_vol_port = Port(master_vol, 0.1, 0.1)

for i in range(4):
    out = ((noise * noise_ports[i]) + (sine * sine_ports[i])) * master_vol_port
    out.out(i)

print("--- Audio Engine Started ---")

# --- 4. Helper Functions ---
def get_quad_gains(x, y):
    nx = x / 7.0
    ny = (y - 1) / 7.0
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def lp_led_raw(bid, r, g, b=0):
    if mode == "Mk2": lp.LedCtrlRaw(bid, int(r * 21), int(g * 21), int(b * 21))
    else: lp.LedCtrlRaw(bid, r, g)

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
scan_active = manual_active = False
pressed_top_btns = set()
pressed_grid_cells = set() 

for btn in TOP_BTNS: lp_led_raw(btn, 0, 3)
for btn in SCAN_CTRL_BTNS: lp_led_raw(btn, 0, 3)
update_vol_leds()

if mode == "Mk2": lp.LedCtrlRaw(EXIT_PWR_BTN, 10, 10, 63)
else: lp_led_raw(EXIT_PWR_BTN, 1, 3)

# --- 6. Main Loop ---
try:
    print("--- Starting Updated Loop ---")
    step_interval = 4.0 / 64.0
    last_step_time = time.time()
    grid_idx = -1
    scan_gains = manual_gains = [0.0] * 4
    last_top_states = {btn: 0 for btn in SCAN_CTRL_BTNS}

    while True:
        current_time = time.time()
        ev = lp.ButtonStateRaw()
        if ev:
            bid, state = ev[0], ev[1]
            if bid == EXIT_PWR_BTN and state > 0: 
                print("--- System: Exit Triggered ---")
                break
            
            if bid in SCAN_CTRL_BTNS:
                idx = SCAN_CTRL_BTNS.index(bid)
                if state > 0 and last_top_states[bid] == 0:
                    if idx == 0:
                        scan_active = not scan_active
                        print(f"--- Auto-Scan: {scan_active} ---")
                        if not scan_active and grid_idx >= 0:
                            px, py = grid_idx % 8, grid_idx // 8
                            lp_led_grid(px, py, 0, 0)
                            grid_idx = -1
                    elif idx == 1:
                        manual_active = not manual_active
                        print(f"--- Manual Mode: {manual_active} ---")
                        if not manual_active:
                            for (gx, gy) in pressed_grid_cells: lp_led_grid(gx, gy, 0, 0)
                            pressed_grid_cells.clear()
                    for i, b in enumerate(SCAN_CTRL_BTNS):
                        act = scan_active if i == 0 else manual_active
                        lp_led_raw(b, *( (3, 0) if act else (0, 3) ))
                last_top_states[bid] = state

            elif bid in TOP_BTNS:
                idx = TOP_BTNS.index(bid)
                if state > 0:
                    print(f"--- Solo Button {idx} Pressed ---")
                    pressed_top_btns.add(bid); lp_led_raw(bid, 3, 0)
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
                    if state > 0:
                        print(f"--- Grid Pressed: ({gx}, {gy}) ---")
                        pressed_grid_cells.add((gx, gy)); lp_led_grid(gx, gy, 0, 3)
                    else:
                        if (gx, gy) in pressed_grid_cells:
                            pressed_grid_cells.remove((gx, gy)); lp_led_grid(gx, gy, 0, 0)

        is_paused = len(pressed_top_btns) > 0
        if scan_active and not is_paused:
            if current_time - last_step_time >= step_interval:
                if grid_idx >= 0:
                    px, py = grid_idx % 8, grid_idx // 8
                    if (px, py) not in pressed_grid_cells: lp_led_grid(px, py, 0, 0)
                grid_idx = (grid_idx + 1) % 64
                sx, sy = grid_idx % 8, grid_idx // 8
                scan_gains = get_quad_gains(sx, sy + 1)
                lp_led_grid(sx, sy, 0, 3)
                last_step_time = current_time
        elif not scan_active or is_paused:
            scan_gains = [0.0] * 4
            if is_paused: last_step_time = current_time 

        manual_gains = [0.0] * 4
        if manual_active and pressed_grid_cells:
            for (mx, my) in pressed_grid_cells:
                gains = get_quad_gains(mx, my + 1)
                for i in range(4): manual_gains[i] = max(manual_gains[i], gains[i])

        for i in range(4):
            noise_gains[i].value = scan_gains[i]
            target_sine = manual_gains[i]
            if TOP_BTNS[i] in pressed_top_btns: target_sine = 1.0
            sine_gains[i].value = target_sine
            
        time.sleep(0.005)

except KeyboardInterrupt: pass
finally:
    s.stop(); s.shutdown(); lp.Reset(); lp.Close()
    print("--- Goodbye ---")
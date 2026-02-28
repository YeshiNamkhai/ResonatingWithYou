# Resonating With You
Welcome to repository of **Resonating With You**, an event held in February 2026 at Dzamling Gar featuring an immersive sound experience designed to help you better understand yourself and the characteristics of your own perception.


## Requirements
To run the scripts you need a working knowledge of Python programming language, some DSP and audio programming, ability to use MIDI devices. First of all install [Python 3.11](https://www.python.org/downloads/release/python-3111/) and create an environement to add the modules from the [requirements](requirements.txt).


### Novation Launchpad
Choose a device, either mini or regular Launchpad; leds will operate RED and GREEN, no BLUE for backward compatibility. 
- MK1 
- MK2   

If you own a different gear properly managed by the [launchpad.py](https://github.com/FMMT666/launchpad.py) library, you may use it with minimal adjustment to the code. Keep in mind that top and side buttons have different numbering, just like the main grid 8x8. The supprted code is the following:

MK1 RAW MODE
```python
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
```

MK2 RAW MODE
```python
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
```

When is X/Y MODE most Launchpad operate in same way.
```python
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
```

### Audio Settings
Check your [audio setting](audio_setting.py), run the script and remember the id of your device, usually ASIO. All script default to id=10, eventually the sound card has 4 outputs. Check your quadrophonic setup with [test_speakers](test_speakers.py).

#### Quadriphonic setup
The soundstage is arranged in quadraphonic fashion, with the top-left grid outputting channel 0, the top-right grid outputting channel 1, the bottom-left grid outputting channel 3, and finally the bottom-right grid outputting channel 4.
```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```


## Initialization
All scripts initialize Launchpad over MIDI using pygame, while audio engine is initialized with [PYO](https://belangeo.github.io/pyo/) without MIDI support; pay attention to precedence or import with name.

```python
from pyo import *
import launchpad_py as launchpad

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio'
BUFFER_SIZE = 512 

# --- 1. Launchpad Setup ---
mode = None
lp = launchpad.Launchpad()
if lp.Check(0, "Mini"):
    lp.Open(); mode = "Mk1"
    print("--- System: Launchpad Mk1/S/Mini detected ---")
elif lp.Check(0, "Mk2"):
    lp = launchpad.LaunchpadMk2(); lp.Open(); mode = "Mk2"
    print("--- System: Launchpad Mk2 detected ---")
else:
    exit("Launchpad not detected.")
lp.Reset()

# --- 2. Audio Server ---
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()
```
## Harmonic synth
## Chaotic 

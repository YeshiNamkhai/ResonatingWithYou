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
The soundstage is arranged in quadraphonic fashion, with the top-left grid outputting channel 0 on speaker 1, the top-right grid outputting channel 1 on speaker 2, the bottom-left grid outputting channel 2 on speaker 3, and finally the bottom-right grid outputting channel 3 on speaker 4.
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
The [synth_harms](synth_harms.py) script features a musical instrument selectable by its starting note (root) and scale. There are 20 different scales, including tonal, non-tonal, and microtonal, one of which is randomly generated upon startup. The buttons at the top allow you to increase or decrease the natural harmonics between 5 and 60, and control the volume. The buttons on the side activate the effects: reverb, delay, chorus, compression, and octave shift; the last button on the side turns everything off.

```python
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
```

## Chaotic 

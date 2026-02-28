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
The [synth_harms](synth_harms.py) script features a musical instrument selectable by its starting note (root) and scale. There are many interesting scales, including tonal, non-tonal and microtonal, one of which is randomly generated upon startup. 

Buttons follow this schema:
```python
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
```
The 30 scales available are:
```python
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
    "Hungarian Min": [0, 2, 3, 6, 7, 8, 11], "Double Harm": [0, 1, 4, 5, 7, 8, 11],
    "15-TET": [0, 1.6, 4.0, 5.6, 8.0, 9.6, 11.2],
    "19-TET": [0, 1.89, 3.79, 5.05, 6.95, 8.84, 10.74],
    "Bohlen-Pierce": [0, 1.46, 2.93, 4.39, 5.85, 7.32, 8.78],
    "Just Intonation": [0, 2.31, 3.86, 4.98, 7.02, 9.33, 10.88]
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

## Stochastic field
The [stochastic_field](stochastic_field.py) script is a rhythmic musical instrument that organizes notes in quadraphony, with their relative positioning allowing the user to choose the root note, the reference scale. The left area of ​​the grid generates even rhythms, while the right area generates odd rhythms; the octave is distributed from top to bottom.

Buttons follow this schema:
"""python
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

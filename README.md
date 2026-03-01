# Resonating With You
Welcome to the repository for **Resonating With You**, an event taking place in February 2026 at Dzamling Gar, offering an immersive sound experience designed to help you truly understand yourself and the characteristics of your perception of the world. It is intended for reflective individuals, those familiar with meditation, and researchers who wish to explore their work—the process of making sense of their data, experientially, through sound.

Whether you're a yoga practitioner, a tireless enthusiast, or an academic, here you'll find scripts that gradually help you develop an awareness of sonic space, specifically quadraphonic space. In the same way we often take over visual space to project our own world of meaning—for example, a graph or histogram describing something interesting—we also take over sonic space. But there's a big difference between the correlation of two or more variables (already difficult to represent because statistics is not an easy subject) and the sense of coherence a soundscape provides. It's not a scalar, an abstract value, but a dynamic experience that somehow belongs to us. Music does this, so why not use this natural propensity to better understand ourselves and the world?

Within this space, scripts allow us to experience familiar aspects of music and acoustics, as well as shifting data arrangements and less-than-obvious relationships. This allows us to acquire a basic vocabulary and become aware of how data always carries meaning. Humans, in their actions, regardless of the meaning of their actions, produce noise [^1]; knowing how to listen makes a difference.

## Requirements
To run the scripts you need a working knowledge of Python programming language, some DSP and audio programming, ability to use MIDI devices. First of all install Python[^2]  and create an environement to add the modules from the [requirements](requirements.txt).


### Novation Launchpad
Choose a device, either mini or regular Launchpad; leds will operate RED and GREEN, no BLUE for backward compatibility. 
- MK1 
- MK2   

If you own a different gear check the library[^3], you may use it with minimal adjustment to the code. Keep in mind that top and side buttons have different numbering, just like the main grid 8x8. The supprted code is the following:

<details>

<summary>MK1 RAW MODE</summary>

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
</details>

<details>

<summary>MK2 RAW MODE</summary>

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
</details>

<details>

<summary>X/Y MODE</summary>

```python
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
</details>

When is X/Y MODE most Launchpads operate in same way.

### Audio Settings
Check your [audio setting](audio_setting.py), run the script and remember the id of your device (default to 10), using ASIO host for low latency. The sound card has to have 4 outputs, verify your quadrophonic setup with [test_speakers](test_speakers.py), by scanning every grid cell, that correspond to a position in sound space, and by playing a pure sinewave within the sound space; use a fast circular gesture.

#### Quadraphonic
The soundstage is arranged in quadraphonic fashion, ideally using four identical speakers: Ch0 --> Spk1, Ch1 --> Spk2, Ch2 --> Spk3, Ch3 --> Spk4; interpolation takes place between cells, for intermediate values.
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
<details>

<summary>get_quad_gains(x, y)</summary>

```python
       (0,0)  nx = x / 7.0  (1,0)
         TL ----------------- TR
          |        |          |
          |     (nx, ny)      |  ny = (y - 1) / 7.0
          |        |          |
         BL ----------------- BR
       (0,1)                (1,1)
```
</details>


## Initialization
All scripts initialize Launchpad over MIDI using pygame, before audio engine[^4] and  with no MIDI support; respect precedence or import with name. 

<details>

<summary>example of import and initialization</summary>

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
</details>

## Harmonic synth
The [synth_harms](synth_harms.py) script features a musical instrument selectable by its starting note (root) and scale. There are many interesting scales, including tonal, non-tonal and microtonal, one of which is randomly generated upon startup. 

Buttons follow this schema:
```python
"""
Quadraphonic Harmonic Synth
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

<details>

<summary>30 built in scales</summary>

```python
SCALES = {
    "Major": [0, 2, 4, 5, 7, 9, 11], 
    "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Indian Bhairav": [0, 1.12, 3.86, 4.98, 7.02, 8.14, 10.88],
    "Indian Marwa": [0, 1.12, 3.86, 5.90, 7.02, 9.06, 10.88],
    "Chinese Pentatonic": [0, 2.04, 3.86, 7.02, 9.06],
    "Ligeti Micro": [0, 0.5, 2.5, 3.5, 6.5, 7.5, 10.5],
    "Spectral": [0, 2.04, 3.86, 5.51, 7.02, 8.41, 9.69, 10.88],
    "Partch Otonality": [0, 2.04, 3.86, 4.98, 7.02, 8.84, 10.88],
    "Japanese Hirajoshi": [0, 2.04, 3.16, 7.02, 8.14],
    "Japanese In Sen": [0, 1.12, 4.98, 7.02, 8.14],
    "Dorian": [0, 2, 3, 5, 7, 9, 10], 
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11], 
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Locrian": [0, 1, 3, 5, 6, 8, 10], 
    "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
    "Melodic Minor": [0, 2, 3, 5, 7, 9, 11], 
    "Pentatonic Maj": [0, 2, 4, 7, 9],
    "Pentatonic Min": [0, 3, 5, 7, 10], 
    "Blues": [0, 3, 5, 6, 7, 10],
    "Whole Tone": [0, 2, 4, 6, 8, 10], 
    "Acoustic": [0, 2, 4, 6, 7, 9, 10],
    "Altered": [0, 1, 3, 4, 6, 8, 10], 
    "Phrygian Dom": [0, 1, 4, 5, 7, 8, 10],
    "Hungarian Min": [0, 2, 3, 6, 7, 8, 11], 
    "Double Harm": [0, 1, 4, 5, 7, 8, 11],
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
</details>

The grid shows the scales considering always (0,0) as the root note, therefore changing scale draws a different chromatic organizazion, opens with C Major scale.

```
0      1      2      3      4      5      6      7    (X)
    +------+------+------+------+------+------+------+------+
 7  |  **C**   |  ·  |  D   |  ·  |  E   |  F   |  ·  |  G   |
    +------+------+------+------+------+------+------+------+
 6  |  G   |  ·  |  A   |  ·  |  B   |  **C**   |  ·  |  D   |
    +------+------+------+------+------+------+------+------+
 5  |  D   |  ·  |  E   |  F   |  ·  |  G   |  ·  |  A   |
    +------+------+------+------+------+------+------+------+
 4  |  A   |  ·  |  B   |  **C**   |  ·  |  D   |  ·  |  E   |
    +------+------+------+------+------+------+------+------+
 3  |  E   |  F   |  ·  |  G   |  ·  |  A   |  ·  |  B   |
    +------+------+------+------+------+------+------+------+
 2  |  B   |  **C**   |  ·  |  D   |  ·  |  E   |  F   |  ·  |
    +------+------+------+------+------+------+------+------+
 1  |  F   |  ·  |  G   |  ·  |  A   |  ·  |  B   |  **C**   |
    +------+------+------+------+------+------+------+------+
 0  |  **C**   |  ·  |  D   |  ·  |  E   |  F   |  ·  |  G   |
    +------+------+------+------+------+------+------+------+
(Y)    0      1      2      3      4      5      6      7
```

## Stochastic field
The [stochastic_field](stochastic_field.py) script is a rhythmic musical instrument that organizes notes in quadraphony, with their relative positioning allowing the user to choose the root note and the reference scale while playing. The left area of ​​the grid generates even rhythms, while the right area generates odd rhythms; the octave is distributed from top to bottom; the timbre can be modified  adding effect or channging the instrument playing.

Buttons follow this schema:
```python
"""
Stochastic Field
===========================================================
- Top Button 0: Decrements global root note (C, C#, etc.)
- Top Button 1: Increments global root note
- Top Button 2: Cycles backward through the SCALES
- Top Button 3: Cycles forward through the SCALES
- Top Button 4: Reverb, cycles through Small Room, Medium Hall, and Large Hall
- Top Button 5: Displacement, active cells jump to empty one
- Top Button 6: Volume up
- Top Button 7: Volume down

- Side Button 0: Fades master out, clears all active agents, then restores volume
- Side Button 1: Delay, cycles delay timings: OFF -> 1/4 -> 1/8 -> 1/16
- Side Button 2: Chorus, cycles chorus settings: OFF -> SUBTLE -> MOD -> DEEP
- Side Button 3: Sound, change timbre (e.g., Glass Pluck, Bamboo FM)
- Side Button 4: Sound, change timbre (e.g., Crystal Tine, Digital Marimba)
- Side Button 5: Switch off, initiates a 4-second fade out and exits

- 8x8 Grid: Toggle action. Press to activate a Cell Agent; press again to deactivate
            X/Y position calculates gain across 4 output channels (Quadraphonic)
            Position determines octave offset, scale note, and playback frequency
            Dim color = Ready; Bright color = Triggering; Red = Scale Root
"""
```


[^1]: Schafer's definitive soundscape text "The Tuning of the World" was published in 1977 within the [World SoundScape Project](https://www.sfu.ca/~truax/wsp.html).
[^2]: [Python 3.11](https://www.python.org/downloads/release/python-3111/)
[^3]: A Novation Launchpad (and Midi Fighter) control suite for Python. If you ever dreamed of using your Launchpad for completely other stuff than music: Welcome !-) [FMMT666/launchpad.py](https://github.com/FMMT666/launchpad.py)]
[^4]: [PYO](https://belangeo.github.io/pyo/) is a Python module written in C to help digital signal processing script creation.
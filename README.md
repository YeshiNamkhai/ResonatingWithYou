# Resonating With You
Welcome to the repository for **Resonating With You**, an event taking place in February 2026 at Dzamling Gar, offering an immersive sound experience designed to help you truly understand yourself and the characteristics of your perception of the world. It is intended for reflective individuals, those familiar with meditation, and researchers who wish to explore their work—the process of making sense of their data, experientially, through sound.

## Who is it for?
Whether you're a yoga practitioner, a tireless enthusiast, or an academic, here you'll find scripts that gradually help you develop an awareness of sonic space, specifically quadraphonic space. In the same way we often take over visual space to project our own world of meaning—for example, a graph or histogram describing something interesting—we also take over sonic space. But there's a big difference between the correlation of two or more variables (already difficult to represent because statistics is not an easy subject) and the sense of coherence a soundscape provides. It's not a scalar, an abstract value, but a dynamic experience that somehow belongs to us. Music does this, so why not use this natural propensity to better understand ourselves and the world?

## Why it matters?
There are several similar projects and many highly valuable electroacoustic artistic works. What's different about this? The sonic space is fixed, the directions are fixed, the colors have complete meaning, as the attributes and actions of the sonic entities. The entire coherence is based on principles familiar to Tibetan Buddhism, which make the mandala something extraordinary, and all of this is not just a flavor but a place for reflection.

### What makes it work?
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
The [synth_harms](synth_harms.py) script features a musical instrument that allows you to explore melodic lines, to acquire a sensitivity to harmony, to create hybrid textures between harmonics and rhythm. It is selectable by its starting note (root) and scale. There are many interesting scales, including tonal, non-tonal and microtonal, one of which is randomly generated upon startup. 

Buttons follow this schema:
```
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

The grid adopts the isomorphic note layout[^5], scales start at (0,0) as the root note, therefore changing scale draws a different chromatic organizazion, opens with C Major scale. Same note show as white color, so playing F on row (0) will light up also on row (1); the notes on the 8x8 grid are laid out in fourths vertically. 

```
0      1      2      3      4      5      6      7    (X)
    +------+------+------+------+------+------+------+------+
 7  |  C   |  ··  |  D   |  ··  |  E   |  F   |  ··  |  G   |
    +------+------+------+------+------+------+------+------+
 6  |  G   |  ··  |  A   |  ··  |  B   |  C   |  ··  |  D   |
    +------+------+------+------+------+------+------+------+
 5  |  D   |  ··  |  E   |  F   |  ··  |  G   |  ··  |  A   |
    +------+------+------+------+------+------+------+------+
 4  |  A   |  ··  |  B   |  C   |  ··  |  D   |  ··  |  E   |
    +------+------+------+------+------+------+------+------+
 3  |  E   |  F   |  ··  |  G   |  ··  |  A   |  ··  |  B   |
    +------+------+------+------+------+------+------+------+
 2  |  B   |  C   |  ··  |  D   |  ··  |  E   |  F   |  ··  |
    +------+------+------+------+------+------+------+------+
 1  |  F   |  ··  |  G   |  ··  |  A   |  ··  |  B   |  C   |
    +------+------+------+------+------+------+------+------+
 0  |  C   |  ··  |  D   |  ··  |  E   |  F   |  ··  |  G   |
    +------+------+------+------+------+------+------+------+
(Y)    0      1      2      3      4      5      6      7
```

## Stochastic field
The [stochastic_field](stochastic_field.py) script is a musical instrument that allows you to explore rhythm and its relationship with internal time; rhythmic pulses are generated when a cell from the grid is activated, they are pitched according to the root note and scale selected. Cells on the grid, with their relative positioning in a quadraphonic configuration, play until deactivaed a sequence chosen randomly. 

The left area of ​​the grid generates even rhythms, while the right area generates odd rhythms. 
<details>

<summary>Even and Odd</summary>

```python
LEFT (x < 4)                 RIGHT (x >= 4)
        "EVEN" Rhythms                 "ODD" Rhythms
      (Divisions: 1, 2, 4)           (Divisions: 1, 3, 5)
    +-----------------------+      +-----------------------+
    | Zone 12  |  Zone 13   |      | Zone 14  |  Zone 15   |
7   | (Fastest | (Fast)     |      | (Fastest | (Fast)     |
6   |  Center) |            |      |  Center) |            |
5   |          |            |      |          |            |
    +----------+------------+      +----------+------------+  <-- Row 5
4   | Zone 8   |  Zone 9    |      | Zone 10  |  Zone 11   |
3   | (Slow)   | (Slowest)  |      | (Slow)   | (Slowest)  |
    +----------+------------+      +----------+------------+  <-- Row 3
2   | Zone 4   |  Zone 5    |      | Zone 6   |  Zone 7    |
1   | (Fastest | (Fast)     |      | (Fastest | (Fast)     |
0   |  Center) |            |      |  Center) |            |
    |          |            |      |          |            |
    +----------+------------+      +----------+------------+
(Y)    0  1  2  3                4  5  6  7    (X)
```
* Horizontal Split (Rhythm Type):
  - Left (x < 4): Cells are marked as is_even = True. When activated, they choose a beat division of 1, 2, or 4.
  - Right (x >= 4): Cells are marked as is_even = False. They choose a beat division of 1, 3, or 5, creating triplets and quintuplets.

*  Quadrant Speed (speed_mult):
   - Within each 4x4 quadrant, the speed is calculated based on the distance from the center of that quadrant (coordinates 1.5, 1.5).
   - Center of 4x4: The speed_mult is highest (up to 4.0x), making the notes trigger very fast.
   - Corners of 4x4: The speed_mult is lowest (closer to 1.0x), resulting in a standard tempo.
</details><br>

The notes are arranged vertically, from top to bottom.
<details>

<summary>Octaves</summary>

```python
LEFT (x < 4)          RIGHT (x >= 4)
    +---------------------+---------------------+
    |                     |                     |
7   |       +1.5          |       +0.5          |
6   |      Octave         |      Octave         |
5   |                     |                     |
    +---------------------+---------------------+  <-- Row 5 boundary
4   |       +0.5          |       -0.5          |
3   |      Octave         |      Octave         |
    +---------------------+---------------------+  <-- Row 3 boundary
2   |                     |                     |
1   |       -1.0          |       -1.5          |
0   |      Octave         |      Octave         |
    |                     |                     |
    +---------------------+---------------------+
(Y)    0    1    2    3      4    5    6    7 (X)
```
* Key Distribution Details:
    - Top Section (Rows 5, 6, 7): Provides the highest pitches, with the left side being one full octave higher than the right.
    - Middle Section (Rows 3, 4): Provides a transition zone with a subtle one-octave difference (+0.5 vs -0.5) across the vertical split.
    - Bottom Section (Rows 0, 1, 2): Provides the bass registers, where the right side (-1.5) is the lowest point on the grid.
These offsets are multiplied by 12 and added to the scale degree and root note to determine the final frequency.
</details><br>

Finally, the timbre can be modified by adding effects or changing the instrument's performance.


Buttons follow this schema:
```
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
```

## Living beings field
The [beings_field](beings_field.py) script is a musical instrument that allows exploration of sound space within time constrains, living beings are created by pressing side buttons. Their ability to move and interact depends on top buttons, while cells on the grid activate obstacles, you can trap beings and their sound will switch from pulse to tone. Music ends with the last being dying, pressing a side button triggers death or ribirth.  

Buttons follow this schema:
```
Living Beings Field: 
====================================================================================================
Top Buttons   0: Delay Multi-State (Cycle Off/Circular/Ping-Pong, Green/Red/Amber)
Top Button    1: FM Collision Toggle (Red = Enabled, Green = Disabled)
Top Button    2: Warp Jump (Randomly relocates all active balls, Red while running)
Top Button    3: Granulator Multi-State (Cycle Off/Random Pos/Random All, Green/Red/Amber)
Top Button    4: Wrap/No-Walls Toggle (Red = Enabled, Green = Disabled, 8s Lock)
Top Button    5: Obstacle Multi-State (Cycle Idle/Remove All/Relocate All, Green/Red/Amber)
Top Buttons 6-7: Master Volume (Decrease/Increase by 0.05, Color reflects level)
(all top buttons have 8s Lock, except for volume)

Side Buttons 0-1: Trigger/Kill being (Very Highs)
Side Buttons 2-3: Trigger/Kill being (Mids)
Side Button    4: Trigger/Kill being (Percussions)
Side Button    5: Trigger/Kill being (Drums)
Side Buttons 6-7: Trigger/Kill being (Lows)

Main Grid (8x8):
- Press Empty Cell: Toggle Static Obstacle (Amber LED)
- Active Balls: Real-time position tracking (Unique colors per ball index)

Life Expectancy (shown at start):
- FEW COLUMNS (e.g., 1): Balls lose energy quickly and stop soon.
- MANY COLUMNS (e.g., 8): Balls lose energy very slowly, moving for a long time.
====================================================================================================
```
<details>

<summary>Scales</summary>

```python
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'whole_tone': [0, 2, 4, 6, 8, 10],
    'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'hexatonic': [0, 1, 4, 5, 8, 9],  # Augmented scale
    'octatonic': [0, 2, 3, 5, 6, 8, 9, 11],  # Diminished scale
    'indian_raga_bhairav': [0, 1, 4, 5, 7, 8, 11],
    'indian_raga_kalyan': [0, 2, 4, 6, 7, 9, 11],
    'neapolitan_major': [0, 1, 3, 5, 7, 9, 11],
    'neapolitan_minor': [0, 1, 3, 5, 7, 8, 11],
    'hungarian_minor': [0, 2, 3, 6, 7, 8, 11],
}
```
</details><br>

## Psychoacoustic Tests
The [psychoa_test](psychoa_test.py) script is a series of psychoacoustic tests that offer the opportunity to gain experiential knowledge in the context of quadraphonic setup.

Buttons follow this schema :
```
Experiential psychoacoustic tests
============================================================

- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red)
- Top Button 4: Toggles Auto-Scan (Pink Noise, Green/Red)
- Top Button 5: Toggles Manual Mode (Sine Wave over Grid, Green/Red)
- Top Buttons 6-7: Master Volume

- Side Button 0: Doppler (Cycle: Low -> Mid -> High -> Off)
- Side Button 1: Binaural Beats (Cycle: 36Hz -> 72Hz -> 108Hz -> Off)
- Side Button 2: Toggles Ascending Shepherd (Green)
- Side Button 3: Toggles Descending Shepherd (Green)
- Side Button 4: Toggles Risset Accelerando (Blue)
- Side Button 5: Toggles Risset Decelerando (Blue)
- Side Button 6: EXIT / POWER OFF (Blue/Cyan)
```

## Entropic field
The [entropic_field](entropic_field.py) script creates a chaotic motion of cells, initially stacked in two columns. You can select the initial layout, default to left which works also in stereo, when top or bottom, which goes from bright to dull tone or opposite, only works with 4 speakers; you may also experiment with reverb, delay and speed. Entropy increases and the cells move for about 4 minutes, reaching the opposite side.

Buttons follow this schema:
```
Entropic field
==========================================================================
- Top Buttons 0-1: Scale Selection (Cycle SCALES_DICT, Green/Amber)
- Top Buttons 2-3: Position Selection (Cycle LEFT/RIGHT/TOP/BOTTOM, Amber)
- Top Buttons 6-7: Main Volume (Amber 60%, Adjusts user_vol)

- Side Button 0: Start Sequence (Locks Setup Mode, Red/Green)
- Side Button 1: Reverb Toggle (Cycle 0.0-0.7 Mix, Green/Amber/Red)
- Side Button 2: Filter Toggle (Schumann Resonance 7.83Hz, Green/Amber)
- Side Button 3: Delay Toggle (Temporal Delay 0.1s-0.2s, Green/Amber)
- Side Button 6: EXIT / POWER OFF (Blue/Cyan - Matched to test_speakers)
```

<details>

<summary>Scales</summary>

```python
SCALES_DICT = {
    "Chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "Indian Bhairav": [0, 1.12, 3.86, 4.98, 7.02, 8.14, 10.88],
    "Partch Otonality": [0, 2.04, 3.86, 4.98, 7.02, 8.84, 10.88],
    "Partch Utonality": [0, 1.12, 3.16, 4.98, 7.02, 8.14, 9.96],
    "Partch Diamond": [0, 1.51, 1.65, 1.82, 2.04, 2.31, 2.67, 3.18, 3.47, 3.86, 4.35, 4.98, 5.51, 6.49, 7.02, 7.65, 8.14, 8.53, 8.84, 9.33, 9.69, 9.96, 10.18, 10.35, 10.49, 10.88, 11.44],
    "Young Lamonte": [0, 1.14, 3.86, 4.98, 7.02, 8.14, 10.88],
    "31-TET Pure": [0, 1.93, 3.87, 5.03, 6.96, 8.90, 10.83],
    "Bohlen-Pierce": [0, 1.46, 2.92, 4.38, 5.84, 7.30, 8.76, 10.22, 11.68],
    "Carlos Alpha": [0, 0.78, 1.56, 2.34, 3.12, 3.90, 4.68, 5.46, 6.24, 7.02],
    "Gamelan Slendro": [0, 2.4, 4.8, 7.2, 9.6],
    "Random 1": sorted([0] + [round(random.uniform(0.5, 11.5), 2) for _ in range(6)]),
}
```
</details><br>

Example of default scale (Partch Otonality)
```
[Y]  TOP of Grid (High Pitch)
   0 |  10/4    11/4    3/1     13/4* ...  <-- Higher Harmonics
   1 |  8/4     9/4     10/4    11/4    ...  
   2 |  6/4     7/4     8/4     9/4     ...  
   3 |  4/4     5/4     6/4     7/4     ...  <-- Degree 0 (Root 1/1)
   4 |  2/1     9/4     10/4    11/4    ...  
   5 |  7/4     8/4     9/4     10/4    ...  
   6 |  5/4     6/4     7/4     8/4     ...  
   7 |  1/1     5/4     6/4     7/4     ...  <-- Root (4/4)
     +--------------------------------------
 [X]    0        1       2       3      RIGHT (+1 Degree)
```

## ChNN sonic image 
The [chnn_scan](chnn_scan.py) script is a quadraphonic image-to-sound sonifier. It scans a digital image pixel-by-pixel and shows the position on GUI, while allowing to control the speed, reverb and compression for a better listening experience.
<p><img src="https://raw.githubusercontent.com/YeshiNamkhai/ResonatingWithYou/refs/heads/main/201310%20ChNN%20Barcelona%20by%20Paolo%20Fassoli_09_square_BW.jpg" width="150"></p>

Auditory display: 
* Pitch depends on brightness (grayscale) which maps the frequency.
* Timbre depends on RGB values which controls the number of harmonics in the waveform.
* Spatialization depends on pixel's Y-coordinate for front and rear speakers, X-coordinate for left and right.


## Generative field
The [gen_field](gen_field.py) script creates walker logic to navigate a stochastic soundscape, where four independent algorithmic agents move across an 8x8 grid to trigger and spatialize sound.

Buttons follow this schema:
```
Generative Field
============================================================
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Button 4: Delay Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Button 5: Reverb Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Buttons 6-7: Main Volume (Amber 60%, Red at Peak)

- Side Buttons 0-3: Toggle Algorithmic Walkers (Markov, Brownian, Fractal, Genetic)
- Side Buttons 4-6: Speed Selectors (Half, Normal, Double Schumann Speed)
- Side Button 7: EXIT / POWER OFF (Blue/Cyan on Mk2, 2-sec Fade Out on press)
```

## Formalized music
The [formalized_m](formalized_m.py) script retraces the main stages of Iannis Xenakis's text, arranging the iconic sounds in conflict with each other in quadraphonic sound, as is predictable, according to game theory; the grid is occupied with known statistical models and algorithms reported in the text[^6].

Buttons follow this schema:
```
Formalized music
============================================================
- Top Buttons 0-3: Momentary Channel Solo (Sine Wave, Red on press)
- Top Button 4: Delay Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Button 5: Reverb Multi-State (Cycle Off/Low/Mid/High, Green/Amber/Red)
- Top Buttons 6-7: Main Volume (Amber 60%, Red at Peak)

- Side Buttons 0-3: Toggle Stochastic Engines (Markov, Analog, GENDYN, Poisson)
- Side Buttons 4-6: Density Selectors (Half, Normal, Double Density)
- Side Button 7: EXIT / POWER OFF (Blue/Cyan, 2-sec Fade Out on press)
```

[^1]: Schafer's definitive soundscape text "The Tuning of the World" was published in 1977 within the [World SoundScape Project](https://www.sfu.ca/~truax/wsp.html).
[^2]: [Python 3.11](https://www.python.org/downloads/release/python-3111/)
[^3]: A Novation Launchpad (and Midi Fighter) control suite for Python. If you ever dreamed of using your Launchpad for completely other stuff than music: Welcome !-) [FMMT666/launchpad.py](https://github.com/FMMT666/launchpad.py)]
[^4]: [PYO](https://belangeo.github.io/pyo/) is a Python module written in C to help digital signal processing script creation.
[^5]: [The isomorphic note layout](https://hearandknow.wordpress.com/2014/03/15/the-isomorphic-note-layout/)
[^6]: [Formalized Music](https://en.wikipedia.org/wiki/Formalized_Music): Thought and Mathematics in Composition
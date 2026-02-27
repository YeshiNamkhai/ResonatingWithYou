# Resonating With You
Welcome to repository of **Resonating With You**, an event held in February 2026 at Dzamling Gar featuring an immersive sound experience designed to help you better understand yourself and the characteristics of your own perception.


## Requirements
To run the scripts you need a working knowledge of Python programming language, some DSP and audio programming, ability to use MIDI devices. First of all install [Python 3.11](https://www.python.org/downloads/release/python-3111/) and create an environement to add the modules from the [requirements](requirements.txt).


### Novation Launchpad
Choose a device, either mini or regular Launchpad; leds will operate RED and GREEN, no BLUE for backward compatibility. 
- MK1 
- MK2   

If you own a different gear properly managed by the [launchpad.py](https://github.com/FMMT666/launchpad.py) library, you may use it with minimal adjustment to the code. Keep in mind that top and side buttons have different numbering, just like the main grid 8x8. The supprted code is the following:

```python

```

### Audio Settings
Check your [audio setting](audio_settings.py), run the script and remember the id of your device, usually ASIO. All script default to id=10, eventually the sound card has 4 outputs. 


## Initialization
All scripts initialize Launchpad over MIDI before audio (pygame), moreover the [PYO](https://belangeo.github.io/pyo/) server should not activate MIDI.

```python
AUDIO_DEVICE = 10

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
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=512, winhost='asio')
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()
```


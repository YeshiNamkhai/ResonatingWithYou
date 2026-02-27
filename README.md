# Resonating With You
Welcome to repository of **Resonating With You**, an event held in Febrary 2026 at Dzamling Gar featuring an immersive sound experience designed to help you better understand yourself and the characteristics of your own perception.


## Requirements
To run the scripts you need a working knowledge of Python programming language, some DSP and audio programming and  ability to use MIDI devices. First of all install [Python 3.11](https://www.python.org/downloads/release/python-3111/) and create an environement to add the modules from the [requirements](requirements.txt).


### Novation Launchpad
Choose a device, either mini or regular; leds will operate RED and GREEN, no BLUE for backward compatibility. 
- MK1 
- MK2   


### AUDIO SETTINGS
Check your [audio setting](audio_settings.py), run the script and remember the id of y9our device, usually ASIO. All script default to id=10.


## INITIALIZATION
All scripts initialize Launchpad over MIDI before audio (pygame), moreover the [PYO](https://belangeo.github.io/pyo/) server should not activate MIDI.

```
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
s.setOutputDevice(10)
s.deactivateMidi()
s.boot().start()
```
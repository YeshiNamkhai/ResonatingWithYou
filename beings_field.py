import time, random, math, threading
import numpy as np
from pyo import *
import launchpad_py as launchpad

"""
Living Beings Field: 
====================================================================================================
The [beings_field](beings_field.py) script is a musical instrument that allows you to explore sound 
space within time constrains, living beings are created by pressing side buttons. Their ability to 
move and interact is modulated by your choises, pressing top buttons. On the grid youcan activate 
obstacles and trap beings, their sound will switch from pulse to tone. 
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

====================================================================================================
Life Expectancy (shown at start):
- FEW COLUMNS (e.g., 1): Balls lose energy quickly and stop soon.
- MANY COLUMNS (e.g., 8): Balls lose energy very slowly, moving for a long time.

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

# --- 3. Instrument Families & Envelopes ---

# Envelope format: (attack, decay, sustain, release, osc_type, filter_type, brightness)
# osc_type: 'sine', 'saw', 'square', 'noise', 'pulse'
# filter_type: 'lp' (lowpass), 'hp' (highpass), 'bp' (bandpass), 'none'
# brightness: 0.0-1.0 (affects filter cutoff)

# --- 3. Instrument Families & Envelopes ---
INSTRUMENT_FAMILIES = {
    'lows': {
        'bass': (0.08, 0.15, 0.7, 0.5, 'saw', 'lp', 0.3),
        'cello': (0.06, 0.12, 0.75, 0.45, 'saw', 'lp', 0.4),
        'piano': (0.003, 0.3, 0.2, 0.6, 'saw', 'lp', 0.7),
        'harp': (0.002, 0.2, 0.15, 0.7, 'sine', 'lp', 0.8),
        'bass_tuba': (0.08, 0.15, 0.75, 0.4, 'square', 'lp', 0.25),
        'bass_trombone': (0.06, 0.12, 0.7, 0.35, 'square', 'lp', 0.35),
        'baritone_sax': (0.04, 0.12, 0.7, 0.35, 'square', 'bp', 0.4),
        'tenor_sax': (0.035, 0.1, 0.7, 0.3, 'square', 'bp', 0.5),
        'contra_bassoon': (0.06, 0.15, 0.7, 0.4, 'sine', 'lp', 0.2),
        'bass_clarinet': (0.05, 0.12, 0.75, 0.35, 'sine', 'lp', 0.3),
   },
   
    'mids': {
        'viola': (0.05, 0.1, 0.75, 0.4, 'saw', 'lp', 0.5),
        'vibraphone': (0.005, 0.4, 0.3, 1.2, 'sine', 'none', 0.9),
        'celeste': (0.004, 0.25, 0.25, 0.8, 'sine', 'lp', 0.85),
        'tenor_trombone': (0.05, 0.1, 0.7, 0.3, 'square', 'lp', 0.45),
        'soprano_sax': (0.03, 0.08, 0.65, 0.28, 'square', 'bp', 0.6),
        'alto_clarinet': (0.04, 0.1, 0.75, 0.3, 'sine', 'lp', 0.4),
        'clarinet': (0.035, 0.08, 0.75, 0.28, 'sine', 'lp', 0.5),
        'english_horn': (0.04, 0.1, 0.7, 0.3, 'sine', 'lp', 0.45),
    },
    'highs': {
        'violin': (0.04, 0.08, 0.8, 0.35, 'saw', 'lp', 0.6),
        'xylophone': (0.001, 0.08, 0.1, 0.25, 'sine', 'hp', 0.95),
        'glockenspiel': (0.001, 0.15, 0.1, 0.4, 'sine', 'hp', 1.0),
        'trumpet': (0.03, 0.08, 0.65, 0.25, 'square', 'lp', 0.6),
        'sopranino_sax': (0.025, 0.07, 0.65, 0.25, 'square', 'bp', 0.7),
        'oboe': (0.03, 0.08, 0.7, 0.25, 'sine', 'lp', 0.6),
        'alto_flute': (0.04, 0.1, 0.65, 0.3, 'sine', 'lp', 0.65),
    },

    'veryhighs': {
        'violin': (0.04, 0.08, 0.8, 0.35, 'saw', 'lp', 0.6),
        'xylophone': (0.001, 0.08, 0.1, 0.25, 'sine', 'hp', 0.95),
        'glockenspiel': (0.001, 0.15, 0.1, 0.4, 'sine', 'hp', 1.0),
        'trumpet': (0.03, 0.08, 0.65, 0.25, 'square', 'lp', 0.6),
        'piccolo': (0.02, 0.06, 0.5, 0.2, 'sine', 'hp', 0.9),
    },    
    'strings': {
        'bass': (0.08, 0.15, 0.7, 0.5, 'saw', 'lp', 0.3),
        'cello': (0.06, 0.12, 0.75, 0.45, 'saw', 'lp', 0.4),
        'viola': (0.05, 0.1, 0.75, 0.4, 'saw', 'lp', 0.5),
        'violin': (0.04, 0.08, 0.8, 0.35, 'saw', 'lp', 0.6),
    }, 
   'keyboard_perc': {
        'piano': (0.003, 0.3, 0.2, 0.6, 'saw', 'lp', 0.7),
        'harp': (0.002, 0.2, 0.15, 0.7, 'sine', 'lp', 0.8),
        'vibraphone': (0.005, 0.4, 0.3, 1.2, 'sine', 'none', 0.9),
        'celeste': (0.004, 0.25, 0.25, 0.8, 'sine', 'lp', 0.85),
        'xylophone': (0.001, 0.08, 0.1, 0.25, 'sine', 'hp', 0.95),
        'glockenspiel': (0.001, 0.15, 0.1, 0.4, 'sine', 'hp', 1.0),
    },
    'brass': {
        'bass_tuba': (0.08, 0.15, 0.75, 0.4, 'square', 'lp', 0.25),
        'bass_trombone': (0.06, 0.12, 0.7, 0.35, 'square', 'lp', 0.35),
        'tenor_trombone': (0.05, 0.1, 0.7, 0.3, 'square', 'lp', 0.45),
        'trumpet': (0.03, 0.08, 0.65, 0.25, 'square', 'lp', 0.6),
    },
    'saxophones': {
        'baritone_sax': (0.04, 0.12, 0.7, 0.35, 'square', 'bp', 0.4),
        'tenor_sax': (0.035, 0.1, 0.7, 0.3, 'square', 'bp', 0.5),
        'soprano_sax': (0.03, 0.08, 0.65, 0.28, 'square', 'bp', 0.6),
        'sopranino_sax': (0.025, 0.07, 0.65, 0.25, 'square', 'bp', 0.7),
    },
    'woodwinds': {
        'contra_bassoon': (0.06, 0.15, 0.7, 0.4, 'sine', 'lp', 0.2),
        'bass_clarinet': (0.05, 0.12, 0.75, 0.35, 'sine', 'lp', 0.3),
        'alto_clarinet': (0.04, 0.1, 0.75, 0.3, 'sine', 'lp', 0.4),
        'clarinet': (0.035, 0.08, 0.75, 0.28, 'sine', 'lp', 0.5),
        'english_horn': (0.04, 0.1, 0.7, 0.3, 'sine', 'lp', 0.45),
        'oboe': (0.03, 0.08, 0.7, 0.25, 'sine', 'lp', 0.6),
        'alto_flute': (0.04, 0.1, 0.65, 0.3, 'sine', 'lp', 0.65),
        'flute': (0.03, 0.08, 0.6, 0.25, 'sine', 'lp', 0.75),
        'piccolo': (0.02, 0.06, 0.5, 0.2, 'sine', 'hp', 0.9),
    },
    'drums': {
        'bass_drum': (0.001, 0.15, 0.0, 0.3, 'noise', 'lp', 0.15),
        'snare_drum': (0.001, 0.05, 0.0, 0.12, 'noise', 'bp', 0.6),
        'closed_hihat': (0.001, 0.03, 0.0, 0.08, 'noise', 'hp', 0.95),
        'open_hihat': (0.001, 0.08, 0.1, 0.25, 'noise', 'hp', 0.9),
        'ride': (0.002, 0.12, 0.15, 0.4, 'noise', 'hp', 0.7),
        'cymbals': (0.003, 0.3, 0.2, 1.5, 'noise', 'hp', 0.75),
    },
    'percussion': {
        'triangle': (0.001, 0.1, 0.1, 1.2, 'sine', 'hp', 1.0),
        'claves': (0.001, 0.02, 0.0, 0.05, 'noise', 'bp', 0.8),
        'maracas': (0.002, 0.05, 0.0, 0.15, 'noise', 'hp', 0.85),
        'gong': (0.01, 0.5, 0.3, 2.0, 'noise', 'lp', 0.3),
        'woodblock': (0.001, 0.03, 0.0, 0.08, 'noise', 'bp', 0.7),
        'cowbell': (0.001, 0.08, 0.05, 0.2, 'square', 'bp', 0.75),
        'bongos': (0.002, 0.08, 0.0, 0.15, 'noise', 'bp', 0.5),
    }
}

BALL_FAMILY_MAP = [
    'veryhighs',   # Ball 0
    'veryhighs',   # Ball 1
    'mids',        # Ball 2
    'mids',        # Ball 3
    'percussion',  # Ball 4
    'drums',       # Ball 5
    'lows',        # Ball 6
    'lows'         # Ball 7
]

# --- 4. Configuration & State ---
SIZE, MAX_BALLS = 8, 8
STOP_THRESHOLD, ANGLE_VAR = 1.8, 0.5

# Musical Scales (semitone intervals from root)
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

# Select random scale at startup (will be set later)
selected_scale = None
selected_scale_name = None

MIDI_RANGES = [
    (84, 108), (72, 96), (60, 84), (55, 77), 
    (48, 70), (36, 60), (28, 52), (18, 42)
]

COLOR_PAIRS = [(0,3), (1,3), (2,3), (3,3), (3,2), (3,1), (3,0), (2,0)]
SIDE_MK1, TOP_MK1 = [8,24,40,56,72,88,104,120], [200,201,202,203,204,205,206,207]
SIDE_MK2, TOP_MK2 = [89,79,69,59,49,39,29,19], [104,105,106,107,108,109,110,111]

# Feature States
lifetime_mode = 1 
fm_enabled = False
warp_running = False
gran_mode = 0    
wrap_enabled = False
obstacle_mode = 0  # 0=idle(green), 1=removing(red), 2=relocating(amber)
delay_mode = 0  # 0=off(green), 1=circular(red), 2=pingpong(amber)
obstacles = set()
grid_map = {} 
ball_freqs = [0.0] * MAX_BALLS
balls = [None] * MAX_BALLS
lock = threading.Lock()

lt_timer = fm_timer = gran_timer = wrap_timer = obstacle_timer = delay_timer = None
FRICTION_VALUES = [1.1, 1.04, 1.015]

# Select random musical scale at startup
selected_scale_name = random.choice(list(SCALES.keys()))
selected_scale = SCALES[selected_scale_name]
print(f"--- Musical Scale: {selected_scale_name} {selected_scale} ---")

# Scale families for each ball
BALL_SCALE_FAMILIES = [
    ['major', 'lydian', 'mixolydian'],  # Ball 0 - Major family
    ['major', 'lydian', 'mixolydian'],  # Ball 1 - Major family
    ['minor', 'dorian', 'phrygian'],    # Ball 2 - Minor family
    ['minor', 'dorian', 'phrygian'],    # Ball 3 - Minor family
    ['pentatonic_major', 'pentatonic_minor', 'blues'],  # Ball 4 - Pentatonic family
    ['octatonic', 'hexatonic', 'whole_tone'],  # Ball 5 - Exotic family
    ['harmonic_minor', 'melodic_minor', 'hungarian_minor'],  # Ball 6 - Minor variations
    ['indian_raga_bhairav', 'indian_raga_kalyan', 'neapolitan_minor']  # Ball 7 - Modal/Raga
]

# Ableton Link tempo (BPM)
GLOBAL_TEMPO = 120.0
link_metro = None  # Will hold the master Metro

# --- 5. Musical Scale Functions ---
def quantize_to_scale(midi_note, scale_intervals):
    """Quantize a MIDI note to the nearest note in the given scale"""
    octave = midi_note // 12
    note_in_octave = midi_note % 12
    
    # Find closest scale degree
    closest_interval = min(scale_intervals, key=lambda x: abs(x - note_in_octave))
    
    return octave * 12 + closest_interval

def get_random_note_in_scale(min_note, max_note, scale_intervals):
    """Get a random MIDI note within range that fits the scale"""
    # Generate all possible notes in range that fit the scale
    valid_notes = []
    for note in range(min_note, max_note + 1):
        if (note % 12) in scale_intervals:
            valid_notes.append(note)
    
    if valid_notes:
        return random.choice(valid_notes)
    else:
        # Fallback: quantize a random note in range
        note = random.randint(min_note, max_note)
        return quantize_to_scale(note, scale_intervals)

# --- 6. Logic Functions ---
def get_quad_gains(x, y):
    nx, ny = x / 7.0, (y - 1) / 7.0
    return [(1.-nx)*(1.-ny), nx*(1.-ny), (1.-nx)*ny, nx*ny]

def lp_led(x, y, r, g, raw=False):
    if mode == "Mk1":
        if raw: lp.LedCtrlRaw(x, r, g)
        else: lp.LedCtrlXY(x, y, r, g)
    else:
        rs, gs = int(r * 21), int(g * 21)
        if raw: lp.LedCtrlRaw(x, rs, gs, 0)
        else: lp.LedCtrlXY(x, y, rs, gs, 0)

def update_ui():
    with lock:
        T = TOP_MK1 if mode == "Mk1" else TOP_MK2
        # Button 0: Delay (Green=off, Red=circular, Amber=pingpong)
        lp_led(T[0], 0, *[(0,3), (3,0), (3,3)][delay_mode], raw=True) 
        lp_led(T[1], 0, *( (3,0) if fm_enabled else (0,3) ), raw=True) 
        lp_led(T[2], 0, *( (3,0) if warp_running else (0,3) ), raw=True)
        lp_led(T[3], 0, *[(0,3), (3,0), (3,3)][gran_mode], raw=True)
        lp_led(T[4], 0, *( (3,0) if wrap_enabled else (0,3) ), raw=True)
        # Button 5: Obstacle control (Green=idle, Red=removing, Amber=relocating)
        lp_led(T[5], 0, *[(0,3), (3,0), (3,3)][obstacle_mode], raw=True)
        
        # Button 6 & 7: Master Volume
        vol = master_vol.value
        if vol < 0.4: v_col = (0, 3)
        elif vol < 0.7: v_col = (3, 3)
        elif vol < 0.9: v_col = (2, 0)
        else: v_col = (3, 0)
        lp_led(T[6], 0, *v_col, raw=True)
        lp_led(T[7], 0, *v_col, raw=True)

# --- 6. Audio Engine with Multiple Oscillators ---
class BallVoice:
    def __init__(self, index):
        self.index = index
        self.f_sig, self.g_sig = Sig(440), Sig([0,0,0,0])
        self.m_f_sig, self.m_i_sig = Sig(0), Sig(0)
        
        # Select random instrument from family
        family_name = BALL_FAMILY_MAP[index]
        self.family = family_name
        instruments = list(INSTRUMENT_FAMILIES[family_name].keys())
        self.instrument = random.choice(instruments)
        base_params = INSTRUMENT_FAMILIES[family_name][self.instrument]
        
        # Add slight random variation to envelope (+/-10%)
        attack, decay, sustain, release, osc_type, filt_type, brightness = base_params
        self.env_params = (
            attack * random.uniform(0.9, 1.1),
            decay * random.uniform(0.9, 1.1),
            sustain * random.uniform(0.95, 1.05),
            release * random.uniform(0.9, 1.1)
        )
        self.osc_type = osc_type
        self.filt_type = filt_type
        self.brightness = brightness * random.uniform(0.95, 1.05)
        
        # Smooth all frequency and gain changes
        self.f_port = Port(self.f_sig, 0.02, 0.02)
        self.g_port = Port(self.g_sig, 0.1, 0.1)
        self.m_f_port = Port(self.m_f_sig, 0.05, 0.05)
        self.m_i_port = Port(self.m_i_sig, 0.05, 0.15)
        
        # Ring modulation for wall hits
        self.ring_mod_sig = Sig(0)
        self.ring_mod_port = Port(self.ring_mod_sig, 0.01, 0.08)
        self.ring_mod_ratio = random.uniform(1.5, 2.2)
        self.ring_mod_osc = Sine(freq=self.f_port * self.ring_mod_ratio, mul=self.ring_mod_port)
        
        # FM modulation
        self.mod_osc = Sine(freq=self.m_f_port, mul=self.m_i_port)
        
        # Create envelope
        attack, decay, sustain, release = self.env_params
        self.env = Adsr(attack=attack, decay=decay, sustain=sustain, release=release, dur=1, mul=0)
        
        # Create oscillator based on type
        total_freq = self.f_port + self.mod_osc
        
        if self.osc_type == 'sine':
            self.osc = Sine(freq=total_freq)
        elif self.osc_type == 'saw':
            # Use LFO with type=0 (saw up)
            self.osc = LFO(freq=total_freq, sharp=1, type=0)
        elif self.osc_type == 'square':
            # Use LFO with type=2 (square wave)
            self.osc = LFO(freq=total_freq, sharp=1, type=2)
        elif self.osc_type == 'pulse':
            # Use LFO with type=4 (pulse wave) and random width
            self.osc = LFO(freq=total_freq, sharp=random.uniform(0.3, 0.7), type=4)
        elif self.osc_type == 'noise':
            # For noise, frequency affects filter cutoff
            self.osc = Noise()
        
        # Apply envelope and granulation
        self.osc_env = self.osc * self.env
        
        # Apply ring modulation
        self.ring_modulated = self.osc_env * (1 + self.ring_mod_osc)
        
        # Apply filter based on type
        base_cutoff = 500 + (brightness * 14000)
        self.cutoff = base_cutoff + random.uniform(-1000, 1000)
        self.cutoff = max(200, min(self.cutoff, 18000))
        self.filter_q = random.uniform(0.7, 2.5)
        
        if self.filt_type == 'lp':
            self.fil = Biquad(self.ring_modulated, freq=self.cutoff, q=self.filter_q, type=0)
        elif self.filt_type == 'hp':
            self.fil = Biquad(self.ring_modulated, freq=self.cutoff, q=self.filter_q, type=1)
        elif self.filt_type == 'bp':
            self.fil = Biquad(self.ring_modulated, freq=self.cutoff, q=self.filter_q, type=2)
        else:  # 'none'
            self.fil = self.ring_modulated
        
        # Resonant tail: noise through resonant bandpass filter tuned to note
        self.tail_noise = Noise()
        self.tail_env = Adsr(attack=0.001, decay=0.1, sustain=0.2, release=1.5, dur=1, mul=0)
        self.tail_filter_q = random.uniform(8, 15)  # High Q for resonance
        self.tail_filter = Biquad(self.tail_noise, freq=self.f_port, q=self.tail_filter_q, type=2)  # Bandpass
        self.tail_output = self.tail_filter * self.tail_env * 0.15  # Mix at lower level
        
        # Mix main signal with resonant tail
        self.mixed = self.fil + self.tail_output
        
        self.output = (self.mixed * self.g_port)
        
        print(f"--- Voice {self.index}: {self.family}/{self.instrument}, Osc={self.osc_type}, Filt={self.filt_type}, Q={self.filter_q:.2f}, TailQ={self.tail_filter_q:.2f} ---")

    def trigger(self, freq, amp, dur):
        self.f_sig.value = freq
        attack, decay, sustain, release = self.env_params
        self.env.attack = attack * dur * 0.3
        self.env.decay = decay * dur
        self.env.sustain = sustain
        self.env.release = release
        self.env.dur = dur
        self.env.mul = amp
        self.ring_mod_sig.value = 0
        self.env.play()
        
        # Trigger resonant tail
        self.tail_env.dur = dur * 1.5
        self.tail_env.play()
    
    def trigger_wall_hit(self, freq, amp, dur):
        self.f_sig.value = freq
        attack, decay, sustain, release = self.env_params
        self.env.attack = attack * 0.5
        self.env.decay = decay * dur * 0.8
        self.env.sustain = sustain * 0.5
        self.env.release = release * 0.7
        self.env.dur = dur * 0.8
        self.env.mul = amp * 1.4
        self.ring_mod_sig.value = random.uniform(0.5, 0.9)
        self.env.play()
        
        # Trigger resonant tail (stronger for wall hits)
        self.tail_env.dur = dur * 2.0
        self.tail_env.play()

    def update_panning(self, gains): self.g_sig.value = gains
    def set_fm(self, mod_freq): self.m_f_sig.value, self.m_i_sig.value = mod_freq, mod_freq * 1.5 
    def stop_fm(self): self.m_i_sig.value = 0

voices = [BallVoice(i) for i in range(MAX_BALLS)]
bus = Mix([v.output for v in voices], voices=4)

# --- Granulator (Particle) ---
# Serial Processing: Bus -> Granulator -> Reverb
gran_table = NewTable(length=1.0, chnls=4)
gran_rec = TableRec(bus, table=gran_table).play()

# Selectors for parameters
# Position: 0=Linear, 1=Random
gran_pos_lin = Phasor(0.1)
gran_pos_rnd = Randh(min=0, max=1, freq=4)
gran_pos_sel = Selector([gran_pos_lin, gran_pos_rnd], voice=0)

# Duration: 0=Static, 1=Random
gran_dur_base = 0.1 + Noise(mul=0.03)
gran_dur_rnd = Randi(min=0.05, max=0.5, freq=1)
gran_dur_sel = Selector([gran_dur_base, gran_dur_rnd], voice=0)

# Density: 0=Static, 1=Random
gran_dens_base = 120 + Noise(mul=30)
gran_dens_rnd = Randi(min=20, max=150, freq=0.5)
gran_dens_sel = Selector([gran_dens_base, gran_dens_rnd], voice=0)

# Wet level
gran_wet = Sig(0)
gran_wet_port = Port(gran_wet, 1.0, 1.0)
gran_dry = Sig(1) - gran_wet_port

gran = Particle(gran_table, env=WinTable(2), pitch=1, pos=gran_pos_sel, dur=gran_dur_sel, dens=gran_dens_sel, chnls=4, mul=gran_wet_port)

# Mix Dry + Wet
serial_bus = (bus * gran_dry) + gran

rev = WGVerb(serial_bus, feedback=0.8, cutoff=5000, bal=0.3)

# 4-Channel Delay Matrix (8 second delay time)
delay_time = 8.0
delay_feedback_sig = Sig(0)  # Controlled by delay mode
delay_feedback = Port(delay_feedback_sig, 0.1, 0.1)

# Create 4 delay lines (one per channel)
delays = [
    Delay(rev[i], delay=delay_time, feedback=delay_feedback, maxdelay=10)
    for i in range(4)
]

# Delay routing matrix - controlled by delay_mode
# Mode 0: No delay (bypass)
# Mode 1: Circular (each channel feeds into next: 0->1->2->3->0)
# Mode 2: Ping-pong (0<->1, 2<->3)
delay_matrix_sigs = [[Sig(0) for _ in range(4)] for _ in range(4)]
delay_matrix = [[Port(delay_matrix_sigs[i][j], 0.05, 0.05) for j in range(4)] for i in range(4)]

# Mix delayed signals with routing matrix
delay_outputs = []
for i in range(4):
    # Each output is a mix of all 4 delay lines with matrix gains
    channel_mix = delays[0] * delay_matrix[0][i] + \
                  delays[1] * delay_matrix[1][i] + \
                  delays[2] * delay_matrix[2][i] + \
                  delays[3] * delay_matrix[3][i]
    delay_outputs.append(channel_mix)

# Final output: reverb + delay mix
# Master Volume
master_vol = Sig(0.6)
master_vol_port = Port(master_vol, 0.1, 0.1)

# Apply master gain
gained_mix = Mix([Sig(rev[i]) + delay_outputs[i] for i in range(4)], voices=4) * master_vol_port

# Master limiter (-6dB threshold, 0.1s falltime)
limited = Compress(gained_mix, thresh=-6, ratio=20, knee=0.5, risetime=0.001, falltime=0.1, mul=1)

final_output = limited.out()

def update_gran_state():
    """Update granulator parameters based on gran_mode"""
    if gran_mode == 0:
        gran_wet.value = 0
        gran_pos_sel.voice = 0
        gran_dur_sel.voice = 0
        gran_dens_sel.voice = 0
    elif gran_mode == 1:
        gran_wet.value = 0.3
        gran_pos_sel.voice = 1 # Random Pos
        gran_dur_sel.voice = 0
        gran_dens_sel.voice = 0
    elif gran_mode == 2:
        gran_wet.value = 0.5
        gran_pos_sel.voice = 1
        gran_dur_sel.voice = 1 # Random Dur
        gran_dens_sel.voice = 1 # Random Dens

def update_delay_matrix():
    """Update delay routing matrix based on delay_mode"""
    if delay_mode == 0:
        # Off: no delay routing
        delay_feedback_sig.value = 0
        for i in range(4):
            for j in range(4):
                delay_matrix_sigs[i][j].value = 0
    elif delay_mode == 1:
        # Circular: 0->1->2->3->0
        delay_feedback_sig.value = 0.6
        for i in range(4):
            for j in range(4):
                if j == (i + 1) % 4:
                    delay_matrix_sigs[i][j].value = 1.0
                else:
                    delay_matrix_sigs[i][j].value = 0
    elif delay_mode == 2:
        # Ping-pong: 0<->1, 2<->3
        delay_feedback_sig.value = 0.6
        for i in range(4):
            for j in range(4):
                delay_matrix_sigs[i][j].value = 0
        # 0 <-> 1
        delay_matrix_sigs[0][1].value = 1.0
        delay_matrix_sigs[1][0].value = 1.0
        # 2 <-> 3
        delay_matrix_sigs[2][3].value = 1.0
        delay_matrix_sigs[3][2].value = 1.0

# --- 7. Pyo-based Ball with Metro timing ---
class MetroBall:
    """Ball physics driven by Pyo Metro for sample-accurate timing"""
    def __init__(self, index, r, g, lp_handle, start_pos=None):
        self.index, self.r, self.g, self.lp = index, r, g, lp_handle
        # Select note from the current musical scale
        #note = get_random_note_in_scale(MIDI_RANGES[index][0], MIDI_RANGES[index][1], selected_scale)
        
        ball_scale_name = random.choice(BALL_SCALE_FAMILIES[index])
        ball_scale = SCALES[ball_scale_name]
        note = get_random_note_in_scale(MIDI_RANGES[index][0], MIDI_RANGES[index][1], ball_scale)
        print(f"--- Ball {index}: Using scale {ball_scale_name} ---")

        self.freq_val = midiToHz(note)
        ball_freqs[index] = self.freq_val
        self.amp_val = 0.06 + (index * 0.025)
        
        if start_pos:
            self.x, self.y = start_pos
        else:
            self.x, self.y = random.uniform(0, 7), random.uniform(1, 8)
        
        self.angle = random.uniform(0, 2*math.pi)
        self.sleep = 0.08
        self.dur = random.uniform(0.1, 2.5)
        self.active, self.fast_decay, self.last_grid_pos = True, False, None
        
        # Create Metro for this ball
        # Metro time is controlled by a Sig that can be updated
        self.metro_time = Sig(self.sleep)
        self.metro = Metro(time=self.metro_time).play()
        
        # TrigFunc calls update method on each metro tick
        self.trig = TrigFunc(self.metro, self.update)
        
        print(f"--- Ball {self.index}: Launch (Pos: {int(self.x)}/{int(self.y)}), Metro started with time={self.sleep}s ---")
        # LED will be handled by led_update_loop thread

    def update(self):
        """Called by Pyo Metro - runs at metro frequency"""
        try:
            self._do_update()
        except Exception as e:
            print(f"--- Ball {self.index}: Error in update: {e} ---")
            try:
                self.stop()
            except:
                pass
    
    def _do_update(self):
        """Actual update logic"""
        # Debug: print first few updates
        if not hasattr(self, 'update_count'):
            self.update_count = 0
            print(f"--- Ball {self.index}: First update called! ---")
        
        self.update_count += 1
        if not self.active or self.sleep >= STOP_THRESHOLD:
            self.stop()
            return
        
        # Calculate next position
        next_x = self.x + math.cos(self.angle)
        next_y = self.y + math.sin(self.angle)
        
        hit = False
        hit_obstacle = False
        
        # Check obstacle collision
        next_gx, next_gy = int(round(next_x)), int(round(next_y))
        if (next_gx, next_gy) in obstacles:
            self.angle = -self.angle + random.uniform(-ANGLE_VAR, ANGLE_VAR)
            hit = True
            hit_obstacle = True
        else:
            self.x, self.y = next_x, next_y
        
        # Check boundaries
        if wrap_enabled:
            if self.x < 0: self.x = 7; hit = True
            elif self.x > 7: self.x = 0; hit = True
            if self.y < 1: self.y = 8; hit = True
            elif self.y > 8: self.y = 1; hit = True
        else:
            if self.x <= 0 or self.x >= 7: 
                self.angle = math.pi - self.angle + random.uniform(-ANGLE_VAR, ANGLE_VAR)
                hit = True
            if self.y <= 1 or self.y >= 8: 
                self.angle = -self.angle + random.uniform(-ANGLE_VAR, ANGLE_VAR)
                hit = True
            self.x, self.y = max(0, min(self.x, 7)), max(1, min(self.y, 8))

        voices[self.index].update_panning(get_quad_gains(self.x, self.y))
        
        gx, gy = int(round(self.x)), int(round(self.y))
        if (gx, gy) != self.last_grid_pos:
            try:
                with lock:
                    # Clear old position
                    if self.last_grid_pos in grid_map and grid_map[self.last_grid_pos] == self.index: 
                        del grid_map[self.last_grid_pos]
                    
                    # FM collision check
                    if fm_enabled and (gx, gy) in grid_map:
                        other = grid_map[(gx, gy)]
                        voices[self.index].set_fm(ball_freqs[other])
                        voices[other].set_fm(self.freq_val)
                    
                    # Register new position
                    grid_map[(gx, gy)] = self.index
            except:
                pass  # Don't crash on lock failure
            
            # Trigger sound
            try:
                if hit_obstacle:
                    voices[self.index].trigger_wall_hit(self.freq_val, self.amp_val, self.dur)
                else:
                    voices[self.index].trigger(self.freq_val, self.amp_val, self.dur)
            except:
                pass
            
            self.last_grid_pos = (gx, gy)
        
        if hit:
            voices[self.index].stop_fm()
            if self.fast_decay:
                self.sleep *= 1.7
            else:
                self.sleep *= FRICTION_VALUES[lifetime_mode]
            
            # Update metro time (time between ticks)
            self.metro_time.value = self.sleep
        
        if self.fast_decay:
            self.sleep *= 1.15
            self.metro_time.value = self.sleep

    def stop(self):
        """Stop the ball cleanly"""
        try:
            self.active = False
            self.metro.stop()
            self.trig.stop()
            
            with lock:
                if self.last_grid_pos in grid_map:
                    del grid_map[self.last_grid_pos]
            
            # LED cleanup will be handled by led_update_loop
            print(f"--- Ball {self.index}: Expired ---")
        except Exception as e:
            print(f"--- Ball {self.index}: Error in stop: {e} ---")

# --- 8. LED Update Thread (separate from audio) ---
def led_update_loop():
    """Update LEDs based on grid_map - runs in separate thread"""
    last_grid_state = {}
    last_ball_active = [False] * MAX_BALLS
    
    while True:
        try:
            with lock:
                current_state = dict(grid_map)  # Copy current state
                current_ball_active = [balls[i] and balls[i].active for i in range(MAX_BALLS)]
            
            # Update grid LEDs
            for pos, ball_idx in current_state.items():
                if pos not in last_grid_state:
                    # New position - light it up
                    gx, gy = pos
                    if (gx, gy) not in obstacles:
                        r, g = COLOR_PAIRS[ball_idx]
                        lp_led(gx, gy, r, g)
            
            for pos in last_grid_state:
                if pos not in current_state:
                    # Position cleared - turn off LED
                    gx, gy = pos
                    if (gx, gy) in obstacles:
                        lp_led(gx, gy, 3, 3)  # Restore obstacle
                    else:
                        lp_led(gx, gy, 0, 0)  # Clear
            
            # Update side button indicators
            for i in range(MAX_BALLS):
                if current_ball_active[i] != last_ball_active[i]:
                    if current_ball_active[i]:
                        r, g = COLOR_PAIRS[i]
                        lp_led(8, i + 1, r, g)
                    else:
                        lp_led(8, i + 1, 0, 0)
            
            last_grid_state = current_state
            last_ball_active = current_ball_active
            time.sleep(0.02)  # 50 Hz update rate
        except Exception as e:
            # print(f"LED update error: {e}")
            time.sleep(0.05)

# Start LED update thread
led_thread = threading.Thread(target=led_update_loop, daemon=True)
led_thread.start()
print("--- LED update thread started ---")

# --- 9. Resets & Triggers ---
def reset_fm():
    print("--- Feature Timer: FM reset to Off (Green) ---")
    global fm_enabled; fm_enabled = False; update_ui()

def reset_gran():
    print("--- Feature Timer: Granulation reset to Off (Green) ---")
    global gran_mode; gran_mode = 0; update_gran_state(); update_ui()

def reset_wrap():
    print("--- Feature Timer: No walls reset to Off (Green) ---")
    global wrap_enabled; wrap_enabled = False; update_ui()

def reset_obstacles():
    print("--- Feature Timer: Obstacles reset to Idle (Green) ---")
    global obstacle_mode; obstacle_mode = 0; update_ui()

def reset_delay():
    print("--- Feature Timer: Delay reset to Off (Green) ---")
    global delay_mode; delay_mode = 0
    update_delay_matrix()
    update_ui()

def remove_obstacles_sequence():
    """Remove all obstacles piece by piece over 8 seconds"""
    print("--- Obstacle Mode: Removing all obstacles [8s] ---")
    
    with lock:
        obstacle_list = list(obstacles)
    
    if len(obstacle_list) == 0:
        print("--- No obstacles to remove ---")
        return
    
    delay = 8.0 / len(obstacle_list)
    
    for pos in obstacle_list:
        with lock:
            if pos in obstacles:
                obstacles.remove(pos)
                gx, gy = pos
                lp_led(gx, gy, 0, 0)
        time.sleep(delay)
    
    print("--- Obstacle removal complete ---")

def relocate_obstacles_sequence():
    """Randomly move all obstacles piece by piece over 8 seconds"""
    print("--- Obstacle Mode: Randomly relocating obstacles [8s] ---")
    
    with lock:
        obstacle_list = list(obstacles)
    
    if len(obstacle_list) == 0:
        print("--- No obstacles to relocate ---")
        reset_obstacles()
        return
    
    delay = 8.0 / len(obstacle_list)
    
    for old_pos in obstacle_list:
        # Find new random position (not occupied by ball or another obstacle)
        for _ in range(50):  # Try up to 50 times
            new_x = random.randint(0, 7)
            new_y = random.randint(1, 8)
            new_pos = (new_x, new_y)
            
            with lock:
                # Check if position is free
                if new_pos not in obstacles and new_pos not in grid_map:
                    # Remove from old position
                    if old_pos in obstacles:
                        obstacles.remove(old_pos)
                        ox, oy = old_pos
                        lp_led(ox, oy, 0, 0)
                    
                    # Add to new position
                    obstacles.add(new_pos)
                    lp_led(new_x, new_y, 3, 3)
                    break
        
        time.sleep(delay)
    
    print("--- Obstacle relocation complete ---")

def warp_sequence():
    global warp_running
    warp_running = True; update_ui()
    print("--- Top Button 2: Warp Jump Initialized ---")
    for i in range(MAX_BALLS):
        nx, ny = random.uniform(0, 7), random.uniform(1, 8)
        with lock:
            if balls[i] and balls[i].active:
                balls[i].x, balls[i].y = nx, ny
                voices[i].update_panning(get_quad_gains(nx, ny))
                voices[i].trigger(midiToHz(random.randint(40,80)), 0.15, 2.0)
        time.sleep(1.0)
    warp_running = False; update_ui()

def trigger_ball(idx):
    with lock:
        if balls[idx] is None or not balls[idx].active:
            balls[idx] = MetroBall(idx, *COLOR_PAIRS[idx], lp)
        else:
            print(f"--- Ball {idx}: 2-Second Fast Kill Triggered ---")
            balls[idx].fast_decay = True

def toggle_obstacle(x, y):
    with lock:
        if (x, y) in obstacles:
            obstacles.remove((x, y))
            lp_led(x, y, 0, 0)
        else:
            obstacles.add((x, y))
            lp_led(x, y, 3, 3)

# --- 9. Ableton Link Setup (via MIDI Clock) ---
def setup_link():
    """Setup Ableton Link sync via MIDI clock output"""
    global link_metro
    # Create a master metro at current tempo
    link_metro = Metro(time=60.0/GLOBAL_TEMPO/24).play()  # MIDI clock = 24 ppqn
    
    # Send MIDI clock messages
    def send_clock():
        # This would send MIDI clock - requires MIDI output setup
        # For now, just print tempo info
        pass
    
    # TrigFunc(link_metro, send_clock)
    print(f"--- Ableton Link: Tempo = {GLOBAL_TEMPO} BPM ---")

setup_link()

# --- 10. Scalar Start ---
scalar = random.randint(1, 8)
for c in range(scalar):
    for r in range(1, 9): lp_led(c, r, 3, 3)
base_f = 1.01 + (0.12 / scalar)
FRICTION_VALUES = [base_f * 1.12, base_f, base_f * 0.96]

while not lp.ButtonStateRaw(): time.sleep(0.01)
lp.Reset(); update_ui()

# --- 11. Main Loop ---
try:
    launched = False
    while True:
        ev = lp.ButtonStateRaw()
        if ev and ev[1]:
            bid = ev[0]
            print(f"--- Button pressed: {bid} ---")
            idx = -1
            
            # Main Grid: Obstacle Toggle
            if mode == "Mk1":
                gx =  bid % 16 
                gy = (bid // 16) + 1
                if 0 <= gx <= 7 and 1 <= gy <= 8:
                    print(f"--- Obstacle toggle at {gx}, {gy} ---")
                    toggle_obstacle(gx, gy)
            else:
                gx = (bid % 10) - 1
                gy = 9 - (bid // 10)
                if 0 <= gx <= 7 and 1 <= gy <= 8:
                    print(f"--- Obstacle toggle at {gx}, {gy} ---")
                    toggle_obstacle(gx, gy)

            if mode == "Mk1" and bid in SIDE_MK1: idx = SIDE_MK1.index(bid)
            elif mode == "Mk2" and bid in SIDE_MK2: idx = SIDE_MK2.index(bid)
            if 0 <= idx < MAX_BALLS: 
                print(f"--- Triggering ball {idx} ---")
                trigger_ball(idx)

            T = TOP_MK1 if mode == "Mk1" else TOP_MK2
            if bid == T[0]:
                if delay_mode == 0:
                    delay_mode = 1
                    delay_timer = threading.Timer(8.0, reset_delay)
                    delay_timer.start()
                    print("--- Top Button 0: Delay set to Circular (Red) [8s Lock] ---")
                elif delay_mode == 1:
                    delay_mode = 2
                    print("--- Top Button 0: Delay set to Ping-Pong (Amber) ---")
                update_delay_matrix()
                update_ui()
            elif bid == T[1]:
                if not fm_enabled:
                    fm_enabled = True; fm_timer = threading.Timer(8.0, reset_fm); fm_timer.start()
                    print("--- Top Button 1: FM Collision Enabled [8s Lock] ---")
                    update_ui()
            elif bid == T[2] and not warp_running:
                threading.Thread(target=warp_sequence, daemon=True).start()
            elif bid == T[3]:
                if gran_mode == 0:
                    gran_mode = 1; gran_timer = threading.Timer(8.0, reset_gran); gran_timer.start()
                    print("--- Top Button 3: Granulation set to Active (Red) [8s Lock] ---")
                elif gran_mode == 1:
                    gran_mode = 2
                    print("--- Top Button 3: Granulation set to Random (Amber) ---")
                update_gran_state()
                update_ui()
            elif bid == T[4]:
                if not wrap_enabled:
                    wrap_enabled = True; wrap_timer = threading.Timer(8.0, reset_wrap); wrap_timer.start()
                    print("--- Top Button 4: Wrap, no-walls set to Active (Red) [8s Lock] ---")
                    update_ui()
            elif bid == T[5]:
                # Button 5: Obstacle mode (Moved from T[7])
                if obstacle_mode == 0:
                    obstacle_mode = 1
                    obstacle_timer = threading.Timer(8.0, reset_obstacles)
                    obstacle_timer.start()
                    print("--- Top Button 5: Obstacles set to Remove (Red) [8s Lock] ---")
                    threading.Thread(target=remove_obstacles_sequence, daemon=True).start()
                elif obstacle_mode == 1:
                    obstacle_mode = 2
                    print("--- Top Button 5: Obstacles set to Relocate (Amber) ---")
                    threading.Thread(target=relocate_obstacles_sequence, daemon=True).start()
                update_ui()
            elif bid == T[6]:
                master_vol.value = max(0.0, master_vol.value - 0.05)
                print(f"--- Master Volume: {master_vol.value:.2f} ---")
                update_ui()
            elif bid == T[7]:
                master_vol.value = min(1.0, master_vol.value + 0.05)
                print(f"--- Master Volume: {master_vol.value:.2f} ---")
                update_ui()

        active_count = sum(1 for b in balls if b and b.active)
        if active_count > 0: launched = True
        if launched and active_count == 0: break
        time.sleep(0.01)

except KeyboardInterrupt: pass
finally:
    for t in [lt_timer, fm_timer, gran_timer, wrap_timer, obstacle_timer, delay_timer]:
        if t: t.cancel()
    for b in balls:
        if b and b.active: b.stop()
    s.stop()
    s.shutdown()
    time.sleep(0.5); lp.Reset(); lp.Close()
    print("--- System Shutdown: Goodbye ---")
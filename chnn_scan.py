import os
import wx
from PIL import Image
from pyo import *

AUDIO_DEVICE = 10
AUDIO_HOST = 'asio'
BUFFER_SIZE = 512 

"""
ChNN sonic image
================================================================
This script is a quadraphonic image-to-sound sonifier. It scans
a digital image pixel-by-pixel and shows the position on GUI, while
allowing to control the speed, reverb and compression for a better
listening experience.
"""

# 1. File Path Configuration
path = './'
file = '201310 ChNN Barcelona by Paolo Fassoli_09_square'
target_file = path + file + '.jpg'

# 2. Server Setup
s = Server(sr=48000, nchnls=4, duplex=0, buffersize=BUFFER_SIZE, winhost=AUDIO_HOST)
s.setOutputDevice(AUDIO_DEVICE)
s.deactivateMidi()
s.boot().start()


# 3. Image Processing
def load_image_data(img_path, size=(64, 64)):
    img = Image.open(img_path).convert('RGB')
    img_res = img.resize(size)
    pixels = list(img_res.getdata())
    img_display = img.resize((400, 400))
    return pixels, size[0], size[1], img_display

pixel_data, width, height, display_img = load_image_data(target_file)
num_pixels = len(pixel_data)

# 4. Synth Engine
env = Adsr(attack=0.002, decay=0.03, sustain=0.1, release=0.01, dur=0.05)
freq_ctrl = Sig(440)
harm_ctrl = Sig(10)
wave = Blit(freq=[freq_ctrl, freq_ctrl*1.005], harms=harm_ctrl, mul=env).mix(1)

# 5. Effects (Reverb & Compress)
rev_mix = Sig(0.3)
reverb = Freeverb(wave, size=0.8, damp=0.5, bal=rev_mix)
comp_thresh, comp_ratio = Sig(-20), Sig(4)
comp = Compress(reverb, thresh=comp_thresh, ratio=comp_ratio, risetime=0.01, falltime=0.1)

# 6. Quad Routing & Level Control
db_val = Sig(6)
master_gain = DBToA(db_val)
pan_front, pan_rear = Sig(0.5), Sig(0.5)
pan_left, pan_right = Sig(0.5), Sig(0.5)

out_fl = (comp * pan_left * pan_front * master_gain).out(0)
out_fr = (comp * pan_right * pan_front * master_gain).out(1)
out_rl = (comp * pan_left * pan_rear * master_gain).out(2)
out_rr = (comp * pan_right * pan_rear * master_gain).out(3)

# 7. Visual Analysis
sc = Scope(comp)
sp = Spectrum(comp)

# 8. wxPython Interface with Compact Sliders
class SonifierFrame(wx.Frame):
    def __init__(self, parent, title, img_obj):
        super(SonifierFrame, self).__init__(parent, title=title, size=(420, 780))
        self.panel = wx.Panel(self)
        
        # Display Image
        wx_img = wx.Image(img_obj.width, img_obj.height)
        wx_img.SetData(img_obj.tobytes())
        self.bmp = wx.Bitmap(wx_img)
        self.canvas = wx.StaticBitmap(self.panel, -1, self.bmp, pos=(0, 0))
        self.cursor = wx.Panel(self.panel, size=(400//width, 400//height), pos=(-10, -10))
        self.cursor.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Start Button
        y_pos = 410
        self.start_btn = wx.Button(self.panel, label="START SCAN", pos=(10, y_pos), size=(380, 35))
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)

        # Slider Helper Function for Thinness
        def create_thin_slider(label, val, mini, maxi, y):
            lbl = wx.StaticText(self.panel, label=label, pos=(15, y))
            lbl.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            # Height set to 20 for a thinner look
            slider = wx.Slider(self.panel, value=val, minValue=mini, maxValue=maxi, 
                               pos=(10, y+15), size=(380, 20), style=wx.SL_HORIZONTAL)
            return slider

        y_pos += 50
        self.vol_slider = create_thin_slider("Volume (dB)", 6, -60, 18, y_pos)
        self.vol_slider.Bind(wx.EVT_SLIDER, self.update_vol)
        
        y_pos += 45
        self.speed_slider = create_thin_slider("Scan Speed", 40, 5, 200, y_pos)
        self.speed_slider.Bind(wx.EVT_SLIDER, self.update_speed)
        
        y_pos += 45
        self.rev_slider = create_thin_slider("Reverb Mix", 30, 0, 100, y_pos)
        self.rev_slider.Bind(wx.EVT_SLIDER, self.update_rev)

        y_pos += 45
        self.thresh_slider = create_thin_slider("Comp Threshold (dB)", -20, -60, 0, y_pos)
        self.thresh_slider.Bind(wx.EVT_SLIDER, self.update_thresh)

        y_pos += 45
        self.ratio_slider = create_thin_slider("Comp Ratio", 4, 1, 20, y_pos)
        self.ratio_slider.Bind(wx.EVT_SLIDER, self.update_ratio)

    def on_start(self, e):
        self.start_btn.Disable()
        count.reset()
        met.play()

    def update_vol(self, e): db_val.value = self.vol_slider.GetValue()
    def update_speed(self, e): met.time = self.speed_slider.GetValue() / 1000.0
    def update_rev(self, e): rev_mix.value = self.rev_slider.GetValue() / 100.0
    def update_thresh(self, e): comp_thresh.value = self.thresh_slider.GetValue()
    def update_ratio(self, e): comp_ratio.value = self.ratio_slider.GetValue()
    def update_cursor(self, x, y):
        self.cursor.SetPosition((int((x/width)*400), int((y/height)*400)))

# 9. Logic
met = Metro(time=0.04)
count = Counter(met, min=0, max=num_pixels)

def update_params():
    idx = int(count.get())
    if idx < num_pixels - 1:
        r, g, b = pixel_data[idx]
        x_idx, y_idx = idx % width, idx // width
        f_gain = 1.0 - (y_idx / (height - 1)) if height > 1 else 1.0
        pan_front.value, pan_rear.value = f_gain, 1.0 - f_gain
        r_side = x_idx / (width - 1) if width > 1 else 0.5
        pan_right.value, pan_left.value = r_side, 1.0 - r_side
        gray = (0.299*r + 0.587*g + 0.114*b)
        freq_ctrl.value = midiToHz((gray / 255.0) * 127.0)
        total = r + g + b + 1
        harm_ctrl.value = max(1, (r/total)*45 + (g/total)*20 + (b/total)*5)
        env.mul = (gray / 255.0) * 0.2
        env.play()
        wx.CallAfter(frame.update_cursor, x_idx, y_idx)
    else:
        met.stop()
        wx.CallAfter(frame.start_btn.Enable)

trig = TrigFunc(met, update_params)

# 10. Run
s.start()
app = wx.App(False)
frame = SonifierFrame(None, "Paolo Fassoli - Compact Quad Scan", display_img)
frame.Show()
app.MainLoop()
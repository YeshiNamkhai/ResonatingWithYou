from pyo import *

print("Audio host APIS:")
pa_list_host_apis()
pa_list_devices()

print("Default input device: %i" % pa_get_default_input())
print("Default output device: %i" % pa_get_default_output())

"""
s = Server(sr=48000, nchnls=4, duplex=0, winhost="asio")
s.setOutputDevice(10)
s.deactivateMidi()   
s.boot()
"""

import pyaudio
import wave
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show
import numpy as np


# example code for PyAudio
#p = pyaudio.PyAudio()

#stream = p.open() # need to put arguments in here

# Code to play around with Bokeh

# fake data
N = 100
x = np.linspace(0, 4*np.pi, N)
y0 = np.sin(x)


output_file("sound.html")

# example plot
s1 = figure(width=250, plot_height=250, title=None)
s1.circle(x, y0, size=10, color="navy", alpha=0.5)

#display plot
show(s1)

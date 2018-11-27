# see "License Acknowledgement" for accrediton to original source code
# adapted from florian, who extended from the SciPy 2015 Vispy talk opening example
# https://github.com/flothesof/LiveFFTPitchTracker

### NOTES ###
# sine tone generater with Hz, sliding bar (other goal) -> separate
# note to self: might want to add in functionality where you can pick your sound source,
# in order to be more adaptable

import sys
import threading
import atexit
import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import figure
from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

# gets you the instance of the item we are gathering data from
class SoundRecorder(object):

    # can go back and change rate and chunksize if needed
    def __init__(self, rate=4000, chunksize=1024):
        self.rate = rate
        self.chunksize = chunksize
        self.stream = 0

        # initialize a pyAudio session
        self.p = pyaudio.PyAudio()
        self.choices = []
        self.updateInputOptions()

        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def updateInputOptions(self):
        # change channel to be USB source
        self.choices.clear()
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        # get the index we need to read from
        # for actual device, want name == "USB Audio CODEC"
        # when practicing with mic -> "Yeti Stereo Microphone"

        for i in range(0, numdevices):
            if ((self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0):
                name = self.p.get_device_info_by_host_api_device_index(0, i).get('name')
                index = i
                stringLabel = str(name) + " - " + str(index)
                self.choices.append(stringLabel)

    def chooseInput(self, text):
        if(text == "No Input Selected"):
            return
        else:
            parts = text.split()
            index = int(parts[-1])
            self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame, input_device_index=index)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.fromstring(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames

    def start(self):
        if(self.stream == 0):
            return
        else:
            self.stream.start_stream()

    def close(self):
        if (self.stream == 0):
            return
        else:
            with self.lock:
                self.stop = True
            self.stream.close()
            self.p.terminate()


class MplFigure(object):
    def __init__(self, parent):
        self.figure = figure.Figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent)

class LiveFFTWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        #init class data # note: flipped from being after initUI
        self.initData()

        # customize the UI
        self.initUI()


        # connect slots
        self.connectSlots()

        # init MPL widget
        self.initMplWidget()



    def initUI(self):
        # timer for calls, taken from:
        # http://ralsina.me/weblog/posts/BB974.html
        timer = QtCore.QTimer()
        timer.timeout.connect(self.handleNewData)
        # timer.start(50) # don't start until hit "start button"
        # keep reference to timer
        self.timer = timer

        # create start and stop button
        # hold together in a horizontal box
        hbox_startStop = QtWidgets.QHBoxLayout()
        startButton = QtWidgets.QPushButton("Start Recording")
        stopButton = QtWidgets.QPushButton("Stop Recording")
        startButton.clicked.connect(lambda: self.startRecording())
        stopButton.clicked.connect(lambda: self.stopRecording())
        hbox_startStop.addWidget(startButton)
        hbox_startStop.addWidget(stopButton)

        # references to buttons for later use
        self.startButton = startButton
        self.stopButton = stopButton

        # define chooseInput section
        hbox_chooseInput = QtWidgets.QHBoxLayout()
        comboLabel = QtWidgets.QLabel("Audio Input: ")
        comboLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItem("No Input Selected")
        for item in self.sound.choices:
            self.comboBox.addItem(item)
        self.comboBox.activated[str].connect(self.sound.chooseInput)
        self.refreshButton = QtWidgets.QPushButton("Refresh Options")
        self.refreshButton.clicked.connect(lambda: self.updateChoiceUI())
        hbox_chooseInput.addWidget(comboLabel)
        hbox_chooseInput.addWidget(self.comboBox)
        hbox_chooseInput.addWidget(self.refreshButton)

        # create a vertical box to hold all items in
        vbox = QtWidgets.QVBoxLayout()

        # add in the buttons
        vbox.addLayout(hbox_startStop)

        # add in the main figure and it's toolbar
        self.main_figure = MplFigure(self)
        vbox.addWidget(self.main_figure.toolbar)
        vbox.addWidget(self.main_figure.canvas)

        vbox.addLayout(hbox_chooseInput)

        self.setLayout(vbox)

        # set the size the window opens to
        self.setGeometry(300, 300, 1000, 1000)
        # set the title
        self.setWindowTitle('Sound Visualization')
        self.show()

    def updateChoiceUI(self):
        self.sound.updateInputOptions()
        self.comboBox.clear()
        self.comboBox.addItem("No Input Selected")
        for item in self.sound.choices:
            self.comboBox.addItem(item)
        self.comboBox.update()

    def startRecording(self):
        self.timer.start(50)

    def stopRecording(self):
        self.timer.stop()

    def initData(self):
        sound = SoundRecorder()
        sound.start()

        # keeps reference to sound data
        self.sound = sound

        # computes the parameters that will be used during plotting
        self.time_vect = np.arange(sound.chunksize, dtype=np.float32) / sound.rate * 1000

    def connectSlots(self):
        pass

    def initMplWidget(self):
        # create the plot to represent the sound wave
        self.ax_top = self.main_figure.figure.add_subplot(211)
        self.ax_top.set_ylim(-32768, 32768)
        self.ax_top.set_xlim(0, self.time_vect.max())
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6)

        self.line_top, = self.ax_top.plot(self.time_vect,
                                         np.ones_like(self.time_vect))

    def handleNewData(self):
        """ handles the asynchroneously collected sound chunks """
        # gets the latest frames
        frames = self.sound.get_frames()

        if len(frames) > 0:
            # keeps only the last frame
            current_frame = frames[-1]
            # plots the time signal
            self.line_top.set_data(self.time_vect, current_frame)

            # refreshes the plots
            self.main_figure.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LiveFFTWidget()
    sys.exit(app.exec_())

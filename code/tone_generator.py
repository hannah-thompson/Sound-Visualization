### NOTES ###


import sys
import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import figure
from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


# create our Oscillator
class ToneGenerator(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # define commonly shared values
        self.currentFrequency1 = 0
        self.currentAmplitude1 = 1.0
        # not using option to hide overlay currently
        self.y = 0
        self.isPlaying1 = False
        self.phase1 = 0

        # customize the UI
        self.initUI()

        # generate initial pitch of 0
        self.generatePitch1()

    def initUI(self):
        # create a timer to keep calling the pitch player
        timer = QtCore.QTimer()
        timer.timeout.connect(self.play_Pitch)
        self.timer = timer

        ### BEGIN TOP ROW ###

        # will hold all of the top row frequency controls
        vbox = QtWidgets.QVBoxLayout()

        # define slider
        self.freqSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.freqSlider.setRange(0, 1000)
        self.freqSlider.setValue(6)
        self.freqSlider.valueChanged.connect(lambda: self.changeFrequency1())

        # define label
        currentFreq = QtWidgets.QLabel("6 Times per Second")
        currentFreq.setAlignment(QtCore.Qt.AlignCenter)
        self.currentFreq = currentFreq

        # define Hz buttons
        button_hbox = QtWidgets.QHBoxLayout()
        two = QtWidgets.QPushButton("2 Hz")
        four = QtWidgets.QPushButton("4 Hz")
        two.clicked.connect(lambda: self.updateFrequency(2))
        four.clicked.connect(lambda: self.updateFrequency(4))
        button_hbox.addWidget(two)
        button_hbox.addWidget(four)
        # vbox.addLayout(button_hbox)


        # add slider
        vbox.addWidget(self.freqSlider)

        # add label
        vbox.addWidget(currentFreq)

        hbox_startStop = QtWidgets.QHBoxLayout()
        startButton = QtWidgets.QPushButton("Play")
        stopButton = QtWidgets.QPushButton("Stop")
        startButton.clicked.connect(lambda: self.startPlaying())
        stopButton.clicked.connect(lambda: self.stopPlaying())
        hbox_startStop.addWidget(startButton)
        hbox_startStop.addWidget(stopButton)
        vbox.addLayout(hbox_startStop)





        self.setLayout(vbox)

        # set the size the window opens to
        self.setGeometry(300, 300, 1000, 1000)
        # set the title
        self.setWindowTitle('Tone Generator')
        self.show()

    # connected to first start button
    def startPlaying(self):
        self.isPlaying1 = True
        self.generatePitch1()
        self.start()

    # connected to first stop button
    def stopPlaying(self):
        self.isPlaying1 = False
        self.stop()

    # stops/updates the current running stream
    def stop(self):
        if((self.isPlaying1 == False)):
            self.timer.stop()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        else:
            self.generatePitch1()

    # starts the timer (timer connected to "play pitch")
    def start(self):
        self.timer.start()


    # generates the pitch stream to play
    def generatePitch1(self):
        self.p = pyaudio.PyAudio()
        fs = 44100  # sampling rate
        duration = 1 # play for 1 second

        # equation generated from top row
        equation1 = (np.sin(2 * np.pi * np.arange(fs * duration) * 0 / fs))
        # only generate if user has pressed play
        if(self.isPlaying1):
            f1 = self.currentFrequency1
            volume1 = 1.0
            phase1 = 0
            # added pi
            equation1 = volume1*(np.sin((2 * np.pi * np.arange(fs * duration) * f1 / fs)+ phase1))

        self.samples = (equation1).astype(np.float32).tobytes()
        # create stream
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=fs,
                                  output=True)

    # actually play the pitch from the stream we've created
    def play_Pitch(self):
        self.stream.write(self.samples)

    # connected to two frequency dials to update frequency
    # in the label, played pitch, and graph
    def changeFrequency1(self):
        self.f = self.freqSlider.value()

        self.currentFrequency1 = self.f
        self.currentFreq.setText(str(self.f) + " Times per Second")
        self.currentFreq.update()


        # regenerates pitch if currently playing
        if(self.isPlaying1):
            self.generatePitch1()

    def updateFrequency(self, freq):
        self.f = freq
        self.freqSlider.setValue(self.f)
        self.freqSlider.update()

        self.currentFrequency1 = self.f
        self.currentFreq.setText(str(self.f) + " Times per Second")
        self.currentFreq.update()

        # regenerates pitch if currently playing
        if (self.isPlaying1):
            self.generatePitch1()

        QtWidgets.QApplication.processEvents()


# run the program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ToneGenerator()
    sys.exit(app.exec_())

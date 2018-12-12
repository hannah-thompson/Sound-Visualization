# see "License Acknowledgement" for accrediton to original source code
# adapted from florian, who extended from the SciPy 2015 Vispy talk opening example
# https://github.com/flothesof/LiveFFTPitchTracker

### NOTES ###
# sine tone generater with Hz, sliding bar (other goal) -> separate
# frequency range from 0 to 1000 Hz # two frequencies
# each with own amplitude measure
# two frequencies displayed graphically separately
# at top have overlay
# fine and gross control with radio buttons // check for lag
# can we get the internal audio to route here?
# OR can we represent beats graphically without real time input..?
# have play/ stop button
# have ms
# other axis should scale to -1 to 1
# need to be able to measure amplitude at any point and want this scaled (height of wave)

# NOTE: use timer to implement the sine wave sound and remember to connect to stop/start buttons as well as frequency

import sys
import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import figure
from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class MplFigure(object):
    def __init__(self, parent):
        self.figure = figure.Figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        #self.toolbar = NavigationToolbar(self.canvas, parent)

class LiveFFTWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.currentFrequency1 = 0
        self.currentAmplitude1 = 1.0
        self.currentFrequency2 = 0
        self.currentAmplitude2 = 1.0
        self.lastSample1 = 0
        self.boolShowOverlay = False
        self.y = 0
        self.y1 = 0

        # customize the UI
        self.initUI()

        # init MPL widget
        self.initMplWidget()

    def initUI(self):
        # create a timer to keep calling sound file
        timer = QtCore.QTimer()
        timer.timeout.connect(self.generatePitch1)
        self.timer = timer

        timer1 = QtCore.QTimer()
        timer1.timeout.connect(self.generatePitch2)
        self.timer1 = timer1

        # will hold all of the controls
        vbox_FreqControls = QtWidgets.QVBoxLayout()


        # add Frequency Label
        freqLabel = QtWidgets.QLabel("Choose First Frequency:")
        vbox_FreqControls.addWidget(freqLabel)

        # add Frequency knobs
        hbox_FreqKnobs = QtWidgets.QHBoxLayout()
        radioFreq = QtWidgets.QDial()
        radioFreq.setNotchesVisible(True)
        radioFreq.setRange(0, 1000)
        radioFreq.setNotchTarget(20)
        radioFreq.valueChanged.connect(lambda: self.changeFrequency1())
        self.radioFreq = radioFreq

        currentFreq = QtWidgets.QLabel("0 Hz")
        self.currentFreq = currentFreq
        hbox_FreqKnobs.addWidget(radioFreq)
        hbox_FreqKnobs.addWidget(currentFreq)
        vbox_FreqControls.addLayout(hbox_FreqKnobs)

        # add amplitude Label
        ampLabel = QtWidgets.QLabel("Choose First Amplitude:")
        vbox_FreqControls.addWidget(ampLabel)

        # amplitude slider
        hbox_AmpChooser = QtWidgets.QHBoxLayout()
        self.ampSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ampSlider.setRange(0,100)
        self.ampSlider.setValue(100)
        self.currentAmp = QtWidgets.QLabel("1 Db")
        self.ampSlider.valueChanged.connect(lambda: self.changeAmplitude1())
        hbox_AmpChooser.addWidget(self.ampSlider)
        hbox_AmpChooser.addWidget(self.currentAmp)
        vbox_FreqControls.addLayout(hbox_AmpChooser)

        # create start and stop button
        # hold together in a horizontal box
        hbox_startStop = QtWidgets.QHBoxLayout()
        startButton = QtWidgets.QPushButton("Play")
        stopButton = QtWidgets.QPushButton("Stop")
        startButton.clicked.connect(lambda: self.startPlaying())
        stopButton.clicked.connect(lambda: self.stopPlaying())
        hbox_startStop.addWidget(startButton)
        hbox_startStop.addWidget(stopButton)
        vbox_FreqControls.addLayout(hbox_startStop)

        # references to buttons for later use
        self.startButton = startButton
        self.stopButton = stopButton

        # create horizontal box to hold whole top in
        hbox_TopRow = QtWidgets.QHBoxLayout()

        # add in the main figure and it's toolbar
        vbox_graph1 = QtWidgets.QVBoxLayout()
        self.main_figure = MplFigure(self)
        #vbox_graph1.addWidget(self.main_figure.toolbar)
        vbox_graph1.addWidget(self.main_figure.canvas)
        hbox_TopRow.addLayout(vbox_FreqControls)
        hbox_TopRow.addLayout(vbox_graph1)


        ####BEGIN 2nd
        # will hold all of the controls
        vbox_FreqControls1 = QtWidgets.QVBoxLayout()

        # add Frequency Label
        freqLabel1 = QtWidgets.QLabel("Choose Second Frequency:")
        vbox_FreqControls1.addWidget(freqLabel1)

        # add Frequency knobs
        hbox_FreqKnobs1 = QtWidgets.QHBoxLayout()
        radioFreq1 = QtWidgets.QDial()
        radioFreq1.setNotchesVisible(True)
        radioFreq1.setRange(0, 1000)
        radioFreq1.setNotchTarget(20)
        radioFreq1.valueChanged.connect(lambda: self.changeFrequency2())
        self.radioFreq1 = radioFreq1

        currentFreq1 = QtWidgets.QLabel("0 Hz")
        self.currentFreq1 = currentFreq1
        hbox_FreqKnobs1.addWidget(radioFreq1)
        hbox_FreqKnobs1.addWidget(currentFreq1)
        vbox_FreqControls1.addLayout(hbox_FreqKnobs1)

        # add amplitude Label
        ampLabel1 = QtWidgets.QLabel("Choose Second Amplitude:")
        vbox_FreqControls1.addWidget(ampLabel1)

        # amplitude slider
        hbox_AmpChooser1 = QtWidgets.QHBoxLayout()
        self.ampSlider1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ampSlider1.setRange(0, 100)
        self.ampSlider1.setValue(100)
        self.currentAmp1 = QtWidgets.QLabel("1 Db")
        self.ampSlider1.valueChanged.connect(lambda: self.changeAmplitude2())
        hbox_AmpChooser1.addWidget(self.ampSlider1)
        hbox_AmpChooser1.addWidget(self.currentAmp1)
        vbox_FreqControls1.addLayout(hbox_AmpChooser1)

        # create start and stop button
        # hold together in a horizontal box
        hbox_startStop1 = QtWidgets.QHBoxLayout()
        startButton1 = QtWidgets.QPushButton("Play")
        stopButton1 = QtWidgets.QPushButton("Stop")
        startButton1.clicked.connect(lambda: self.startPlaying1())
        stopButton1.clicked.connect(lambda: self.stopPlaying1())
        hbox_startStop1.addWidget(startButton1)
        hbox_startStop1.addWidget(stopButton1)
        vbox_FreqControls1.addLayout(hbox_startStop1)

        # references to buttons for later use
        self.startButton1 = startButton1
        self.stopButton1 = stopButton1

        # create horizontal box to hold whole top in
        hbox_BottomRow = QtWidgets.QHBoxLayout()

        # add in the main figure and it's toolbar
        vbox_graph2 = QtWidgets.QVBoxLayout()
        self.main_figure1 = MplFigure(self)
        #vbox_graph2.addWidget(self.main_figure1.toolbar)
        vbox_graph2.addWidget(self.main_figure1.canvas)
        hbox_BottomRow.addLayout(vbox_FreqControls1)
        hbox_BottomRow.addLayout(vbox_graph2)


        ### END 2nd

        hbox_lastRow = QtWidgets.QHBoxLayout()

        hbox_showHideButtons = QtWidgets.QHBoxLayout()
        showOverlayButton = QtWidgets.QPushButton("Show Overlay")
        showOverlayButton.clicked.connect(lambda: self.showOverlay())
        hideOverlayButton = QtWidgets.QPushButton("Hide Overlay")
        hideOverlayButton.clicked.connect(lambda: self.hideOverlay())
        hbox_showHideButtons.addWidget(showOverlayButton)
        hbox_showHideButtons.addWidget(hideOverlayButton)

        hbox_lastRow.addLayout(hbox_showHideButtons)

        vbox_graph3 = QtWidgets.QVBoxLayout()
        self.main_figure2 = MplFigure(self)
        #vbox_graph3.addWidget(self.main_figure2.toolbar)
        vbox_graph3.addWidget(self.main_figure2.canvas)

        hbox_lastRow.addLayout(vbox_graph3)


        # create a vertical box to hold all items in
        vbox = QtWidgets.QVBoxLayout()

        # add in the top row
        vbox.addLayout(hbox_TopRow)
        vbox.addLayout(hbox_BottomRow)
        vbox.addLayout(hbox_lastRow)

        self.setLayout(vbox)

        # set the size the window opens to
        self.setGeometry(300, 300, 1000, 1000)
        # set the title
        self.setWindowTitle('Oscillator')
        self.show()

    def startPlaying(self):
        self.timer.start()

    def stopPlaying(self):
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()

    def startPlaying1(self):
        self.timer1.start()

    def stopPlaying1(self):
        self.timer1.stop()
        self.stream1.stop_stream()
        self.stream1.close()

        self.p1.terminate()

    def showOverlay(self):
        self.boolShowOverlay = True
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)
        # refreshes the plots (put only when click out of page..?)
        self.main_figure2.canvas.draw()
        print("show")


    def hideOverlay(self):
        self.boolShowOverlay = False
        self.y2 = 0
        self.line_final.set_data(self.x, self.y2)
        print("hide")
        # refreshes the plots
        self.main_figure2.canvas.draw()

    # note to self: need to find way to get rid of clipping
    def generatePitch1(self):
        self.p = pyaudio.PyAudio()
        volume = self.currentAmplitude1  # range [0.0, 1.0]
        fs = 44100  # sampling rate, Hz, must be integer
        f = self.currentFrequency1  # sine frequency, Hz, may be float
        duration = 1.0
        # generate samples, note conversion to float32 array
        samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)
        samples = samples + self.lastSample1
        # this didn't fix it
        self.lastSample1 = samples[-1]

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=fs,
                                  output=True)

        self.stream.write(volume * samples)

    def generatePitch2(self):
        self.p1 = pyaudio.PyAudio()
        volume = self.currentAmplitude2  # range [0.0, 1.0]
        fs = 44100  # sampling rate, Hz, must be integer
        f = self.currentFrequency2  # sine frequency, Hz, may be float
        duration = 1.0
        # generate samples, note conversion to float32 array
        samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)
        #samples = samples + self.lastSample1
        # this didn't fix it
        #self.lastSample1 = samples[-1]

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        self.stream1 = self.p1.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=fs,
                                  output=True)

        self.stream1.write(volume * samples)

    def changeFrequency1(self):
        self.f =self.radioFreq.value()
        self.currentFrequency1 = self.f
        self.currentFreq.setText(str(self.f) + " Hz")
        self.currentFreq.update()
        self.y = self.amplitude*np.sin(2 * np.pi * self.f * self.x / self.Fs)
        self.line_top.set_data(self.x, self.y)

        #update overlay
        if(self.boolShowOverlay):
            self.y2 = self.y + self.y1
            self.line_final.set_data(self.x, self.y2)

            # refreshes the plots
            self.main_figure2.canvas.draw()

        # refreshes the plots
        self.main_figure.canvas.draw()

    def changeAmplitude1(self):
        self.amplitude = self.ampSlider.value()/100
        self.currentAmplitude1 = self.amplitude
        self.currentAmp.setText(str(self.amplitude) + " Db")
        self.currentAmp.update()
        self.y = self.amplitude * np.sin(2 * np.pi * self.f * self.x / self.Fs)
        self.line_top.set_data(self.x, self.y)

        # change overlay
        if (self.boolShowOverlay):
            self.y2 = self.y + self.y1
            self.line_final.set_data(self.x, self.y2)
            self.main_figure2.canvas.draw()

        # refreshes the plots
        self.main_figure.canvas.draw()

    def changeFrequency2(self):
        self.f1 =self.radioFreq1.value()
        self.currentFrequency2 = self.f1
        self.currentFreq1.setText(str(self.f1) + " Hz")
        self.currentFreq1.update()
        self.y1 = self.amplitude1*np.sin(2 * np.pi * self.f1 * self.x / self.Fs)
        self.line_bottom.set_data(self.x, self.y1)

        # change overlay
        if (self.boolShowOverlay):
            self.y2 = self.y + self.y1
            self.line_final.set_data(self.x, self.y2)
            self.main_figure2.canvas.draw()

        # refreshes the plots
        self.main_figure1.canvas.draw()

    def changeAmplitude2(self):
        self.amplitude1 = self.ampSlider1.value()/100
        self.currentAmplitude2 = self.amplitude1
        self.currentAmp1.setText(str(self.amplitude1) + " Db")
        self.currentAmp1.update()
        self.y1 = self.amplitude1 * np.sin(2 * np.pi * self.f1 * self.x / self.Fs)
        self.line_bottom.set_data(self.x, self.y1)

        # change overlay
        if (self.boolShowOverlay):
            self.y2 = self.y + self.y1
            self.line_final.set_data(self.x, self.y2)
            self.main_figure2.canvas.draw()

        # refreshes the plots
        self.main_figure1.canvas.draw()


    def initMplWidget(self):
        # create the plot to represent the sound wave
        self.ax_top = self.main_figure.figure.add_subplot(111) #changing to 111 makes bigger

        self.ax_top.set_ylim(-1, 1)
        self.ax_top.set_xlim(0,1000)
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6)

        self.f = 0
        self.Fs = 44100
        sample = 44100
        self.x = np.arange(sample)
        self.amplitude = 1
        self.y = self.amplitude*np.sin(2 * np.pi * self.f * self.x / self.Fs)


        self.line_top, = self.ax_top.plot(self.x, self.y)

        # BOTTOM PLOT
        self.bx_top = self.main_figure1.figure.add_subplot(111)  # changing to 111 makes bigger

        self.bx_top.set_ylim(-1, 1)
        self.bx_top.set_xlim(0, 1000)
        self.bx_top.set_xlabel(u'time (ms)', fontsize=6)

        self.f1 = 0
        self.Fs = 44100
        sample = 44100
        self.x1 = np.arange(sample)
        self.amplitude1 = 1
        self.y1 = self.amplitude1 * np.sin(2 * np.pi * self.f1 * self.x / self.Fs)

        self.line_bottom, = self.bx_top.plot(self.x, self.y1)

        # COMBINED PLOT
        self.cx_top = self.main_figure2.figure.add_subplot(111)  # changing to 111 makes bigger

        self.cx_top.set_ylim(-1, 1)
        self.cx_top.set_xlim(0, 1000)
        self.cx_top.set_xlabel(u'time (ms)', fontsize=6)

        self.f2 = 0
        self.Fs = 44100
        sample = 44100
        self.x2 = np.arange(sample)
        self.amplitude2 = 1
        self.y2 = self.amplitude2 * np.sin(2 * np.pi * self.f2 * self.x2 / self.Fs)

        self.line_final, = self.cx_top.plot(self.x2, self.y2)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LiveFFTWidget()
    sys.exit(app.exec_())

### NOTES ###
# unclear if there is a way to produce the sound
# without the lag that it causes to the controls
# if this is an issue we can force the sound to stop
# if the user starts to use the controls, forcing to press play again?


import sys
import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import figure
from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

# set up overall graph structure
class MplFigure(object):
    def __init__(self, parent):
        self.figure = figure.Figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        # can uncomment this and other .toolbars to add in a toolbar to each graph
        #self.toolbar = NavigationToolbar(self.canvas, parent)

# create our Oscillator
class Oscillator(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # define commonly shared values
        self.currentFrequency1 = 0
        self.currentAmplitude1 = 1.0
        self.currentFrequency2 = 0
        self.currentAmplitude2 = 1.0
        # not using option to hide overlay currently
        self.boolShowOverlay = False
        self.y = 0
        self.y1 = 0
        self.isPlaying1 = False
        self.isPlaying2 = False

        # customize the UI
        self.initUI()

        # initialize graphs
        self.initMplWidget()

        # generate initial pitch of 0
        self.generatePitch1()

    def initUI(self):
        # create a timer to keep calling the pitch player
        timer = QtCore.QTimer()
        timer.timeout.connect(self.play_Pitch)
        self.timer = timer

        ### BEGIN TOP ROW ###

        # will hold all of the top row frequency controls
        vbox_FreqControls = QtWidgets.QVBoxLayout()

        # add Top Row Frequency Label
        freqLabel = QtWidgets.QLabel("Choose First Frequency:")
        vbox_FreqControls.addWidget(freqLabel)

        # add Top Row Frequency knobs
        hbox_FreqKnobs = QtWidgets.QHBoxLayout()
        radioFreq = QtWidgets.QDial()
        radioFreq.setNotchesVisible(True)
        radioFreq.setRange(0, 1000)
        radioFreq.setNotchTarget(20)
        radioFreq.valueChanged.connect(lambda: self.changeFrequency1())
        self.radioFreq = radioFreq

        # top row frequency label (updated as change dials)
        currentFreq = QtWidgets.QLabel("0 Hz")
        self.currentFreq = currentFreq
        hbox_FreqKnobs.addWidget(radioFreq)
        hbox_FreqKnobs.addWidget(currentFreq)
        vbox_FreqControls.addLayout(hbox_FreqKnobs)

        # top row fine tune box and label
        vbox_fineTune1 = QtWidgets.QVBoxLayout()
        fineTuneLabel1 = QtWidgets.QLabel("Fine Tune:")
        vbox_fineTune1.addWidget(fineTuneLabel1)

        # top row fine tune dial
        fineTuneRadio = QtWidgets.QDial()
        fineTuneRadio.setNotchesVisible(True)
        fineTuneRadio.setRange(0, 40)
        fineTuneRadio.setNotchTarget(1)
        fineTuneRadio.setValue(20)
        fineTuneRadio.valueChanged.connect(lambda: self.changeFrequency1())
        self.fineTuneRadio = fineTuneRadio
        vbox_fineTune1.addWidget(self.fineTuneRadio)

        hbox_FreqKnobs.addLayout(vbox_fineTune1)

        # add top row amplitude Label
        ampLabel = QtWidgets.QLabel("Choose First Amplitude:")
        vbox_FreqControls.addWidget(ampLabel)

        # top row amplitude slider
        hbox_AmpChooser = QtWidgets.QHBoxLayout()
        self.ampSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ampSlider.setRange(0,100)
        self.ampSlider.setValue(100)
        self.currentAmp = QtWidgets.QLabel("1 Db")
        self.ampSlider.valueChanged.connect(lambda: self.changeAmplitude1())
        hbox_AmpChooser.addWidget(self.ampSlider)
        hbox_AmpChooser.addWidget(self.currentAmp)
        vbox_FreqControls.addLayout(hbox_AmpChooser)

        # create top row start and stop button
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

        # add in the top row main graph
        vbox_graph1 = QtWidgets.QVBoxLayout()
        self.main_figure = MplFigure(self)
        # currently not showing the graph's toolbar due to space constraints
        #vbox_graph1.addWidget(self.main_figure.toolbar)
        vbox_graph1.addWidget(self.main_figure.canvas)

        # bring whole top row together
        hbox_TopRow.addLayout(vbox_FreqControls)
        hbox_TopRow.addLayout(vbox_graph1)

        ### END TOP ROW UI ###


        ### BEGIN MIDDLE ROW UI ###
        # will hold all of the middle row frequency controls
        vbox_FreqControls1 = QtWidgets.QVBoxLayout()

        # add middle row Frequency Label
        freqLabel1 = QtWidgets.QLabel("Choose Second Frequency:")
        vbox_FreqControls1.addWidget(freqLabel1)

        # add middle row Frequency knobs
        hbox_FreqKnobs1 = QtWidgets.QHBoxLayout()
        radioFreq1 = QtWidgets.QDial()
        radioFreq1.setNotchesVisible(True)
        radioFreq1.setRange(0, 1000)
        radioFreq1.setNotchTarget(20)
        radioFreq1.valueChanged.connect(lambda: self.changeFrequency2())
        self.radioFreq1 = radioFreq1

        # middle row freqnecy label (will dynamically change)
        currentFreq1 = QtWidgets.QLabel("0 Hz")
        self.currentFreq1 = currentFreq1
        hbox_FreqKnobs1.addWidget(radioFreq1)
        hbox_FreqKnobs1.addWidget(currentFreq1)
        vbox_FreqControls1.addLayout(hbox_FreqKnobs1)

        # add middle row fine tuner label
        vbox_fineTune2 = QtWidgets.QVBoxLayout()
        fineTuneLabel2 = QtWidgets.QLabel("Fine Tune:")
        vbox_fineTune2.addWidget(fineTuneLabel2)

        # middle row fine tuner dial
        fineTuneRadio1 = QtWidgets.QDial()
        fineTuneRadio1.setNotchesVisible(True)
        fineTuneRadio1.setRange(0, 40)
        fineTuneRadio1.setNotchTarget(1)
        fineTuneRadio1.setValue(20)
        fineTuneRadio1.valueChanged.connect(lambda: self.changeFrequency2())
        self.fineTuneRadio1 = fineTuneRadio1
        vbox_fineTune2.addWidget(self.fineTuneRadio1)

        hbox_FreqKnobs1.addLayout(vbox_fineTune2)

        # add middle row amplitude Label
        ampLabel1 = QtWidgets.QLabel("Choose Second Amplitude:")
        vbox_FreqControls1.addWidget(ampLabel1)

        # middle row amplitude slider
        hbox_AmpChooser1 = QtWidgets.QHBoxLayout()
        self.ampSlider1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ampSlider1.setRange(0, 100)
        self.ampSlider1.setValue(100)
        self.currentAmp1 = QtWidgets.QLabel("1 Db")
        self.ampSlider1.valueChanged.connect(lambda: self.changeAmplitude2())
        hbox_AmpChooser1.addWidget(self.ampSlider1)
        hbox_AmpChooser1.addWidget(self.currentAmp1)
        vbox_FreqControls1.addLayout(hbox_AmpChooser1)

        # create middle row start and stop button
        # hold together in a horizontal box
        hbox_startStop1 = QtWidgets.QHBoxLayout()
        startButton1 = QtWidgets.QPushButton("Play")
        stopButton1 = QtWidgets.QPushButton("Stop")
        startButton1.clicked.connect(lambda: self.startPlaying1())
        stopButton1.clicked.connect(lambda: self.stopPlaying1())
        hbox_startStop1.addWidget(startButton1)
        hbox_startStop1.addWidget(stopButton1)
        vbox_FreqControls1.addLayout(hbox_startStop1)

        # references to middle row buttons for later use
        self.startButton1 = startButton1
        self.stopButton1 = stopButton1

        # create horizontal box to hold whole middle in
        hbox_MiddleRow = QtWidgets.QHBoxLayout()

        # add in the middle graph
        vbox_graph2 = QtWidgets.QVBoxLayout()
        self.main_figure1 = MplFigure(self)
        # toolbar currently commented out
        #vbox_graph2.addWidget(self.main_figure1.toolbar)
        vbox_graph2.addWidget(self.main_figure1.canvas)
        hbox_MiddleRow.addLayout(vbox_FreqControls1)
        hbox_MiddleRow.addLayout(vbox_graph2)


        ### END MIDDLE ROW UI ###

        ### BEGIN LAST ROW/ OVERLAY SECTION UI ###

        hbox_lastRow = QtWidgets.QHBoxLayout()

        # This section previously had buttons to allow you to not
        # update the overlay unless you had clicked "show"
        # but due to a weird glitch and spacing
        # these button have been commented out for now
        '''
        hbox_showHideButtons = QtWidgets.QHBoxLayout()
        showOverlayButton = QtWidgets.QPushButton("Show Overlay")
        showOverlayButton.clicked.connect(lambda: self.showOverlay())
        hideOverlayButton = QtWidgets.QPushButton("Hide Overlay")
        hideOverlayButton.clicked.connect(lambda: self.hideOverlay())
        hbox_showHideButtons.addWidget(showOverlayButton)
        hbox_showHideButtons.addWidget(hideOverlayButton)

        hbox_lastRow.addLayout(hbox_showHideButtons)
        '''

        # create the overlay graph
        vbox_graph3 = QtWidgets.QVBoxLayout()
        self.main_figure2 = MplFigure(self)
        # toolbar is currently commented out
        #vbox_graph3.addWidget(self.main_figure2.toolbar)
        vbox_graph3.addWidget(self.main_figure2.canvas)

        hbox_lastRow.addLayout(vbox_graph3)


        # create a vertical box to hold all items in
        vbox = QtWidgets.QVBoxLayout()

        # add in the 3 rows to the final vertical holder
        vbox.addLayout(hbox_TopRow)
        vbox.addLayout(hbox_MiddleRow)
        vbox.addLayout(hbox_lastRow)

        self.setLayout(vbox)

        # set the size the window opens to
        self.setGeometry(300, 300, 1000, 1000)
        # set the title
        self.setWindowTitle('Oscillator')
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
        if((self.isPlaying1 == False) & (self.isPlaying2 == False)):
            self.timer.stop()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        else:
            self.generatePitch1()

    # starts the timer (timer connected to "play pitch")
    def start(self):
        self.timer.start()

    # connected to second start button
    def startPlaying1(self):
        self.isPlaying2 = True
        self.generatePitch1()
        self.start()

    # connected to second stop button
    def stopPlaying1(self):
        self.isPlaying2 = False
        self.stop()

    # currently unused, but before connected to button that would show/hide overlay
    def showOverlay(self):
        self.boolShowOverlay = True
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)
        # refreshes the plots (put only when click out of page..?)
        self.main_figure2.canvas.draw()

    # currently unused, but before connected to button that would show/hide overlay
    def hideOverlay(self):
        self.boolShowOverlay = False
        self.y2 = 0
        self.line_final.set_data(self.x, self.y2)
        # refreshes the plots
        self.main_figure2.canvas.draw()

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
            volume1 = self.currentAmplitude1
            equation1 = volume1*(np.sin(2 * np.pi * np.arange(fs * duration) * f1 / fs))

        # equation generated from middle row
        equation2 = (np.sin(2 * np.pi * np.arange(fs * duration) * 0 / fs))
        # only generate if user has pressed play
        if(self.isPlaying2):
            f2 = self.currentFrequency2
            volume2 = self.currentAmplitude2
            equation2 = volume2 * (np.sin(2 * np.pi * np.arange(fs * duration) * f2 / fs))
        # generate samples
        self.samples = (equation1 + equation2).astype(np.float32).tobytes()

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
        self.f = self.radioFreq.value() + ((self.fineTuneRadio.value()) - 20)
        if(self.f < 0): self.f = 0
        self.currentFrequency1 = self.f
        self.currentFreq.setText(str(self.f) + " Hz")
        self.currentFreq.update()
        self.y = self.amplitude*np.sin(2 * np.pi * self.f * self.x / self.Fs)
        self.line_top.set_data(self.x, self.y)

        #update overlay
        #if(self.boolShowOverlay): # was used back when had show/hide button
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)

        # refreshes the plots
        self.main_figure2.canvas.draw()

        # regenerates pitch if currently playing
        if(self.isPlaying1):
            self.generatePitch1()

        # refreshes the plots
        self.main_figure.canvas.draw()

    # connected to top amplitude slider
    # updates amplitude label, pitch, and graph
    def changeAmplitude1(self):
        self.amplitude = self.ampSlider.value()/100
        self.currentAmplitude1 = self.amplitude
        self.currentAmp.setText(str(self.amplitude) + " Db")
        self.currentAmp.update()
        self.y = self.amplitude * np.sin(2 * np.pi * self.f * self.x / self.Fs)
        self.line_top.set_data(self.x, self.y)

        # change overlay
        #if (self.boolShowOverlay):
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)
        self.main_figure2.canvas.draw()

        # updates pitch if playing
        if(self.isPlaying1):
            self.generatePitch1()

        # refreshes the plots
        self.main_figure.canvas.draw()

    # connected to middle frequency dials
    # updates label, pitch, and graph
    def changeFrequency2(self):
        self.f1 =self.radioFreq1.value() + (self.fineTuneRadio1.value() - 20)
        if (self.f1 < 0): self.f1 = 0
        self.currentFrequency2 = self.f1
        self.currentFreq1.setText(str(self.f1) + " Hz")
        self.currentFreq1.update()
        self.y1 = self.amplitude1*np.sin(2 * np.pi * self.f1 * self.x / self.Fs)
        self.line_bottom.set_data(self.x, self.y1)

        # change overlay graph
        #if (self.boolShowOverlay):
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)
        self.main_figure2.canvas.draw()

        # updates pitch if playing
        if (self.isPlaying2):
            self.generatePitch1()

        # refreshes the plots
        self.main_figure1.canvas.draw()

    # connected to middle amplitude slider
    # updates label, pitch, and graph
    def changeAmplitude2(self):
        self.amplitude1 = self.ampSlider1.value()/100
        self.currentAmplitude2 = self.amplitude1
        self.currentAmp1.setText(str(self.amplitude1) + " Db")
        self.currentAmp1.update()
        self.y1 = self.amplitude1 * np.sin(2 * np.pi * self.f1 * self.x / self.Fs)
        self.line_bottom.set_data(self.x, self.y1)

        # change overlay
        #if (self.boolShowOverlay):
        self.y2 = self.y + self.y1
        self.line_final.set_data(self.x, self.y2)
        self.main_figure2.canvas.draw()

        # changes pitch if playing
        if (self.isPlaying2):
            self.generatePitch1()

        # refreshes the plots
        self.main_figure1.canvas.draw()

    # initializes our three graphs (labeled a, b, c)
    def initMplWidget(self):
        # TOP PLOT
        # create the plot to represent the sound wave
        self.ax_top = self.main_figure.figure.add_subplot(111) #changing to 211 makes smaller

        self.ax_top.set_ylim(-1, 1)
        self.ax_top.set_xlim(0,1000)
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6)

        self.f = 0 # frequency
        self.Fs = 44100 # sampluing rate
        sample = 44100
        # generate sine wave
        self.x = np.arange(sample)
        self.amplitude = 1
        self.y = self.amplitude*np.sin(2 * np.pi * self.f * self.x / self.Fs)

        # plot graph
        self.line_top, = self.ax_top.plot(self.x, self.y)


        # MIDDLE PLOT
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

        self.line_bottom, = self.bx_top.plot(self.x, self.y1, 'r')

        # OVERLAY PLOT
        self.cx_top = self.main_figure2.figure.add_subplot(111)  # changing to 111 makes bigger

        self.cx_top.set_ylim(-2, 2) # greater range since max combined amp = 2
        self.cx_top.set_xlim(0, 1000)
        self.cx_top.set_xlabel(u'time (ms)', fontsize=6)
        self.cx_top.set_title("Overlay")

        self.f2 = 0
        self.Fs = 44100
        sample = 44100
        self.x2 = np.arange(sample)
        self.amplitude2 = 1
        self.y2 = self.amplitude2 * np.sin(2 * np.pi * self.f2 * self.x2 / self.Fs)

        self.line_final, = self.cx_top.plot(self.x2, self.y2, 'm')

# run the program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Oscillator()
    sys.exit(app.exec_())

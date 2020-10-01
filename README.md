# Sound-Visualization and Oscillator
This project was created under a NSF-STEM grant as a pair to a curriculum to enable rural students to better understand and visualize sound waves.

The sound visualizer will visually representing sine waves being read in real time from the user's selected audio input. The user can stop the recording at any moment and then go back through the graph to further analyze the sound wave.

The oscillator allows the user to manipulate the properties of a sine wave and visually and auditorally see the outcomes. Additionally, they can visualize and hear how two different sound waves interact with eachother by manipulating the second sine wave and observing and hearing the overlay effect.

Both programs were written and run in pure Python.

## Video Examples
### Oscillator Video
Here you can observe the manipulating of the sine waves and the subsequent effect within the graphs. Additionally, you see the user press play to listen to the sound the wave would create.

### Sound Visualizer Video
Here you can observe the user choosing their built-in mic as their input, then making noises and observing the resulting sine waves, and subsequently stopping the audio to further analyze the resulting sine wave.

## Code Updates
pyqt_sound.py is fully functional, graphing based on the audio input chosen by the user.

oscillator.py is a fully functional oscillator where the user can generate two sine wave and hear and see them overlaid on top of each other.

The files denoted "practice," will remain in the repo while research is being done, but currently do not serve a purpose outside of idea generation.

## Getting Started

These instructions will help you install the dependencies necessary to run this program.

### For Mac

#### Installing Python
**Important Note:** The latest version of Python is 3.7, but you must download 3.6 or below in order for PyAudio to work
Go to [python downloads](https://www.python.org/downloads/) and choose the option to download Python 3.6 and run the installer.

#### Installing pip3
Securely download pip3 from this [link](https://pip.pypa.io/en/stable/installing/).

In the terminal, navigate to the place where you have download the file:
```
cd <file path to where you downloaded file>
```
an example filepath would be /Users/Jim/Downloads

Once in the proper folder, run the following commands:
```
python3 get-pip.py
which pip3
```

#### Installing PyQt5

Run the following commands in terminal:

```
pip3 install PyQt5
```

#### Installing matplotlib

Run the following commands in terminal:

```
pip3 install matplotlib
```

#### Installing PyAudio

Run the following commands in terminal:

```
curl https://bootstrap.pypa.io/get-pip.py | sudo python3
```
```
pip3 install PyAudio
```

### For Windows

#### Installing Python
**Important Note:** The latest version of Python is 3.7, but you must download 3.6 or below in order for PyAudio to work
Go to [python downloads](https://www.python.org/downloads/) and choose the option to download Python 3.6 and run the installer.

#### Installing PyQt5
Run the following commands in terminal:

```
py -m pip install PyQt5
```

#### Installing matplotlib

Run the following commands in terminal:

```
py -m pip install matplotlib
```

#### Installing PyAudio

Run the following commands in terminal:

```
curl https://bootstrap.pypa.io/get-pip.py | py
```
```
py -m pip install PyAudio
```

**If you are getting an error about C++ Visualizer, complete the following steps:**
1. Install Visual Studio [here](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15)
2. When installing, select: workload-> Visual C++ build tools; AND install options: select only the “Windows 10 SDK” (assuming the computer is Windows 10)

## Running pyqt_sound.py

### On Mac
Go to terminal and navigate to where you have downloaded pyqt_sound.py
```
cd <file path to where you downloaded file>
```
an example filepath would be /Users/Jim/Downloads

Once there, run the following command to run the program:
```
python3 pyqt_sound.py
```

### On Windows
Go to terminal and navigate to where you have downloaded pyqt_sound.py
```
cd <file path to where you downloaded file>
```
an example filepath would be /Users/Jim/Downloads

Once there, run the following command to run the program:
```
py pyqt_sound.py
```
## Running oscillator.py

### On Mac
Go to terminal and navigate to where you have downloaded pyqt_sound.py
```
cd <file path to where you downloaded file>
```
an example filepath would be /Users/Jim/Downloads

Once there, run the following command to run the program:
```
python3 oscillator.py
```

### On Windows
Go to terminal and navigate to where you have downloaded pyqt_sound.py
```
cd <file path to where you downloaded file>
```
an example filepath would be /Users/Jim/Downloads

Once there, run the following command to run the program:
```
py oscillator.py
```

## Using PyInstaller to Package Files
Start by installing pyinstaller using pip on your machine, then run the following command to create the packaged file:

```
pyinstaller --onefile --windowed <scriptname.py>
```

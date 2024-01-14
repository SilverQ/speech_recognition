# import tkinter as tk
# from tkinter import ttk
# from speech_recorder import *
#
#
# def on_source_selected():
#     selected_source = source_var.get()
#     window.destroy()
#     recognize_and_save_speech(selected_source)
#
#
# def create_ui():
#     global window, source_var
#
#     window = tk.Tk()
#     window.title("Speech Recognition App")
#
#     label = tk.Label(window, text="Select Speech Source:")
#     label.pack(pady=10)
#
#     source_var = tk.StringVar(value="microphone")
#
#     microphone_radio = ttk.Radiobutton(window, text="Microphone", variable=source_var, value="microphone")
#     microphone_radio.pack()
#
#     movie_clip_radio = ttk.Radiobutton(window, text="Movie Clip", variable=source_var, value="movie_clip")
#     movie_clip_radio.pack()
#
#     start_button = tk.Button(window, text="Start", command=on_source_selected)
#     start_button.pack(pady=20)
#
#     window.mainloop()
#
#
# if __name__ == "__main__":
#     create_ui()
#
import sys
import speech_recognition as sr
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QImage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.ndimage import gaussian_filter1d


class MicrophoneStream:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

    def read(self):
        return np.frombuffer(self.stream.read(1024), dtype=np.int16)


class MicrophoneCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-32768, 32767)
        self.ax.set_xlim(0, 1024)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(None)

    def update_plot(self, audio_data):
        self.line.set_ydata(audio_data)
        self.draw()

class TextCanvas(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_label = QLabel('Recognized Text Will Appear Here')
        layout.addWidget(self.text_label)

        self.setLayout(layout)

    def update_text(self, text):
        self.text_label.setText(f'Recognized: {text}')

class SpeechRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.recognizer = sr.Recognizer()

        self.microphone_stream = MicrophoneStream()

        self.init_ui()

        self.timer_id = self.startTimer(50)  # Timer interval in milliseconds

    def init_ui(self):
        self.setWindowTitle('Speech Recognition App')
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

        self.microphone_canvas = MicrophoneCanvas()
        layout.addWidget(self.microphone_canvas)

        self.text_canvas = TextCanvas()
        layout.addWidget(self.text_canvas)

        self.setLayout(layout)

    def timerEvent(self, event):
        audio_data = self.microphone_stream.read()
        self.microphone_canvas.update_plot(audio_data)

        try:
            audio = self.recognizer.listen(sr.AudioData(audio_data, 44100, 2))
            text = self.recognizer.recognize_google(audio, language='en-US')
            self.text_canvas.update_text(text)
        except sr.UnknownValueError:
            pass  # Ignore if no speech is detected

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = SpeechRecognitionApp()
    main_win.show()
    sys.exit(app.exec_())

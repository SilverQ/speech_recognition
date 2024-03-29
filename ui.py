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
import time

import speech_recognition as sr
from datetime import datetime
import pyaudio
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex, QCoreApplication
from PyQt5.QtGui import QPixmap, QImage, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt

# https://www.youtube.com/watch?v=U_vWfzhWINw&list=PLOJ3MJq530fhU8m9pBq7ysQk4KtkdOQZC
# https://devskim.tistory.com/60
# . Vosk, whisper를 사용해 인식
# 환경 구성
# 모델 다운로드
# https://alphacephei.com/vosk/models
# https://alphacephei.com/vosk/models/vosk-model-small-ko-0.22.zip
# 모델 파일 다운로드 이후에, 프로젝트 폴더 하위에 model 폴더 생성 후 압축해제한다.

# 고민 포인트
# 1. 스피커를 통해서 나오는 낮은 음량의 음성 인식 불가 해결
# 2. 음성 인식 정확도 개선을 위해, 재생속도를 느리게 해서 문장 이어붙이기 가능성
# 3. 여러 API에 인식을 요청하고, 가장 좋은 문장을 선택하는 방안(next sentence pred?)
# 4. 단어 중간에 잘리지 않도록 duration 설정하기
# https://wdprogrammer.tistory.com/38
# 5. 인터넷 연결을 필요로 하지 않는 sphinx를 제외하고 나머지 6개의 메서드는 인터넷 연결이 필요
#

class MicrophoneStream:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.dev_cnt = self.pa.get_device_count()
        print('장치 수: ', self.dev_cnt)
        for index in range(self.dev_cnt):
            desc = self.pa.get_device_info_by_index(index)
            print("DEVICE: {device}, INDEX: {index}, RATE: {rate} ".format(
                device=desc["name"], index=index, rate=int(desc["defaultSampleRate"])))

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

        self.text_out = QLabel('Waiting')
        layout.addWidget(self.text_out)

        self.setLayout(layout)

    def update_text(self, text):
        self.text_label.setText(f'Recognized: {text}')


class SpeechRecognitionThread(QThread):
    recognition_complete = pyqtSignal(str)
    # recognizer = sr.Recognizer()

    def __init__(self, recognizer, microphone):
        super().__init__()
        self.mutex = QMutex()
        self.recognizer = recognizer
        self.microphone = microphone

    def reg_lang(self, audio, lang):
        try:
            # tmp = self.recognizer.recognize_sphinx(audio)
            tmp = self.recognizer.recognize_google(audio, language=lang)
        except Exception as e:
            print(e)
            tmp = ''
        return tmp

    def run(self):
        print(1)
        with self.microphone as source:
            while True:
                try:
                    print(2)
                    audio = self.recognizer.listen(source,
                                                   timeout=10,
                                                   phrase_time_limit=10)
                    # language = "ko-KR"
                    # text = self.recognizer.recognize_google(audio, language=language)
                    text_kor = self.reg_lang(audio, 'ko-kr')
                    text_eng = self.reg_lang(audio, 'eng')
                    print('인식 중입니다.')
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    self.mutex.lock()
                    if len(text_kor) > 0:
                        print(f"[{current_time}] {text_kor}")
                        # self.recognition_complete.emit(f"[{current_time}] {text_kor}")
                        # self.recognition_complete.emit(f"[{current_time}] {text}")
                    if len(text_eng) > 0:
                        print(f"[{current_time}] {text_eng}")
                        self.recognition_complete.emit(f"[{current_time}] {text_eng}")
                    self.mutex.unlock()
                except sr.UnknownValueError:
                    print("음성을 감지하지 못했습니다.")
                except sr.RequestError as e:
                    print(f"음성 서비스에 접근할 수 없습니다; {e}")
                except KeyboardInterrupt:
                    print("앱이 종료되었습니다.")
                    break
                except Exception as e:
                    print(e)
                    pass
                # time.sleep(5)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.init_ui()
        self.init_microphone()
        # print('__init__ complete')

        # self.timer_id = self.startTimer(50)  # Timer interval in milliseconds

    def init_ui(self):
        self.setGeometry(100, 100, 1000, 700)  # x, y, w, height
        self.setWindowTitle('Kipro 음성인식')

        # 메뉴바
        menubar = self.menuBar()
        # menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('File')
        filemenu.addAction('New')
        # filemenu.addAction('Quit')

        # 툴바
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)
        # layout = QVBoxLayout(central_widget)
        exitAction = QAction(QIcon('icons/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        RecAction = QAction(QIcon('icons/rec.png'), 'Exit', self)
        RecAction.setShortcut('Ctrl+R')
        RecAction.setStatusTip('Start Record')
        RecAction.triggered.connect(self.start_recognition)

        # filemenu.addAction(RecAction)
        # filemenu.addAction(exitAction)

        toolbar.addAction(RecAction)
        toolbar.addAction(exitAction)

        self.statusBar()

        vbox_layout = QVBoxLayout()  # main
        hbox_layout = QHBoxLayout()  # 음원 선택, 녹음
        vbox_layout1 = QVBoxLayout()  # 음원 선택

        source_label = QLabel('Select Speech Source:')
        vbox_layout1.addWidget(source_label)

        source_combo_box = QComboBox()
        source_combo_box.addItem('Microphone')
        source_combo_box.addItem('Aux Input')
        source_combo_box.addItem('Vedio File')
        source_combo_box.addItem('Streaming')
        vbox_layout1.addWidget(source_combo_box)

        rec_button = QPushButton('Rec Now', self)
        rec_button.clicked.connect(self.start_recognition)
        # open_clip_widget = QPushButton('Open Clip')
        # date_widget = QDateTimeEdit()
        self.list_widget = QListWidget(self)
        # self.text_widget = QTextEdit(self)
        # self.microphone_canvas = MicrophoneCanvas()  # instance 생성
        # self.text_canvas = TextCanvas()

        # quit_btn = QPushButton('Quit', self)
        # quit_btn.clicked.connect(QCoreApplication.instance().quit)
        # layout.addStretch(1)
        # layout.addWidget(open_clip_widget)
        # layout.addWidget(date_widget)
        # layout.addStretch(1)
        # layout.addWidget(self.text_widget)
        # layout.addWidget(self.microphone_canvas)  # ui에 추가
        # layout.addWidget(self.text_canvas)
        # layout.addWidget(quit_btn)
        # layout.addStretch(1)

        # # QTimer to trigger recognition every 5 seconds
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.start_recognition)
        # self.timer.start(5000)  # Set the interval to 5000 milliseconds (5 seconds)

        main_widget = QWidget()
        main_widget.setLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout1)
        hbox_layout.addWidget(rec_button)

        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.list_widget)

        self.setCentralWidget(main_widget)
        self.setWindowIcon(QIcon('icons/rec.png'))
        self.statusBar().showMessage('Ready')

    def init_microphone(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        sr.energy_threshold = 50
        sr.pause_threshold = 1
        print('Recognizer 객체 생성.')
        try:
            self.calibrate_noise()  # 주변 소음 기준 설정
        except Exception as e:
            print(e)
        # print('__init_ui__ complete')

    def calibrate_noise(self):
        # 마이크 노이즈 기준 설정
        print("마이크 노이즈를 측정하고 있습니다. 조용한 상태에서 잠시 기다려주세요...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=4)
        except Exception as e:
            print(e)
            pass
        print("노이즈 측정이 완료되었습니다.")

    def start_recognition(self):
        self.recognition_thread = SpeechRecognitionThread(self.recognizer, self.microphone)
        self.recognition_thread.recognition_complete.connect(self.update_list_widget)
        self.recognition_thread.start()

    def update_list_widget(self, text):
        # self.mutex.lock()
        self.list_widget.addItem(text)
        self.list_widget.addItem('\n')
        # self.text_widget.toPlainText(text)
        # self.text_widget.insertPlainText(text)
        # self.text_widget.insertPlainText('\n')
        # self.mutex.unlock()

    def timerEvent(self, event):
        audio_data = self.microphone_stream.read()
        self.microphone_canvas.update_plot(audio_data)

        try:
            audio = self.recognizer.listen(sr.AudioData(audio_data, 44100, 2))
            text = self.recognizer.recognize_google(audio, language='en-US')
            self.text_canvas.update_text(text)
        except sr.UnknownValueError:
            pass  # Ignore if no speech is detected

    # def recognize_speech(self):
    #     recognizer = sr.Recognizer()
    #
    #     with sr.Microphone() as source:
    #     # with sr.AudioFile("IPC_CE/WG50_231120_1.mp4") as source:
    #     #     calibrate_noise(recognizer, source)  # 주변 소음 기준 설정
    #     #     print("앱이 음성을 실시간으로 인식 중입니다. 종료하려면 Ctrl+C를 누르세요.")
    #
    #         while True:
    #             try:
    #                 audio = recognizer.listen(source, timeout=5)  # 대기 시간을 늘리거나 timeout=None으로 변경
    #                 sr.energy_threshold = 100
    #                 sr.pause_threshold = 1
    # #                 print("음성 감지 완료")
    # #                 text = recognizer.recognize_sphinx(audio)
    # #                 language = "eng"
    #                 language = "ko-KR"
    #                 text = recognizer.recognize_google(audio, language=language)
    # #                 print(f"음성 인식 결과: {text}")
    #                 current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                 print(f"[{current_time}] {text}")
    #                 self.list_widget.addItem(f"[{current_time}] {text}")
    #
    #                 # save_to_file(f"[{current_time}] {text}")
    #
    #             except sr.UnknownValueError:
    #                 print("음성을 감지하지 못했습니다.")
    #             except sr.RequestError as e:
    #                 print(f"음성 서비스에 접근할 수 없습니다; {e}")
    #             except KeyboardInterrupt:
    #                 print("앱이 종료되었습니다.")
    #                 break
    #             except Exception as e:
    #                 # print(f"오류 발생: {e}")
    #                 pass


if __name__ == '__main__':
    app = QApplication(sys.argv)  # create pyqt app
    main = Main()  # create the instance of Window
    main.show()
    # sys.exit(app.exec_())  # start the app
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('closing Window...')


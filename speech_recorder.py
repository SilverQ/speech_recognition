import speech_recognition as sr
from datetime import datetime

# pip install SpeechRecognition


def calibrate_noise(recognizer, source):
    # 마이크 노이즈 기준 설정
    print("마이크 노이즈를 측정하고 있습니다. 조용한 상태에서 잠시 기다려주세요...")
    recognizer.adjust_for_ambient_noise(source, duration=5)
    print("노이즈 측정이 완료되었습니다.")


def recognize_and_save_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
    # with sr.AudioFile("IPC_CE/WG50_231120_1.mp4") as source:
        calibrate_noise(recognizer, source)  # 주변 소음 기준 설정
        print("앱이 음성을 실시간으로 인식 중입니다. 종료하려면 Ctrl+C를 누르세요.")

        while True:
            try:
                audio = recognizer.listen(source, timeout=5)  # 대기 시간을 늘리거나 timeout=None으로 변경
                sr.energy_threshold = 300
                sr.pause_threshold = 1
#                 print("음성 감지 완료")
#                 text = recognizer.recognize_sphinx(audio)
                language = "eng"
#                 language = "ko-KR"
                text = recognizer.recognize_google(audio, language=language)
#                 print(f"음성 인식 결과: {text}")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] {text}")
                save_to_file(f"[{current_time}] {text}")

            except sr.UnknownValueError:
                print("음성을 감지하지 못했습니다.")
            except sr.RequestError as e:
                print(f"음성 서비스에 접근할 수 없습니다; {e}")
            except KeyboardInterrupt:
                print("앱이 종료되었습니다.")
                break
            except Exception as e:
                # print(f"오류 발생: {e}")
                pass


def save_to_file(text):
    try:
        with open("speech_log.txt", "a") as file:
            file.write(text + "\n")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")


if __name__ == "__main__":
    recognize_and_save_speech()


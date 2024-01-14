import os
# import ffmpeg
# import subprocess
from pydub import AudioSegment

# - 실행전 아래 pip명령으로 관련된 모듈을 설치해 주시기 바랍니다.
# pip install pydubpip install ffmpeg-downloaderffdl install --add-path
# 출처: https://pagichacha.tistory.com/141 [파기차차:티스토리]
# command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(item, os.path.join(this_path, save_file_id))

# list = os.walk('IPC_CE')
# print(list)
# subprocess.call(command, shell=True)

# stream = ffmpeg.input('IPC_CE/WG50_231120_1.mp4')
# stream = ffmpeg.hflip(stream)
# stream = ffmpeg.output(stream, 'output.mp4')
# ffmpeg.run(stream)

mp4_file = 'IPC_CE/WG50_231120_1.mp4'
if os.mp4_file.is
wav_file = 'IPC_CE/WG50_231120_1.wav'

track = AudioSegment.from_file(mp4_file, format='mp4')
print(track)
file_handle = track.export(wav_file, format='wav')
print(file_handle)

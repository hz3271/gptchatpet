
import math
import time
import call_live2d
print("start!")
#import ChatWaifuServer
import winsound
import soundfile as sf
from vits_F.use import text_to_speech
use_live2d=True

class TTSHandler:
    def __init__(self):
        self.use_live2d = True
    def call_send_message(self,text):
        self.live2d.call_send_message(text)
    def use_or(self, use):
        self.use_live2d = use
        if self.use_live2d:
            self.live2d = call_live2d.Simple()

    def tts(self, text, trans, model_path, config_path):
        print("************开始生成*************")
        model_path = model_path
        config_path = config_path
        trans = trans
        text = text
        output_file = "output.wav"
        noise_scale = 0.6
        noise_scale_w = 0.668
        length_scale = 1
        speaker_id = 10

    # generateSound("[ZH]"+input_text+"[ZH]", speaker_id, model_id)

        print("播放合成的声音：")


        text_to_speech(trans,model_path,config_path,output_file,noise_scale,noise_scale_w,length_scale,speaker_id)
        #ChatWaifuServer.generateSound(trans,speaker_id,model_path, config_path)
        print("*****************************")


    # 调整音高

        try:
            # Code that might raise an exception
            lower_volume_of_app('cloudmusic.exe')
            time1 = math.ceil(read_time(r'.\output.wav'))
            if use_live2d:
                self.live2d.call_send_message(text)
            winsound.PlaySound(r'.\output.wav', winsound.SND_FILENAME)

            time.sleep(time1)
            restore_volume_of_app('cloudmusic.exe')
        except Exception:  # Catch any type of exception
            print("-------未运行网易云------")
            print(Exception)
            if use_live2d:
                call_live2d.call_send_message(text)
            winsound.PlaySound(r'.\output.wav', winsound.SND_FILENAME)


def read_time(fname):
    data, samplerate = sf.read(fname)
    duration = len(data) / samplerate
    print(duration)
    return duration

from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

def lower_volume_of_app(app_name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == app_name:
            print(f'Current volume of {app_name}:', volume.GetMasterVolume())
            volume.SetMasterVolume(0.03, None)  # 将音量调低到%

def restore_volume_of_app(app_name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == app_name:
            volume.SetMasterVolume(0.4, None)  # 恢复音量到100%

def caw():    #打印当前正在放音乐的程序
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process is not None:  # 有可能音频会话没有关联的进程
            print(session.Process.name())


#lower_volume_of_app('cloudmusic.exe')
#tts("今日の杭州市","今日の杭州市の天気は曇りで、気温は32度になるようです！明日の天気予報によると、中雨が降る予定で、最高気温は29度、最低気温は24度です。ご主上様、ご注意くださいね〜",model_path = "model/mika/mika.pth",config_path = "model/mika/config.json")
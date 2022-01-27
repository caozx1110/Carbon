# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: Carbon.py
date: 2021/7/26
function: Voice assistant Carbon, python 3.6
"""

import webbrowser
import time
import ctypes
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from aip import AipSpeech
import pyaudio
from pydub import AudioSegment
import audioop
import wave
from HookThread import HookThread
from WeChat import WeChat
from CloudMusic import CloudMusic
from PersonalComputer import PersonalComputer
from WebBrowser import WebBrowser
from WhatDoYouMean import Means, Understand

# 百度语音识别license
APP_ID = '24605447'
API_KEY = 'o95uZvX8GeGA6IHTBHMcNKOf'
SECRET_KEY = 'zvwUAyalshmALkxdacMTfLW2MtUToy6F'

TEMP_WAV = './data/temp.wav'    # 临时wav文件地址
TEMP_MP3 = './data/temp.mp3'    # 临时mp3
CHUNK = 2048                    # 采样点缓存数量为2048
MUTE_THRESHOLD = 500            # 静音rms阈值
MUTE_TIME_THRESHOLD = 15        # 静音次数阈值, 以一个CHUNK为计量单位, 30大概3s

# Voice assistant Carbon
class Carbon:
    Order = []                                                  # 命令队列
    Client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)    # 百度AI用户
    Audio = pyaudio.PyAudio()                                   # 实例化一个PyAudio对象
    RecordBuff = []                                             # 录音存储区
    MuteTime = 0                                                # 静音时间长度
    InitAudioRMS = 0                                            # 录音初始音量，用于排除外界常在的噪音干扰
    UdrStnd = Understand()                                      # Understand what do you mean
    Chat = WeChat()                                             # Wechat
    Music = CloudMusic()                                        # cloud music
    PC = PersonalComputer()                                     # PC
    Web = WebBrowser()                                          # Web

    def __init__(self):
        # 训练集生成
        # f = open("./data/train.txt", 'x')
        # for n in self.AppList:
        #     f.write('打开' + n + '\n')
        # f.close()

        # 打开声卡，设置 采样深度为16位、声道数为1、采样率为16、输入、采样点缓存数量为2048
        self.Stream = self.Audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
        # 关闭声卡，等待打开
        self.Stream.stop_stream()

    # 听，读取缓存区，加入存储区
    def Listen(self):
        audio_data = self.Stream.read(CHUNK)  # 读出声卡缓冲区的音频数据
        self.RecordBuff.append(audio_data)  # 将读出的音频数据追加到record_buf列表
        rms = audioop.rms(audio_data, 2)
        print('rms: ', rms)
        if rms < MUTE_THRESHOLD + self.InitAudioRMS:
            self.MuteTime = self.MuteTime + 1
        else:
            self.MuteTime = 0
        print("MuteTime: ", self.MuteTime)
        print(time.asctime(time.localtime(time.time())))

        return rms

    # todo: 可以标定固定用户的声音频率范围
    def ListenUntilMute(self):
        # 更新初始rms
        self.InitAudioRMS = self.Listen()
        print(self.InitAudioRMS)
        # 小于静音次数阈值则认为在说话，Carbon听
        while self.MuteTime < MUTE_TIME_THRESHOLD:
            self.Listen()

        # 重置MuteTime
        self.MuteTime = 0

    # 将存储区的音频数据存储至本地临时文件
    def SaveAudio(self):
        # WAV
        wf = wave.open(TEMP_WAV, 'wb')  # 创建一个音频文件
        wf.setnchannels(1)  # 设置声道数为1
        wf.setsampwidth(2)  # 设置采样深度为16bit
        wf.setframerate(16000)  # 设置采样率为16000
        # 将数据写入创建的音频文件
        wf.writeframes("".encode().join(self.RecordBuff))
        # 写完后将文件关闭
        wf.close()
        # MP3
        self.RecordBuff.clear()
        TempAudio = AudioSegment.from_wav(TEMP_WAV)
        TempAudio.export(TEMP_MP3, format="mp3")

    # 识别temp.wav
    def Recognize(self):
        try:
            RecResult = self.Client.asr(self.get_file_content(TEMP_WAV), 'pcm', 16000, {'dev_pid': 1536, })
            NewOrder = RecResult['result'][0]
            print(NewOrder)
            self.Order.append(NewOrder)
            return NewOrder
        except ConnectionError:
            print("Recognition Error: ConnectionError")
        except KeyError:
            print("Recognition Error: KeyError")

    # 执行Order
    def Execute(self):
        MatchAppName = ''
        try:
            order = self.Order[0]
            Mean = self.UdrStnd.WhatDoYouMean(order)
            print(Mean)
            # UNKNOWN
            if Mean['Type'] == Means.UNKNOWN:
                print("Sorry, Master, I don't understand what you mean.")
            # PC
            elif Mean['Type'] == Means.PC_LOCK:
                time.sleep(Mean['SleepTime'])
                # 锁屏
                ctypes.windll.user32.LockWorkStation()
            elif Mean['Type'] == Means.PC_CLOSE:
                pass
            # APP
            elif Mean['Type'] == Means.APP_OPEN:
                self.PC.OpenApp(Mean['AppName'])
            # WEB
            elif Mean['Type'] == Means.WEB_BAIDU_SEARCH:
                self.Web.BaiduSearch(Mean['ToSearch'])
            elif Mean['Type'] == Means.WEB_IQIYI_SEARCH:
                self.Web.IqiyiSearch(Mean['ToSearch'])
            elif Mean['Type'] == Means.WEB_VQQ_SEARCH:
                self.Web.VqqSearch(Mean['ToSearch'])
            elif Mean['Type'] == Means.WEB_MUSIC_PLAY:
                self.Web.PlayMusic(Mean['MusicName'])
            # WECHAT
            elif Mean['Type'] == Means.WECHAT_SEND:
                self.Chat.SendMsg(Mean['Name'], Mean['Massage'])
            elif Mean['Type'] == Means.WECHAT_PYQ:
                # todo
                pass
            # MUSIC, cloud music
            elif Mean['Type'] == Means.MUSIC_START:
                self.Music.Start()
            elif Mean['Type'] == Means.MUSIC_STOP:
                self.Music.Stop()
            elif Mean['Type'] == Means.MUSIC_LAST:
                self.Music.Last()
            elif Mean['Type'] == Means.MUSIC_NEXT:
                self.Music.Next()
            elif Mean['Type'] == Means.MUSIC_VOLUME_UP:
                self.Music.VolumeUp()
            elif Mean['Type'] == Means.MUSIC_VOLUME_DOWN:
                self.Music.VolumeDown()
            elif Mean['Type'] == Means.MUSIC_LIKE:
                self.Music.Like()
            elif Mean['Type'] == Means.MUSIC_LYRIC:
                self.Music.Lyric()

            self.Order.pop(0)
            # if '打开' in order:
            #     pass
            #     Flag = 0
            #     for an in self.AppList:
            #         an_ratio = fuzz.partial_ratio(an, order.replace('打开', ''))
            #         if an_ratio > Flag:
            #             Flag = an_ratio
            #             MatchAppName = an
            #     if Flag > 50:
            #         self.PC.OpenApp(MatchAppName)
            #     self.Order.pop(0)
            #     # print(MatchAppName)
            #     # print(Flag)
            # elif '锁屏' in order:
            #     # kb = PyKeyboard()
            #     # # Win + L 锁屏
            #     # kb.press_key(kb.windows_l_key)
            #     # kb.tap_key('l')
            #     # kb.release_key(kb.windows_l_key)
            #     ReferTime = order[0: order.rfind('锁屏')]     # 指代时间的部分
            #     if ReferTime:
            #         if ReferTime[-1] == '后':
            #             if ReferTime[-2] == '秒':
            #                 # 转换为数字
            #                 time.sleep(cntn.ch2num(ReferTime[0: -2]))
            #             elif ReferTime[-3: -1] == '分钟':
            #                 # 转换为数字
            #                 time.sleep(cntn.ch2num(ReferTime[0: -3]) * 60)
            #     # 锁屏
            #     ctypes.windll.user32.LockWorkStation()
            #     # user = ctypes.windll.LoadLibrary('user32.dll')
            #     # user.LockWorkStation()
            #     self.Order.pop(0)
            # elif '百度搜索' in order:
            #     # 百度搜索后的内容，+4指针移到搜索后
            #     ToSearch = order[(order.rfind('百度搜索') + 4):]
            #     # print(order)
            #     # print(ToSearch)
            #     webbrowser.open(He.BAIDU_URL + ToSearch)
            #     self.Order.pop(0)
            # elif '发送' in order:
            #     # 姓名
            #     FindResult = re.findall('给(.*?)发送', order)
            #     # 给...发送...
            #     if FindResult:
            #         RecoName = FindResult[0]
            #     # 只有发送
            #     else:
            #         RecoName = order[0: (order.rfind('发送'))]
            #     Name = ''
            #     for i in range(len(self.FriendNameList)):
            #         # 比较两者拼音的相似度
            #         # print(''.join(ppy.lazy_pinyin(self.FriendNameList[i])))
            #         Similarity = self.PinYinSimilarity(
            #             ''.join(ppy.lazy_pinyin(self.FriendNameList[i])),
            #             ''.join(ppy.lazy_pinyin(RecoName)))
            #         # 若拼音相似度大于95%
            #         if Similarity > 0.9:
            #             Name = self.FriendNameList[i]
            #             print(Name)
            #             break
            #     # 消息
            #     Msg = order[(order.rfind('发送') + 2):]
            #     # 发送
            #     self.Chat.SendMsg(Name, Msg)
            #     self.Order.pop(0)
            # else:
            #     print("Sorry, Carbon don't understand what Master mean.")
            #     self.Order.pop(0)
        except IndexError:
            print("No Order In List")
        # except:
        #     print('Execute error')

    # 获取wav文件内容
    @staticmethod
    def get_file_content(FilePath):
        with open(FilePath, 'rb') as fp:
            return fp.read()

    # 关闭收听功能, __del__
    def __del__(self):
        # 停止声卡
        self.Stream.stop_stream()
        # 关闭声卡
        self.Stream.close()
        # 不能使用以下终止pyaudio, 因为唤醒也要使用
        # 终止pyaudio
        # self.Audio.terminate()


if __name__ == '__main__':
    pass
    HThread = HookThread()
    HThread.start()
    # Thr.join()

    c = Carbon()
    while True:
        # c.Recognize()
        # time.sleep(1)
        # 一套流程
        # 如果PrtSc按下开始录音
        if HThread.IsPrtScPushed:
            c.Stream.start_stream()
            while HThread.IsPrtScPushed:
                c.Listen()
            # 松开结束录音
            c.Stream.stop_stream()
            c.SaveAudio()
            c.Recognize()
            c.Execute()

    # 测试
    # c = Carbon()
    # c.Order.append('给徐兴宏发送你好')
    # c.Execute()

    # c.Listen()
    # c.Execute()
    # f = open('data/FriendNameRepair.txt')
    # start = time.time()
    # Temp = AudioSegment.from_wav(TEMP_WAV)
    # Temp.export(TEMP_MP3, format="mp3")
    # end = time.time()
    # print('use', end - start, 's')



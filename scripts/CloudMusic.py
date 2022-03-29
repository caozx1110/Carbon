# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: CloudMusic.py
date: 2021/8/3
function: 网易云音乐相关操作
"""
import time
from Focus import Focus
from pykeyboard import PyKeyboard
from PersonalComputer import PersonalComputer

#       MUSIC
#       MUSIC_START         = 40
#       MUSIC_STOP          = 41
#       MUSIC_LAST          = 42
#       MUSIC_NEXT          = 43
#       MUSIC_VOLUME_UP     = 44
#       MUSIC_VOLUME_DOWN   = 45
#       MUSIC_LIKE          = 46
#       MUSIC_LYRIC         = 47

class CloudMusic:
    IsAppOpen = False
    # IsStart = False
    IsLyric = False
    CM = Focus("cloudmusic.exe")
    PC = PersonalComputer()
    KB = PyKeyboard()

    def __init__(self):
        pass

    def GetIsAppOpen(self):
        # 如果有对应的PID，则正在后台运行
        if self.CM.GetPidForPname(self.CM.ExeName):
            self.IsAppOpen = True
        else:
            self.IsAppOpen = False

        return self.IsAppOpen

    def Start(self):
        self.GetIsAppOpen()
        # APP打开
        if self.IsAppOpen:
            # 音乐未打开
            # if not self.IsStart:
            # Ctrl + Alt + P
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key('p')
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)
            # self.IsStart = True
        else:
            # open cloudmusic
            self.PC.OpenApp('网易云音乐')
            # 等待网易云打开，10s
            time.sleep(10)
            # Ctrl + P
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.tap_key('p')
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # self.IsStart = True

    def Stop(self):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            # if self.IsStart:
            # Ctrl + Alt + P
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key('p')
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)
            # self.IsStart = True
        else:
            pass

    def Last(self):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            # Ctrl + Alt + Left
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key(self.KB.left_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)

    def Next(self):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            # Ctrl + Alt + Right
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key(self.KB.right_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)

    def VolumeUp(self, Times=1):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            for i in range(Times):
                # Ctrl + Alt + Up
                self.KB.press_key(self.KB.control_key)
                # time.sleep(0.1)
                self.KB.press_key(self.KB.alt_key)
                # time.sleep(0.1)
                self.KB.tap_key(self.KB.up_key)
                # time.sleep(0.1)
                self.KB.release_key(self.KB.control_key)
                # time.sleep(0.1)
                self.KB.release_key(self.KB.alt_key)

    def VolumeDown(self, Times=1):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            for i in range(Times):
                # Ctrl + Alt + Down
                self.KB.press_key(self.KB.control_key)
                # time.sleep(0.1)
                self.KB.press_key(self.KB.alt_key)
                # time.sleep(0.1)
                self.KB.tap_key(self.KB.down_key)
                # time.sleep(0.1)
                self.KB.release_key(self.KB.control_key)
                # time.sleep(0.1)
                self.KB.release_key(self.KB.alt_key)

    def Like(self):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            # Ctrl + Alt + L
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key('l')
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)

    def Lyric(self):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            # Ctrl + Alt + D
            self.KB.press_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.press_key(self.KB.alt_key)
            # time.sleep(0.1)
            self.KB.tap_key('d')
            # time.sleep(0.1)
            self.KB.release_key(self.KB.control_key)
            # time.sleep(0.1)
            self.KB.release_key(self.KB.alt_key)


if __name__ == '__main__':
    cm = CloudMusic()
    cm.Last()
    cm.Next()
    cm.Start()
    cm.Like()
    cm.Lyric()
    cm.VolumeUp(4)
    cm.VolumeDown(2)
    time.sleep(3)
    cm.Stop()

    # 打开网易云音乐测试
    # sf = Focus("cloudmusic.exe")
    # if sf.GetPidForPname(sf.ExeName):
    #     # 如果在运行，可以直接使用全局快捷键
    #     OpenApp("网易云音乐")
    #     time.sleep(2)
    #     print('ctrl p')
    # else:
    #     # 如果没有在运行，则需要等待较长时间
    #     OpenApp("网易云音乐")
    #     time.sleep(10)
    #     print('ctrl p')

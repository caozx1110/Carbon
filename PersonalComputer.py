# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: PersonalComputer.py
date: 2021/8/8
function: PC操作
"""
import os
import ctypes
from pykeyboard import PyKeyboard

# App快捷方式目录
import time

APP_FOLDER = r'C:\Users\q7423\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\APP'

class PersonalComputer:
    AppList = []  # 应用快捷方式列表

    def __init__(self):
        # 读取APP目录
        self.AppList = os.listdir(APP_FOLDER)
        for i in range(len(self.AppList)):
            self.AppList[i] = self.AppList[i].split('.')[0]

    @staticmethod
    def OpenApp(AppName):
        try:
            os.startfile(os.path.join(APP_FOLDER, AppName))
            pass
        except FileNotFoundError:
            print("FileNotFoundError: Cannot open", AppName)

    @staticmethod
    def Lock():
        ctypes.windll.user32.LockWorkStation()

    @staticmethod
    def UnLock():
        # todo
        pass


if __name__ == '__main__':

    ctypes.windll.user32.LockWorkStation()
    time.sleep(5)
    print("ok")
    kb = PyKeyboard()
    kb.tap_key(kb.space_key)
    time.sleep(0.1)
    kb.tap_key(kb.space_key)
    time.sleep(5)
    kb.tap_key('2')
    kb.tap_key('3')
    kb.tap_key('5')
    kb.tap_key('8')
    kb.tap_key('1')
    kb.tap_key('3')
    print('ok')
    time.sleep(100)

# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: MainProgress.py
date: 2021/8/11
function: MainProgress of Carbon
"""
from WakeUp import WakeUp
from PyQt5.QtCore import QThread

# 语音唤醒模式
class WakeupThread(QThread):
    MainWakeUp: WakeUp

    def __init__(self, wu):
        super(WakeupThread, self).__init__()
        self.MainWakeUp = wu

    def run(self) -> None:
        self.MainWakeUp.ivw_wakeup()

# 其他方式直接执行
class DoThread(QThread):
    MainWakeUp: WakeUp

    def __init__(self, wu):
        super(DoThread, self).__init__()
        self.MainWakeUp = wu

    def run(self) -> None:
        self.MainWakeUp.Do()
        self

class MainProgress:
    MainWakeUp = WakeUp()
    WThread: WakeupThread
    DThread: DoThread

    def __init__(self):
        self.WThread = WakeupThread(self.MainWakeUp)
        self.DThread = DoThread(self.MainWakeUp)
        pass

    # 唤醒入口（带执行）
    def WakeUp(self):
        self.WThread.start()

    def Do(self):
        # 直接执行
        self.DThread.start()

# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: MyThread.py
date: 2021/7/28
function: multi thread
"""
import threading
import PyHook3
import pythoncom
import time

class HookThread(threading.Thread):
    IsPrtScPushed = False
    hm = PyHook3.HookManager()

    def __init__(self):
        super(HookThread, self).__init__()
        pass

    def run(self) -> None:
        self.hm.KeyDown = self.PushKeyboardEvent  # 将OnKeyboardEvent函数绑定到KeyDown事件上
        self.hm.KeyUp = self.ReleaseKeyboardEvent
        self.hm.HookKeyboard()
        pythoncom.PumpMessages()
        pass

    # 键盘事件处理函数，按下
    def PushKeyboardEvent(self, event):
        if event.Key == 'Snapshot':
            self.IsPrtScPushed = True
            # print(time.ctime(time.time()))

        # print('MessageName:', event.MessageName)          # 同上，共同属性不再赘述
        # print('Message:', event.Message)
        # print('Time:', event.Time)
        # print('Window:', event.Window)
        # print('WindowName:', event.WindowName)
        # print('Ascii:', event.Ascii, chr(event.Ascii))   # 按键的ASCII码
        # print('Key:', event.Key)                         # 按键的名称
        # print('KeyID:', event.KeyID)                     # 按键的虚拟键值
        # print('ScanCode:', event.ScanCode)               # 按键扫描码
        # print('Extended:', event.Extended)               # 判断是否为增强键盘的扩展键
        # print('Injected:', event.Injected)
        # print('Alt', event.Alt)                          # 是某同时按下Alt
        # print('Transition', event.Transition)            # 判断转换状态
        # print('---')

        # 返回True代表将事件继续传给其他句柄，为False则停止传递，即被拦截
        return True

    # 键盘事件处理函数，松开
    def ReleaseKeyboardEvent(self, event):
        self.IsPrtScPushed = False

        return True

# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: SetFocus.py
date: 2021/7/30
function: https://blog.csdn.net/qq_32126137/article/details/82217630
"""
# coding:utf-8
import time
import ctypes
import psutil
import win32com.client
import win32con
import win32gui
import win32process


class Focus:
    def __init__(self, exename='WeChat.exe'):
        self.ExeName = exename
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.dll = ctypes.windll.user32

    def SetFocus(self):
        pid = self.GetPidForPname(self.ExeName)
        if pid:
            for hwnd in self.GetHwndsForPid(pid):
                self.shell.SendKeys('%')
                self.dll.LockSetForegroundWindow(2)
                if self.dll.IsIconic(hwnd):
                    win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
                self.dll.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                self.dll.SetForegroundWindow(hwnd)
                self.dll.SetActiveWindow(hwnd)

    # get pid
    def GetPidForPname(self, processName):
        try:
            pids = psutil.pids()  # 获取主机所有的PID
            for pid in pids:  # 对所有PID进行循环
                p = psutil.Process(pid)  # 实例化进程对象
                # print(p.name())
                if p.name() == processName:  # 判断实例进程名与输入的进程名是否一致（判断进程是否存活）
                    return pid  # 返回
                    pass
        except:
            return 0

    def GetHwndsForPid(self, pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
                return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        # print(hwnds)

        return hwnds


if __name__ == '__main__':
    sf = Focus("cloudmusic.exe")

    # time.sleep(3)
    try:
        sf.SetFocus()
    except Exception as e:
        print(e)

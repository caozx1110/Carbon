# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: WeChat.py
date: 2021/7/30
function: 用pyuserinput模拟微信聊天
"""
import time
import pyperclip as clip
# todo: pynput instead of pyuserinput
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from Focus import Focus
from PersonalComputer import PersonalComputer

# 需要事先导出微信联系人，并且将联系人list交给baidu-aip训练

# 不具备可移植性
# 微信导出联系人，网页版不能用，第三方软件不敢用，用最笨的方法，pyuserinput模拟操作
# 微信 win + <-
def SaveFriendName():
    # 鼠标
    # (300, 162)->(300, 193)一屏联系人, 30
    # (78, 102) ->(82, 162) 跨越一个联系人, 60
    # (410, 243)备注的位置
    # 屏幕最下方863
    Mouse = PyMouse()
    Keyboard = PyKeyboard()
    f = open("data/FriendName.txt", 'w+')
    Sliding = [300, 165]
    InitMouse = [100, 100]
    NewMouse = InitMouse.copy()
    
    while Sliding[1] < 853:
        NewMouse[1] = InitMouse[1]
        while NewMouse[1] < 863:
            Mouse.click(NewMouse[0], NewMouse[1])
            time.sleep(0.1)
            Mouse.click(420, 245)   # 备注的位置
            time.sleep(0.1)
            Mouse.click(420, 245)
            time.sleep(0.1)
            Mouse.click(420, 245)
            time.sleep(0.1)
            # # Ctrl + A
            # Keyboard.press_key(Keyboard.control_key)
            # time.sleep(0.1)
            # Keyboard.tap_key('a')
            # time.sleep(0.1)
            # Keyboard.release_key(Keyboard.control_key)
            # Ctrl + C
            Keyboard.press_key(Keyboard.control_key)
            time.sleep(0.1)
            Keyboard.tap_key('c')
            time.sleep(0.1)
            Keyboard.release_key(Keyboard.control_key)
            time.sleep(0.1)
            # 粘贴到txt中
            f.write(clip.paste() + '\n')

            NewMouse[1] = NewMouse[1] + 60
        # 移动滑块
        Mouse.move(Sliding[0], Sliding[1])
        Sliding[1] = Sliding[1] + 30
        time.sleep(0.1)
        Mouse.drag(Sliding[0], Sliding[1])
        pass

    print(Mouse.position())

# 修复NameList
def RepairNameList():
    f = open("data/FriendName.txt")
    FriendNameList = f.read().splitlines()
    list2 = list(set(FriendNameList))
    nf = open("data/FriendNameRepair.txt", 'w+')
    for i in range(len(list2)):
        nf.write(list2[i] + '\n')
    print(len(list2))

class WeChat:
    PC = PersonalComputer()
    FriendNameList = []  # 微信朋友名字列表
    CM = Focus("WeChat.exe")
    IsAppOpen = False

    def __init__(self):
        # 读取朋友名称
        f = open("data/FriendNameRepair.txt")
        self.FriendNameList = f.read().splitlines()
        # print(self.FriendNameList)
        # for i in range(len(self.FriendNameList)):
        #     # 每个名字的拼音拼成一串
        #     # lazy_pinyin会得到类似['cong', 'ming', 'de', 'xiao', 'tu', 'zi']这样的结果
        #     # join拼接list
        #     self.FriendNameList[i] = ''.join(ppy.lazy_pinyin(self.FriendNameList[i]))
        f.close()

    def GetIsAppOpen(self):
        # 如果有对应的PID，则正在后台运行
        if self.CM.GetPidForPname(self.CM.ExeName):
            self.IsAppOpen = True
        else:
            self.IsAppOpen = False

        return self.IsAppOpen

    # 发送信息
    def SendMsg(self, Name, Msg):
        self.GetIsAppOpen()
        if self.IsAppOpen:
            self.PC.OpenApp('微信')
            # 将焦点置于微信上， 默认'WeChat.exe'
            WC = Focus('WeChat.exe')
            WC.SetFocus()
            KB = PyKeyboard()
            # Ctrl + F
            KB.press_key(KB.control_key)
            # time.sleep(0.1)
            KB.tap_key('f')
            # time.sleep(0.1)
            KB.release_key(KB.control_key)
            # time.sleep(0.1)
            # 复制姓名
            clip.copy(Name)
            # Ctrl + V
            KB.press_key(KB.control_key)
            # time.sleep(0.1)
            KB.tap_key('v')
            # time.sleep(0.1)
            KB.release_key(KB.control_key)
            time.sleep(0.6)     # 测试发现这里必须要0.6，等待微信响应搜索词，否则还没搜索到就将Msg粘贴在搜索框中了
            # enter
            KB.tap_key(KB.enter_key)
            # time.sleep(0.1)
            # 复制消息
            clip.copy(Msg)
            # Ctrl + V
            KB.press_key(KB.control_key)
            # time.sleep(0.1)
            KB.tap_key('v')
            # time.sleep(0.1)
            KB.release_key(KB.control_key)
            # time.sleep(0.1)
            # enter
            KB.tap_key(KB.enter_key)
            time.sleep(0.1)     # delay 0.1，防止连续发送时出现bug
        else:
            print("Sorry, Master, WeChat is not logging on.")


if __name__ == '__main__':
    # time.sleep(2)
    # SaveFriendName()
    # RepairNameList()
    wechat = WeChat()
    for i in range(10):
        wechat.SendMsg('向欣怡', '[敲打]')


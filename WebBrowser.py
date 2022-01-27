# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: WebBrowser.py
date: 2021/8/8
function: 浏览器
"""
import time
import webbrowser
from WebCloudMusic import WebCloudMusic
from pykeyboard import PyKeyboard
from Focus import Focus

# 百度搜索网址示例（%20表示空格）：https://www.baidu.com/s?wd=搜索%20测试
BAIDU_URL = 'https://www.baidu.com/s?wd='
# 爱奇艺
IQIYI_URL = 'https://so.iqiyi.com/so/q_'
# 腾讯视频
VQQ_URL = 'https://v.qq.com/x/search/?q='
# 网易云音乐，https://music.163.com/#/song?id=386844&autoplay=true
CLOUDMUSIC_URL= 'https://music.163.com/#/song?id='


class WebBrowser:
    WebMusic = WebCloudMusic()
    Kb = PyKeyboard()
    Web = Focus('msedge.exe')
    IsAppOpen = False

    def __init__(self):
        pass

    @staticmethod
    def BaiduSearch(ToSearch):
        webbrowser.open(BAIDU_URL + ToSearch)

    @staticmethod
    def IqiyiSearch(ToSearch):
        webbrowser.open(IQIYI_URL + ToSearch)

    @staticmethod
    def VqqSearch(ToSearch):
        webbrowser.open(VQQ_URL + ToSearch)

    def GetIsAppOpen(self):
        # 如果有对应的PID，则正在后台运行
        if self.Web.GetPidForPname(self.Web.ExeName):
            self.IsAppOpen = True
        else:
            self.IsAppOpen = False

        return self.IsAppOpen

    def PlayMusic(self, MusicName):
        # 获取浏览器是否在运行
        self.GetIsAppOpen()
        SearchResult = self.WebMusic.get_music_list(MusicName)
        FirstName = SearchResult[0]['name']
        print('Master,《', FirstName, '》will be played.')
        FirstId = SearchResult[0]['id']
        # 自动播放
        webbrowser.open(CLOUDMUSIC_URL + str(FirstId) + '&autoplay=true')
        # todo: 这可用来做播放列表
        # 不自动播放，按一次P会导致：若之前有一首歌，则会将新的歌加入播放列表
        # webbrowser.open(CLOUDMUSIC_URL + str(FirstId))
        # 发现这样打开的网页不会自动播放，按P解决
        # 设置焦点
        self.Web.SetFocus()
        if self.IsAppOpen:
            time.sleep(0.5)
        else:
            time.sleep(6)
        self.Kb.tap_key('p')
        self.Kb.tap_key('p')

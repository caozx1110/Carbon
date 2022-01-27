# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: WhatDoYouMean.py
date: 2021/8/3
function: Understand what do you mean
"""

from enum import Enum
import pypinyin as ppy
from fuzzywuzzy import fuzz
import difflib
import ChNumToNum as cntn
import re
from WeChat import WeChat
from PersonalComputer import PersonalComputer

# 枚举类，各种不同的意思
class Means(Enum):
    # UNKNOWN
    UNKNOWN = 0
    # PC
    PC_LOCK = 1
    PC_CLOSE = 2
    # APP
    APP_OPEN = 10
    # WEB
    WEB_BAIDU_SEARCH = 20
    WEB_IQIYI_SEARCH = 21
    WEB_VQQ_SEARCH = 22
    WEB_MUSIC_PLAY = 23
    # WECHAT
    WECHAT_SEND = 30
    WECHAT_PYQ = 31
    # MUSIC, cloud music
    MUSIC_START = 40
    MUSIC_STOP = 41
    MUSIC_LAST = 42
    MUSIC_NEXT = 43
    MUSIC_VOLUME_UP = 44
    MUSIC_VOLUME_DOWN = 45
    MUSIC_LIKE = 46
    MUSIC_LYRIC = 47
    # todo: Add more

# Understand what do you mean
class Understand:
    PC = PersonalComputer()
    Chat = WeChat()
    MeansWeight = {Means.UNKNOWN: 0}  # Means权重

    def __init__(self):
        pass

    # 在self.MeansWeight中给Mean(list)添加权重
    def AddWeight(self, MeanList, Weight=1):
        for mean in MeanList:
            # 已存在Mean
            if mean in self.MeansWeight:
                self.MeansWeight[mean] = self.MeansWeight[mean] + Weight
            # 未存在Mean
            else:
                self.MeansWeight[mean] = Weight

    @staticmethod
    def PinYinSimilarity(str1, str2):
        # 忽略g的发音
        return difflib.SequenceMatcher(lambda x: x in "g", str1, str2).quick_ratio()

    # todo: 这一部分应该可以用deep learning做
    # 返回一个字典，类似于{'Type': Means.WECHAT_SEND, 'Name': '妈妈', 'Msg': '测试'}
    def WhatDoYouMean(self, Order):
        # 最终的意思
        FinalMean = Means.UNKNOWN
        # Order中各意思的权重，字典，格式类似以下：
        # self.MeansWeight = {Means.UNKNOWN: 1, Means.MUSIC_LYRIC: 2}
        # 初始化MeansWeight
        self.MeansWeight = {Means.UNKNOWN: 0}
        # example
        # self.AddWeight([Means.UNKNOWN, Means.APP_OPEN])
        # print(self.MeansWeight)

        # 关键词分析
        # PC
        if '电脑' in Order:
            self.AddWeight([Means.PC_LOCK, Means.PC_CLOSE])
        # PC ++
        if '锁屏' in Order:
            self.AddWeight([Means.PC_LOCK], 2)
        if '关机' in Order:
            self.AddWeight([Means.PC_CLOSE], 2)

        # APP
        if '软件' in Order:
            self.AddWeight([Means.APP_OPEN])
        # APP ++
        if '打开' in Order or 'open' in Order:
            self.AddWeight([Means.APP_OPEN], 2)

        # WEB
        if '搜索' in Order:
            self.AddWeight([Means.WEB_BAIDU_SEARCH, Means.WEB_IQIYI_SEARCH, Means.WEB_VQQ_SEARCH])
        # WEB ++
        if '百度搜索' in Order:
            self.AddWeight([Means.WEB_BAIDU_SEARCH], 2)
        if '爱奇艺搜索' in Order:
            self.AddWeight([Means.WEB_IQIYI_SEARCH], 2)
        if '腾讯搜索' in Order or '腾讯视频搜索' in Order:
            self.AddWeight([Means.WEB_VQQ_SEARCH], 2)
        if Order[0: 2] == '播放' and len(Order) > 2:
            self.AddWeight([Means.WEB_MUSIC_PLAY], 2)

        # WECHAT
        if '微信' in Order:
            self.AddWeight([Means.WECHAT_SEND, Means.WECHAT_PYQ])
        # WECHAT ++
        if '发送' in Order:
            self.AddWeight([Means.WECHAT_SEND], 5)

        # MUSIC
        if '音乐' in Order:
            self.AddWeight([Means.MUSIC_START, Means.MUSIC_STOP, Means.MUSIC_LAST,
                            Means.MUSIC_NEXT, Means.MUSIC_VOLUME_UP, Means.MUSIC_VOLUME_DOWN,
                            Means.MUSIC_LIKE, Means.MUSIC_LYRIC], 2)
        # MUSIC ++
        if '播放' in Order:
            self.AddWeight([Means.MUSIC_START], 1)
        if '打开' in Order or '开始' in Order:
            self.AddWeight([Means.MUSIC_START], 2)
        if '停' in Order or '暂' in Order or '关' in Order:
            self.AddWeight([Means.MUSIC_STOP], 2)
        if '上一' in Order:
            self.AddWeight([Means.MUSIC_LAST], 2)
        if '下一' in Order:
            self.AddWeight([Means.MUSIC_NEXT], 2)
        if '音量' in Order or '声音' in Order:
            self.AddWeight([Means.MUSIC_VOLUME_UP, Means.MUSIC_VOLUME_DOWN], 2)
        if '增' in Order or '加' in Order or '大' in Order or '高' in Order:
            self.AddWeight([Means.MUSIC_VOLUME_UP])
        if '降' in Order or '低' in Order or '减' in Order or '小' in Order:
            self.AddWeight([Means.MUSIC_VOLUME_DOWN])
        if '喜' in Order or '爱' in Order or 'like' in Order or 'love' in Order:
            self.AddWeight([Means.MUSIC_LIKE], 2)
        if '歌词' in Order:
            self.AddWeight([Means.MUSIC_LYRIC], 3)

        MaxWeight = max(self.MeansWeight.values())
        for key in self.MeansWeight.keys():
            if self.MeansWeight[key] == MaxWeight:
                FinalMean = key
                break

        # 重新初始化MeansWeight
        self.MeansWeight = {Means.UNKNOWN: 0}

        # UNKNOWN
        if FinalMean == Means.UNKNOWN:
            return {'Type': FinalMean}
        # PC
        elif FinalMean == Means.PC_LOCK:
            ReferTime = Order[0: Order.rfind('锁屏')]  # 指代时间的部分
            SleepTime = 0
            if ReferTime:
                if ReferTime[-1] == '后':
                    if ReferTime[-2] == '秒':
                        # 转换为数字
                        SleepTime = cntn.ch2num(ReferTime[0: -2])
                    elif ReferTime[-3: -1] == '分钟':
                        # 转换为数字
                        SleepTime = cntn.ch2num(ReferTime[0: -3]) * 60
            return {'Type': FinalMean, 'SleepTime': SleepTime}
        elif FinalMean == Means.PC_CLOSE:
            pass
        # APP
        elif FinalMean == Means.APP_OPEN:
            Flag = 0
            an_ratio = 0
            MatchAppName = ''
            for an in self.PC.AppList:
                if '打开' in Order:
                    an_ratio = fuzz.partial_ratio(an, Order.replace('打开', ''))
                elif 'open' in Order:
                    an_ratio = fuzz.partial_ratio(an, Order.replace('open', ''))
                if an_ratio > Flag:
                    Flag = an_ratio
                    MatchAppName = an
            if Flag > 50:
                return {'Type': FinalMean, 'AppName': MatchAppName}
            # 否则直接返回UNKNOWN
        # WEB
        elif FinalMean in [Means.WEB_BAIDU_SEARCH, Means.WEB_IQIYI_SEARCH, Means.WEB_VQQ_SEARCH]:
            # 搜索后的内容，+4指针移到搜索后
            ToSearch = Order[(Order.rfind('搜索') + 2):]
            return {'Type': FinalMean, 'ToSearch': ToSearch}
        elif FinalMean == Means.WEB_MUSIC_PLAY:
            MusicName = Order[2:]
            return {'Type': FinalMean, 'MusicName': MusicName}
        # WECHAT
        elif FinalMean == Means.WECHAT_SEND:
            # 姓名
            FindResult = re.findall('给(.*?)发送', Order)
            # 给...发送...
            if FindResult:
                RecoName = FindResult[0]
            # 只有发送
            else:
                RecoName = Order[0: (Order.rfind('发送'))]
            Name = ''
            for i in range(len(self.Chat.FriendNameList)):
                # 比较两者拼音的相似度
                # print(''.join(ppy.lazy_pinyin(self.FriendNameList[i])))
                Similarity = self.PinYinSimilarity(
                    ''.join(ppy.lazy_pinyin(self.Chat.FriendNameList[i])),
                    ''.join(ppy.lazy_pinyin(RecoName)))
                # 若拼音相似度大于95%
                if Similarity > 0.9:
                    Name = self.Chat.FriendNameList[i]
                    break
            # 消息
            Msg = Order[(Order.rfind('发送') + 2):]
            print(Msg, 'will be sent to', Name)
            return {'Type': FinalMean, 'Name': Name, 'Massage': Msg}
        elif FinalMean == Means.WECHAT_PYQ:
            # todo
            pass
        # MUSIC, cloud music
        elif FinalMean in [Means.MUSIC_START, Means.MUSIC_STOP, Means.MUSIC_LAST,
                           Means.MUSIC_NEXT, Means.MUSIC_VOLUME_UP, Means.MUSIC_VOLUME_DOWN,
                           Means.MUSIC_LIKE, Means.MUSIC_LYRIC]:
            return {'Type': FinalMean}

        # 其他情况，返回UNKNOWN
        return {'Type': Means.UNKNOWN}


if __name__ == '__main__':
    us = Understand()
    us.WhatDoYouMean('音量增加')

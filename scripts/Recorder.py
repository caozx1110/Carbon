# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: Recorder.py
date: 2021/7/29
function: https://blog.csdn.net/muxiong0308/article/details/113835127
"""

import pyaudio
from loguru import logger

'''
参考文档
http://people.csail.mit.edu/hubert/pyaudio/#docs
'''


class Recorder(object):

    def __init__(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=16000, CHUNK=1024):
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        logger.info('Recorder已创建')
        return

    def get_record_audio(self):
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        return frames

    def __del__(self):
        # self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        logger.info('Recorder已销毁')
        return



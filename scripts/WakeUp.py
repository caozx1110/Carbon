# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: WakeUp.py
date: 2021/7/29
function: https://blog.csdn.net/muxiong0308/article/details/113835127
"""

import os
from ctypes import cdll, byref, c_void_p, CFUNCTYPE, c_char_p, c_uint64, c_int64
from loguru import logger
import Recorder
from Carbon import Carbon
from PyQt5.QtCore import pyqtSignal, QObject

class WakeUp(QObject):
    WakedUp = pyqtSignal()
    RecoFinished = pyqtSignal(str)
    ExecuteFinished = pyqtSignal()
    Car = Carbon()

    def __init__(self):
        super(WakeUp, self).__init__()
        CALLBACKFUNC = CFUNCTYPE(None, c_char_p, c_uint64, c_uint64, c_uint64, c_void_p, c_void_p)
        self.pCallbackFunc = CALLBACKFUNC(self.py_ivw_callback)
        pass

    def ivw_wakeup(self):
        try:
            msc_load_library = './awaken/bin/msc_x64.dll'
            app_id = '316e9b7a'  # 填写自己的app_id
            ivw_threshold = '0:1450'
            jet_path = os.getcwd() + './awaken/bin/msc/res/ivw/wakeupresource.jet'
            work_dir = 'fo|' + jet_path
        except Exception as e:
            return e

        # ret 成功码
        MSP_SUCCESS = 0

        dll = cdll.LoadLibrary(msc_load_library)
        errorCode = c_int64()
        sessionID = c_void_p()
        # MSPLogin
        Login_params = "appid={},engine_start=ivw".format(app_id)
        Login_params = bytes(Login_params, encoding="utf8")
        ret = dll.MSPLogin(None, None, Login_params)
        if MSP_SUCCESS != ret:
            logger.info("MSPLogin failed, error code is: %d", ret)
            return

        # QIVWSessionBegin
        Begin_params = "sst=wakeup,ivw_threshold={},ivw_res_path={}".format(
            ivw_threshold, work_dir)
        Begin_params = bytes(Begin_params, encoding="utf8")
        dll.QIVWSessionBegin.restype = c_char_p
        sessionID = dll.QIVWSessionBegin(None, Begin_params, byref(errorCode))
        if MSP_SUCCESS != errorCode.value:
            logger.info("QIVWSessionBegin failed, error code is: {}".format(
                errorCode.value))
            return

        # QIVWRegisterNotify
        dll.QIVWRegisterNotify.argtypes = [c_char_p, c_void_p, c_void_p]
        ret = dll.QIVWRegisterNotify(sessionID, self.pCallbackFunc, None)
        if MSP_SUCCESS != ret:
            logger.info("QIVWRegisterNotify failed, error code is: {}".format(ret))
            return

        # QIVWAudioWrite
        recorder = Recorder.Recorder()
        dll.QIVWAudioWrite.argtypes = [c_char_p, c_void_p, c_uint64, c_int64]
        ret = MSP_SUCCESS
        logger.info("* start recording")
        while ret == MSP_SUCCESS:
            audio_data = b''.join(recorder.get_record_audio())
            audio_len = len(audio_data)
            ret = dll.QIVWAudioWrite(sessionID, audio_data, audio_len, 2)
        logger.info('QIVWAudioWrite ret =>{}', ret)
        logger.info("* done recording")
        recorder.__del__()

    def py_ivw_callback(self, sessionID, msg, param1, param2, info, userDate):
        # typedef int( *ivw_ntf_handler)( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData );
        # 在此处编辑唤醒后的动作
        # print("sessionID =>", sessionID)
        # print("msg =>", msg)
        # print("param1 =>", param1)
        # print("param2 =>", param2)
        # print("info =>", info)
        # print("userDate =>", userDate)

        try:
            # 被唤醒的信号
            self.WakedUp.emit()
            print("Hi, Master!")
            # 唤醒后打开声卡
            self.Car.Stream.start_stream()
            # 听直到无声音
            self.Car.ListenUntilMute()
            # 结束收听
            self.Car.Stream.stop_stream()
            # 保存识别执行
            self.Car.SaveAudio()
            # 识别
            RecoResult = self.Car.Recognize()
            # 投射信号
            self.RecoFinished.emit(RecoResult)
            # 执行
            self.Car.Execute()
            # 投射信号
            self.ExecuteFinished.emit()

        except KeyboardInterrupt:
            print("You stop Carbon (sad) : KeyboardInterrupt")

    # 非唤醒模式，其他方式执行（鼠标或键盘）
    def Do(self):
        try:
            print("Hi, Master!")
            # 唤醒后打开声卡
            self.Car.Stream.start_stream()
            # 听直到无声音
            self.Car.ListenUntilMute()
            # 结束收听
            self.Car.Stream.stop_stream()
            # 保存识别执行
            self.Car.SaveAudio()
            # 识别
            RecoResult = self.Car.Recognize()
            # 投射信号
            self.RecoFinished.emit(RecoResult)
            # 执行
            self.Car.Execute()
            # 投射信号
            self.ExecuteFinished.emit()
        except KeyboardInterrupt:
            print("You stop Carbon (sad) : KeyboardInterrupt")


if __name__ == '__main__':
    # 语音唤醒
    try:
        WakeUp().ivw_wakeup()
    except KeyboardInterrupt:
        print("You stop Carbon (sad) : KeyboardInterrupt")


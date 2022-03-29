# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: CarbonUI.py
date: 2021/8/10
function: UI for Carbon
"""
import sys
import time
from PyQt5.QtWidgets import QLabel, QFrame, QApplication, QSystemTrayIcon, QAction, QMenu, qApp, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QMouseEvent
from MainWindowUI import *
from MainProgress import MainProgress
import Resource_rc

# 带点击槽函数的Label
class MyQLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    doubleclicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    # 重写label双击事件
    def mouseDoubleClickEvent(self, e: QMouseEvent):
        # 左键双击
        if e.button() == Qt.LeftButton:
            self.doubleclicked_signal.emit()
        else:
            pass

# 球的滚动线程
class RollThread(QThread):
    Ball: MyQLabel

    def __init__(self, ball):
        super(RollThread, self).__init__()
        self.Ball = ball

    def run(self) -> None:
        pass
        while True:
            for i in range(28):
                self.Ball.setPixmap(QPixmap('./rcc/' + str(i) + '.png'))
                time.sleep(1 / 12)

# 线的跳动线程
class JumpThread(QThread):
    Line1: QFrame
    Line2: QFrame
    Line3: QFrame
    Line4: QFrame
    Line5: QFrame
    Len = 40

    def __init__(self, line1, line2, line3, line4, line5):
        super(JumpThread, self).__init__()
        self.Line1 = line1
        self.Line2 = line2
        self.Line3 = line3
        self.Line4 = line4
        self.Line5 = line5
        self.Line1.setFixedSize(10, self.Len)
        self.Line3.setFixedSize(10, self.Len)
        self.Line5.setFixedSize(10, self.Len)
        self.Line2.setFixedSize(10, 60 - self.Len)
        self.Line4.setFixedSize(10, 60 - self.Len)

    def run(self) -> None:
        while True:
            while self.Len < 50:
                self.Len = self.Len + 5
                self.Line1.setFixedSize(10, self.Len)
                self.Line3.setFixedSize(10, self.Len)
                self.Line5.setFixedSize(10, self.Len)
                self.Line2.setFixedSize(10, 60 - self.Len)
                self.Line4.setFixedSize(10, 60 - self.Len)
                time.sleep(1 / 24)
            while self.Len > 10:
                self.Len = self.Len - 5
                self.Line1.setFixedSize(10, self.Len)
                self.Line3.setFixedSize(10, self.Len)
                self.Line5.setFixedSize(10, self.Len)
                self.Line2.setFixedSize(10, 60 - self.Len)
                self.Line4.setFixedSize(10, 60 - self.Len)
                time.sleep(1 / 24)

class MainWindow(QtWidgets.QWidget, Ui_Carbon):
    Mp = MainProgress()
    lbl_Ball: MyQLabel
    lbl_Info: MyQLabel
    RThread: RollThread
    JThread: JumpThread
    Info = ''
    IsShow = True           # 设置默认是否显示

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/Carbon.ico'))
        # 重写鼠标事件用
        self._endPos = None
        self._startPos = None
        self._isTracking = False
        # 无边框, 不显示在任务栏
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 位于底部
        Desk = QApplication.desktop()
        x = (Desk.width() - self.width()) // 2
        y = (Desk.height() - self.height()) - 20
        self.move(x, y)
        # 透明度
        self.setWindowOpacity(0.9)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # 系统托盘
        self.SystemTray = QSystemTrayIcon(self)  # 图标设置
        self.SystemTray.setIcon(QIcon(':/Carbon.ico'))
        # 设置托盘单击事件, 显示和隐藏
        self.SystemTray.activated.connect(self.SystemTrayClicked)
        # 操作，显示和隐藏不许要了，用单双击实现
        # self.ActionShow = QAction('&显示', self.SystemTray, triggered=self.show)
        # self.ActionHide = QAction('&最小化', self.SystemTray, triggered=self.hide)
        self.ActionQuit = QAction('&退出', self.SystemTray, triggered=self.Quit)
        # 菜单
        self.stMenu = QMenu()
        # self.stMenu.addAction(self.ActionShow)
        # self.stMenu.addAction(self.ActionHide)
        self.stMenu.addAction(self.ActionQuit)
        self.SystemTray.setContextMenu(self.stMenu)
        # 不调用show不会显示系统托盘
        self.SystemTray.show()

        # lbl_Ball
        self.lbl_Ball = MyQLabel(self)
        self.lbl_Ball.setFixedSize(80, 80)
        x = (self.width() - self.lbl_Ball.width()) // 2
        y = (self.height() - self.lbl_Ball.height()) // 2
        self.lbl_Ball.move(x, y)
        self.lbl_Ball.setScaledContents(True)
        self.lbl_Ball.doubleclicked_signal.connect(self.lbl_Ball_doubleclicked)
        # lbl_Info
        self.lbl_Info = MyQLabel(self)
        self.lbl_Info.setFixedHeight(20)
        x = (self.width() - self.lbl_Info.width()) // 2
        y = (self.height() - self.lbl_Info.height()) // 2
        self.lbl_Info.move(x, y)
        self.lbl_Info.setAlignment(Qt.AlignCenter)      # 文字居中
        self.lbl_Info.setStyleSheet('''QLabel{
                                                font-size:18px;
                                                font-weight:200;
                                                color: orange;
                                                font-family: "微软雅黑";
                                              }''')
        self.lbl_Info.doubleclicked_signal.connect(self.lbl_Ball_doubleclicked)
        # Ball Roll线程
        # todo: 可在合适时候关闭线程，减小资源的占用
        self.RThread = RollThread(self.lbl_Ball)
        self.RThread.start()
        # line jump线程
        # todo: 可在合适时候关闭线程，减小资源的占用
        self.JThread = JumpThread(self.ln_Yellow, self.ln_Orange, self.ln_Purple, self.ln_Blue, self.ln_Cyan)
        self.JThread.start()
        # signal
        self.Mp.MainWakeUp.RecoFinished.connect(self.RecoFinished)
        self.Mp.MainWakeUp.ExecuteFinished.connect(self.ExecuteFinished)
        # WakeUp
        self.Mp.WakeUp()
        self.Mp.MainWakeUp.WakedUp.connect(self.ShowLines)
        # Show Ball
        self.ShowBall()

    def __del__(self):
        self.SystemTray.setVisible(False)
        super(MainWindow, self).__del__()

    # 重写鼠标移动事件
    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        # if e.button() == Qt.LeftButton:
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    # 重写鼠标按下事件
    def mousePressEvent(self, e: QMouseEvent):
        self._isTracking = True
        self._startPos = QPoint(e.x(), e.y())

    # 重写鼠标松开事件
    def mouseReleaseEvent(self, e: QMouseEvent):
        self._isTracking = False
        self._startPos = None
        self._endPos = None

    # 安全退出
    def Quit(self):
        self.SystemTray.setVisible(False)
        qApp.quit()

    # 只显示跳动的线
    def ShowLines(self):
        self.show()
        # 黄橘紫蓝青show
        self.ln_Yellow.show()
        self.ln_Orange.show()
        self.ln_Purple.show()
        self.ln_Blue.show()
        self.ln_Cyan.show()
        # ball hide
        self.lbl_Ball.hide()
        # Info hide
        self.lbl_Info.hide()

    # 只显示滚动的球
    def ShowBall(self):
        self.show()
        # 黄橘紫蓝青hide
        self.ln_Yellow.hide()
        self.ln_Orange.hide()
        self.ln_Purple.hide()
        self.ln_Blue.hide()
        self.ln_Cyan.hide()
        # ball show
        self.lbl_Ball.show()
        # Info hide
        self.lbl_Info.hide()

    # 显示Info
    def ShowInfo(self):
        self.lbl_Info.show()
        self.lbl_Info.setText(self.Info)

    # 球双击
    def lbl_Ball_doubleclicked(self):
        self.ShowLines()
        self.Mp.Do()

    # 识别结束
    def RecoFinished(self, RecoResult):
        self.Info = RecoResult
        self.ShowInfo()

    def ExecuteFinished(self):
        if self.IsShow:
            self.ShowBall()
        else:
            self.ShowBall()
            self.hide()

    # 系统托盘点击
    def SystemTrayClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 3:
            if self.isVisible():
                self.hide()
                self.IsShow = False
            else:
                self.show()
                self.IsShow = True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

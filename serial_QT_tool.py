#!/user/bin/python3
# -*- coding:utf-8 -*-
'''
产测工具，用于测试串口通信是否ok.主要流程是，串口发送测试指令，然后检查返回指令是否为期待指令。
'''

__author__ = 'Duanlin D'

import sys
import threading
import SerialSettingLayout as SSLayout

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QGridLayout,
                             QVBoxLayout, QGroupBox, QToolTip, QDesktopWidget, QTextBrowser)
from PyQt5.QtGui import (QIcon, QFont, QColor)
from PyQt5.QtCore import (QBasicTimer)


class SerialQtTool(QWidget):
    Qt_Test_interval = 0.2  # 产测时间间隔
    Qt_Test_Count = 5   # 测试次数
    Qt_Test_Message = "test_cmd"    # 测试指令
    Qt_Test_Return = "ok"   # 期待的返回指令

    def __init__(self):
        super(SerialQtTool, self).__init__()
        self.read_data_timer = QBasicTimer()    # 定时器,用于定时读取串口返回值

        # 产测状态
        self.qt_test_count = SerialQtTool.Qt_Test_Count     # 测试次数,每次启动测试自减
        self.qt_test_interval = SerialQtTool.Qt_Test_interval   # 测试间隔
        self.is_qt_test_ok = False  # 测试成功标志

        # 产测工具界面
        self.qt_test_button = QPushButton(u'start')     # 启动测试按钮,
        self.log_view_groupBox = QGroupBox("log view")  # 测试结果显示窗口组
        self.serial_setting_groupBox = QGroupBox("serial_setting")     # 串口设置界面组

        # 产测结果显示文本框设置
        self.log_view_textBrowser = QTextBrowser()      # 用于显示结果的文本框
        self.log_view_textBrowser.setFont(QFont('Helvetica', 28))   # 配置显示格式

        # 串口工具界面布局
        self.serial_setting_layout = SSLayout.SerialSettingLayout(self.start_read_data, self.stop_read_data) #初始化串口设置界面布局,并绑定串口打开和关闭时的操作

        # 初始化界面
        self.init_ui()

    def init_log_view_group(self):
        """
        初始化打印窗口
        :return:
        """
        # 初始化测试结果界面布局为垂直布局
        log_view_layout = QVBoxLayout()
        # 添加文本框
        log_view_layout.addWidget(self.log_view_textBrowser)

        # 添加布局到组
        self.log_view_groupBox.setLayout(log_view_layout)

    def init_serial_setting_group(self):
        """
        初始化串口设置界面
        :return:
        """

        # 设置产测开始按钮
        QToolTip.setFont(QFont('SansSerif', 10))    # 设置按钮提示样式
        self.qt_test_button.setToolTip("start qt test")     # 设置按钮提示文本
        self.qt_test_button.clicked.connect(self.qt_test_button_handle)     # 绑定按钮点击事件
        self.qt_test_button.setEnabled(False)       # 按钮默认不可点击

        # 设置串口设置界面
        serial_setting_layout = self.serial_setting_layout.get_serial_setting_layout()  # 获取串口设置界面布局
        serial_setting_layout.addWidget(self.qt_test_button)    # 添加开始测试按钮到布局

        # 添加布局到组
        self.serial_setting_groupBox.setLayout(serial_setting_layout)

    def init_ui(self):
        """
        初始化界面布局
        :return:
        """
        # 初始化串口设置界面组
        self.init_serial_setting_group()
        # 初始化测试结果显示界面组
        self.init_log_view_group()
        # 设置窗口布局
        self.set_frame()

    def qt_test_fun(self):
        """
        产测执行程序，以一定的时间间隔执行指定次数，直到成功为止
        :return:
        """

        # 写入产测指令
        self.serial_setting_layout.serial_write(SerialQtTool.Qt_Test_Message)
        self.qt_test_count -= 1     # 产测次数自减
        # 判断是否还有产测次数
        if self.qt_test_count > 0:
            # 有,则继续执行产测
            self.qt_fun_timer = threading.Timer(self.qt_test_interval, self.qt_test_fun)    # 设置产测定时器
            self.qt_fun_timer.start()   # 启动产测定时器

    def qt_test_button_handle(self):
        """
        产测按钮响应程序
        :return:
        """

        # 判断串口工具是否已打开
        if self.serial_setting_layout.is_serial_open:
            # 已打开
            self.qt_test_button.setEnabled(False)   # 设置测试按钮为不可点击
            self.log_view_textBrowser.clear()       # 清除测试结果显示文本框
            self.qt_test_count = SerialQtTool.Qt_Test_Count     # 初始化测试次数
            self.qt_fun_timer = threading.Timer(self.qt_test_interval, self.qt_test_fun)    # 设置产测定时器,定时执行产测
            self.qt_fun_timer.start()   # 启动产测定时器

    def timerEvent(self, e):
        """
        定时器执行程序,复写此函数,则当系统定时器启动时,定时执行此程序
        :param e:
        :return:
        """

        # 读取一行串口数据,返回字符串
        text_line = self.serial_setting_layout.serial_readline()

        # 判断返回的是否为期待指令
        if text_line and SerialQtTool.Qt_Test_Return in text_line:
            # 是期待指令,则测试成功
            self.log_view_textBrowser.setTextColor(QColor(0, 255, 0))   # 设置测试结果显示字体颜色为绿色
            self.log_view_textBrowser.setText("测试成功")       # 设置测试结果显示内容为测试成功
            self.qt_fun_timer.cancel()      # 关闭定时发送指令定时器
            self.qt_test_button.setEnabled(True)    # 设置产测按钮为可点击
        # 判断测试次数是否已用完
        elif self.qt_test_count <= 0:
            # 测试超时
            self.log_view_textBrowser.setTextColor(QColor(255, 0, 0))   #设置测试结果显示字体颜色为红色
            self.log_view_textBrowser.setText("测试失败")   #设置测试结果显示内容为测试失败
            self.qt_test_button.setEnabled(True)    # 设置测试按钮为可点击

    def start_read_data(self):
        """
        开始读取数据,此函数与SerialSettingLayout 类下的,串口开启按钮关联,并在串口打开时自动执行
        :return:
        """
        # 启动数据读取定时器
        self.read_data_timer.start(2, self)     # 开启定时读取定时器,间隔2ms
        self.qt_test_button.setEnabled(True)    # 设置产测按钮为可点击
        pass

    def stop_read_data(self):
        """
        停止读取数据，此函数与SerialSettingLayout 类下的,串口开启按钮关联,并在串口关闭时自动执行
        :return:
        """
        self.read_data_timer.stop()     # 停止定时读取定时器
        self.qt_test_button.setEnabled(False)   # 设置产测按钮为不可点击
        pass

    def center(self):
        """
        将程序串口置于屏幕中央
        :return:
        """
        qr = self.frameGeometry()   # 获取当前程序窗口
        cp = QDesktopWidget().availableGeometry().center()  # 获取桌面中心点
        qr.moveCenter(cp)   # 设置当前窗口中心为桌面中心
        self.move(qr.topLeft())     # 移动当前窗口到,相对于当前窗口中心的左上角

    def set_frame(self):
        """
        设置窗口布局
        :return:
        """
        main_layout = QGridLayout()     # 初始化主窗口布局为网格布局
        main_layout.addWidget(self.log_view_groupBox, 0, 0, 1, 4)   # 在（0,0）格子上放置一个跨度1行，4列的控件组
        main_layout.addWidget(self.serial_setting_groupBox, 0, 5)   # 在(0,5) 格子上放置一个控件组
        self.setLayout(main_layout)     # 设置窗口布局

        self.setWindowTitle('serial qt tool')   # 设置主窗口标题

        self.setWindowIcon(QIcon('images/logo.png'))    # 设置窗口图标
        self.resize(600, 400)   # 设置窗口大小
        self.center()   # 窗口居中显示
        self.show()     # 显示窗口


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SerialQtTool()
    sys.exit(app.exec_())

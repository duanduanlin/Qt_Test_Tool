#!/user/bin/python3
# -*- coding:utf-8 -*-
'''
串口工具设置面板
'''

__author__ = 'Duanlin D'

import sys
import os
import serial
import serial.tools.list_ports
import configparser

from PyQt5.QtWidgets import (QWidget, QApplication, QComboBox, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QToolTip, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont)


class SerialSettingLayout(QWidget):

    def __init__(self, open_callback=None, close_callback=None):
        """
        SerialSettingLayout构造函数
        :param open_callback: 串口打开时,执行的回调
        :param close_callback: 串口关闭时，执行的回调
        """
        super(SerialSettingLayout, self).__init__()

        # 初始化serial对象,用于串口通信
        self.serial = serial.Serial()

        # 串口设置界面
        self.open_close_button = QPushButton(u'打开串口')   # 打开或关闭串口按钮
        self.refresh_button = QPushButton(u'刷新串口')      # 刷新串口按钮

        self.serial_setting_layout = QVBoxLayout()      # 串口设置界面布局，垂直布局

        self.serial_parity_comboBox = QComboBox()       # 奇偶校验下拉列表
        self.serial_stopBits_comboBox = QComboBox()     # 停止位下拉列表
        self.serial_data_comboBox = QComboBox()         # 数据位下拉列表
        self.serial_baudRate_comboBox = QComboBox()     # 波特率下拉列表
        self.serial_COM_comboBox = QComboBox()          # 串口号下拉列表

        # 串口设置信息 保存和读取
        self.cfg_serial_dic = {}        # 用于保存串口设置信息的字典
        self.current_path = os.path.dirname(os.path.realpath(__file__))     # 当前目录
        self.cfg_path = ''  # 配置文件的路径
        self.cfg_dir = 'settings'   # 配置文件目录
        self.conf_file_name = "cfg.ini"     # 配置文件名
        self.confParse = configparser.ConfigParser()    # 配置文件解析ConfigParser对象
        self.is_serial_open = False     # 串口状态,默认关闭

        self.serial_open_callback = open_callback   # 串口打开时执行的回调
        self.serial_close_callback = close_callback     # 串口关闭时执行的回调
        self.init_ui()      # 初始化界面布局

    def init_ui(self):
        """
        初始化串口设置界面布局
        :return:
        """
        self.read_config()      # 读取串口设置信息
        self.init_setting_layout()  # 初始化串口界面布局

    def read_config(self):
        """
        读取串口配置
        :return:
        """
        self.cfg_path = os.path.join(self.current_path, self.cfg_dir, self.conf_file_name)  # 获取配置文件路径
        # 判断读取配置文件是否正常
        if self.confParse.read(self.cfg_path, encoding='utf-8'):

            # 判断读取section是否正常
            try:
                items = self.confParse.items('serial_setting')      # 获取 serial_setting section，返回字典
                self.cfg_serial_dic = dict(items)
                # print(self.cfg_serial_dic)
            # 未找到section
            except configparser.NoSectionError:
                self.confParse.add_section('serial_setting')    # 添加section
                self.confParse.write(open(self.cfg_path, 'w'))  # 保存到配置文件
        # 异常
        else:
            # 判断目录是否存在,不存在的话新建目录
            if not os.path.exists(os.path.join(self.current_path, self.cfg_dir)):
                os.mkdir(os.path.join(self.current_path, self.cfg_dir))

            self.confParse.add_section('serial_setting')        # 添加section
            self.confParse.write(open(self.cfg_path, 'w'))      # 保存到配置文件

    def init_setting_layout(self):
        """
        初始化串口设置组
        :return:
        """
        # 串口设置界面初始化
        serial_com_label = QLabel(u'串口号')
        self.serial_COM_comboBox.addItems(self.get_port_list())
        self.serial_COM_comboBox.setCurrentText(self.cfg_serial_dic.get('com', 'COM1'))     # 选择默认端口

        serial_baud_rate_label = QLabel(u'波特率')
        self.serial_baudRate_comboBox.addItems(['100', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200',
                                                '38400', '56000', '57600', '115200', '128000', '256000'])
        self.serial_baudRate_comboBox.setCurrentText(self.cfg_serial_dic.get('baudrate', '9600'))   # 选择默认波特率

        serial_data_label = QLabel(u'数据位')
        self.serial_data_comboBox.addItems(['5', '6', '7', '8'])
        self.serial_data_comboBox.setCurrentText(self.cfg_serial_dic.get('data', '8'))      # 选择默认数据位

        serial_stop_bits_label = QLabel(u'停止位')
        self.serial_stopBits_comboBox.addItems(['1', '1.5', '2'])
        self.serial_stopBits_comboBox.setCurrentText(self.cfg_serial_dic.get('stopbits', '1'))  # 选择默认停止位

        serial_parity_label = QLabel(u'奇偶校验位')
        self.serial_parity_comboBox.addItems(['N', 'E', 'O', 'M', 'S'])
        self.serial_parity_comboBox.setCurrentText(self.cfg_serial_dic.get('parity', 'N'))      # 选择默认奇偶校验位

        # 设置按钮
        QToolTip.setFont(QFont('SansSerif', 10))    # 设置按钮提示样式
        self.open_close_button.setToolTip("open or close selected port")    # 设置打开或关闭串口按钮提示信息
        self.refresh_button.setToolTip("refresh current port")      # 设置刷新串口按钮提示信息
        self.open_close_button.clicked.connect(self.open_close_button_handle)   # 绑定开启按钮点击事件
        self.refresh_button.clicked.connect(self.refresh_button_handle)     # 绑定刷新串口点击事件

        # 设置串口选择布局为水平布局
        serial_com_layout = QHBoxLayout()
        serial_com_layout.addWidget(serial_com_label)   # 添加标签
        serial_com_layout.addWidget(self.serial_COM_comboBox)   # 添加下拉列表

        # 设置波特率选择布局为水平布局
        serial_baud_rate_layout = QHBoxLayout()
        serial_baud_rate_layout.addWidget(serial_baud_rate_label)
        serial_baud_rate_layout.addWidget(self.serial_baudRate_comboBox)

        # 设置数据位选择布局为水平布局
        serial_data_layout = QHBoxLayout()
        serial_data_layout.addWidget(serial_data_label)
        serial_data_layout.addWidget(self.serial_data_comboBox)

        # 设置停止位选择布局为水平布局
        serial_stop_bits_layout = QHBoxLayout()
        serial_stop_bits_layout.addWidget(serial_stop_bits_label)
        serial_stop_bits_layout.addWidget(self.serial_stopBits_comboBox)

        # 设置奇偶校验位选择布局为水平布局
        serial_parity_layout = QHBoxLayout()
        serial_parity_layout.addWidget(serial_parity_label)
        serial_parity_layout.addWidget(self.serial_parity_comboBox)

        # 设置按钮布局为水平布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_close_button)
        button_layout.addWidget(self.refresh_button)

        # 添加控件布局到串口设置布局
        self.serial_setting_layout.addLayout(serial_com_layout)
        self.serial_setting_layout.addLayout(serial_baud_rate_layout)
        self.serial_setting_layout.addLayout(serial_data_layout)
        self.serial_setting_layout.addLayout(serial_stop_bits_layout)
        self.serial_setting_layout.addLayout(serial_parity_layout)
        self.serial_setting_layout.addLayout(button_layout)

    @staticmethod
    def get_port_list():
        """
        获取当前系统所有COM口
        :return:
        """
        com_list = []   # 用于保存端口名的列表
        port_list = serial.tools.list_ports.comports()    # 获取本机端口，返回list
        for port in port_list:
            com_list.append(port[0])    # 保存端口到列表
        return com_list     # 返回列表

    def save_config(self):
        """
        保存配置
        :return:
        """
        self.confParse.set('serial_setting', 'com', self.serial.port)
        self.confParse.set('serial_setting', 'baudRate', str(self.serial.baudrate))
        self.confParse.set('serial_setting', 'data', str(self.serial.bytesize))
        self.confParse.set('serial_setting', 'stopBits', str(self.serial.stopbits))
        self.confParse.set('serial_setting', 'parity', self.serial.parity)
        self.confParse.write(open(self.cfg_path, 'w'))

    def get_serial_setting(self):
        """
        读取串口配置信息
        :return:
        """
        self.serial.port = self.serial_COM_comboBox.currentText()
        self.serial.baudrate = int(self.serial_baudRate_comboBox.currentText())
        self.serial.bytesize = int(self.serial_data_comboBox.currentText())
        self.serial.stopbits = int(self.serial_stopBits_comboBox.currentText())
        self.serial.parity = self.serial_parity_comboBox.currentText()
        self.serial.timeout = 0

    def open_serial(self):
        """
            打开串口
            :return:
        """
        # 获取当前串口设置信息,并保存
        self.get_serial_setting()
        self.save_config()

        # 打开串口
        try:
            self.serial.open()
        except serial.SerialException:
            QMessageBox.critical(self, "Critical", "无法打开串口！！")  # 打开失败，弹窗提示
        else:
            self.is_serial_open = True      # 更新串口状态
            self.open_close_button.setText(u'关闭串口')     # 更新按钮名称
            self.enable_serial_setting(False)   # 设置串口设置界面为不可修改
            self.serial_open_callback()     # 调用串口打开回调

    def close_serial(self):
        """
            关闭串口
            :return:
        """
        # 更新串口状态
        self.is_serial_open = False
        self.open_close_button.setText(u'打开串口')     # 更新串口打开按钮名称
        self.enable_serial_setting(True)    # 设置串口设置界面为可修改
        self.serial_close_callback()        # 调用串口关闭回调
        self.serial.close()     # 关闭串口

    def open_close_button_handle(self):
        """
        处理打开或关闭串口按键事件
        :return:
        """
        # 判断串口是否已打开,没打开的话打开,打开的话关闭
        if self.is_serial_open:
            self.close_serial()
        else:
            self.open_serial()

    def refresh_button_handle(self):
        """
        处理刷新端口按钮点击事件
        :return:
        """

        self.serial_COM_comboBox.clear()    # 清空端口选择下拉列表
        self.serial_COM_comboBox.addItems(self.get_port_list())     # 重新设置端口下拉列表

    def enable_serial_setting(self, enable):
        """
        使能串口设置组件和刷新串口组件
        :param enable: bool ,True: enable,False: disable
        :return:
        """

        # 设置串口设置界面是否可操作
        self.refresh_button.setEnabled(enable)
        self.serial_parity_comboBox.setEnabled(enable)
        self.serial_stopBits_comboBox.setEnabled(enable)
        self.serial_data_comboBox.setEnabled(enable)
        self.serial_baudRate_comboBox.setEnabled(enable)
        self.serial_COM_comboBox.setEnabled(enable)

    def get_serial_setting_layout(self):
        """
        获取串口设置布局
        :return QVBoxLayout:
        """
        return self.serial_setting_layout

    def serial_readline(self):
        """
        读取一行,串口已打开则返回读取的内容，否则返回空字符串
        :return str:
        """
        if self.is_serial_open:
            try:
                text_line = self.serial.readline()
            except Exception as e:
                print(e)
                self.close_serial()
            else:
                return text_line.decode("utf-8", "ignore")
        else:
            return ""

    def serial_write(self, data):
        """
        串口发送字符串
        :param data 待发送的字符串str:
        :return:
        """
        if self.is_serial_open:
            try:
                self.serial.write(data.encode("utf-8", "ignore"))
            except Exception as e:
                print(e)

    def set_frame(self):
        """
        设置窗口布局,测试用
        :return:
        """
        self.setLayout(self.serial_setting_layout)

        self.setWindowTitle('serial qt tool')

        self.setWindowIcon(QIcon('images/logo.png'))
        self.resize(600, 400)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SerialSettingLayout()
    w.set_frame()
    sys.exit(app.exec_())

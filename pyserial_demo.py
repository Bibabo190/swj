import sys
import struct
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from ui_demo_1 import Ui_Form
global data_num_received
x = []

def hex_to_float(h):
    i = int(h, 16)
    return struct.unpack('<f', struct.pack('<I', i))[0]

class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("串口小助手")
        self.ser = serial.Serial()
        self.port_check()

        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.charge_type = 0
        self.lineEdit_3.setText(str(self.charge_type))
        self.charge_v = 0
        self.lineEdit_4.setText(str(self.charge_v))
        self.Ammerter_v = 0
        self.lineEdit_6.setText(str(self.Ammerter_v))
        self.plc_tem = 0
        self.lineEdit_8.setText(str(self.plc_tem))
        self.plc_hum = 0
        self.lineEdit_9.setText(str(self.plc_hum))
    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)
        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)
        # 打开串口按钮/关闭串口按钮
        self.open_button.clicked.connect(self.port_open)
        self.close_button.clicked.connect(self.port_close)
        #打开蓄电池按钮/关闭蓄电池按钮
        self.open_charge.clicked.connect(self.charge_open)
        self.close_charge.clicked.connect(self.charge_close)
        # 打开智能电表按钮/关闭智能电表按钮
        self.open_Ammeter.clicked.connect(self.Ammeter_open)
        self.close_Ammeter.clicked.connect(self.Ammeter_close)
        # 打开PLC按钮/关闭智能电表按钮
        self.open_plc.clicked.connect(self.plc_open)
        self.close_plc.clicked.connect(self.plc_close)
        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)
        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)
        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)
        # 清除发送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)
        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（已开启）")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串口状态（已关闭）")
        x=[]

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if self.hex_receive.checkState():
                out_s = ''
                for i in range(0,len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                    if out_s:
                        x.append('{:02X}'.format(data[i]))
                self.s2__receive_text.insertPlainText(out_s)
                xx=x        # x为局部变量，xx为全局变量
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s2__receive_text.insertPlainText(data.decode('utf-8'))
            # 统计接收字符的数量
            self.data_num_received += num
            self.lineEdit.setText(str(self.data_num_received))
            # 获取到text光标
            textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s2__receive_text.setTextCursor(textCursor)



            if self.data_num_received % 9 == 0:
                if self.open_charge.isEnabled() is False:
                    self.charge_type = xx[4]
                    self.charge_v = int(xx[6], 16)
                    self.lineEdit_4.setText(str(self.charge_v))
                    self.lineEdit_3.setText(str(self.charge_type))
                    xx.clear()
                elif self.open_Ammeter.isEnabled() is False:
                    print(xx)
                    self.Ammerter_v = hex_to_float(''.join(xx[3:7]))
                    self.lineEdit_6.setText(str(self.Ammerter_v))


                elif self.open_plc.isEnabled() is False:
                    if self.data_num_received % 9 == 0:
                       self.plc_tem = hex_to_float(str(x[9:20]))
                       self.lineEdit_8.setText(str(self.plc_tem))
                       self.plc_hum = (x[9:20])
                       self.lineEdit_9.setText(str(self.plc_hum))

        else:
            pass


    # 定时发送数据
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)
    # 蓄电池
    def charge_open(self):
        if self.open_charge.isChecked() is False:
            self.open_charge.setEnabled(False)
            self.close_charge.setEnabled(True)
            self.formGroupBox2.setTitle("蓄电池（开启）")
    def charge_close(self):
        if self.close_charge.isChecked() is False:
            self.open_charge.setEnabled(True)
            self.close_charge.setEnabled(False)
            self.formGroupBox2.setTitle("蓄电池（关闭）")
            self.charge_type = 0
            self.lineEdit_3.setText(str(self.charge_type))
            self.charge_v= 0
            self.lineEdit_4.setText(str(self.charge_v))
    # 智能电表
    def Ammeter_open(self):
        if self.open_Ammeter.isChecked() is False:
            self.open_Ammeter.setEnabled(False)
            self.close_Ammeter.setEnabled(True)
            self.formGroupBox3.setTitle("智能电表_V（开启）")
    def Ammeter_close(self):
        if self.close_Ammeter.isChecked() is False:
            self.open_Ammeter.setEnabled(True)
            self.close_Ammeter.setEnabled(False)
            self.formGroupBox3.setTitle("智能电表（关闭）")
            self.Ammerter_v = 0
            self.lineEdit_6.setText(str(self.Ammerter_v))
    #PLC
    def plc_open(self):
        if self.open_plc.isChecked() is False:
            self.open_plc.setEnabled(False)
            self.close_plc.setEnabled(True)
            self.formGroupBox4.setTitle("plc（开启）")

    def plc_close(self):
        if self.close_plc.isChecked() is False:
            self.open_plc.setEnabled(True)
            self.close_plc.setEnabled(False)
            self.formGroupBox4.setTitle("plc（关闭）")
            self.plc_tem = 0
            self.lineEdit_8.setText(str(self.plc_tem))
            self.plc_hum = 0
            self.lineEdit_9.setText(str(self.plc_hum))

    # 清除显示
    def send_data_clear(self):
        self.s3__send_text.setText("")

    def receive_data_clear(self):
        self.s2__receive_text.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())


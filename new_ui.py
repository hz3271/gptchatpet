import json
import os
import random
import threading
import time
from datetime import datetime
from PyQt5.QtGui import QIcon,QFont,QPalette,QBrush,QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
import sys

import common
from get_weather import get_weather_data
from pyqt5_chat import ChatUI
from pyqt5_chat import user




file = "charactor/mika.txt"
charac="未花"
userchar="老师"
picai_path="png/mika.png"
model_path = "model/mika/mika.pth"
config_path = "model/mika/config.json"
apikey=""
avatar_path = "png/user64.png"
bgpic_path="png/test.png"

def charactor(charactor):
    global file,charac,userchar,picai_path,model_path,config_path
    if charactor=="小鳐":
        file = "charactor/xiaoyao.txt"
        charac="小鳐"
        userchar="指挥官"
        picai_path="png/xiaoyao.png"
        model_path = "model/yao/G_25000.pth"
        config_path = "model/yao/config.json"
class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("日志")
        self.log_text = QPlainTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QPlainTextEdit.WidgetWidth) # 启用自动换行

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.log_text)
        self.setLayout(self.layout)

        self.setFixedWidth(200)



    def update_log(self, text):
        self.log_text.appendPlainText(text)




class MessageWidget(QWidget):
    def __init__(self, avatar_path, nickname, message):
        super().__init__()
        layout = QHBoxLayout()

        avatar = QLabel()
        avatar.setFixedSize(64, 64)
        avatar.setStyleSheet("background-color: transparent;")
        avatar.setPixmap(QPixmap(avatar_path).scaled(64, 64))
        layout.addWidget(avatar)
        layout.addSpacing(5) # 在头像和文本之间添加 20 像素的空间
        text = QLabel("{}<br>{}".format(nickname, message))
        text.setWordWrap(True)    # 启用自动换行
        text.setFixedWidth(200) # 为 QLabel 设置固定宽度
        layout.addWidget(text)
        # 修改日志按钮的点击事件

        self.setLayout(layout)

class Worker(QThread):
    result = pyqtSignal(str)

    def __init__(self, func, arg):
        super().__init__()
        self.func = func
        self.arg = arg

    def run(self):
        res = self.func(self.arg)
        self.result.emit(res)

class MukuchiChatDemo(QWidget):
    new_message_signal = pyqtSignal(str)
    def __init__(self,parent=None):
        super(MukuchiChatDemo, self).__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.addMessageWidget)



        user(userchar, charac,model_path,config_path)
        use_voice=True
        self.main_sys = ChatUI(apikey,file,use_voice)
        self.log_window = LogWindow(self)
        self.new_message_signal.connect(self.send2)
        self.setWindowFlags(Qt.FramelessWindowHint)#取消边框
        self.set_palette()
        self.initUI()
        self.current_time = datetime.now()

        use_live2d = True
        common.use_live2d(use_live2d)

        self.trigger_gpt_response()
        self.worker = Worker(self.main_sys.get_response,None)
        self.worker.result.connect(self.send2)


        self.update_api_button = QPushButton('更新API', self)
        self.update_api_button.clicked.connect(self.on_update_api_button_clicked)
        self.update_api_button.setGeometry(10, 460, 80, 30)

        self.save_button = QPushButton('保存', self)
        self.save_button.clicked.connect(self.main_sys.save_chat_history)
        self.save_button.setGeometry(100, 460, 80, 30)

        self.check_button = QCheckBox('使用语音', self)
        self.check_button.setCheckState(Qt.Checked)
        self.check_button.clicked.connect(self.main_sys.use_voicecheck)
        self.check_button.setGeometry(100, 370, 80, 30)

        self.log_button = QPushButton('日志', self)
        self.log_button.clicked.connect(self.toggle_log)
        self.log_button.setGeometry(190, 460, 80, 30)

        self.jiaoben_button = QPushButton('脚本', self)
        self.jiaoben_button.clicked.connect(self.toggle_jiaoben)
        self.jiaoben_button.setGeometry(280, 460, 80, 30)

    def toggle_jiaoben(self):
        try:
            with open('prompts-zh.json', 'r', encoding="utf-8") as f:
                self.jiaoben_list = json.load(f)

            script_names = [script['act'] for script in self.jiaoben_list]

            dialog = QInputDialog()
            dialog.setWindowTitle("选择脚本")
            dialog.setLabelText("请选择一个脚本：")
            dialog.setComboBoxItems(script_names)
            if dialog.exec_() == QDialog.Accepted:
                clicked_button_text = dialog.textValue()
                for script in self.jiaoben_list:
                    if script['act'] == clicked_button_text:
                        self.get_res(script['prompt'])

        except Exception:  # Catch any type of exception
            print("-------json格式似乎不正确------")
            print(Exception)
            pass
    def on_update_api_button_clicked(self):
        # 弹出输入框
        text, ok = QInputDialog.getText(self, '更新API', '请输入新的API:')
        if ok:
            # 如果用户点击了“确定”，则使用输入的文本调用 update 方法
            self.main_sys.update_api(text)

    def toggle_log(self):
        if self.log_window.isVisible():
            self.log_window.hide()
        else:
            self.log_window.show()

    # 添加更新日志的函数
    def update_log(self, text):
        self.log_window.update_log(text)



    def initUI(self):

        font = QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(13)
        self.chat_window = QListWidget(self)
        self.chat_window.setGeometry(10, 10, 330, 350)
        self.chat_window.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 10px;
        """)


        # self.textBR.moveCursor()
        self.textEdit=QTextEdit("来聊天吧",self)

        #创建两个按钮
        self.btnPress1=QPushButton('发送',self)
        self.btnPress1.setToolTip('点击这个按钮<b>发送</b>')
        self.btnPress1.setStyleSheet("background-color: white; color: black; border-radius: 3px; ")

        #退出键

        #设置位置
        #self.textBR.setGeometry(10,10,280,300)#聊天显示框
        self.textEdit.setGeometry(10,400,280,50)#输入框
        # self.btnPress2.setGeometry(340,535,121,30)#清空
        self.btnPress1.setGeometry(310,410,40,40)#发送


        #将按钮的点击信号与相关的槽函数进行绑定，点击即触发
        self.btnPress1.clicked.connect(self.btnPress1_clicked)
        # self.btnPress2.clicked.connect(self.btnPress2_clicked)#清空按钮
        #窗口设置
        self.setWindowIcon(QIcon())
        self.setWindowTitle('聊天界面')
        self.setFixedSize(370, 502)
        self.center()

    def create_message_widget(self, username, avatar_path, message):
        return MessageWidget(username, avatar_path, message)

    def btnPress1_clicked(self):           #按钮事件
        msg0 = self.textEdit.toPlainText()
        self.bubble(msg0)
        self.textEdit.clear()

        self.worker.arg = msg0
        self.worker.start()


    def bubble(self,msg):

        msg1 = "[用户]"

        message_widget = MessageWidget(avatar_path, msg1, msg)
        list_item = QListWidgetItem(self.chat_window)
        list_item.setSizeHint(message_widget.sizeHint())  # Set appropriate size for the item
        self.chat_window.addItem(list_item)
        self.chat_window.setItemWidget(list_item, message_widget)



    def get_res(self,mes):
        mesr = self.main_sys.get_response(mes)
        self.new_message_signal.emit(mesr)
        self.update_log(mesr)

    def send2(self, message):
        self.msg1 = charac
        self.avatar_path = picai_path
        self.message_parts = message.split()
        self.timer.start(8000)  # 每x秒触发一次定时器

    def addMessageWidget(self):
        if self.message_parts:
            part = self.message_parts.pop(0)  # 从列表头部取出一个部分
            message_widget = MessageWidget(self.avatar_path, self.msg1, part)
            list_item = QListWidgetItem(self.chat_window)
            list_item.setSizeHint(message_widget.sizeHint())  # Set appropriate size for the item
            self.chat_window.addItem(list_item)
            self.chat_window.setItemWidget(list_item, message_widget)
        else:
            self.timer.stop()  # 所有部分都已使用，停止定时器

    def timesleep(self,time):
        time.sleep(time)

    #---------------------------------------


    def send_random_message(self):

        response=self.main_sys.send_random_message()
        if response !=None:


            print(f"发送随机消息: {response}")
            self.update_log(response)

        else:
            pass

        #self.send2(response)


    def schedule_next_random_message(self):
        while True:
            random_time=random.randint(60,600)
            print(random_time)
            self.update_log(f'随机时间{random_time}')
            time.sleep(random_time)
            self.send_random_message()



    def trigger_gpt_response(self):
        hour = self.current_time.hour
        minute = self.current_time.minute
        weekday = self.current_time.strftime("%A")
        if weekday in ["星期一", "星期二", "星期三", "星期四", "星期五"]:
            day="老师在上班"
        else:
            day="老师在休息"
        if 6 <= hour < 9:
            daytime = "早上"
        elif 9 <= hour < 12:
            daytime = "上午"
        elif 12 <= hour < 14:
            daytime = "中午"
        elif 14 <= hour < 18:
            daytime = "下午"
        else:
            daytime = "晚上"

        weather=get_weather_data()
        self.get_res(f"{str(daytime)}好啊,{str(hour)}点{str(minute)}分啦，你刚刚收到了一份来自API的天气预报数据，按照你的性格和语言风格，向老师解释明天的天气情况，以下是天气数据：{str(weather)}，{day}")
        thread = threading.Thread(target=self.schedule_next_random_message)
        thread.start()

    # 定义 UI

    def btnPress2_clicked(self):
        self.textBR.clear()

    def center(self):
        # ------居中显示方法-------------
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_palette(self):
        #------------设置背景----------------------
        self.setAutoFillBackground(True)
        palette=QPalette()
        palette.setColor(QPalette.WindowText, Qt.white)
        # palette.setColor(self.backgroundRole(),QColor(192,253,123,100))#设置背景颜色
        palette.setBrush(self.backgroundRole(), QBrush(QPixmap(bgpic_path).scaled(370, 502)))
        # self.label.width(), self.label.height()
        self.setPalette(palette)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.btnPress1.click()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.draggable:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.force_exit_app)
        menu.addAction(exit_action)
        menu.exec_(event.globalPos())

    def force_exit_app(self):
        os._exit(0)


if __name__ == '__main__':
    app=QApplication(sys.argv)
    win=MukuchiChatDemo()
    win.show()
    sys.exit(app.exec_())


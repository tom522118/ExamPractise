# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 06:36:05 2023
2023.06.09 
@author: Wen-Kuang Lu
英句選英單
"""


from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QMessageBox, QGridLayout, 
                             QMainWindow, QButtonGroup, QRadioButton, QVBoxLayout)
from PyQt5.QtGui import QScreen, QWindow, QPixmap
from PyQt5.QtCore import QTimer, QSize, Qt, QCoreApplication
from PyQt5.QtGui import QFontDatabase, QFont

import sys, time, json, pickle, glob, os, subprocess, datetime
import csv, random, time
from datetime import datetime
import pandas as pd
from os import path
from PyQt5.uic import loadUiType

from PyQt5 import QtCore, QtWidgets

class RadioButton(QtWidgets.QRadioButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)        
        self.setObjectName(text)
        self.setStyleSheet("QRadioButton::checked:pressed"
                                         "{"
                                         "background-color : green"
                                        "}"                                        
                                        "QRadioButton:hover" 
                                        "{"        
                                        "color:tomato;"
                                        "}"            
                                        "QRadioButton"
                                        "{"
                                        "font : 65px Typewriter;"
                                        "color : #00f;"
                                        "}")



class PushButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("pushButton")
        self.setStyleSheet("""
                QPushButton {
                    background-color: #2B5DD1;
                    font: bold 40px "Candara";
                    color: #FFFFFF;
                    text-align:center;
                    border-style: outset;
                    padding: 2px;    
                    border-width: 6px;
                    border-radius: 10px;
                    border-color: #2752B8;
                    }
                QPushButton:hover {
                        background-color: lightgreen;
                    }                  
                                      """)
        self.setText(text)


class LCDNumber(QtWidgets.QLCDNumber):
    def __init__(self, digit_count, parent=None):
        super().__init__(parent)
        self.setObjectName("lcdNumber")
        self.setDigitCount(digit_count)
        self.display(0) 

with open(".\data\data.json", 'r') as file:
        json_data = json.load(file)
        file.close()
        
with open(".\data\高年級單字表.csv", 'r', encoding='utf8', errors='ignore') as x:
    word_list = list(csv.reader(x, delimiter=","))
    x.close()

with open(".\data\word2175.pkl", 'rb') as handle:
    load_dic = pickle.load(handle)
    handle.close()
for key,value in list(load_dic.items()):
    if len(value) == 0:
        del load_dic[key]    
for i in word_list:    
    if i[0] not in load_dic.keys():
        word_list.remove(i)
for i in word_list:    
    if i[0] in dict( [x for x in word_list if x[0] not in load_dic.keys()]).keys():
        word_list.remove(i)


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main,self).__init__(parent)         
        
        self.installEventFilter(self)        
        self._id_1 = QtGui.QFontDatabase.addApplicationFont(os.path.join("data", "隸書體w3.TTC"))
        self.fontFamilies_1 = QFontDatabase.applicationFontFamilies(self._id_1)
        self._id_2 = QtGui.QFontDatabase.addApplicationFont(os.path.join("data", "TYPEWR_B.TTF"))
        self.fontFamilies_2 = QFontDatabase.applicationFontFamilies(self._id_2)
        
        self.word_list = word_list
        self.directory_path = None
        self.error_capture = '英句選英單'
        self.create_directory_path()        
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)
        
        self.right_number =0
        self.wrong_number =0
        self.timer = QTimer()
        self.timer_duration = json_data['timer']
        self.duration = self.timer_duration
        self.total_quiz = json_data['total_quiz']
        self.save_log_name = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p_")+'b.csv'
        self.msgX=json_data['msgX']
        self.msgY=json_data['msgY']
        self.key_count = 0
        self.show_radio_button_number = json_data['radionumber']
        self.msg_status = 0
        
        self.setObjectName("MainWindow")
        self.resize(1920, 1024)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(90, 20, 1291, 371))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        
        self.bg1 = QButtonGroup(self) 
        self.radio_buttons = {}
        for i in range(self.show_radio_button_number):
            radio_button_name = f"radioButton_{i+1}"
            self.radio_button = RadioButton(f"radioButton_{i+1}", self.gridLayoutWidget)            
            self.radio_button.hide()
            self.radio_button.clicked.connect(self.radio_btn)
            self.radio_buttons[radio_button_name] = self.radio_button            
        
            self.bg1.addButton(self.radio_button, i+1)            
            
            row = i % 4  
            column = i // 4  
            self.gridLayout.addWidget(self.radio_button, row, column)
        
        self.push_button = PushButton("Start", self.centralwidget)
        self.push_button.setGeometry(QtCore.QRect(1600, 20, 138, 121))        
        self.push_button.clicked.connect(self.startMe)
        
        self.lcdNumber = LCDNumber(1, self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(1760, 20, 131, 121))
        self.lcdNumber.setStyleSheet("color: seagreen;" "background-color: powderblue")        
        self.lcdNumber_2 = LCDNumber(2, self.centralwidget)
        self.lcdNumber_2.setGeometry(QtCore.QRect(1760, 180, 131, 121))
        self.lcdNumber_2.setStyleSheet("color: blue;" "background-color: lightskyblue")        
        self.lcdNumber_3 = LCDNumber(2, self.centralwidget)
        self.lcdNumber_3.setGeometry(QtCore.QRect(1600, 180, 131, 121))
        self.lcdNumber_3.setStyleSheet("color: red;" "background-color: gainsboro")
        
        parent_layout = QtWidgets.QVBoxLayout()
        self.Qlabel_quiz = QtWidgets.QLabel(self.centralwidget)
        self.Qlabel_quiz.setWordWrap(True)
        self.Qlabel_quiz.setStyleSheet("QLabel{"
                               "min-width: 800px;"
                               "min-height: 250px;"
                               "font: 40pt Typewriter;"
                               "color: steelblue; " 
                               "background-color: lightcyan;"
                               "border: 1px solid olivedrab;"
                               "}"                 
                               )


        parent_layout.setContentsMargins(90, 480, 90, 35)  
        parent_layout.setSpacing(20)  
        parent_layout.addWidget(self.Qlabel_quiz)
        
        self.centralwidget.setLayout(parent_layout)
        
        self.msg = QMessageBox()
        self.msg.setWindowTitle(f"告答-{self.error_capture}")
        self.msg.setStyleSheet("QLabel{"
                               "min-width: 800px;"
                               "min-height: 250px;"
                               "font: 30pt DFPLiShuW3-B5;"
                               "color: green; background:black;"
                               "letter-spacing: 1px;"  
                               "border: 1px solid white;"
                               "}"
                               "QPushButton{" 
                               "width:15px;" 
                               "font-size: 13px;" 
                               "}"
                               )        
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)        
        self.label_3.setGeometry(QtCore.QRect(90, 420, 1450, 55))
        self.label_3.setFrameShape(QtWidgets.QFrame.NoFrame)        
        font3 = QtGui.QFont()
        font3.setFamily('Verdana')                  
        font3.setPointSize(25)                      
        font3.setBold(True)                         
        font3.setItalic(True)                       
        self.label_3.setFont(font3)
        self.label_3.setStyleSheet("QLabel{"
                               "font: 25pt 'DFPLiShuW3-B5';"
                               "color: firebrick; background:lightyellow;"
                               "border: 1px solid white;"
                               "}"
                               "QPushButton{" 
                               "width:15px;" 
                               "font-size: 13px;" 
                               "}"                               
                               ) 
        self.label_3.setText('請閱讀例句,選出正確的單字(原型->單字三態see/saw/seen)')
        
        self.setCentralWidget(self.centralwidget)
 
    def startMe(self):
        self.push_button.hide()        
        self.restart()

    def setStyledText(self, text, styledCharacters):
        formattedText = text.replace(styledCharacters, f'<font color="yellow">{styledCharacters}</font>')
        self.setText(formattedText)
        
    def restart(self):        
        self.chk_quiz()
        self.randomlist = []
        self.QA_list =[]
 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.duration = self.timer_duration

        counter_i =0
        while counter_i <= len(self.radio_buttons):        
            self.n = random.randint(1,len(word_list)-1)
            if self.n not in self.randomlist:
                self.randomlist.append(self.n)
                counter_i +=1
        for i in self.randomlist:
            self.QA_list.append(word_list[i])

        self.Answer_int= random.randint(1,len(self.radio_buttons))
        for i, radio_button in enumerate(self.radio_buttons.values()):
            radio_button.show()
            radio_button.setText(self.QA_list[i][0])

        self.quiz_list = load_dic[self.QA_list[self.Answer_int-1][0]]
        self.show_quiz = random.randint(0,len(self.quiz_list)-1)
        qlabel_msg = """<font color='darkred' ><b>{0}</b></font>
                        """.format(self.quiz_list[self.show_quiz][0].replace(self.QA_list[self.Answer_int-1][0], " ___"))

        self.Qlabel_quiz.setText(qlabel_msg)

    def update(self):
        self.duration -= 1        
        self.lcdNumber.display(self.duration)        
        if self.duration < 0:
            self.timer.stop()
            self.wrong_number +=1 
            self.lcdNumber_3.display(self.wrong_number)
            self.write_to_csv()
            self.show_msg()
    
    def show_msg(self):        
        if self.msg_status == 0:
            self.msg_status =1
        
            trymsg = """<font color='skyblue'><b>{0}</b> / </font><font color='red'> {1} </font>
            <font color='slateblue'><p><b>{2}</b></p></font>
            <font color='powderblue'><p><b>{3}</b></p></font>        
                
                """.format(self.QA_list[self.Answer_int-1][0], self.QA_list[self.Answer_int-1][1], self.quiz_list[self.show_quiz][0], self.quiz_list[self.show_quiz][1]) 
    
            self.msg.setText(trymsg)            
            self.msg.move(self.msgX,self.msgY)
            reslut = self.msg.exec_()
            self.capture_and_save_screenshot()
            if reslut == 1024:
                self.duration = 10
                self.radio_clean()
                self.restart()
                self.msg_status =0
                self.next_or_stop()
        
    def radio_clean(self):
        self.bg1.setExclusive(False)
        for i, radio_button in enumerate(self.radio_buttons.values()):            
            radio_button.setText('')
            radio_button.setChecked(False)

    def radio_btn(self):
        self.timer.stop()
        self.button = self.sender()

        if self.bg1.checkedId() == self.Answer_int:
            self.right_number +=1
            self.lcdNumber_2.display(self.right_number)
            self.write_to_csv()
            self.next_or_stop()            
        else:            
            self.wrong_number +=1
            self.lcdNumber_3.display(self.wrong_number)     
            self.write_to_csv()
            self.show_msg()
            self.next_or_stop()            
    
    def next_or_stop(self):
        if (self.right_number + self.wrong_number) == self.total_quiz:
            self.close()
        else:
            self.radio_clean()
            self.restart()
            
    def write_to_csv(self):
        log_list = []
        log_list = [self.QA_list[self.Answer_int-1][0], self.QA_list[self.Answer_int-1][1], self.timer_duration-self.duration,  self.QA_list[self.bg1.checkedId()-1][0]]
        
        file = open(self.save_log_name, 'a', encoding='utf-8', newline='')
        write = csv.writer(file)
        write.writerow(log_list)        
        file.close()

    def create_directory_path(self):
        now = datetime.now()
        directory_name = now.strftime("%Y-%m-%d")
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.directory_path = os.path.join(desktop_path, directory_name)

    def open_directory(path):
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def capture_and_save_screenshot(self):         
        screen = app.primaryScreen()        
        pixmap = screen.grabWindow(0)        
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{self.error_capture}_{self.QA_list[self.Answer_int-1][0]}_{timestamp}.png"            
        screenshot_path = os.path.join(self.directory_path, file_name)
        pixmap.save(screenshot_path)        

    def chk_quiz(self):
        if (self.right_number + self.wrong_number) == self.total_quiz:
            self.close()     

    def restart_application(self):        
        executable = sys.executable
        args = sys.argv

        self.close()        
        subprocess.Popen([executable] + args)        

    def eventFilter(self, obj, event):
        
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Q and event.modifiers() == QtCore.Qt.ControlModifier:                
                self.close()
                
            elif event.text().lower() == "q":
                self.key_count += 1
                if self.key_count >= 2:
                
                    self.restart_application()

        return super(Main, self).eventFilter(obj, event)
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)    
    app.setApplicationDisplayName("英句選英單")
    w = Main()    
    w.showMaximized()
    sys.exit(app.exec_())
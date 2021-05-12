#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QLabel,
                             QPushButton,
                             QSpinBox,
                             QGridLayout,
                             QVBoxLayout,
                             QProgressBar,
                             QStyleFactory,
                             QFrame,
                             QDialog,
                             QScrollArea,
                             )
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.Qt import Qt
import threading
from playsound import playsound
import functools
import os


class TimeConversion():

    def convert_to_string(self, hr, min, sec):
        if sec < 10:
            sec = f"0{sec}"
        if hr < 10:
            hr = f"0{hr}"
        if min < 10:
            min = f"0{min}"

        return f"{hr}:{min}:{sec}"

    def convert_to_int(self, time):
        time = time.split(":")
        return {'H': int(time[0]),
                'M': int(time[1]),
                'S': int(time[2])
                }

    def subtract_1(self, time):
        time = self.convert_to_int(time)
        if time['S'] > 0:
            time['S'] -= 1
        else:
            time['S'] = 59
            if time['M'] > 0:
                time['M'] -= 1
            else:
                time['M'] = 59
                if time['H'] > 0:
                    time['H'] -= 1
                else:
                    time['H'] = 0
        return time

    def add_increment(self, time, increment):
        time = self.convert_to_int(time)
        seconds = (3600 * time['H']) + (60 * time['M']) + time['S'] + increment
        time['M'], time['S'] = divmod(seconds, 60)
        time['H'], time['M'] = divmod(time['M'], 60)
        return time


class Clock(QWidget):
    def __init__(self, color, hr, min, sec, increment):
        super().__init__()
        self.t = TimeConversion()
        self.hr = hr
        self.min = min
        self.sec = sec
        self.color = color
        self.increment = increment
        self.time = self.t.convert_to_int(
            self.t.convert_to_string(self.hr, self.min, self.sec))
        self.total_seconds = (hr * 3600) + (min * 60) + (sec)

        if self.total_seconds >= 300:
            self.low_time = int(round(0.1 * self.total_seconds))
        if self.total_seconds <= 30:
            self.low_time = 5
        else:
            self.low_time = 20
        self.GUI()

    def GUI(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.lbl = QLabel(self, text=self.t.convert_to_string(
            self.hr, self.min, self.sec))
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.f = QFont("Courier", 100)
        self.f.setBold(True)
        self.lbl.setFont(self.f)
        self.lbl.setFixedSize(len(self.lbl.text()) * 75, 150)

        if self.color == 'W':
            self.lbl.setStyleSheet("color: black; background-color: white;")

        elif self.color == 'B':
            self.lbl.setStyleSheet("color: white; background-color: black;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(self.total_seconds * 100)
        self.progress_bar.setValue(self.total_seconds * 100)
        s = QStyleFactory.create('Fusion')
        self.progress_bar.setStyle(s)

        self.progress_bar.setFixedSize(600, 20)
        self.progress_bar.move(0, 155)

    def decrease(self):
        self.decrease_progress_bar()

        def func():
            self.total_seconds -= 1
            self.time = self.t.subtract_1(self.lbl.text())
            if self.total_seconds == self.low_time:
                self.low_time_warning()
            self.lbl.setText(self.t.convert_to_string(
                self.time['H'], self.time['M'], self.time['S']))
            if self.time['H'] == 0 and self.time['M'] == 0 and self.time['S'] == 0:
                self.stop()
                self.lbl.setStyleSheet(
                    f"{self.lbl.styleSheet()} background-color: red; color: white;")
                self.progress_bar.setValue(0)

                threading.Thread(target=self.play_sound).start()

        self.timer = QTimer(self, timeout=func)
        self.timer.start(1000)
        self.flag = True

    def decrease_progress_bar(self):
        self.progress_bar.setValue((self.total_seconds) * 100)

        def run():
            if self.progress_bar.maximum() < self.total_seconds * 100:
                return
            v = self.progress_bar.value()
            v = v - 1
            self.progress_bar.setValue(v)
            QApplication.processEvents()
        self.ptimer = QTimer(self, timeout=run, interval=10)
        self.ptimer.start()

    def stop(self):
        self.timer.stop()
        self.ptimer.stop()

    def highlight(self):
        self.lbl.setStyleSheet(
            f'{self.lbl.styleSheet()} border: 5px solid lime;')

    def increment_(self):
        self.total_seconds += self.increment
        time = self.t.add_increment(self.lbl.text(), self.increment)
        self.lbl.setText(self.t.convert_to_string(
            time['H'], time['M'], time['S']))
        if self.progress_bar.value() + (self.increment * 100) >= self.progress_bar.maximum():
            self.progress_bar.setValue(self.progress_bar.maximum())
        else:
            self.progress_bar.setValue(
                self.progress_bar.value() + (self.increment * 100))

    def unhighlight(self):
        self.lbl.setStyleSheet(f"{self.lbl.styleSheet()} border: 0px;")

    def change_time(self, hr, min, sec, increment):
        try:
            self.timer.stop()
            self.ptimer.stop()
        except:
            pass
        self.total_seconds = (hr * 3600) + (min * 60) + (sec)
        if self.total_seconds == 0:
            self.total_seconds = 1
            self.increment = 0
            self.lbl.setText('00:00:01')
        else:
            self.increment = increment
            self.lbl.setText(self.t.convert_to_string(hr, min, sec))
            self.lbl.setFixedSize(len(self.lbl.text()) * 75, 150)

        self.progress_bar.setMaximum(self.total_seconds * 100)
        self.progress_bar.setValue(self.total_seconds * 100)
        if self.total_seconds >= 300:
            self.low_time = int(round(0.1 * self.total_seconds))
        if self.total_seconds <= 30:
            self.low_time = 5
        else:
            self.low_time = 20

    def play_sound(self):
        playsound(f'{os.getcwd()}/time_out.mp3'.replace(" ", "%20"))

    def low_time_warning(self):
        self.counter = 0
        threading.Thread(target=functools.partial(lambda: playsound(
            f'{os.getcwd()}/low_time.mp3'.replace(" ", "%20")))).start()

        def f():
            if self.counter > 11:
                self.s.stop()
                return
            self.counter += 1
            if self.flag:
                self.lbl.setStyleSheet(
                    f'{self.lbl.styleSheet()} background-color: yellow; color: black;')
                self.flag = False

            else:
                if self.color == 'W':
                    self.lbl.setStyleSheet(
                        f'{self.lbl.styleSheet()} background-color: white; color: black;')
                else:
                    self.lbl.setStyleSheet(
                        f'{self.lbl.styleSheet()} background-color: black; color: white;')
                self.flag = True
            QApplication.processEvents()

        self.s = QTimer(self, interval=250, timeout=f)
        self.s.start()


...
...
...
...
...
...

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.TIME_CONTROL = [10, 0]
        self.setWindowTitle("Chess Clock")
        self.setFixedSize(1300, 700)
        self.current_move = 'W'
        self.GUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.SWITCH()
        elif event.text() == 'P' or event.text() == 'p':
            self.PAUSE()
        elif event.text() == 'S' or event.text() == 's':
            self.START()
        elif event.text() == 'I' or event.text() == 'i':
            self.info()

    def GUI(self):
        self.layout = QGridLayout(self)
        self.font = QFont("Courier", 48)
        self.wclock = Clock(color='W', hr=0, min=10, sec=0, increment=5)
        self.layout.addWidget(self.wclock, 0, 0)
        self.bclock = Clock(color='B', hr=0, min=10, sec=0, increment=5)
        self.layout.addWidget(self.bclock, 0, 1)

        self.frm = QFrame(self)
        self.frm.setFixedSize(800, 500)
        self.l = QGridLayout(self.frm)
        self.frm.setLayout(self.l)

        self.start = QPushButton(self, text='START')
        self.start.setStyleSheet("""
            border-radius: 10px;
            background-color: green;
            color: white;
        """)
        self.start.setFixedSize(300, 100)
        self.start.setFont(self.font)
        self.start.clicked.connect(self.START)
        self.start.move(50, 200)

        self.switch = QPushButton(self, text='SWITCH')
        self.switch.setStyleSheet("""
            border-radius: 10px;
            background-color: #00b0ff;
            color: white;
        """)
        self.switch.setFixedSize(300, 100)
        self.switch.setFont(self.font)
        self.switch.clicked.connect(self.SWITCH)
        self.switch.move(50, 350)

        self.pause = QPushButton(self, text='PAUSE')
        self.pause.setStyleSheet("""
            border-radius: 10px;
            background-color: gray;
            color: white;
        """)
        self.pause.setFixedSize(300, 100)
        self.pause.setFont(self.font)
        self.pause.clicked.connect(self.PAUSE)
        self.pause.move(50, 500)

        ...
        ...
        ...
        ...
        ...

        self.f = QFrame(self)
        self.f.setFixedSize(800, 500)
        self.frm_layout = QGridLayout(self.f)
        self.f.setLayout(self.frm_layout)

        self.time_controls = {
            0: ['1+0', '2+1', '3+0', '3+2'],
            1: ['5+0', '5+3', '10+0', '10+5'],
            2: ['15+10', '30+0', '30+20', 'Custom'],
        }

        def create_button(text, row, column):
            btn = QPushButton(self, text=text)
            btn.setFixedSize(125, 125)
            btn.setFont(QFont('Courier', 24))
            btn.clicked.connect(lambda: self.get_times(text))
            btn.setStyleSheet("""
            QPushButton {
            border-radius: 10px;
            background-color: white;
            color: black;
            font-weight: bold;
            }
            """)
            self.frm_layout.addWidget(btn, row, column)

        for t in self.time_controls[0]:
            create_button(t, 0, int(self.time_controls[0].index(t)))

        for t in self.time_controls[1]:
            create_button(t, 1, int(self.time_controls[1].index(t)))

        for t in self.time_controls[2]:
            create_button(t, 2, int(self.time_controls[2].index(t)))

        self.frm.move(400, 175)
        self.f.move(400, 175)

        self.infobtn = QPushButton(self, text='INFO')
        self.infobtn.setStyleSheet("""
            background-color: #00b0ff;
            color: white;
            border-radius: 10px;
            font-family: Courier;
            font-size: 14pt;
            font-weightL bold;
        """)
        self.infobtn.move(1180, 640)
        self.infobtn.clicked.connect(self.info)
        ...
        ...
        ...

    def info(self):
        d = QDialog()
        d.setFixedSize(700, 700)
        with open('README.txt', 'r') as file:
            lbl = QLabel(d, text=file.read())
            lbl.setFont(QFont('Courier New', 14))
        l = QVBoxLayout(d)
        d.setLayout(l)
        s = QScrollArea(d)
        s.setFixedSize(650, 750)
        lbl.setWordWrap(True)
        s.setWidget(lbl)
        l.addWidget(s)
        d.exec()

    def get_times(self, time_control):
        if time_control != 'Custom':
            time_control = time_control.split("+")
            time_control[0] = int(time_control[0])
            time_control[1] = int(time_control[1])
            self.TIME_CONTROL = time_control
            self.change_time()
        else:
            self.time_dlg()

    def START(self):
        if self.start.text() == 'START':
            self.start.setText('RESET')
            self.wclock.decrease()
            self.wclock.highlight()

        else:
            self.wclock.highlight()
            self.bclock.unhighlight()
            self.wclock.lbl.setStyleSheet(
                f"{self.wclock.lbl.styleSheet()} background-color: white; color: black;")

            self.bclock.lbl.setStyleSheet((
                f"{self.bclock.lbl.styleSheet()} background-color: black; color: white;"))

            self.change_time()
            self.start.setText('START')

    def SWITCH(self):
        if (self.start.text() == 'START') or (self.wclock.total_seconds == 0) or (self.bclock.total_seconds == 0):
            return
        if self.current_move == 'W':
            self.wclock.stop()
            self.wclock.increment_()
            self.bclock.decrease()
            self.bclock.highlight()
            self.wclock.unhighlight()
            self.current_move = 'B'

        elif self.current_move == 'B':
            self.bclock.stop()
            self.bclock.increment_()
            self.wclock.decrease()
            self.wclock.highlight()
            self.bclock.unhighlight()
            self.current_move = 'W'

    def PAUSE(self):
        if (self.start.text() == 'START') or (self.wclock.total_seconds == 0) or (self.bclock.total_seconds == 0):
            return
        if self.pause.text() == 'PAUSE':
            try:
                self.wclock.stop()
                self.bclock.stop()
            except:
                pass

            self.pause.setText('RESUME')
        else:
            if self.current_move == 'W':
                self.wclock.decrease()

            else:
                self.bclock.decrease()
            self.pause.setText('PAUSE')

    def change_time(self):
        self.start.setText('START')
        self.pause.setText('PAUSE')
        self.wclock.unhighlight()
        self.bclock.unhighlight()
        self.wclock.change_time(
            hr=0, min=self.TIME_CONTROL[0], sec=0, increment=self.TIME_CONTROL[1])
        self.bclock.change_time(
            hr=0, min=self.TIME_CONTROL[0], sec=0, increment=self.TIME_CONTROL[1])
        self.wclock.lbl.setStyleSheet(
            f"{self.wclock.lbl.styleSheet()} background-color: white; color: black;")

        self.bclock.lbl.setStyleSheet((
            f"{self.bclock.lbl.styleSheet()} background-color: black; color: white;"))

    def check_for_new_time(self):
        time1 = self.TIME_CONTROL
        while True:
            if self.TIME_CONTROL != time1:
                self.change_time()
                time1 = self.TIME_CONTROL
    ...
    ...
    ...
    ...
    ...
    ...

    def time_dlg(self):
        self.dlg = QDialog()
        self.pause.setText('PAUSE')
        self.PAUSE()

        def DONE():
            n = []
            for widget in self.dlg.children():
                try:
                    n.append(int(widget.text()))
                except:
                    pass
            self.WHITE['H'] = n[0]
            self.WHITE['M'] = n[1]
            self.WHITE['S'] = n[2]
            self.WHITE['INC'] = n[3]

            self.BLACK['H'] = n[4]
            self.BLACK['M'] = n[5]
            self.BLACK['S'] = n[6]
            self.BLACK['INC'] = n[7]

            self.dlg.close()
            self.wclock.change_time(
                hr=self.WHITE['H'], min=self.WHITE['M'], sec=self.WHITE['S'], increment=self.WHITE['INC'])
            self.bclock.change_time(
                hr=self.BLACK['H'], min=self.BLACK['M'], sec=self.BLACK['S'], increment=self.BLACK['INC'])
            self.wclock.highlight()
            self.bclock.unhighlight()
            self.start.setText('START')
            self.pause.setText('PAUSE')
            self.switch.setText('SWITCH')

        def EXIT():
            self.dlg.close()

        self.dlg.setWindowTitle("Custom Time Control")
        self.dlg.setFixedSize(700, 500)
        f = QFont('Courier', 22)
        f.setBold(True)
        self.dlg.setFont(f)

        self.WHITE = {
            'H': 0,
            'M': 0,
            'S': 0,
            'INC': 0,
        }

        self.BLACK = {
            'H': 0,
            'M': 0,
            'S': 0,
            'INC': 0,
        }
        ...

        self.dlglayout = QGridLayout()
        self.dlg.setLayout(self.dlglayout)
        for lbltext in ['White Time Control (HR/MIN/SEC):', 'White Increment (Seconds):', 'Black Time Control (HR/MIN/SEC):', 'Black Increment (Seconds):']:
            self.dlglayout.addWidget(QLabel(self, text=lbltext), [
                'White Time Control (HR/MIN/SEC):', 'White Increment (Seconds):', 'Black Time Control (HR/MIN/SEC):', 'Black Increment (Seconds):'].index(lbltext), 0)
        self.lineEdits = {
            'WhiteHR': (0, 1),
            'WhiteMIN': (0, 2),
            'WhiteSEC': (0, 3),
            'WhiteINC': (1, 1),

            'BlackHR': (2, 1),
            'BlackMIN': (2, 2),
            'BlackSEC': (2, 3),
            'BlackINC': (3, 1),
        }

        for name, coords in self.lineEdits.items():
            s = QSpinBox(self)
            if name == 'WhiteINC' or name == 'BlackINC':
                s.setMaximum(1800)
            else:
                s.setMaximum(59)
            s.setAlignment(QtCore.Qt.AlignCenter)
            s.setFixedSize(60, 30)
            f = QFont('Courier', 16)
            f.setBold(False)
            s.setFont(f)
            self.dlglayout.addWidget(s, coords[0], coords[1])

        self.done = QPushButton(self.dlg, text='DONE')
        self.done.setStyleSheet(
            """
            border-radius: 10px;
            background-color: #00b0ff;
            color: white;
            font-family: Courier;
            font-size: 24pt;
            font-weight: bold;
        """)
        self.done.setFixedSize(150, 40)
        self.done.move(540, 450)
        self.done.clicked.connect(DONE)

        self.exit = QPushButton(self.dlg, text='EXIT')
        self.exit.setStyleSheet(
            """
            border-radius: 10px;
            background-color: #CD5D5C;
            color: white;
            font-family: Courier;
            font-size: 24pt;
            font-weight: bold;
        """)
        self.exit.setFixedSize(150, 40)
        self.exit.move(360, 450)
        self.exit.clicked.connect(EXIT)

        self.dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Macintosh')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

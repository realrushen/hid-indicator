import itertools
import logging
import sys
from typing import List

from PyQt5.QtCore import QSize, Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QMainWindow, QGridLayout, QApplication, QPushButton

from xkeys import open_xkeys, read_xkeys, device_connected

LOGGING_LEVEL = logging.INFO

BUTTON_IDS = itertools.chain(range(0, 6), range(8, 14), range(16, 22), range(24, 30))

SET_RED_COLOR = [0, 181, 0, 1] + [0] * 32  # bank 1
SET_BLUE_COLOR = [0, 181, 32, 1] + [0] * 32  # bank 2
TURN_OFF_BACKLIGHT = [0, 181, 0, 0] + [0] * 32
MESSAGES = {
    'Red': SET_RED_COLOR,
    'Blue': SET_BLUE_COLOR,
    'Off': TURN_OFF_BACKLIGHT,
}

logger = logging.getLogger(__name__)


class Button(QPushButton):
    backlight_change = pyqtSignal(list)

    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(QSize(40, 40))  # button size
        self.setText(str(self.index))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu()
        action_red = QAction('Red', self)
        action_red.triggered.connect(lambda: self.set_color('Red'))
        action_blue = QAction('Blue', self)
        action_blue.triggered.connect(lambda: self.set_color('Blue'))
        action_off = QAction('Off', self)
        action_off.triggered.connect(lambda: self.set_color('Off'))
        menu.addAction(action_red)
        menu.addAction(action_blue)
        menu.addAction(action_off)
        menu.exec_(self.mapToGlobal(pos))

    @pyqtSlot(str)
    def set_color(self, color):
        message: bytearray = MESSAGES[color]
        message[2] += self.index
        self.backlight_change.emit(message)


# Define main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buttons = [Button(index, parent=self) for index in BUTTON_IDS]

        self.device = None

        self.setup_ui()
        self.setup_timers()

    def setup_timers(self):
        self.open_device_timer = QTimer(self)
        self.open_device_timer.setInterval(2000)
        self.open_device_timer.timeout.connect(self.open_device)
        self.open_device_timer.start()

        self.receive_report_timer = QTimer(self)
        self.receive_report_timer.setInterval(100)
        self.receive_report_timer.timeout.connect(self.receive_report)

    def setup_ui(self):
        self.setWindowTitle("X-keys XK-24 Test Program")
        self.setCentralWidget(QWidget())
        grid_layout = QGridLayout(self.centralWidget())
        for i, button in enumerate(self.buttons):
            row = i % 6
            col = i // 6
            button.backlight_change.connect(self.send_report)
            grid_layout.addWidget(button, row, col)

    def update_buttons(self, button_states: List[int]):
        for button, state in zip(self.buttons, button_states):
            button_pressed = (state != 0)

            if button_pressed:  # simulate button press
                button.setDown(True)
            else:
                button.setDown(False)

    def receive_report(self):
        button_states = read_xkeys(self.device)
        if button_states:
            self.update_buttons(button_states)

    def send_report(self, message: List[int]):
        if device_connected():
            try:
                self.device.write(message)
            except IOError as ex:
                print(ex)

    def clean_up(self):
        if device_connected():
            self.device.close()
            self.device = None

    def open_device(self):
        logger.info('serching for device')
        if device_connected():
            device = open_xkeys()
            if device:
                logger.info('device found %s', device)
                self.device = device
                self.receive_report_timer.start()
                self.open_device_timer.stop()


def main():
    logging.basicConfig(level=LOGGING_LEVEL)

    app = QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.clean_up)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

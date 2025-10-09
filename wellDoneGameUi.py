from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import os

SOURCE_PATH = 'D:/default/2026/scripts/wellDoneGame/source_image'

class GameMenu(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        self.layout = QtWidgets.QVBoxLayout(self)

        self.bg = QtWidgets.QLabel(self)
        self.bg.setPixmap(QtGui.QPixmap(f'{SOURCE_PATH}/image/background.gif'))
        self.bg.setScaledContents(True)
        self.bg.setGeometry(0, 0, 1200, 700)

        self.menuLayout = QtWidgets.QVBoxLayout()
        self.menuLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.menuLayout.setContentsMargins(50, 0, 0, 0)

        self.event = QtWidgets.QLabel()
        self.event.setPixmap(QtGui.QPixmap(f'{SOURCE_PATH}/image/event.jpg'))
        self.event.setScaledContents(True)
        self.event.setFixedSize(400, 200)
        self.menuLayout.addWidget(self.event)

        self.startButton = QtWidgets.QPushButton('START')
        self.startButton.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))

        self.howtoplayButton = QtWidgets.QPushButton('HOW TO PLAY')
        self.howtoplayButton.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))

        self.exitButton = QtWidgets.QPushButton('EXIT')
        self.exitButton.clicked.connect(self.close_main_window)

        for b in [self.startButton, self.howtoplayButton, self.exitButton]:
            b.setFixedWidth(200)
            self.menuLayout.addWidget(b)

        self.layout.addLayout(self.menuLayout)

    def close_main_window(self):
        main_window = self.window()
        if main_window:
            main_window.hide()
            main_window.deleteLater()

class HowToPlayPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        self.backButton = QtWidgets.QPushButton('←')
        self.backButton.setFixedSize(80, 60)
        self.backButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.backButton.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        self.imageLabel = QtWidgets.QLabel()
        self.img_path = f'{SOURCE_PATH}/image/event.jpg'
        self.imageLabel.setPixmap(QtGui.QPixmap(self.img_path))
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setFixedSize(1200, 700)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.backButton, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.imageLabel, alignment=QtCore.Qt.AlignCenter)


class Ingame(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        self.bg = QtWidgets.QLabel("Game is Running...", self)
        self.bg.setAlignment(QtCore.Qt.AlignCenter)

        self.bg.setGeometry(0, 0, 1200, 700)

        self.pauseButton = QtWidgets.QPushButton('⏸️', self)
        self.pauseButton.setGeometry(20, 20, 60, 40)

        self.pauseButton.raise_()
        self.pauseButton.clicked.connect(self.show_pause_menu)

    def resizeEvent(self, event):
        self.bg.setGeometry(self.rect())
        super().resizeEvent(event)

    def show_pause_menu(self):
        pause_popup = PauseOverlay(self)
        pause_popup.resumeClicked.connect(lambda: print("Resume Game"))
        pause_popup.quitClicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        pause_popup.show()

class PauseOverlay(QtWidgets.QWidget):
    resumeClicked = QtCore.Signal()
    quitClicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(parent.geometry())

        self.bg = QtWidgets.QFrame(self)
        self.bg.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 10px;")

        layout = QtWidgets.QVBoxLayout(self.bg)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(15)

        self.resume_btn = QtWidgets.QPushButton("RESUME")
        self.quit_btn = QtWidgets.QPushButton("QUIT")

        for b in [self.resume_btn, self.quit_btn]:
            b.setFixedSize(200, 50)

        layout.addWidget(self.resume_btn)
        layout.addWidget(self.quit_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.bg)

        self.resume_btn.clicked.connect(self._resume)
        self.quit_btn.clicked.connect(self._quit)

    def _resume(self):
        self.resumeClicked.emit()
        self.close()

    def _quit(self):
        self.quitClicked.emit()
        self.close()

    def resizeEvent(self, event):
        self.bg.setGeometry(self.rect())
        super().resizeEvent(event)

class WellDoneGame(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Well Done! 🧑‍🍳")
        self.resize(1200, 700)

        self.stacked = QtWidgets.QStackedWidget()
        self.page1 = GameMenu(self.stacked)
        self.page2 = HowToPlayPage(self.stacked)
        self.page3 = Ingame(self.stacked)

        self.stacked.addWidget(self.page1)
        self.stacked.addWidget(self.page2)
        self.stacked.addWidget(self.page3)

        self.setCentralWidget(self.stacked)

def run():
    global ui
    try:
        ui.close()
        ui.deleteLater()
    except:
        pass
    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = WellDoneGame(parent=ptr)
    ui.show()
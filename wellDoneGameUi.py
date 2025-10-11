from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import importlib
import os
import time

from . import wellDoneGameUtil as wdutil
importlib.reload(wdutil)

SOURCE_PATH = wdutil.SOURCE_PATH


# 🏠 เมนูหลัก
class GameMenu(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        layout = QtWidgets.QVBoxLayout(self)
        bg = QtWidgets.QLabel(self)
        bg.setPixmap(QtGui.QPixmap(f'{SOURCE_PATH}/image/background.gif'))
        bg.setScaledContents(True)
        bg.setGeometry(0, 0, 1200, 700)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        vbox.setContentsMargins(50, 0, 0, 0)

        event = QtWidgets.QLabel()
        event.setPixmap(QtGui.QPixmap(f'{SOURCE_PATH}/image/event.jpg'))
        event.setScaledContents(True)
        event.setFixedSize(400, 200)
        vbox.addWidget(event)

        def make_btn(name, color="#F5F5F0", click=None):
            btn = QtWidgets.QPushButton(name)
            btn.setFixedWidth(200)
            btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {color};
                    color: #4B352A;
                    border-radius: 10px;
                    font-size: 16px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:pressed {{ background-color: #4B352A; color: white; }}
            ''')
            if click:
                btn.clicked.connect(click)
            return btn

        vbox.addWidget(make_btn("START", click=lambda: stacked_widget.setCurrentIndex(2)))
        vbox.addWidget(make_btn("HOW TO PLAY", click=lambda: stacked_widget.setCurrentIndex(1)))
        vbox.addWidget(make_btn("EXIT", click=self.close_main_window))
        layout.addLayout(vbox)

    def close_main_window(self):
        main_window = self.window()
        if main_window:
            main_window.hide()
            main_window.deleteLater()


# 📘 หน้าคู่มือ
class HowToPlayPage(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        layout = QtWidgets.QHBoxLayout(self)
        back = QtWidgets.QPushButton("⬅️")
        back.setFixedSize(80, 60)
        back.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        img = QtWidgets.QLabel()
        img.setPixmap(QtGui.QPixmap(f"{SOURCE_PATH}/image/event.jpg"))
        img.setScaledContents(True)
        img.setFixedSize(1200, 700)
        layout.addWidget(back, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(img, alignment=QtCore.Qt.AlignCenter)


# 🕹️ หน้าเล่นเกม
class Ingame(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        layout = QtWidgets.QHBoxLayout(self)

        # Scene + View
        self.scene = QtWidgets.QGraphicsScene(0, 0, 800, 600)
        self.scene.setBackgroundBrush(QtGui.QColor("#333"))

        # 👨‍🍳 2 Players
        self.chefs = {
            wdutil.ChefItem("P1", 100, 300, wdutil.get_img("chef1.png")): {
                "up": QtCore.Qt.Key_W,
                "down": QtCore.Qt.Key_S,
                "left": QtCore.Qt.Key_A,
                "right": QtCore.Qt.Key_D
            },
            wdutil.ChefItem("P2", 600, 300, wdutil.get_img("chef2.png")): {
                "up": QtCore.Qt.Key_I,
                "down": QtCore.Qt.Key_K,
                "left": QtCore.Qt.Key_J,
                "right": QtCore.Qt.Key_L
            }
        }

        for c in self.chefs.keys():
            self.scene.addItem(c)

        # 🔥 Stations
        self.stations = [
            wdutil.StationItem("เตา", 100, 500, wdutil.get_img("stove.png")),
            wdutil.StationItem("เขียง", 300, 500, wdutil.get_img("cutting_board.png")),
            wdutil.StationItem("เสิร์ฟ", 500, 500, wdutil.get_img("serve.png")),
            wdutil.StationItem("จุดหยิบ", 700, 100, wdutil.get_img("pickup.png")),
        ]
        for s in self.stations:
            self.scene.addItem(s)

        # View
        self.view = GameView(self.scene, self.chefs)
        layout.addWidget(self.view, 4)

        # Sidebar
        side = QtWidgets.QVBoxLayout()
        self.timer_label = QtWidgets.QLabel("⏱️ 0s")
        self.score_label = QtWidgets.QLabel("⭐ Score: 0")
        self.inv_label = QtWidgets.QLabel("🧺 Inventory:")
        side.addWidget(self.timer_label)
        side.addWidget(self.score_label)
        side.addWidget(self.inv_label)
        side.addStretch()
        layout.addLayout(side, 1)

        # Timer
        self.start_time = time.time()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(50)

        self.setLayout(layout)

    def update_game(self):
        self.view.update_movement()
        self.timer_label.setText(f"⏱️ {int(time.time() - self.start_time)}s")


# 🎮 ควบคุมตัวละคร
class GameView(QtWidgets.QGraphicsView):
    def __init__(self, scene, chefs):
        super().__init__(scene)
        self.chefs = chefs
        self.keys_pressed = set()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def keyPressEvent(self, e):
        self.keys_pressed.add(e.key())

    def keyReleaseEvent(self, e):
        if e.key() in self.keys_pressed:
            self.keys_pressed.remove(e.key())

    def update_movement(self):
        for chef, controls in self.chefs.items():
            dx = dy = 0
            if controls["up"] in self.keys_pressed: dy -= chef.speed
            if controls["down"] in self.keys_pressed: dy += chef.speed
            if controls["left"] in self.keys_pressed: dx -= chef.speed
            if controls["right"] in self.keys_pressed: dx += chef.speed

            if dx or dy:
                chef.setPos(
                    max(0, min(chef.x() + dx, 760)),
                    max(0, min(chef.y() + dy, 560))
                )


# 🧩 รวมทุกหน้า
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
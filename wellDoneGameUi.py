from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import importlib
import sys, os
import time
import random

# Support running as a package (relative import) or as a standalone script
try:
    from . import wellDoneGameUtil as wdutil
except Exception:
    import wellDoneGameUtil as wdutil
try:
    importlib.reload(wdutil)
except Exception:
    pass

SOURCE_PATH = os.path.join(os.path.dirname(__file__), "source_image", "image")

class GameMenu(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.bg = QtWidgets.QLabel(self)
        self.bg.setPixmap(QtGui.QPixmap(f"{SOURCE_PATH}/background.png"))
        self.bg.setScaledContents(True)
        self.bg.lower()

        self.menuLayout = QtWidgets.QVBoxLayout()
        self.menuLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.menuLayout.setContentsMargins(75, 90, 0, 0)

        self.startButton = QtWidgets.QPushButton('START')
        # ให้เรียกเมธอด start_new_game เพื่อรีเซ็ตสถานะเกมก่อนเปลี่ยนหน้า
        self.startButton.clicked.connect(self.start_new_game)
        self.startButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(216, 110, 14, 0);
                color: #7f7b71;
                border-radius: 2px;
                font-size: 40px;
                font-family: "Showcard Gothic";
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(216, 110, 14, 180);
                color: #e1e8e4;
            }
            QPushButton:pressed {
                background-color: rgba(75, 53, 42, 255);
                color: white;
            }
        """)

        self.howtoplayButton = QtWidgets.QPushButton('HOW TO PLAY')
        self.howtoplayButton.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.howtoplayButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(216, 110, 14, 0);
                color: #7f7b71;
                border-radius: 2px;
                font-size: 22px;
                font-family: "Showcard Gothic";
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(216, 110, 14, 180);
                color: #e1e8e4;
            }
            QPushButton:pressed {
                background-color: rgba(75, 53, 42, 255);
                color: white;
            }
        """)


        self.exitButton = QtWidgets.QPushButton('EXIT')
        self.exitButton.clicked.connect(self.close_main_window)
        self.exitButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(216, 110, 14, 0);
                color: #7f7b71;
                border-radius: 2px;
                font-size: 28px;
                font-family: "Showcard Gothic";
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(216, 110, 14, 180);
                color: #e1e8e4;
            }
            QPushButton:pressed {
                background-color: rgba(75, 53, 42, 255);
                color: white;
            }
        """)


        for b in [self.startButton, self.howtoplayButton, self.exitButton]:
            b.setFixedWidth(300)
            self.menuLayout.addWidget(b)

        self.layout.addLayout(self.menuLayout)

    def start_new_game(self):
        # 🔹 เปลี่ยนหน้าไป GamePage
        # ใช้ self.stacked_widget (ไม่ใช่ stacked_widget ที่ไม่อยู่ใน scope)
        try:
            game_page = self.stacked_widget.widget(2)  # ดึง GamePage ออกมา
            if game_page is not None and hasattr(game_page, "restart_game"):
                game_page.restart_game()
        except Exception as e:
            print("❌ Error restarting game:", e)

        # สุดท้ายเปลี่ยนไปหน้าเกม
        try:
            self.stacked_widget.setCurrentIndex(2)
        except Exception:
            pass

    def resizeEvent(self, event):
        if self.bg and self.bg.pixmap():
            self.bg.setGeometry(self.rect()) 
        super().resizeEvent(event)


    def close_main_window(self):
        main_window = self.window()
        if main_window:
            main_window.hide()
            main_window.deleteLater()


class HowToPlayPage1(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        # ==== พื้นหลัง ====
        self.bg_base = QtWidgets.QLabel(self)
        bg_base_path = os.path.join(SOURCE_PATH, "Bg_base.png")
        if os.path.exists(bg_base_path):
            self.bg_base.setPixmap(QtGui.QPixmap(bg_base_path))
        self.bg_base.setScaledContents(True)

        self.bg = QtWidgets.QLabel(self)
        bg_path = os.path.join(SOURCE_PATH, "Howtoplay1.png")
        if os.path.exists(bg_path):
            self.bg.setPixmap(QtGui.QPixmap(bg_path))
        self.bg.setScaledContents(True)

        # ==== ปุ่ม ====
        back_icon_path = os.path.join(SOURCE_PATH, "back_icon.png")
        self.btn_back = ImageButton(back_icon_path, size=(200, 100))
        self.btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        home_icon_path = os.path.join(SOURCE_PATH, "home_icon.png")
        self.btn_home = ImageButton(home_icon_path, size=(200, 100))
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        next_icon_path = os.path.join(SOURCE_PATH, "next_icon.png")
        self.btn_next = ImageButton(next_icon_path, size=(200, 100))
        self.btn_next.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        # ==== Layout ====
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.btn_back, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_home, alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()

        # ==== Resize event ====
        self.resizeEvent = self._on_resize

    def _on_resize(self, event=None):
        """ให้พื้นหลังเต็มจอทุกครั้งที่ resize"""
        w, h = self.width(), self.height()
        self.bg_base.setGeometry(0, 0, w, h)
        self.bg.setGeometry(0, 0, w, h)

class HowToPlayPage2(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        # ==== พื้นหลัง ====
        self.bg_base = QtWidgets.QLabel(self)
        bg_base_path = os.path.join(SOURCE_PATH, "Bg_base.png")
        if os.path.exists(bg_base_path):
            self.bg_base.setPixmap(QtGui.QPixmap(bg_base_path))
        self.bg_base.setScaledContents(True)

        self.bg = QtWidgets.QLabel(self)
        bg_path = os.path.join(SOURCE_PATH, "Howtoplay2.png")
        if os.path.exists(bg_path):
            self.bg.setPixmap(QtGui.QPixmap(bg_path))
        self.bg.setScaledContents(True)

        # ==== ปุ่ม ====
        back_icon_path = os.path.join(SOURCE_PATH, "back_icon.png")
        self.btn_back = ImageButton(back_icon_path, size=(200, 100))
        self.btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        home_icon_path = os.path.join(SOURCE_PATH, "home_icon.png")
        self.btn_home = ImageButton(home_icon_path, size=(200, 100))
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        next_icon_path = os.path.join(SOURCE_PATH, "next_icon.png")
        self.btn_next = ImageButton(next_icon_path, size=(200, 100))
        self.btn_next.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        # ==== Layout ====
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.btn_back, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_home, alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()

        # ==== Resize event ====
        self.resizeEvent = self._on_resize

    def _on_resize(self, event=None):
        """ให้พื้นหลังเต็มจอทุกครั้งที่ resize"""
        w, h = self.width(), self.height()
        self.bg_base.setGeometry(0, 0, w, h)
        self.bg.setGeometry(0, 0, w, h)

class HowToPlayPage3(QtWidgets.QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        # ==== พื้นหลัง ====
        self.bg_base = QtWidgets.QLabel(self)
        bg_base_path = os.path.join(SOURCE_PATH, "Bg_base.png")
        if os.path.exists(bg_base_path):
            self.bg_base.setPixmap(QtGui.QPixmap(bg_base_path))
        self.bg_base.setScaledContents(True)

        self.bg = QtWidgets.QLabel(self)
        bg_path = os.path.join(SOURCE_PATH, "Howtoplay3.png")
        if os.path.exists(bg_path):
            self.bg.setPixmap(QtGui.QPixmap(bg_path))
        self.bg.setScaledContents(True)

        # ==== ปุ่ม ====
        back_icon_path = os.path.join(SOURCE_PATH, "back_icon.png")
        self.btn_back = ImageButton(back_icon_path, size=(200, 100))
        self.btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        home_icon_path = os.path.join(SOURCE_PATH, "home_icon.png")
        self.btn_home = ImageButton(home_icon_path, size=(200, 100))
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        next_icon_path = os.path.join(SOURCE_PATH, "next_icon.png")
        self.btn_next = ImageButton(next_icon_path, size=(200, 100))
        self.btn_next.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # ==== Layout ====
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.btn_back, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_home, alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        top_layout.addWidget(self.btn_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addStretch()

        # ==== Resize event ====
        self.resizeEvent = self._on_resize

    def _on_resize(self, event=None):
        """ให้พื้นหลังเต็มจอทุกครั้งที่ resize"""
        w, h = self.width(), self.height()
        self.bg_base.setGeometry(0, 0, w, h)
        self.bg.setGeometry(0, 0, w, h)

class ImageButton(QtWidgets.QPushButton):
    def __init__(self, image_path, size=(200, 100), parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(*size)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setIcon(QtGui.QIcon(image_path))
        self.setIconSize(QtCore.QSize(*size))
        self.setStyleSheet("""
            QPushButton {
                border: 3px solid transparent;
                border-radius: 10px;
                background-color: transparent;
            }
        """)

class GameWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setStyleSheet("background-color: #8BC34A;")  # สีพื้นสนาม
        self.objects = []


        # สร้างวัตถุในฉาก
        self.create_game_objects()

        # ตัวละคร (เชฟ)
        self.has_item = False
        self.current_item = None
        self.held_icon = None

        self.placed_items = []
        self.chopping_board_icons = []

        self.pot_icons = []  # เก็บ QLabel ของวัตถุดิบบน pot
        self.pot_contents = [] # ข้อมูลวัตถุดิบ

        self.obstacles = []
        wdutil._create_invisible_walls(self)

        self.chef = QtWidgets.QLabel(self)
        chef_pixmap = QtGui.QPixmap(f"{SOURCE_PATH}/chef.png")

        # ให้รองรับ transparency และไม่ขึ้นสีพื้น
        self.chef.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.chef.setStyleSheet("background: transparent;")

        self.chef.setPixmap(chef_pixmap)
        self.chef.setScaledContents(True)
        self.chef.resize(111.875, 133.33)
        self.chef.move(200, 200)
        self.chef_speed = 10


        # ตัวจับเวลาเดินอัตโนมัติ
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)
        self.pressed_keys = set()

    def create_image_object(self, x, y, w, h, image_name):
        """สร้าง QLabel ที่มีภาพ"""
        obj = QtWidgets.QLabel(self)
        obj.setGeometry(x, y, w, h)
        obj.setStyleSheet("background: transparent;")
        pix = QtGui.QPixmap(f"{SOURCE_PATH}/{image_name}")
        obj.setPixmap(pix)
        obj.setScaledContents(True)
        self.objects.append(obj)
        return obj

    def create_game_objects(self):
        # เตา (stove)
        self.pot = self.create_image_object(280, 145, 90, 106, "pot.png")
        self.pot_icons = []
        self.pot_contents = []

        self.chopping_board = self.create_image_object(427, 180, 70, 50, "chopping_board.png")
        self.chopping_board_icons = []

        # จุดเสิร์ฟ (serve)
        self.serve_station = self.create_image_object(1060, 158, 160, 229, "serve_station.png")
        self.plate_station = self.create_image_object(1065, 353, 100, 85, "plate_station.png")
        self.trash_bin = self.create_image_object(958, 172, 85, 85, "trash_bin.png")

        # โต๊ะ (table)
        self.create_image_object(150, 500, 1240, 715, "table.png")

        # วัตถุดิบ (ingredients)
        self.ingredients = []  # ✅ เก็บรายการวัตถุดิบ

        tomato = self.create_image_object(845, 463, 77, 77, "tomato.png")
        lettuce = self.create_image_object(783, 448, 85, 125, "lettuce.png")
        cucamber = self.create_image_object(900, 462, 85, 75, "cucamber.png")

        # ใส่ใน list เพื่อใช้ตรวจชน
        self.ingredients = [
            {"name": "tomato", "widget": tomato},
            {"name": "lettuce", "widget": lettuce},
            {"name": "cucamber", "widget": cucamber},
        ]


    def keyPressEvent(self, event):
        key = event.key()
        self.pressed_keys.add(key)

        # 🎯 ปุ่ม F = ใช้ทำหลายอย่าง (หยิบ, ใส่จาน, ทิ้ง, รับจาน)
        if key == QtCore.Qt.Key_F:

            # ----- 1️⃣ กรณีถืออะไรอยู่ -----
            if self.has_item:
                # ถ้าอยู่ใกล้ถังขยะ → ทิ้งของ
                if wdutil.is_near_trash(self):
                    wdutil.try_throw_item_to_trash(self)

                # ถ้าอยู่ใกล้จาน → ใส่วัตถุดิบลงจาน
                # ถ้าอยู่ใกล้ plate station → ใส่ลงจานที่ station
                elif hasattr(self, "plate_station") and wdutil.is_near_object(self.chef, self.plate_station):
                    wdutil.add_item_to_plate(self, self.current_item)
                    # ล้างของในมือ
                    self.has_item = False
                    self.current_item = None
                    if getattr(self, "held_icon", None):
                        self.held_icon.deleteLater()
                        self.held_icon = None

                elif getattr(self, "dropped_plates", None) and any(
                    wdutil.is_near_object(self.chef, plate_dict.get("label"))
                    for plate_dict in self.dropped_plates
                    if plate_dict.get("label") is not None
                ):
                    # หา plate ที่อยู่ใกล้ที่สุดและใส่ของลงไปบนจานที่พื้น
                    for plate_dict in list(self.dropped_plates):
                        plate_label = plate_dict.get("label")
                        if plate_label and wdutil.is_near_object(self.chef, plate_label):
                            wdutil.add_item_to_dropped_plate(self, plate_dict, self.current_item)
                            self.update()
                            QtWidgets.QApplication.processEvents()
                            break

                    # ล้างของในมือ
                    self.has_item = False
                    self.current_item = None
                    if getattr(self, "held_icon", None):
                        self.held_icon.deleteLater()
                        self.held_icon = None

                # ถ้าเราถือจานอยู่และถือวัตถุดิบด้วย → ใส่ลงในจานที่ถือ
                elif getattr(self, "has_plate", False):
                    wdutil.add_item_to_held_plate(self, self.current_item)
                    # ล้างของในมือ
                    self.has_item = False
                    self.current_item = None
                    if getattr(self, "held_icon", None):
                        self.held_icon.deleteLater()
                        self.held_icon = None

                # ถ้าไม่เข้าเงื่อนไขอื่น ๆ → วางของ (drop)
                else:
                    wdutil.drop_item(self)

            # ----- 2️⃣ ถ้าไม่มีวัตถุดิบ แต่ถือจานอยู่ -----
            elif getattr(self, "has_plate", False):
                # ถ้าอยู่ใกล้ถังขยะ → ทิ้งจาน
                if wdutil.is_near_trash(self):
                    wdutil.throw_plate_to_trash(self)
                # ถ้าอยู่ใกล้จุดเสิร์ฟ → เสิร์ฟจาน
                elif wdutil.try_serve_plate(self):
                    # เสิร์ฟเสร็จแล้ว ฟังก์ชันจะจัดการ state ให้
                    return
                else:
                    pass  # ยังไม่วาง (ใช้ปุ่ม G วางแทน)

            # ----- 3️⃣ ถ้าไม่มีของในมือเลย -----
            else:
                # พยายามหยิบจานก่อน (เพราะจานมี priority สูงกว่า item)
                if wdutil.try_pickup_plate(self):
                    return
                # ถ้าไม่เจอจาน → พยายามหยิบวัตถุดิบแทน
                wdutil.try_pick_item(self)

        # 🎯 ปุ่ม G = วางของ/จานบนพื้น
        elif key == QtCore.Qt.Key_G:
            if getattr(self, "has_plate", False):
                wdutil.drop_plate(self)
            elif self.has_item:
                wdutil.drop_item(self)

        # 🔪 ปุ่ม Space = ใช้ทำ action เช่น หั่นของ
        elif key == QtCore.Qt.Key_Space:
            print("space bar preesed")
            wdutil.process_space_action(self)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def update_position(self):
        dx = dy = 0
        if QtCore.Qt.Key_Left in self.pressed_keys:
            dx -= self.chef_speed
        if QtCore.Qt.Key_Right in self.pressed_keys:
            dx += self.chef_speed
        if QtCore.Qt.Key_Up in self.pressed_keys:
            dy -= self.chef_speed
        if QtCore.Qt.Key_Down in self.pressed_keys:
            dy += self.chef_speed

        if dx == 0 and dy == 0:
            return

        new_x = max(0, min(self.chef.x() + dx, self.width() - self.chef.width()))
        new_y = max(0, min(self.chef.y() + dy, self.height() - self.chef.height()))

        can_move = wdutil._can_move_to(self, new_x, new_y)

        if not can_move:
            return

        self.chef.move(new_x, new_y)

        if getattr(self, "held_icon", None):
            icon_x = new_x + (self.chef.width() - self.held_icon.width()) // 2
            icon_y = new_y - self.held_icon.height() - 5
            self.held_icon.move(icon_x, icon_y)

        if getattr(self, "has_plate", False) and hasattr(self, "held_plate"):
            wdutil.update_plate_position(self, self.chef, self.held_plate)


class Overlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        # -----------------------------
        # 🔹 พื้นหลัง pause_bg.png
        # -----------------------------
        self.bg_label = QtWidgets.QLabel(self)
        bg_path = os.path.join(SOURCE_PATH, "pause_bg.png")
        pix = QtGui.QPixmap(bg_path)
        scaled_pix = pix.scaled(600, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.bg_label.setPixmap(scaled_pix)
        self.bg_label.setScaledContents(False)
        self.bg_label.setAlignment(QtCore.Qt.AlignCenter)

        parent_w, parent_h = 1200, 675
        pix_w, pix_h = scaled_pix.width(), scaled_pix.height()
        x = (parent_w - pix_w) // 2
        y = (parent_h - pix_h) // 2
        self.bg_label.setGeometry(x, y, pix_w, pix_h)

        # -----------------------------
        # 🔹 ข้อความ
        # -----------------------------
        self.message_label = QtWidgets.QLabel("", self)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #fff7d6; /* สีครีมอบอุ่น */
                font: bold 20px 'Comic Sans MS';
                background-color: transparent;
                padding: 4px;
                border: None;
                qproperty-alignment: AlignCenter;
                text-shadow: 58px 85px 10px #1c1308; /* เงาเข้มแบบขอบการ์ตูน */
            }
        """)

        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.message_label)

        # -----------------------------
        # 🔹 ปุ่ม (เริ่มจาก Pause Mode)
        # -----------------------------
        continue_icon_path = os.path.join(SOURCE_PATH, "continue_icon.png")
        quit_icon_path = os.path.join(SOURCE_PATH, "quit_icon.png")

        self.continue_btn = ImageButton(continue_icon_path, size=(200, 100))
        self.quit_btn = ImageButton(quit_icon_path, size=(200, 100))

        self.layout.addWidget(self.continue_btn)
        self.layout.addWidget(self.quit_btn)

        # state flag
        self.is_game_over = False
        self.restart_btn = None  # จะสร้างตอน Game Over เท่านั้น

    # -----------------------------
    # 🔸 โหมด Pause
    # -----------------------------
    def set_paused(self):
        self.is_game_over = False
        self.message_label.setText("Paused")

        # ถ้ามี restart_btn จาก game over ก่อนหน้า → ลบทิ้ง
        if self.restart_btn:
            self.layout.removeWidget(self.restart_btn)
            self.restart_btn.deleteLater()
            self.restart_btn = None

        # ถ้า continue_btn ถูกลบไป (จาก game over) → สร้างกลับมา
        if not hasattr(self, "continue_btn") or self.continue_btn is None:
            continue_icon_path = os.path.join(SOURCE_PATH, "continue_icon.png")
            self.continue_btn = ImageButton(continue_icon_path, size=(200, 100))
            self.layout.insertWidget(1, self.continue_btn)

    # -----------------------------
    # 🔸 โหมด Game Over
    # -----------------------------
    def set_game_over(self, score):
        self.is_game_over = True
        self.message_label.setText(f"Game Over\nScore: {score}")

        # ลบปุ่ม continue ออก
        if self.continue_btn:
            self.layout.removeWidget(self.continue_btn)
            self.continue_btn.deleteLater()
            self.continue_btn = None

        # สร้างปุ่ม restart แทน
        if not self.restart_btn:
            restart_icon_path = os.path.join(SOURCE_PATH, "restart_icon.png")
            self.restart_btn = ImageButton(restart_icon_path, size=(200, 100))
            self.layout.insertWidget(1, self.restart_btn)

            # ✅ เชื่อมสัญญาณคลิกเข้ากับ GamePage ผ่าน parent
            try:
                parent = self.parent()
                if hasattr(parent, "_overlay_continue_clicked"):
                    self.restart_btn.clicked.connect(parent._overlay_continue_clicked)
            except Exception as e:
                print("⚠️ Cannot connect restart button:", e)

class GamePage(QtWidgets.QWidget):
    """แทน MainWindow เดิม แต่เป็น QWidget"""
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.bg_label = QtWidgets.QLabel(self)
        self.bg_label.setScaledContents(True)  # ให้ขยายเต็มพื้นที่ widget
        self.bg_pixmap = QtGui.QPixmap(f"{SOURCE_PATH}/bg_kitchen.png")
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.lower()

        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, 1200, 675)

        self.game_widget = GameWidget()
        layout.addWidget(self.game_widget)
        # ให้ GameWidget รู้จัก GamePage เพื่อให้การเสิร์ฟสามารถอัปเดต orders/score ได้
        try:
            self.game_widget.game_page = self
        except Exception:
            pass
        self.game_widget.setFocus()

        # Score / Time / Orders labels (create early so helpers can use them)
        self.score_bg = QtWidgets.QLabel(self)
        self.score_bg.setGeometry(10, 610, 80, 80)  # ตำแหน่งมุมล่างซ้าย
        self.score_bg.setStyleSheet("""
            QLabel {
                background-color: #FFD54F;        /* สีเหลืองทอง */
                border: 3px solid #E0B000;        /* ขอบสีเหลืองเข้ม */
                border-radius: 40px;              /* ครึ่งหนึ่งของขนาด เพื่อให้เป็นวงกลม */
            }
        """)

        self.score_label = QtWidgets.QLabel("0", self)
        self.score_label.setGeometry(10, 600, 80, 80) 
        self.score_label.setAlignment(QtCore.Qt.AlignCenter)
        self.score_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Showcard Gothic"; 
                font-size: 48px;
                font-weight: bold;
                text-shadow: 2px 2px 4px black;
            }
        """)

        # ====== ตัวเลขเวลาอยู่บนวงกลม ======
        self.clock_bg = QtWidgets.QLabel(self)
        self.clock_bg.setGeometry(1105, 610, 80, 80)
        self.clock_bg.setStyleSheet("""
            QLabel {
                background-color: gray;
                border-radius: 40px;
            }
        """)

        self.remaining_time = 300
        self.time_label = QtWidgets.QLabel(str(self.remaining_time), self)
        self.time_label.setGeometry(1105, 600, 80, 80)
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Showcard Gothic";
                font-size: 48px;       /* เล็กหรือใหญ่ตามต้องการ */
                font-weight: bold;
            }
        """)

        # Game clock
        self.time_label.setText(f"{self.remaining_time}")
        self.game_clock = QtCore.QTimer(self)
        self.game_clock.timeout.connect(self._tick_game_clock)
        self.game_clock.start(1000)

        # 🔹 Order Display (ใช้ภาพแทนข้อความ)
        self.order_container = QtWidgets.QWidget(self)
        self.order_container.setGeometry(0, 0, 300, 130)

        bg_path = os.path.join(os.path.dirname(__file__), "source_image", "image", "bg_order.png")
        self.order_bg = QtWidgets.QLabel(self.order_container)
        self.order_bg.setGeometry(0, 0, 300, 130)
        self.order_bg.setScaledContents(True)
        if os.path.exists(bg_path):
            self.order_bg.setPixmap(QtGui.QPixmap(bg_path))

        self.order_layout = QtWidgets.QHBoxLayout(self.order_container)
        self.order_layout.setContentsMargins(20, 0, 0, 0)
        self.order_layout.setSpacing(2)

        # โหลด order จาก recipe dict
        try:
            files = os.listdir(os.path.join(os.path.dirname(__file__), "source_image", "image"))
            combos = [f[len("order_"):-4] for f in files if f.startswith("order_") and f.lower().endswith('.png')]
        except Exception:
            combos = []
        if not combos:
            combos = ["tomato_soup", "delux_salad", "lettuce_salad","tomato_lettuce_salad"]

        self.orders = [random.choice(combos) for _ in range(3)]
        self._refresh_orders_images()

        self.game_widget.current_orders = self.orders

        # ปุ่ม Pause
        self.pause_icon_path = os.path.join(SOURCE_PATH, "pause_icon.png")
        self.pause_btn = ImageButton(self.pause_icon_path, size=(180, 80), parent=self)
        self.pause_btn.clicked.connect(self.show_overlay)

        # ตั้งตำแหน่งมุมขวาบน
        self.pause_btn.move(self.width() - 200, 20)  # ขยับจากขอบขวา 20px
        self.pause_btn.raise_()  # ✅ ให้อยู่บนสุด (เหนือ widget อื่น)

        # Overlay
        self.overlay = Overlay(self)
        self.overlay.setGeometry(0, 0, 1200, 675)
        self.overlay.hide()
        # connect to a handler that can decide between resume or restart
        self.overlay.continue_btn.clicked.connect(self._overlay_continue_clicked)
        self.overlay.quit_btn.clicked.connect(self.back_to_menu)

        
    def _refresh_orders_images(self):
        # ลบภาพเก่าทั้งหมดก่อน
        while self.order_layout.count():
            item = self.order_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # วาดภาพใหม่ทั้งหมด
        for order in self.orders:
            lbl = QtWidgets.QLabel()
            path = os.path.join(os.path.dirname(__file__), "source_image", "image", f"order_{order}.png")
            if os.path.exists(path):
                pix = QtGui.QPixmap(path)
            lbl.setPixmap(pix.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            self.order_layout.addWidget(lbl)

    def serve_dish_to_order(self, dish_name: str):
        if dish_name in self.orders:
            self.orders.remove(dish_name)
            # เพิ่มออเดอร์ใหม่ให้ครบ 3
            try:
                files = os.listdir(os.path.join(os.path.dirname(__file__), "source_image", "image"))
                combos = [f[len("order_"):-4] for f in files if f.startswith("order_") and f.lower().endswith('.png')]
            except Exception:
                combos = ["tomato_soup", "delux_salad", "lettuce_salad","tomato_lettuce_salad"]

            while len(self.orders) < 3:
                self.orders.append(random.choice(combos))

            self._refresh_orders_images()


    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.pause_btn.move(self.width() - 170, 0)
        super().resizeEvent(event)

    def showEvent(self, event):
        # เมื่อหน้า GamePage ปรากฎ ให้โฟกัสที่ game_widget เพื่อรับ key events (เช่น Space)
        try:
            self.game_widget.setFocus()
        except Exception:
            pass
        super().showEvent(event)

    def show_overlay(self):
        # pause game timers
        try:
            self.game_clock.stop()
        except Exception:
            pass
        try:
            self.game_widget.timer.stop()
        except Exception:
            pass
        # Set overlay to paused mode and show
        try:
            self.overlay.set_paused()
        except Exception:
            pass
        self.overlay.show()

    def hide_overlay(self):
        self.overlay.hide()
        # resume game timers
        try:
            self.game_clock.start(1000)
        except Exception:
            pass
        try:
            self.game_widget.timer.start(16)
        except Exception:
            pass

    def _tick_game_clock(self):
        self.remaining_time -= 1
        if self.remaining_time < 0:
            self.remaining_time = 0

        # แสดงตัวเลขตรง ๆ ไม่มี 'Time:'
        self.time_label.setText(str(self.remaining_time))

        if self.remaining_time <= 0:
            # time up -> show overlay and stop timers
            try:
                self.game_clock.stop()
            except Exception:
                pass
            try:
                self.game_widget.timer.stop()
            except Exception:
                pass
            # show game-over overlay with final score
            try:
                score = int(self.score_label.text())
            except Exception:
                score = 0
            try:
                self.overlay.set_game_over(score)
            except Exception:
                pass
            self.overlay.show()

    def _overlay_continue_clicked(self):
        """Called when overlay continue/restart button is clicked."""
        try:
            if getattr(self.overlay, 'is_game_over', False):
                self.restart_game()
            else:
                self.hide_overlay()
        except Exception:
            try:
                self.hide_overlay()
            except Exception:
                pass

    def restart_game(self):
        """Reset game state to allow a fresh playthrough."""
        # reset time and score
        self.remaining_time = 330
        self.time_label.setText(f"{self.remaining_time}")
        self.score_label.setText("0")

        # clear items from the game widget
        gw = self.game_widget
        try:
            for lbl in list(getattr(gw, 'placed_items', [])):
                try:
                    lbl.deleteLater()
                except Exception:
                    pass
            gw.placed_items = []
        except Exception:
            gw.placed_items = []

        try:
            for lbl in list(getattr(gw, 'pot_icons', [])):
                try:
                    lbl.deleteLater()
                except Exception:
                    pass
            gw.pot_icons = []
            gw.pot_contents = []
        except Exception:
            gw.pot_icons = []
            gw.pot_contents = []

        try:
            for lbl in list(getattr(gw, 'chopping_board_icons', [])):
                try:
                    lbl.deleteLater()
                except Exception:
                    pass
            gw.chopping_board_icons = []
        except Exception:
            gw.chopping_board_icons = []

        try:
            for pd in list(getattr(gw, 'dropped_plates', [])):
                try:
                    lab = pd.get('label')
                    if lab:
                        lab.deleteLater()
                except Exception:
                    pass
            gw.dropped_plates = []
        except Exception:
            gw.dropped_plates = []

        try:
            if getattr(gw, 'held_plate', None):
                gw.held_plate.deleteLater()
            gw.held_plate = None
        except Exception:
            gw.held_plate = None

        try:
            if getattr(gw, 'held_icon', None):
                gw.held_icon.deleteLater()
            gw.held_icon = None
        except Exception:
            gw.held_icon = None

        gw.has_item = False
        gw.current_item = None
        gw.has_plate = False
        gw.plate_items = []
        gw.station_plate_items = []
        gw.pot_icons = []

        # regenerate orders
        try:
            files = os.listdir(os.path.join(os.path.dirname(__file__), "source_image", "image"))
            # orders are represented by files named order_<name>.png
            combos = [f[len("order_"):-4] for f in files if f.startswith("order_") and f.lower().endswith('.png')]
        except Exception:
            combos = []
        if not combos:
            combos = ["tomato_soup", "delux_salad", "lettuce_salad","tomato_lettuce_salad"]
        import random
        self.orders = [random.choice(combos) for _ in range(3)]
        # Refresh order images in the UI and sync gamestate
        self._refresh_orders_images()
        try:
            self.game_widget.current_orders = self.orders
        except Exception:
            pass

        # hide overlay and restart timers
        try:
            self.overlay.set_paused()
        except Exception:
            pass
        try:
            self.overlay.hide()
        except Exception:
            pass
        try:
            self.game_clock.start(1000)
        except Exception:
            pass
        try:
            self.game_widget.timer.start(16)
        except Exception:
            pass

    def _refresh_orders_label(self):
        # display orders nicely
        disp = " | ".join(self.orders)
        self.order_label.setText(f"Orders: {disp}")

    def back_to_menu(self):
        self.overlay.hide()
        self.stacked_widget.setCurrentIndex(0)

class WellDoneGame(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Well Done! 🧑‍🍳")
        self.resize(1200, 675)

        self.stacked = QtWidgets.QStackedWidget()
        self.page1 = GameMenu(self.stacked)
        self.page2 = HowToPlayPage1(self.stacked)
        self.page3 = GamePage(self.stacked)
        self.page4 = HowToPlayPage2(self.stacked)
        self.page5 = HowToPlayPage3(self.stacked)

        self.stacked.addWidget(self.page1)
        self.stacked.addWidget(self.page2)
        self.stacked.addWidget(self.page3)
        self.stacked.addWidget(self.page4)
        self.stacked.addWidget(self.page5)
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
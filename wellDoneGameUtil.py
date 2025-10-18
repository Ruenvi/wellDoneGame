import os
from PySide6 import QtWidgets, QtCore, QtGui

SOURCE_PATH = os.path.join(os.path.dirname(__file__), "source_image")

# ------------------- การหยิบของ -------------------
def try_pick_item(game_widget, threshold=50):
    if getattr(game_widget, "has_item", False):
        print("เชฟถือของอยู่แล้ว 🧺")
        return

    chef_geom = game_widget.chef.geometry()
    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )

    found = False

    # 1️⃣ ตรวจสอบ ingredients
    for ing in getattr(game_widget, "ingredients", []):
        name = ing["name"]
        ing_widget = ing["widget"]
        ing_geom = ing_widget.geometry()
        ing_center = QtCore.QPoint(
            ing_geom.x() + ing_geom.width() // 2,
            ing_geom.y() + ing_geom.height() // 2
        )
        dx = chef_center.x() - ing_center.x()
        dy = chef_center.y() - ing_center.y()
        distance = (dx**2 + dy**2) ** 0.5
        if distance <= threshold:
            game_widget.has_item = True
            game_widget.current_item = name
            print(f"✅ หยิบวัตถุดิบ: {name}")
            show_pick_feedback(game_widget, name)
            found = True
            break

    # 2️⃣ ตรวจสอบ placed_items (บนพื้น)
    if not found and hasattr(game_widget, "placed_items"):
        for item_label in list(game_widget.placed_items):  # ใช้ list() เพื่อแก้ไขระหว่าง loop
            name = getattr(item_label, "item_name", None)
            if not name:
                continue

            item_geom = item_label.geometry()
            item_center = QtCore.QPoint(
                item_geom.x() + item_geom.width() // 2,
                item_geom.y() + item_geom.height() // 2
            )
            dx = chef_center.x() - item_center.x()
            dy = chef_center.y() - item_center.y()
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= threshold:
                game_widget.has_item = True
                game_widget.current_item = name
                print(f"✅ หยิบวัตถุดิบจากพื้น: {name}")

                show_pick_feedback(game_widget, name)

                # เอา icon ของวัตถุดิบบนพื้นออก
                item_label.deleteLater()
                game_widget.placed_items.remove(item_label)
                found = True
                break

    if not found:
        print("❌ ไม่ได้อยู่ใกล้วัตถุดิบใด ๆ")

# ------------------- icon ติดตามเชฟ -------------------
def show_pick_feedback(game_widget, item_name):
    pix_path = os.path.join(SOURCE_PATH, "image", f"{item_name}_icon.png")
    pix = QtGui.QPixmap(pix_path)
    if pix.isNull():
        return

    if getattr(game_widget, "held_icon", None):
        game_widget.held_icon.deleteLater()
        game_widget.held_icon = None

    icon_label = QtWidgets.QLabel(game_widget)
    icon_label.setPixmap(pix)
    icon_label.setScaledContents(True)
    icon_label.resize(40, 40)

    icon_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    icon_label.setStyleSheet("background: transparent;")

    icon_label.show()
    game_widget.held_icon = icon_label

    update_held_icon_position(game_widget)

def update_held_icon_position(game_widget):
    if getattr(game_widget, "held_icon", None):
        drop_x = game_widget.chef.x() + (game_widget.chef.width() - 40) // 2
        drop_y = game_widget.chef.y() - 40 - 5
        game_widget.held_icon.move(drop_x, drop_y)

# ------------------- วางของ -------------------
def drop_item(game_widget):
    if not getattr(game_widget, "has_item", False):
        return

    drop_x = game_widget.chef.x() + (game_widget.chef.width() - 40) // 2  # 40 = ขนาด icon
    drop_y = game_widget.chef.y() + game_widget.chef.height() - 10
    item_name = game_widget.current_item

    item_label = QtWidgets.QLabel(game_widget)
    pix_path = os.path.join(SOURCE_PATH, "image", f"{item_name}_icon.png")
    pix = QtGui.QPixmap(pix_path)
    item_label.setPixmap(pix)
    item_label.setScaledContents(True)
    item_label.resize(40, 40)
    item_label.move(drop_x, drop_y)

    item_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    item_label.setStyleSheet("background: transparent;")

    item_label.show()

    chef_center = QtCore.QPoint(
        game_widget.chef.x() + game_widget.chef.width() // 2,
        game_widget.chef.y() + game_widget.chef.height() // 2
    )

    # --- chopping board ---
    board_geom = game_widget.chopping_board.geometry()
    board_center = QtCore.QPoint(
        board_geom.x() + board_geom.width() // 2,
        board_geom.y() + board_geom.height() // 2
    )
    dx = chef_center.x() - board_center.x()
    dy = chef_center.y() - board_center.y()
    distance_board = (dx**2 + dy**2) ** 0.5

    if distance_board <= 50:
        game_widget.chopping_board_icons.append(item_label)
        print(f"วาง {item_name} บน chopping board")
    else:
        # --- pot ---
        pot_geom = game_widget.pot.geometry()
        pot_center = QtCore.QPoint(
            pot_geom.x() + pot_geom.width() // 2,
            pot_geom.y() + pot_geom.height() // 2
        )
        dx = chef_center.x() - pot_center.x()
        dy = chef_center.y() - pot_center.y()
        distance_pot = (dx**2 + dy**2) ** 0.5

        if distance_pot <= 50:
            game_widget.pot_icons.append(item_label)
            if not hasattr(game_widget, "pot_contents"):
                game_widget.pot_contents = []
            game_widget.pot_contents.append(item_name)
            print(f"วาง {item_name} ลง pot")

            count = game_widget.pot_contents.count(item_name)
            if count == 3:
                print(f"🎉 ต้มเสร็จ: {item_name.replace('_chopped','')}")
                for _ in range(3):
                    game_widget.pot_contents.remove(item_name)
                for icon in game_widget.pot_icons[:3]:
                    icon.deleteLater()
                    game_widget.pot_icons.remove(icon)
        else:
            print(f"วาง {item_name} บนพื้น")
            item_label.item_name = item_name 
            game_widget.placed_items.append(item_label)

    if getattr(game_widget, "held_icon", None):
        game_widget.held_icon.deleteLater()
        game_widget.held_icon = None
    game_widget.has_item = False
    game_widget.current_item = None

# ------------------- หั่น -------------------
def process_space_action(game_widget):
    for icon_label in game_widget.chopping_board_icons:
        # สมมติเราจำชื่อใน property name
        chopped_name = icon_label.property("item_name")
        if not chopped_name:
            continue
        chopped_name = f"{chopped_name}_chopped"
        pix_path = os.path.join(SOURCE_PATH, "image", f"{chopped_name}_icon.png")
        pix = QtGui.QPixmap(pix_path)
        if not pix.isNull():
            icon_label.setPixmap(pix)
            icon_label.setScaledContents(True)
            icon_label.setProperty("item_name", chopped_name)
            print(f"✅ หั่นวัตถุดิบ: {chopped_name}")

# ------------------- ทิ้งของลงถังขยะ -------------------
def try_throw_item_to_trash(game_widget, threshold=50):
    """
    เช็คว่าตัวเชฟอยู่ใกล้ถังขยะหรือไม่
    ถ้าใช่ -> ทิ้งของที่ถืออยู่ (หรือของบนพื้นใกล้ถัง)
    """
    chef_geom = game_widget.chef.geometry()
    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )

    # ต้องมีถังขยะใน game_widget
    if not hasattr(game_widget, "trash_bin"):
        print("❌ ไม่มีถังขยะในเกม")
        return

    # ตำแหน่งถังขยะ
    trash_geom = game_widget.trash_bin.geometry()
    trash_center = QtCore.QPoint(
        trash_geom.x() + trash_geom.width() // 2,
        trash_geom.y() + trash_geom.height() // 2
    )

    dx = chef_center.x() - trash_center.x()
    dy = chef_center.y() - trash_center.y()
    distance = (dx**2 + dy**2) ** 0.5

    if distance > threshold:
        print("🚫 ยังไม่อยู่ใกล้ถังขยะพอ")
        return

    # ถ้ามีของในมือ -> ทิ้ง
    if getattr(game_widget, "has_item", False):
        item_name = game_widget.current_item
        print(f"🗑️ ทิ้งของในมือ: {item_name}")
        game_widget.has_item = False
        game_widget.current_item = None

        if getattr(game_widget, "held_icon", None):
            game_widget.held_icon.deleteLater()
            game_widget.held_icon = None
        return

    # ถ้าไม่มีของในมือ -> ลองเช็คของที่อยู่บนพื้นใกล้ถัง
    if hasattr(game_widget, "placed_items"):
        for item_label in list(game_widget.placed_items):
            item_geom = item_label.geometry()
            item_center = QtCore.QPoint(
                item_geom.x() + item_geom.width() // 2,
                item_geom.y() + item_geom.height() // 2
            )
            dx = trash_center.x() - item_center.x()
            dy = trash_center.y() - item_center.y()
            dist_item = (dx**2 + dy**2) ** 0.5

            if dist_item <= threshold:
                print(f"🗑️ เก็บ {item_label.item_name} ที่พื้นทิ้งถังขยะ")
                item_label.deleteLater()
                game_widget.placed_items.remove(item_label)

    print("🧹 ทำความสะอาดเรียบร้อย!")

def add_item_to_plate(game_widget, item_name):
    """เพิ่มวัตถุดิบลงในจานและอัปเดตภาพ"""
    if not hasattr(game_widget, "plate_items"):
        game_widget.plate_items = []

    # ตรวจสอบว่าอยู่ใกล้จานไหม
    chef_center = QtCore.QPoint(
        game_widget.chef.x() + game_widget.chef.width() // 2,
        game_widget.chef.y() + game_widget.chef.height() // 2
    )
    plate_geom = game_widget.plate.geometry()
    plate_center = QtCore.QPoint(
        plate_geom.x() + plate_geom.width() // 2,
        plate_geom.y() + plate_geom.height() // 2
    )
    dx = chef_center.x() - plate_center.x()
    dy = chef_center.y() - plate_center.y()
    distance = (dx**2 + dy**2) ** 0.5

    if distance > 60:
        print("❌ ไม่ได้อยู่ใกล้จาน")
        return

    # เพิ่มของลงจาน
    game_widget.plate_items.append(item_name)
    print(f"🍽️ ใส่ {item_name} ลงจาน")

    update_plate_image(game_widget)


def update_plate_image(game_widget):
    """อัปเดตภาพในจานตามส่วนผสม"""
    items = sorted(game_widget.plate_items)

    # รวมชื่อเป็นสูตร เช่น ['lettuce', 'tomato'] → 'salad_lettuce_tomato'
    combo_name = "_".join(items)
    combo_image_name = f"plate_{combo_name}.png"

    combo_path = os.path.join(SOURCE_PATH, "image", combo_image_name)

    # ถ้าไม่มีภาพรวม ให้ fallback เป็นภาพจานว่าง
    if not os.path.exists(combo_path):
        combo_path = os.path.join(SOURCE_PATH, "image", "plate_base.png")

    pix = QtGui.QPixmap(combo_path)
    game_widget.plate.setPixmap(pix)
    game_widget.plate.setScaledContents(True)

    # ลบ icon เดิม
    if hasattr(game_widget, "plate_icons"):
        for icon in game_widget.plate_icons:
            icon.deleteLater()
    game_widget.plate_icons = []

    # แสดงไอคอนของวัตถุดิบบนจาน
    for i, item in enumerate(items):
        icon_path = os.path.join(SOURCE_PATH, "image", f"{item}_icon.png")
        if not os.path.exists(icon_path):
            continue
        icon_label = QtWidgets.QLabel(game_widget)
        icon_label.setPixmap(QtGui.QPixmap(icon_path))
        icon_label.setScaledContents(True)
        icon_label.resize(32, 32)
        icon_label.move(game_widget.plate.x() + 10 + i * 35, game_widget.plate.y() - 35)
        icon_label.setStyleSheet("background: transparent;")
        icon_label.show()
        game_widget.plate_icons.append(icon_label)
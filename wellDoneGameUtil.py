import os
from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds

try:
    from .recipe_data import RECIPE_DICT, SCORE_DICT  # type: ignore
except Exception:
    # Fallback recipe mapping: keys are frozensets of ingredient names (use chopped names where appropriate)
    RECIPE_DICT = {
        frozenset(['lettuce_chopped']): 'lettuce_salad',
        frozenset(['tomato_chopped', 'lettuce_chopped']): 'tomato_lettuce_salad',
        frozenset(['tomato_chopped', 'lettuce_chopped', 'cucamber_chopped']): 'delux_salad',
        frozenset(['tomato_soup']): 'tomato_soup',
    }
    SCORE_DICT = {
        'lettuce_salad': 5,
        'tomato_lettuce_salad': 10,
        'delux_salad': 15,
        'tomato_soup': 20,
    }

SOURCE_PATH = os.path.join(os.path.dirname(__file__), 'source_image')

# ------------------- การหยิบของ -------------------
def try_pick_item(game_widget, threshold=80):  # เพิ่มระยะการหยิบเป็น 80
    if getattr(game_widget, 'has_item', False):
        print('เชฟถือของอยู่แล้ว 🧺')
        return

    chef_geom = game_widget.chef.geometry()
    # ใช้พื้นที่จริงของเชฟในการตรวจจับ
    chef_rect = QtCore.QRect(
        chef_geom.x() - 20,  # ขยายพื้นที่การหยิบออกไปด้านข้าง
        chef_geom.y() - 10,  # ขยายพื้นที่การหยิบขึ้นด้านบน
        chef_geom.width() + 40,  # เพิ่มความกว้างของพื้นที่การหยิบ
        chef_geom.height() + 20  # เพิ่มความสูงของพื้นที่การหยิบ
    )
    
    # คำนวณจุดศูนย์กลางสำหรับการคำนวณระยะห่าง
    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )

    found = False

    # 1️⃣ ตรวจสอบ ingredients
    for ing in getattr(game_widget, 'ingredients', []):
        name = ing['name']
        ing_widget = ing['widget']
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
            pick_msg = f'หยิบ {name} ✅'
            print(pick_msg)
            game_page = getattr(game_widget, 'game_page', None)
            if game_page and hasattr(game_page, 'show_toast'):
                game_page.show_toast(pick_msg)
            show_pick_feedback(game_widget, name)
            found = True
            break

    # 2️⃣ ตรวจสอบ placed_items (บนพื้น)
    if not found and hasattr(game_widget, 'placed_items'):
        for item_label in list(game_widget.placed_items):  # ใช้ list() เพื่อแก้ไขระหว่าง loop
            name = getattr(item_label, 'item_name', None)
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
                print(f'✅ หยิบวัตถุดิบจากพื้น: {name}')

                show_pick_feedback(game_widget, name)

                # เอา icon ของวัตถุดิบบนพื้นออก
                item_label.deleteLater()
                game_widget.placed_items.remove(item_label)
                found = True
                break

    if not found and hasattr(game_widget, 'chopping_board_icons'):
        for icon_label in list(game_widget.chopping_board_icons):
            name = icon_label.property('item_name') or getattr(icon_label, 'item_name', None)
            if not name:
                continue

            icon_geom = icon_label.geometry()
            icon_center = QtCore.QPoint(
                icon_geom.x() + icon_geom.width() // 2,
                icon_geom.y() + icon_geom.height() // 2
            )
            dx = chef_center.x() - icon_center.x()
            dy = chef_center.y() - icon_center.y()
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= threshold:
                game_widget.has_item = True
                game_widget.current_item = name
                print(f'🔪 หยิบวัตถุดิบจากเขียง: {name}')

                show_pick_feedback(game_widget, name)

                # เอา icon ของวัตถุดิบบนเขียงออก
                try:
                    game_widget.chopping_board_icons.remove(icon_label)
                except ValueError:
                    pass
                icon_label.deleteLater()
                found = True
                break

    if not found and hasattr(game_widget, "pot"):
        pot_geom = game_widget.pot.geometry()
        pot_center = QtCore.QPoint(
            pot_geom.x() + pot_geom.width() // 2,
            pot_geom.y() + pot_geom.height() // 2
        )

        dx = chef_center.x() - pot_center.x()
        dy = chef_center.y() - pot_center.y()
        distance_pot = (dx ** 2 + dy ** 2) ** 0.5

        if distance_pot <= threshold:
            # ถ้ามีซุปแล้ว ต้องถือจานถึงหยิบได้
            if hasattr(game_widget, "soup_icon"):
                if getattr(game_widget, "has_plate", False):
                    # หยิบซุปใส่จาน
                    game_widget.soup_icon.deleteLater()
                    del game_widget.soup_icon

                    if hasattr(game_widget, "held_plate"):
                        game_widget.held_plate.deleteLater()
                        del game_widget.held_plate

                    plate_soup = QtWidgets.QLabel(game_widget)
                    plate_soup.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
                    soup_path = os.path.join(SOURCE_PATH, "image", "plate_tomato_soup_icon.png")
                    soup_pix = QtGui.QPixmap(soup_path)
                    plate_soup.setPixmap(soup_pix)
                    plate_soup.setScaledContents(True)
                    plate_soup.resize(64, 64)
                    plate_soup.move(game_widget.chef.x(), game_widget.chef.y() - 70)
                    plate_soup.show()

                    game_widget.held_plate = plate_soup
                    game_widget.has_plate = True
                    game_widget.has_item = True
                    game_widget.current_item = "tomato_soup"

                    show_pick_feedback(game_widget, "tomato_soup")
                    found = True
                else:
                    print("⚠️ ต้องถือจานก่อนถึงจะตักซุปได้!")

            # ถ้ายังไม่ครบ 3 ชิ้น → สามารถหยิบวัตถุดิบเป็น item เดิม
            elif getattr(game_widget, "pot_contents", []):
                # เอาไอเทมล่าสุดออกจากหม้อ
                item_name = game_widget.pot_contents.pop()
                item_label = game_widget.pot_icons.pop()
                item_label.deleteLater()

                # สร้างไอเทมในมือ
                game_widget.has_item = True
                game_widget.current_item = item_name
                show_pick_feedback(game_widget, item_name)

                # จัดเรียงไอคอนหม้อที่เหลือ
                for idx, icon in enumerate(game_widget.pot_icons):
                    icon.move(
                        pot_geom.x() + (pot_geom.width() // 2) - 32 + idx * 45,
                        pot_geom.y() - 40
                    )

                print(f"🥄 หยิบ {item_name} ออกจากหม้อ (ไม่ต้องใช้จาน)")
            else:
                print("🥣 หม้อยังไม่มีวัตถุดิบให้หยิบ!")
    else:
        # กรณีไม่มี pot หรือไม่เข้าเงื่อนไข found
        pot_geom = None


    if not found:
        print("ไม่มีวัตถุดิบใกล้ตัว")

# ------------------- icon ติดตามเชฟ -------------------
def show_pick_feedback(game_widget, item_name):
    pix_path = os.path.join(SOURCE_PATH, 'image', f'{item_name}_icon.png')
    pix = QtGui.QPixmap(pix_path)
    if pix.isNull():
        return

    if getattr(game_widget, 'held_icon', None):
        game_widget.held_icon.deleteLater()
        game_widget.held_icon = None

    icon_label = QtWidgets.QLabel(game_widget)
    icon_label.setPixmap(pix)
    icon_label.setScaledContents(True)
    icon_label.resize(40, 40)

    icon_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    icon_label.setStyleSheet('background: transparent;')

    icon_label.show()
    game_widget.held_icon = icon_label

    update_held_icon_position(game_widget)

def update_held_icon_position(game_widget):
    if getattr(game_widget, 'held_icon', None):
        drop_x = game_widget.chef.x() + (game_widget.chef.width() - 40) // 2
        drop_y = game_widget.chef.y() - 40 - 5
        game_widget.held_icon.move(drop_x, drop_y)

# ------------------- วางของ -------------------
def drop_item(game_widget):
    'วางของจากมือเชฟลงบนเขียง, หม้อ หรือพื้น'

    # --- ตรวจว่ามีของในมือไหม ---
    if not getattr(game_widget, 'has_item', False):
        print('❌ ไม่มีของในมือ')
        return

    item_name = game_widget.current_item
    if not hasattr(game_widget, 'chef'):
        print('⚠️ ไม่มี chef ในเกม')
        return

    # --- เตรียมค่าพื้นฐาน ---
    chef = game_widget.chef
    chef_center = QtCore.QPoint(
        chef.x() + chef.width() // 2,
        chef.y() + chef.height() // 2
    )

    placed = False
    target_pos = None
    parent_widget = game_widget

    # ------------------------------------------------------------
    # 🔪 1) ตรวจเขียง
    # ------------------------------------------------------------
    if hasattr(game_widget, 'chopping_board'):
        board = game_widget.chopping_board
        board_geom = board.geometry()
        board_pos = board.mapToParent(QtCore.QPoint(0, 0))

        # ระยะระหว่างเชฟกับเขียง
        dx = chef_center.x() - (board_pos.x() + board_geom.width() // 2)
        dy = chef_center.y() - (board_pos.y() + board_geom.height() // 2)
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 120:
            # 🔹 วางเหนือเขียงเล็กน้อย
            new_x = board_pos.x() + (board_geom.width() // 2) - 20
            new_y = board_pos.y()
            target_pos = QtCore.QPoint(new_x, new_y)
            placed = 'chopping_board'

    # ------------------------------------------------------------
    # 🥘 2) ตรวจหม้อ
    # ------------------------------------------------------------
    if not placed and hasattr(game_widget, 'pot'):
        pot = game_widget.pot
        pot_geom = pot.geometry()
        pot_pos = pot.mapToParent(QtCore.QPoint(0, 0))

        dx = chef_center.x() - (pot_pos.x() + pot_geom.width() // 2)
        dy = chef_center.y() - (pot_pos.y() + pot_geom.height() // 2)
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 120:
            # 🔹 วางเหนือหม้อเล็กน้อย
            new_x = pot_pos.x() + (pot_geom.width() // 2) - 20
            new_y = pot_pos.y() - 35
            target_pos = QtCore.QPoint(new_x, new_y)
            placed = 'pot'

    # ------------------------------------------------------------
    # 📦 3) ถ้าไม่เข้า station ใดเลย → วางบนพื้น
    # ------------------------------------------------------------
    if not placed:
        chef_x = chef.x() + chef.width() // 2 - 20
        chef_y = chef.y() + chef.height() - 10
        target_pos = QtCore.QPoint(chef_x, chef_y)
        placed = 'ground'

    # ------------------------------------------------------------
    # ✅ สร้าง QLabel สำหรับวัตถุดิบ (เฉพาะตอนที่รู้ว่าจะวางที่ไหน)
    # ------------------------------------------------------------
    item_label = QtWidgets.QLabel(parent_widget)
    pix_path = os.path.join(SOURCE_PATH, 'image', f'{item_name}_icon.png')

    if not os.path.exists(pix_path):
        print(f'⚠️ ไม่พบภาพ: {pix_path}')
        return

    pix = QtGui.QPixmap(pix_path)
    item_label.setPixmap(pix)
    item_label.setScaledContents(True)
    item_label.resize(40, 40)
    item_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    item_label.setStyleSheet('background: transparent;')
    item_label.move(target_pos)
    item_label.raise_()
    item_label.show()
    # เก็บชื่อวัตถุดิบบน QLabel ให้ฟังก์ชันอื่นอ่านได้ (ใช้ทั้ง property และ attribute)
    try:
        item_label.setProperty('item_name', item_name)
    except Exception:
        pass
    item_label.item_name = item_name

    # ------------------------------------------------------------
    # 🔧 จัดเก็บ reference ถ้าจำเป็น
    # ------------------------------------------------------------
    if placed == 'chopping_board':
        if not hasattr(game_widget, 'chopping_board_icons'):
            game_widget.chopping_board_icons = []
        game_widget.chopping_board_icons.append(item_label)
        print(f'🔪 วาง {item_name} บนเขียงที่ {target_pos}')

    elif placed == 'pot':
        if not hasattr(game_widget, 'pot_icons'):
            game_widget.pot_icons = []
        if not hasattr(game_widget, 'pot_contents'):
            game_widget.pot_contents = []
        game_widget.pot_icons.append(item_label)
        game_widget.pot_contents.append(item_name)
        # ให้ QLabel ในหม้อมีชื่อด้วย เพื่อให้การหยิบทำงานได้
        try:
            item_label.setProperty('item_name', item_name)
        except Exception:
            pass
        item_label.item_name = item_name
        
        # จัดตำแหน่งวัตถุดิบให้เรียงกันในหม้อ
        num_items = len(game_widget.pot_icons)
        pot_geom = game_widget.pot.geometry()
        item_x = pot_geom.x() + (num_items - 1) * 30  # เว้นระยะห่าง 30 pixels
        item_y = pot_geom.y() - 35  # วางเหนือหม้อนิดหน่อย
        item_label.move(item_x, item_y)
        
        print(f'🥘 วาง {item_name} ลงหม้อที่ {item_x}, {item_y}')
        # พยายามต้มอัตโนมัติเมื่อใส่วัตถุดิบครบสูตร
        try:
            try_cook_pot(game_widget)
        except Exception:
            pass

    else:
        if not hasattr(game_widget, 'placed_items'):
            game_widget.placed_items = []
        game_widget.placed_items.append(item_label)
        # ให้ QLabel บนพื้นมี item_name เพื่อให้การหยิบทำงาน
        try:
            item_label.setProperty('item_name', item_name)
        except Exception:
            pass
        item_label.item_name = item_name
        print(f'📦 วาง {item_name} บนพื้นที่ {target_pos}')

    # ------------------------------------------------------------
    # 🧹 ลบของในมือ (ไอคอนที่เชฟถืออยู่)
    # ------------------------------------------------------------
    if getattr(game_widget, 'held_icon', None):
        game_widget.held_icon.deleteLater()
        game_widget.held_icon = None

    # แจ้งเตือนการวางของ
    drop_msg = ''
    if placed == 'chopping_board':
        drop_msg = f'วาง {item_name} บนเขียง 🔪'
    elif placed == 'pot':
        drop_msg = f'ใส่ {item_name} ลงหม้อ 🥘'
    else:
        drop_msg = f'วาง {item_name} ลงพื้น 📦'
        
    print(drop_msg)
        
    game_widget.has_item = False
    game_widget.current_item = None

# ------------------- หั่น -------------------
def process_space_action(game_widget):
    # ตรวจสอบว่าเชฟอยู่ใกล้ chopping_board หรือไม่
    if not is_near_object(game_widget.chef, game_widget.chopping_board):
        return

    # ถ้า chopping_board มีไอคอนอยู่
    for icon_label in game_widget.chopping_board_icons:
        item_name = icon_label.property('item_name')
        if not item_name:
            continue

        chopped_name = f'{item_name}_chopped'
        pix_path = os.path.join(SOURCE_PATH, 'image', f'{chopped_name}_icon.png')
        pix = QtGui.QPixmap(pix_path)
        if pix.isNull():
            print(f'❌ ไม่พบไฟล์ภาพ: {pix_path}')
            continue

        # สร้าง QTimer เพื่อหั่นเป็นเวลา 3 วินาที
        def finish_chop():
            icon_label.setPixmap(pix)
            icon_label.setScaledContents(True)
            icon_label.setProperty('item_name', chopped_name)
            # ให้ attribute ด้วยเพื่อให้โค้ดอื่นอ่านได้สะดวก (บางที่อ่าน attribute แทน property)
            try:
                icon_label.item_name = chopped_name
            except Exception:
                pass
            # วางตำแหน่งตรงกับ chopping_board
            icon_label.move(game_widget.chopping_board.x(), game_widget.chopping_board.y())
            print(f'✅ หั่นวัตถุดิบเสร็จ: {chopped_name}')

        # แสดง toast ว่ากำลังหั่น
    try:
        if hasattr(game_widget, 'game_page') and game_widget.game_page:
            game_widget.game_page.show_toast(f'กำลังหั่น {item_name}... ⌛', duration=3000)
    except Exception as e:
        print(f"❌ ไม่สามารถแสดง toast ได้: {e}")

    # กำหนด delay 3000 ms (3 วินาที)
    QtCore.QTimer.singleShot(3000, finish_chop)
    print(f'⏳ เริ่มหั่นวัตถุดิบ: {item_name}')

# ------------------- ทิ้งของลงถังขยะ ------------------

def try_throw_item_to_trash(game_widget, threshold=80):
    """
    ถ้าอยู่ใกล้ trash_bin → ทิ้งของในมือ (หรือของที่พื้นใกล้ถัง)
    """
    if not hasattr(game_widget, 'trash_bin'):
        print('❌ ไม่มี trash_bin ในเกม')
        return

    chef_geom = game_widget.chef.geometry()
    trash_geom = game_widget.trash_bin.geometry()

    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )
    trash_center = QtCore.QPoint(
        trash_geom.x() + trash_geom.width() // 2,
        trash_geom.y() + trash_geom.height() // 2
    )

    dx = chef_center.x() - trash_center.x()
    dy = chef_center.y() - trash_center.y()
    distance = (dx**2 + dy**2) ** 0.5

    if distance > threshold:
        print(f'🚫 ยังไม่ใกล้ถังพอ ({int(distance)} px)')
        return

    # ถ้ามีของในมือ → ทิ้ง
    if getattr(game_widget, 'has_item', False):
        item_name = game_widget.current_item
        print(f'🗑️ ทิ้งของ: {item_name}')
        game_widget.has_item = False
        game_widget.current_item = None

        if getattr(game_widget, 'held_icon', None):
            game_widget.held_icon.deleteLater()
            game_widget.held_icon = None
        return

    # ถ้าไม่มีของในมือ → ลบของที่พื้นใกล้ถัง
    if hasattr(game_widget, 'placed_items'):
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
                print(f'🗑️ เก็บ {item_label.item_name} ทิ้งถังขยะ')
                item_label.deleteLater()
                game_widget.placed_items.remove(item_label)

    print('🧹 ทำความสะอาดเรียบร้อย!')

# ============================================================
# 🧺 ฟังก์ชันเกี่ยวกับ 'จาน (Plate)'
# ============================================================

def add_item_to_plate(game_widget, item_name):
    'เพิ่มวัตถุดิบลงในจานและอัปเดตภาพ'
    if not hasattr(game_widget, 'plate_station'):
        print('❌ ไม่มี plate_station ในเกม')
        return

    if not hasattr(game_widget, 'plate_items'):
        game_widget.plate_items = []

    # ตรวจว่าอยู่ใกล้จานไหม
    if not is_near_object(game_widget.chef, game_widget.plate, mode='center'):
        print('❌ ไม่ได้อยู่ใกล้จาน')
        return
    
    # 🔎 ตรวจกฎการใส่วัตถุดิบ: ถ้าวัตถุดิบเป็น raw แต่สูตรคาดว่าเป็น chopped -> ต้องหั่นก่อน
    try:
        # RECIPE_DICT นำเข้าจาก recipe_data ถ้ามี
        recipe_map = RECIPE_DICT if isinstance(RECIPE_DICT, dict) and RECIPE_DICT else {}
    except Exception:
        recipe_map = {}

    # รวมชื่อวัตถุดิบที่สูตรต่างๆ ใช้ (เช่น 'tomato_chopped' หรือ 'tomato')
    used_names = set()
    for key in recipe_map.keys():
        try:
            for n in key:
                used_names.add(n)
        except Exception:
            pass

    # ถ้าวัตถุดิบที่ใส่ไม่ตรงกับชื่อที่สูตรใช้ แต่มีชื่อ _chopped อยู่ → แจ้งให้หั่นก่อน
    if (item_name not in used_names) and (f"{item_name}_chopped" in used_names):
        print(f'⚠️ ต้องหั่น "{item_name}" ก่อนจึงจะใส่ในจานได้')
        return

    # เพิ่มของลงจาน
    if not hasattr(game_widget, 'plate_items'):
        game_widget.plate_items = []
    game_widget.plate_items.append(item_name)
    add_msg = f'ใส่ {item_name} ลงจาน 🍽️'
    print(add_msg)
    try:
        if hasattr(game_widget, 'game_page') and game_widget.game_page:
            game_widget.game_page.show_toast(add_msg)
            print("✅ แสดง toast: " + add_msg)
    except Exception as e:
        print(f"❌ ไม่สามารถแสดง toast ได้: {e}")

    update_plate_image(game_widget)


def update_plate_image(game_widget, target_label=None, items=None):
    if target_label is None:
        target_label = getattr(game_widget, 'plate_station', None)
        if target_label is None:
            print('❌ ไม่มี target_label สำหรับจาน')
            return

    if items is None:
        items = getattr(game_widget, 'plate_items', [])

    # 🔹 ทำความสะอาดชื่อวัตถุดิบ
    clean_items = [item.strip().lower() for item in items]
    items_set = frozenset(clean_items)

    # ใช้ RECIPE_DICT ที่นำเข้าจาก recipe_data ถ้ามี (เป็น authoritative source)
    try:
        recipe_map = RECIPE_DICT if isinstance(RECIPE_DICT, dict) and RECIPE_DICT else None
    except Exception:
        recipe_map = None

    if recipe_map is None:
        recipe_map = {
            frozenset(['lettuce_chopped']): 'lettuce_salad',
            frozenset(['tomato_chopped', 'lettuce_chopped']): 'tomato_lettuce_salad',
            frozenset(['tomato_chopped', 'lettuce_chopped', 'cucamber_chopped']): 'delux_salad',
            frozenset(['tomato_soup']): 'tomato_soup',
        }

    # ลบวัตถุดิบเก่า
    if hasattr(target_label, 'ingredient_icons'):
        for icon in target_label.ingredient_icons:
            icon.deleteLater()
        target_label.ingredient_icons.clear()
    else:
        target_label.ingredient_icons = []

    combo_name = recipe_map.get(items_set, None)

    if combo_name:
        combo_image_name = f'plate_{combo_name}.png'
        combo_path = os.path.join(SOURCE_PATH, 'image', combo_image_name)
        if not os.path.exists(combo_path):
            combo_path = os.path.join(SOURCE_PATH, 'image', 'plate.png')

        pix = QtGui.QPixmap(combo_path)
        target_label.clear()
        target_label.setPixmap(pix)
        target_label.setScaledContents(True)
        target_label.repaint()  # ✅ เพิ่มจุดนี้ให้ refresh ทันที

        print(f'🍽️ เมนูสำเร็จ: {combo_name}')


    else:
        plate_base = os.path.join(SOURCE_PATH, 'image', 'plate.png')
        pix = QtGui.QPixmap(plate_base)
        target_label.setPixmap(pix)
        target_label.setScaledContents(True)

        base_x = target_label.x()
        base_y = target_label.y()
        spacing = 20

        for i, ingredient in enumerate(clean_items):
            icon_path = os.path.join(SOURCE_PATH, 'image', f'{ingredient}.png')
            if os.path.exists(icon_path):
                icon_label = QtWidgets.QLabel(game_widget)
                icon_pix = QtGui.QPixmap(icon_path)
                icon_label.setPixmap(icon_pix)
                icon_label.setScaledContents(True)
                icon_label.resize(32, 32)
                icon_label.move(base_x + 16, base_y - (i + 1) * spacing)
                icon_label.show()
                target_label.ingredient_icons.append(icon_label)

        print(f'🥗 ยังไม่ตรงสูตร: แสดง {len(clean_items)} วัตถุดิบเหนือจาน')

def try_pickup_plate(game_widget):
    'ให้เชฟหยิบจานจาก station หรือจากพื้น (พร้อมของบนจาน)'
    # 🧺 ถ้ามือเชฟถือของอื่นอยู่ หยุดเลย
    if getattr(game_widget, 'has_item', False):
        print('เชฟถือของอยู่แล้ว 🧺')
        return

    # 🔸 ลบจานเก่าถ้ามี
    if hasattr(game_widget, 'held_plate') and game_widget.held_plate:
        game_widget.held_plate.deleteLater()
        game_widget.held_plate = None

    # 📍 ศูนย์กลางเชฟ
    chef_geom = game_widget.chef.geometry()
    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )

    threshold = getattr(game_widget, 'pickup_threshold', 40)

    # 1️⃣ ตรวจว่าใกล้ plate_station หรือไม่
    if hasattr(game_widget, 'plate_station') and is_near_object(game_widget.chef, game_widget.plate_station, mode='center'):
        if getattr(game_widget, 'has_plate', False):
            print('⚠️ มีจานอยู่แล้ว')
            return

        # ✅ หยิบจานใหม่จาก station
        game_widget.has_plate = True
        game_widget.current_item = 'plate'
        game_widget.plate_items = []

        held_plate = QtWidgets.QLabel(game_widget)
        img_path = os.path.join(SOURCE_PATH, 'image', 'plate.png')
        if os.path.exists(img_path):
            held_plate.setPixmap(QtGui.QPixmap(img_path))
        held_plate.setScaledContents(True)
        held_plate.resize(50, 50)
        held_plate.setStyleSheet('background: transparent;')
        held_plate.show()

        # จัดตำแหน่งบนหัวเชฟ
        update_plate_position(game_widget, game_widget.chef, held_plate)
        held_plate.ingredient_icons = []  # เตรียมเก็บไอคอนวัตถุดิบ
        game_widget.held_plate = held_plate

        print('✅ หยิบจานเรียบร้อยจาก station!')
        return

    # 2️⃣ ตรวจ dropped_plates (จานที่วางพื้น)
    if hasattr(game_widget, 'dropped_plates'):
        for plate_dict in list(game_widget.dropped_plates):
            lbl = plate_dict.get('label')
            items_on_plate = plate_dict.get('items', [])

            if lbl is None:
                continue

            # ระยะเชฟกับจาน
            item_geom = lbl.geometry()
            item_center = QtCore.QPoint(
                item_geom.x() + item_geom.width() // 2,
                item_geom.y() + item_geom.height() // 2
            )
            dx = chef_center.x() - item_center.x()
            dy = chef_center.y() - item_center.y()
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= threshold:
                # ✅ หยิบจานพร้อมของทั้งหมด
                game_widget.has_plate = True
                game_widget.current_item = 'plate'
                game_widget.plate_items = list(items_on_plate)

                held_plate = QtWidgets.QLabel(game_widget)
                img_path = os.path.join(SOURCE_PATH, 'image', 'plate_icon.png')
                if os.path.exists(img_path):
                    held_plate.setPixmap(QtGui.QPixmap(img_path))
                held_plate.setScaledContents(True)
                held_plate.resize(50, 50)
                held_plate.setStyleSheet('background: transparent;')
                held_plate.show()

                # จัดตำแหน่งบนหัวเชฟ
                update_plate_position(game_widget, game_widget.chef, held_plate)
                held_plate.ingredient_icons = []

                # 🔹 ทำความสะอาดชื่อวัตถุดิบ
                clean_items = [item.strip().lower() for item in game_widget.plate_items]

                # อัปเดตรูปจานให้ตรง combo
                update_plate_image(game_widget, target_label=held_plate, items=game_widget.plate_items)

                game_widget.held_plate = held_plate

                # ลบจานจากพื้น
                lbl.deleteLater()
                try:
                    game_widget.dropped_plates.remove(plate_dict)
                except ValueError:
                    pass

                print(f'✅ หยิบจานพร้อมของทั้งหมดจากพื้น: {game_widget.plate_items}')
                return

    print('❌ ไม่ได้อยู่ใกล้วัตถุดิบหรือจานใด ๆ')

def add_item_to_held_plate(game_widget, item_name):
    'เพิ่มวัตถุดิบลงในจานที่ถืออยู่ (held_plate)'
    if not getattr(game_widget, 'has_plate', False):
        print('❌ ไม่มีจานในมือ')
        return

    if not hasattr(game_widget, 'held_plate') or game_widget.held_plate is None:
        print('❌ ไม่มี held_plate')
        return

    if not hasattr(game_widget, 'plate_items'):
        game_widget.plate_items = []

    # ตรวจความต้องการของสูตร: ถ้าสูตรต้องการ xxx_chopped แต่ผู้เล่นใส่ xxx ดิบ -> แจ้งให้หั่นก่อน
    try:
        recipe_map = RECIPE_DICT if isinstance(RECIPE_DICT, dict) and RECIPE_DICT else {}
    except Exception:
        recipe_map = {}
    used_names = set()
    for key in recipe_map.keys():
        try:
            for n in key:
                used_names.add(n)
        except Exception:
            pass

    if (item_name not in used_names) and (f"{item_name}_chopped" in used_names):
        print(f'⚠️ ต้องหั่น "{item_name}" ก่อนจึงจะใส่ในจานได้')
        return

    game_widget.plate_items.append(item_name)
    print(f'🍽️ ใส่ {item_name} ลงจานที่ถืออยู่: {game_widget.plate_items}')

    try:
        update_plate_image(game_widget, target_label=game_widget.held_plate, items=game_widget.plate_items)
    except Exception:
        pass

def add_item_to_dropped_plate(game_widget, plate_dict, item_name):
    'เพิ่มวัตถุดิบลงในจานที่วางบนพื้น แล้วอัปเดตภาพให้ตรงสูตร'
    lbl = plate_dict.get('label')
    if lbl is None or not isinstance(lbl, QtWidgets.QLabel):
        print('❌ plate label ไม่ถูกต้อง')
        return

    # ตรวจความต้องการของสูตรก่อนจะเพิ่ม: ต้องหั่นถ้าสูตรต้องการ chopped
    try:
        recipe_map = RECIPE_DICT if isinstance(RECIPE_DICT, dict) and RECIPE_DICT else {}
    except Exception:
        recipe_map = {}
    used_names = set()
    for key in recipe_map.keys():
        try:
            for n in key:
                used_names.add(n)
        except Exception:
            pass
    if (item_name not in used_names) and (f"{item_name}_chopped" in used_names):
        print(f'⚠️ ต้องหั่น "{item_name}" ก่อนจึงจะใส่ในจานได้')
        return

    # เพิ่มวัตถุดิบใหม่เข้า list
    items = list(plate_dict.get('items', []))
    items.append(item_name)
    plate_dict['items'] = items
    print(f'🍽️ ใส่ {item_name} ลงจานที่พื้น: {items}')

    # 🔧 ล้างภาพเก่าก่อน (เพื่อให้ภาพใหม่ถูกแสดงทันที)
    lbl.clear()
    lbl.repaint()

    # 🔹 เรียก update_plate_image โดยอ้างถึง QLabel ตัวนี้
    update_plate_image(game_widget, target_label=lbl, items=items)

    # ✅ บังคับ refresh QLabel ให้แสดงผลใหม่
    lbl.raise_()
    lbl.show()
    lbl.repaint()

    print('✅ จานบนพื้นอัปเดตภาพเรียบร้อย')

def is_near_object(obj_a, obj_b, threshold=60, mode='center'):
    """
    ตรวจว่าวัตถุ obj_a อยู่ใกล้ obj_b หรือไม่

    mode:
        - 'center' : วัดระยะจากจุดศูนย์กลาง (เหมาะกับ station ทั่วไป)
        - 'bounds' : วัดจากระยะขอบของ bounding box (เหมาะกับ trash_bin หรือ collision check)
    """
    if not (obj_a and obj_b):
        return False

    if mode == 'center':
        # --- วัดระยะจากจุดศูนย์กลาง ---
        ax = obj_a.x() + obj_a.width() / 2
        ay = obj_a.y() + obj_a.height() / 2
        bx = obj_b.x() + obj_b.width() / 2
        by = obj_b.y() + obj_b.height() / 2
        distance = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    elif mode == 'bounds':
        # --- วัดจากขอบกล่อง (เหมือน trash) ---
        a_rect = QtCore.QRect(obj_a.x(), obj_a.y(), obj_a.width(), obj_a.height())
        b_rect = QtCore.QRect(obj_b.x(), obj_b.y(), obj_b.width(), obj_b.height())

        dx = max(b_rect.left() - a_rect.right(), a_rect.left() - b_rect.right(), 0)
        dy = max(b_rect.top() - a_rect.bottom(), a_rect.top() - b_rect.bottom(), 0)
        distance = (dx**2 + dy**2) ** 0.5

    else:
        raise ValueError("mode ต้องเป็น 'center' หรือ 'bounds'")

    return distance < threshold


def update_plate_position(game_widget, chef, plate_label):
    'อัปเดตตำแหน่งจานให้อยู่บนหัวเชฟ'
    plate_x = chef.x() + (chef.width() - plate_label.width()) // 2
    plate_y = chef.y() - plate_label.height() + 10  # +10 ให้จานลอยเหนือหัวนิดหน่อย
    plate_label.move(plate_x, plate_y)

def drop_plate(game_widget):
    'วางจานลงพื้น'
    if not getattr(game_widget, 'has_plate', False):
        print('❌ ไม่มีจานในมือ')
        return

    chef_x = game_widget.chef.x()
    chef_y = game_widget.chef.y()

    dropped_label = QtWidgets.QLabel(game_widget)
    dropped_label.setGeometry(chef_x + 40, chef_y + 40, 50, 50)
    dropped_label.setStyleSheet('background: transparent;')
    dropped_label.show()

    update_plate_image(game_widget, target_label=dropped_label, items=getattr(game_widget, 'plate_items', []))

    if not hasattr(game_widget, 'dropped_plates'):
        game_widget.dropped_plates = []
    game_widget.dropped_plates.append({
        'label': dropped_label,
        'items': list(getattr(game_widget, 'plate_items', []))
    })

    game_widget.has_plate = False
    game_widget.current_item = None
    game_widget.plate_items = []
    if hasattr(game_widget, 'held_plate'):
        game_widget.held_plate.deleteLater()
        game_widget.held_plate = None

    drop_msg = 'วางจานลงพื้น 🧺'
    print(drop_msg)
    game_page = getattr(game_widget, 'game_page', None)
    if game_page and hasattr(game_page, 'show_toast'):
        game_page.show_toast(drop_msg)

def is_near_trash(game_widget, threshold=40):
    """
    ตรวจสอบว่าเชฟอยู่ใกล้ถังขยะหรือไม่
    return: True ถ้าอยู่ในระยะ threshold, False ถ้าไกลเกินไป
    """
    if not hasattr(game_widget, 'trash_bin') or game_widget.trash_bin is None:
        print('⚠️ ไม่มี trash_bin ในเกม')
        return False

    chef_geom = game_widget.chef.geometry()
    trash_geom = game_widget.trash_bin.geometry()

    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )
    trash_center = QtCore.QPoint(
        trash_geom.x() + trash_geom.width() // 2,
        trash_geom.y() + trash_geom.height() // 2
    )

    dx = chef_center.x() - trash_center.x()
    dy = chef_center.y() - trash_center.y()
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance <= threshold

def throw_plate_to_trash(game_widget):
    'ทิ้งจานในถังขยะ'
    if not getattr(game_widget, 'has_plate', False):
        print('❌ ไม่มีจานในมือ')
        return
    if not hasattr(game_widget, 'trash_bin'):
        print('❌ ไม่มี trash_bin ในเกม')
        return

    if not is_near_trash(game_widget):
        print('🚫 อยู่ไกลเกินไปจากถังขยะ')
        return

    print('🗑️ ทิ้งจานลงถังขยะแล้ว')
    if hasattr(game_widget, 'held_plate'):
        game_widget.held_plate.deleteLater()
        game_widget.held_plate = None

    game_widget.has_plate = False
    game_widget.current_item = None
    game_widget.plate_items = []

' serve station '

def try_serve_plate(game_widget, threshold=80):

    if not hasattr(game_widget, 'serve_station'):
        print('❌ ไม่มี serve_station ในเกม')
        return False

    chef_geom = game_widget.chef.geometry()
    chef_center = QtCore.QPoint(
        chef_geom.x() + chef_geom.width() // 2,
        chef_geom.y() + chef_geom.height() // 2
    )

    serv_geom = game_widget.serve_station.geometry()
    serv_center = QtCore.QPoint(
        serv_geom.x() + serv_geom.width() // 2,
        serv_geom.y() + serv_geom.height() // 2
    )

    dx = chef_center.x() - serv_center.x()
    dy = chef_center.y() - serv_center.y()
    distance = (dx**2 + dy**2) ** 0.5

    if distance > threshold:
        far_msg = 'ยังไม่ใกล้จุดเสิร์ฟ 🚫'
        print(far_msg)
        try:
            if game_page and hasattr(game_page, 'show_toast'):
                game_page.show_toast(far_msg, duration=3000)
                print("✅ แสดง toast ระยะห่าง")
        except Exception as e:
            print(f"❌ Error showing toast: {e}")
        return False

    # หา game_page ถ้า GameWidget ถูกเชื่อมไว้
    game_page = getattr(game_widget, 'game_page', None)
    parent = game_page or game_widget.parent()

    # ใช้ SCORE_DICT ที่นำเข้าจาก recipe_data ถ้ามี
    try:
        score_dict = SCORE_DICT if isinstance(SCORE_DICT, dict) and SCORE_DICT else {}
    except Exception:
        score_dict = {}

    # current_orders จะมาจาก game_page.orders ถ้าเชื่อมไว้, มิฉะนั้น fallback ไปยัง property บน widget
    if game_page is not None and hasattr(game_page, 'orders'):
        current_orders = game_page.orders
    else:
        current_orders = getattr(game_widget, 'current_orders', [])
    if not isinstance(current_orders, list):
        current_orders = []

    def check_and_score(plate_items):
        # ใช้ RECIPE_DICT ที่นำเข้าจาก recipe_data ถ้ามี
        try:
            recipe_map = RECIPE_DICT if isinstance(RECIPE_DICT, dict) and RECIPE_DICT else None
        except Exception:
            recipe_map = None

        if recipe_map is None:
            recipe_map = {
                frozenset(['lettuce_chopped']): 'lettuce_salad',
                frozenset(['tomato_chopped', 'lettuce_chopped']): 'tomato_lettuce_salad',
                frozenset(['tomato_chopped', 'lettuce_chopped', 'cucamber_chopped']): 'delux_salad',
                frozenset(['tomato_soup']): 'tomato_soup',
            }

        meal_name = None
        for recipe, name in recipe_map.items():
            if set(plate_items) == set(recipe):
                meal_name = name
                break

        if not meal_name:
            print('🍽️ เมนูไม่ตรงกับสูตรใด ๆ')
            return 0

        # ถ้าพบเมนู ให้เช็คว่าอยู่ในออร์เดอร์หรือไม่ (ตรวจจาก authoritative orders ถ้ามี)
        in_orders = False
        if game_page is not None and hasattr(game_page, 'orders'):
            in_orders = meal_name in game_page.orders
        else:
            in_orders = meal_name in current_orders

        if in_orders:
            score = score_dict.get(meal_name, 0)
            success_msg = f'เสิร์ฟ {meal_name} ถูกต้อง +{score} คะแนน ✅'
            print(success_msg)
            try:
                if game_page and hasattr(game_page, 'show_toast'):
                    game_page.show_toast(success_msg, duration=4000)
                    print("✅ แสดง toast เสิร์ฟสำเร็จ")
            except Exception as e:
                print(f"❌ Error showing toast: {e}")
            spawn_served_object(meal_name, spacing=3.0)
            # อัปเดต authoritative orders ถ้าเป็น GamePage
            if game_page is not None and hasattr(game_page, 'serve_dish_to_order'):
                try:
                    game_page.serve_dish_to_order(meal_name)
                except Exception:
                    try:
                        # fallback: remove and refresh
                        game_page.orders.remove(meal_name)
                        if hasattr(game_page, '_refresh_orders_images'):
                            game_page._refresh_orders_images()
                    except Exception:
                        pass
            else:
                try:
                    current_orders.remove(meal_name)
                except Exception:
                    pass
            return score
        else:
            fail_msg = f'เสิร์ฟ {meal_name} ไม่ตรงออร์เดอร์ ❌ (-5)'
            print(f'⚠️ {fail_msg}')
            try:
                if game_page and hasattr(game_page, 'show_toast'):
                    game_page.show_toast(fail_msg, duration=4000)
                    print("✅ แสดง toast เสิร์ฟผิด")
            except Exception as e:
                print(f"❌ Error showing toast: {e}")
            return -5

    def update_score(amount):
        target = game_page if game_page is not None else parent
        if target is not None and hasattr(target, 'score_label'):
            try:
                num = int(target.score_label.text())
            except Exception:
                num = 0

            num += amount
            if num < 0:
                num = 0

            target.score_label.setText(str(num))

            # อัปเดตค่าใน GamePage ให้ตรงกัน
            if hasattr(target, 'current_score'):
                target.current_score = num


    # เสิร์ฟจากจานในมือ
    if getattr(game_widget, 'has_plate', False):
        plate_items = getattr(game_widget, 'plate_items', [])
        score = check_and_score(plate_items)
        update_score(score)

        if hasattr(game_widget, 'held_plate') and game_widget.held_plate:
            game_widget.held_plate.deleteLater()
            game_widget.held_plate = None

        game_widget.has_plate = False
        game_widget.current_item = None
        game_widget.plate_items = []
        return True

    # เสิร์ฟจากจานบนพื้น
    if hasattr(game_widget, 'dropped_plates'):
        for plate_dict in list(game_widget.dropped_plates):
            lbl = plate_dict.get('label')
            if lbl is None:
                continue

            item_geom = lbl.geometry()
            item_center = QtCore.QPoint(
                item_geom.x() + item_geom.width() // 2,
                item_geom.y() + item_geom.height() // 2
            )
            dx = serv_center.x() - item_center.x()
            dy = serv_center.y() - item_center.y()
            dist_item = (dx**2 + dy**2) ** 0.5

            if dist_item <= threshold:
                plate_items = plate_dict.get('items', [])
                score = check_and_score(plate_items)
                update_score(score)

                lbl.deleteLater()
                try:
                    game_widget.dropped_plates.remove(plate_dict)
                except Exception:
                    pass
                return True

    print('❌ ไม่มีจานที่จะเสิร์ฟ')
    return False


def try_cook_pot(game_widget):
    """ตรวจว่าสามารถต้มในหม้อได้หรือไม่ - สร้าง soup_icon และเคลียร์วัตถุดิบเมื่อสำเร็จ"""
    # ถ้าไม่มีหม้อหรือไม่มีเนื้อหา -> return
    if not hasattr(game_widget, 'pot'):
        return False
    contents = getattr(game_widget, 'pot_contents', [])
    icons = getattr(game_widget, 'pot_icons', [])

    print(f'[pot] current pot_contents={contents}')
    if not contents:
        return False

    # ถ้ามี soup อยู่แล้ว ให้ไม่ทำซ้ำ
    if hasattr(game_widget, 'soup_icon'):
        return False

    # หาชื่อ base ของวัตถุดิบ (ตัด '_chopped') และนับ
    bases = [c.replace('_chopped', '').replace('_icon', '') for c in contents]
    counts = {}
    for b in bases:
        counts[b] = counts.get(b, 0) + 1

    # กฎง่าย ๆ: ถ้ามีมะเขือเทศ 3 ชิ้นจะทำซุปมะเขือเทศ
    chosen_base = None
    for k, v in counts.items():
        if k == 'tomato' and v >= 3:
            chosen_base = k
            break
    if chosen_base is None and len(contents) >= 3:
        # ถ้าไม่มีชนิดซ้ำ แต่ใส่ครบ 3 ชิ้น ให้เลือกชนิดแรก
        chosen_base = bases[0]

    if not chosen_base:
        return False

    # แปลงเป็นชื่อซุป (mapping สำหรับชื่อที่รองรับ)
    soup_name = None
    if chosen_base == 'tomato':
        soup_name = 'tomato_soup'
    # เพิ่ม mapping อื่น ๆ ได้ที่นี่

    if not soup_name:
        return False

    # ตั้งเวลาทำซุป 2 วินาที
    def cook_finish():
        # ลบไอคอนวัตถุดิบในหม้อ
        for ic in list(icons):
            try:
                ic.deleteLater()
            except Exception:
                pass
        game_widget.pot_icons = []
        game_widget.pot_contents = []

        # สร้างไอคอนซุปบนหม้อ
        pot_geom = game_widget.pot.geometry()
        pot_pos = game_widget.pot.mapToParent(QtCore.QPoint(0, 0))

        # สร้าง QLabel สำหรับซุป
        soup_lbl = QtWidgets.QLabel(game_widget)

        # โหลด PNG (โปร่งใส)
        soup_path = os.path.join(SOURCE_PATH, 'image', f'{soup_name}.png')
        pix = QtGui.QPixmap(soup_path) if os.path.exists(soup_path) else QtGui.QPixmap()
        soup_lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        soup_lbl.setPixmap(pix)

        # ตั้งค่าให้ QLabel รองรับการปรับขนาด
        soup_lbl.setScaledContents(True)
        soup_lbl.resize(49, 57)

        # วางตรงกลางหม้อ และยกขึ้นเล็กน้อย
        soup_lbl.move(
            pot_pos.x() + (pot_geom.width() - 48) // 2,
            pot_pos.y() - 40
        )

        soup_lbl.show()

        game_widget.soup_icon = soup_lbl
        print(f'🍲 ต้มเสร็จแล้ว: {soup_name} (created soup_icon)')

    # รอ 2 วินาทีแล้วค่อยทำซุป
    QtCore.QTimer.singleShot(4000, cook_finish)
    print('⏳ เริ่มต้มซุป... (2 วินาที)')
    if hasattr(game_widget, 'game_page') and game_widget.game_page:
        game_widget.game_page.show_toast('⏳ เริ่มต้มซุป... (4 วินาที)')
    return True
    game_widget.soup_icon = soup_lbl

    print(f'🍲 ต้มเสร็จแล้ว: {soup_name} (created soup_icon)')
    if hasattr(game_widget, 'game_page') and game_widget.game_page:
        game_widget.game_page.show_toast(f'🍲 ต้มเสร็จแล้ว: {soup_name}')
    return True

"""------------Invisible Colliders-----------"""
def _create_invisible_walls(self):
    zones = [
        QtCore.QRect(725, 295, 15, 235),
        QtCore.QRect(520, 120, 30, 130),
        QtCore.QRect(1000, 460, 100, 65),
        QtCore.QRect(790, 510, 200, 15),
        QtCore.QRect(1130, 180, 80, 250),
        QtCore.QRect(65, 290, 80, 110),
        QtCore.QRect(195, 80, 355, 65),
        QtCore.QRect(715, 80, 260, 65),
        QtCore.QRect(195, 480, 355, 50)
    ]
    for rect in zones:
        box = QtWidgets.QFrame(self)
        box.setGeometry(rect)
        #box.setStyleSheet("background-color: rgba(255, 0, 0, 100); border: 1px solid red;")
        box.setStyleSheet("background: transparent;")
        box.hide()
        self.obstacles.append(box)

def _can_move_to(self, new_x, new_y):
    new_rect = QtCore.QRect(new_x, new_y, self.chef.width(), self.chef.height())
    for obs in getattr(self, "obstacles", []):
        if new_rect.intersects(obs.geometry()):
            return False
    return True

def spawn_served_object(menu_name, spacing=3.0, row_spacing=3.0):

    menu_to_object = {
        "tomato_soup": "sphere",             # ซุปมะเขือเทศ -> ทรงกลม
        "lettuce_salad": "cube",             # สลัดผัก -> ทรงสี่เหลี่ยม
        "tomato_lettuce_salad": "cylinder",  # สลัดมะเขือเทศ -> ทรงกระบอก
        "delux_salad": "cone",               # สลัดรวม -> ทรงกรวย
        "lettuce_tomato_salad": "cylinder"   # สลัดมะเขือผัด -> ทรงกระบอก
    }

    menu_to_row = {
        "tomato_soup": 0,
        "lettuce_salad": 1,
        "tomato_lettuce_salad": 2,
        "lettuce_tomato_salad": 2,  # ใช้แถวเดียวกับ tomato_lettuce_salad
        "delux_salad": 3
    }

    if menu_name not in menu_to_object:
        cmds.warning(f"⚠️ ไม่มีเมนูชื่อ '{menu_name}' ในรายการ mapping.")
        return

    object_type = menu_to_object[menu_name]
    row_index = menu_to_row.get(menu_name, 0)  # ถ้าไม่เจอให้เป็นแถวแรก

    existing_objs = cmds.ls(f"{menu_name}_*")
    next_index = len(existing_objs) + 1

    obj_name = f"{menu_name}_{next_index}"

    if object_type == "sphere":
        obj = cmds.polySphere(name=obj_name)[0]
    elif object_type == "cube":
        obj = cmds.polyCube(name=obj_name)[0]
    elif object_type == "cylinder":
        obj = cmds.polyCylinder(name=obj_name)[0]
    elif object_type == "cone":
        obj = cmds.polyCone(name=obj_name)[0]
    else:
        cmds.warning(f"⚠️ ไม่รู้จัก object_type: {object_type}")
        return

    x_pos = (next_index - 1) * spacing
    y_pos = row_index * row_spacing
    cmds.move(x_pos, y_pos, 0, obj, absolute=True)

    print(f"✅ Created {obj_name} ({object_type}) at X={x_pos}, Y={y_pos}")
    return obj

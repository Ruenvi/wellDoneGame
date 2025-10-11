from PySide6 import QtCore, QtGui, QtWidgets
import os

SOURCE_PATH = 'D:/default/2026/scripts/wellDoneGame/source_image'


def get_img(name):
    """ดึงภาพ sprite จากโฟลเดอร์"""
    return QtGui.QPixmap(os.path.join(SOURCE_PATH, "image", name))


# 👨‍🍳 ตัวละครเชฟ
class ChefItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, name, x, y, pixmap):
        super().__init__(pixmap)
        self.name = name
        self.setPos(x, y)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.speed = 5
        self.held_item = None


# 🔥 สถานี (เตา / เขียง / เสิร์ฟ / จุดหยิบ)
class StationItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, label, x, y, pixmap):
        super().__init__(pixmap)
        self.label = label
        self.setPos(x, y)


# 🍣 วัตถุดิบ
class IngredientItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, name, x, y, pixmap):
        super().__init__(pixmap)
        self.name = name
        self.setPos(x, y)

class GameObject:
    def __init__(self, name, image_path, pos):
        self.name = name
        self.image_path = image_path
        self.pos = QtCore.QPointF(pos)
        self.sprite = None

class Ingredient(GameObject):
    def __init__(self, name, image_path, pos):
        super().__init__(name, image_path, pos)
        self.held = False
        self.cooked = False

class Station(GameObject):
    def __init__(self, station_type, image_path, pos):
        super().__init__(station_type, image_path, pos)
        self.station_type = station_type
        self.occupied = None  # ใครวางของอยู่

class Chef(GameObject):
    def __init__(self, name, image_path, pos):
        super().__init__(name, image_path, pos)
        self.speed = 6
        self.holding = None  # ถือของอยู่มั้ย

    def can_pick(self):
        return self.holding is None

    def pick(self, ingredient):
        if self.can_pick():
            self.holding = ingredient
            ingredient.held = True
            return True
        return False

    def drop(self, target_station):
        if self.holding:
            target_station.occupied = self.holding
            self.holding.held = False
            self.holding = None

class RecipeBook:
    RECIPES = {
        ('fish', 'rice'): 'sushi',
        ('fish', 'rice', 'seaweed'): 'deluxe_sushi'
    }

    @classmethod
    def get_recipe_result(cls, items):
        names = tuple(sorted([i.name for i in items]))
        for recipe, result in cls.RECIPES.items():
            if tuple(sorted(recipe)) == names:
                return result
        return None

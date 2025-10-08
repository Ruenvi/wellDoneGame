from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import os

SOURCE_PATH = 'D:/default/2026/scripts/wellDoneGame'

class GameMenu(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)
	pass

class HowToPlayPage(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)
	pass

class ResumePage(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)
	pass

class Ingame(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)
	pass

class WellDoneGame(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)

		self.setWindowTiTle('Well Done !')
		self.resize(1200,700)


		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)


def run():
	global ui
	try:
		ui.close()
	except:
		pass
	ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
	ui = WellDoneGame(parent=ptr)
	ui.show()
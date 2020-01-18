import sys
from operator import xor

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtGui import QIntValidator

from food_loader import *

tree:QTreeWidget = 0

def filter(str):
	items = tree.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
	for item in items:
		text = item.text(0)
		hidden = str not in text
		item.setHidden(hidden)
		item.setExpanded(False)
		if hidden == False:
			parent = item.parent()
			if parent is not None:
				parent.setHidden(False)
				parent.setExpanded(True)


class Meal(QWidget):
	def __init__(self, name):
		super().__init__()
		self.layout_main = QVBoxLayout()
		self.setLayout(self.layout_main)
		self.table = QTableWidget()
		self.table.setColumnCount(6)
		self.table.setHorizontalHeaderLabels(["Name", "Fat", "Protein", "Carbohydrates", "KCalories", "Amount, g"])
		self.table.verticalHeader().setVisible(False)
		self.layout_main.addWidget(QLabel(name))
		self.layout_main.addWidget(self.table)
		self.layout_main.setContentsMargins(0, 0, 0, 0)
		self.table.setDragEnabled(False)
		self.setAcceptDrops(True)

	def dragEnterEvent(self, e):
		e.accept()

	def dropEvent(self, e):
		self.table.insertRow(self.table.rowCount())
		item = tree.selectedItems()[0]
		name = item.text(0)
		food = foods[name]
		items = [QTableWidgetItem(name), QTableWidgetItem(str(food["f"])), QTableWidgetItem(str(food["p"])), QTableWidgetItem(str(food["c"])), QTableWidgetItem(str(food["cal"]))]
		for i in range(len(items)):
			items[i].setFlags(Qt.ItemIsEnabled)
			self.table.setItem(self.table.rowCount() - 1, i, items[i])
		edit_amount = QLineEdit("100")
		edit_amount.editingFinished.connect(self.update)
		edit_amount.setValidator(QIntValidator(0, 10000000))
		self.table.setCellWidget(self.table.rowCount() - 1, 5, edit_amount)
		self.update()

	def update(self):
		print("Update")


class DayWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.breakfast = Meal("Breakfast")
		self.lunch = Meal("Lunch")
		self.dinner = Meal("Dinner")
		self.layout_main = QVBoxLayout()
		self.setLayout(self.layout_main)
		self.layout_main.addWidget(self.breakfast)
		self.layout_main.addWidget(self.lunch)
		self.layout_main.addWidget(self.dinner)


def main():
	load_foods()
	app = QApplication (sys.argv)

	widget_main = QWidget()
	layout_main = QHBoxLayout()
	layout_tree = QVBoxLayout()
	layout_main.addLayout(layout_tree, 3)
	edit_filter = QLineEdit()
	global tree
	tree = QTreeWidget()
	tab = QTabWidget()
	tab.addTab(DayWidget(), "Mon")
	tab.addTab(DayWidget(), "Tue")
	tab.addTab(DayWidget(), "Wed")
	tab.addTab(DayWidget(), "Thu")
	tab.addTab(DayWidget(), "Fri")
	tab.addTab(DayWidget(), "Sat")
	tab.addTab(DayWidget(), "Sun")
	widget_main.setLayout(layout_main)
	layout_main.addWidget(tab, 7)
	layout_tree.addWidget(edit_filter)
	layout_tree.addWidget(tree)
	tree.setHeaderHidden(True)
	tree.setDragDropMode(QTreeWidget.DragOnly)
	for c in categories.values():
		parent = QTreeWidgetItem(tree)
		parent.setText(0, c["name"])
		parent.setFlags(Qt.ItemIsEnabled)
		for f in c["food"]:
			child = QTreeWidgetItem(parent)
			child.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			child.setText(0, f["name"])

	edit_filter.textChanged.connect(filter)
	widget_main.resize(640, 480)
	widget_main.show()
	sys.exit(app.exec_())

main()
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QStyle, QMainWindow, QAction, QFileDialog
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
	updated = pyqtSignal()

	def __init__(s, name):
		super().__init__()
		s.total_p = 0
		s.total_c = 0
		s.total_f = 0
		s.total_cal = 0
		s.layout_main = QVBoxLayout()
		s.setLayout(s.layout_main)
		s.table = QTableWidget()
		s.table.setColumnCount(7)
		s.table.setHorizontalHeaderLabels(["Name", "Amount, g", "Protein", "Fat", "Carbohydrates", "KCalories", "Remove"])
		s.table.verticalHeader().setVisible(False)
		s.layout_main.addWidget(QLabel(name))
		s.layout_main.addWidget(s.table)
		s.layout_main.setContentsMargins(0, 0, 0, 0)
		s.table.setDragEnabled(False)
		s.setAcceptDrops(True)

		s.table.insertRow(s.table.rowCount())
		item_total = QTableWidgetItem("total:")
		item_total.setFlags(Qt.ItemIsEnabled)
		s.table.setItem(s.table.rowCount() - 1, 0, item_total)
		item_amount = QTableWidgetItem("")
		item_amount.setFlags(Qt.ItemIsEnabled)
		s.table.setItem(s.table.rowCount() - 1, 1, item_amount)
		for i in range(2, 7):
			item = QTableWidgetItem("")
			item.setFlags(Qt.ItemIsEnabled)
			s.table.setItem(s.table.rowCount() - 1, i, item)

	def dragEnterEvent(self, e):
		e.accept()

	def dropEvent(s, e):
		s.table.insertRow(s.table.rowCount())
		item = tree.selectedItems()[0]
		name = item.text(0)
		food = foods[name]
		items = [QTableWidgetItem(name), QTableWidgetItem(str(food["p"])), QTableWidgetItem(str(food["f"])), QTableWidgetItem(str(food["c"])), QTableWidgetItem(str(food["cal"]))]
		shift = 0
		for i in range(len(items) + 1):
			if i == 1:
				shift = 1
				continue
			items[i - shift].setFlags(Qt.ItemIsEnabled)
			s.table.setItem(s.table.rowCount() - 1, i, items[i - shift])
		edit_amount = QLineEdit("100")
		edit_amount.editingFinished.connect(s.update)
		edit_amount.setValidator(QIntValidator(0, 10000000))
		s.table.setCellWidget(s.table.rowCount() - 1, 1, edit_amount)
		button_remove = QPushButton(s.style().standardIcon(QStyle.SP_TitleBarCloseButton), "")
		button_remove.clicked.connect(s.remove)
		s.table.setCellWidget(s.table.rowCount() - 1, 6, button_remove)
		s.update()

	def remove(s):
		obj = s.sender()
		for i in range(1, s.table.rowCount()):
			btn = s.table.cellWidget(i, 6)
			if btn == obj:
				s.table.removeRow(i)
				break
		s.update()

	def update(s):
		s.total_p = 0
		s.total_c = 0
		s.total_f = 0
		s.total_cal = 0
		for i in range(1, s.table.rowCount()):
			name = s.table.item(i, 0).text()
			f = foods[name]
			mass = int(s.table.cellWidget(i, 1).text()) / 100
			prot = f["p"] * mass
			carb = f["c"] * mass
			fat = f["f"] * mass
			cal = f["cal"] * mass
			s.total_p += prot
			s.total_c += carb
			s.total_f += fat
			s.total_cal += cal
			s.table.item(i, 2).setText(str(prot))
			s.table.item(i, 3).setText(str(fat))
			s.table.item(i, 4).setText(str(carb))
			s.table.item(i, 5).setText(str(cal))
		s.table.item(0, 2).setText(str(s.total_p))
		s.table.item(0, 3).setText(str(s.total_f))
		s.table.item(0, 4).setText(str(s.total_c))
		s.table.item(0, 5).setText(str(s.total_cal))
		s.updated.emit()


class DayWidget(QWidget):
	def __init__(s):
		super().__init__()
		s.breakfast = Meal("Breakfast")
		s.lunch = Meal("Lunch")
		s.dinner = Meal("Dinner")
		s.layout_main = QVBoxLayout()
		s.setLayout(s.layout_main)
		s.layout_main.addWidget(s.breakfast)
		s.layout_main.addWidget(s.lunch)
		s.layout_main.addWidget(s.dinner)
		s.layout_total = QHBoxLayout()
		s.layout_main.addLayout(s.layout_total)
		headers = [QLabel("Protein: "), QLabel("Fat: "), QLabel("Carbohydrates: "), QLabel("KCalories: ")]
		s.label_prot, s.label_fat, s.label_carb, s.label_cal = QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0")
		vars = [s.label_prot, s.label_fat, s.label_carb, s.label_cal]
		for i in range(len(vars)):
			s.layout_total.addWidget(headers[i])
			s.layout_total.addWidget(vars[i])
		s.lunch.updated.connect(s.update)
		s.breakfast.updated.connect(s.update)
		s.dinner.updated.connect(s.update)

	def update(s):
		total_p = s.lunch.total_p + s.dinner.total_p + s.breakfast.total_p
		total_c = s.lunch.total_c + s.dinner.total_c + s.breakfast.total_c
		total_f = s.lunch.total_f + s.dinner.total_f + s.breakfast.total_f
		total_cal = s.lunch.total_cal + s.dinner.total_cal + s.breakfast.total_cal
		s.label_carb.setText(str(total_c))
		s.label_cal.setText(str(total_cal))
		s.label_fat.setText(str(total_f))
		s.label_prot.setText(str(total_p))

	def save_to_xml(s, parent: minidom.Element):
		el = minidom.Element()
		el.tagName = "day"
		parent.appendChild(el)
		return el

tab: QTabWidget

class main_window(QMainWindow):
	def __init__(self):
		super().__init__()
		m = self.menuBar()
		action_save = QAction("Save")
		action_save.triggered.connect(self.save)
		m.addAction(action_save)

	def save(s):
		path = QFileDialog.getSaveFileName(s, "Save menu to", "", "Menu files (*.ffm)")
		if path is None or len(path) == 0:
			return
		file = open(path, "wb")
		doc = minidom.Document()
		doc.createElement("menu")
		for t in tab.children():
			t.save_to_xml(doc)
		file.write(doc.toprettyxml().encode())
		file.close()

def main():
	load_foods()
	app = QApplication (sys.argv)

	widget_main = main_window()
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
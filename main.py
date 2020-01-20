import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QStyle, QMainWindow, QAction, QFileDialog, qApp, QMessageBox
from PyQt5.QtGui import QIntValidator, QIcon

from food_loader import *

tree:QTreeWidget = 0


def fl(v:float):
	return "{:.2f}".format(v)


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
		s.name = name
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
		item = tree.selectedItems()[0]
		name = item.text(0)
		s.add_food(name, 100)

	def add_food(s, name, amount):
		s.table.insertRow(s.table.rowCount())
		food = foods[name]
		items = [QTableWidgetItem(name), QTableWidgetItem(fl(food["p"])), QTableWidgetItem(fl(food["f"])),
				 QTableWidgetItem(fl(food["c"])), QTableWidgetItem(fl(food["cal"]))]
		shift = 0
		for i in range(len(items) + 1):
			if i == 1:
				shift = 1
				continue
			items[i - shift].setFlags(Qt.ItemIsEnabled)
			s.table.setItem(s.table.rowCount() - 1, i, items[i - shift])
		edit_amount = QLineEdit(str(amount))
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
			s.table.item(i, 2).setText(fl(prot))
			s.table.item(i, 3).setText(fl(fat))
			s.table.item(i, 4).setText(fl(carb))
			s.table.item(i, 5).setText(fl(cal))
		s.table.item(0, 2).setText(fl(s.total_p))
		s.table.item(0, 3).setText(fl(s.total_f))
		s.table.item(0, 4).setText(fl(s.total_c))
		s.table.item(0, 5).setText(fl(s.total_cal))
		s.updated.emit()

	def save_to_xml(s, parent: minidom.Element, doc: minidom.Document):
		el = doc.createElement("meal")
		el.setAttribute("name", s.name)
		el.setAttribute("p", fl(s.total_p))
		el.setAttribute("f", fl(s.total_f))
		el.setAttribute("c", fl(s.total_c))
		el.setAttribute("cal", fl(s.total_cal))
		for i in range(1, s.table.rowCount()):
			dish = doc.createElement("dish")
			dish.setAttribute("name", s.table.item(i, 0).text())
			dish.setAttribute("amount", s.table.cellWidget(i, 1).text())
			dish.setAttribute("p", s.table.item(i, 2).text())
			dish.setAttribute("f", s.table.item(i, 3).text())
			dish.setAttribute("c", s.table.item(i, 4).text())
			dish.setAttribute("cal", s.table.item(i, 5).text())
			el.appendChild(dish)
		parent.appendChild(el)
		return el

	def load_from_xml(s, el: minidom.Element):
		for dish in el.getElementsByTagName("dish"):
			name = dish.getAttribute("name")
			amount = dish.getAttribute("amount")
			s.add_food(name, amount)

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
		s.label_carb.setText(fl(total_c))
		s.label_cal.setText(fl(total_cal))
		s.label_fat.setText(fl(total_f))
		s.label_prot.setText(fl(total_p))

	def save_to_xml(s, parent: minidom.Element, doc: minidom.Document):
		el = doc.createElement("day")
		s.lunch.save_to_xml(el, doc)
		s.dinner.save_to_xml(el, doc)
		s.breakfast.save_to_xml(el, doc)
		parent.appendChild(el)
		return el

	def load_from_xml(s, el: minidom.Element):
		d = {a:b for (a,b) in map(lambda e:(e.getAttribute("name"), e), el.getElementsByTagName("meal"))}
		s.lunch.load_from_xml(d["Lunch"])
		s.dinner.load_from_xml(d["Dinner"])
		s.breakfast.load_from_xml(d["Breakfast"])


class main_widget(QWidget):
	def __init__(s):
		super().__init__()
		layout_main = QHBoxLayout()
		layout_tree = QVBoxLayout()
		layout_main.addLayout(layout_tree, 3)
		edit_filter = QLineEdit()
		global tree
		tree = QTreeWidget()
		s.tab = QTabWidget()
		days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
		s.dayTabs = {}
		for d in days:
			dtab = DayWidget()
			s.dayTabs[d] = dtab
			s.tab.addTab(dtab, d)
		layout_main.addWidget(s.tab, 7)
		layout_tree.addWidget(edit_filter)
		layout_tree.addWidget(tree)
		tree.setHeaderHidden(True)
		tree.setDragDropMode(QTreeWidget.DragOnly)
		s.setLayout(layout_main)
		for c in categories.values():
			parent = QTreeWidgetItem(tree)
			parent.setText(0, c["name"])
			parent.setFlags(Qt.ItemIsEnabled)
			for f in c["food"]:
				child = QTreeWidgetItem(parent)
				child.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
				child.setText(0, f["name"])
		edit_filter.textChanged.connect(s.filter)

	def filter(s, st):
		items = tree.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive)
		for item in items:
			text = item.text(0)
			hidden = st.lower() not in text.lower()
			item.setHidden(hidden)
			item.setExpanded(False)
			if hidden == False:
				parent = item.parent()
				if parent is not None:
					parent.setHidden(False)
					parent.setExpanded(True)


class main_window(QMainWindow):
	def __init__(s):
		super().__init__()
		s.last_path = ""
		m = s.menuBar()
		s.mw = main_widget()
		action_save_as = QAction("&Save as", s)
		action_save_as.setShortcut('Ctrl+Shift+S')
		action_save_as.triggered.connect(s.save_as)

		action_save = QAction("&Save", s)
		action_save.setShortcut('Ctrl+S')
		action_save.triggered.connect(s.save)

		action_open = QAction("&Open", s)
		action_open.setShortcut('Ctrl+O')
		action_open.triggered.connect(s.open)

		file_menu = m.addMenu('&File')
		file_menu.addAction(action_open)
		file_menu.addAction(action_save)
		file_menu.addAction(action_save_as)

		action_exit = QAction('&Exit', s)
		action_exit.setShortcut('Ctrl+Q')
		action_exit.triggered.connect(qApp.quit)

		file_menu.addAction(action_exit)
		s.setCentralWidget(s.mw)

	def save_as(s):
		path = QFileDialog.getSaveFileName(s, "Save menu to", "", "Menu files (*.ffm)", ".ffm", QFileDialog.DontConfirmOverwrite)[0]
		if path is None or len(path) == 0:
			return
		if not path.endswith(".ffm"):
			path += ".ffm"
		if QFile(path).exists():
			res = QMessageBox.question(s, "File exists", "File '" + path + "' exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
			if res == QMessageBox.No:
				return
		s.do_save(path)

	def save(s):
		if len(s.last_path) == 0 or s.last_path == ".ffm":
			s.save_as()
		else:
			s.do_save(s.last_path)
		return

	def do_save(s, path):
		if path is None or len(path) == 0:
			return
		s.last_path = path
		file = open(path, "wb")
		doc = minidom.Document()
		menu_element = doc.createElement("menu")
		doc.appendChild(menu_element)
		for name, t in s.mw.dayTabs.items():
			dayel = t.save_to_xml(menu_element, doc)
			dayel.setAttribute("name", name)
		file.write(doc.toprettyxml().encode())
		file.close()

	def cleanup(s):
		s.mw.dayTabs.clear()
		while s.mw.tab.count():
			s.mw.tab.removeTab(0)

	def load_xml(s, path):
		doc = minidom.parse(path)
		root:minidom.Element = doc.documentElement
		days = root.getElementsByTagName("day")
		for d in days:
			day = DayWidget()
			n = d.getAttribute("name")
			s.mw.dayTabs[n] = day
			day.load_from_xml(d)
			s.mw.tab.addTab(day, n)

	def open(s):
		path = QFileDialog.getOpenFileName(s, "Open menu from", "", "Menu files (*.ffm)", ".ffm")[0]
		if path is None or len(path) == 0:
			return
		s.cleanup()
		s.load_xml(path)


def main():
	load_foods()
	app = QApplication (sys.argv)
	window_main = main_window()
	window_main.resize(640, 480)
	window_main.show()
	sys.exit(app.exec_())


main()
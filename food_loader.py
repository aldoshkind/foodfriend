from xml.dom import minidom

doc = minidom.parse("food_ru.xml")

cats_xml = doc.getElementsByTagName("category")

categories = {}
foods = {}

def get_value(e, tag):
	vels = e.getElementsByTagName(tag)
	vel = vels[0]
	vdat = vel.firstChild.data
	return vdat

def load_foods():
	for c in cats_xml:
		ids = c.getElementsByTagName("id")
		id = ids[0]
		id = id.firstChild.data
		id = int(id)
		print(id)
		name = c.getElementsByTagName("name")[0].firstChild.data
		print(name)
		categories[id] = {}
		categories[id]["name"] = name
		categories[id]["food"] = []
	food_xml = doc.getElementsByTagName("food")
	for f in food_xml:
		id = int(get_value(f, "id"))
		cat_id = int(get_value(f, "c_id"))
		name = get_value(f, "n")
		protein = float(get_value(f, "p"))
		fat = float(get_value(f, "f"))
		carb = float(get_value(f, "c"))
		cal = float(get_value(f, "cal"))
		food = {"name": name, "c": carb, "f": fat, "p": protein, "cal": cal, "id": id, "cat": cat_id}
		categories[cat_id]["food"].append(food)
		foods[name] = food
	print(foods)
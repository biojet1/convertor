from decimal import *
#from sys import argv
#_ = argv.pop(0)



units_xml=r'''C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units1.xml'''

no_symbol = []
no_desc = []
ids={}

def doUnit(cur):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = cur.getAttribute("description")
	prio = cur.getAttribute("priority")
	f = cur.getAttribute("factor")
	y = cur.getAttribute("y") or "0"
	symbol = cur.getAttribute("symbol")
	# print("doUnit: %r %r %r %r %r %r" % (name, desc, prio, symbol, f, y) )
	if not symbol:
		no_symbol.append((name, desc))
	if not desc:
		no_desc.append((name, desc))
	if not id:
		# raise RuntimeError("No id")
		pass
	elif id.lower() in ids:
		raise RuntimeError("Duplicate id %r" % id)
	else:
		ids[id.lower()] = name
	assert Decimal(f).is_finite()
	assert (1/Decimal(f)).is_finite()
	assert Decimal(y).is_finite()

def doSub(cur):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = cur.getAttribute("description")
	prio = cur.getAttribute("priority")
	print("doSub: %r %r %r %r" % (name, id, desc, prio) )
	if not name:
		raise RuntimeError("No name")
	if not id:
		raise RuntimeError("No id")
	elif id.lower() in ids:
		raise RuntimeError("Duplicate id %r" % id)
	else:
		ids[id.lower()] = name
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "unit":
				doUnit(x)
			else:
				raise RuntimeError(t)

def doGroup(root, parent=None):
	id = root.getAttribute("id")
	name = root.getAttribute("name")
	if parent:
		print("Group: %r %s" % (name, id) )
		if not name:
			raise RuntimeError("No name")
		if not id:
			raise RuntimeError("No id")
		elif id.lower() in ids:
			raise RuntimeError("Duplicate id %r" % id)
		else:
			ids[id.lower()] = name
	cur = root.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "sub":
				doSub(x)
			elif t == "group":
				if parent:
					raise RuntimeError(t)
				doGroup(x, x)
			else:
				raise RuntimeError(t)


from xml.dom.minidom import parse, parseString
dom = parse(units_xml)
root = dom.documentElement
doGroup(root)


# if no_symbol:
	# for (name, desc) in no_symbol:
		# print("\tNOSYM: %r %r" % (name, desc) )
# if no_desc:
	# for (name, desc) in no_desc:
		# print("\tNODES: %r %r" % (name, desc) )

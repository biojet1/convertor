from decimal import *
from random import randint
from sys import stdout, stderr

nos=set()

def attrs(cur):
	a = cur.attributes
	n = a.length
	while n > 0:
		n -= 1
		x = a.item(n)
		yield (x.localName, x.value)

def doCheckNo(cur, add=True):
	no = cur.getAttribute("no")
	if no:
		no = int(no, 16)
		if no >= 0xFFFF or no <= 0x8000:
			raise RuntimeError("no not in range %r %r" % (no, cur.getAttribute("no")))
		elif add:
			if no in nos:
				raise RuntimeError("Duplicate no %r" % no)
			else:
				nos.add(no)
	elif add:
		x = randint(0x8000+1, 0xFFFF-1)
		while x in nos:
			x = randint(0x8000+1, 0xFFFF-1)
		nos.add(x)
		no = x
		x = "%04X" % x
		cur.setAttribute("no", x)
		stderr.write("New no %r" % x)
	return no

no_symbol = []
no_desc = []
ids={}
conv_map={}
same_list = []

def doUnit(cur):
	id=None
	y="0"
	symbol=None
	for (k, v) in attrs(cur):
		if k == "id": id = v
		elif k == "name": name = v
		# elif k == "description": desc = v
		elif k == "priority": prio = v
		elif k == "factor": f = v
		elif k == "y": y = v
		elif k == "symbol": symbol = v
		elif k == "no": pass
		else: raise RuntimeError("Unexpected attribute %r=%r" % (k, v))

	# id = cur.getAttribute("id")
	# name = cur.getAttribute("name")
	# desc = cur.getAttribute("description")
	# prio = cur.getAttribute("priority")
	# f = cur.getAttribute("factor")
	# y = cur.getAttribute("y") or "0"
	# symbol = cur.getAttribute("symbol")
	# zf = cur.getAttribute("zf")
	# if desc:
		# cur.appendChild(cur.ownerDocument.createTextNode(desc.strip().strip('.')))
		# cur.removeAttribute("description")
	# print("doUnit: %r %r %r %r %r %r" % (name, desc, prio, symbol, f, y) )
	# if not desc:
		# no_desc.append((name, desc))
	if not id:
		# raise RuntimeError("No id")
		pass
	elif id.lower() in ids:
		raise RuntimeError("Duplicate id %r" % id)
	else:
		ids[id.lower()] = name
	no = doCheckNo(cur)
	if not symbol:
		no_symbol.append((name, no))
	if no in conv_map:
		 raise RuntimeError("no %X in conv_map" % no)

	assert Decimal(f).is_finite()
	assert (1/Decimal(f)).is_finite()
	assert Decimal(y).is_finite()
	assert no not in conv_map
	conv_map[no] = (Decimal(f), Decimal(y), name)
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "same":
				iB = doCheckNo(x, False)
				vB = Decimal(x.getAttribute("equals"))
				vA = Decimal(x.getAttribute("value") or 1)
				same_list.append((no, iB, vB, vA))
			else:
				raise RuntimeError("unexpected element %r" % x.tagName)
		elif t == x.TEXT_NODE:
			if x.previousSibling:
				if x.data.strip():
					raise RuntimeError("unexpected TEXT_NODE %r" % x.data.strip())
		elif t in (x.COMMENT_NODE, ):
			pass
		else:
			raise RuntimeError("unexpected node %r %r" % (t, x.nodeName))

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
	doCheckNo(cur)
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
		elif t == x.TEXT_NODE:
			if x.previousSibling:
				if x.data.strip():
					raise RuntimeError("unexpected TEXT_NODE %r" % x.data.strip())
		elif t in (x.COMMENT_NODE, ):
			pass
		else:
			raise RuntimeError("unexpected node %r %r" % (t, x.nodeName))

def doGroup(root, parent=None):
	id = root.getAttribute("id")
	name = root.getAttribute("name")
	if root.tagName == "group":
		print("Group: %r %s" % (name, id) )
		if not name:
			raise RuntimeError("No name")
		if not id:
			raise RuntimeError("No id")
		elif id.lower() in ids:
			raise RuntimeError("Duplicate id %r" % id)
		else:
			ids[id.lower()] = name
		doCheckNo(root)
	elif root.tagName == "sub":
		return doSub(root)
	else:
		assert(parent is None)
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
		elif t == x.TEXT_NODE:
			if x.data.strip():
				raise RuntimeError("unexpected TEXT_NODE %r" % x.data.strip())
		elif t in (x.COMMENT_NODE, ):
			pass
		else:
			raise RuntimeError("unexpected node %r" % t)

def on_xml_doc(doc, ctx):
	doGroup(doc.documentElement)

def on_xml_end(ctx):
	i = 0
	for (noA, noB, valueB, valueA) in same_list:
		a = conv_map[noA]
		b = conv_map[noB]
		valueA = ((valueA*a[0]) + a[1] - b[1])/b[0]
		if valueA != valueB:
			stderr.write("\rFactor Error %r/%r %r %r" % (a, b, valueA, valueB))
			raise RuntimeError("Factor [%r%X(%s)] != [%r%X(%s)]" % (a[2], noA, valueA, b[2], noB, valueB))
		else:
			i += 1
			stdout.write("\rCHECKED %r/%r [%d]" % (a[2], b[2], i))
	# for A in checkf:
		# a = checkf[A]
		# if a[2] is not None:
			# (B, valueB) = a[2]
			# b = checkf[B]
			# valueA = (a[0] + a[1] - b[1])/b[0]
			# if valueA != valueB:
				# raise RuntimeError("Factor check [%r%X(%s)] != [%r%X(%s)]" % (b[3], B, valueB, a[3],  A, valueA))
			# else:
				# i += 1
				# stdout.write("\rCHECKED %r [%d]" % (a[3], i))

"""
alterx -np K:\wrx\android\convertor\check.py C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units1.xml
alterx -np K:\wrx\android\convertor\check.py C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units1.xml
mee --cd K:\wrx\android\convertor -- nmake check
"""

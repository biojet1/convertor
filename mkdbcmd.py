from sys import stdout
import re
units = []
usageMap = {}
sukiMap = {}
flagTag = {"priority":usageMap, "suki":sukiMap}
types_map = {}

def children(cur):
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		yield (x, t)

def childrenR(cur):
	cur = cur.lastChild
	while cur:
		x = cur
		(cur, t) = (x.previousSibling, x.nodeType)
		yield (x, t)

def writeln(x):
	stdout.write(x.encode("UTF-8"))
	stdout.write(b'\n')

def doUnit(cur, type, order):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = cur.getAttribute("description")
	prio = int(cur.getAttribute("priority") or 0)
	f = cur.getAttribute("factor")
	y = cur.getAttribute("y") or "0"
	symbol = cur.getAttribute("symbol")
	no = int(cur.getAttribute("no"), 16)
	for (x, t) in children(cur):
		if t == x.ELEMENT_NODE:
			if x.tagName in ('same',):
				pass
			else:
				raise RuntimeError("unexpected element %r" % x.tagName)
		elif t == x.TEXT_NODE:
			if x.previousSibling:
				if x.data.strip():
					raise RuntimeError("unexpected TEXT_NODE %r" % x.data.strip())
			else:
				x = x.data.strip()
				desc = re.sub(r'\s+', ' ', x)
		elif t in (x.COMMENT_NODE, ):
			pass
		else:
			raise RuntimeError("unexpected node %r %r" % (t, x.nodeName))
	units.append((no, name, desc, type, f, y, symbol, 0, order))

def toSQLq(x):
	return '"' + x.replace('"', '""') + '"'


def doSub(cur):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = None
	no = int(cur.getAttribute("no"), 16)
	if not name:
		raise RuntimeError("No name")
	order = cur.getAttribute("order")
	if order:
		order=int(order)
	else:
		order=0
	for (x, t) in childrenR(cur):
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "unit":
				order+=1
				doUnit(x, no, order)
			else:
				raise RuntimeError(t)
		elif t == x.TEXT_NODE:
			if x.previousSibling:
				if x.data.strip():
					raise RuntimeError("unexpected TEXT_NODE %r" % x.data.strip())
			else:
				x = x.data.strip()
				desc = re.sub(r'\s+', ' ', x)
		elif t in (x.COMMENT_NODE, ):
			pass
		else:
			raise RuntimeError("unexpected node %r %r" % (t, x.nodeName))
	e = types_map.get(no)
	if not e:
		types_map[no] = e = {}
		e["name"] = name
		e["desc"] = desc
		e["id"] = id
		e["batch"] = 0
	elif e["name"] != name:
		raise RuntimeError("%X has different name %r and %r" % (no, e["name"], name))
	elif e["id"] != id:
		raise RuntimeError("%r has different id %r and %r" % (name, e["id"], id))
	elif e["desc"]:
		if desc:
			raise RuntimeError("%r has dual description %r and %r" % (name, e["desc"], desc))
	elif desc:
		e["desc"] = desc
	e["batch"] += 1

def doGroup(root, parent=None):
	id = root.getAttribute("id")
	name = root.getAttribute("name")
	if root.tagName == "group":
		if not name:
			raise RuntimeError("No name")
		if not id:
			raise RuntimeError("No id")
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
	cur = doc.documentElement
	ft_map = flagTag.get(cur.tagName, None)
	if ft_map is not None:
		i = 0
		for (n, t) in childrenR(cur):
			if t == n.ELEMENT_NODE:
				t = n.tagName
				if t == "sub":
					i += 1
					no = int(n.getAttribute("no"), 16)
					assert no not in ft_map
					ft_map[no] = i
	else:
		doGroup(cur)

def on_xml_end(ctx):
	tables = {}
	tables["unit"] =[
				("id", "INTEGER UNIQUE"),
				("name", "TEXT"),
				("description", "TEXT"),
				("flag", "INTEGER"),
				("used", "INTEGER DEFAULT 0"),
				("liked", "INTEGER DEFAULT 0"),
				("type", "INTEGER"),
				("f", "TEXT"),
				("y", "TEXT"),
				("symbol", "TEXT"),
			];
	tables["kind"] =[
				("id", "INTEGER UNIQUE"),
				("name", "TEXT"),
				("description", "TEXT"),
				("flag", "INTEGER"),
				("used", "INTEGER DEFAULT 0"),
				("liked", "INTEGER DEFAULT 0"),
				# favorite
				# disable
			];

	for k in tables:
		writeln("CREATE TABLE %s (%s);" % (k, ", ".join(["%s %s" % (name, type) for (name, type) in tables[k]])))
	c_units=0
	c_types=0
	for no in types_map:
		e = types_map[no]
		name = e["name"]
		desc = e["desc"]
		flag = 0
		c_types += 1
		used = usageMap.get(no, 0)
		liked = sukiMap.get(no)
		_ = ", ".join(_ for _ in ("0x%X" % no, toSQLq(name), toSQLq(desc), str(flag), str(used), liked and ("0x%X" % (liked|(1<<62))) or '0'))
		writeln("INSERT INTO kind VALUES(%s);" % (_, ))

	for (no, name, desc, type, f, y, symbol, flag, used) in units:
		c_units += 1
		liked = sukiMap.get(no, 0)
		_ = ", ".join(_ for _ in ("0x%X" % no, toSQLq(name), toSQLq(desc), str(flag), str(used)
			, (liked and ("0x%X" % (liked|(1<<62))) or '0')
			, str(type), toSQLq(f), toSQLq(y), toSQLq(symbol)))
		writeln("INSERT INTO unit VALUES(%s);" % (_, ))
	writeln("/*%d types; %d units;*/" % (c_types, c_units))

"""
mee --cd K:\wrx\android\convertor-db -- nmake 
"""
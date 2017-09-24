from sys import stdout
import re

def writeln(x):
	stdout.write(x.encode("UTF-8"))
	stdout.write(b'\n')

def doUnit(cur, type):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = cur.getAttribute("description")
	prio = int(cur.getAttribute("priority") or 0)
	f = cur.getAttribute("factor")
	y = cur.getAttribute("y") or "0"
	symbol = cur.getAttribute("symbol")
	no = int(cur.getAttribute("no"), 16)
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
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
	writeln("INSERT INTO unit VALUES(0x%X, %s, %s, %d, 0, 0x%X, %s, %s, %s);" % (no, toSQLq(name), toSQLq(desc), prio, type, toSQLq(f), toSQLq(y), toSQLq(symbol)))

def toSQLq(x):
	# x = repr(x)
	# if x.startswith('u'):
		# x = x[1:]
	# return x
	return '"' + x.replace('"', '""') + '"'

def doSub(cur):
	id = cur.getAttribute("id")
	name = cur.getAttribute("name")
	desc = cur.getAttribute("description")
	prio = cur.getAttribute("priority") or None
	no = int(cur.getAttribute("no"), 16)
	if not name:
		raise RuntimeError("No name")
	if not id:
		raise RuntimeError("No id")
	if prio:
		prio=int(prio)
	else:
		prio=0
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "unit":
				doUnit(x, no)
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
	writeln("INSERT INTO kind VALUES(0x%X, %s, %s, %d, 0);" % (no, toSQLq(name), toSQLq(desc), prio))

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
	doGroup(doc.documentElement);

def on_xml_start(ctx):
	tables = {}
	tables["unit"] =[
	            ("id", "INTEGER UNIQUE"),
                ("name", "TEXT"),
                ("description", "TEXT"),
                ("priority", "INTEGER"),
                ("used", "INTEGER DEFAULT 0"),
                ("type", "INTEGER"),
                ("f", "TEXT"),
                ("y", "TEXT"),
               ("symbol", "TEXT"),
			   ];
	tables["kind"] =[
	            ("id", "INTEGER UNIQUE"),
                ("name", "TEXT"),
                ("description", "TEXT"),
                ("priority", "INTEGER"),
                ("used", "INTEGER DEFAULT 0"),
			   ];
	for k in tables:
		writeln("CREATE TABLE %s (%s);" % (k, ", ".join(["%s %s" % (name, type) for (name, type) in tables[k]])));
"""
		
alterx -np K:\wrx\android\convertor\mkdbcmd.py C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units1.xml
alterx -np K:\wrx\android\convertor\mkdbcmd.py C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units1.xml >C:\ProgramData\home\AndroidStudio2.3\AndroidStudioProjects\MasterFlow\app\src\main\assets\units.sql 
"""
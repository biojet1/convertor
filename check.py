from decimal import Decimal, getcontext
from random import randint
from sys import stdout, stderr
PI=None
def calcuator():
	from ast import Call, Name, Attribute, Load, copy_location, NodeTransformer, fix_missing_locations, Str, parse, Pow
	from decimal import Decimal, getcontext
	class Num2Decimal(NodeTransformer):
		def visit_Num(self, node):
			return Call(Name('Decimal', Load()), [Str(s=str(node.n))], [], None, None)
	class PowChange(NodeTransformer):
		def visit_BinOp(self, node):
			if node.op is Pow:
				return Call(Attribute(Call(Name('getcontext',Load()), [], [], None, None),'power',Load()),[node.left, node.right],	[],	None,	None)
			return node
	def pi():
		getcontext().prec += 2  # extra digits for intermediate steps
		three = Decimal(3)      # substitute "three=3.0" for regular floats
		lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
		while s != lasts:
			lasts = s
			n, na = n+na, na+8
			d, da = d+da, da+32
			t = (t * n) / d
			s += t
		getcontext().prec -= 2
		return +s               # unary plus applies the new precision
	getcontext().prec = 64
	global PI
	PI=pi()
	def fn(expr):
		n1 = parse(expr, mode='eval')
		n0 = Num2Decimal().visit(PowChange().visit(n1))
		fix_missing_locations(n0) 
		return eval(compile(n0, 'q', 'eval'))
	return fn

dcalc=calcuator()


nos=set()

def attrs(cur):
	a = cur.attributes
	n = a.length
	while n > 0:
		n -= 1
		x = a.item(n)
		yield (x.localName, x.value)

def doCheckNo(cur, add=True, checkDup=True):
	no = cur.getAttribute("no")
	if no:
		no = int(no, 16)
		if no >= 0xFFFF or no <= 0x8000:
			raise RuntimeError("no not in range %r %r" % (no, cur.getAttribute("no")))
		elif add:
			if no in nos:
				if checkDup:
					raise RuntimeError("Duplicate no %X" % no)
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
	else:
		raise RuntimeError("no expected")
	return no

no_symbol = []
no_desc = []
conv_map={}
same_list = []
types_map={}
def doCheckName(cur):
	name = cur.getAttribute("name")
	if name[0].isdigit():
		pass
	elif not name[0].isupper():
		n = name[0].upper() + name[1:]
		print("NotTitle: %r %r" % (name, n) )
		assert(n[0].isupper())
		cur.setAttribute("name", n)
def doCheckEval(cur):
	x = cur.getAttribute("eval")
	if not x:
		assert cur.getAttribute("factor")
		return
	y = cur.getAttribute("factor")
	if not y:
		assert cur.getAttribute("eval")
		return
	e = dcalc(x)
	f = Decimal(y)
	if f == e:
		return
	raise RuntimeError("Eval %r [%r == %r] != [%r == %r] %r" % (cur.getAttribute("name"), x,e,y,f, e-f))


def doUnit(cur):
	id=None
	y="0"
	f=None
	symbol=None
	for (k, v) in attrs(cur):
		if k == "id": id = v
		elif k == "name": name = v
		elif k == "eval": e=v
		# elif k == "ref": pass
		elif k == "href": pass
		elif k == "factor": f = v
		elif k == "y": y = v
		elif k == "symbol": symbol = v
		elif k == "no": pass
		else: raise RuntimeError("Unexpected attribute %r=%r" % (k, v))
	no = doCheckNo(cur)
	if not symbol:
		no_symbol.append((name, no))
	if no in conv_map:
		 raise RuntimeError("no %X in conv_map" % no)
	doCheckName(cur)
	if f:
		f=Decimal(f) 
	else:
		f=dcalc(e) 
	assert f.is_finite()
	assert (1/f).is_finite()
	assert Decimal(y).is_finite()
	assert no not in conv_map
	assert no not in types_map
	doCheckEval(cur)
	conv_map[no] = (f, Decimal(y), name)
	cur = cur.firstChild
	while cur:
		x = cur
		(cur, t) = (x.nextSibling, x.nodeType)
		if t == x.ELEMENT_NODE:
			t = x.tagName
			if t == "same":
				iB = doCheckNo(x, False)
				vB = dcalc(x.getAttribute("equals"))
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
	id = None
	for (k, v) in attrs(cur):
		if k == "id": id = v
		elif k == "name": name = v
		elif k == "no": pass
		# elif k == "priority": prio = v
		else: raise RuntimeError("Invalid Attribute %r" % k)

	# name = cur.getAttribute("name")
	# desc = cur.getAttribute("description")
	# prio = cur.getAttribute("priority")
	print("doSub: %r %r" % (name, id) )
	if not name:
		raise RuntimeError("No name")
	no = doCheckNo(cur, checkDup=False)
	# assert no not in types_map
	assert no not in conv_map
	
	# types_map[no] = (name, id)
	
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
	e = types_map.get(no)
	if not e:
		types_map[no] = e = (name, id)
	elif e[0] != name:
		raise RuntimeError("%X has different name %r and %r" % (no, e[0], name))
	elif e[1] != id:
		raise RuntimeError("%r has different id %r and %r" % (name, e[1], id))


def doGroup(root, parent=None):
	id = root.getAttribute("id")
	name = root.getAttribute("name")
	if root.tagName == "group":
		print("Group: %r %s" % (name, id) )
		if not name:
			raise RuntimeError("No name")
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

flagTag = set(("priority", "suki"))

def on_xml_doc(doc, ctx):
	cur = doc.documentElement
	if cur.tagName in flagTag:
		pass
	else:
		doGroup(cur)

def on_xml_end(ctx):
	i = 0
	for (noA, noB, valueB, valueA) in same_list:
		stderr.write("\rCHECKED %X/%X %r/%r" % (noA, noB, valueB, valueA))
		a = conv_map[noA]
		b = conv_map[noB]
		valueA = ((valueA*a[0]) + a[1] - b[1])/b[0]
		if valueA != valueB:
			ctx = getcontext().copy()
			ctx.prec -= 2
			stderr.write("Factor error %r and %r\n" % (a[2], b[2]))
			stderr.write("a = %r\n" % (a,))
			stderr.write("b = %r\n" % (b,))
			stderr.write("A = %r\n" % (valueA))
			stderr.write("B = %r\n" % (valueB))
			stderr.write("%r, %r \n" % (valueA.normalize(ctx),valueB.normalize(ctx)))
			if valueA.normalize(ctx).compare(valueB.normalize(ctx)) != 0:
				raise RuntimeError("Factor [%r%X(%s)] != [%r%X(%s)]" % (a[2], noA, valueA, b[2], noB, valueB))
		else:
			i += 1
			stderr.write("\rCHECKED %r/%r [%d]" % (a[2], b[2], i))
	stderr.write("\nTypes %d; Units %d;" % (len(types_map), len(conv_map)))

"""
mee --cd K:\wrx\android\convertor-db -- nmake check
mee --cd K:\wrx\android\convertor-db -- nmake unitsdb
"""

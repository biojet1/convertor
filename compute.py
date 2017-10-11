def calcuator():
	from ast import Call, Name, Attribute, Load, copy_location, NodeTransformer, fix_missing_locations, Str, parse, Pow
	from decimal import Decimal, getcontext
	class Num2Decimal(NodeTransformer):
		def visit_Num(self, node):
			return Call(Name('Decimal', Load()), [Str(s=str(node.n))], [], None, None)
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
		n0 = Num2Decimal().visit(n1)
		fix_missing_locations(n0) 
		return eval(compile(n0, 'q', 'eval'))
	return fn

dcalc=calcuator()

from decimal import *
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
    return +s

# unary plus applies the new precision
getcontext().prec = 64
print(pi(), "Pi")
print((149597870700*648000)/pi(), "Parsec EB29")
print(pi()/648000, "Parsec of AU")
print(Decimal(1200)/Decimal(3937), "US survey foot")
print(Decimal(660)*Decimal(1200)/Decimal(3937), "Furlong US survey foot")
print(Decimal(66)*Decimal(1200)/Decimal(3937), "Chain (US survey foot)")
print(Decimal(66)*Decimal(1200)/Decimal(3937)/Decimal(100), "Link (US survey foot)")
print(Decimal('0.3048')*5280*3, "League (US)?")
print(dcalc('(1200/3937)*5280*3'), "League (US)?")


import ast
from ast import Call, Name, Load, copy_location, NodeTransformer, fix_missing_locations, Str
# print(ast.dump(ast.parse("Decimal(1200)/Decimal(3937)"),annotate_fields=False))
# print(ast.dump(ast.parse("Decimal(1200)"),annotate_fields=False))
# print(ast.dump(ast.parse("+Decimal(1200)"),annotate_fields=False))
print(ast.dump(ast.parse("23**2"),annotate_fields=False))
print(ast.BinOp._fields)
print(ast.Pow)
print(ast.dump(ast.parse("getcontext().power(2,4)")))


from sys import stderr
def testexp(x):
	n1=ast.parse(x,mode='eval')
	fix_missing_locations(n1) 
	print("A", x,"=",eval(compile(n1, 'q', 'eval')))
	print("A", x,"=",dcalc(x))
	
testexp("1200/3937")
testexp("1200/PI")
testexp("1200**23")


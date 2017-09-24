import re, sys, os

nos = set()

def on_xml_etree(doc, ctx):
	root = doc.getroot()
	for e in root.xpath(r".//*[@no]"):
		if e.tag in ('same',):
			pass
		else:
			sn = no = e.attrib.get("no")
			no = int(no, 16)
			if no >= 0xFFFF or no <= 0x8000:
				raise RuntimeError("no not in range %r %r" % (no, sn))
			elif no in nos:
				raise RuntimeError("Duplicate no %r" % no)
			else:
				nos.add(no)
def on_xml_end(ctx):
	from random import randint
	from sys import stdout, stderr
	x = randint(0x8000+1, 0xFFFF-1)
	while x in nos:
		x = randint(0x8000+1, 0xFFFF-1)
	nos.add(x)
	no = x
	x = "%04X" % x
	stderr.write("Current total nos: %r\n" % len(nos))
	stdout.write("New no: %s\n" % x)

r"""
alterx -np K:\wrx\android\convertor\newno.py 
"""
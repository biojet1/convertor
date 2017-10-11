import sys, os
import json

name_map={}

def on_xml_etree(doc, ctx):
	root = doc.getroot()
	# for e in root.findall(r".//sub[@no]"):
		# name = e.get("name")
		# no = e.get("no")
		# no = int(no, 16)
		# name_map[no] = name
	for e in root.findall(r".//same[@no]"):
		name = e.get("name")
		no = e.get("no")
		no = int(no, 16)
		n2 = name_map[no]
		if n2:
			if name: name = name.lower()
			if n2.lower() != name:
				sys.stderr.write("%X %r %r -> %r\n" % (no, e.tag, name, n2))
				e.set("name", n2)

def on_xml_start(ctx):
	global name_map
	name_map=eval(sys.stdin.read())
	# import pprint
	# pp = pprint.PrettyPrinter(depth=6)
	# pp.pprint(name_map)

r"""
alterx -np K:\wrx\android\convertor-db\list_types.py K:\wrx\android\convertor-db
mee --cd K:\wrx\android\convertor-db -- nmake check_names
"""
import sys, os

name_map={}

def on_xml_etree(doc, ctx):
	root = doc.getroot()
	for e in root.findall(r".//sub[@no]"):
		name = e.get("name")
		no = e.get("no")
		no = int(no, 16)
		name_map[no] = name
	for e in root.findall(r".//unit[@no]"):
		name = e.get("name")
		no = e.get("no")
		no = int(no, 16)
		name_map[no] = name

def on_xml_end(ctx):
	import pprint
	pp = pprint.PrettyPrinter(depth=6)
	pp.pprint(name_map)
r"""
alterx -np K:\wrx\android\convertor-db\list_types.py K:\wrx\android\convertor-db

"""
import re, sys, os
from lxml import etree
from io import StringIO, BytesIO

ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'sch': 'http://schema.org/',}

#	"urn:node:acltinqg85ttz77ghajkzeg80" "http://dgcidol.jp/" 
def on_xml_etree(doc, ctx):
	root = doc.getroot()
	seen = set()
	def found(cur):
		no = cur.get("no")
		name = cur.get("name")
		sub = etree.Element(cur.tag)
		sub.set("no", no)
		sub.set("name", name)
		print etree.tostring(sub)
	if root.tag == "sub":
		found(root)
	else:
		for e in root.findall(r".//sub[@no]"):
			found(e)

r"""
alterx -np K:\wrx\android\convertor\list_types.py K:\wrx\android\convertor

"""
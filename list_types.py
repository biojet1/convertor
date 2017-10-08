import sys, os

def on_xml_etree(doc, ctx):
	root = doc.getroot()
	seen = set()
	def found(cur):
		no = cur.get("no")
		name = cur.get("name")
		sub = ctx.etree.Element(cur.tag)
		sub.set("no", no)
		sub.set("name", name)
		sys.stdout.write(ctx.etree.tostring(sub))
		sys.stdout.write("\n")
	if root.tag == "sub":
		found(root)
	else:
		for e in root.findall(r".//sub[@no]"):
			found(e)

r"""
alterx -np K:\wrx\android\convertor-db\list_types.py K:\wrx\android\convertor-db

"""
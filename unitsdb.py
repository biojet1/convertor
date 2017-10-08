java=r'''package biojet1.github.com.convertor;
public class UnitsDB {
    static final String DATABASE_NAME = "units";
    static final int DATABASE_VERSION = %d;
}'''
from time import time
from sys import stdout, argv
from re import sub

#stdout.write(java % (int(time()/60), ))
f = argv[1]
s = open(f, 'rb').read().decode("ASCII")
def inc(m):
	n = int(m.group(2))
	return m.group(1) + str(n+1) + m.group(3)
stdout.write(sub(r'\s+', ' ', s) + "\n")
s2 = sub("(_VERSION\s*=\s*)(\d+)(\s*;)", inc, s)
if s != s2:
	h = open(f, 'wb')
	h.write(s2.encode("ASCII"))
	h.close()
	stdout.write(sub(r'\s+', ' ', s2) + "\n")

	
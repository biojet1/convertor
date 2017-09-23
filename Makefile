
check: check.py units.xml
	alterx -np ./check.py units.xml

checkw: check.py units.xml
	alterx -mmp ./check.py units.xml

sql: .build/units.sql

.build/units.sql: mkdbcmd.py units.xml
	alterx -np mkdbcmd.py units.xml

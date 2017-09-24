
check: check.py *.xml
	alterx -np ./check.py .

newno: newno.py *.xml
	alterx -np ./newno.py .

checkw: check.py *.xml
	alterx -mmp ./check.py .

sql: check .build/units.sql

.build/units.sql: mkdbcmd.py *.xml
	alterx -np ./mkdbcmd.py . >.build/units.sql

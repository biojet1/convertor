
check: check.py *.xml
	alterx -np ./check.py .

newno: newno.py *.xml
	alterx -np ./newno.py .

checkw: check.py *.xml
	alterx -mmp ./check.py .

sql: check .build/units.sql

unitsdb: .build/UnitsDB.java

.build/units.sql: check mkdbcmd.py *.xml
	alterx -np ./mkdbcmd.py .>.build/units.sql

.build/UnitsDB.java: .build/units.sql
	python ./unitsdb.py .build/UnitsDB.java

sqlo: mkdbcmd.py *.xml
	alterx -np ./mkdbcmd.py .

list_types: .build/list_types
list_names: list_names.py  *.xml
	alterx -np ./list_names.py .

.build/list_types: list_types.py *.xml
	alterx -np ./list_types.py . >.build/list_types.txt


check_names: list_names.py *.xml
	alterx -np ./list_names.py . | alterx -np ./check_names.py .
	
fix_names: list_names.py *.xml
	alterx -np ./list_names.py . | alterx -mmp ./check_names.py .



import cx_Oracle

dsn_tns = cx_Oracle.makedsn('192.168.0.233', "1521", service_name='EMGSPROD2012.WORLD')
conn = cx_Oracle.connect(user=r'GARI', password='Inrs2019', dsn=dsn_tns)


































# cursor.execute("""
#     SELECT first_name, last_name
#     FROM employees
#     WHERE department_id = :did AND employee_id > :eid""",
#     did = 50,
#     eid = 190)
# for fname, lname in cursor:
#     print("Values:", fname, lname)
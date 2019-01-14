import cx_Oracle

# Connect as user "hr" with password "welcome" to the "oraclepdb" service running on this computer.
#connection = cx_Oracle.connect("GARI", "Inrs2019", "")
connection = cx_Oracle.connect('sales.us.oracle.com')

cursor = connection.cursor()
cursor.execute("""
    SELECT first_name, last_name
    FROM employees
    WHERE department_id = :did AND employee_id > :eid""",
    did = 50,
    eid = 190)
for fname, lname in cursor:
    print("Values:", fname, lname)
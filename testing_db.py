from interfaces.database import DBHandler
import sqlite3

con = sqlite3.connect("gps.db")
cursor = con.cursor()
cursor.execute('SELECT * FROM location_and_time')
rows = cursor.fetchall()
print(rows)
for row in rows:
    print(row)

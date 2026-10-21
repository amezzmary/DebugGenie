
import sqlite3

db_path = r"D:\DebugGenie\debuggenie.db"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

print("USERS TABLE")

cursor.execute("PRAGMA table_info(users)")
for column in cursor.fetchall():
    print(column[1], "-", column[2])

print("\nANALYSIS HISTORY TABLE")

cursor.execute("PRAGMA table_info(analysis_history)")
for column in cursor.fetchall():
    print(column[1], "-", column[2])

connection.close()

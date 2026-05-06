from db.postgres import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT 1;")
print(cur.fetchone())

cur.close()
conn.close()

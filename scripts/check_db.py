import sqlite3
for p in ['divyadrishti.db', 'backend/divyadrishti.db']:
    try:
        conn = sqlite3.connect(p)
        c = conn.cursor()
        c.execute("PRAGMA table_info(conversations)")
        print(p, [r[1] for r in c.fetchall()])
        conn.close()
    except Exception as e:
        print(p, e)

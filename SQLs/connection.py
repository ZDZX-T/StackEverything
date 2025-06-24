import sqlite3


conn = sqlite3.connect('_StackEverything.db', check_same_thread=False)
# 启用外键支持
conn.execute("PRAGMA foreign_keys = ON")
conn.commit()
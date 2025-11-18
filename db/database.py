import sqlite3
import os
sql_file = "/app/db/init.sql"

def get_connection():
    conn = sqlite3.connect(database=os.getenv('DB_PATH'))
    conn.row_factory = sqlite3.Row 
    return conn


def init_db():
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.executescript(sql_script)
        
        conn.commit()
        print("Base de datos creada con éxito")
    except Exception as e:
        print("Error al inicializar la base de datos")
        print(e)
    conn.close()

init_db()
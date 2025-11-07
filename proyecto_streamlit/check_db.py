import sqlite3, os

path = "data/students.db"
print("Ruta absoluta:", os.path.abspath(path))
print("Existe:", os.path.exists(path))

if not os.path.exists(path):
    print("El archivo students.db NO existe en data/. Termina el script.")
else:
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tablas encontradas:", tables)
        # Mostrar hasta 3 filas de ejemplo de la primera tabla si existe
        if tables:
            tbl = tables[0][0]
            print(f"\nPrimeras 3 filas de la tabla '{tbl}':")
            cursor.execute(f"SELECT * FROM \"{tbl}\" LIMIT 3;")
            for row in cursor.fetchall():
                print(row)
        conn.close()
    except Exception as e:
        print("Error al abrir la DB:", e)

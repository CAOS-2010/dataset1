# api/create_db_from_clean.py
import pandas as pd
from pathlib import Path
import sqlite3

# --- RUTAS ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
csv_path = PROJECT_ROOT / "data" / "student_dataset1.csv"
db_path = PROJECT_ROOT / "data" / "students.db"
table_name = "students"

print(f"📁 Cargando CSV desde: {csv_path}")

# --- CARGA CSV ---
if not csv_path.exists():
    raise FileNotFoundError(f"No se encontró el archivo CSV en: {csv_path}")

# Detecta separador automáticamente
with open(csv_path, "r", encoding="utf-8") as f:
    head = f.readline()
sep = ";" if ";" in head else ","
print(f"➡️  Separador detectado: '{sep}'")

# Cargar y limpiar básico
df = pd.read_csv(csv_path, sep=sep, encoding="utf-8", engine="python")
print(f"🔍 Filas: {len(df)}, Columnas: {len(df.columns)}")

# Limpieza de columnas con nombres vacíos o espacios
df.columns = [c.strip().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]

# Reemplazar strings vacíos o 'NaN' por valores nulos reales
df = df.replace(["", " ", "NaN", "nan", "N/A"], pd.NA)

# Guardar en SQLite
conn = sqlite3.connect(db_path)
df.to_sql(table_name, conn, if_exists="replace", index=False)
conn.close()

print(f"✅ Base de datos creada correctamente en: {db_path}")
print(f"✅ Tabla '{table_name}' con {len(df)} registros.")

from .db import engine
import pandas as pd

def get_preview(limit: int = 100):
    q = f"SELECT * FROM students LIMIT {limit}"
    return pd.read_sql(q, engine).to_dict(orient="records")

def get_summary_by_gender():
    q = "SELECT gender, COUNT(*) as count FROM students GROUP BY gender"
    return pd.read_sql(q, engine).to_dict(orient="records")

def get_subjects_averages():
    q = """
    SELECT 
      AVG(math_score) as avg_math,
      AVG(reading_score) as avg_reading,
      AVG(writing_score) as avg_writing
    FROM students
    """
    return pd.read_sql(q, engine).to_dict(orient="records")[0]

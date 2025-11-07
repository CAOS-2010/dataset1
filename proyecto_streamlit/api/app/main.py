from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from . import crud

app = FastAPI(title="Students Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/preview")
def preview(limit: int = Query(100, le=1000)):
    return {"data": crud.get_preview(limit)}

@app.get("/summary/gender")
def summary_gender():
    return {"data": crud.get_summary_by_gender()}

@app.get("/summary/subjects")
def subjects_summary():
    return {"data": crud.get_subjects_averages()}

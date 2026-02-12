from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from datetime import date

app = FastAPI(title="Longevity OS API", version="0.1.0")

DB: Dict[str, list] = {
    "immunizations": [],
    "biomarkers": [],
    "doctor_visits": [],
}

class ImmunizationIn(BaseModel):
    vaccine: str
    date: date
    provider: str = ""

class BiomarkerIn(BaseModel):
    name: str
    value: float
    unit: str = ""
    measured_on: date
    source: str = "manual"
class DoctorVisitIn(BaseModel):
    date: date
    doctor: str = ""
    specialty: str = ""
    reason: str = ""
    notes: str = ""
    follow_up_date: date | None = None
    
@app.get("/")
def root():
    return {"ok": True, "service": "longevity-os-api"}

@app.get("/v1/immunizations")
def list_immunizations():
    return DB["immunizations"]

@app.post("/v1/immunizations")
def add_immunization(payload: ImmunizationIn):
    item = payload.model_dump()
    item["id"] = len(DB["immunizations"]) + 1
    DB["immunizations"].append(item)
    return {"id": item["id"]}

@app.get("/v1/biomarkers/trends")
def biomarker_trends(name: str):
    rows = [r for r in DB["biomarkers"] if r["name"] == name]
    rows.sort(key=lambda x: x["measured_on"])
    return rows

@app.post("/v1/biomarkers/results")
def add_biomarker(payload: BiomarkerIn):
    item = payload.model_dump()
    item["id"] = len(DB["biomarkers"]) + 1
    DB["biomarkers"].append(item)
    return {"id": item["id"]}
@app.get("/v1/doctor-visits")
def list_doctor_visits():
    return DB["doctor_visits"]

@app.post("/v1/doctor-visits")
def add_doctor_visit(payload: DoctorVisitIn):
    item = payload.model_dump()
    item["id"] = len(DB["doctor_visits"]) + 1
    DB["doctor_visits"].append(item)
    return {"id": item["id"]}

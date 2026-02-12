from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date

app = FastAPI(title="Family Health OS API", version="0.2.0")

# ---------------------------
# In-memory "database" (MVP)
# ---------------------------
DB: Dict[str, list] = {
    "families": [],        # list[dict]
    "members": [],         # list[dict] (belongs to family)
    "immunizations": [],   # list[dict] (belongs to member)
    "doctor_visits": [],   # list[dict] (belongs to member)
}

def _next_id(items: List[dict]) -> int:
    return (items[-1]["id"] + 1) if items else 1

def _get_family(family_id: int) -> dict:
    fam = next((f for f in DB["families"] if f["id"] == family_id), None)
    if not fam:
        raise HTTPException(status_code=404, detail="Family not found")
    return fam

def _get_member(member_id: int) -> dict:
    mem = next((m for m in DB["members"] if m["id"] == member_id), None)
    if not mem:
        raise HTTPException(status_code=404, detail="Member not found")
    return mem

# ---------------------------
# Schemas
# ---------------------------
class FamilyIn(BaseModel):
    name: str

class MemberIn(BaseModel):
    family_id: int
    name: str
    birthdate: Optional[date] = None
    relation: str = ""  # e.g. "Vater", "Mutter", "Kind"

class ImmunizationIn(BaseModel):
    member_id: int
    vaccine: str
    date: date
    provider: str = ""
    notes: str = ""

class DoctorVisitIn(BaseModel):
    member_id: int
    date: date
    doctor: str = ""
    specialty: str = ""
    reason: str = ""
    notes: str = ""
    follow_up_date: Optional[date] = None

# ---------------------------
# Health check
# ---------------------------
@app.get("/")
def root():
    return {"ok": True, "service": "family-health-os-api"}

# ---------------------------
# Families
# ---------------------------
@app.get("/v1/families")
def list_families():
    return DB["families"]

@app.post("/v1/families")
def create_family(payload: FamilyIn):
    item = payload.model_dump()
    item["id"] = _next_id(DB["families"])
    DB["families"].append(item)
    return {"id": item["id"]}

# ---------------------------
# Members
# ---------------------------
@app.get("/v1/members")
def list_members(family_id: int):
    _get_family(family_id)
    return [m for m in DB["members"] if m["family_id"] == family_id]

@app.post("/v1/members")
def create_member(payload: MemberIn):
    _get_family(payload.family_id)
    item = payload.model_dump()
    item["id"] = _next_id(DB["members"])
    DB["members"].append(item)
    return {"id": item["id"]}

# ---------------------------
# Immunizations (per member)
# ---------------------------
@app.get("/v1/immunizations")
def list_immunizations(member_id: int):
    _get_member(member_id)
    return [i for i in DB["immunizations"] if i["member_id"] == member_id]

@app.post("/v1/immunizations")
def add_immunization(payload: ImmunizationIn):
    _get_member(payload.member_id)
    item = payload.model_dump()
    item["id"] = _next_id(DB["immunizations"])
    DB["immunizations"].append(item)
    return {"id": item["id"]}

# ---------------------------
# Doctor visits (per member)
# ---------------------------
@app.get("/v1/doctor-visits")
def list_doctor_visits(member_id: int):
    _get_member(member_id)
    return [v for v in DB["doctor_visits"] if v["member_id"] == member_id]

@app.post("/v1/doctor-visits")
def add_doctor_visit(payload: DoctorVisitIn):
    _get_member(payload.member_id)
    item = payload.model_dump()
    item["id"] = _next_id(DB["doctor_visits"])
    DB["doctor_visits"].append(item)
    return {"id": item["id"]}

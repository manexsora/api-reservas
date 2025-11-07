# routers/courts.py
import sqlite3
from fastapi import APIRouter, HTTPException
from db.database import get_connection
from models import CourtCreate, CourtOut

router = APIRouter(prefix="/courts", tags=["courts"])

@router.post("/", response_model=CourtOut, status_code=201)
async def create_court(court: CourtCreate):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO courts (name, id_zona, id_actividad_libre, duration_minutes) VALUES (?, ?, ?, ?)",
            (court.name, court.id_zona, court.id_actividad_libre, court.duration_minutes)
        )
        conn.commit()
        court_id = cur.lastrowid
        return CourtOut(id=court_id, **court.model_dump())
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

@router.get("/", response_model=list[CourtOut])
async def get_all_courts():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, id_zona, id_actividad_libre, duration_minutes FROM courts")
        courts = cur.fetchall()
        return [dict(c) for c in courts]
    finally:
        conn.close()

@router.get("/{court_id}", response_model=CourtOut)
async def get_court(court_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, id_zona, id_actividad_libre, duration_minutes FROM courts WHERE id = ?", (court_id,))
        court = cur.fetchone()
        if court is None:
            raise HTTPException(status_code=404, detail="Pista no encontrada")
        return dict(court)
    finally:
        conn.close()

@router.put("/{court_id}", response_model=CourtOut)
async def update_court(court_id: int, court: CourtCreate):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE courts SET name = ?, id_zona = ?, id_actividad_libre = ?, duration_minutes = ? WHERE id = ?",
            (court.name, court.id_zona, court.id_actividad_libre, court.duration_minutes, court_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pista no encontrada")
        return await get_court(court_id)
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

@router.delete("/{court_id}", status_code=204)
async def delete_court(court_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM courts WHERE id = ?", (court_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pista no encontrada")
        return
    except sqlite3.IntegrityError:
        # En caso de que queden 'jobs' asociados y la restricción ON DELETE lo impida
        raise HTTPException(status_code=409, detail="No se puede eliminar. Existen reservas (jobs) asociadas.")
    finally:
        conn.close()
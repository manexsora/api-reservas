# routers/jobs.py
import sqlite3
from fastapi import APIRouter, HTTPException
from db.database import get_connection
from models import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobOut, status_code=201)
async def create_job(job: JobCreate):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO jobs (name, user_id, court_id, reservation_day, reservation_time, is_active) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job.name, job.user_id, job.court_id, job.reservation_day, job.reservation_time, job.is_active)
        )
        conn.commit()
        job_id = cur.lastrowid
        return JobOut(id=job_id, **job.model_dump())
    except sqlite3.IntegrityError:
        # Atrapa el error si user_id o court_id no existen (Foreign Key)
        raise HTTPException(status_code=400, detail="Error de clave foránea: user_id o court_id no existen.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

@router.get("/", response_model=list[JobOut])
async def get_all_jobs():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                j.id, j.name, j.user_id, j.court_id, j.reservation_day, j.reservation_time, j.is_active, u.name AS user_name, c.name AS court_name
            FROM jobs j
            JOIN users u ON j.user_id = u.id
            JOIN courts c ON j.court_id = c.id
        """)
        jobs = cur.fetchall()
        return [dict(j) for j in jobs]
    finally:
        conn.close()

@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, user_id, court_id, reservation_day, reservation_time, is_active FROM jobs WHERE id = ?", (job_id,))
        job = cur.fetchone()
        if job is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return dict(job)
    finally:
        conn.close()

@router.put("/{job_id}", response_model=JobOut)
async def update_job(job_id: int, job: JobCreate):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE jobs SET name = ?, user_id = ?, court_id = ?, 
            reservation_day = ?, reservation_time = ?, is_active = ? 
            WHERE id = ?
            """,
            (job.name, job.user_id, job.court_id, job.reservation_day, job.reservation_time, job.is_active, job_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return await get_job(job_id)
    except sqlite3.IntegrityError:
        # Atrapa el error si user_id o court_id no existen (Foreign Key)
        raise HTTPException(status_code=400, detail="Error de clave foránea: user_id o court_id no existen.")
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return
    finally:
        conn.close()

@router.patch("/{job_id}/toggle-active")
async def toggle_job_active(job_id: int):
    """Alterna el estado is_active (1 a 0, 0 a 1) de un trabajo por su ID."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Obtener el estado actual
        cur.execute("SELECT is_active, name FROM jobs WHERE id = ?", (job_id,))
        job = cur.fetchone()
        
        if job is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        name = job["name"]
        current_state = job["is_active"]
        new_state = 1 if current_state == 0 else 0
        
        # 2. Actualizar el estado
        cur.execute("UPDATE jobs SET is_active = ? WHERE id = ?", (new_state, job_id))
        conn.commit()
        
        return {"id": job_id, "name": name, "is_active": new_state, "message": f"Estado cambiado a {'Activo' if new_state == 1 else 'Inactivo'}."}
        
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")
    finally:
        conn.close()
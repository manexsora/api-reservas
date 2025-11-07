# routers/users.py
import sqlite3
from fastapi import APIRouter, HTTPException
from db.database import get_connection
from models import UserCreate, UserUpdate, UserOut
from utils import encode_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate):
    encoded_password = encode_password(user.password)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, password, email) VALUES (?, ?, ?)",
            (user.name, encoded_password, user.email)
        )
        conn.commit()
        user_id = cur.lastrowid
        return UserOut(id=user_id, name=user.name, email=user.email)
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

@router.get("/", response_model=list[UserOut])
async def get_all_users():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users")
        users = cur.fetchall()
        return [dict(u) for u in users]
    finally:
        conn.close()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return dict(user)
    finally:
        conn.close()

@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserUpdate):
    updates = []
    values = []
    
    if user.name is not None:
        updates.append("name = ?")
        values.append(user.name)
    if user.email is not None:
        updates.append("email = ?")
        values.append(user.email)
    if user.password is not None:
        updates.append("password = ?")
        values.append(encode_password(user.password))
        
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    sql = "UPDATE users SET " + ", ".join(updates) + " WHERE id = ?"
    values.append(user_id)
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(values))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        # Retorna el objeto recién actualizado
        return await get_user(user_id)
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"DB Error: {e}")
    finally:
        conn.close()

# --- DELETE (DELETE) ---
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return
    finally:
        conn.close()
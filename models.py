# models.py
from pydantic import BaseModel, Field, validator
from typing import Optional

# --- USERS ---
class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str 

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    # La contraseña NO se incluye en la salida
    class Config:
        from_attributes = True

# --- COURTS ---
class CourtBase(BaseModel):
    name: str
    id_zona: str
    id_actividad_libre: str
    duration_minutes: int

class CourtCreate(CourtBase):
    pass

class CourtOut(CourtBase):
    id: int
    class Config:
        from_attributes = True
    
# --- JOBS (Reservas) ---
class JobBase(BaseModel):
    name: str
    user_id: int
    court_id: int
    reservation_day: int = Field(..., ge=1, le=7, description="Día de la semana para la reserva (1=Lunes, 7=Domingo)")
    reservation_time: str
    user_name: Optional[str] = None 
    court_name: Optional[str] = None
    is_active: Optional[int] = 1

    @validator('reservation_day')
    def validate_day_of_week(cls, v):
        if not 1 <= v <= 7:
            raise ValueError('El día de la semana debe ser un número entre 1 (Lunes) y 7 (Domingo).')
        return v

class JobCreate(BaseModel):
    name: str
    user_id: int
    court_id: int
    reservation_day: int = Field(..., ge=1, le=7)
    reservation_time: str
    is_active: int = 1
    
class JobOut(JobBase):
    id: int
    class Config:
        from_attributes = True
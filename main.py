from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import users, courts, jobs
from db.database import init_db
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.getenv("DB_PATH")

    # Inicialización de la base de datos
    if not os.path.exists(db_path):
        print("Base de datos no encontrada. Inicializando...")
        init_db()
    else:
        print("Base de datos existente. No es necesario inicializar.")

    # Se levanta FastApi
    yield

    print("Cerrando aplicación...")

app = FastAPI(
    title="Sistema de Reservas API",
    description="API CRUD para Usuarios, Pistas y Reservas.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(courts.router)
app.include_router(jobs.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Reservas. Accede a /docs para la documentación de la API."}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from routers import users, courts, jobs
from db.database import init_db
from contextlib import asynccontextmanager
import os
from pathlib import Path

# Definimos la ruta base para los archivos estáticos
STATIC_DIR = Path("static")

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

# Monta el directorio estático para servir CSS, JS, imágenes, etc. en /static/...
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    # Lee el contenido del archivo index.html y lo devuelve como respuesta HTML
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Esto solo se ejecuta si el index.html no existe
        return "<h1>Error 404: Archivo index.html no encontrado.</h1>"
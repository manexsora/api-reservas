from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import users, courts, jobs

app = FastAPI(
    title="Sistema de Reservas API",
    description="API CRUD para Usuarios, Pistas y Reservas.",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(courts.router)
app.include_router(jobs.router)

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Reservas. Accede a /docs para la documentación de la API."}


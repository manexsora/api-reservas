# Poli-Reserbak: Sistema Automatizado de Gestión de Reservas

![Python Version](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.122.0+-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

## 📋 Descripción del Proyecto

**Poli-Reserbak** es una solución backend diseñada para automatizar la reserva de instalaciones deportivas en el polideportivo municipal. El sistema permite gestionar tareas programadas ("Jobs") que ejecutan procesos de reserva autónomos mediante *web scraping* e interacción directa con el portal del proveedor (`kirolzer-tolosa`).

La aplicación expone una API RESTful construida con **FastAPI** para la administración de usuarios, pistas y programaciones, e integra un motor de ejecución basado en `cron` dentro de un entorno contenerizado, asegurando que las reservas se ejecuten con precisión en el momento de apertura de los plazos.

## 🚀 Características Principales

* **API RESTful de Alto Rendimiento:** Gestión CRUD completa de Usuarios, Pistas y Trabajos de Reserva (Jobs).
* **Programación Inteligente:** Integración de `python-crontab` para transformar reglas de negocio en tareas del sistema (`cron`) automáticamente.
* **Web Scraping Robusto:** Scripts de automatización (`BeautifulSoup` + `Requests`) que manejan autenticación, tokens CSRF y selección de pistas.
* **Persistencia Ligera:** Base de datos SQLite integrada, ideal para despliegues portátiles.
* **Arquitectura Dockerizada:** Entorno autocontenido que ejecuta tanto el servidor web (Uvicorn) como el demonio de planificación (Cron) en un solo servicio.
* **Interfaz de Gestión:** Panel web estático simple para la administración rápida de recursos.

## 🛠 Arquitectura del Proyecto

El proyecto sigue una arquitectura modular:

```text
.
├── db/                 # Capa de persistencia (SQLite + Scripts SQL)
├── routers/            # Endpoints de la API (Usuarios, Pistas, Jobs)
├── scripts/            # Lógica de automatización y scraping (reserva.py)
├── static/             # Interfaz web (Frontend ligero)
├── main.py             # Punto de entrada de la aplicación
├── Dockerfile          # Definición del entorno
└── docker-compose.yml  # Orquestación de servicios
```

### Flujo de Trabajo
1. Configuración: El usuario define una "Pista" y crea un "Job" a través de la API/Web.

2. Planificación: El sistema registra una tarea en el crontab del sistema operativo (dentro del contenedor).

3. Ejecución: A la hora programada (00:00 del día objetivo), el cron dispara el script reserva.py.

4. Acción: El script se autentica en el portal externo, obtiene el token de sesión y confirma la reserva.

## 🔧 Requisitos Previos
- [Docker engine](https://docs.docker.com/engine/install/)

- [Docker Compose](https://docs.docker.com/compose/install/)

## 📦 Instalación y Despliegue
Este proyecto está totalmente "dockerizado" para facilitar su puesta en marcha en cualquier servidor Linux/Windows.

1. Clonar el repositorio
    
    ```
    git clone https://github.com/manexsora/api-reservas.git

    cd poli-reserbak
    ```
2. Construir y Levantar el servicio
El contenedor compilará las dependencias e inicializará la base de datos automáticamente en el primer arranque.

    ```
    docker-compose up -d --build
    ```
3. Verificar el estado
El servicio estará disponible en el puerto 8080.

    - API Docs (Swagger UI): http://localhost:8080/docs

    - Panel de Gestión: http://localhost:8080/static/index.html

## ⚙️ Uso de la API
### Autenticación
El sistema utiliza una gestión de usuarios interna. Asegúrese de crear un usuario con las credenciales válidas del portal del polideportivo, ya que estas serán utilizadas por el bot para realizar la reserva.

### Ejemplo de Creación de Job (Reserva Automática)
Para programar una reserva, envíe una petición POST a /jobs/:
```
{
  "name": "Reserva Padel Semanal",
  "user_id": 1,
  "court_id": 1,
  "reservation_day": 2, 
  "reservation_time": "19:00",
  "is_active": 1
}
```
Nota: reservation_day: 1 = Lunes, 7 = Domingo.

## 🛡️ Notas Técnicas
- Logs: La salida de los cron jobs se redirige a stdout, por lo que pueden consultarse mediante docker logs poli_reserbak_api.

- Seguridad: Las contraseñas se almacenan con una codificación estándar (Base64) para su uso por el bot. Se recomienda desplegar este servicio en un entorno controlado.
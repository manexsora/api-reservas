from db.database import get_connection
from utils import decode_password
from bs4 import BeautifulSoup
import argparse
import requests
import datetime
BASE = "https://kirolzer-tolosa.provis.es"


def get_job_details(job_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
                SELECT
                    j.name,
                    j.reservation_day as day,
                    j.reservation_time as hora,
                    c.name as nombre_cancha,
                    c.id_zona ,
                    c.id_actividad_libre ,
                    c.duration_minutes as duracion,
                    u.email,
                    u.password
                FROM
                    jobs j
                JOIN courts c on
                    j.court_id = c.id
                JOIN users u on
                    j.user_id = u.id
                WHERE 
                    j.id = ?
                    """, (job_id,))
        job = cur.fetchone()
        
        return dict(job) if job else None
    except Exception as e:
        print(f"ERROR: No se pudo obtener el Job {job_id} de la BD. {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_next_target_date(target_day_of_week: int) -> str:
    target_weekday_py = target_day_of_week - 1 

    today = datetime.date.today()
    current_weekday_py = today.weekday()
    days_until_next_target = (target_weekday_py - current_weekday_py + 7) % 7
    if days_until_next_target == 0:
        days_until_next_target = 7

    next_target_day_date = today + datetime.timedelta(days=days_until_next_target)

    return next_target_day_date.strftime("%d/%m/%Y")

def run_reservation_logic(job_id):
    print(f"[CRON] Empezando reserva {job_id}")
    details = get_job_details(job_id)

    ## LOGIN ##
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    r = session.get(f"{BASE}/Login")
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    if token_input is None:
        raise RuntimeError("No encontré __RequestVerificationToken en la página (comprueba la URL).")

    token_value = token_input.get("value")

    payload = {
        "__RequestVerificationToken": token_value,
        "Username": details['email'],
        "Password": decode_password(details['password']),
        "RememberMe": "false"
    }
    login_resp = session.post(f"{BASE}/Login", data=payload)
    login_resp.raise_for_status()


    ## RESERVA ##
    payload = {
        "idActividadLibre": details['id_actividad_libre'],
        "idZona": details['id_zona'],
        "hora": details['hora'],
        "fecha": get_next_target_date(int(details['day'])),
        "duracion": details['duracion'],
        "importe": "0.00",
        "suplementos": "",
        "tokenizar": 0,
        "token": 0,
        "tieneBono": False
    }
    confirm = session.post(
        f"{BASE}/Reservas/ConfirmarActividadLibre",
        json=payload,
        headers={
            "Origin": BASE,
            "X-Requested-With": "XMLHttpRequest"
        })
    print(confirm.status_code, confirm.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Espera el parámetro --job-id
    parser.add_argument('--job-id', type=int, required=True, help="ID del Job a ejecutar.")
    args = parser.parse_args()
    run_reservation_logic(args.job_id)
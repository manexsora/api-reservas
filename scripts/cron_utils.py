import sqlite3
import os
from crontab import CronTab
from typing import Dict

# PATHS DENTRO DEL CONTENEDOR
SCHEDULER_SCRIPT_PATH = f"/app/scripts/reserva.py"
PYTHON_EXEC = "/usr/local/bin/python"   # Python real dentro del contenedor
CRON_COMMENT_TAG = 'poli-reserbak-job'


def _generate_command_line(job_data: Dict) -> str:
    job_id = job_data['id']
    db_path = os.getenv("DB_PATH", "/app/db/database.db")
    return f'DB_PATH={db_path} PYTHONPATH=/app {PYTHON_EXEC} {SCHEDULER_SCRIPT_PATH} --job-id {job_id} >> /var/log/cron_custom.log 2>&1'


def add_or_update_job(job_data: Dict, is_active: bool = True):
    job_id = job_data['id']
    search_term = f'--job-id {job_id}'

    # Cron del contenedor
    cron = CronTab(user=True)

    # Borrar cualquier job previo
    cron.remove_all(command=search_term)

    if is_active:
        cmd = _generate_command_line(job_data)

        new_job = cron.new(command=cmd, comment=CRON_COMMENT_TAG)
        new_job.minute.on(0)
        new_job.hour.on(0)

        court_day = int(job_data['reservation_day'])
        cron_dow = (court_day % 7) + 1
        new_job.dow.on(cron_dow)

        new_job.enable()

        print(f"Cron: Job {job_id} añadido para día {cron_dow}.")

    cron.write()

def delete_job(job_id: int):
    cron = CronTab(user=True)
    search_term = f'--job-id {job_id}'
    removed = cron.remove_all(command=search_term)
    cron.write()
    print(f"Cron: eliminadas {removed} tareas para Job {job_id}.")

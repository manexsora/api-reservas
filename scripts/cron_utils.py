import sqlite3
from crontab import CronTab
from typing import Dict, Optional

# --- CONFIGURACIÓN CRÍTICA (AJUSTAR EN EL HOST) ---
SCHEDULER_SCRIPT_PATH = '/opt/poli-reserbak/scheduler_script.py'
CRON_COMMENT_TAG = 'poli-reserbak-job'
PYTHON_EXEC = '/usr/bin/python3'

def _generate_command_line(job_data: Dict) -> str:
    job_id = job_data['id']
    command = f'{PYTHON_EXEC} {SCHEDULER_SCRIPT_PATH} --job-id {job_id}'
    return command

def add_or_update_job(job_data: Dict, is_active: bool = True):
    """Crea una nueva tarea Cron, o actualiza una existente. Elimina si está inactiva."""
    print(job_data)
    job_id = job_data['id']
    search_term = f'--job-id {job_id}'

    court_day = int(job_data['reservation_day'])
    cron_dow = (court_day % 7) + 1 

    cron = CronTab(True) 
    
    # 1. Eliminar la tarea existente para asegurar una actualización limpia
    cron.remove_all(command=search_term) 
    
    if is_active:
        # 2. Recrear la tarea con la nueva configuración
        full_command_line = _generate_command_line(job_data)
        
        # El método .new automáticamente parsea la línea (tiempo y comando)
        new_job = cron.new(command=full_command_line, comment=CRON_COMMENT_TAG)
        new_job.minute.on(0)
        new_job.hour.on(0)
        new_job.dow.on(cron_dow)
        
        new_job.enabled = True 
        print(f"Cron: Job {job_id} añadido/actualizado para {job_data['reservation_time']}.")

    # 3. Escribir los cambios
    cron.write()
    if not is_active:
        print(f"Cron: Job {job_id} eliminado por inactividad.")


def delete_job(job_id: int):
    """Elimina la tarea de la Crontab asociada a un Job ID específico."""
    
    cron = CronTab(user=True)
    search_term = f'--job-id {job_id}'
    
    # Eliminar todas las tareas que contienen el ID del job
    removed_count = cron.remove_all(command=search_term)
    # Escribir los cambios
    cron.write()
    print(f"Cron: {removed_count} tarea(s) eliminada(s) para Job ID {job_id}.")
"""
Configuración del bot de productividad
"""
import os
from datetime import time

# Token del bot de Telegram
BOT_TOKEN = "8222314009:AAG-nc-6_IJvVMk-LH4Q5bFVO3GLOymTA4o"

# ID del usuario autorizado (solo tú puedes usar el bot)
AUTHORIZED_USER_ID = 6009496370

# Configuración de la base de datos
DATABASE_PATH = "productivity_bot.db"

# Configuración de recordatorios
DEFAULT_DAILY_SUMMARY_TIME = time(7, 0)  # 07:00 AM
DEFAULT_EVENING_REMINDER_TIME = time(18, 0)  # 06:00 PM

# Zona horaria por defecto
DEFAULT_TIMEZONE = "Europe/Madrid"

# Límites y configuración
MAX_PROJECT_NAME_LENGTH = 100
MAX_TASK_NAME_LENGTH = 200
MAX_NOTE_TITLE_LENGTH = 100
MAX_NOTE_CONTENT_LENGTH = 4000

# Estados de tareas
TASK_STATUS = {
    'pending': '⏳ Pendiente',
    'in_progress': '🔄 En progreso',
    'completed': '✅ Completada'
}

# Prioridades
PRIORITY_LEVELS = {
    'low': '🟢 Baja',
    'medium': '🟡 Media',
    'high': '🔴 Alta'
}

# Estados de proyectos
PROJECT_STATUS = {
    'active': '🟢 Activo',
    'paused': '⏸️ Pausado',
    'completed': '✅ Finalizado'
}

# Emojis para el menú
EMOJI = {
    'project': '📁',
    'task': '✅',
    'note': '📝',
    'dashboard': '📊',
    'settings': '⚙️',
    'today': '📅',
    'back': '◀️',
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'search': '🔍',
    'stats': '📈',
    'calendar': '📆',
    'reminder': '⏰',
    'export': '📤'
}

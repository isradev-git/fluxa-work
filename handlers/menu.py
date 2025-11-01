"""
Handler del menú principal con personalidad Cortana
Maneja la navegación general del bot y las vistas principales
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import date, datetime, timedelta

import config
from database.models import DatabaseManager, Project, Task
from utils.keyboards import (
    get_main_keyboard,
    get_projects_menu,
    get_tasks_menu,
    get_notes_menu,
    get_dashboard_menu,
    get_settings_menu
)
from utils.formatters import format_task_list, format_dashboard
from cortana_personality import (
    CORTANA_PROJECT_MENU,
    CORTANA_TASK_MENU,
    CORTANA_NOTES_MENU,
    CORTANA_TODAY_VIEW,
    CORTANA_DASHBOARD_INTRO,
    CORTANA_SETTINGS_MENU,
    CORTANA_TASK_NO_RESULTS
)

# Inicializar gestores de base de datos
db_manager = DatabaseManager()
task_manager = Task(db_manager)
project_manager = Project(db_manager)


async def show_projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de proyectos"""
    await update.message.reply_text(
        CORTANA_PROJECT_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_projects_menu()
    )


async def show_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de tareas"""
    await update.message.reply_text(
        CORTANA_TASK_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def show_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra las tareas de hoy y tareas atrasadas"""
    today = date.today()
    
    # Obtener tareas de hoy
    today_tasks = task_manager.get_all({'today': True})
    
    # Obtener tareas atrasadas
    overdue_tasks = task_manager.get_all({'overdue': True})
    
    lines = [CORTANA_TODAY_VIEW, ""]
    
    # Tareas atrasadas (si hay)
    if overdue_tasks:
        lines.append("⚠️ <b>Objetivos Atrasados</b>")
        lines.append(f"Tienes {len(overdue_tasks)} objetivo(s) que requieren atención inmediata:\n")
        
        for task in overdue_tasks[:5]:
            status_emoji = "✅" if task['status'] == 'completed' else "⏳"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
            lines.append(f"{status_emoji}{priority_emoji} {task['title']}")
        
        if len(overdue_tasks) > 5:
            lines.append(f"\n...y {len(overdue_tasks) - 5} más")
        
        lines.append("")
    
    # Tareas de hoy
    if today_tasks:
        lines.append("📅 <b>Objetivos de Hoy</b>")
        lines.append(f"En la agenda para hoy: {len(today_tasks)} objetivo(s)\n")
        
        for task in today_tasks[:5]:
            status_emoji = "✅" if task['status'] == 'completed' else "⏳"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
            lines.append(f"{status_emoji}{priority_emoji} {task['title']}")
        
        if len(today_tasks) > 5:
            lines.append(f"\n...y {len(today_tasks) - 5} más")
    else:
        lines.append("📅 <b>Objetivos de Hoy</b>")
        lines.append(f"\n{CORTANA_TASK_NO_RESULTS}")
    
    if not today_tasks and not overdue_tasks:
        lines.append("\n✨ Todo despejado por ahora. Buen momento para planificar.")
    
    message = "\n".join(lines)
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el dashboard con el resumen general"""
    today = date.today()
    next_week = today + timedelta(days=7)
    
    # Obtener estadísticas de tareas
    all_tasks = task_manager.get_all({'parent_only': True})
    
    tasks_pending = len([t for t in all_tasks if t['status'] == 'pending'])
    tasks_in_progress = len([t for t in all_tasks if t['status'] == 'in_progress'])
    
    tasks_completed_today = len([
        t for t in all_tasks 
        if t['status'] == 'completed' 
        and t.get('completed_at') 
        and datetime.fromisoformat(t['completed_at']).date() == today
    ])
    
    tasks_overdue = len([
        t for t in all_tasks 
        if t.get('deadline') 
        and datetime.strptime(t['deadline'], "%Y-%m-%d").date() < today
        and t['status'] != 'completed'
    ])
    
    active_projects = project_manager.get_all(status='active')
    paused_projects = project_manager.get_all(status='paused')
    
    upcoming_deadlines = []
    for project in active_projects:
        if project.get('deadline'):
            try:
                deadline = datetime.strptime(project['deadline'], "%Y-%m-%d").date()
                if today <= deadline <= next_week:
                    upcoming_deadlines.append(project)
            except:
                continue
    
    upcoming_deadlines.sort(key=lambda x: x['deadline'])
    
    summary = {
        'tasks_pending': tasks_pending,
        'tasks_in_progress': tasks_in_progress,
        'tasks_completed_today': tasks_completed_today,
        'tasks_overdue': tasks_overdue,
        'projects_active': len(active_projects),
        'projects_paused': len(paused_projects),
        'upcoming_deadlines': upcoming_deadlines
    }
    
    message = f"{CORTANA_DASHBOARD_INTRO}\n\n{format_dashboard(summary)}"
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_dashboard_menu()
    )


async def show_notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de notas"""
    await update.message.reply_text(
        CORTANA_NOTES_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_notes_menu()
    )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de configuración"""
    await update.message.reply_text(
        CORTANA_SETTINGS_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_settings_menu()
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vuelve al menú principal"""
    query = update.callback_query
    await query.answer()
    
    message = """
🏠 <b>Menú Principal</b>

Sistema Cortana listo para recibir órdenes.

Usa los botones de abajo para navegar por las diferentes secciones.

📁 Misiones | ✅ Objetivos
📅 Hoy | 📊 Análisis Táctico
📝 Base de Datos | ⚙️ Configuración

Comando /help disponible si necesitas orientación.
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML
    )
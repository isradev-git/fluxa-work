"""
Handler de dashboard
Muestra estadísticas y resumen general de productividad
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import date, datetime, timedelta

import config
from database.models import DatabaseManager, Task, Project
from utils.keyboards import get_dashboard_menu
from utils.formatters import format_dashboard, format_weekly_stats, format_monthly_stats
from utils.reminders import ReminderSystem

# Inicializar gestores
db_manager = DatabaseManager()
task_manager = Task(db_manager)
project_manager = Project(db_manager)


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el dashboard con el resumen general.
    Puede ser llamado desde mensaje o desde callback.
    """
    # Determinar si viene de mensaje o callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        is_callback = True
    else:
        is_callback = False
    
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
    
    message = format_dashboard(summary)
    
    if is_callback:
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_dashboard_menu()
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_dashboard_menu()
        )


async def show_weekly_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra estadísticas semanales"""
    query = update.callback_query
    await query.answer("📊 Calculando estadísticas...", show_alert=False)
    
    # Calcular semana actual
    today = date.today()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    # Crear sistema de recordatorios temporal para usar su método
    reminder = ReminderSystem(db_manager, None, config.AUTHORIZED_USER_ID)
    stats = reminder._calculate_weekly_stats(week_start, week_end)
    
    message = format_weekly_stats(stats)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_dashboard_menu()
    )


async def show_monthly_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra estadísticas mensuales"""
    query = update.callback_query
    await query.answer("📊 Calculando estadísticas...", show_alert=False)
    
    # Calcular mes actual
    today = date.today()
    first_day = today.replace(day=1)
    
    # Último día del mes
    if today.month == 12:
        last_day = today.replace(day=31)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
        last_day = next_month - timedelta(days=1)
    
    # Calcular estadísticas
    reminder = ReminderSystem(db_manager, None, config.AUTHORIZED_USER_ID)
    stats = reminder._calculate_monthly_stats(first_day, last_day)
    
    message = format_monthly_stats(stats)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_dashboard_menu()
    )

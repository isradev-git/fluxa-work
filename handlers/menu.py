"""
Handler del menú principal
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

# Inicializar gestores de base de datos
db_manager = DatabaseManager()
task_manager = Task(db_manager)
project_manager = Project(db_manager)


async def show_projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de proyectos.
    
    Se activa cuando el usuario presiona el botón "📁 Proyectos"
    del menú principal.
    
    Args:
        update: Contiene la información del mensaje del usuario
        context: Contexto de la conversación
    """
    message = """
📁 <b>Gestión de Proyectos</b>

Desde aquí puedes crear y gestionar tus proyectos de desarrollo.

Cada proyecto puede tener tareas asociadas y un seguimiento de progreso.

¿Qué quieres hacer?
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_projects_menu()
    )


async def show_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de tareas.
    
    Se activa cuando el usuario presiona el botón "✅ Tareas"
    del menú principal.
    """
    message = """
✅ <b>Gestión de Tareas</b>

Organiza todas tus tareas y pendientes.

Puedes filtrar por fecha, prioridad o proyecto.

¿Qué quieres hacer?
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def show_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra las tareas de hoy y tareas atrasadas.
    
    Esta es una vista rápida para ver qué hay que hacer hoy.
    Se activa con el botón "📅 Hoy" del menú principal.
    """
    today = date.today()
    
    # Obtener tareas de hoy (parent_only=True significa solo tareas principales, no subtareas)
    tasks_today = task_manager.get_all({
        'today': True,
        'parent_only': True
    })
    
    # Obtener tareas atrasadas
    tasks_overdue = task_manager.get_all({
        'overdue': True,
        'parent_only': True
    })
    
    # Construir mensaje
    lines = [
        f"📅 <b>Resumen de hoy - {today.strftime('%d/%m/%Y')}</b>",
        ""
    ]
    
    # Tareas de hoy
    if tasks_today:
        lines.append("<b>🎯 Tareas con fecha límite hoy:</b>")
        for i, task in enumerate(tasks_today, 1):
            # Emoji según estado de la tarea
            status = "✅" if task['status'] == 'completed' else "🔄" if task['status'] == 'in_progress' else "⏳"
            # Emoji según prioridad
            priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            
            lines.append(f"{i}. {status}{priority} {task['title']}")
        lines.append("")
    else:
        lines.append("✨ No tienes tareas con fecha límite hoy")
        lines.append("")
    
    # Tareas atrasadas
    if tasks_overdue:
        lines.append("<b>⚠️ Tareas atrasadas:</b>")
        for i, task in enumerate(tasks_overdue, 1):
            priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            
            # Calcular días de atraso
            deadline = datetime.strptime(task['deadline'], "%Y-%m-%d").date()
            days_overdue = (today - deadline).days
            
            lines.append(f"{i}. {priority} {task['title']} ({days_overdue} días)")
        lines.append("")
    else:
        if tasks_today:
            lines.append("✅ No tienes tareas atrasadas. ¡Bien!")
            lines.append("")
    
    # Mensaje motivacional
    if not tasks_today and not tasks_overdue:
        lines.append("🎉 ¡Genial! No tienes tareas urgentes hoy.")
        lines.append("Es un buen momento para avanzar en tus proyectos.")
    elif tasks_overdue:
        lines.append("💪 ¡Vamos a ponernos al día con las tareas atrasadas!")
    else:
        lines.append("🚀 ¡A por un día productivo!")
    
    message = "\n".join(lines)
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el dashboard con el resumen general.
    
    El dashboard muestra:
    - Número de tareas pendientes, en progreso y completadas hoy
    - Tareas atrasadas
    - Proyectos activos
    - Próximas entregas (7 días)
    
    Se activa con el botón "📊 Dashboard" del menú principal.
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    
    # Obtener estadísticas de tareas
    all_tasks = task_manager.get_all({'parent_only': True})
    
    # Contar tareas por estado
    tasks_pending = len([t for t in all_tasks if t['status'] == 'pending'])
    tasks_in_progress = len([t for t in all_tasks if t['status'] == 'in_progress'])
    
    # Tareas completadas hoy
    tasks_completed_today = len([
        t for t in all_tasks 
        if t['status'] == 'completed' 
        and t.get('completed_at') 
        and datetime.fromisoformat(t['completed_at']).date() == today
    ])
    
    # Tareas atrasadas
    tasks_overdue = len([
        t for t in all_tasks 
        if t.get('deadline') 
        and datetime.strptime(t['deadline'], "%Y-%m-%d").date() < today
        and t['status'] != 'completed'
    ])
    
    # Obtener proyectos activos
    active_projects = project_manager.get_all(status='active')
    paused_projects = project_manager.get_all(status='paused')
    
    # Próximas entregas de proyectos (7 días)
    upcoming_deadlines = []
    for project in active_projects:
        if project.get('deadline'):
            try:
                deadline = datetime.strptime(project['deadline'], "%Y-%m-%d").date()
                if today <= deadline <= next_week:
                    upcoming_deadlines.append(project)
            except:
                continue
    
    # Ordenar por fecha
    upcoming_deadlines.sort(key=lambda x: x['deadline'])
    
    # Preparar resumen para formatear
    summary = {
        'tasks_pending': tasks_pending,
        'tasks_in_progress': tasks_in_progress,
        'tasks_completed_today': tasks_completed_today,
        'tasks_overdue': tasks_overdue,
        'projects_active': len(active_projects),
        'projects_paused': len(paused_projects),
        'upcoming_deadlines': upcoming_deadlines
    }
    
    # Formatear mensaje usando la función del formateador
    message = format_dashboard(summary)
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_dashboard_menu()
    )


async def show_notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de notas.
    
    Se activa cuando el usuario presiona el botón "📝 Notas"
    del menú principal.
    """
    message = """
📝 <b>Gestión de Notas</b>

Guarda tus ideas, fragmentos de código y documentación.

Puedes organizar tus notas con etiquetas y asociarlas a proyectos o tareas.

¿Qué quieres hacer?
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_notes_menu()
    )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de configuración.
    
    Se activa cuando el usuario presiona el botón "⚙️ Configuración"
    del menú principal.
    """
    message = """
⚙️ <b>Configuración</b>

Personaliza el funcionamiento del bot:

• Cambiar horarios de recordatorios
• Activar/desactivar notificaciones
• Exportar tus datos
• Ajustar zona horaria

¿Qué quieres configurar?
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_settings_menu()
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Vuelve al menú principal.
    
    Esta función se ejecuta cuando el usuario presiona un botón
    "◀️ Volver al menú" en cualquier submenú.
    
    Args:
        update: Como viene de un botón inline, usamos update.callback_query
        context: Contexto de la conversación
    """
    query = update.callback_query
    await query.answer()  # Confirmar que recibimos el click del botón
    
    message = """
🏠 <b>Menú Principal</b>

Usa los botones de abajo para navegar por las diferentes secciones.

📁 Proyectos | ✅ Tareas
📅 Hoy | 📊 Dashboard
📝 Notas | ⚙️ Configuración

Escribe /help si necesitas ayuda.
"""
    
    # Editar el mensaje existente en lugar de enviar uno nuevo
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML
    )

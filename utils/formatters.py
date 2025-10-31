"""
Utilidades para formatear mensajes del bot
Este archivo contiene funciones para dar formato a los mensajes que envía el bot
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import config

def format_date(date_str: Optional[str]) -> str:
    """
    Formatea una fecha en formato legible en español.
    
    Args:
        date_str: Fecha en formato YYYY-MM-DD o None
        
    Returns:
        Fecha formateada o "Sin fecha" si es None
    """
    if not date_str:
        return "Sin fecha límite"
    
    try:
        # Convertir string a objeto date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        
        # Calcular diferencia de días
        diff = (date_obj - today).days
        
        # Formatear según cercanía
        if diff < 0:
            return f"⚠️ Atrasada ({abs(diff)} días)"
        elif diff == 0:
            return "🔥 Hoy"
        elif diff == 1:
            return "⚡ Mañana"
        elif diff <= 7:
            return f"📅 En {diff} días ({date_obj.strftime('%d/%m')})"
        else:
            return date_obj.strftime("%d/%m/%Y")
    except:
        return date_str


def format_project(project: Dict[str, Any], include_progress: bool = True) -> str:
    """
    Formatea la información de un proyecto para mostrarlo.
    
    Args:
        project: Diccionario con datos del proyecto
        include_progress: Si incluir información de progreso
        
    Returns:
        String formateado con la información del proyecto
    """
    # Emojis según estado y prioridad
    status_emoji = {
        'active': '🟢',
        'paused': '⏸️',
        'completed': '✅'
    }
    
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }
    
    # Construir mensaje
    lines = [
        f"📁 <b>{project['name']}</b>",
        f"",
        f"Estado: {status_emoji.get(project['status'], '❓')} {config.PROJECT_STATUS.get(project['status'], 'Desconocido')}",
        f"Prioridad: {priority_emoji.get(project['priority'], '❓')} {config.PRIORITY_LEVELS.get(project['priority'], 'Media')}"
    ]
    
    # Cliente si existe
    if project.get('client'):
        lines.append(f"Cliente: {project['client']}")
    
    # Fecha límite
    if project.get('deadline'):
        lines.append(f"Entrega: {format_date(project['deadline'])}")
    
    # Descripción si existe
    if project.get('description'):
        lines.append(f"")
        lines.append(f"📄 {project['description']}")
    
    return "\n".join(lines)


def format_project_with_progress(project: Dict[str, Any], 
                                 progress: Dict[str, Any]) -> str:
    """
    Formatea un proyecto incluyendo su progreso.
    
    Args:
        project: Diccionario con datos del proyecto
        progress: Diccionario con estadísticas de progreso
        
    Returns:
        String formateado con proyecto y progreso
    """
    base_info = format_project(project, include_progress=False)
    
    # Agregar barra de progreso visual
    percentage = progress['percentage']
    filled = int(percentage / 10)  # Cada bloque representa 10%
    empty = 10 - filled
    
    progress_bar = "█" * filled + "░" * empty
    
    progress_info = [
        "",
        f"📊 <b>Progreso: {percentage}%</b>",
        f"[{progress_bar}]",
        f"",
        f"✅ Completadas: {progress['completed_tasks']}",
        f"⏳ Pendientes: {progress['pending_tasks']}",
        f"📋 Total: {progress['total_tasks']} tareas"
    ]
    
    return base_info + "\n" + "\n".join(progress_info)


def format_task(task: Dict[str, Any], include_project: bool = False,
                project_name: Optional[str] = None) -> str:
    """
    Formatea la información de una tarea.
    
    Args:
        task: Diccionario con datos de la tarea
        include_project: Si incluir nombre del proyecto
        project_name: Nombre del proyecto (si include_project es True)
        
    Returns:
        String formateado con la información de la tarea
    """
    # Emojis según estado
    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅'
    }
    
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }
    
    # Construir mensaje
    lines = [
        f"{status_emoji.get(task['status'], '❓')} <b>{task['title']}</b>",
        f""
    ]
    
    # Proyecto si se incluye
    if include_project and project_name:
        lines.append(f"📁 Proyecto: {project_name}")
    
    lines.extend([
        f"Estado: {config.TASK_STATUS.get(task['status'], 'Desconocido')}",
        f"Prioridad: {priority_emoji.get(task['priority'], '❓')} {config.PRIORITY_LEVELS.get(task['priority'], 'Media')}"
    ])
    
    # Fecha límite
    if task.get('deadline'):
        lines.append(f"Fecha límite: {format_date(task['deadline'])}")
    
    # Descripción si existe
    if task.get('description'):
        lines.append(f"")
        lines.append(f"📝 {task['description']}")
    
    # Fecha de creación
    if task.get('created_at'):
        try:
            created = datetime.fromisoformat(task['created_at'])
            lines.append(f"")
            lines.append(f"🕐 Creada: {created.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
    
    return "\n".join(lines)


def format_task_list(tasks: List[Dict[str, Any]], 
                    title: str = "📋 Tareas") -> str:
    """
    Formatea una lista de tareas de forma resumida.
    
    Args:
        tasks: Lista de tareas
        title: Título de la lista
        
    Returns:
        String formateado con la lista de tareas
    """
    if not tasks:
        return f"{title}\n\n❌ No hay tareas"
    
    lines = [f"<b>{title}</b>", ""]
    
    for i, task in enumerate(tasks, 1):
        # Emoji de estado
        if task['status'] == 'completed':
            status = "✅"
        elif task['status'] == 'in_progress':
            status = "🔄"
        else:
            status = "⏳"
        
        # Emoji de prioridad
        priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
        
        # Fecha si tiene
        deadline_str = ""
        if task.get('deadline'):
            deadline_str = f" - {format_date(task['deadline'])}"
        
        lines.append(f"{i}. {status}{priority} {task['title']}{deadline_str}")
    
    return "\n".join(lines)


def format_note(note: Dict[str, Any]) -> str:
    """
    Formatea una nota completa.
    
    Args:
        note: Diccionario con datos de la nota
        
    Returns:
        String formateado con la información de la nota
    """
    lines = [
        f"📝 <b>{note['title']}</b>",
        f""
    ]
    
    # Etiquetas si existen
    if note.get('tags'):
        tags = note['tags'].split(',')
        tags_str = " ".join([f"#{tag.strip()}" for tag in tags if tag.strip()])
        lines.append(f"🏷️ {tags_str}")
        lines.append("")
    
    # Contenido
    lines.append(note['content'])
    
    # Fecha de creación
    if note.get('created_at'):
        try:
            created = datetime.fromisoformat(note['created_at'])
            lines.append("")
            lines.append(f"🕐 Creada: {created.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
    
    return "\n".join(lines)


def format_daily_summary(tasks_today: List[Dict[str, Any]],
                        tasks_overdue: List[Dict[str, Any]],
                        upcoming_deadlines: List[Dict[str, Any]],
                        active_projects: int) -> str:
    """
    Formatea el resumen diario que se envía cada mañana.
    
    Args:
        tasks_today: Tareas con fecha límite hoy
        tasks_overdue: Tareas atrasadas
        upcoming_deadlines: Próximas entregas de proyectos (7 días)
        active_projects: Número de proyectos activos
        
    Returns:
        String formateado con el resumen diario
    """
    today = date.today()
    
    lines = [
        f"🌅 <b>Buenos días! Resumen del {today.strftime('%d/%m/%Y')}</b>",
        f""
    ]
    
    # Resumen general
    lines.append(f"📊 <b>Estado general</b>")
    lines.append(f"📁 Proyectos activos: {active_projects}")
    lines.append(f"📅 Tareas de hoy: {len(tasks_today)}")
    lines.append(f"⚠️ Tareas atrasadas: {len(tasks_overdue)}")
    lines.append("")
    
    # Tareas de hoy
    if tasks_today:
        lines.append(f"<b>📅 Tareas para hoy:</b>")
        for i, task in enumerate(tasks_today[:5], 1):  # Máximo 5
            priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            lines.append(f"{i}. {priority} {task['title']}")
        
        if len(tasks_today) > 5:
            lines.append(f"... y {len(tasks_today) - 5} más")
        lines.append("")
    
    # Tareas atrasadas
    if tasks_overdue:
        lines.append(f"<b>⚠️ Tareas atrasadas:</b>")
        for i, task in enumerate(tasks_overdue[:3], 1):  # Máximo 3
            priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
            days_overdue = (today - datetime.strptime(task['deadline'], "%Y-%m-%d").date()).days
            lines.append(f"{i}. {priority} {task['title']} ({days_overdue} días)")
        
        if len(tasks_overdue) > 3:
            lines.append(f"... y {len(tasks_overdue) - 3} más")
        lines.append("")
    
    # Próximas entregas
    if upcoming_deadlines:
        lines.append(f"<b>⏰ Próximas entregas (7 días):</b>")
        for i, project in enumerate(upcoming_deadlines[:3], 1):
            lines.append(f"{i}. {project['name']} - {format_date(project['deadline'])}")
        
        if len(upcoming_deadlines) > 3:
            lines.append(f"... y {len(upcoming_deadlines) - 3} más")
        lines.append("")
    
    # Motivación
    if not tasks_today and not tasks_overdue:
        lines.append(f"✨ ¡Genial! No tienes tareas urgentes hoy. ¡Buen momento para avanzar proyectos!")
    elif tasks_overdue:
        lines.append(f"💪 Tienes tareas atrasadas. ¡Vamos a ponernos al día!")
    else:
        lines.append(f"🚀 ¡A por un día productivo!")
    
    return "\n".join(lines)


def format_weekly_stats(stats: Dict[str, Any]) -> str:
    """
    Formatea las estadísticas semanales.
    
    Args:
        stats: Diccionario con estadísticas de la semana
        
    Returns:
        String formateado con las estadísticas
    """
    lines = [
        f"📊 <b>Resumen Semanal</b>",
        f"🗓️ {stats['week_start']} - {stats['week_end']}",
        f"",
        f"<b>📋 Tareas</b>",
        f"➕ Creadas: {stats['tasks_created']}",
        f"✅ Completadas: {stats['tasks_completed']}",
        f"⚠️ Atrasadas: {stats['tasks_overdue']}",
        f"📈 Tasa de cumplimiento: {stats['completion_rate']}%",
        f"",
        f"<b>📊 Productividad</b>",
        f"⚡ Media diaria: {stats['daily_average']} tareas completadas",
        f""
    ]
    
    # Proyectos con progreso
    if stats.get('project_progress'):
        lines.append(f"<b>📁 Progreso de proyectos</b>")
        for proj in stats['project_progress']:
            lines.append(f"• {proj['name']}: {proj['progress']}%")
        lines.append("")
    
    # Comparativa con semana anterior
    if stats.get('comparison'):
        comp = stats['comparison']
        if comp > 0:
            lines.append(f"📈 {comp}% mejor que la semana anterior")
        elif comp < 0:
            lines.append(f"📉 {abs(comp)}% menos que la semana anterior")
        else:
            lines.append(f"➡️ Igual que la semana anterior")
    
    return "\n".join(lines)


def format_monthly_stats(stats: Dict[str, Any]) -> str:
    """
    Formatea las estadísticas mensuales.
    
    Args:
        stats: Diccionario con estadísticas del mes
        
    Returns:
        String formateado con las estadísticas
    """
    lines = [
        f"📊 <b>Resumen Mensual</b>",
        f"📅 {stats['month_name']} {stats['year']}",
        f"",
        f"<b>📋 Tareas del mes</b>",
        f"➕ Creadas: {stats['tasks_created']}",
        f"✅ Completadas: {stats['tasks_completed']}",
        f"⚠️ Atrasadas: {stats['tasks_overdue']}",
        f"📈 Puntualidad: {stats['on_time_rate']}%",
        f"",
        f"<b>📁 Proyectos</b>",
        f"✅ Finalizados: {stats['projects_completed']}",
        f"🟢 Activos: {stats['projects_active']}",
        f"",
        f"<b>📊 Distribución por prioridad</b>",
        f"🔴 Alta: {stats['priority_high']}",
        f"🟡 Media: {stats['priority_medium']}",
        f"🟢 Baja: {stats['priority_low']}",
        f""
    ]
    
    # Semana más productiva
    if stats.get('best_week'):
        lines.append(f"🏆 Mejor semana: Semana {stats['best_week']} ({stats['best_week_tasks']} tareas)")
    
    return "\n".join(lines)


def format_dashboard(summary: Dict[str, Any]) -> str:
    """
    Formatea el dashboard principal.
    
    Args:
        summary: Diccionario con el resumen general
        
    Returns:
        String formateado con el dashboard
    """
    lines = [
        f"📊 <b>Dashboard Personal</b>",
        f"",
        f"<b>📋 Tareas</b>",
        f"⏳ Pendientes: {summary['tasks_pending']}",
        f"🔄 En progreso: {summary['tasks_in_progress']}",
        f"✅ Completadas (hoy): {summary['tasks_completed_today']}",
        f"⚠️ Atrasadas: {summary['tasks_overdue']}",
        f"",
        f"<b>📁 Proyectos</b>",
        f"🟢 Activos: {summary['projects_active']}",
        f"⏸️ Pausados: {summary['projects_paused']}",
        f""
    ]
    
    # Próximas entregas
    if summary.get('upcoming_deadlines'):
        lines.append(f"<b>⏰ Próximas entregas (7 días)</b>")
        for deadline in summary['upcoming_deadlines'][:3]:
            lines.append(f"• {deadline['name']} - {format_date(deadline['deadline'])}")
        lines.append("")
    
    # Motivación según el estado
    if summary['tasks_overdue'] > 0:
        lines.append(f"⚠️ Tienes {summary['tasks_overdue']} tareas atrasadas que requieren atención")
    elif summary['tasks_pending'] == 0:
        lines.append(f"✨ ¡Excelente! Todas tus tareas están al día")
    else:
        lines.append(f"💪 Sigue así! Mantén el ritmo de trabajo")
    
    return "\n".join(lines)


def escape_markdown(text: str) -> str:
    """
    Escapa caracteres especiales para Markdown de Telegram.
    
    Args:
        text: Texto a escapar
        
    Returns:
        Texto con caracteres especiales escapados
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

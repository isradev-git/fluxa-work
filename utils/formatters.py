"""
Utilidades para formatear mensajes del bot con personalidad Cortana
Este archivo contiene funciones para dar formato a los mensajes que envía el bot
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import config

def format_date(date_str: Optional[str]) -> str:
    """Formatea una fecha en formato legible en español"""
    if not date_str:
        return "Sin deadline"
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        
        diff = (date_obj - today).days
        
        if diff < 0:
            return f"⚠️ Atrasado ({abs(diff)} días)"
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
    """Formatea la información de un proyecto"""
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
    
    lines = [
        f"📁 <b>{project['name']}</b>",
        f"",
        f"Estado: {status_emoji.get(project['status'], '❓')} {config.PROJECT_STATUS.get(project['status'], 'Desconocido')}",
        f"Prioridad: {priority_emoji.get(project['priority'], '❓')} {config.PRIORITY_LEVELS.get(project['priority'], 'Media')}"
    ]
    
    if project.get('client'):
        lines.append(f"Cliente: {project['client']}")
    
    if project.get('deadline'):
        lines.append(f"Deadline: {format_date(project['deadline'])}")
    
    if project.get('description'):
        lines.append(f"")
        lines.append(f"📄 {project['description']}")
    
    return "\n".join(lines)


def format_project_with_progress(project: Dict[str, Any], 
                                 progress: Dict[str, Any]) -> str:
    """Formatea un proyecto incluyendo su progreso"""
    base = format_project(project, include_progress=False)
    
    lines = [base, ""]
    
    if progress['total_tasks'] > 0:
        lines.append(f"📊 <b>Progreso de Objetivos</b>")
        lines.append(f"Total: {progress['total_tasks']} objetivos")
        lines.append(f"✅ Completados: {progress['completed_tasks']}")
        lines.append(f"⏳ Pendientes: {progress['pending_tasks']}")
        
        percentage = progress['percentage']
        bar_length = 10
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        lines.append(f"")
        lines.append(f"[{bar}] {percentage}%")
    else:
        lines.append(f"📊 Sin objetivos asignados todavía.")
    
    return "\n".join(lines)


def format_task(task: Dict[str, Any], include_project: bool = False,
               project_name: Optional[str] = None) -> str:
    """Formatea la información de una tarea"""
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
    
    lines = [
        f"{status_emoji.get(task['status'], '❓')}{priority_emoji.get(task['priority'], '❓')} <b>{task['title']}</b>",
        f""
    ]
    
    lines.append(f"Estado: {config.TASK_STATUS.get(task['status'], 'Desconocido')}")
    lines.append(f"Prioridad: {config.PRIORITY_LEVELS.get(task['priority'], 'Media')}")
    
    if task.get('deadline'):
        lines.append(f"Deadline: {format_date(task['deadline'])}")
    
    if include_project and project_name:
        lines.append(f"Misión: {project_name}")
    
    if task.get('description'):
        lines.append(f"")
        lines.append(f"📄 {task['description']}")
    
    if task.get('created_at'):
        try:
            created = datetime.fromisoformat(task['created_at'])
            lines.append(f"")
            lines.append(f"📅 Creado: {created.strftime('%d/%m/%Y')}")
        except:
            pass
    
    if task['status'] == 'completed' and task.get('completed_at'):
        try:
            completed = datetime.fromisoformat(task['completed_at'])
            lines.append(f"✅ Completado: {completed.strftime('%d/%m/%Y')}")
        except:
            pass
    
    return "\n".join(lines)


def format_task_list(tasks: List[Dict[str, Any]], title: str) -> str:
    """Formatea una lista de tareas"""
    if not tasks:
        return f"{title}\n\n❌ No hay objetivos"
    
    lines = [f"<b>{title}</b>", ""]
    
    for i, task in enumerate(tasks, 1):
        if task['status'] == 'completed':
            status = "✅"
        elif task['status'] == 'in_progress':
            status = "🔄"
        else:
            status = "⏳"
        
        priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
        
        deadline_str = ""
        if task.get('deadline'):
            deadline_str = f" - {format_date(task['deadline'])}"
        
        lines.append(f"{i}. {status}{priority} {task['title']}{deadline_str}")
    
    return "\n".join(lines)


def format_note(note: Dict[str, Any]) -> str:
    """Formatea una nota completa"""
    lines = [
        f"📝 <b>{note['title']}</b>",
        f""
    ]
    
    if note.get('tags'):
        tags = note['tags'].split(',')
        tags_str = " ".join([f"#{tag.strip()}" for tag in tags if tag.strip()])
        lines.append(f"🏷️ {tags_str}")
        lines.append("")
    
    lines.append(note['content'])
    
    if note.get('created_at'):
        try:
            created = datetime.fromisoformat(note['created_at'])
            lines.append("")
            lines.append(f"🕐 Archivado: {created.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
    
    return "\n".join(lines)


def format_dashboard(summary: Dict[str, Any]) -> str:
    """Formatea el dashboard principal"""
    lines = [
        f"📊 <b>Análisis Táctico</b>",
        f""
    ]
    
    lines.append(f"⏳ Objetivos pendientes: {summary['tasks_pending']}")
    lines.append(f"🔄 En progreso: {summary['tasks_in_progress']}")
    lines.append(f"✅ Completados hoy: {summary['tasks_completed_today']}")
    
    if summary['tasks_overdue'] > 0:
        lines.append(f"⚠️ Atrasados: {summary['tasks_overdue']}")
    
    lines.append("")
    lines.append(f"📁 Misiones activas: {summary['projects_active']}")
    
    if summary['projects_paused'] > 0:
        lines.append(f"⏸️ Misiones pausadas: {summary['projects_paused']}")
    
    if summary.get('upcoming_deadlines'):
        lines.append("")
        lines.append(f"⏰ <b>Próximos Deadlines (7 días):</b>")
        for i, project in enumerate(summary['upcoming_deadlines'][:3], 1):
            lines.append(f"{i}. {project['name']} - {format_date(project['deadline'])}")
        
        if len(summary['upcoming_deadlines']) > 3:
            lines.append(f"... y {len(summary['upcoming_deadlines']) - 3} más")
    
    lines.append("")
    
    if summary['tasks_overdue'] > 0:
        lines.append("⚠️ Prioridad: Resolver objetivos atrasados.")
    elif summary['tasks_pending'] == 0:
        lines.append("✨ Todos los objetivos están bajo control.")
    else:
        lines.append("📋 Sistema operacional. Todo en orden.")
    
    return "\n".join(lines)


def format_progress_bar(percentage: float, length: int = 10) -> str:
    """Crea una barra de progreso visual"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage}%"
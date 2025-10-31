"""
Handler de tareas
Gestiona la visualización, creación y modificación de tareas
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime, date, timedelta

import config
from database.models import DatabaseManager, Task, Project
from utils.keyboards import (
    get_tasks_menu,
    get_task_list_keyboard,
    get_task_detail_keyboard,
    get_priority_keyboard,
    get_cancel_keyboard
)
from utils.formatters import format_task

# Inicializar gestores
db_manager = DatabaseManager()
task_manager = Task(db_manager)
project_manager = Project(db_manager)

# Estados para el ConversationHandler de creación de tareas
TASK_TITLE, TASK_DESCRIPTION, TASK_PRIORITY, TASK_DEADLINE, TASK_PROJECT = range(5)


async def show_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de tareas desde un callback"""
    query = update.callback_query
    await query.answer()
    
    message = """
✅ <b>Gestión de Tareas</b>

Organiza todas tus tareas y pendientes.

Puedes filtrar por fecha, prioridad o proyecto.

¿Qué quieres hacer?
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lista tareas según diferentes filtros.
    
    Filtros disponibles:
    - today: Tareas de hoy
    - week: Tareas de esta semana
    - overdue: Tareas atrasadas
    - high_priority: Tareas de alta prioridad
    - all: Todas las tareas
    - project_[id]: Tareas de un proyecto específico
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer tipo de filtro del callback_data
    callback_parts = query.data.split('_')
    
    # Determinar filtro y título
    filters = {}
    title = "📋 Tareas"
    filter_type = "all"
    
    if 'today' in callback_parts:
        filters['today'] = True
        filters['parent_only'] = True
        title = "📅 Tareas de Hoy"
        filter_type = "today"
    
    elif 'week' in callback_parts:
        # Tareas de esta semana
        today = date.today()
        week_end = today + timedelta(days=7)
        filters['parent_only'] = True
        title = "📅 Tareas de esta Semana"
        filter_type = "week"
        
        # Obtener todas y filtrar por fecha
        all_tasks = task_manager.get_all({'parent_only': True})
        tasks = [
            t for t in all_tasks 
            if t.get('deadline') 
            and t['status'] != 'completed'
            and datetime.strptime(t['deadline'], "%Y-%m-%d").date() <= week_end
        ]
    
    elif 'overdue' in callback_parts:
        filters['overdue'] = True
        filters['parent_only'] = True
        title = "⚠️ Tareas Atrasadas"
        filter_type = "overdue"
    
    elif 'high' in callback_parts:
        filters['priority'] = 'high'
        filters['parent_only'] = True
        title = "🔴 Alta Prioridad"
        filter_type = "high_priority"
    
    elif 'project' in callback_parts:
        # Tareas de un proyecto específico
        try:
            project_id = int(callback_parts[-1])
            filters['project_id'] = project_id
            filters['parent_only'] = True
            
            # Obtener nombre del proyecto
            project = project_manager.get_by_id(project_id)
            if project:
                title = f"📁 Tareas de: {project['name']}"
            filter_type = f"project_{project_id}"
        except ValueError:
            pass
    
    else:
        filters['parent_only'] = True
        title = "📋 Todas las Tareas"
        filter_type = "all"
    
    # Determinar página
    page = 0
    if 'page' in callback_parts:
        try:
            page = int(callback_parts[-1])
        except:
            page = 0
    
    # Obtener tareas según filtros (si no se filtraron antes por semana)
    if 'week' not in callback_parts:
        tasks = task_manager.get_all(filters if filters else None)
    
    # Construir mensaje
    if not tasks:
        message = f"{title}\n\n❌ No hay tareas en esta categoría."
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
        return
    
    # Contar tareas por estado
    completed = len([t for t in tasks if t['status'] == 'completed'])
    in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
    pending = len([t for t in tasks if t['status'] == 'pending'])
    
    message = f"""{title}

Total: {len(tasks)} tareas
✅ Completadas: {completed}
🔄 En progreso: {in_progress}
⏳ Pendientes: {pending}

Selecciona una tarea para ver detalles:"""
    
    # Crear teclado con lista de tareas
    keyboard = get_task_list_keyboard(tasks, filter_type=filter_type, page=page)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra los detalles de una tarea específica.
    
    Callback format: task_view_123
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID de la tarea
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID de tarea inválido")
        return
    
    # Obtener tarea
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Obtener nombre del proyecto si está asociada
    project_name = None
    if task.get('project_id'):
        project = project_manager.get_by_id(task['project_id'])
        if project:
            project_name = project['name']
    
    # Formatear mensaje
    message = format_task(task, include_project=True, project_name=project_name)
    
    # Verificar si tiene subtareas
    subtasks = task_manager.get_subtasks(task_id)
    has_subtasks = len(subtasks) > 0
    
    # Si tiene subtareas, agregar resumen
    if has_subtasks:
        completed_subtasks = len([s for s in subtasks if s['status'] == 'completed'])
        message += f"\n\n📋 Subtareas: {completed_subtasks}/{len(subtasks)} completadas"
    
    # Crear teclado con acciones
    keyboard = get_task_detail_keyboard(task_id, task['status'], has_subtasks)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def change_task_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cambia el estado de una tarea.
    
    Callback format: task_status_123_in_progress
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID y nuevo estado
    parts = query.data.split('_')
    
    try:
        task_id = int(parts[2])
        new_status = parts[3]
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    # Actualizar estado
    success = task_manager.update_status(task_id, new_status)
    
    if success:
        status_messages = {
            'pending': "⏳ Tarea marcada como pendiente",
            'in_progress': "🔄 Tarea en progreso",
            'completed': "✅ Tarea completada"
        }
        
        await query.answer(
            status_messages.get(new_status, "✅ Estado actualizado"),
            show_alert=False
        )
        
        # Volver a mostrar la tarea
        await view_task(update, context)
    else:
        await query.answer("❌ Error al actualizar estado", show_alert=True)


async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Marca una tarea como completada.
    
    Callback format: task_complete_123
    """
    query = update.callback_query
    
    # Extraer ID de la tarea
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Completar tarea
    success = task_manager.update_status(task_id, 'completed')
    
    if success:
        await query.answer("✅ ¡Tarea completada! Buen trabajo", show_alert=True)
        await view_task(update, context)
    else:
        await query.answer("❌ Error al completar tarea", show_alert=True)


async def postpone_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Pospone una tarea X días.
    
    Callback format: task_postpone_123_1 (posponer tarea 123 por 1 día)
    """
    query = update.callback_query
    
    # Extraer ID y días
    parts = query.data.split('_')
    
    try:
        task_id = int(parts[2])
        days = int(parts[3])
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    # Verificar que la tarea tenga fecha límite
    task = task_manager.get_by_id(task_id)
    
    if not task or not task.get('deadline'):
        await query.answer("❌ Esta tarea no tiene fecha límite", show_alert=True)
        return
    
    # Posponer
    success = task_manager.postpone(task_id, days)
    
    if success:
        days_text = "día" if days == 1 else f"{days} días"
        await query.answer(
            f"📅 Tarea pospuesta {days_text}",
            show_alert=True
        )
        await view_task(update, context)
    else:
        await query.answer("❌ Error al posponer tarea", show_alert=True)


# ==================== CREACIÓN DE TAREAS ====================

async def create_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el proceso de creación de una nueva tarea.
    Este es el primer paso del diálogo.
    """
    query = update.callback_query
    await query.answer()
    
    # Inicializar datos de la tarea en el contexto
    context.user_data['new_task'] = {}
    
    message = """
✅ <b>Nueva Tarea</b>

Vamos a crear una nueva tarea paso a paso.

<b>Paso 1/4:</b> ¿Cuál es el título de la tarea?

Ejemplos:
• Implementar login con OAuth
• Revisar diseño de la landing
• Actualizar documentación API

Escribe el título de tu tarea:
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    
    return TASK_TITLE


async def task_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe el título de la tarea y pide la descripción.
    """
    # Guardar título
    title = update.message.text.strip()
    
    if len(title) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres.\n\n"
            "Intenta con un título más corto:"
        )
        return TASK_TITLE
    
    context.user_data['new_task']['title'] = title
    
    message = f"""
✅ <b>Nueva Tarea</b>

Título: <i>{title}</i>

<b>Paso 2/4:</b> Agrega una descripción (opcional)

La descripción puede incluir:
• Detalles técnicos
• Requisitos específicos
• Enlaces o referencias
• Cualquier información adicional

Escribe la descripción o envía <b>-</b> para omitir:
"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    
    return TASK_DESCRIPTION


async def task_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la descripción y pide la prioridad.
    """
    description = update.message.text.strip()
    
    # Si el usuario pone "-", no agregar descripción
    if description == "-":
        description = ""
    
    context.user_data['new_task']['description'] = description
    
    # Obtener título para mostrarlo
    title = context.user_data['new_task']['title']
    
    message = f"""
✅ <b>Nueva Tarea</b>

Título: <i>{title}</i>
Descripción: {'<i>' + description[:50] + '...</i>' if description else '<i>Sin descripción</i>'}

<b>Paso 3/4:</b> Selecciona la prioridad

¿Qué tan importante es esta tarea?
"""
    
    # Crear teclado de prioridad
    keyboard = get_priority_keyboard()
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )
    
    return TASK_PRIORITY


async def task_priority_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la prioridad y pide la fecha límite.
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer prioridad del callback_data (format: priority_high)
    priority = query.data.split('_')[1]
    context.user_data['new_task']['priority'] = priority
    
    title = context.user_data['new_task']['title']
    priority_text = config.PRIORITY_LEVELS.get(priority, 'Media')
    
    message = f"""
✅ <b>Nueva Tarea</b>

Título: <i>{title}</i>
Prioridad: {priority_text}

<b>Paso 4/4:</b> ¿Cuál es la fecha límite?

Formatos aceptados:
• <code>YYYY-MM-DD</code> (ejemplo: 2024-12-31)
• <code>hoy</code> - Para hoy
• <code>mañana</code> - Para mañana
• <code>+3</code> - Para dentro de 3 días
• <code>-</code> - Sin fecha límite

Escribe la fecha límite:
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    
    return TASK_DEADLINE


async def task_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la fecha límite y pregunta si asociar a un proyecto.
    """
    deadline_input = update.message.text.strip().lower()
    
    # Procesar entrada de fecha
    deadline = None
    today = date.today()
    
    if deadline_input == "-":
        deadline = None
    elif deadline_input == "hoy":
        deadline = today.strftime("%Y-%m-%d")
    elif deadline_input == "mañana" or deadline_input == "manana":
        deadline = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif deadline_input.startswith("+"):
        try:
            days = int(deadline_input[1:])
            deadline = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido. Ejemplo: +3 para dentro de 3 días\n\n"
                "Intenta de nuevo:"
            )
            return TASK_DEADLINE
    else:
        # Intentar parsear fecha YYYY-MM-DD
        try:
            parsed_date = datetime.strptime(deadline_input, "%Y-%m-%d").date()
            deadline = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de fecha inválido.\n\n"
                "Usa el formato: YYYY-MM-DD (ejemplo: 2024-12-31)\n"
                "O escribe: hoy, mañana, +3, -\n\n"
                "Intenta de nuevo:"
            )
            return TASK_DEADLINE
    
    context.user_data['new_task']['deadline'] = deadline
    
    # Obtener proyectos activos
    projects = project_manager.get_all(status='active')
    
    title = context.user_data['new_task']['title']
    deadline_text = deadline if deadline else "Sin fecha límite"
    
    if not projects:
        # No hay proyectos, crear tarea directamente
        message = f"""
✅ <b>Nueva Tarea - Resumen</b>

Título: <i>{title}</i>
Fecha límite: {deadline_text}

No tienes proyectos activos para asociar esta tarea.

¿Confirmas la creación de la tarea?
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Crear tarea", callback_data="task_create_confirm"),
                InlineKeyboardButton("❌ Cancelar", callback_data="task_create_cancel")
            ]
        ]
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return TASK_PROJECT
    
    # Hay proyectos, preguntar si quiere asociar
    message = f"""
✅ <b>Nueva Tarea - Resumen</b>

Título: <i>{title}</i>
Fecha límite: {deadline_text}

<b>Último paso (opcional):</b> ¿Asociar a un proyecto?

Tienes {len(projects)} proyecto(s) activo(s):
"""
    
    # Crear teclado con proyectos
    keyboard = []
    for project in projects[:5]:  # Máximo 5 proyectos
        keyboard.append([
            InlineKeyboardButton(
                f"📁 {project['name']}",
                callback_data=f"task_project_{project['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("➕ Sin proyecto", callback_data="task_project_none")
    ])
    keyboard.append([
        InlineKeyboardButton("❌ Cancelar", callback_data="task_create_cancel")
    ])
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return TASK_PROJECT


async def task_project_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la selección de proyecto (o ninguno) y crea la tarea.
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer selección
    if query.data == "task_project_none":
        project_id = None
    elif query.data == "task_create_confirm":
        project_id = None
    else:
        # Format: task_project_123
        try:
            project_id = int(query.data.split('_')[-1])
        except ValueError:
            project_id = None
    
    # Obtener datos de la tarea
    task_data = context.user_data['new_task']
    
    # Crear tarea en la base de datos
    try:
        task_id = task_manager.create(
            title=task_data['title'],
            description=task_data.get('description', ''),
            project_id=project_id,
            priority=task_data.get('priority', 'medium'),
            deadline=task_data.get('deadline')
        )
        
        # Mensaje de éxito
        message = f"""
🎉 <b>¡Tarea creada con éxito!</b>

✅ {task_data['title']}

ID de tarea: {task_id}
"""
        
        # Limpiar datos del contexto
        context.user_data.pop('new_task', None)
        
        # Botones para ver la tarea o crear otra
        keyboard = [
            [
                InlineKeyboardButton("👁️ Ver tarea", callback_data=f"task_view_{task_id}"),
                InlineKeyboardButton("➕ Nueva tarea", callback_data="task_new")
            ],
            [
                InlineKeyboardButton("📋 Ver todas", callback_data="task_list_all")
            ]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error al crear la tarea: {e}\n\n"
            "Intenta de nuevo.",
            reply_markup=get_tasks_menu()
        )
        return ConversationHandler.END


async def cancel_task_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancela el proceso de creación de tarea.
    """
    query = update.callback_query
    await query.answer("❌ Creación cancelada", show_alert=False)
    
    # Limpiar datos del contexto
    context.user_data.pop('new_task', None)
    
    message = """
❌ <b>Creación de tarea cancelada</b>

¿Qué quieres hacer?
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )
    
    return ConversationHandler.END

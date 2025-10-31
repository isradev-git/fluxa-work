"""
Conversation handlers para crear y editar tareas
Maneja diálogos multi-paso para crear nuevas tareas, subtareas y edición
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime, date, timedelta

import config
from database.models import DatabaseManager, Task, Project
from utils.keyboards import get_tasks_menu, get_priority_keyboard, get_cancel_keyboard

# Inicializar gestores
db_manager = DatabaseManager()
task_manager = Task(db_manager)
project_manager = Project(db_manager)

# Estados del conversationhandler
(
    TASK_TITLE,
    TASK_DESCRIPTION,
    TASK_PRIORITY,
    TASK_DEADLINE,
    TASK_PROJECT,
    TASK_CONFIRM,
    ADD_SUBTASK_TITLE,
    ADD_SUBTASK_DESC,
    EDIT_FIELD,
    EDIT_VALUE
) = range(10)


async def create_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de creación de tarea"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['new_task'] = {}
    
    message = """
📝 <b>Nueva Tarea</b>

Vamos a crear una nueva tarea paso a paso.

<b>Paso 1/5: Título</b>

¿Cuál es el título de la tarea?

Ejemplo: "Implementar API de pagos"
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="task_create_cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_TITLE


async def task_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el título de la tarea"""
    title = update.message.text
    
    if len(title) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres.\n\n"
            "Por favor, envía un título más corto:"
        )
        return TASK_TITLE
    
    context.user_data['new_task']['title'] = title
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}

<b>Paso 2/5: Descripción (opcional)</b>

¿Quieres agregar una descripción?

Envía la descripción o escribe <code>-</code> para omitir.
"""
    
    keyboard = [[InlineKeyboardButton("⏭️ Omitir", callback_data="task_skip_description")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_DESCRIPTION


async def task_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la descripción de la tarea"""
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        description = ""
    else:
        description = update.message.text
        if description == "-":
            description = ""
    
    context.user_data['new_task']['description'] = description
    
    title = context.user_data['new_task']['title']
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Descripción: {description if description else "Sin descripción"}

<b>Paso 3/5: Prioridad</b>

¿Qué prioridad tiene esta tarea?
"""
    
    keyboard = [
        [InlineKeyboardButton("🔴 Alta", callback_data="task_priority_high")],
        [InlineKeyboardButton("🟡 Media", callback_data="task_priority_medium")],
        [InlineKeyboardButton("🟢 Baja", callback_data="task_priority_low")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    return TASK_PRIORITY


async def task_priority_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la prioridad de la tarea"""
    query = update.callback_query
    await query.answer()
    
    priority = query.data.split('_')[-1]
    context.user_data['new_task']['priority'] = priority
    
    title = context.user_data['new_task']['title']
    priority_text = config.PRIORITY_LEVELS.get(priority, priority)
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Prioridad: {priority_text}

<b>Paso 4/5: Fecha límite (opcional)</b>

¿Cuándo debe estar lista esta tarea?

Puedes:
• Escribir una fecha: YYYY-MM-DD
• Usar atajos rápidos
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 Hoy", callback_data="task_deadline_today")],
        [InlineKeyboardButton("📅 Mañana", callback_data="task_deadline_tomorrow")],
        [InlineKeyboardButton("📅 En 3 días", callback_data="task_deadline_3")],
        [InlineKeyboardButton("📅 En 1 semana", callback_data="task_deadline_7")],
        [InlineKeyboardButton("⏭️ Sin fecha", callback_data="task_deadline_none")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_DEADLINE


async def task_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la fecha límite de la tarea"""
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        deadline_option = query.data.split('_')[-1]
        
        if deadline_option == "none":
            deadline = None
        elif deadline_option == "today":
            deadline = date.today().strftime("%Y-%m-%d")
        elif deadline_option == "tomorrow":
            deadline = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            try:
                days = int(deadline_option)
                deadline = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
            except ValueError:
                deadline = None
    else:
        deadline_text = update.message.text.strip()
        try:
            datetime.strptime(deadline_text, "%Y-%m-%d")
            deadline = deadline_text
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de fecha inválido. Usa YYYY-MM-DD\n\n"
                "Ejemplo: 2024-12-31\n\n"
                "Intenta de nuevo:"
            )
            return TASK_DEADLINE
    
    context.user_data['new_task']['deadline'] = deadline
    
    title = context.user_data['new_task']['title']
    priority_text = config.PRIORITY_LEVELS.get(context.user_data['new_task']['priority'], "Media")
    deadline_text = deadline if deadline else "Sin fecha límite"
    
    # Obtener proyectos activos
    projects = project_manager.get_all(status='active')
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Prioridad: {priority_text}
✅ Fecha límite: {deadline_text}

<b>Paso 5/5: Proyecto (opcional)</b>

¿A qué proyecto pertenece esta tarea?
"""
    
    keyboard = []
    
    if projects:
        for project in projects[:5]:
            keyboard.append([InlineKeyboardButton(
                f"📁 {project['name']}",
                callback_data=f"task_project_{project['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton("⏭️ Sin proyecto", callback_data="task_project_none")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    return TASK_PROJECT


async def task_project_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el proyecto de la tarea"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "task_project_none":
        project_id = None
    else:
        try:
            project_id = int(query.data.split('_')[-1])
        except ValueError:
            project_id = None
    
    context.user_data['new_task']['project_id'] = project_id
    
    # Mostrar resumen para confirmar
    task_data = context.user_data['new_task']
    
    project_name = "Sin proyecto"
    if project_id:
        project = project_manager.get_by_id(project_id)
        if project:
            project_name = project['name']
    
    message = f"""
📝 <b>Resumen de la Nueva Tarea</b>

<b>Título:</b> {task_data['title']}
<b>Descripción:</b> {task_data.get('description', 'Sin descripción')}
<b>Prioridad:</b> {config.PRIORITY_LEVELS.get(task_data['priority'], 'Media')}
<b>Fecha límite:</b> {task_data.get('deadline', 'Sin fecha')}
<b>Proyecto:</b> {project_name}

¿Crear esta tarea?
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Crear tarea", callback_data="task_confirm_yes"),
            InlineKeyboardButton("❌ Cancelar", callback_data="task_confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_CONFIRM


async def task_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la tarea en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    task_data = context.user_data.get('new_task', {})
    
    try:
        task_id = task_manager.create(
            title=task_data['title'],
            description=task_data.get('description', ''),
            project_id=task_data.get('project_id'),
            priority=task_data.get('priority', 'medium'),
            deadline=task_data.get('deadline')
        )
        
        message = f"""
✅ <b>¡Tarea creada con éxito!</b>

La tarea "{task_data['title']}" ha sido creada.

Puedes verla en el menú de tareas.
"""
        
        keyboard = [
            [InlineKeyboardButton("👁️ Ver tarea", callback_data=f"task_view_{task_id}")],
            [InlineKeyboardButton("📋 Ver todas las tareas", callback_data="task_list_all")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        message = f"❌ Error al crear la tarea: {str(e)}"
        await query.edit_message_text(message)
    
    context.user_data.pop('new_task', None)
    
    return ConversationHandler.END


async def task_creation_cancelled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la creación de la tarea"""
    query = update.callback_query
    await query.answer()
    
    message = """
❌ <b>Creación cancelada</b>

No se ha creado ninguna tarea.
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )
    
    context.user_data.pop('new_task', None)
    
    return ConversationHandler.END
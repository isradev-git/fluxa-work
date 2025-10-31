"""
Conversation handlers para crear y editar tareas
Maneja diálogos multi-paso para crear nuevas tareas
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
    TASK_CONFIRM
) = range(6)


async def create_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el proceso de creación de tarea.
    Primera pregunta: ¿Cuál es el título de la tarea?
    """
    query = update.callback_query
    await query.answer()
    
    # Inicializar diccionario para guardar datos temporales
    context.user_data['new_task'] = {}
    
    message = """
📝 <b>Nueva Tarea</b>

Vamos a crear una nueva tarea paso a paso.

<b>Paso 1/5: Título</b>

¿Cuál es el título de la tarea?

Ejemplo: "Implementar API de pagos"
"""
    
    # Botón para cancelar
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="task_create_cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_TITLE


async def task_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe el título de la tarea.
    Segunda pregunta: ¿Descripción? (opcional)
    """
    title = update.message.text
    
    # Validar longitud
    if len(title) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres.\n\n"
            "Por favor, envía un título más corto:"
        )
        return TASK_TITLE
    
    # Guardar título
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
    """
    Recibe la descripción de la tarea.
    Tercera pregunta: ¿Prioridad?
    """
    # Puede venir de mensaje de texto o de botón "omitir"
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        description = ""
        is_callback = True
    else:
        description = update.message.text
        is_callback = False
        
        # Si el usuario escribió "-", omitir descripción
        if description == "-":
            description = ""
    
    # Guardar descripción
    context.user_data['new_task']['description'] = description
    
    title = context.user_data['new_task']['title']
    desc_text = description if description else "(sin descripción)"
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Descripción: {desc_text}

<b>Paso 3/5: Prioridad</b>

Selecciona la prioridad de la tarea:
"""
    
    # Teclado de prioridades
    keyboard = [
        [InlineKeyboardButton("🔴 Alta", callback_data="task_priority_high")],
        [InlineKeyboardButton("🟡 Media", callback_data="task_priority_medium")],
        [InlineKeyboardButton("🟢 Baja", callback_data="task_priority_low")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await query.edit_message_text(
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
    """
    Recibe la prioridad de la tarea.
    Cuarta pregunta: ¿Fecha límite?
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer prioridad del callback_data: "task_priority_high" -> "high"
    priority = query.data.split('_')[-1]
    context.user_data['new_task']['priority'] = priority
    
    title = context.user_data['new_task']['title']
    desc_text = context.user_data['new_task']['description'] or "(sin descripción)"
    priority_text = config.PRIORITY_LEVELS.get(priority, "Media")
    
    # Calcular fechas sugeridas
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Descripción: {desc_text}
✅ Prioridad: {priority_text}

<b>Paso 4/5: Fecha límite (opcional)</b>

¿Cuándo debe estar lista esta tarea?

Puedes usar los botones rápidos o enviar una fecha en formato <code>DD/MM/YYYY</code>
Ejemplo: <code>15/11/2024</code>
"""
    
    keyboard = [
        [InlineKeyboardButton(f"📅 Hoy ({today.strftime('%d/%m')})", 
                             callback_data=f"task_deadline_{today.isoformat()}")],
        [InlineKeyboardButton(f"📅 Mañana ({tomorrow.strftime('%d/%m')})", 
                             callback_data=f"task_deadline_{tomorrow.isoformat()}")],
        [InlineKeyboardButton(f"📅 En 1 semana ({next_week.strftime('%d/%m')})", 
                             callback_data=f"task_deadline_{next_week.isoformat()}")],
        [InlineKeyboardButton("⏭️ Sin fecha límite", 
                             callback_data="task_deadline_none")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return TASK_DEADLINE


async def task_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la fecha límite de la tarea.
    Quinta pregunta: ¿Asociar a un proyecto?
    """
    # Puede venir de callback (botones) o mensaje de texto (fecha escrita)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        # Extraer fecha del callback_data
        if "none" in query.data:
            deadline = None
        else:
            deadline_str = query.data.split('_')[-1]  # "task_deadline_2024-10-30" -> "2024-10-30"
            deadline = deadline_str
        
        is_callback = True
    else:
        # Usuario escribió la fecha
        date_text = update.message.text
        
        if date_text == "-":
            deadline = None
        else:
            # Parsear fecha DD/MM/YYYY
            try:
                date_obj = datetime.strptime(date_text, "%d/%m/%Y").date()
                deadline = date_obj.isoformat()
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha inválido.\n\n"
                    "Por favor usa el formato DD/MM/YYYY\n"
                    "Ejemplo: 15/11/2024\n\n"
                    "O escribe <code>-</code> para omitir."
                )
                return TASK_DEADLINE
        
        is_callback = False
    
    # Guardar deadline
    context.user_data['new_task']['deadline'] = deadline
    
    # Obtener proyectos activos para asociar
    projects = project_manager.get_all(status='active')
    
    title = context.user_data['new_task']['title']
    desc_text = context.user_data['new_task']['description'] or "(sin descripción)"
    priority = context.user_data['new_task']['priority']
    priority_text = config.PRIORITY_LEVELS.get(priority, "Media")
    
    if deadline:
        try:
            deadline_date = datetime.fromisoformat(deadline).date()
            deadline_text = deadline_date.strftime("%d/%m/%Y")
        except:
            deadline_text = deadline
    else:
        deadline_text = "(sin fecha límite)"
    
    message = f"""
📝 <b>Nueva Tarea</b>

✅ Título: {title}
✅ Descripción: {desc_text}
✅ Prioridad: {priority_text}
✅ Fecha límite: {deadline_text}

<b>Paso 5/5: Proyecto (opcional)</b>

¿Quieres asociar esta tarea a un proyecto?
"""
    
    keyboard = []
    
    # Agregar botones de proyectos activos
    if projects:
        for project in projects[:5]:  # Máximo 5 proyectos
            keyboard.append([InlineKeyboardButton(
                f"📁 {project['name'][:30]}",
                callback_data=f"task_project_{project['id']}"
            )])
    
    # Botón para no asociar a proyecto
    keyboard.append([InlineKeyboardButton(
        "⏭️ Sin proyecto",
        callback_data="task_project_none"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await query.edit_message_text(
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
    """
    Recibe el proyecto asociado.
    Muestra resumen y pide confirmación.
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID del proyecto
    if "none" in query.data:
        project_id = None
        project_name = None
    else:
        project_id = int(query.data.split('_')[-1])
        project = project_manager.get_by_id(project_id)
        project_name = project['name'] if project else None
    
    # Guardar proyecto
    context.user_data['new_task']['project_id'] = project_id
    
    # Mostrar resumen y pedir confirmación
    title = context.user_data['new_task']['title']
    description = context.user_data['new_task']['description']
    priority = context.user_data['new_task']['priority']
    deadline = context.user_data['new_task']['deadline']
    
    priority_text = config.PRIORITY_LEVELS.get(priority, "Media")
    
    if deadline:
        try:
            deadline_date = datetime.fromisoformat(deadline).date()
            deadline_text = deadline_date.strftime("%d/%m/%Y")
        except:
            deadline_text = deadline
    else:
        deadline_text = "Sin fecha límite"
    
    project_text = f"📁 {project_name}" if project_name else "Sin proyecto"
    desc_text = description if description else "Sin descripción"
    
    message = f"""
📝 <b>Resumen de Nueva Tarea</b>

<b>Título:</b> {title}
<b>Descripción:</b> {desc_text}
<b>Prioridad:</b> {priority_text}
<b>Fecha límite:</b> {deadline_text}
<b>Proyecto:</b> {project_text}

¿Confirmas la creación de esta tarea?
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
    """
    Crea la tarea en la base de datos.
    """
    query = update.callback_query
    await query.answer()
    
    # Obtener datos guardados
    task_data = context.user_data.get('new_task', {})
    
    # Crear tarea en la base de datos
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
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
        
    except Exception as e:
        message = f"❌ Error al crear la tarea: {str(e)}"
        await query.edit_message_text(message)
    
    # Limpiar datos temporales
    context.user_data.pop('new_task', None)
    
    return ConversationHandler.END


async def task_creation_cancelled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancela la creación de la tarea.
    """
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
    
    # Limpiar datos temporales
    context.user_data.pop('new_task', None)
    
    return ConversationHandler.END

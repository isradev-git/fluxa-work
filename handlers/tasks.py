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

# Estados para el ConversationHandler de creación/edición
(TASK_TITLE, TASK_DESCRIPTION, TASK_PRIORITY, TASK_DEADLINE, TASK_PROJECT,
 EDIT_FIELD, EDIT_VALUE, ADD_SUBTASK_TITLE, ADD_SUBTASK_DESC) = range(9)


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
    """Lista tareas según diferentes filtros"""
    query = update.callback_query
    await query.answer()
    
    # Extraer filtro (task_list_today, task_list_week, etc.)
    filter_type = query.data.split('_')[-1]
    
    # Obtener tareas según filtro
    filters = {}
    title = ""
    
    if filter_type == "today":
        filters = {'today': True}
        title = "📅 <b>Tareas de Hoy</b>"
    elif filter_type == "week":
        filters = {'deadline': (date.today(), date.today() + timedelta(days=7))}
        title = "📅 <b>Tareas de Esta Semana</b>"
    elif filter_type == "overdue":
        filters = {'overdue': True}
        title = "⚠️ <b>Tareas Atrasadas</b>"
    elif filter_type == "high":
        filters = {'priority': 'high'}
        title = "🔴 <b>Tareas de Alta Prioridad</b>"
    elif filter_type == "all":
        filters = {'parent_only': True}
        title = "📋 <b>Todas las Tareas</b>"
    else:
        filters = {}
        title = "📋 <b>Tareas</b>"
    
    tasks = task_manager.get_all(filters=filters)
    
    if not tasks:
        message = f"""{title}

❌ No hay tareas en esta categoría.
"""
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
    keyboard = get_task_list_keyboard(tasks, filter_type=filter_type, page=1)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los detalles de una tarea específica"""
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
    """Cambia el estado de una tarea"""
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
    """Marca una tarea como completada"""
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
    """Pospone una tarea X días"""
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


# ==================== AGREGAR SUBTAREA ====================

async def add_subtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso para agregar una subtarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        parent_task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Guardar ID de la tarea padre en el contexto
    context.user_data['parent_task_id'] = parent_task_id
    context.user_data['new_subtask'] = {}
    
    message = f"""
➕ <b>Nueva Subtarea</b>

Tarea principal: <b>{parent_task['title']}</b>

<b>Paso 1/2:</b> ¿Cuál es el título de la subtarea?

Ejemplos:
• Diseñar mockups
• Escribir tests unitarios
• Revisar código

Escribe el título:
"""
    
    keyboard = [[InlineKeyboardButton(
        "❌ Cancelar",
        callback_data=f"task_view_{parent_task_id}"
    )]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ADD_SUBTASK_TITLE


async def subtask_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el título de la subtarea"""
    title = update.message.text.strip()
    
    if len(title) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres.\n\n"
            "Por favor, envía un título más corto:"
        )
        return ADD_SUBTASK_TITLE
    
    context.user_data['new_subtask']['title'] = title
    parent_task_id = context.user_data['parent_task_id']
    
    message = f"""
➕ <b>Nueva Subtarea</b>

✅ Título: {title}

<b>Paso 2/2:</b> ¿Descripción? (opcional)

Envía la descripción o escribe <code>-</code> para omitir.
"""
    
    keyboard = [
        [InlineKeyboardButton("⏭️ Omitir", callback_data=f"subtask_skip_desc_{parent_task_id}")],
        [InlineKeyboardButton("❌ Cancelar", callback_data=f"task_view_{parent_task_id}")]
    ]
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ADD_SUBTASK_DESC


async def subtask_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la descripción de la subtarea o la omite"""
    
    # Verificar si viene del callback (omitir) o del mensaje
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        description = ""
    else:
        description = update.message.text.strip()
        if description == "-":
            description = ""
    
    parent_task_id = context.user_data['parent_task_id']
    subtask_data = context.user_data['new_subtask']
    parent_task = task_manager.get_by_id(parent_task_id)
    
    # Crear subtarea en la base de datos
    try:
        subtask_id = task_manager.create(
            title=subtask_data['title'],
            description=description,
            project_id=parent_task.get('project_id'),
            priority=parent_task.get('priority', 'medium'),
            deadline=parent_task.get('deadline'),
            parent_task_id=parent_task_id
        )
        
        message = f"""
✅ <b>Subtarea creada con éxito</b>

La subtarea "{subtask_data['title']}" ha sido agregada a:
<b>{parent_task['title']}</b>

Puedes verla en la lista de subtareas.
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Ver subtareas", callback_data=f"task_view_subtasks_{parent_task_id}")],
            [InlineKeyboardButton("🔙 Volver a tarea", callback_data=f"task_view_{parent_task_id}")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        error_message = f"❌ Error al crear la subtarea: {str(e)}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
    
    # Limpiar datos temporales
    context.user_data.pop('parent_task_id', None)
    context.user_data.pop('new_subtask', None)
    
    return ConversationHandler.END


async def view_subtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra todas las subtareas de una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        parent_task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    subtasks = task_manager.get_subtasks(parent_task_id)
    
    if not subtasks:
        message = f"""
📋 <b>Subtareas</b>

Tarea principal: <b>{parent_task['title']}</b>

❌ Esta tarea no tiene subtareas todavía.
"""
        keyboard = [[InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver",
            callback_data=f"task_view_{parent_task_id}"
        )]]
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    completed = len([s for s in subtasks if s['status'] == 'completed'])
    
    message = f"""
📋 <b>Subtareas de: {parent_task['title']}</b>

Progreso: {completed}/{len(subtasks)} completadas

<b>Lista de subtareas:</b>
"""
    
    for i, subtask in enumerate(subtasks, 1):
        if subtask['status'] == 'completed':
            status_emoji = "✅"
        elif subtask['status'] == 'in_progress':
            status_emoji = "🔄"
        else:
            status_emoji = "⏳"
        
        priority_emoji = {
            'high': "🔴",
            'medium': "🟡",
            'low': "🟢"
        }.get(subtask['priority'], "⚪")
        
        message += f"\n{i}. {status_emoji}{priority_emoji} {subtask['title']}"
    
    keyboard = []
    for subtask in subtasks[:10]:
        title_short = subtask['title'][:30] + "..." if len(subtask['title']) > 30 else subtask['title']
        
        keyboard.append([InlineKeyboardButton(
            f"👁️ {title_short}",
            callback_data=f"task_view_{subtask['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver a tarea principal",
        callback_data=f"task_view_{parent_task_id}"
    )])
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================== EDICIÓN DE TAREAS ====================

async def edit_task_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de opciones para editar una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Guardar ID de la tarea en el contexto
    context.user_data['edit_task_id'] = task_id
    
    message = f"""
✏️ <b>Editar Tarea</b>

<b>Tarea:</b> {task['title']}

¿Qué deseas editar?
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Título", callback_data=f"edit_task_field_title_{task_id}")],
        [InlineKeyboardButton("📄 Descripción", callback_data=f"edit_task_field_description_{task_id}")],
        [InlineKeyboardButton("⚡ Prioridad", callback_data=f"edit_task_field_priority_{task_id}")],
        [InlineKeyboardButton("📅 Fecha límite", callback_data=f"edit_task_field_deadline_{task_id}")],
        [InlineKeyboardButton(f"{config.EMOJI['back']} Volver", callback_data=f"task_view_{task_id}")]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def edit_task_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicita el nuevo valor para el campo a editar"""
    query = update.callback_query
    await query.answer()
    
    # Extraer el campo y el task_id
    # Formato: edit_task_field_title_123
    parts = query.data.split('_')
    field = parts[3]
    task_id = int(parts[4])
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text("❌ Tarea no encontrada")
        return ConversationHandler.END
    
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_task_field'] = field
    
    # Si es prioridad, mostrar opciones
    if field == "priority":
        message = f"""
✏️ <b>Editar Prioridad</b>

Tarea: <b>{task['title']}</b>
Prioridad actual: {config.PRIORITY_LEVELS.get(task['priority'], task['priority'])}

Selecciona la nueva prioridad:
"""
        keyboard = [
            [InlineKeyboardButton("🔴 Alta", callback_data="edit_priority_high")],
            [InlineKeyboardButton("🟡 Media", callback_data="edit_priority_medium")],
            [InlineKeyboardButton("🟢 Baja", callback_data="edit_priority_low")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"task_view_{task_id}")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_VALUE
    
    # Para otros campos, pedir texto
    field_names = {
        'title': 'título',
        'description': 'descripción',
        'deadline': 'fecha límite (YYYY-MM-DD)'
    }
    
    field_name = field_names.get(field, field)
    current_value = task.get(field, 'Sin valor')
    
    message = f"""
✏️ <b>Editar {field_name.capitalize()}</b>

Tarea: <b>{task['title']}</b>
{field_name.capitalize()} actual: <b>{current_value}</b>

Envía el nuevo valor:
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data=f"task_view_{task_id}")]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return EDIT_VALUE


async def edit_task_value_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nuevo valor y actualiza la tarea"""
    
    task_id = context.user_data.get('edit_task_id')
    field = context.user_data.get('edit_task_field')
    
    if not task_id or not field:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Error en la edición")
        else:
            await update.message.reply_text("❌ Error en la edición")
        return ConversationHandler.END
    
    # Si viene de callback (prioridad)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        new_value = query.data.split('_')[-1]  # edit_priority_high -> high
    else:
        new_value = update.message.text.strip()
    
    # Validar según el campo
    if field == 'title' and len(new_value) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres."
        )
        return EDIT_VALUE
    
    # Actualizar en la base de datos
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            UPDATE tasks 
            SET {field} = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_value, task_id))
        
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        success = False
    finally:
        conn.close()
    
    if success:
        message = f"""
✅ <b>Tarea actualizada</b>

El campo <b>{field}</b> ha sido actualizado correctamente.
"""
        keyboard = [[InlineKeyboardButton("👁️ Ver tarea", callback_data=f"task_view_{task_id}")]]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        error_msg = "❌ Error al actualizar la tarea"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
    
    # Limpiar contexto
    context.user_data.pop('edit_task_id', None)
    context.user_data.pop('edit_task_field', None)
    
    return ConversationHandler.END


# ==================== ELIMINACIÓN DE TAREAS ====================

async def delete_task_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicita confirmación antes de eliminar una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    subtasks = task_manager.get_subtasks(task_id)
    
    warning = ""
    if subtasks:
        warning = f"\n\n⚠️ <b>Atención:</b> Esta tarea tiene {len(subtasks)} subtarea(s). Al eliminarla, también se eliminarán todas sus subtareas."
    
    message = f"""
🗑️ <b>Confirmar Eliminación</b>

¿Estás seguro de que quieres eliminar esta tarea?

<b>Tarea:</b> {task['title']}
<b>Estado:</b> {config.TASK_STATUS.get(task['status'], task['status'])}
<b>Prioridad:</b> {config.PRIORITY_LEVELS.get(task['priority'], task['priority'])}{warning}

<b>⚠️ Esta acción no se puede deshacer.</b>
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Sí, eliminar",
                callback_data=f"task_delete_{task_id}"
            ),
            InlineKeyboardButton(
                "❌ No, cancelar",
                callback_data=f"task_view_{task_id}"
            )
        ]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def delete_task_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina la tarea después de la confirmación"""
    query = update.callback_query
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    task_title = task['title'] if task else "Tarea"
    
    success = task_manager.delete(task_id)
    
    if success:
        await query.answer(
            f"🗑️ Tarea '{task_title}' eliminada",
            show_alert=True
        )
        
        message = """
✅ <b>Tarea eliminada correctamente</b>

¿Qué quieres hacer ahora?
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
    else:
        await query.answer(
            "❌ Error al eliminar la tarea",
            show_alert=True
        )
        
        if task:
            await view_task(update, context)
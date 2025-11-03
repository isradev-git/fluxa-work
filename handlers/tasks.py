"""
Handler de tareas con personalidad Cortana
Gestiona la visualización, creación y modificación de tareas
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime, date, timedelta
import random

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
from cortana_personality import (
    CORTANA_TASK_MENU,
    CORTANA_TASK_COMPLETED,
    CORTANA_TASK_DELETED,
    CORTANA_TASK_POSTPONED,
    CORTANA_TASK_NO_RESULTS,
    CORTANA_SUBTASK_MENU,
    CORTANA_SUBTASK_CREATED,
    CORTANA_SUBTASK_NO_RESULTS,
    CORTANA_EDIT_MENU,
    CORTANA_EDIT_SUCCESS,
    CORTANA_DELETE_CONFIRM,
    CORTANA_CONFIRM_YES,
    CORTANA_ERROR_NOT_FOUND,
    CORTANA_ERROR_INVALID,
    CORTANA_MOTIVATION
)

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
    
    await query.edit_message_text(
        CORTANA_TASK_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_tasks_menu()
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista tareas según diferentes filtros"""
    query = update.callback_query
    await query.answer()
    
    filter_type = query.data.split('_')[-1]
    
    filters = {}
    title = ""
    
    if filter_type == "today":
        filters = {'today': True}
        title = "📅 <b>Objetivos de Hoy</b>"
    elif filter_type == "week":
        filters = {'deadline': (date.today(), date.today() + timedelta(days=7))}
        title = "📅 <b>Objetivos de Esta Semana</b>"
    elif filter_type == "overdue":
        filters = {'overdue': True}
        title = "⚠️ <b>Objetivos Atrasados</b>"
    elif filter_type == "high":
        filters = {'priority': 'high'}
        title = "🔴 <b>Objetivos de Alta Prioridad</b>"
    elif filter_type == "all":
        filters = {'parent_only': True}
        title = "📋 <b>Todos los Objetivos</b>"
    else:
        filters = {}
        title = "📋 <b>Objetivos</b>"
    
    tasks = task_manager.get_all(filters=filters)
    
    if not tasks:
        message = f"""{title}

{CORTANA_TASK_NO_RESULTS}
"""
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
        return
    
    completed = len([t for t in tasks if t['status'] == 'completed'])
    in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
    pending = len([t for t in tasks if t['status'] == 'pending'])
    
    message = f"""{title}

Total: {len(tasks)} objetivos
✅ Completados: {completed}
🔄 En progreso: {in_progress}
⏳ Pendientes: {pending}

Selecciona un objetivo para ver detalles:"""
    
    keyboard = get_task_list_keyboard(tasks, filter_type=filter_type, page=0)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los detalles de una tarea específica"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text(f"{CORTANA_ERROR_INVALID}")
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    project_name = None
    if task.get('project_id'):
        project = project_manager.get_by_id(task['project_id'])
        if project:
            project_name = project['name']
    
    message = format_task(task, include_project=True, project_name=project_name)
    
    subtasks = task_manager.get_subtasks(task_id)
    has_subtasks = len(subtasks) > 0
    
    if has_subtasks:
        completed_subtasks = len([s for s in subtasks if s['status'] == 'completed'])
        message += f"\n\n📋 Subobjetivos: {completed_subtasks}/{len(subtasks)} completados"
    
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
    
    parts = query.data.split('_')
    
    try:
        task_id = int(parts[2])
        new_status = parts[3]
    except (IndexError, ValueError):
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    success = task_manager.update_status(task_id, new_status)
    
    if success:
        status_messages = {
            'pending': "⏳ Objetivo marcado como pendiente",
            'in_progress': "🔄 Objetivo en progreso. Adelante, Spartan.",
            'completed': "✅ Objetivo completado"
        }
        
        await query.answer(
            status_messages.get(new_status, "✅ Estado actualizado"),
            show_alert=False
        )
        
        await view_task(update, context)
    else:
        await query.answer("❌ Error al actualizar estado", show_alert=True)


async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Marca una tarea como completada"""
    query = update.callback_query
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    success = task_manager.update_status(task_id, 'completed')
    
    if success:
        await query.answer(CORTANA_TASK_COMPLETED, show_alert=True)
        await view_task(update, context)
    else:
        await query.answer("❌ Error al completar objetivo", show_alert=True)


async def postpone_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pospone una tarea X días"""
    query = update.callback_query
    
    parts = query.data.split('_')
    
    try:
        task_id = int(parts[2])
        days = int(parts[3])
    except (IndexError, ValueError):
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task or not task.get('deadline'):
        await query.answer("❌ Este objetivo no tiene deadline", show_alert=True)
        return
    
    success = task_manager.postpone(task_id, days)
    
    if success:
        days_text = "día" if days == 1 else f"{days} días"
        await query.answer(
            f"📅 {CORTANA_TASK_POSTPONED}",
            show_alert=True
        )
        await view_task(update, context)
    else:
        await query.answer("❌ Error al posponer objetivo", show_alert=True)


# ==================== AGREGAR SUBTAREA ====================

async def add_subtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso para agregar una subtarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        parent_task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    context.user_data['parent_task_id'] = parent_task_id
    context.user_data['new_subtask'] = {}
    
    message = f"""
➕ <b>Nuevo Subobjetivo</b>

Objetivo principal: <b>{parent_task['title']}</b>

{CORTANA_SUBTASK_MENU}

<b>Paso 1/2:</b> ¿Título del subobjetivo?

Ejemplos:
• Diseñar mockups
• Escribir tests unitarios
• Revisar código
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
➕ <b>Nuevo Subobjetivo</b>

✅ Título: {title}

<b>Paso 2/2:</b> ¿Descripción? (opcional)

Envía la descripción o <code>-</code> para omitir.
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
✅ <b>Subobjetivo Registrado</b>

{CORTANA_SUBTASK_CREATED}

"{subtask_data['title']}" añadido a:
<b>{parent_task['title']}</b>
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Ver subobjetivos", callback_data=f"task_view_subtasks_{parent_task_id}")],
            [InlineKeyboardButton("🔙 Volver a objetivo", callback_data=f"task_view_{parent_task_id}")]
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
        error_message = f"❌ Error al crear el subobjetivo: {str(e)}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
    
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
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    subtasks = task_manager.get_subtasks(parent_task_id)
    
    if not subtasks:
        message = f"""
📋 <b>Subobjetivos</b>

Objetivo principal: <b>{parent_task['title']}</b>

{CORTANA_SUBTASK_NO_RESULTS}
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
📋 <b>Subobjetivos de: {parent_task['title']}</b>

Progreso: {completed}/{len(subtasks)} completados

<b>Lista de subobjetivos:</b>
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
        f"{config.EMOJI['back']} Volver a objetivo principal",
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
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    context.user_data['edit_task_id'] = task_id
    
    message = f"""
{CORTANA_EDIT_MENU}

<b>Objetivo:</b> {task['title']}

¿Qué parámetro modificamos?
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Título", callback_data=f"edit_task_field_title_{task_id}")],
        [InlineKeyboardButton("📄 Descripción", callback_data=f"edit_task_field_description_{task_id}")],
        [InlineKeyboardButton("⚡ Prioridad", callback_data=f"edit_task_field_priority_{task_id}")],
        [InlineKeyboardButton("📅 Deadline", callback_data=f"edit_task_field_deadline_{task_id}")],
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
    
    parts = query.data.split('_')
    field = parts[3]
    task_id = int(parts[4])
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(CORTANA_ERROR_NOT_FOUND)
        return ConversationHandler.END
    
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_task_field'] = field
    
    if field == "priority":
        message = f"""
✏️ <b>Editar Prioridad</b>

Objetivo: <b>{task['title']}</b>
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
    
    field_names = {
        'title': 'título',
        'description': 'descripción',
        'deadline': 'deadline (YYYY-MM-DD)'
    }
    
    field_name = field_names.get(field, field)
    current_value = task.get(field, 'Sin valor')
    
    message = f"""
✏️ <b>Editar {field_name.capitalize()}</b>

Objetivo: <b>{task['title']}</b>
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
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        new_value = query.data.split('_')[-1]
    else:
        new_value = update.message.text.strip()
    
    if field == 'title' and len(new_value) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres."
        )
        return EDIT_VALUE
    
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
        motivation = random.choice(CORTANA_MOTIVATION)
        message = f"""
{CORTANA_EDIT_SUCCESS}

{motivation}
"""
        keyboard = [[InlineKeyboardButton("👁️ Ver objetivo", callback_data=f"task_view_{task_id}")]]
        
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
        error_msg = "❌ Error al actualizar el objetivo"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
    
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
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    subtasks = task_manager.get_subtasks(task_id)
    
    warning = ""
    if subtasks:
        warning = f"\n\n⚠️ <b>Atención:</b> Este objetivo tiene {len(subtasks)} subobjetivo(s). Al eliminarlo, también se eliminarán todos sus subobjetivos."
    
    message = f"""
{CORTANA_DELETE_CONFIRM}

<b>Objetivo:</b> {task['title']}
<b>Estado:</b> {config.TASK_STATUS.get(task['status'], task['status'])}
<b>Prioridad:</b> {config.PRIORITY_LEVELS.get(task['priority'], task['priority'])}{warning}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirmar eliminación",
                callback_data=f"task_delete_{task_id}"
            ),
            InlineKeyboardButton(
                "❌ Cancelar",
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
        await query.answer(f"❌ {CORTANA_ERROR_INVALID}", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    task_title = task['title'] if task else "Objetivo"
    
    success = task_manager.delete(task_id)
    
    if success:
        await query.answer(
            f"🗑️ '{task_title}' eliminado del sistema",
            show_alert=True
        )
        
        message = f"""
{CORTANA_TASK_DELETED}
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
    else:
        await query.answer(
            "❌ Error al eliminar el objetivo",
            show_alert=True
        )
        
        if task:
            await view_task(update, context)
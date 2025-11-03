"""
Handler de tareas con personalidad Cortana
Gestiona la creación, visualización y edición de tareas
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import date, datetime, timedelta

import config
from database.models import DatabaseManager, Task
from utils.keyboards import (
    get_tasks_menu,
    get_task_list_keyboard,
    get_task_detail_keyboard
)
from utils.formatters import format_task, format_task_list
from cortana_personality import (
    CORTANA_TASK_MENU,
    CORTANA_TASK_CREATED,
    CORTANA_TASK_COMPLETED,
    CORTANA_TASK_POSTPONED,
    CORTANA_TASK_DELETED,
    CORTANA_NO_TASKS,
    CORTANA_TASK_NO_RESULTS,
    CORTANA_OVERDUE_WARNING,
    CORTANA_ERROR_NOT_FOUND
)

# Inicializar gestor de base de datos
db_manager = DatabaseManager()
task_manager = Task(db_manager)


async def show_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de tareas"""
    # Determinar si viene de mensaje o callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        is_callback = True
    else:
        is_callback = False
    
    if is_callback:
        await query.edit_message_text(
            CORTANA_TASK_MENU,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
    else:
        await update.message.reply_text(
            CORTANA_TASK_MENU,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista las tareas según el filtro solicitado"""
    query = update.callback_query
    await query.answer()
    
    callback_parts = query.data.split('_')
    
    if 'today' in callback_parts:
        filter_type = 'today'
        title = "📅 Objetivos de Hoy"
        tasks = task_manager.get_all({'today': True})
    elif 'week' in callback_parts:
        filter_type = 'week'
        title = "📅 Objetivos de esta Semana"
        today = date.today()
        week_end = today + timedelta(days=7)
        tasks = task_manager.get_all({
            'deadline_from': today.strftime("%Y-%m-%d"),
            'deadline_to': week_end.strftime("%Y-%m-%d")
        })
    elif 'overdue' in callback_parts:
        filter_type = 'overdue'
        title = "⚠️ Objetivos Atrasados"
        # CORRECCIÓN: Asegurarse de que el filtro 'overdue' funcione
        tasks = task_manager.get_all({'overdue': True, 'parent_only': True})
    elif 'high_priority' in callback_parts:
        filter_type = 'high_priority'
        title = "🔴 Objetivos de Alta Prioridad"
        # CORRECCIÓN: Añadir el filtro de prioridad alta
        tasks = task_manager.get_all({'priority': 'high', 'parent_only': True})
    else:  # 'all' o cualquier otro caso
        filter_type = 'all'
        title = "📋 Todos los Objetivos"
        tasks = task_manager.get_all({'parent_only': True})
    
    page = 0
    if 'page' in callback_parts:
        try:
            page = int(callback_parts[-1])
        except:
            page = 0
    
    if not tasks:
        message = f"{title}\n\n{CORTANA_TASK_NO_RESULTS}"
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
        return
    
    message = f"""{title}

Total: {len(tasks)} objetivos

Selecciona un objetivo para ver detalles:"""
    
    keyboard = get_task_list_keyboard(tasks, filter_type=filter_type, page=page)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los detalles completos de una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID de objetivo inválido")
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    # Obtener subtareas si existen
    subtasks = task_manager.get_all({'parent_task_id': task_id})
    has_subtasks = len(subtasks) > 0
    
    # Obtener nombre del proyecto si está asociado a uno
    project_name = None
    if task.get('project_id'):
        from database.models import Project
        project_manager = Project(db_manager)
        project = project_manager.get_by_id(task['project_id'])
        if project:
            project_name = project['name']
    
    message = format_task(task, include_project=True, project_name=project_name)
    
    keyboard = get_task_detail_keyboard(
        task_id, 
        task['status'],
        has_subtasks
    )
    
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
    
    # CORRECCIÓN: Manejar correctamente el callback_data "task_status_ID_estado"
    try:
        # El formato es "task_status_ID_estado"
        task_id = int(parts[2])
        new_status = parts[3]
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    success = task_manager.update_status(task_id, new_status)
    
    if success:
        status_messages = {
            'pending': "⏳ Objetivo marcado como pendiente",
            'in_progress': "🔄 Objetivo en progreso",
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
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.answer(f"❌ {CORTANA_ERROR_NOT_FOUND}", show_alert=True)
        return
    
    success = task_manager.update_status(task_id, 'completed')
    
    if success:
        await query.answer(
            CORTANA_TASK_COMPLETED,
            show_alert=True
        )
        
        await view_task(update, context)
    else:
        await query.answer("❌ Error al completar objetivo", show_alert=True)


async def postpone_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pospone una tarea"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    
    # CORRECCIÓN: Manejar correctamente el callback_data "task_postpone_ID_dias"
    try:
        task_id = int(parts[2])
        days = int(parts[3])
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.answer(f"❌ {CORTANA_ERROR_NOT_FOUND}", show_alert=True)
        return
    
    # Calcular nueva fecha límite
    if task.get('deadline'):
        try:
            current_deadline = datetime.strptime(task['deadline'], "%Y-%m-%d").date()
        except:
            current_deadline = date.today()
    else:
        current_deadline = date.today()
    
    new_deadline = current_deadline + timedelta(days=days)
    
    # CORRECCIÓN: Usar un método genérico de actualización si update_deadline no existe
    # Necesitaremos ver database/models.py para implementar esto correctamente
    try:
        # Intentar usar el método update_deadline si existe
        success = task_manager.update_deadline(task_id, new_deadline.strftime("%Y-%m-%d"))
    except AttributeError:
        # Si no existe, usar un método de actualización genérico
        success = task_manager.update(task_id, {'deadline': new_deadline.strftime("%Y-%m-%d")})
    
    if success:
        await query.answer(
            CORTANA_TASK_POSTPONED,
            show_alert=False
        )
        
        await view_task(update, context)
    else:
        await query.answer("❌ Error al posponer objetivo", show_alert=True)


async def view_subtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra las subtareas de una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID inválido")
        return
    
    subtasks = task_manager.get_all({'parent_task_id': task_id})
    
    if not subtasks:
        message = "📋 <b>Subobjetivos</b>\n\n❌ No hay subobjetivos registrados."
    else:
        lines = ["📋 <b>Subobjetivos</b>\n"]
        
        for i, subtask in enumerate(subtasks, 1):
            status = "✅" if subtask['status'] == 'completed' else "⏳"
            priority = "🔴" if subtask['priority'] == 'high' else "🟡" if subtask['priority'] == 'medium' else "🟢"
            lines.append(f"{i}. {status}{priority} {subtask['title']}")
        
        message = "\n".join(lines)
    
    keyboard = [
        [InlineKeyboardButton(
            f"➕ Añadir subobjetivo",
            callback_data=f"task_add_subtask_{task_id}"
        )],
        [InlineKeyboardButton(
            f"🔙 Volver a objetivo",
            callback_data=f"task_view_{task_id}"
        )]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def edit_task_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de edición de una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID inválido")
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    message = f"✏️ <b>Editar Objetivo</b>\n\n<b>{task['title']}</b>\n\n¿Qué campo quieres modificar?"
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Título", callback_data=f"edit_task_field_{task_id}_title"),
            InlineKeyboardButton("📄 Descripción", callback_data=f"edit_task_field_{task_id}_description")
        ],
        [
            InlineKeyboardButton("🎯 Prioridad", callback_data=f"edit_task_field_{task_id}_priority"),
            InlineKeyboardButton("📅 Deadline", callback_data=f"edit_task_field_{task_id}_deadline")
        ],
        [
            InlineKeyboardButton("🔙 Volver", callback_data=f"task_view_{task_id}")
        ]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def edit_task_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia la edición de un campo específico de la tarea"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    
    try:
        task_id = int(parts[2])
        field = parts[3]
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    # Guardar información para el siguiente paso
    context.user_data['edit_task'] = {
        'task_id': task_id,
        'field': field
    }
    
    field_messages = {
        'title': "Envía el nuevo título del objetivo:",
        'description': "Envía la nueva descripción (o '-' para dejar vacía):",
        'priority': "Selecciona la nueva prioridad:",
        'deadline': "Envía la nueva fecha límite (DD/MM/AAAA) o '-' para sin fecha:"
    }
    
    if field == 'priority':
        keyboard = [
            [InlineKeyboardButton("🔴 Alta", callback_data="edit_priority_high")],
            [InlineKeyboardButton("🟡 Media", callback_data="edit_priority_medium")],
            [InlineKeyboardButton("🟢 Baja", callback_data="edit_priority_low")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = None
    
    await query.edit_message_text(
        field_messages.get(field, "Envía el nuevo valor:"),
        reply_markup=reply_markup
    )
    
    return EDIT_VALUE


async def edit_task_value_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nuevo valor para el campo de la tarea"""
    task_data = context.user_data.get('edit_task', {})
    
    if not task_data:
        await update.message.reply_text("❌ Error: sesión de edición perdida")
        return ConversationHandler.END
    
    task_id = task_data['task_id']
    field = task_data['field']
    
    # Procesar el valor recibido
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if field == 'priority':
            new_value = query.data.split('_')[-1]
        else:
            new_value = None
    else:
        new_value = update.message.text
        query = None
    
    # Validar y actualizar
    success = False
    
    if field == 'title':
        if len(new_value) > config.MAX_TASK_NAME_LENGTH:
            await update.message.reply_text(
                f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres."
            )
            return EDIT_VALUE
        
        success = task_manager.update_title(task_id, new_value)
    
    elif field == 'description':
        if new_value == '-':
            new_value = ''
        
        success = task_manager.update_description(task_id, new_value)
    
    elif field == 'priority':
        success = task_manager.update_priority(task_id, new_value)
    
    elif field == 'deadline':
        if new_value == '-':
            success = task_manager.update_deadline(task_id, None)
        else:
            try:
                deadline_date = datetime.strptime(new_value, "%d/%m/%Y").date()
                success = task_manager.update_deadline(task_id, deadline_date.strftime("%Y-%m-%d"))
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha incorrecto. Usa DD/MM/AAAA (ejemplo: 25/12/2024)"
                )
                return EDIT_VALUE
    
    if success:
        message = f"✅ <b>Campo actualizado</b>\n\n{field.capitalize()}: {new_value}"
        
        if query:
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.HTML
            )
        
        # Limpiar datos temporales
        context.user_data.pop('edit_task', None)
        
        return ConversationHandler.END
    else:
        error_message = "❌ Error al actualizar el campo"
        
        if query:
            await query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
        
        return ConversationHandler.END


async def delete_task_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicita confirmación para eliminar una tarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID inválido")
        return
    
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_tasks_menu()
        )
        return
    
    message = f"🗑️ <b>Confirmar Eliminación</b>\n\n¿Estás seguro de que quieres eliminar este objetivo?\n\n<b>{task['title']}</b>\n\n⚠️ Esta acción no se puede deshacer."
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"task_delete_{task_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"task_view_{task_id}")
        ]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def delete_task_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina una tarea confirmada"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID inválido")
        return
    
    success = task_manager.delete(task_id)
    
    if success:
        await query.edit_message_text(
            CORTANA_TASK_DELETED,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
    else:
        await query.edit_message_text(
            "❌ Error al eliminar el objetivo",
            reply_markup=get_tasks_menu()
        )


async def add_subtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de añadir una subtarea"""
    query = update.callback_query
    await query.answer()
    
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID inválido")
        return
    
    # Guardar el ID de la tarea padre
    context.user_data['subtask'] = {
        'parent_task_id': task_id
    }
    
    message = "📋 <b>Nuevo Subobjetivo</b>\n\n¿Cuál es el título de este subobjetivo?"
    
    keyboard = [
        [InlineKeyboardButton("❌ Cancelar", callback_data=f"task_view_{task_id}")]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ADD_SUBTASK_TITLE


async def subtask_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el título de la subtarea"""
    title = update.message.text
    
    if len(title) > config.MAX_TASK_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El título es muy largo. Máximo {config.MAX_TASK_NAME_LENGTH} caracteres."
        )
        return ADD_SUBTASK_TITLE
    
    # Guardar título
    context.user_data['subtask']['title'] = title
    
    # Pedir descripción
    keyboard = [
        [InlineKeyboardButton("⏭️ Omitir", callback_data=f"subtask_skip_desc_{context.user_data['subtask']['parent_task_id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📝 <b>Descripción del Subobjetivo</b>\n\nAñade detalles o envía '-' para omitir:",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return ADD_SUBTASK_DESC


async def subtask_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la descripción de la subtarea y la crea"""
    subtask_data = context.user_data.get('subtask', {})
    
    if not subtask_data:
        await update.message.reply_text("❌ Error: sesión perdida")
        return ConversationHandler.END
    
    # Procesar descripción
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        description = ""
    else:
        description = update.message.text
        if description == "-":
            description = ""
    
    # Crear subtarea
    try:
        subtask_id = task_manager.create(
            title=subtask_data['title'],
            description=description,
            parent_task_id=subtask_data['parent_task_id'],
            priority='medium'  # Prioridad por defecto para subtareas
        )
        
        message = f"✅ <b>Subobjetivo añadido</b>\n\n{subtask_data['title']}"
        
        keyboard = [
            [InlineKeyboardButton("👁️ Ver subobjetivo", callback_data=f"task_view_{subtask_id}")],
            [InlineKeyboardButton("🔙 Volver a objetivo", callback_data=f"task_view_{subtask_data['parent_task_id']}")]
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
        error_message = f"❌ Error al crear subobjetivo: {str(e)}"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
    
    # Limpiar datos temporales
    context.user_data.pop('subtask', None)
    
    return ConversationHandler.END


# Constantes para los estados del ConversationHandler
ADD_SUBTASK_TITLE = 0
ADD_SUBTASK_DESC = 1
EDIT_FIELD = 2
EDIT_VALUE = 3
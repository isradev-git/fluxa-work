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

async def add_subtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú para agregar una subtarea.
    
    Callback format: task_add_subtask_123
    
    **¿Qué hace esta función?**
    - Se ejecuta cuando presionas el botón "➕ Agregar subtarea"
    - Extrae el ID de la tarea padre del botón presionado
    - Verifica que la tarea padre existe
    - Muestra un mensaje indicando cómo agregar subtareas
    
    **¿Por qué no crea la subtarea directamente?**
    Para crear tareas (incluyendo subtareas) necesitamos un ConversationHandler
    que haga un diálogo paso a paso. Por ahora, esta función solo informa al usuario.
    
    **Flujo**:
    1. Usuario presiona "➕ Agregar subtarea" en tarea con ID 123
    2. callback_data = "task_add_subtask_123"
    3. Esta función extrae el "123"
    4. Busca la tarea padre en la base de datos
    5. Muestra un mensaje con instrucciones
    """
    query = update.callback_query
    await query.answer()  # Confirma que recibimos el click del botón
    
    # Extraer el ID de la tarea padre del callback_data
    # Ejemplo: "task_add_subtask_123" → split('_') → ["task", "add", "subtask", "123"]
    # Tomamos el último elemento: "123" y lo convertimos a número
    try:
        parent_task_id = int(query.data.split('_')[-1])
    except ValueError:
        # Si no se puede convertir a número, mostrar error
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Verificar que la tarea padre existe en la base de datos
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Construir mensaje informativo
    message = f"""
➕ <b>Agregar Subtarea</b>

Tarea principal: <b>{parent_task['title']}</b>

<i>Nota: Esta funcionalidad aún no está completamente implementada.</i>

Para agregar subtareas por ahora, debes:
1. Crear una nueva tarea desde el menú principal
2. En la base de datos se asociará como subtarea

<i>En una próxima actualización podrás crear subtareas directamente desde aquí.</i>
"""
    
    # Crear botón para volver a la tarea padre
    keyboard = [[InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver",
        callback_data=f"task_view_{parent_task_id}"
    )]]
    
    # Mostrar mensaje
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def view_subtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra todas las subtareas de una tarea.
    
    Callback format: task_view_subtasks_123
    
    **¿Qué hace esta función?**
    - Se ejecuta cuando presionas "📋 Ver subtareas"
    - Obtiene todas las subtareas de la tarea padre
    - Muestra un resumen con el progreso (X/Y completadas)
    - Crea botones para ver cada subtarea
    
    **Explicación técnica**:
    - Las subtareas son tareas normales con un campo parent_task_id
    - El task_manager.get_subtasks(id) busca en la BD:
      SELECT * FROM tasks WHERE parent_task_id = ?
    
    **Flujo**:
    1. Usuario presiona "📋 Ver subtareas" en tarea ID 123
    2. callback_data = "task_view_subtasks_123"
    3. Esta función extrae el "123"
    4. Busca todas las tareas donde parent_task_id = 123
    5. Muestra lista con botones para cada subtarea
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID de la tarea padre
    try:
        parent_task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Obtener tarea padre de la base de datos
    parent_task = task_manager.get_by_id(parent_task_id)
    
    if not parent_task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Obtener todas las subtareas
    # get_subtasks busca en la BD: WHERE parent_task_id = parent_task_id
    subtasks = task_manager.get_subtasks(parent_task_id)
    
    # Si no hay subtareas, mostrar mensaje
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
    
    # Calcular cuántas subtareas están completadas
    # Usamos list comprehension para filtrar
    completed = len([s for s in subtasks if s['status'] == 'completed'])
    
    # Construir mensaje con el resumen
    message = f"""
📋 <b>Subtareas de: {parent_task['title']}</b>

Progreso: {completed}/{len(subtasks)} completadas

<b>Lista de subtareas:</b>
"""
    
    # Agregar cada subtarea al mensaje
    for i, subtask in enumerate(subtasks, 1):  # enumerate empieza en 1
        # Emoji según el estado de la subtarea
        if subtask['status'] == 'completed':
            status_emoji = "✅"
        elif subtask['status'] == 'in_progress':
            status_emoji = "🔄"
        else:
            status_emoji = "⏳"
        
        # Emoji según prioridad usando un diccionario
        priority_emoji = {
            'high': "🔴",
            'medium': "🟡",
            'low': "🟢"
        }.get(subtask['priority'], "⚪")  # ⚪ si no encuentra la prioridad
        
        # Agregar línea al mensaje
        message += f"\n{i}. {status_emoji}{priority_emoji} {subtask['title']}"
    
    # Crear botones para cada subtarea (máximo 10 para no saturar)
    keyboard = []
    for subtask in subtasks[:10]:  # Solo las primeras 10 subtareas
        # Truncar título si es muy largo (máximo 30 caracteres)
        title_short = subtask['title'][:30] + "..." if len(subtask['title']) > 30 else subtask['title']
        
        keyboard.append([InlineKeyboardButton(
            f"👁️ {title_short}",
            callback_data=f"task_view_{subtask['id']}"
        )])
    
    # Botón para volver a la tarea principal
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver a tarea principal",
        callback_data=f"task_view_{parent_task_id}"
    )])
    
    # Mostrar el mensaje con los botones
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================== EDICIÓN DE TAREAS ====================

async def edit_task_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de opciones para editar una tarea.
    
    Callback format: task_edit_123
    
    **¿Qué hace esta función?**
    - Se ejecuta cuando presionas "✏️ Editar"
    - Por ahora solo muestra un mensaje informativo
    - En el futuro, mostrará opciones como:
      • Editar título
      • Editar descripción
      • Cambiar prioridad
      • Cambiar fecha límite
      • Cambiar proyecto asociado
    
    **¿Por qué no edita directamente?**
    La edición completa requiere ConversationHandler para hacer diálogos.
    Por ejemplo, si quieres editar el título:
    1. Bot pregunta: "¿Nuevo título?"
    2. Usuario escribe el título
    3. Bot pregunta: "¿Confirmas el cambio?"
    4. Usuario confirma
    5. Bot actualiza en la BD
    
    Este flujo multi-paso necesita ConversationHandler, que es más complejo.
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID de la tarea
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Obtener tarea de la base de datos
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Mensaje informativo
    message = f"""
✏️ <b>Editar Tarea</b>

<b>Tarea:</b> {task['title']}

<i>Nota: La edición de tareas aún no está completamente implementada.</i>

Para editar una tarea por ahora, necesitas:
1. Marcarla como completada si ya terminó
2. Usar "Posponer" para cambiar la fecha
3. Para cambios mayores, crear una nueva tarea

<i>En una próxima actualización podrás editar todos los campos directamente.</i>
"""
    
    # Botón para volver
    keyboard = [[InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver",
        callback_data=f"task_view_{task_id}"
    )]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================== ELIMINACIÓN DE TAREAS ====================

async def delete_task_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Solicita confirmación antes de eliminar una tarea.
    
    Callback format: task_delete_confirm_123
    
    **¿Por qué pedir confirmación?**
    - Previene eliminaciones accidentales
    - Da al usuario la oportunidad de cancelar
    - Muestra información de la tarea para que sepa qué va a eliminar
    
    **Flujo de eliminación**:
    1. Usuario presiona "🗑️ Eliminar" → llama a esta función
    2. Esta función muestra confirmación
    3. Usuario presiona "✅ Sí, eliminar" → llama a delete_task_confirmed()
    4. delete_task_confirmed() ejecuta DELETE en la BD
    
    **¿Qué pasa con las subtareas?**
    Si la tarea tiene subtareas, también se eliminan (CASCADE).
    Por eso mostramos una advertencia especial.
    
    **Explicación del callback_data**:
    - "task_delete_confirm_123" → Esta función (confirmación)
    - "task_delete_123" → delete_task_confirmed() (eliminación real)
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID de la tarea
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Obtener tarea de la base de datos
    task = task_manager.get_by_id(task_id)
    
    if not task:
        await query.edit_message_text(
            "❌ Tarea no encontrada",
            reply_markup=get_tasks_menu()
        )
        return
    
    # Verificar si tiene subtareas
    subtasks = task_manager.get_subtasks(task_id)
    
    # Si tiene subtareas, agregar advertencia
    warning = ""
    if subtasks:
        warning = f"\n\n⚠️ <b>Atención:</b> Esta tarea tiene {len(subtasks)} subtarea(s). Al eliminarla, también se eliminarán todas sus subtareas."
    
    # Construir mensaje de confirmación
    message = f"""
🗑️ <b>Confirmar Eliminación</b>

¿Estás seguro de que quieres eliminar esta tarea?

<b>Tarea:</b> {task['title']}
<b>Estado:</b> {config.TASK_STATUS.get(task['status'], task['status'])}
<b>Prioridad:</b> {config.PRIORITY_LEVELS.get(task['priority'], task['priority'])}{warning}

<b>⚠️ Esta acción no se puede deshacer.</b>
"""
    
    # Botones de confirmación
    # - "Sí, eliminar" → task_delete_123 (sin "_confirm")
    # - "No, cancelar" → task_view_123 (vuelve a ver la tarea)
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
    """
    Elimina la tarea después de la confirmación.
    
    Callback format: task_delete_123 (sin "confirm")
    
    **¿Qué hace esta función?**
    - Solo se ejecuta DESPUÉS de que el usuario confirma
    - Llama a task_manager.delete(id) que ejecuta:
      DELETE FROM tasks WHERE id = ?
    - Si tiene subtareas, también se eliminan (ON DELETE CASCADE)
    - Muestra mensaje de éxito y vuelve al menú de tareas
    
    **Explicación técnica de la eliminación**:
    
    En database/models.py, el método delete() hace:
    ```python
    def delete(self, task_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Esta query elimina la tarea
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        # Como la tabla tiene ON DELETE CASCADE,
        # automáticamente elimina subtareas
        
        conn.commit()
        conn.close()
        return True
    ```
    
    **Flujo completo**:
    1. delete_task_confirm() muestra: "¿Seguro?"
    2. Usuario presiona "✅ Sí, eliminar"
    3. Esta función se ejecuta
    4. Llama a task_manager.delete(123)
    5. Se elimina de la BD
    6. Muestra mensaje de éxito
    7. Vuelve al menú de tareas
    """
    query = update.callback_query
    
    # Extraer ID de la tarea
    try:
        task_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Obtener título antes de eliminar (para el mensaje de confirmación)
    task = task_manager.get_by_id(task_id)
    task_title = task['title'] if task else "Tarea"
    
    # ELIMINAR TAREA DE LA BASE DE DATOS
    # Esto llama al método delete() de la clase Task
    success = task_manager.delete(task_id)
    
    if success:
        # Mostrar notificación emergente de éxito
        await query.answer(
            f"🗑️ Tarea '{task_title}' eliminada",
            show_alert=True  # Muestra un popup en lugar de una notificación pequeña
        )
        
        # Mensaje con confirmación
        message = """
✅ <b>Tarea eliminada correctamente</b>

¿Qué quieres hacer ahora?
"""
        
        # Mostrar el menú de tareas
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_tasks_menu()
        )
    else:
        # Si algo falló en la eliminación
        await query.answer(
            "❌ Error al eliminar la tarea",
            show_alert=True
        )
        
        # Si falla, volver a mostrar la tarea
        if task:
            await view_task(update, context)
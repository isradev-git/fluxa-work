"""
Conversation handlers para crear y editar proyectos con personalidad Cortana
Maneja diálogos multi-paso para crear nuevos proyectos
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime, date, timedelta
import random

import config
from database.models import DatabaseManager, Project
from utils.keyboards import get_projects_menu, get_priority_keyboard

# Mensajes de Cortana para proyectos
CORTANA_NEW_PROJECT_START = """📁 <b>Nueva Misión</b>

Vamos a registrar un nuevo proyecto en el sistema.

Primero necesito el nombre. ¿Cómo llamamos a esta misión?"""

CORTANA_NEW_PROJECT_DESCRIPTION = """📝 <b>Detalles de la Misión</b>

Bien. Ahora dame más contexto sobre este proyecto.

Escribe una descripción o envía "-" para omitir."""

CORTANA_NEW_PROJECT_PRIORITY = """🎯 <b>Nivel de Prioridad</b>

¿Qué tan crítica es esta misión? Selecciona la prioridad:"""

CORTANA_NEW_PROJECT_DEADLINE = """📅 <b>Fecha Objetivo</b>

¿Cuándo debe estar completada esta misión?

Formato: DD/MM/AAAA (ejemplo: 25/12/2024)
O envía "-" para sin fecha límite."""

CORTANA_NEW_PROJECT_CONFIRM = """📝 <b>Resumen de la Nueva Misión</b>

<b>Nombre:</b> {name}
<b>Descripción:</b> {description}
<b>Prioridad:</b> {priority}
<b>Fecha límite:</b> {deadline}

¿Confirmas? Quedará registrada en el sistema."""

CORTANA_PROJECT_CREATED = """✅ <b>Misión registrada</b>

Ya está en el sistema. Ahora puedes añadir objetivos específicos para maximizar la eficiencia."""

CORTANA_CREATION_CANCELLED = """❌ <b>Operación Cancelada</b>

No hay problema. A veces necesitamos replantear la estrategia.

¿Qué hacemos en su lugar?"""

CORTANA_MOTIVATION = [
    "💪 Los Spartans nunca se rinden. Tú tampoco.",
    "🎯 Enfócate en el objetivo. Los datos muestran que funciona.",
    "🚀 Un paso a la vez. Así se conquistan misiones imposibles.",
]

# Inicializar gestores
db_manager = DatabaseManager()
project_manager = Project(db_manager)

# Estados del ConversationHandler
(
    PROJECT_NAME,
    PROJECT_DESCRIPTION,
    PROJECT_PRIORITY,
    PROJECT_DEADLINE,
    PROJECT_CONFIRM
) = range(5)


async def create_project_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de creación de proyecto"""
    query = update.callback_query
    await query.answer()
    
    # Inicializar diccionario para guardar datos del proyecto
    context.user_data['new_project'] = {}
    
    # Botón de cancelar
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="project_create_cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        CORTANA_NEW_PROJECT_START,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return PROJECT_NAME


async def project_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nombre del proyecto"""
    name = update.message.text
    
    # Validar longitud del nombre
    if len(name) > config.MAX_PROJECT_NAME_LENGTH:
        await update.message.reply_text(
            f"❌ El nombre es muy largo. Máximo {config.MAX_PROJECT_NAME_LENGTH} caracteres."
        )
        return PROJECT_NAME
    
    # Guardar nombre
    context.user_data['new_project']['name'] = name
    
    # Pedir descripción
    keyboard = [[InlineKeyboardButton("➡️ Omitir", callback_data="project_skip_desc")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        CORTANA_NEW_PROJECT_DESCRIPTION,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return PROJECT_DESCRIPTION


async def project_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la descripción del proyecto"""
    
    # Puede venir de mensaje de texto o botón "Omitir"
    if update.callback_query:
        # Usuario presionó "Omitir"
        description = ""
        await update.callback_query.answer()
        query = update.callback_query
    else:
        # Usuario escribió descripción
        description = update.message.text
        if description == "-":
            description = ""
        query = None
    
    # Guardar descripción
    context.user_data['new_project']['description'] = description
    
    # Pedir prioridad
    keyboard = get_priority_keyboard()
    
    if query:
        await query.edit_message_text(
            CORTANA_NEW_PROJECT_PRIORITY,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            CORTANA_NEW_PROJECT_PRIORITY,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    return PROJECT_PRIORITY


async def project_priority_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la prioridad del proyecto"""
    query = update.callback_query
    await query.answer()
    
    # Extraer prioridad del callback_data: "priority_high" -> "high"
    priority = query.data.split('_')[-1]
    
    # Guardar prioridad
    context.user_data['new_project']['priority'] = priority
    
    # Pedir fecha límite
    keyboard = [[InlineKeyboardButton("➡️ Sin fecha", callback_data="project_skip_deadline")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        CORTANA_NEW_PROJECT_DEADLINE,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return PROJECT_DEADLINE


async def project_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la fecha límite del proyecto"""
    
    deadline = None
    
    # Puede venir de mensaje de texto o botón "Sin fecha"
    if update.callback_query:
        # Usuario presionó "Sin fecha"
        await update.callback_query.answer()
        query = update.callback_query
    else:
        # Usuario escribió fecha
        deadline_text = update.message.text
        query = None
        
        if deadline_text != "-":
            try:
                # Intentar parsear la fecha en formato DD/MM/AAAA
                deadline_date = datetime.strptime(deadline_text, "%d/%m/%Y").date()
                deadline = deadline_date.strftime("%Y-%m-%d")
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha incorrecto. Usa DD/MM/AAAA (ejemplo: 25/12/2024)\n"
                    "O envía '-' para omitir."
                )
                return PROJECT_DEADLINE
    
    # Guardar deadline
    context.user_data['new_project']['deadline'] = deadline
    
    # Mostrar resumen y pedir confirmación
    project_data = context.user_data['new_project']
    
    # Formatear datos para mostrar
    priority_names = {
        'high': '🔴 Alta',
        'medium': '🟡 Media',
        'low': '🟢 Baja'
    }
    
    deadline_display = deadline if deadline else "Sin fecha límite"
    if deadline:
        try:
            deadline_obj = datetime.strptime(deadline, "%Y-%m-%d")
            deadline_display = deadline_obj.strftime("%d/%m/%Y")
        except:
            pass
    
    message = CORTANA_NEW_PROJECT_CONFIRM.format(
        name=project_data['name'],
        description=project_data.get('description', 'Sin descripción') or 'Sin descripción',
        priority=priority_names.get(project_data['priority'], project_data['priority']),
        deadline=deadline_display
    )
    
    # Botones de confirmación
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="project_confirm_yes"),
            InlineKeyboardButton("❌ Cancelar", callback_data="project_create_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
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
    
    return PROJECT_CONFIRM


async def project_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma y crea el proyecto en la base de datos"""
    query = update.callback_query
    await query.answer()
    
    project_data = context.user_data.get('new_project', {})
    
    try:
        # Crear proyecto en la base de datos
        project_id = project_manager.create(
            name=project_data['name'],
            description=project_data.get('description', ''),
            priority=project_data.get('priority', 'medium'),
            deadline=project_data.get('deadline')
        )
        
        # Mensaje de éxito con motivación
        motivation = random.choice(CORTANA_MOTIVATION)
        
        message = f"""
{CORTANA_PROJECT_CREATED}

<b>Misión:</b> {project_data['name']}

{motivation}
"""
        
        # Botones para ver el proyecto o ver todos
        keyboard = [
            [InlineKeyboardButton("👁️ Ver misión", callback_data=f"project_view_{project_id}")],
            [InlineKeyboardButton("📁 Ver todas las misiones", callback_data="project_list_active")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        message = f"❌ Error del sistema al crear la misión: {str(e)}"
        await query.edit_message_text(message)
    
    # Limpiar datos temporales
    context.user_data.pop('new_project', None)
    
    return ConversationHandler.END


async def project_creation_cancelled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la creación del proyecto"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        CORTANA_CREATION_CANCELLED,
        parse_mode=ParseMode.HTML,
        reply_markup=get_projects_menu()
    )
    
    # Limpiar datos temporales
    context.user_data.pop('new_project', None)
    
    return ConversationHandler.END
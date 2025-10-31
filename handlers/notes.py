"""
Handler de notas
Gestiona la creación, visualización y edición de notas
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import config
from database.models import DatabaseManager, Note
from utils.keyboards import (
    get_notes_menu,
    get_note_list_keyboard,
    get_note_detail_keyboard
)
from utils.formatters import format_note

# Inicializar gestores
db_manager = DatabaseManager()
note_manager = Note(db_manager)


async def show_notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de notas.
    Puede ser llamado desde mensaje o desde callback.
    """
    # Determinar si viene de mensaje o callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        is_callback = True
    else:
        is_callback = False
    
    message = """
📝 <b>Gestión de Notas</b>

Guarda tus ideas, fragmentos de código y documentación.

Puedes organizar tus notas con etiquetas y asociarlas a proyectos o tareas.

¿Qué quieres hacer?
"""
    
    if is_callback:
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_notes_menu()
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_notes_menu()
        )


async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todas las notas con paginación"""
    query = update.callback_query
    await query.answer()
    
    # Determinar página
    callback_parts = query.data.split('_')
    page = 0
    if 'page' in callback_parts:
        try:
            page = int(callback_parts[-1])
        except:
            page = 0
    
    # Obtener notas
    notes = note_manager.get_all()
    
    if not notes:
        message = "📝 <b>Notas</b>\n\n❌ No tienes notas guardadas aún."
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_notes_menu()
        )
        return
    
    message = f"📝 <b>Notas</b>\n\nTotal: {len(notes)} notas\n\nSelecciona una nota para ver su contenido:"
    
    keyboard = get_note_list_keyboard(notes, page=page)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra una nota específica"""
    query = update.callback_query
    await query.answer()
    
    # Extraer ID de la nota
    try:
        note_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID de nota inválido")
        return
    
    # Obtener nota
    note = note_manager.get_by_id(note_id)
    
    if not note:
        await query.edit_message_text(
            "❌ Nota no encontrada",
            reply_markup=get_notes_menu()
        )
        return
    
    # Formatear mensaje
    message = format_note(note)
    
    # Crear teclado
    keyboard = get_note_detail_keyboard(note_id)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


# NOTA: Para crear, editar y eliminar notas se necesitaría implementar
# ConversationHandler que maneja diálogos multi-paso.
# Por simplicidad, esta versión inicial solo incluye visualización.
# En una versión completa, agregarías:
# - create_note_start() → Inicia diálogo de creación
# - create_note_title() → Pide título
# - create_note_content() → Pide contenido
# - create_note_tags() → Pide etiquetas
# - create_note_finish() → Guarda en base de datos

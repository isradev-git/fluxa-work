"""
Handler de proyectos
Gestiona la creación, visualización y edición de proyectos
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import config
from database.models import DatabaseManager, Project
from utils.keyboards import (
    get_projects_menu,
    get_project_list_keyboard,
    get_project_detail_keyboard
)
from utils.formatters import format_project, format_project_with_progress

# Inicializar gestor de base de datos
db_manager = DatabaseManager()
project_manager = Project(db_manager)


async def show_projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de proyectos (desde callback de botón).
    
    Args:
        update: Actualización desde un callback query (botón presionado)
        context: Contexto de la conversación
    """
    query = update.callback_query
    await query.answer()
    
    message = """
📁 <b>Gestión de Proyectos</b>

Desde aquí puedes crear y gestionar tus proyectos de desarrollo.

Cada proyecto puede tener tareas asociadas y un seguimiento de progreso.

¿Qué quieres hacer?
"""
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_projects_menu()
    )


async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lista los proyectos según el filtro solicitado.
    
    Esta función se activa cuando presionas botones como:
    - "Ver proyectos activos"
    - "Proyectos finalizados"
    - Botones de paginación
    
    El callback_data del botón tiene el formato:
    - "project_list_active" → lista proyectos activos
    - "project_list_completed" → lista proyectos completados
    - "project_list_page_1" → página 1 de proyectos
    
    Args:
        update: Actualización desde un callback query
        context: Contexto de la conversación
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer información del callback_data
    # callback_data tiene formato: project_list_[tipo] o project_list_page_[número]
    callback_parts = query.data.split('_')
    
    # Determinar el filtro
    if 'active' in callback_parts:
        status = 'active'
        title = "🟢 Proyectos Activos"
    elif 'completed' in callback_parts:
        status = 'completed'
        title = "✅ Proyectos Finalizados"
    elif 'paused' in callback_parts:
        status = 'paused'
        title = "⏸️ Proyectos Pausados"
    else:
        status = 'active'  # Por defecto
        title = "📁 Proyectos"
    
    # Determinar página (para paginación)
    page = 0
    if 'page' in callback_parts:
        try:
            page = int(callback_parts[-1])
        except:
            page = 0
    
    # Obtener proyectos de la base de datos
    projects = project_manager.get_all(status=status)
    
    # Construir mensaje
    if not projects:
        message = f"{title}\n\n❌ No hay proyectos en esta categoría."
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_projects_menu()
        )
        return
    
    message = f"{title}\n\nTotal: {len(projects)} proyectos\n\nSelecciona un proyecto para ver detalles:"
    
    # Crear teclado con lista de proyectos
    keyboard = get_project_list_keyboard(projects, page=page)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra los detalles de un proyecto específico.
    
    Se activa cuando presionas un proyecto de la lista.
    El callback_data tiene formato: "project_view_123" donde 123 es el ID del proyecto.
    
    Args:
        update: Actualización desde un callback query
        context: Contexto de la conversación
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID del proyecto del callback_data
    # Formato: "project_view_123"
    try:
        project_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID de proyecto inválido")
        return
    
    # Obtener proyecto de la base de datos
    project = project_manager.get_by_id(project_id)
    
    if not project:
        await query.edit_message_text(
            "❌ Proyecto no encontrado",
            reply_markup=get_projects_menu()
        )
        return
    
    # Obtener progreso del proyecto
    progress = project_manager.get_progress(project_id)
    
    # Formatear mensaje con proyecto y progreso
    message = format_project_with_progress(project, progress)
    
    # Crear teclado con acciones del proyecto
    keyboard = get_project_detail_keyboard(project_id, project['status'])
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def change_project_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cambia el estado de un proyecto.
    
    Se activa cuando presionas botones como:
    - "▶️ Activar"
    - "⏸️ Pausar"
    - "🔄 Reabrir proyecto"
    
    El callback_data tiene formato: "project_status_123_active"
    donde 123 es el ID y 'active' es el nuevo estado.
    
    Args:
        update: Actualización desde un callback query
        context: Contexto de la conversación
    """
    query = update.callback_query
    await query.answer()
    
    # Extraer ID y nuevo estado del callback_data
    # Formato: "project_status_123_active"
    parts = query.data.split('_')
    
    try:
        project_id = int(parts[2])
        new_status = parts[3]
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    # Actualizar estado en la base de datos
    success = project_manager.update_status(project_id, new_status)
    
    if success:
        # Mensajes según el nuevo estado
        status_messages = {
            'active': "🟢 Proyecto activado",
            'paused': "⏸️ Proyecto pausado",
            'completed': "✅ Proyecto completado"
        }
        
        await query.answer(
            status_messages.get(new_status, "✅ Estado actualizado"),
            show_alert=False
        )
        
        # Volver a mostrar el proyecto actualizado
        await view_project(update, context)
    else:
        await query.answer("❌ Error al actualizar estado", show_alert=True)


async def complete_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Marca un proyecto como completado.
    
    Esta es una función especial que además de cambiar el estado,
    muestra un mensaje de felicitación.
    
    Se activa con el botón "✅ Marcar como completado".
    
    Args:
        update: Actualización desde un callback query
        context: Contexto de la conversación
    """
    query = update.callback_query
    
    # Extraer ID del proyecto
    try:
        project_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    # Obtener nombre del proyecto antes de completarlo
    project = project_manager.get_by_id(project_id)
    
    if not project:
        await query.answer("❌ Proyecto no encontrado", show_alert=True)
        return
    
    # Marcar como completado
    success = project_manager.update_status(project_id, 'completed')
    
    if success:
        # Mostrar mensaje de felicitación
        await query.answer(
            f"🎉 ¡Felicitaciones! Proyecto completado",
            show_alert=True
        )
        
        # Actualizar vista
        await view_project(update, context)
    else:
        await query.answer("❌ Error al completar proyecto", show_alert=True)


# NOTA: Para crear, editar y eliminar proyectos se necesitaría implementar
# ConversationHandler que maneja diálogos multi-paso.
# Por simplicidad, esta versión inicial solo incluye visualización y cambio de estado.
# En una versión completa, agregarías:
# - create_project_start() → Inicia diálogo de creación
# - create_project_name() → Pide nombre
# - create_project_client() → Pide cliente
# - create_project_deadline() → Pide fecha límite
# - create_project_finish() → Guarda en base de datos

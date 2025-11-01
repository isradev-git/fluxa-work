"""
Handler de proyectos con personalidad Cortana
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
from cortana_personality import (
    CORTANA_PROJECT_MENU,
    CORTANA_PROJECT_COMPLETED,
    CORTANA_PROJECT_NO_RESULTS,
    CORTANA_ERROR_NOT_FOUND
)

# Inicializar gestor de base de datos
db_manager = DatabaseManager()
project_manager = Project(db_manager)


async def show_projects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de proyectos (desde callback de botón)"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        CORTANA_PROJECT_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=get_projects_menu()
    )


async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista los proyectos según el filtro solicitado"""
    query = update.callback_query
    await query.answer()
    
    callback_parts = query.data.split('_')
    
    if 'active' in callback_parts:
        status = 'active'
        title = "🟢 Misiones Activas"
    elif 'completed' in callback_parts:
        status = 'completed'
        title = "✅ Misiones Completadas"
    elif 'paused' in callback_parts:
        status = 'paused'
        title = "⏸️ Misiones Pausadas"
    else:
        status = 'active'
        title = "📁 Misiones"
    
    page = 0
    if 'page' in callback_parts:
        try:
            page = int(callback_parts[-1])
        except:
            page = 0
    
    projects = project_manager.get_all(status=status)
    
    if not projects:
        message = f"{title}\n\n{CORTANA_PROJECT_NO_RESULTS}"
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_projects_menu()
        )
        return
    
    message = f"""{title}

Total: {len(projects)} misiones

Selecciona una misión para ver detalles:"""
    
    keyboard = get_project_list_keyboard(projects, status=status, page=page)
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def view_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los detalles completos de un proyecto"""
    query = update.callback_query
    await query.answer()
    
    try:
        project_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.edit_message_text("❌ Error: ID de misión inválido")
        return
    
    project = project_manager.get_by_id(project_id)
    
    if not project:
        await query.edit_message_text(
            CORTANA_ERROR_NOT_FOUND,
            reply_markup=get_projects_menu()
        )
        return
    
    progress = project_manager.get_progress(project_id)
    
    message = format_project_with_progress(project, progress)
    
    keyboard = get_project_detail_keyboard(
        project_id, 
        project['status'],
        progress['total_tasks']
    )
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def change_project_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cambia el estado de un proyecto"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    
    try:
        project_id = int(parts[2])
        new_status = parts[3]
    except (IndexError, ValueError):
        await query.answer("❌ Error en los datos", show_alert=True)
        return
    
    success = project_manager.update_status(project_id, new_status)
    
    if success:
        status_messages = {
            'active': "🟢 Misión reactivada. De vuelta al trabajo.",
            'paused': "⏸️ Misión pausada temporalmente.",
            'completed': "✅ Misión completada"
        }
        
        await query.answer(
            status_messages.get(new_status, "✅ Estado actualizado"),
            show_alert=False
        )
        
        await view_project(update, context)
    else:
        await query.answer("❌ Error al actualizar estado", show_alert=True)


async def complete_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Marca un proyecto como completado"""
    query = update.callback_query
    
    try:
        project_id = int(query.data.split('_')[-1])
    except ValueError:
        await query.answer("❌ Error: ID inválido", show_alert=True)
        return
    
    project = project_manager.get_by_id(project_id)
    
    if not project:
        await query.answer(f"❌ {CORTANA_ERROR_NOT_FOUND}", show_alert=True)
        return
    
    success = project_manager.update_status(project_id, 'completed')
    
    if success:
        await query.answer(
            CORTANA_PROJECT_COMPLETED,
            show_alert=True
        )
        
        await view_project(update, context)
    else:
        await query.answer("❌ Error al completar misión", show_alert=True)
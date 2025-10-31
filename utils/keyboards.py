"""
Utilidades para crear teclados y botones de Telegram
Este archivo contiene funciones para generar los menús interactivos del bot
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from typing import List, Dict, Any, Optional
import config

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Crea el teclado persistente del menú principal.
    Este teclado siempre está visible en la parte inferior del chat.
    
    Returns:
        ReplyKeyboardMarkup con el menú principal
    """
    keyboard = [
        [
            KeyboardButton(f"{config.EMOJI['project']} Proyectos"),
            KeyboardButton(f"{config.EMOJI['task']} Tareas")
        ],
        [
            KeyboardButton(f"{config.EMOJI['today']} Hoy"),
            KeyboardButton(f"{config.EMOJI['dashboard']} Dashboard")
        ],
        [
            KeyboardButton(f"{config.EMOJI['note']} Notas"),
            KeyboardButton(f"{config.EMOJI['settings']} Configuración")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Ajusta el tamaño de los botones
        one_time_keyboard=False  # El teclado siempre está visible
    )


def get_projects_menu() -> InlineKeyboardMarkup:
    """
    Crea el menú inline de proyectos.
    Estos botones aparecen dentro del mensaje del chat.
    
    Returns:
        InlineKeyboardMarkup con opciones de proyectos
    """
    keyboard = [
        [InlineKeyboardButton(
            f"{config.EMOJI['add']} Nuevo proyecto",
            callback_data="project_new"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['project']} Ver proyectos activos",
            callback_data="project_list_active"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['search']} Buscar proyecto",
            callback_data="project_search"
        )],
        [InlineKeyboardButton(
            f"📦 Proyectos finalizados",
            callback_data="project_list_completed"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver al menú",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_project_list_keyboard(projects: List[Dict[str, Any]], 
                              page: int = 0, 
                              items_per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Crea un teclado con lista de proyectos paginada.
    
    Args:
        projects: Lista de proyectos
        page: Página actual (para paginación)
        items_per_page: Cantidad de proyectos por página
        
    Returns:
        InlineKeyboardMarkup con la lista de proyectos
    """
    keyboard = []
    
    # Calcular rango de proyectos para esta página
    start = page * items_per_page
    end = start + items_per_page
    page_projects = projects[start:end]
    
    # Agregar botón para cada proyecto
    for project in page_projects:
        # Emoji según estado
        status_emoji = "🟢" if project['status'] == 'active' else "⏸️" if project['status'] == 'paused' else "✅"
        priority_emoji = "🔴" if project['priority'] == 'high' else "🟡" if project['priority'] == 'medium' else "🟢"
        
        button_text = f"{status_emoji}{priority_emoji} {project['name']}"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"project_view_{project['id']}"
        )])
    
    # Botones de navegación
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "⬅️ Anterior",
            callback_data=f"project_list_page_{page-1}"
        ))
    
    if end < len(projects):
        nav_buttons.append(InlineKeyboardButton(
            "Siguiente ➡️",
            callback_data=f"project_list_page_{page+1}"
        ))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Botón volver
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver",
        callback_data="menu_projects"
    )])
    
    return InlineKeyboardMarkup(keyboard)


def get_project_detail_keyboard(project_id: int, 
                                status: str) -> InlineKeyboardMarkup:
    """
    Crea el teclado de acciones para un proyecto específico.
    
    Args:
        project_id: ID del proyecto
        status: Estado actual del proyecto
        
    Returns:
        InlineKeyboardMarkup con acciones del proyecto
    """
    keyboard = []
    
    # Botón para agregar tarea al proyecto
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['add']} Nueva tarea",
        callback_data=f"task_new_for_project_{project_id}"
    )])
    
    # Botón para ver tareas del proyecto
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['task']} Ver tareas",
        callback_data=f"task_list_project_{project_id}"
    )])
    
    # Botón para ver progreso
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['stats']} Ver progreso",
        callback_data=f"project_progress_{project_id}"
    )])
    
    # Botones de cambio de estado
    status_buttons = []
    if status != 'active':
        status_buttons.append(InlineKeyboardButton(
            "▶️ Activar",
            callback_data=f"project_status_{project_id}_active"
        ))
    
    if status != 'paused':
        status_buttons.append(InlineKeyboardButton(
            "⏸️ Pausar",
            callback_data=f"project_status_{project_id}_paused"
        ))
    
    if status_buttons:
        keyboard.append(status_buttons)
    
    # Botón para completar/reabrir
    if status != 'completed':
        keyboard.append([InlineKeyboardButton(
            "✅ Marcar como completado",
            callback_data=f"project_complete_{project_id}"
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            "🔄 Reabrir proyecto",
            callback_data=f"project_status_{project_id}_active"
        )])
    
    # Botones de edición y eliminación
    keyboard.append([
        InlineKeyboardButton(
            f"{config.EMOJI['edit']} Editar",
            callback_data=f"project_edit_{project_id}"
        ),
        InlineKeyboardButton(
            f"{config.EMOJI['delete']} Eliminar",
            callback_data=f"project_delete_confirm_{project_id}"
        )
    ])
    
    # Botón volver
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver a proyectos",
        callback_data="project_list_active"
    )])
    
    return InlineKeyboardMarkup(keyboard)


def get_tasks_menu() -> InlineKeyboardMarkup:
    """
    Crea el menú inline de tareas.
    
    Returns:
        InlineKeyboardMarkup con opciones de tareas
    """
    keyboard = [
        [InlineKeyboardButton(
            f"{config.EMOJI['add']} Nueva tarea",
            callback_data="task_new"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['today']} Tareas de hoy",
            callback_data="task_list_today"
        )],
        [InlineKeyboardButton(
            "📅 Esta semana",
            callback_data="task_list_week"
        )],
        [InlineKeyboardButton(
            "⚠️ Atrasadas",
            callback_data="task_list_overdue"
        )],
        [InlineKeyboardButton(
            "🔴 Alta prioridad",
            callback_data="task_list_high_priority"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['task']} Todas las tareas",
            callback_data="task_list_all"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver al menú",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_task_list_keyboard(tasks: List[Dict[str, Any]], 
                           filter_type: str = "all",
                           page: int = 0,
                           items_per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Crea un teclado con lista de tareas paginada.
    
    Args:
        tasks: Lista de tareas
        filter_type: Tipo de filtro aplicado (para callback)
        page: Página actual
        items_per_page: Cantidad de tareas por página
        
    Returns:
        InlineKeyboardMarkup con la lista de tareas
    """
    keyboard = []
    
    # Calcular rango de tareas para esta página
    start = page * items_per_page
    end = start + items_per_page
    page_tasks = tasks[start:end]
    
    # Agregar botón para cada tarea
    for task in page_tasks:
        # Emoji según estado
        if task['status'] == 'completed':
            status_emoji = "✅"
        elif task['status'] == 'in_progress':
            status_emoji = "🔄"
        else:
            status_emoji = "⏳"
        
        # Emoji de prioridad
        priority_emoji = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
        
        button_text = f"{status_emoji}{priority_emoji} {task['title']}"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"task_view_{task['id']}"
        )])
    
    # Botones de navegación
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "⬅️ Anterior",
            callback_data=f"task_list_{filter_type}_page_{page-1}"
        ))
    
    if end < len(tasks):
        nav_buttons.append(InlineKeyboardButton(
            "Siguiente ➡️",
            callback_data=f"task_list_{filter_type}_page_{page+1}"
        ))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Botón volver
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver",
        callback_data="menu_tasks"
    )])
    
    return InlineKeyboardMarkup(keyboard)


def get_task_detail_keyboard(task_id: int, 
                             status: str,
                             has_subtasks: bool = False) -> InlineKeyboardMarkup:
    """
    Crea el teclado de acciones para una tarea específica.
    
    Args:
        task_id: ID de la tarea
        status: Estado actual de la tarea
        has_subtasks: Si la tarea tiene subtareas
        
    Returns:
        InlineKeyboardMarkup con acciones de la tarea
    """
    keyboard = []
    
    # Botones de cambio de estado (solo si no está completada)
    if status != 'completed':
        status_row = []
        
        if status != 'in_progress':
            status_row.append(InlineKeyboardButton(
                "▶️ En progreso",
                callback_data=f"task_status_{task_id}_in_progress"
            ))
        
        status_row.append(InlineKeyboardButton(
            "✅ Completar",
            callback_data=f"task_complete_{task_id}"
        ))
        
        keyboard.append(status_row)
        
        # Botones para posponer
        keyboard.append([
            InlineKeyboardButton(
                "📅+1 día",
                callback_data=f"task_postpone_{task_id}_1"
            ),
            InlineKeyboardButton(
                "📅+2 días",
                callback_data=f"task_postpone_{task_id}_2"
            ),
            InlineKeyboardButton(
                "📅+1 semana",
                callback_data=f"task_postpone_{task_id}_7"
            )
        ])
    else:
        # Si está completada, permitir reabrir
        keyboard.append([InlineKeyboardButton(
            "🔄 Reabrir tarea",
            callback_data=f"task_status_{task_id}_pending"
        )])
    
    # Botón para agregar subtarea
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['add']} Agregar subtarea",
        callback_data=f"task_add_subtask_{task_id}"
    )])
    
    # Si tiene subtareas, botón para verlas
    if has_subtasks:
        keyboard.append([InlineKeyboardButton(
            "📋 Ver subtareas",
            callback_data=f"task_view_subtasks_{task_id}"
        )])
    
    # Botones de edición y eliminación
    keyboard.append([
        InlineKeyboardButton(
            f"{config.EMOJI['edit']} Editar",
            callback_data=f"task_edit_{task_id}"
        ),
        InlineKeyboardButton(
            f"{config.EMOJI['delete']} Eliminar",
            callback_data=f"task_delete_confirm_{task_id}"
        )
    ])
    
    # Botón volver
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver a tareas",
        callback_data="menu_tasks"
    )])
    
    return InlineKeyboardMarkup(keyboard)


def get_notes_menu() -> InlineKeyboardMarkup:
    """
    Crea el menú inline de notas.
    
    Returns:
        InlineKeyboardMarkup con opciones de notas
    """
    keyboard = [
        [InlineKeyboardButton(
            f"{config.EMOJI['add']} Nueva nota",
            callback_data="note_new"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['note']} Todas las notas",
            callback_data="note_list_all"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['search']} Buscar nota",
            callback_data="note_search"
        )],
        [InlineKeyboardButton(
            "🏷️ Ver por etiquetas",
            callback_data="note_list_tags"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver al menú",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_note_list_keyboard(notes: List[Dict[str, Any]], 
                           page: int = 0,
                           items_per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Crea un teclado con lista de notas paginada.
    
    Args:
        notes: Lista de notas
        page: Página actual
        items_per_page: Cantidad de notas por página
        
    Returns:
        InlineKeyboardMarkup con la lista de notas
    """
    keyboard = []
    
    # Calcular rango de notas para esta página
    start = page * items_per_page
    end = start + items_per_page
    page_notes = notes[start:end]
    
    # Agregar botón para cada nota
    for note in page_notes:
        # Mostrar etiquetas si existen
        tags_preview = f" [{note['tags'][:20]}...]" if note['tags'] else ""
        button_text = f"📝 {note['title'][:40]}{tags_preview}"
        
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"note_view_{note['id']}"
        )])
    
    # Botones de navegación
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "⬅️ Anterior",
            callback_data=f"note_list_page_{page-1}"
        ))
    
    if end < len(notes):
        nav_buttons.append(InlineKeyboardButton(
            "Siguiente ➡️",
            callback_data=f"note_list_page_{page+1}"
        ))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Botón volver
    keyboard.append([InlineKeyboardButton(
        f"{config.EMOJI['back']} Volver",
        callback_data="menu_notes"
    )])
    
    return InlineKeyboardMarkup(keyboard)


def get_note_detail_keyboard(note_id: int) -> InlineKeyboardMarkup:
    """
    Crea el teclado de acciones para una nota específica.
    
    Args:
        note_id: ID de la nota
        
    Returns:
        InlineKeyboardMarkup con acciones de la nota
    """
    keyboard = [
        [
            InlineKeyboardButton(
                f"{config.EMOJI['edit']} Editar",
                callback_data=f"note_edit_{note_id}"
            ),
            InlineKeyboardButton(
                f"{config.EMOJI['delete']} Eliminar",
                callback_data=f"note_delete_confirm_{note_id}"
            )
        ],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver a notas",
            callback_data="note_list_all"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_dashboard_menu() -> InlineKeyboardMarkup:
    """
    Crea el menú del dashboard con acceso a estadísticas.
    
    Returns:
        InlineKeyboardMarkup con opciones del dashboard
    """
    keyboard = [
        [InlineKeyboardButton(
            f"{config.EMOJI['stats']} Estadísticas semanales",
            callback_data="stats_weekly"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['stats']} Estadísticas mensuales",
            callback_data="stats_monthly"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['project']} Estado de proyectos",
            callback_data="dashboard_projects"
        )],
        [InlineKeyboardButton(
            "⏰ Próximas entregas",
            callback_data="dashboard_deadlines"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver al menú",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_settings_menu() -> InlineKeyboardMarkup:
    """
    Crea el menú de configuración.
    
    Returns:
        InlineKeyboardMarkup con opciones de configuración
    """
    keyboard = [
        [InlineKeyboardButton(
            "⏰ Hora del resumen diario",
            callback_data="settings_daily_time"
        )],
        [InlineKeyboardButton(
            "🔔 Recordatorios de tarde",
            callback_data="settings_evening_reminder"
        )],
        [InlineKeyboardButton(
            "🌍 Zona horaria",
            callback_data="settings_timezone"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['export']} Exportar datos",
            callback_data="settings_export"
        )],
        [InlineKeyboardButton(
            f"{config.EMOJI['back']} Volver al menú",
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """
    Crea un teclado de confirmación genérico.
    
    Args:
        action: Acción a confirmar (ej: "delete_project")
        item_id: ID del elemento
        
    Returns:
        InlineKeyboardMarkup con botones de confirmación
    """
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Sí, confirmar",
                callback_data=f"{action}_{item_id}_confirmed"
            ),
            InlineKeyboardButton(
                "❌ Cancelar",
                callback_data=f"{action}_{item_id}_cancelled"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """
    Crea un teclado para seleccionar prioridad.
    
    Returns:
        InlineKeyboardMarkup con opciones de prioridad
    """
    keyboard = [
        [InlineKeyboardButton("🔴 Alta", callback_data="priority_high")],
        [InlineKeyboardButton("🟡 Media", callback_data="priority_medium")],
        [InlineKeyboardButton("🟢 Baja", callback_data="priority_low")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Crea un simple teclado con botón de cancelar.
    Útil durante procesos de creación/edición.
    
    Returns:
        InlineKeyboardMarkup con botón de cancelar
    """
    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="cancel_operation")]]
    return InlineKeyboardMarkup(keyboard)

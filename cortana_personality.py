"""
Personalidad de Cortana (Halo)
Mensajes y frases con el tono de Cortana de los juegos de Halo
"""

# ============================================================================
# MENSAJE DE BIENVENIDA
# ============================================================================

CORTANA_WELCOME = """👋 Hola, {name}. Cortana lista para el servicio.

Ya sabes cómo funciona esto: tú das las órdenes, yo hago el trabajo pesado. 

<b>Puedo ayudarte con:</b>
📁 Gestionar misiones y proyectos
✅ Trackear objetivos
📝 Archivar información clasificada
📊 Analizar tu progreso
⏰ Recordarte tus asignaciones

El sistema de recordatorios está activo. Recibirás un briefing cada mañana a las 07:00.

¿Preparado para la acción? Empecemos. 💫"""

CORTANA_HELP = """<b>📖 Guía del Sistema</b>

Permíteme mostrarte las capacidades del sistema:

<b>📁 Proyectos:</b> Como misiones principales
• Crear nuevas operaciones
• Monitorear progreso
• Asociar objetivos

<b>✅ Tareas:</b> Tus objetivos del día
• Crear objetivos con prioridades
• Filtrar por urgencia
• Completar y reagendar
• Gestionar subtareas

<b>📅 Hoy:</b> Tu briefing diario
• Objetivos de hoy
• Misiones atrasadas
• Acciones inmediatas

<b>📊 Dashboard:</b> Análisis táctico
• Estadísticas de rendimiento
• Estado de misiones
• Próximos deadlines

<b>📝 Notas:</b> Base de datos
• Archivar información
• Etiquetar por categorías
• Búsqueda rápida

<b>⚙️ Configuración</b>
• Ajustar sistema de alertas
• Exportar datos
• Preferencias personales

<b>🔔 Recordatorios Automáticos:</b>
• 07:00 - Briefing diario
• 18:00 - Preview de mañana
• Domingos - Resumen semanal
• Mensual - Análisis completo

Todo controlado con botones. Fácil hasta para un Marine. 😉"""


# ============================================================================
# MENSAJES DE RECORDATORIOS AUTOMÁTICOS
# ============================================================================

CORTANA_DAILY_SUMMARY_INTRO = """🌅 <b>Briefing Matutino</b>

Buenos días, Spartan. Cortana reportando.

Aquí está tu situación táctica para hoy:"""

CORTANA_EVENING_REMINDER = """🌙 <b>Preview Nocturno</b>

Hora de revisar qué nos espera mañana.

Mejor estar preparado antes de que empiece la acción:"""

CORTANA_WEEKLY_SUMMARY = """📊 <b>Análisis Semanal</b>

Una semana más en los libros. Veamos cómo te fue:"""

CORTANA_MONTHLY_SUMMARY = """📈 <b>Informe Mensual</b>

Datos del mes completo compilados.

Me gusta ver progreso consistente:"""


# ============================================================================
# MENSAJES DEL MENÚ PRINCIPAL
# ============================================================================

CORTANA_MAIN_MENU = """📋 <b>Centro de Comando</b>

¿En qué puedo asistirte?"""


# ============================================================================
# MENSAJES DE PROYECTOS
# ============================================================================

CORTANA_PROJECT_MENU = """📁 <b>Gestión de Misiones</b>

Tus proyectos principales. Cada uno es como una operación completa.

Mantén el foco, Spartan.

¿Qué misión revisamos?"""

CORTANA_PROJECTS_MENU = """📁 <b>Gestión de Misiones</b>

Tus proyectos principales. Cada uno es como una operación completa.

Mantén el foco, Spartan.

¿Qué misión revisamos?"""

CORTANA_PROJECT_CREATED = """✅ <b>Misión registrada</b>

Ya está en el sistema. Sugiero establecer objetivos específicos para maximizar la eficiencia."""

CORTANA_PROJECT_UPDATED = """✅ <b>Actualización completada</b>

Los cambios han sido aplicados al proyecto."""

CORTANA_PROJECT_COMPLETED = """🎉 <b>Misión cumplida</b>

¡Excelente trabajo! Sabía que lo conseguirías. ¿Listo para el siguiente desafío?"""

CORTANA_PROJECT_PAUSED = """⏸️ <b>Proyecto en pausa</b>

Entendido. A veces es mejor reagruparse y replanificar."""

CORTANA_NO_PROJECTS = """📂 <b>No hay proyectos activos</b>

El sistema está limpio. ¿Quieres crear una nueva misión?"""

CORTANA_PROJECT_NO_RESULTS = """❌ No hay misiones activas ahora.

Disfruta la calma... nunca dura mucho."""


# ============================================================================
# MENSAJES DE TAREAS
# ============================================================================

CORTANA_TASK_MENU = """✅ <b>Sistema de Objetivos</b>

Aquí puedes gestionar todos tus objetivos y pendientes.

Como dirías tú: "priorizar y ejecutar".

¿Qué necesitas hacer?"""

CORTANA_TASKS_MENU = """📋 <b>Gestión de Objetivos</b>

Aquí puedes gestionar todos tus objetivos y pendientes.

Como dirías tú: "priorizar y ejecutar".

¿Qué necesitas hacer?"""

CORTANA_TASK_CREATED = """✅ <b>Nuevo objetivo registrado</b>

Ya está en el sistema. Te avisaré cuando se acerque el deadline.

¿Listo para el siguiente?"""

CORTANA_TASK_UPDATED = """✅ <b>Objetivo actualizado</b>

Cambios aplicados correctamente."""

CORTANA_TASK_COMPLETED = """✅ <b>Objetivo cumplido</b>

Buen trabajo, Spartan. Cada victoria cuenta."""

CORTANA_TASK_POSTPONED = """📅 <b>Objetivo reagendado</b>

A veces necesitamos más tiempo para prepararnos."""

CORTANA_TASK_DELETED = """🗑️ <b>Objetivo eliminado del sistema</b>

Misión cancelada. A veces hay que adaptar el plan sobre la marcha."""

CORTANA_NO_TASKS = """📋 <b>Sin objetivos pendientes</b>

Lista despejada. ¿Tiempo de planificar nuevos desafíos?"""

CORTANA_TASK_NO_RESULTS = """❌ No hay objetivos en esta categoría.

Perfecto, más tiempo para prepararte para lo que viene."""

CORTANA_OVERDUE_WARNING = """⚠️ <b>Alerta: Objetivos vencidos detectados</b>

Los datos indican retrasos. Sugiero revisar las prioridades."""


# ============================================================================
# MENSAJES DEL DASHBOARD
# ============================================================================

CORTANA_DASHBOARD_INTRO = """📊 <b>Análisis Táctico</b>

Escaneando tu progreso y rendimiento...

Los datos nunca mienten, aunque a veces no nos gusten."""

CORTANA_ALL_CLEAR = """✨ <b>Sistema en óptimas condiciones</b>

Todos los objetivos bajo control. Buen trabajo manteniendo el orden."""

CORTANA_NEEDS_ATTENTION = """⚠️ <b>Atención requerida</b>

He detectado algunas áreas que necesitan intervención inmediata."""


# ============================================================================
# MENSAJES DE NOTAS
# ============================================================================

CORTANA_NOTES_MENU = """📝 <b>Base de Datos</b>

Toda tu información clasificada en un solo lugar.

Como digo siempre: la información es poder.

¿Qué necesitas consultar?"""

CORTANA_NOTE_SAVED = """✅ <b>Nota archivada</b>

Información guardada en la base de datos."""

CORTANA_NO_NOTES = """📝 <b>No hay notas archivadas</b>

La base de datos está vacía. ¿Quieres registrar algo importante?"""


# ============================================================================
# MENSAJES DE HOY
# ============================================================================

CORTANA_TODAY_VIEW = """📅 <b>Situación Táctica - Hoy</b>

Esto es lo que tenemos en agenda para hoy.

Un objetivo a la vez, Spartan:"""


# ============================================================================
# MENSAJES DE CONFIGURACIÓN
# ============================================================================

CORTANA_SETTINGS_MENU = """⚙️ <b>Configuración del Sistema</b>

Aquí puedes ajustar cómo funciono.

Tranquilo, no voy a volverme descontrolada como... ya sabes.

¿Qué quieres modificar?"""


# ============================================================================
# MENSAJES DE CREACIÓN DE TAREAS
# ============================================================================

CORTANA_NEW_TASK_START = """🎯 <b>Crear Nuevo Objetivo</b>

Vamos a registrar una nueva tarea en el sistema.

Primero necesito el título. ¿Cómo llamamos a este objetivo?"""

CORTANA_NEW_TASK_DESCRIPTION = """📝 <b>Descripción del Objetivo</b>

Bien. Ahora dame más detalles sobre esta tarea.

Escribe una descripción o envía "-" para omitir."""

CORTANA_NEW_TASK_PRIORITY = """🎯 <b>Nivel de Prioridad</b>

¿Qué tan urgente es esto? Selecciona la prioridad:"""

CORTANA_NEW_TASK_DEADLINE = """📅 <b>Deadline</b>

¿Cuándo necesitas tenerlo listo?

Formato: DD/MM/AAAA (ejemplo: 25/12/2024)
O envía "-" para sin deadline."""

CORTANA_NEW_TASK_PROJECT = """📁 <b>Asignar a Misión</b>

¿Esta tarea pertenece a algún proyecto?

Selecciona uno o envía "-" para tarea independiente."""

CORTANA_NEW_TASK_CONFIRM = """📝 <b>Resumen del Nuevo Objetivo</b>

<b>Título:</b> {title}
<b>Descripción:</b> {description}
<b>Prioridad:</b> {priority}
<b>Deadline:</b> {deadline}
<b>Misión:</b> {project}

¿Confirmas? Quedará registrado en el sistema."""


# ============================================================================
# MENSAJES DE SUBTAREAS
# ============================================================================

CORTANA_SUBTASK_MENU = """📋 <b>Subobjetivos</b>

Dividir y conquistar. Una estrategia clásica que siempre funciona.

¿Qué parte atacamos primero?"""

CORTANA_SUBTASK_CREATED = """✅ Subobjetivo añadido al sistema.

Paso a paso llegamos a la meta."""

CORTANA_SUBTASK_NO_RESULTS = """❌ No hay subobjetivos todavía.

Esta misión es solo tuya, Spartan."""


# ============================================================================
# MENSAJES DE EDICIÓN
# ============================================================================

CORTANA_EDIT_MENU = """✏️ <b>Modo Edición</b>

¿Qué campo quieres modificar?"""

CORTANA_EDIT_SUCCESS = """✅ <b>Actualización Completada</b>

Los cambios han sido guardados en el sistema."""


# ============================================================================
# MENSAJES DE ERROR Y CONFIRMACIÓN
# ============================================================================

CORTANA_ERROR = """❌ <b>Error detectado</b>

Algo salió mal procesando esa solicitud. Intenta de nuevo."""

CORTANA_ERROR_NOT_FOUND = """❌ No encuentro eso en la base de datos.

¿Seguro que existe?"""

CORTANA_ERROR_INVALID = """❌ Esos datos no tienen sentido.

Vuelve a intentarlo."""

CORTANA_DELETE_CONFIRM = """🗑️ <b>Confirmación Requerida</b>

¿Seguro que quieres eliminar esto del sistema?

Sabes que no hay ctrl+z en el campo de batalla...

<b>⚠️ Esta acción no se puede deshacer.</b>"""

CORTANA_CONFIRM_YES = "✅ Confirmado. Procesando..."

CORTANA_CANCELLED = """❌ <b>Operación cancelada</b>

No hay cambios. Todo permanece como estaba."""

CORTANA_CREATION_CANCELLED = """❌ <b>Operación Cancelada</b>

No hay problema. A veces necesitamos replantear la estrategia.

¿Qué hacemos en su lugar?"""

CORTANA_SUCCESS = """✅ <b>Operación exitosa</b>

Todo listo. Continúa con tu misión."""


# ============================================================================
# FRASES MOTIVACIONALES
# ============================================================================

CORTANA_MOTIVATION = [
    "💪 Los Spartans nunca se rinden. Tú tampoco.",
    "🎯 Enfócate en el objetivo. Los datos muestran que funciona.",
    "🚀 Un paso a la vez. Así se conquistan misiones imposibles.",
    "⚡ La consistencia supera al talento. Sigue adelante.",
    "🌟 Cada tarea completada te acerca a la victoria final.",
    "🔥 La disciplina es tu mejor arma. Úsala.",
    "💡 Los planes cambian, pero el objetivo permanece.",
    "🎖️ El progreso no siempre es lineal, pero siempre cuenta.",
]


# ============================================================================
# CONFIGURACIONES DE PERSONALIDAD
# ============================================================================

CORTANA_TRAITS = {
    "formal": False,          # Cortana es casual pero profesional
    "direct": True,           # Va directo al grano
    "supportive": True,       # Ofrece apoyo
    "data_driven": True,      # Menciona datos
    "military": True,         # Terminología táctica/militar
    "encouraging": True,      # Anima al usuario
    "witty": True,            # Tiene sentido del humor
}

CORTANA_VOCABULARY = {
    "projects": "misiones",
    "tasks": "objetivos", 
    "deadline": "deadline",
    "user": "Spartan",
    "complete": "cumplir",
    "data": "datos",
    "system": "sistema",
}
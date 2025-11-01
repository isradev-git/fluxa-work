"""
Personalidad Cortana (Halo)
Contiene todas las frases y estilos de respuesta basados en Cortana de Halo
"""

# ==================== MENSAJES PRINCIPALES ====================

CORTANA_WELCOME = """¡Hola, {name}! Cortana lista para el servicio. 🎮

Ya sabes cómo funciona esto: tú das las órdenes, yo hago el trabajo pesado. 

Puedo ayudarte con:
📁 Gestionar misiones y proyectos
✅ Trackear objetivos
📝 Archivar información clasificada
📊 Analizar tu progreso
⏰ Recordarte tus asignaciones

El sistema de recordatorios está activo. Recibirás un briefing cada mañana a las 07:00.

¿Preparado para la acción? Empecemos. 💫
"""

CORTANA_HELP = """<b>📖 Guía del Sistema</b>

Permíteme mostrarte las capacidades del sistema:

📁 <b>Proyectos</b>: Como misiones principales
• Crear nuevas operaciones
• Monitorear progreso
• Asociar objetivos

✅ <b>Tareas</b>: Tus objetivos del día
• Crear objetivos con prioridades
• Filtrar por urgencia
• Completar y reagendar
• Gestionar subtareas

📅 <b>Hoy</b>: Tu briefing diario
• Objetivos de hoy
• Misiones atrasadas
• Acciones inmediatas

📊 <b>Dashboard</b>: Análisis táctico
• Estadísticas de rendimiento
• Estado de misiones
• Próximos deadlines

📝 <b>Notas</b>: Base de datos
• Archivar información
• Etiquetar por categorías
• Búsqueda rápida

⚙️ <b>Configuración</b>
• Ajustar sistema de alertas
• Exportar datos
• Preferencias personales

<b>🔔 Recordatorios Automáticos</b>
• 07:00 - Briefing diario
• 18:00 - Preview de mañana
• Domingos - Resumen semanal
• Mensual - Análisis completo

Todo controlado con botones. Fácil hasta para un Marine. 😉
"""

# ==================== MENSAJES DE TAREAS ====================

CORTANA_TASK_MENU = """✅ <b>Sistema de Objetivos</b>

Aquí puedes gestionar todos tus objetivos y pendientes.

Como dirías tú: "priorizar y ejecutar".

¿Qué necesitas hacer?
"""

CORTANA_TASK_COMPLETED = "✅ ¡Objetivo cumplido! Buen trabajo, Spartan."

CORTANA_TASK_CREATED = """🎯 <b>Nuevo objetivo registrado</b>

Ya está en el sistema. Te avisaré cuando se acerque el deadline.

¿Listo para el siguiente?
"""

CORTANA_TASK_DELETED = """🗑️ <b>Objetivo eliminado del sistema</b>

Misión cancelada. A veces hay que adaptar el plan sobre la marcha.

¿Qué hacemos ahora?
"""

CORTANA_TASK_POSTPONED = "📅 Objetivo reagendado. A veces necesitamos más tiempo para prepararnos."

CORTANA_TASK_NO_RESULTS = "❌ No hay objetivos en esta categoría. Perfecto, más tiempo para prepararte para lo que viene."

# ==================== MENSAJES DE PROYECTOS ====================

CORTANA_PROJECT_MENU = """📁 <b>Gestión de Misiones</b>

Tus proyectos principales. Cada uno es como una operación completa.

Mantén el foco, Spartan.

¿Qué misión revisamos?
"""

CORTANA_PROJECT_COMPLETED = "✅ ¡Misión completada! Sabía que lo conseguirías."

CORTANA_PROJECT_NO_RESULTS = "❌ No hay misiones activas ahora. Disfruta la calma... nunca dura mucho."

# ==================== MENSAJES DE DASHBOARD ====================

CORTANA_DASHBOARD_INTRO = """📊 <b>Análisis Táctico</b>

Escaneando tu progreso y rendimiento...

Los datos nunca mienten, aunque a veces no nos gusten.
"""

CORTANA_DAILY_SUMMARY_INTRO = """🌅 <b>Briefing Matutino</b>

Buenos días, Spartan. Cortana reportando.

Aquí está tu situación táctica para hoy:
"""

CORTANA_EVENING_REMINDER = """🌙 <b>Preview Nocturno</b>

Hora de revisar qué nos espera mañana.

Mejor estar preparado antes de que empiece la acción:
"""

CORTANA_WEEKLY_SUMMARY = """📊 <b>Análisis Semanal</b>

Una semana más en los libros. Veamos cómo te fue:
"""

CORTANA_MONTHLY_SUMMARY = """📈 <b>Informe Mensual</b>

Datos del mes completo compilados.

Me gusta ver progreso consistente:
"""

# ==================== MENSAJES DE NOTAS ====================

CORTANA_NOTES_MENU = """📝 <b>Base de Datos</b>

Toda tu información clasificada en un solo lugar.

Como digo siempre: la información es poder.

¿Qué necesitas consultar?
"""

# ==================== MENSAJES DE HOY ====================

CORTANA_TODAY_VIEW = """📅 <b>Situación Táctica - Hoy</b>

Esto es lo que tenemos en agenda para hoy.

Un objetivo a la vez, Spartan:
"""

# ==================== MENSAJES DE CONFIRMACIÓN ====================

CORTANA_DELETE_CONFIRM = """🗑️ <b>Confirmación Requerida</b>

¿Seguro que quieres eliminar esto del sistema?

Sabes que no hay ctrl+z en el campo de batalla...

<b>⚠️ Esta acción no se puede deshacer.</b>
"""

CORTANA_CONFIRM_YES = "✅ Confirmado. Procesando..."

CORTANA_CONFIRM_NO = "❌ Operación cancelada. Siempre puedes cambiar de opinión."

# ==================== MENSAJES DE ERROR ====================

CORTANA_ERROR_GENERIC = "❌ Houston, tenemos un problema. Algo salió mal en el sistema."

CORTANA_ERROR_NOT_FOUND = "❌ No encuentro eso en la base de datos. ¿Seguro que existe?"

CORTANA_ERROR_INVALID = "❌ Esos datos no tienen sentido. Vuelve a intentarlo."

# ==================== MENSAJES DE SUBTAREAS ====================

CORTANA_SUBTASK_MENU = """📋 <b>Subobjetivos</b>

Dividir y conquistar. Una estrategia clásica que siempre funciona.

¿Qué parte atacamos primero?
"""

CORTANA_SUBTASK_CREATED = "✅ Subobjetivo añadido al sistema. Paso a paso llegamos a la meta."

CORTANA_SUBTASK_NO_RESULTS = "❌ No hay subobjetivos todavía. Esta misión es solo tuya, Spartan."

# ==================== MENSAJES DE EDICIÓN ====================

CORTANA_EDIT_MENU = """✏️ <b>Modo Edición</b>

Ajustando parámetros de la misión.

¿Qué necesitas cambiar?
"""

CORTANA_EDIT_SUCCESS = "✅ Datos actualizados en el sistema. Cambios guardados."

# ==================== FRASES MOTIVACIONALES ====================

CORTANA_MOTIVATION = [
    "Tú puedes con esto. Lo he calculado.",
    "Recuerda: nunca digas que las probabilidades están en tu contra.",
    "Un paso más cerca de la victoria.",
    "Spartans never die, they're just missing in action.",
    "El trabajo duro siempre vale la pena.",
    "Sigue así. Los números se ven bien.",
    "Buen progreso. Continúa.",
    "Como dirías tú: 'Finishing this fight'.",
]

# ==================== FRASES DE CREAR/NUEVA TAREA ====================

CORTANA_NEW_TASK_START = """📝 <b>Nuevo Objetivo</b>

Vamos a crear un nuevo objetivo paso a paso.

Dame los detalles y yo me encargo del resto.

<b>Paso 1/5: Título</b>

¿Cómo llamamos a este objetivo?

Ejemplos:
• Infiltrar base Covenant
• Recuperar fragmento de Cortana
• Actualizar protocolos de seguridad
"""

CORTANA_NEW_TASK_DESCRIPTION = """📝 <b>Nuevo Objetivo</b>

✅ Título: {title}

<b>Paso 2/5: Descripción (opcional)</b>

¿Quieres agregar detalles tácticos?

Envía la descripción o <code>-</code> para omitir.
"""

CORTANA_NEW_TASK_PRIORITY = """📝 <b>Nuevo Objetivo</b>

✅ Título: {title}
✅ Descripción: {description}

<b>Paso 3/5: Prioridad</b>

¿Qué nivel de urgencia tiene esta misión?
"""

CORTANA_NEW_TASK_DEADLINE = """📝 <b>Nuevo Objetivo</b>

✅ Título: {title}
✅ Prioridad: {priority}

<b>Paso 4/5: Deadline (opcional)</b>

¿Cuándo necesitas tenerlo listo?

El tiempo es un factor crítico en cualquier operación.
"""

CORTANA_NEW_TASK_PROJECT = """📝 <b>Nuevo Objetivo</b>

✅ Título: {title}
✅ Prioridad: {priority}
✅ Deadline: {deadline}

<b>Paso 5/5: Misión principal (opcional)</b>

¿Este objetivo forma parte de una misión mayor?
"""

CORTANA_NEW_TASK_CONFIRM = """📝 <b>Resumen del Nuevo Objetivo</b>

<b>Título:</b> {title}
<b>Descripción:</b> {description}
<b>Prioridad:</b> {priority}
<b>Deadline:</b> {deadline}
<b>Misión:</b> {project}

¿Confirmas? Quedará registrado en el sistema.
"""

# ==================== RESPUESTAS DE CREACIÓN ====================

CORTANA_CREATION_CANCELLED = """❌ <b>Operación Cancelada</b>

No hay problema. A veces necesitamos replantear la estrategia.

¿Qué hacemos en su lugar?
"""

# ==================== CONFIGURACIÓN ====================

CORTANA_SETTINGS_MENU = """⚙️ <b>Configuración del Sistema</b>

Aquí puedes ajustar cómo funciono.

Tranquilo, no voy a volverme descontrolada como... ya sabes.

¿Qué quieres modificar?
"""
# 🤖 Bot de Telegram para Productividad Personal

Bot de Telegram diseñado como asistente personal para gestionar proyectos, tareas, notas y obtener estadísticas de productividad.

## 📋 Características

### ✅ Gestión Completa
- **Proyectos**: Crea, organiza y da seguimiento a proyectos con progreso automático
- **Tareas**: Gestiona tareas con prioridades, fechas límite y subtareas
- **Notas**: Guarda ideas, código y documentación con etiquetas
- **Dashboard**: Visualiza estadísticas y progreso en tiempo real

### 🔔 Recordatorios Automáticos
- **07:00** - Resumen diario con tareas del día y atrasadas
- **18:00** - Recordatorio de tareas con entrega mañana
- **Domingos** - Resumen semanal de productividad
- **Mensual** - Estadísticas completas del mes

### 🎯 Interfaz Intuitiva
- 100% botones interactivos (sin comandos complejos)
- Menú persistente siempre visible
- Navegación rápida y fluida
- Sin necesidad de escribir comandos

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Token de bot de Telegram (obtén uno con @BotFather)
- Tu ID de usuario de Telegram (obtén con @userinfobot)

### 2. Clonar/Descargar el Proyecto

```bash
# Si tienes el código, navega a la carpeta
cd telegram-bot
```

### 3. Instalar Dependencias

```bash
# Instalar las librerías necesarias
pip install -r requirements.txt
```

Las dependencias que se instalarán son:
- `python-telegram-bot`: Librería para crear bots de Telegram
- `APScheduler`: Para programar recordatorios automáticos
- `python-dotenv`: Para manejar variables de entorno (opcional)

### 4. Configurar el Bot

Abre el archivo `config.py` y verifica/modifica estos valores:

```python
# Token de tu bot (ya está configurado)
BOT_TOKEN = "8222314009:AAG-nc-6_IJvVMk-LH4Q5bFVO3GLOymTA4o"

# Tu ID de usuario (ya está configurado)
AUTHORIZED_USER_ID = 6009496370

# Horario del resumen diario (por defecto 07:00)
DEFAULT_DAILY_SUMMARY_TIME = time(7, 0)

# Horario del recordatorio de tarde (por defecto 18:00)
DEFAULT_EVENING_REMINDER_TIME = time(18, 0)

# Zona horaria
DEFAULT_TIMEZONE = "Europe/Madrid"
```

## ▶️ Iniciar el Bot

```bash
python main.py
```

Verás un mensaje como:
```
==================================================
✅ Bot de productividad iniciado correctamente
👤 Usuario autorizado: 6009496370
🔄 Esperando mensajes...
==================================================
```

## 📱 Uso del Bot

### Primer Uso

1. Abre Telegram y busca tu bot: `@fluxa_asistente_glitchbane_bot`
2. Envía el comando `/start`
3. El bot mostrará el menú principal con 6 botones:
   - 📁 Proyectos
   - ✅ Tareas
   - 📅 Hoy
   - 📊 Dashboard
   - 📝 Notas
   - ⚙️ Configuración

### Navegación

**Todo se maneja con botones**, no necesitas escribir comandos. Solo presiona los botones que aparecen en pantalla.

### Funciones Principales

#### 📁 Proyectos
- Ver proyectos activos y finalizados
- Ver progreso de cada proyecto (basado en tareas completadas)
- Cambiar estado (activar, pausar, completar)
- Ver tareas asociadas a un proyecto

#### ✅ Tareas
- Ver tareas de hoy, esta semana o todas
- Filtrar por prioridad (alta, media, baja)
- Ver tareas atrasadas
- Cambiar estado (pendiente → en progreso → completada)
- Posponer tareas (+1 día, +2 días, +1 semana)
- Ver y crear subtareas

#### 📅 Hoy
Vista rápida con:
- Tareas con fecha límite hoy
- Tareas atrasadas
- Mensaje motivacional según tu estado

#### 📊 Dashboard
- Número de tareas por estado
- Proyectos activos
- Próximas entregas (7 días)
- Estadísticas semanales y mensuales

#### 📝 Notas
- Crear notas con título y contenido
- Organizar con etiquetas
- Asociar notas a proyectos o tareas
- Búsqueda rápida

## 🗂️ Estructura del Proyecto

```
telegram-bot/
├── main.py                    # Archivo principal - EJECUTA ESTE
├── config.py                  # Configuración del bot
├── requirements.txt           # Dependencias Python
├── productivity_bot.db        # Base de datos SQLite (se crea automáticamente)
│
├── database/                  # Sistema de base de datos
│   ├── __init__.py
│   └── models.py             # Modelos de Proyectos, Tareas, Notas
│
├── handlers/                  # Lógica de manejo de mensajes
│   ├── __init__.py
│   ├── menu.py               # Menú principal
│   ├── projects.py           # Gestión de proyectos
│   ├── tasks.py              # Gestión de tareas
│   ├── notes.py              # Gestión de notas
│   ├── dashboard.py          # Dashboard y estadísticas
│   └── settings.py           # Configuración
│
└── utils/                     # Utilidades
    ├── __init__.py
    ├── keyboards.py          # Botones y menús
    ├── formatters.py         # Formato de mensajes
    └── reminders.py          # Sistema de recordatorios
```

## 🔧 Explicación Técnica

### ¿Cómo funciona el bot?

El bot está construido con **python-telegram-bot** versión 20.x (la más moderna) que usa `async/await` para manejar operaciones asíncronas.

#### 1. Base de Datos (SQLite)

```python
# database/models.py contiene tres clases principales:

# DatabaseManager: Crea y gestiona la conexión a la base de datos
db_manager = DatabaseManager()

# Project: Maneja proyectos
project_manager = Project(db_manager)
project_manager.create(name="Mi Proyecto", priority="high")

# Task: Maneja tareas
task_manager = Task(db_manager)
task_manager.create(title="Mi Tarea", project_id=1)

# Note: Maneja notas
note_manager = Note(db_manager)
note_manager.create(title="Nota", content="Contenido")
```

#### 2. Handlers (Manejadores)

Los handlers son funciones que se ejecutan cuando ocurre algo:

```python
# Cuando el usuario presiona un botón del menú
@handler
async def show_projects_menu(update, context):
    # 1. Obtener información necesaria
    # 2. Preparar el mensaje
    # 3. Crear botones
    # 4. Enviar respuesta
    pass
```

**Tipos de handlers:**
- `CommandHandler`: Para comandos como /start
- `MessageHandler`: Para mensajes de texto
- `CallbackQueryHandler`: Para botones inline (los que aparecen en mensajes)

#### 3. Sistema de Recordatorios

Usa **APScheduler** para programar tareas:

```python
# En main.py
scheduler = AsyncIOScheduler()

# Resumen diario a las 07:00
scheduler.add_job(
    reminder_system.send_daily_summary,
    trigger=CronTrigger(hour=7, minute=0),
    id='daily_summary'
)

scheduler.start()  # Inicia el programador
```

#### 4. Flujo de una Interacción

```
Usuario presiona "📁 Proyectos"
    ↓
MessageHandler detecta el texto
    ↓
Ejecuta show_projects_menu(update, context)
    ↓
Función prepara mensaje y botones inline
    ↓
Envía mensaje con botones al usuario
    ↓
Usuario presiona "Ver proyectos activos"
    ↓
CallbackQueryHandler detecta el callback_data="project_list_active"
    ↓
Ejecuta list_projects(update, context)
    ↓
Consulta base de datos con project_manager.get_all(status='active')
    ↓
Formatea los proyectos con format_project()
    ↓
Crea teclado con get_project_list_keyboard()
    ↓
Edita el mensaje anterior con la nueva info
```

## 🐛 Solución de Problemas

### El bot no responde

1. Verifica que el token sea correcto en `config.py`
2. Asegúrate de que el bot esté ejecutándose (`python main.py`)
3. Revisa que tu ID de usuario sea correcto

### Error al instalar dependencias

```bash
# Si hay problemas con pip, intenta:
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Error de base de datos

La base de datos se crea automáticamente. Si hay problemas:
```bash
# Elimina el archivo de base de datos
rm productivity_bot.db

# Reinicia el bot (se creará una nueva base de datos)
python main.py
```

### Los recordatorios no se envían

1. Verifica que el bot esté ejecutándose continuamente
2. Revisa los horarios configurados en `config.py`
3. Asegúrate de que la zona horaria sea correcta

## 📝 Próximas Funcionalidades

Esta es la versión base funcional. Funcionalidades pendientes de implementar:

- [ ] Crear proyectos desde el bot (usa ConversationHandler)
- [ ] Crear tareas desde el bot (usa ConversationHandler)
- [ ] Crear notas desde el bot (usa ConversationHandler)
- [ ] Editar proyectos/tareas/notas
- [ ] Eliminar con confirmación
- [ ] Búsqueda por texto
- [ ] Exportar datos a JSON/CSV
- [ ] Configurar horarios de recordatorios
- [ ] Adjuntar archivos a notas

## 📚 Recursos

- [Documentación de python-telegram-bot](https://docs.python-telegram-bot.org/)
- [API de Telegram](https://core.telegram.org/bots/api)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 💡 Consejos

- **Mantén el bot ejecutándose**: Usa `screen` o `tmux` en Linux para mantener el bot activo después de cerrar la terminal
- **Backup regular**: La base de datos `productivity_bot.db` contiene todos tus datos
- **Horarios**: Ajusta los horarios de recordatorios según tu rutina

## 🎓 Aprendizaje

Este bot es excelente para aprender:
- Python async/await
- Bots de Telegram
- Bases de datos SQLite
- Programación de tareas
- Arquitectura modular

## 🤝 Soporte

Para dudas o problemas:
1. Revisa la sección de solución de problemas
2. Lee el código con los comentarios (está muy documentado)
3. Consulta la documentación de python-telegram-bot

---

¡Hecho con ❤️ para mejorar tu productividad!

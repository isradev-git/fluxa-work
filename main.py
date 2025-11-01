"""
Bot de Telegram para productividad personal - Versión Cortana (Halo)
Punto de entrada principal de la aplicación

Este archivo inicializa el bot, configura los handlers (manejadores de mensajes y botones),
y arranca el sistema de recordatorios automáticos.
"""
import logging
from datetime import time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Importar configuración y componentes
import config
from database.models import DatabaseManager, Project, Task, Note
from utils.reminders import ReminderSystem
from utils.keyboards import get_main_keyboard
from utils.formatters import format_dashboard

# Importar personalidad de Cortana
from cortana_personality import CORTANA_WELCOME, CORTANA_HELP

# Importar handlers
from handlers import menu, projects, tasks, notes, dashboard, settings, task_conversations

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ProductivityBot:
    """
    Clase principal que gestiona el bot de productividad.
    Coordina la inicialización, handlers y recordatorios.
    Personalidad: Cortana de Halo
    """
    
    def __init__(self):
        """
        Inicializa el bot y todos sus componentes.
        """
        # Inicializar base de datos
        self.db_manager = DatabaseManager()
        logger.info("✅ Base de datos inicializada")
        
        # Inicializar gestores de datos
        self.project_manager = Project(self.db_manager)
        self.task_manager = Task(self.db_manager)
        self.note_manager = Note(self.db_manager)
        
        # Crear aplicación de Telegram
        self.app = Application.builder().token(config.BOT_TOKEN).build()
        
        # Sistema de recordatorios
        self.reminder_system = None
        self.scheduler = AsyncIOScheduler()
        
        logger.info("✅ Bot inicializado - Personalidad: Cortana")
    
    def setup_handlers(self):
        """
        Configura todos los handlers (manejadores) del bot.
        
        Los handlers procesan los mensajes del usuario y las interacciones con botones.
        Hay diferentes tipos:
        - CommandHandler: Para comandos como /start
        - MessageHandler: Para mensajes de texto
        - CallbackQueryHandler: Para cuando presionas un botón inline
        """
        
        # Handler para el comando /start
        self.app.add_handler(CommandHandler("start", self.start_command))
        
        # Handler para el comando /help
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Handlers para los botones del menú principal (teclado persistente)
        # Estos detectan cuando presionas los botones de abajo
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['project']} Proyectos$"),
            menu.show_projects_menu
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['task']} Tareas$"),
            menu.show_tasks_menu
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['today']} Hoy$"),
            menu.show_today
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['dashboard']} Dashboard$"),
            menu.show_dashboard
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['note']} Notas$"),
            menu.show_notes_menu
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['settings']} Configuración$"),
            menu.show_settings_menu
        ))
        
        # Handlers para botones inline (los que aparecen dentro de mensajes)
        # Estos se activan cuando presionas botones como "Ver proyectos", "Nueva tarea", etc.
        
        # Callbacks de navegación general
        self.app.add_handler(CallbackQueryHandler(
            menu.back_to_main,
            pattern="^back_to_main$"
        ))
        
        # Callbacks de proyectos (pattern es un patrón regex que identifica el botón)
        self.app.add_handler(CallbackQueryHandler(
            projects.show_projects_menu,
            pattern="^menu_projects$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            projects.list_projects,
            pattern="^project_list_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            projects.view_project,
            pattern="^project_view_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            projects.change_project_status,
            pattern="^project_status_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            projects.complete_project,
            pattern="^project_complete_"
        ))
        
        # Callbacks de tareas
        self.app.add_handler(CallbackQueryHandler(
            tasks.show_tasks_menu,
            pattern="^menu_tasks$"
        ))
        
        # ConversationHandler para crear nueva tarea
        task_creation_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    task_conversations.create_task_start, 
                    pattern="^task_new$"
                )
            ],
            states={
                task_conversations.TASK_TITLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, 
                        task_conversations.task_title_received
                    ),
                    CallbackQueryHandler(
                        task_conversations.task_creation_cancelled,
                        pattern="^task_create_cancel$"
                    )
                ],
                task_conversations.TASK_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, 
                        task_conversations.task_description_received
                    ),
                    CallbackQueryHandler(
                        task_conversations.task_description_received,
                        pattern="^task_skip_description$"
                    )
                ],
                task_conversations.TASK_PRIORITY: [
                    CallbackQueryHandler(
                        task_conversations.task_priority_received,
                        pattern="^task_priority_"
                    )
                ],
                task_conversations.TASK_DEADLINE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        task_conversations.task_deadline_received
                    ),
                    CallbackQueryHandler(
                        task_conversations.task_deadline_received,
                        pattern="^task_deadline_"
                    )
                ],
                task_conversations.TASK_PROJECT: [
                    CallbackQueryHandler(
                        task_conversations.task_project_received,
                        pattern="^task_project_"
                    )
                ],
                task_conversations.TASK_CONFIRM: [
                    CallbackQueryHandler(
                        task_conversations.task_confirmed,
                        pattern="^task_confirm_yes$"
                    ),
                    CallbackQueryHandler(
                        task_conversations.task_creation_cancelled,
                        pattern="^task_confirm_no$"
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    task_conversations.task_creation_cancelled,
                    pattern="^task_create_cancel$"
                )
            ],
            allow_reentry=True,
            name="task_creation",
            persistent=False
        )
        
        self.app.add_handler(task_creation_handler)
        
        # ConversationHandler para agregar subtarea
        subtask_creation_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    tasks.add_subtask, 
                    pattern="^task_add_subtask_"
                )
            ],
            states={
                tasks.ADD_SUBTASK_TITLE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, 
                        tasks.subtask_title_received
                    )
                ],
                tasks.ADD_SUBTASK_DESC: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        tasks.subtask_description_received
                    ),
                    CallbackQueryHandler(
                        tasks.subtask_description_received,
                        pattern="^subtask_skip_desc_"
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    tasks.view_task,
                    pattern="^task_view_"
                )
            ],
            allow_reentry=True,
            name="subtask_creation",
            persistent=False
        )
        
        self.app.add_handler(subtask_creation_handler)
        
        # ConversationHandler para editar tarea
        task_edit_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    tasks.edit_task_field, 
                    pattern="^edit_task_field_"
                )
            ],
            states={
                tasks.EDIT_VALUE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        tasks.edit_task_value_received
                    ),
                    CallbackQueryHandler(
                        tasks.edit_task_value_received,
                        pattern="^edit_priority_"
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    tasks.view_task,
                    pattern="^task_view_"
                )
            ],
            allow_reentry=True,
            name="task_edit",
            persistent=False
        )
        
        self.app.add_handler(task_edit_handler)
        
        # Handlers para listar y ver tareas
        self.app.add_handler(CallbackQueryHandler(
            tasks.list_tasks,
            pattern="^task_list_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.view_task,
            pattern="^task_view_"
        ))
        
        # Handlers para cambiar estado de tareas
        self.app.add_handler(CallbackQueryHandler(
            tasks.change_task_status,
            pattern="^task_status_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.complete_task,
            pattern="^task_complete_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.postpone_task,
            pattern="^task_postpone_"
        ))
        
        # ========== HANDLERS PARA FUNCIONALIDADES NUEVAS ==========
        
        # Handler para ver subtareas
        self.app.add_handler(CallbackQueryHandler(
            tasks.view_subtasks,
            pattern="^task_view_subtasks_"
        ))
        
        # Handler para el menú de edición de tarea
        self.app.add_handler(CallbackQueryHandler(
            tasks.edit_task_menu,
            pattern="^task_edit_"
        ))
        
        # Handler para solicitar confirmación de eliminación
        self.app.add_handler(CallbackQueryHandler(
            tasks.delete_task_confirm,
            pattern="^task_delete_confirm_"
        ))
        
        # Handler para eliminar después de confirmar
        self.app.add_handler(CallbackQueryHandler(
            tasks.delete_task_confirmed,
            pattern="^task_delete_(?!confirm)"
        ))
        
        # ========== FIN DE HANDLERS NUEVOS ==========
        
        # Callbacks de notas
        self.app.add_handler(CallbackQueryHandler(
            notes.show_notes_menu,
            pattern="^menu_notes$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            notes.list_notes,
            pattern="^note_list_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            notes.view_note,
            pattern="^note_view_"
        ))
        
        # Callbacks de dashboard y estadísticas
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_dashboard,
            pattern="^menu_dashboard$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_weekly_stats,
            pattern="^stats_weekly$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_monthly_stats,
            pattern="^stats_monthly$"
        ))
        
        # Callbacks de configuración
        self.app.add_handler(CallbackQueryHandler(
            settings.show_settings_menu,
            pattern="^menu_settings$"
        ))
        
        logger.info("✅ Handlers configurados")
    
    async def start_command(self, update: Update, context):
        """
        Maneja el comando /start con personalidad de Cortana
        """
        # Verificar que el usuario está autorizado
        user_id = update.effective_user.id
        if user_id != config.AUTHORIZED_USER_ID:
            await update.message.reply_text(
                "❌ Acceso denegado. Este sistema es personal y clasificado."
            )
            return
        
        # Mensaje de bienvenida estilo Cortana
        welcome_message = CORTANA_WELCOME.format(
            name=update.effective_user.first_name
        )
        
        # Enviar mensaje con el teclado principal
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"Usuario {user_id} inició el bot - Cortana activada")
    
    async def help_command(self, update: Update, context):
        """
        Maneja el comando /help con personalidad de Cortana
        """
        await update.message.reply_text(
            CORTANA_HELP,
            parse_mode=ParseMode.HTML
        )
    
    def setup_reminders(self):
        """
        Configura el sistema de recordatorios automáticos.
        
        Usa APScheduler para programar tareas que se ejecutan automáticamente:
        - Briefing diario cada mañana
        - Preview nocturno
        - Análisis semanal
        - Informe mensual
        """
        # Inicializar sistema de recordatorios
        self.reminder_system = ReminderSystem(
            db_manager=self.db_manager,
            bot=self.app.bot,
            user_id=config.AUTHORIZED_USER_ID
        )
        
        # Briefing diario (07:00 por defecto)
        self.scheduler.add_job(
            self.reminder_system.send_daily_summary,
            trigger=CronTrigger(hour=7, minute=0),
            id='daily_summary',
            name='Briefing Matutino',
            replace_existing=True
        )
        
        # Preview nocturno (18:00 por defecto)
        self.scheduler.add_job(
            self.reminder_system.send_evening_reminder,
            trigger=CronTrigger(hour=18, minute=0),
            id='evening_reminder',
            name='Preview Nocturno',
            replace_existing=True
        )
        
        # Análisis semanal (domingos a las 20:00)
        self.scheduler.add_job(
            self.reminder_system.send_weekly_summary,
            trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
            id='weekly_summary',
            name='Análisis Semanal',
            replace_existing=True
        )
        
        # Informe mensual (día 1 de cada mes a las 09:00)
        self.scheduler.add_job(
            self.reminder_system.send_monthly_summary,
            trigger=CronTrigger(day=1, hour=9, minute=0),
            id='monthly_summary',
            name='Informe Mensual',
            replace_existing=True
        )
        
        # Iniciar el scheduler
        self.scheduler.start()
        
        logger.info("✅ Sistema de recordatorios configurado")
        logger.info("📅 Briefing Matutino: 07:00")
        logger.info("🔔 Preview Nocturno: 18:00")
        logger.info("📊 Análisis Semanal: Domingos 20:00")
        logger.info("📈 Informe Mensual: Día 1 de cada mes 09:00")
    
    def run(self):
        """
        Inicia el bot y lo mantiene ejecutándose.
        
        Este método:
        1. Configura los handlers
        2. Configura los recordatorios
        3. Inicia el bot en modo polling (escucha constantemente mensajes)
        """
        logger.info("🚀 Iniciando sistema Cortana...")
        
        # Configurar handlers y recordatorios
        self.setup_handlers()
        self.setup_reminders()
        
        # Mensaje de inicio
        logger.info("=" * 50)
        logger.info("✅ Cortana inicializada correctamente")
        logger.info(f"👤 Spartan autorizado: {config.AUTHORIZED_USER_ID}")
        logger.info("🔄 Sistema en línea, esperando comandos...")
        logger.info("=" * 50)
        
        # Iniciar bot (polling = escuchar constantemente)
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Punto de entrada principal
if __name__ == "__main__":
    """
    Este bloque se ejecuta cuando ejecutas el archivo directamente.
    
    Para iniciar el bot, simplemente ejecuta:
    python main.py
    """
    try:
        # Crear instancia del bot
        bot = ProductivityBot()
        
        # Iniciar bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Cortana desconectada. Stay safe, Spartan.")
    except Exception as e:
        logger.error(f"❌ Error crítico del sistema: {e}", exc_info=True)
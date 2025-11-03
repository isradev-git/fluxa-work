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
from handlers import menu, projects, tasks, notes, dashboard, settings, task_conversations, project_conversations

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
        
        IMPORTANTE: El orden de registro es crítico:
        1. Comandos (/start, /help)
        2. ConversationHandlers (diálogos multi-paso) - DEBEN IR PRIMERO
        3. MessageHandlers del menú persistente
        4. CallbackQueryHandlers (botones inline)
        
        Los ConversationHandlers tienen prioridad sobre otros handlers.
        """
        
        # ========== COMANDOS ==========
        
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # ========== CONVERSATION HANDLERS ==========
        # CRÍTICO: Estos DEBEN ir ANTES del menú persistente
        
        # ConversationHandler para crear nuevo proyecto
        project_creation_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    project_conversations.create_project_start, 
                    pattern="^project_new$"
                )
            ],
            states={
                project_conversations.PROJECT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, 
                        project_conversations.project_name_received
                    ),
                    CallbackQueryHandler(
                        project_conversations.project_creation_cancelled,
                        pattern="^project_create_cancel$"
                    )
                ],
                project_conversations.PROJECT_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        project_conversations.project_description_received
                    ),
                    CallbackQueryHandler(
                        project_conversations.project_description_received,
                        pattern="^project_skip_desc$"
                    )
                ],
                project_conversations.PROJECT_PRIORITY: [
                    CallbackQueryHandler(
                        project_conversations.project_priority_received,
                        pattern="^priority_"
                    )
                ],
                project_conversations.PROJECT_DEADLINE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        project_conversations.project_deadline_received
                    ),
                    CallbackQueryHandler(
                        project_conversations.project_deadline_received,
                        pattern="^project_skip_deadline$"
                    )
                ],
                project_conversations.PROJECT_CONFIRM: [
                    CallbackQueryHandler(
                        project_conversations.project_confirmed,
                        pattern="^project_confirm_yes$"
                    ),
                    CallbackQueryHandler(
                        project_conversations.project_creation_cancelled,
                        pattern="^project_create_cancel$"
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    projects.show_projects_menu,
                    pattern="^menu_projects$"
                )
            ],
            allow_reentry=True,
            per_message=True,
            conversation_timeout=300,
            name="project_creation",
            persistent=False
        )
        
        self.app.add_handler(project_creation_handler)
        
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
                        pattern="^task_skip_desc$"
                    )
                ],
                task_conversations.TASK_PRIORITY: [
                    CallbackQueryHandler(
                        task_conversations.task_priority_received,
                        pattern="^priority_"
                    )
                ],
                task_conversations.TASK_DEADLINE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        task_conversations.task_deadline_received
                    ),
                    CallbackQueryHandler(
                        task_conversations.task_deadline_received,
                        pattern="^task_skip_deadline$"
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
                        pattern="^task_create_cancel$"
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    tasks.show_tasks_menu,
                    pattern="^menu_tasks$"
                )
            ],
            allow_reentry=True,
            per_message=True,
            conversation_timeout=300,
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
            per_message=True,
            conversation_timeout=300,
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
            per_message=True,
            conversation_timeout=300,
            name="task_edit",
            persistent=False
        )
        
        self.app.add_handler(task_edit_handler)
        
        # ========== MENÚ PERSISTENTE ==========
        # IMPORTANTE: Estos van DESPUÉS de los ConversationHandlers
        
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
            dashboard.show_dashboard
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['note']} Notas$"),
            notes.show_notes_menu
        ))
        
        self.app.add_handler(MessageHandler(
            filters.Regex(f"^{config.EMOJI['settings']} Configuración$"),
            settings.show_settings_menu
        ))
        
        # ========== CALLBACKS DE NAVEGACIÓN ==========
        
        self.app.add_handler(CallbackQueryHandler(
            menu.back_to_main,
            pattern="^back_to_main$"
        ))
        
        # ========== HANDLERS DE PROYECTOS ==========
        
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
        
        # ========== HANDLERS DE TAREAS ==========
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.show_tasks_menu,
            pattern="^menu_tasks$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.list_tasks,
            pattern="^task_list_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.view_task,
            pattern="^task_view_"
        ))
        
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
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.view_subtasks,
            pattern="^task_view_subtasks_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.edit_task_menu,
            pattern="^task_edit_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.delete_task_confirm,
            pattern="^task_delete_confirm_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            tasks.delete_task_confirmed,
            pattern="^task_delete_(?!confirm)"
        ))
        
        # ========== HANDLERS DE NOTAS ==========
        
        self.app.add_handler(CallbackQueryHandler(
            notes.show_notes_menu,
            pattern="^menu_notes$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            notes.list_notes,
            pattern="^note_list"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            notes.view_note,
            pattern="^note_view_"
        ))
        
        # ========== HANDLERS DE DASHBOARD ==========
        
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_dashboard,
            pattern="^dashboard_main$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_weekly_stats,
            pattern="^dashboard_weekly$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            dashboard.show_monthly_stats,
            pattern="^dashboard_monthly$"
        ))
        
        # ========== HANDLERS DE CONFIGURACIÓN ==========
        
        self.app.add_handler(CallbackQueryHandler(
            settings.show_settings_menu,
            pattern="^settings_menu$"
        ))
        
        logger.info("✅ Handlers configurados")
    
    def setup_reminders(self):
        """
        Configura el sistema de recordatorios automáticos.
        """
        
        # Inicializar sistema de recordatorios
        self.reminder_system = ReminderSystem(
            self.db_manager,
            self.app.bot,
            config.AUTHORIZED_USER_ID
        )
        
        # Resumen diario
        self.scheduler.add_job(
            self.reminder_system.send_daily_summary,
            trigger=CronTrigger(
                hour=config.DEFAULT_DAILY_SUMMARY_TIME.hour,
                minute=config.DEFAULT_DAILY_SUMMARY_TIME.minute
            ),
            id='daily_summary',
            name='Resumen diario'
        )
        logger.info(f"✅ Resumen diario programado: {config.DEFAULT_DAILY_SUMMARY_TIME}")
        
        # Recordatorio tarde
        self.scheduler.add_job(
            self.reminder_system.send_evening_reminder,
            trigger=CronTrigger(
                hour=config.DEFAULT_EVENING_REMINDER_TIME.hour,
                minute=config.DEFAULT_EVENING_REMINDER_TIME.minute
            ),
            id='evening_reminder',
            name='Recordatorio tarde'
        )
        logger.info(f"✅ Recordatorio tarde programado: {config.DEFAULT_EVENING_REMINDER_TIME}")
        
        # Resumen semanal
        self.scheduler.add_job(
            self.reminder_system.send_weekly_summary,
            trigger=CronTrigger(
                day_of_week='sun',
                hour=20,
                minute=0
            ),
            id='weekly_summary',
            name='Resumen semanal'
        )
        logger.info("✅ Resumen semanal programado: Domingos 20:00")
        
        # Resumen mensual
        self.scheduler.add_job(
            self.reminder_system.send_monthly_summary,
            trigger=CronTrigger(
                day=1,
                hour=9,
                minute=0
            ),
            id='monthly_summary',
            name='Resumen mensual'
        )
        logger.info("✅ Resumen mensual programado: Día 1 de cada mes, 09:00")
        
        # Iniciar el scheduler
        self.scheduler.start()
        logger.info("✅ Sistema de recordatorios configurado")
    
    async def start_command(self, update: Update, context):
        """
        Maneja el comando /start.
        """
        user = update.effective_user
        
        if user.id != config.AUTHORIZED_USER_ID:
            await update.message.reply_text(
                "❌ Lo siento, no estás autorizado para usar este bot."
            )
            return
        
        welcome_message = CORTANA_WELCOME.format(name=user.first_name)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=get_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Usuario {user.first_name} ({user.id}) inició el bot")
    
    async def help_command(self, update: Update, context):
        """
        Maneja el comando /help.
        """
        await update.message.reply_text(
            CORTANA_HELP,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )
    
    def run(self):
        """
        Inicia el bot y lo mantiene ejecutándose.
        """
        
        self.setup_handlers()
        self.setup_reminders()
        
        print("\n" + "="*50)
        print("✅ Bot de productividad iniciado correctamente")
        print(f"👤 Usuario autorizado: {config.AUTHORIZED_USER_ID}")
        print("🔄 Esperando mensajes...")
        print("="*50 + "\n")
        
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """
    Función principal que crea e inicia el bot.
    """
    try:
        bot = ProductivityBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Revisa los logs para más detalles")


if __name__ == "__main__":
    main()
"""
Handler de configuración
Gestiona la configuración del bot
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from utils.keyboards import get_settings_menu


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra el menú de configuración.
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
⚙️ <b>Configuración</b>

Personaliza el funcionamiento del bot:

• Cambiar horarios de recordatorios
• Activar/desactivar notificaciones
• Exportar tus datos
• Ajustar zona horaria

¿Qué quieres configurar?
"""
    
    if is_callback:
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_menu()
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_menu()
        )


# NOTA: La configuración completa requeriría ConversationHandler
# para manejar diálogos de cambio de hora, zona horaria, etc.
# Esta es la estructura base que puedes expandir.

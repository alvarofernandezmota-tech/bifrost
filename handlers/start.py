"""Handler para el comando /start - Mensaje de bienvenida."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.auth import verificar_chat_autorizado


async def comando_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /start - Mensaje de bienvenida.
    
    Muestra los comandos disponibles al usuario.
    """
    if not verificar_chat_autorizado(update):
        return

    await update.message.reply_text(
        "👋 ¡Hola! Soy Bifrost, tu bot de diario personal.\n\n"
        "Comandos disponibles:\n"
        "/diario <texto> - Inserta texto en la entrada de hoy\n"
        "/entrada <fecha> <texto> - Crea/actualiza entrada para una fecha\n"
        "/start - Muestra este mensaje"
    )

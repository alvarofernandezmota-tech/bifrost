"""Handler para el comando /help - Mostrar ayuda."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.auth import verificar_chat_autorizado


async def comando_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /help - Muestra ayuda detallada.
    
    Explica cada comando disponible y su uso.
    """
    if not verificar_chat_autorizado(update):
        return

    await update.message.reply_text(
        "📖 **Ayuda de Bifrost**\n\n"
        "**/diario <texto>**\n"
        "Inserta texto en la sección 'Qué ha pasado hoy' de la entrada de hoy.\n\n"
        "**/entrada <fecha> <texto>**\n"
        "Crea o actualiza una entrada para la fecha especificada (YYYY-MM-DD).\n\n"
        "**/start** - Mensaje de bienvenida\n"
        "**/help** - Muestra esta ayuda"
    )

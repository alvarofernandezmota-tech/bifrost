"""Handler para el comando /diario - Insertar texto en la entrada de hoy."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.auth import verificar_chat_autorizado
from organizar_diario import organizar_texto

logger = logging.getLogger(__name__)


async def comando_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /diario - Inserta texto en la sección 'Qué ha pasado hoy' de la entrada de hoy.
    
    Uso: /diario <texto a registrar>
    """
    if not verificar_chat_autorizado(update):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return

    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("❌ Uso: /diario <texto a registrar>")
        return

    try:
        ruta = organizar_texto(texto)
        await update.message.reply_text(f"✅ Texto guardado en: {ruta}")
    except Exception as e:
        logger.error(f"Error al organizar texto: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

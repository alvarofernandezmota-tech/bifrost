"""Handler para el comando /entrada - Crear/actualizar entrada para una fecha."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.auth import verificar_chat_autorizado
from core.bridge import escribir_entrada

logger = logging.getLogger(__name__)


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /entrada - Crea o actualiza una entrada para una fecha específica.
    
    Uso: /entrada <YYYY-MM-DD> <texto>
    Ej: /entrada 2026-08-30 Hoy fue un gran día
    """
    if not verificar_chat_autorizado(update):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /entrada <YYYY-MM-DD> <texto>")
        return

    fecha = context.args[0]
    texto = " ".join(context.args[1:])

    try:
        ruta = escribir_entrada(fecha, texto)
        await update.message.reply_text(f"✅ Entrada creada/actualizada en: {ruta}")
    except Exception as e:
        logger.error(f"Error al escribir entrada: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

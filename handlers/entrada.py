"""Handler para el comando /entrada."""

import sys
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

# Ruta a midgaror/diario/ (4 niveles arriba desde handlers/)
MIDGAROR = Path(__file__).resolve().parent.parent.parent.parent
DIARIO = MIDGAROR / "diario"
sys.path.insert(0, str(DIARIO))

from bifrost_bridge import escribir_entrada

logger = logging.getLogger(__name__)


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /entrada."""
    if len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /entrada <YYYY-MM-DD> <texto>")
        return

    fecha = context.args[0]
    texto = " ".join(context.args[1:])

    try:
        ruta = escribir_entrada(fecha, texto)
        await update.message.reply_text(f"✅ Guardado en: {ruta}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

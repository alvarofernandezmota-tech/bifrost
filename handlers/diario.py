"""Handler para el comando /diario."""

import sys
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

# Ruta a midgaror/diario/ (4 niveles arriba desde handlers/)
MIDGAROR = Path(__file__).resolve().parent.parent.parent.parent
DIARIO = MIDGAROR / "diario"
sys.path.insert(0, str(DIARIO))

from organizar_diario import organizar_texto

logger = logging.getLogger(__name__)


async def comando_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /diario."""
    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("❌ Uso: /diario <texto>")
        return

    try:
        ruta = organizar_texto(texto)
        await update.message.reply_text(f"✅ Guardado en: {ruta}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

"""Handler para el comando /diario."""

import logging
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

# Ruta a midgaror/diario/ (4 niveles arriba desde handlers/)
MIDGAROR = Path(__file__).resolve().parent.parent.parent.parent
DIARIO = MIDGAROR / "diario"
sys.path.insert(0, str(DIARIO))

from organizar_diario import organizar_texto  # noqa: E402 (requiere sys.path previo)

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
        logger.exception("Error escribiendo en el diario de hoy")
        await update.message.reply_text(f"❌ Error: {e}")

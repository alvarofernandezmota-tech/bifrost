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
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve, responder  # noqa: E402 (requiere sys.path previo)

logger = logging.getLogger(__name__)


async def comando_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /diario."""
    texto = " ".join(context.args)
    if not texto:
        await responder(update, 
            "❌ Escribe el texto detrás del comando, sin < ni >:\n"
            "/diario hoy he dormido fatal")
        return

    try:
        ruta = organizar_texto(texto)
        await responder(update, f"📔 Apuntado en el diario de hoy · {breve(sincronizar(ruta))}")
    except Exception as e:
        logger.exception("Error escribiendo en el diario de hoy")
        await responder(update, f"❌ Error: {e}")

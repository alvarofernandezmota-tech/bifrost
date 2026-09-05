"""Handler para el comando /diario."""

import asyncio
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
        # sincronizar() hace git commit y git push: hasta 90 s con mala red.
        # Dentro de una corrutina eso congela el bot entero para todos los
        # chats, no solo para quien mando el mensaje. to_thread lo saca del
        # hilo del bucle de eventos, que sigue atendiendo lo demas.
        subido = breve(await asyncio.to_thread(sincronizar, ruta))
        await responder(update, f"📔 Apuntado en el diario de hoy · {subido}")
    except Exception as e:
        logger.exception("Error escribiendo en el diario de hoy")
        await responder(update, f"❌ Error: {e}")

"""Handler para el comando /diario."""

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.midgaror import modulo
from utils.respuestas import breve, responder

organizar_texto = modulo("organizar_diario").organizar_texto
sincronizar = modulo("sincronizar").sincronizar

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

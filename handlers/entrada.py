"""Handler para el comando /entrada."""

import asyncio
import logging
import re
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

# Ruta a midgaror/diario/ (4 niveles arriba desde handlers/)
MIDGAROR = Path(__file__).resolve().parent.parent.parent.parent
DIARIO = MIDGAROR / "diario"
sys.path.insert(0, str(DIARIO))

from bifrost_bridge import escribir_entrada  # noqa: E402 (requiere sys.path previo)
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve, responder  # noqa: E402 (requiere sys.path previo)

logger = logging.getLogger(__name__)

FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /entrada <AAAA-MM-DD> <texto>."""
    if len(context.args) < 2:
        await responder(update, 
            "❌ Escribe la fecha y el texto, sin < ni >:\n"
            "/entrada 2026-09-03 se me olvidó apuntar esto")
        return

    fecha = context.args[0]
    if not FECHA_RE.match(fecha):
        await responder(update, 
            f"❌ Fecha inválida: {fecha}\nFormato esperado: AAAA-MM-DD, por ejemplo 2026-09-04"
        )
        return

    texto = " ".join(context.args[1:])

    try:
        ruta = escribir_entrada(texto, fecha)
        # sincronizar() hace git commit y git push: hasta 90 s con mala red.
        # Dentro de una corrutina eso congela el bot entero para todos los
        # chats, no solo para quien mando el mensaje. to_thread lo saca del
        # hilo del bucle de eventos, que sigue atendiendo lo demas.
        subido = breve(await asyncio.to_thread(sincronizar, ruta))
        await responder(update, f"📔 Apuntado en el diario del {fecha} · {subido}")
    except Exception as e:
        logger.exception("Error escribiendo la entrada del %s", fecha)
        await responder(update, f"❌ Error: {e}")

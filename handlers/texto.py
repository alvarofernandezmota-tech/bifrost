"""Un mensaje suelto, sin comando, va al diario de hoy.

Es lo que pasa en cuanto se usa el bot de verdad: se escribe «hoy he dormido
fatal» y se manda, sin acordarse de poner /diario delante. Antes el bot
callaba y el texto se perdía; ahora se apunta igual que con /diario.

Los comandos siguen teniendo prioridad: este handler se registra el último y
solo recibe lo que no empieza por «/».
"""

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

from utils.respuestas import breve  # noqa: E402 (coherencia con el resto de handlers)

logger = logging.getLogger(__name__)


async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cualquier texto que no sea un comando: al diario de hoy."""
    texto = (update.message.text or "").strip()
    if not texto:
        return
    try:
        ruta = organizar_texto(texto)
        await update.message.reply_text(f"📔 Apuntado en el diario de hoy · {breve(sincronizar(ruta))}")
    except Exception as e:
        logger.exception("Error escribiendo un mensaje suelto en el diario")
        await update.message.reply_text(f"❌ Error: {e}")

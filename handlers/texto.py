"""Un mensaje suelto, sin comando, va al diario de hoy.

Es lo que pasa en cuanto se usa el bot de verdad: se escribe «hoy he dormido
fatal» y se manda, sin acordarse de poner /diario delante. Antes el bot
callaba y el texto se perdía; ahora se apunta igual que con /diario.

Los comandos siguen teniendo prioridad: este handler se registra el último y
solo recibe lo que Telegram no marca como comando. Ojo: eso no es lo mismo
que "no empieza por /". Un comando **pegado con formato de código** llega sin
la marca `bot_command`, cae aquí, y acabaría en el diario en vez de
ejecutarse. Pasó el 2026-09-05: treinta comandos seguidos al diario, sin un
solo aviso. Por eso este handler no escribe nada que empiece por «/».
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


AVISO_COMANDO = (
    "⚠️ Esto parece un comando, pero no me ha llegado como tal, así que **no** "
    "lo he ejecutado ni lo he apuntado en el diario.\n\n"
    "Suele pasar al pegarlo con formato (por ejemplo copiado de un bloque de "
    "código). Escríbelo a mano, o pégalo como texto sin formato.\n\n"
    "Lo que me llegó:\n{texto}"
)


async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cualquier texto que no sea un comando: al diario de hoy."""
    texto = (update.message.text or "").strip()
    if not texto:
        return
    if texto.startswith("/"):
        # Un comando de verdad no llega aquí: lo habría cogido su CommandHandler.
        # Si llega, es que Telegram no lo marcó como comando, y meterlo en el
        # diario sería tragárselo en silencio. Se avisa y se devuelve el texto
        # para poder reenviarlo sin volver a escribirlo.
        logger.warning("Texto que parece comando y no lo es (entidades: %s): %r",
                       [e.type for e in (update.message.entities or [])], texto[:80])
        await update.message.reply_text(AVISO_COMANDO.format(texto=texto))
        return
    try:
        ruta = organizar_texto(texto)
        await update.message.reply_text(f"📔 Apuntado en el diario de hoy · {breve(sincronizar(ruta))}")
    except Exception as e:
        logger.exception("Error escribiendo un mensaje suelto en el diario")
        await update.message.reply_text(f"❌ Error: {e}")

"""Handler de /hoy: el día de un vistazo, sin escribir nada.

Junta lo que ya saben decir los módulos de midgaror: la entrada del diario
(`leer_entrada`), las tareas pendientes y los hábitos apuntados. Leer nunca
escribe: si no hay entrada del día, lo dice en vez de crearla.
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
sys.path.insert(0, str(DIARIO / "tareas"))
sys.path.insert(0, str(DIARIO / "habitos"))

import habitos  # noqa: E402 (requiere sys.path previo)
import tareas  # noqa: E402 (requiere sys.path previo)
from bifrost_bridge import leer_entrada  # noqa: E402 (requiere sys.path previo)

logger = logging.getLogger(__name__)

# Telegram corta los mensajes en 4096 caracteres; el diario del día puede
# ser largo, así que se recorta él y no las tareas ni los hábitos.
TOPE_DIARIO = 2500


async def comando_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/hoy [AAAA-MM-DD] — diario, tareas pendientes y hábitos de ese día."""
    fecha = context.args[0] if context.args else None
    try:
        diario = leer_entrada(fecha)
        if len(diario) > TOPE_DIARIO:
            diario = diario[:TOPE_DIARIO].rstrip() + "\n…(recortado)"
        partes = [
            "📔 Diario\n" + diario,
            "\n📋 Tareas\n" + tareas.resumen(),
            "\n🔁 Hábitos\n" + habitos.resumen_dia(fecha),
        ]
        await update.message.reply_text("\n".join(partes))
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /hoy")
        await update.message.reply_text(f"❌ Error: {e}")

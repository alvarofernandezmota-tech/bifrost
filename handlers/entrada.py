"""Handler para el comando /entrada."""

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

logger = logging.getLogger(__name__)

FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /entrada <AAAA-MM-DD> <texto>."""
    if len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /entrada <AAAA-MM-DD> <texto>")
        return

    fecha = context.args[0]
    if not FECHA_RE.match(fecha):
        await update.message.reply_text(
            f"❌ Fecha inválida: {fecha}\nFormato esperado: AAAA-MM-DD, por ejemplo 2026-09-04"
        )
        return

    texto = " ".join(context.args[1:])

    try:
        ruta = escribir_entrada(texto, fecha)
        await update.message.reply_text(f"✅ Guardado en: {ruta}")
    except Exception as e:
        logger.exception("Error escribiendo la entrada del %s", fecha)
        await update.message.reply_text(f"❌ Error: {e}")

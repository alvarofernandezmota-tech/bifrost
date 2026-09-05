"""Handlers de /siento, /aprendo y /plan: cada uno a su sección del diario.

De las cuatro secciones de la plantilla, «Qué ha pasado hoy» está rellena el
100 % de los días y las otras tres entre el 30 y el 40 %. La diferencia no es
la disciplina: es que en la primera escribe el bot y en las otras hay que
abrir un editor (ADR-012, apartado 5). Estos tres comandos igualan eso.

Como el resto de bifrost, esto es solo interfaz: quién escribe dónde y con
qué formato lo decide `organizar_diario.SECCIONES` en midgaror.
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

# comando -> (clave de sección en midgaror, cómo se confirma, ejemplo de uso)
DESTINOS = {
    "siento": ("siento", "💬 Apuntado en «Cómo me siento»",
               "/siento hoy estoy contento, he dormido bien"),
    "aprendo": ("aprendo", "💡 Apuntado en «Avances / aprendizajes»",
                "/aprendo lo de filters.COMMAND de Telegram"),
    "plan": ("plan", "🌅 Apuntado en «Para mañana»",
             "/plan seguir con el portfolio"),
}


async def _escribir(update: Update, context: ContextTypes.DEFAULT_TYPE, comando: str) -> None:
    seccion, confirmacion, ejemplo = DESTINOS[comando]
    texto = " ".join(context.args)
    if not texto.strip():
        await update.message.reply_text(
            f"❌ Escribe el texto detrás del comando, sin < ni >:\n{ejemplo}")
        return
    try:
        ruta = organizar_texto(texto, seccion=seccion)
        await update.message.reply_text(f"{confirmacion} · {breve(sincronizar(ruta))}")
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error escribiendo en la sección %s", seccion)
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_siento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/siento <texto> — va a «## Cómo me siento», con la hora delante."""
    await _escribir(update, context, "siento")


async def comando_aprendo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/aprendo <texto> — va a «## Avances / aprendizajes», como viñeta."""
    await _escribir(update, context, "aprendo")


async def comando_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/plan <texto> — va a «## Para mañana», como viñeta."""
    await _escribir(update, context, "plan")

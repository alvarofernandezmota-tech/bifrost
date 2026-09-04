"""Handlers de /tarea y /tareas.

Como el resto de bifrost, esto es solo interfaz: la lógica vive en
midgaror/diario/tareas/tareas.py y aquí solo se traduce el mensaje de
Telegram a una llamada y la respuesta a texto.
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

import tareas  # noqa: E402 (requiere sys.path previo)
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve  # noqa: E402 (coherencia con el resto de handlers)

logger = logging.getLogger(__name__)

AYUDA = (
    "❌ Uso:\n"
    "/tarea comprar el pan — apunta una tarea\n"
    "/tarea hecha 3 — la marca hecha\n"
    "/tarea borrar 3 — la retira de la lista\n"
    "/tareas — las pendientes"
)


def _subir() -> str:
    return breve(sincronizar(tareas.RUTA_DATOS, "diario: tareas desde bifrost"))


async def comando_tarea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tarea <texto> | /tarea hecha <id> | /tarea borrar <id>"""
    args = context.args
    if not args:
        await update.message.reply_text(AYUDA)
        return
    try:
        if args[0] in ("hecha", "borrar"):
            if len(args) < 2 or not args[1].isdigit():
                await update.message.reply_text(f"❌ Falta el número de la tarea.\n\n{AYUDA}")
                return
            accion = tareas.hecha if args[0] == "hecha" else tareas.borrar
            t = accion(int(args[1]))
            icono = "✅" if args[0] == "hecha" else "🗑️"
            await update.message.reply_text(f"{icono} [{t['id']}] {t['texto']} · {_subir()}")
            return
        t = tareas.agregar(" ".join(args))
        await update.message.reply_text(f"✅ [{t['id']}] {t['texto']} · {_subir()}")
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /tarea")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_tareas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tareas — pendientes y últimas hechas."""
    try:
        await update.message.reply_text(tareas.resumen())
    except Exception as e:
        logger.exception("Error en /tareas")
        await update.message.reply_text(f"❌ Error: {e}")

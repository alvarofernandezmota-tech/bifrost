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
    "/tarea médico mañana a las 10 — apunta una tarea, con fecha si la dices\n"
    "/tarea empezar 3 — la pone en proceso\n"
    "/tarea hecha 3 — la marca hecha\n"
    "/tarea reabrir 3 — la devuelve a pendiente\n"
    "/tarea editar 3 comprar pan y leche — le cambia el texto\n"
    "/tarea aplazar 3 el lunes por la tarde — le cambia la fecha\n"
    "/tarea borrar 3 — la retira de la lista\n"
    "/tareas — las abiertas y las últimas hechas"
)

# Los que solo necesitan el id, y el icono con el que se confirma cada uno.
SOLO_ID = {"empezar": tareas.empezar, "hecha": tareas.hecha,
           "reabrir": tareas.reabrir, "borrar": tareas.borrar}
ICONO = {"empezar": "◐", "hecha": "✅", "reabrir": "○", "borrar": "🗑️",
         "editar": "✏️", "aplazar": "📅"}
# Y los que además necesitan texto detrás del id.
CON_TEXTO = {"editar": tareas.editar, "aplazar": tareas.aplazar}


def _subir() -> str:
    return breve(sincronizar(tareas.RUTA_DATOS, "diario: tareas desde bifrost"))


def _cuando(t: dict) -> str:
    """« · mañana 10:00» si la tarea tiene fecha; nada si no."""
    if not t.get("fecha"):
        return ""
    return f" · {t['fecha']}" + (f" {t['hora']}" if t.get("hora") else "")


async def comando_tarea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tarea <texto> | /tarea <acción> <id> [texto]"""
    args = context.args
    if not args:
        await update.message.reply_text(AYUDA)
        return
    accion, resto = args[0], args[1:]
    try:
        if accion in SOLO_ID or accion in CON_TEXTO:
            if not resto or not resto[0].isdigit():
                await update.message.reply_text(f"❌ Falta el número de la tarea.\n\n{AYUDA}")
                return
            id_tarea, resto = int(resto[0]), resto[1:]
            if accion in SOLO_ID:
                t = SOLO_ID[accion](id_tarea)
            else:
                if not resto:
                    falta = "el texto nuevo" if accion == "editar" else "el cuándo"
                    await update.message.reply_text(f"❌ Falta {falta}.\n\n{AYUDA}")
                    return
                t = CON_TEXTO[accion](id_tarea, " ".join(resto))
            await update.message.reply_text(
                f"{ICONO[accion]} [{t['id']}] {t['texto']}{_cuando(t)} · {_subir()}")
            return
        t = tareas.agregar(" ".join(args))
        await update.message.reply_text(f"✅ [{t['id']}] {t['texto']}{_cuando(t)} · {_subir()}")
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /tarea")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_tareas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/tareas — en proceso, pendientes por fecha y últimas hechas."""
    try:
        await update.message.reply_text(tareas.resumen())
    except Exception as e:
        logger.exception("Error en /tareas")
        await update.message.reply_text(f"❌ Error: {e}")

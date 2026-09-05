"""Handlers de /cita y /agenda.

Como el resto de bifrost, esto es solo interfaz: la lógica vive en
midgaror/diario/agenda/agenda.py y aquí solo se traduce el mensaje de
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
sys.path.insert(0, str(DIARIO / "agenda"))

import agenda  # noqa: E402 (requiere sys.path previo)
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve  # noqa: E402 (coherencia con el resto de handlers)

logger = logging.getLogger(__name__)

AYUDA = (
    "❌ Uso:\n"
    "/cita médico mañana a las 10 — apunta una cita\n"
    "/cita mover 3 el lunes a las 17 — la cambia de hora\n"
    "/cita cancelar 3 — la retira\n"
    "/agenda — las citas de hoy\n"
    "/agenda semana — los siete días desde hoy"
)


def _subir() -> str:
    return breve(sincronizar(agenda.RUTA_DATOS, "diario: citas desde bifrost"))


def _confirmacion(cita: dict, solapan: list[dict], subido: str) -> str:
    """La cita guardada y, si choca con otra, el aviso debajo."""
    cuando = f"{cita['fecha']} {cita['hora']}" if cita.get("hora") else f"{cita['fecha']} (todo el día)"
    texto = f"📅 [{cita['id']}] {cita['texto']} · {cuando} · {subido}"
    aviso = agenda.aviso_choques(solapan)
    return f"{texto}\n{aviso}" if aviso else texto


async def comando_cita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/cita <texto con cuándo> | /cita mover <id> <cuándo> | /cita cancelar <id>"""
    args = context.args
    if not args:
        await update.message.reply_text(AYUDA)
        return
    try:
        if args[0] in ("mover", "cancelar"):
            if len(args) < 2 or not args[1].isdigit():
                await update.message.reply_text(f"❌ Falta el número de la cita.\n\n{AYUDA}")
                return
            id_cita = int(args[1])
            if args[0] == "cancelar":
                cita = agenda.cancelar(id_cita)
                await update.message.reply_text(
                    f"🗑️ [{cita['id']}] {cita['texto']} · {cita['fecha']} · {_subir()}")
                return
            if len(args) < 3:
                await update.message.reply_text(f"❌ Falta el cuándo.\n\n{AYUDA}")
                return
            cita, solapan = agenda.mover(id_cita, " ".join(args[2:]))
            await update.message.reply_text(_confirmacion(cita, solapan, _subir()))
            return
        cita, solapan = agenda.agregar(" ".join(args))
        await update.message.reply_text(_confirmacion(cita, solapan, _subir()))
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /cita")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/agenda [semana] [AAAA-MM-DD]"""
    args = list(context.args)
    semana = bool(args) and args[0] == "semana"
    if semana:
        args = args[1:]
    try:
        await update.message.reply_text(
            agenda.resumen(args[0] if args else None, semana=semana))
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /agenda")
        await update.message.reply_text(f"❌ Error: {e}")

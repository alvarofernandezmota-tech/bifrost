"""Handlers de /habito y /habitos.

Interfaz de midgaror/diario/habitos/habitos.py, igual que /tarea con tareas.
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
sys.path.insert(0, str(DIARIO / "habitos"))

import habitos  # noqa: E402 (requiere sys.path previo)
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve  # noqa: E402 (coherencia con el resto de handlers)

logger = logging.getLogger(__name__)

AYUDA = (
    "❌ Uso:\n"
    "/habito deporte — apúntalo como hecho hoy\n"
    "/habito no meditar — apúntalo como no hecho\n"
    "/habito deporte 2026-09-03 — en otro día\n"
    "/habitos — los de hoy\n"
    "/habitos semana — la semana"
)


async def comando_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/habito [no] <nombre> [AAAA-MM-DD]"""
    args = list(context.args)
    if not args:
        await update.message.reply_text(AYUDA)
        return
    hecho = True
    if args[0] == "no":
        hecho, args = False, args[1:]
    if not args:
        await update.message.reply_text(AYUDA)
        return
    nombre, fecha = args[0], (args[1] if len(args) > 1 else None)
    try:
        fecha, nombre, hecho = habitos.marcar(nombre, hecho=hecho, fecha=fecha)
        subido = breve(sincronizar(habitos.RUTA_DATOS, "diario: hábitos desde bifrost"))
        await update.message.reply_text(f"{'✅' if hecho else '❌'} {nombre} — {fecha} · {subido}")
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /habito")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/habitos [semana | AAAA-MM-DD]"""
    args = context.args
    try:
        if args and args[0] == "semana":
            texto = habitos.resumen_semana(args[1] if len(args) > 1 else None)
        else:
            texto = habitos.resumen_dia(args[0] if args else None)
        await update.message.reply_text(texto)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /habitos")
        await update.message.reply_text(f"❌ Error: {e}")

"""Handlers de /habito y /habitos.

Interfaz de midgaror/diario/habitos/habitos.py, igual que /tarea con tareas.
"""

import asyncio
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

from utils.respuestas import breve, responder  # noqa: E402 (requiere sys.path previo)

logger = logging.getLogger(__name__)

AYUDA = (
    "❌ Uso:\n"
    "/habito deporte — apúntalo como hecho hoy\n"
    "/habito no meditar — apúntalo como no hecho\n"
    "/habito energia 7 — apunta un valor del 1 al 10\n"
    "/habito deporte 2026-09-03 — en otro día\n"
    "/habitos — los de hoy\n"
    "/habitos semana — la semana"
)


async def comando_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/habito [no] <nombre> [valor 1-10] [AAAA-MM-DD]"""
    args = list(context.args)
    if not args:
        await responder(update, AYUDA)
        return
    hecho = True
    if args[0] == "no":
        hecho, args = False, args[1:]
    if not args:
        await responder(update, AYUDA)
        return
    # /habito energia 7 [fecha]: el valor es un número suelto detrás del nombre.
    nombre, resto = args[0], args[1:]
    valor = resto.pop(0) if resto and resto[0].isdigit() else None
    fecha = resto[0] if resto else None
    try:
        fecha, nombre, marca = habitos.marcar(nombre, hecho=hecho, fecha=fecha, valor=valor)
        # sincronizar() hace git commit y git push: hasta 90 s con mala red.
        # Dentro de una corrutina eso congela el bot entero para todos los
        # chats, no solo para quien mando el mensaje. to_thread lo saca del
        # hilo del bucle de eventos, que sigue atendiendo lo demas.
        subido = breve(await asyncio.to_thread(
            sincronizar, habitos.RUTA_DATOS, "diario: hábitos desde bifrost"))
        await responder(update, f"{habitos.formato(marca)} {nombre} — {fecha} · {subido}")
    except ValueError as e:
        await responder(update, f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /habito")
        await responder(update, f"❌ Error: {e}")


async def comando_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/habitos [semana | AAAA-MM-DD]"""
    args = context.args
    try:
        if args and args[0] == "semana":
            texto = habitos.resumen_semana(args[1] if len(args) > 1 else None)
        else:
            texto = habitos.resumen_dia(args[0] if args else None)
        await responder(update, texto)
    except ValueError as e:
        await responder(update, f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /habitos")
        await responder(update, f"❌ Error: {e}")

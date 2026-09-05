"""Handlers de /habito y /habitos.

Interfaz de midgaror/diario/habitos/habitos.py, igual que /tarea con tareas.
"""

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
sys.path.insert(0, str(DIARIO / "habitos"))

import habitos  # noqa: E402 (requiere sys.path previo)
from sincronizar import sincronizar  # noqa: E402 (requiere sys.path previo)

from utils.respuestas import breve, responder  # noqa: E402 (requiere sys.path previo)

logger = logging.getLogger(__name__)

AYUDA = (
    "❌ Uso:\n"
    "/habito deporte — apúntalo como hecho hoy\n"
    "/habito Leer Libro — el nombre puede llevar espacios\n"
    "/habito no meditar — apúntalo como no hecho\n"
    "/habito energia 7 — apunta un valor del 1 al 10\n"
    "/habito deporte 2026-09-03 — en otro día\n"
    "/habito Beber agua 3 2026-09-03 — todo junto\n"
    "/habitos — los de hoy\n"
    "/habitos semana — la semana"
)

FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _partir(args: list[str]) -> tuple[str, str | None, str | None]:
    """(nombre, valor, fecha) a partir de los argumentos de /habito.

    El nombre puede llevar espacios («Leer Libro»), así que se reconoce por
    descarte: del final se quita la fecha si tiene forma AAAA-MM-DD y el
    valor si es un entero; lo que queda es el nombre.

    Antes el último argumento se tomaba SIEMPRE como fecha, y por eso
    «/habito Leer Libro» moría con «fecha no válida: 'Libro'». Un hábito de
    dos palabras es de lo más normal y no había manera de apuntarlo.
    """
    restantes = list(args)
    fecha = restantes.pop() if FECHA_RE.match(restantes[-1]) else None
    # El valor solo se reconoce si detrás queda algo que sea el nombre: en
    # «/habito 7», el 7 es el nombre del hábito, por raro que sea, y no un
    # valor suelto sin hábito al que pegarse.
    valor = restantes.pop() if len(restantes) > 1 and restantes[-1].isdigit() else None
    return " ".join(restantes), valor, fecha


async def comando_habito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/habito [no] <nombre con espacios> [valor 1-10] [AAAA-MM-DD]"""
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
    nombre, valor, fecha = _partir(args)
    try:
        fecha, nombre, marca = habitos.marcar(nombre, hecho=hecho, fecha=fecha, valor=valor)
        subido = breve(sincronizar(habitos.RUTA_DATOS, "diario: hábitos desde bifrost"))
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

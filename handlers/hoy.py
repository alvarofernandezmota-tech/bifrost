"""Handler de /hoy: el día de un vistazo, sin escribir nada.

Junta lo que ya saben decir los módulos de midgaror: la entrada del diario
(`leer_entrada`), las citas del día, las tareas pendientes y los hábitos
apuntados. Leer nunca escribe: si no hay entrada del día, lo dice en vez de
crearla.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.midgaror import modulo
from utils.respuestas import responder

agenda = modulo("agenda")
habitos = modulo("habitos")
tareas = modulo("tareas")
leer_entrada = modulo("bifrost_bridge").leer_entrada

logger = logging.getLogger(__name__)

# Telegram corta los mensajes en 4096 caracteres; el diario del día puede
# ser largo, así que se recorta él y no las tareas ni los hábitos.
TOPE_DIARIO = 2500


async def comando_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/hoy [AAAA-MM-DD] — diario, citas, tareas y hábitos de ese día."""
    fecha = context.args[0] if context.args else None
    try:
        diario = leer_entrada(fecha)
        if len(diario) > TOPE_DIARIO:
            diario = diario[:TOPE_DIARIO].rstrip() + "\n…(recortado)"
        partes = [
            "📔 Diario\n" + diario,
            "\n📅 Citas\n" + agenda.resumen(fecha),
            "\n📋 Tareas\n" + tareas.resumen(hoy=fecha),
            "\n🔁 Hábitos\n" + habitos.resumen_dia(fecha),
        ]
        await responder(update, "\n".join(partes))
    except ValueError as e:
        await responder(update, f"⚠️ {e}")
    except Exception as e:
        logger.exception("Error en /hoy")
        await responder(update, f"❌ Error: {e}")

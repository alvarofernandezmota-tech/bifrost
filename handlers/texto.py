"""Un mensaje suelto, sin comando, va al diario de hoy.

Es lo que pasa en cuanto se usa el bot de verdad: se escribe «hoy he dormido
fatal» y se manda, sin acordarse de poner /diario delante. Antes el bot
callaba y el texto se perdía; ahora se apunta igual que con /diario.

Los comandos siguen teniendo prioridad: este handler se registra el último y
solo recibe lo que Telegram no marca como comando. Ojo: eso no es lo mismo
que "no empieza por /". Un comando **pegado con formato de código** llega sin
la marca `bot_command`, cae aquí, y acabaría en el diario en vez de
ejecutarse. Pasó el 2026-09-05: treinta comandos seguidos al diario, sin un
solo aviso. Por eso este handler no escribe nada que empiece por «/».
"""

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils.midgaror import modulo
from utils.respuestas import breve, dia, responder, responder_si_puedo

fechas = modulo("fechas")
organizar_texto = modulo("organizar_diario").organizar_texto
sincronizar = modulo("sincronizar").sincronizar

logger = logging.getLogger(__name__)


AVISO_COMANDO = (
    "⚠️ Esto parece un comando, pero no me ha llegado como tal, así que **no** "
    "lo he ejecutado ni lo he apuntado en el diario.\n\n"
    "Suele pasar al pegarlo con formato (por ejemplo copiado de un bloque de "
    "código). Escríbelo a mano, o pégalo como texto sin formato.\n\n"
    "Lo que me llegó:\n{texto}"
)


async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cualquier texto que no sea un comando: al diario de hoy."""
    texto = (update.effective_message.text or "").strip()
    if not texto:
        return
    if texto.startswith("/"):
        # Un comando de verdad no llega aquí: lo habría cogido su CommandHandler.
        # Si llega, es que Telegram no lo marcó como comando, y meterlo en el
        # diario sería tragárselo en silencio. Se avisa y se devuelve el texto
        # para poder reenviarlo sin volver a escribirlo.
        logger.warning("Texto que parece comando y no lo es (entidades: %s): %r",
                       [e.type for e in (update.effective_message.entities or [])], texto[:80])
        await responder(update, AVISO_COMANDO.format(texto=texto))
        return
    # «cené con mi hermana ayer» va al día de ayer, sin el «ayer». Solo el
    # pasado sin ambigüedad cuenta (fechas.fecha_detras): «tengo examen
    # mañana» es una frase de hoy y se queda entera.
    texto, fecha = fechas.fecha_detras(texto)
    try:
        ruta = organizar_texto(texto, fecha=fecha)
        # sincronizar() hace git commit y git push: hasta 90 s con mala red.
        # Dentro de una corrutina eso congela el bot entero para todos los
        # chats, no solo para quien mando el mensaje. to_thread lo saca del
        # hilo del bucle de eventos, que sigue atendiendo lo demas.
        subido = breve(await asyncio.to_thread(sincronizar, ruta))
        await responder(update, f"📔 Apuntado en el diario {dia(fecha)} · {subido}")
    except Exception as e:
        logger.exception("Error escribiendo un mensaje suelto en el diario")
        await responder_si_puedo(update, f"❌ Error: {e}")

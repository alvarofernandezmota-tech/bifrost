"""El bot habla sin que le hablen: avisa de una cita antes de que llegue.

Todo lo demás en bifrost contesta a algo. Esto es lo único que empieza la
conversación, y por eso es lo único que puede convertirse en spam: un bucle
que se equivoca aquí manda el mismo mensaje cada minuto hasta que alguien
para el bot.

Quién decide qué avisar es `diario/recordatorios.py`, con sus pruebas. Aquí
solo se pregunta cada poco, se manda, y **se anota después de mandar**: si
Telegram falla, la cita sigue pendiente y se reintenta a la vuelta
siguiente, en vez de darse por avisada sin que nadie la haya leído.

## Por qué un bucle de asyncio y no JobQueue

`python-telegram-bot` trae `JobQueue`, pero solo si se instala con el extra
`[job-queue]`, que arrastra APScheduler. Esto son veinte líneas de `asyncio`
sobre el bucle que el bot ya tiene corriendo, sin una dependencia más que
instalar en Madre.
"""

import asyncio
import logging

from telegram.ext import Application

from utils.auth import chats_autorizados
from utils.limites import recortar
from utils.midgaror import modulo

agenda = modulo("agenda")
recordatorios = modulo("recordatorios")

logger = logging.getLogger(__name__)

# Cada cuánto se mira la agenda. Un minuto es de sobra fino para una ventana
# de media hora, y es barato: leer un JSON pequeño.
CADA_SEGUNDOS = 60


def texto_del_aviso(cita: dict) -> str:
    return f"⏰ En un rato: {agenda.linea(cita)}"


async def avisar_una_vez(app: Application) -> int:
    """Mira la agenda y manda lo que toque. Devuelve cuántos avisos mandó.

    No lanza nunca: un fallo aquí no puede tirar el bucle que lo llama, o el
    bot se quedaría mudo para siempre sin que nada lo dijera.
    """
    try:
        pendientes = recordatorios.pendientes()
    except Exception:
        logger.exception("No se pudo mirar la agenda para los recordatorios")
        return 0
    if not pendientes:
        return 0

    chats = chats_autorizados()
    if not chats:
        # Sin ids no se sabe a quién avisar. El bot ya está cerrado por
        # defecto (utils/auth.py lo grita al arrancar); aquí solo se calla.
        return 0

    mandados = []
    for cita in pendientes:
        llego = False
        for chat in chats:
            try:
                await app.bot.send_message(chat, recortar(texto_del_aviso(cita)))
                llego = True
            except Exception:
                logger.exception("No se pudo avisar de la cita %s al chat %s",
                                 cita.get("id"), chat)
        if llego:
            mandados.append(cita)

    if mandados:
        # Anotar DESPUÉS de mandar, y solo lo que llegó a alguien.
        try:
            recordatorios.anotar(mandados)
        except Exception:
            # Si esto falla, el aviso se repetirá. Molesto, pero es el lado
            # bueno del fallo: lo contrario es no avisar de una cita.
            logger.exception("Avisos mandados pero no anotados: se repetirán")
    return len(mandados)


async def bucle(app: Application) -> None:
    """Pregunta cada CADA_SEGUNDOS, para siempre. Se lanza en post_init."""
    while True:
        await asyncio.sleep(CADA_SEGUNDOS)
        await avisar_una_vez(app)


def arrancar(app: Application) -> asyncio.Task:
    """Deja el bucle corriendo junto al bot. Devuelve la tarea, para pruebas."""
    logger.info("⏰ Recordatorios en marcha (cada %ds, ventana de %d min)",
                CADA_SEGUNDOS, recordatorios.VENTANA_MINUTOS)
    return asyncio.create_task(bucle(app))

"""Autorizacion del bot: quien puede darle ordenes.

Sin esto el bot obedece a cualquiera que lo encuentre, y este bot escribe en
el diario personal. La lista de chats autorizados sale de TELEGRAM_CHAT_ID en
el .env, separando por comas si hay varios.

Si la variable no esta puesta, el bot sigue respondiendo a todo el mundo, como
hasta ahora, pero avisa por el log al arrancar. Se deja asi a proposito para
no romper una instalacion existente al actualizar; el aviso es el que empuja a
configurarlo.

Los no autorizados no reciben respuesta. Es deliberado: contestarles confirma
que el bot existe y que estan hablando con algo vivo.
"""

import logging
import os

from telegram.ext import filters

logger = logging.getLogger(__name__)

VARIABLE = "TELEGRAM_CHAT_ID"


def chats_autorizados() -> list[int]:
    """Ids de chat que pueden usar el bot. Lista vacia = sin restriccion."""
    crudo = os.getenv(VARIABLE, "").strip()
    if not crudo:
        return []
    ids = []
    for trozo in crudo.split(","):
        trozo = trozo.strip()
        if not trozo:
            continue
        try:
            ids.append(int(trozo))
        except ValueError:
            logger.warning("%s: '%s' no es un id de chat valido, se ignora", VARIABLE, trozo)
    return ids


def filtro_autorizado():
    """Filtro para los CommandHandler, o None si no hay restriccion.

    Devolver None deja pasar a todo el mundo, que es el comportamiento previo.
    """
    ids = chats_autorizados()
    if not ids:
        logger.warning(
            "%s sin configurar: el bot responde a CUALQUIERA que le escriba. "
            "Pon tu id de chat en el .env para restringirlo.",
            VARIABLE,
        )
        return None
    logger.info("Autorizacion activa para %d chat(s)", len(ids))
    return filters.Chat(chat_id=ids)

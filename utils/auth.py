"""Funciones de autenticación y autorización del bot."""

import os
import logging
from telegram import Update

logger = logging.getLogger(__name__)

# Cargar chat autorizado desde entorno
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))


def verificar_chat_autorizado(update: Update) -> bool:
    """
    Verifica que el mensaje viene del chat autorizado.
    
    Args:
        update: Update de Telegram con el mensaje
        
    Returns:
        True si el chat está autorizado, False en caso contrario
    """
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        logger.warning(f"Chat no autorizado: {chat_id}")
        return False
    return True

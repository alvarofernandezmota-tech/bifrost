#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal."""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Importar handlers
from handlers.diario import comando_diario
from handlers.entrada import comando_entrada
from utils.auth import filtro_autorizado

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# httpx registra la URL completa de cada peticion a la API de Telegram, y esa
# URL lleva el token dentro. A nivel INFO eso escupe el token en cada sondeo,
# unas seis veces por minuto, a la terminal y a cualquier log que se guarde o
# se pegue en un chat. Silenciado a WARNING: los errores se siguen viendo.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    await update.message.reply_text(
        "👋 ¡Hola! Soy Bifrost, tu bot de diario personal.\n\n"
        "Comandos disponibles:\n"
        "/diario <texto> - Inserta texto en la entrada de hoy\n"
        "/entrada <fecha> <texto> - Crea/actualiza entrada para una fecha"
    )


async def comando_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Muestra ayuda."""
    await update.message.reply_text(
        "📖 **Ayuda de Bifrost**\n\n"
        "**/diario <texto>**\n"
        "Inserta texto en 'Qué ha pasado hoy' de la entrada de hoy.\n\n"
        "**/entrada <fecha> <texto>**\n"
        "Crea o actualiza una entrada para la fecha (YYYY-MM-DD).\n\n"
        "**/start** - Mensaje de bienvenida\n"
        "**/help** - Muestra esta ayuda"
    )


def main() -> None:
    """Inicia el bot de Telegram."""
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        raise ValueError("TELEGRAM_BOT_TOKEN no encontrado en .env")

    logger.info("✅ Iniciando bot de Telegram...")
    app = Application.builder().token(TOKEN).build()

    # Sin TELEGRAM_CHAT_ID en el .env esto es None y el bot responde a todos,
    # avisando por el log. Con el id puesto, los demas no reciben respuesta.
    autorizado = filtro_autorizado()

    app.add_handler(CommandHandler("start", comando_start, filters=autorizado))
    app.add_handler(CommandHandler("help", comando_help, filters=autorizado))
    app.add_handler(CommandHandler("diario", comando_diario, filters=autorizado))
    app.add_handler(CommandHandler("entrada", comando_entrada, filters=autorizado))

    logger.info("🤖 Bot en marcha. Escuchando comandos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

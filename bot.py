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

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
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

    app.add_handler(CommandHandler("start", comando_start))
    app.add_handler(CommandHandler("help", comando_help))
    app.add_handler(CommandHandler("diario", comando_diario))
    app.add_handler(CommandHandler("entrada", comando_entrada))

    logger.info("🤖 Bot en marcha. Escuchando comandos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

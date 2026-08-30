#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal.

Este es el punto de entrada principal del bot.
Importa los handlers desde el módulo handlers y los registra.
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Importar handlers desde módulos independientes
from handlers import (
    comando_inicio,
    comando_ayuda,
    comando_diario,
    comando_entrada,
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Inicia el bot de Telegram."""
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        raise ValueError("TELEGRAM_BOT_TOKEN no encontrado en .env")

    logger.info("✅ Iniciando bot de Telegram...")

    # Crear aplicación
    app = Application.builder().token(TOKEN).build()

    # Registrar handlers
    app.add_handler(CommandHandler("start", comando_inicio))
    app.add_handler(CommandHandler("help", comando_ayuda))
    app.add_handler(CommandHandler("diario", comando_diario))
    app.add_handler(CommandHandler("entrada", comando_entrada))

    # Iniciar polling
    logger.info("🤖 Bot en marcha. Escuchando comandos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal."""

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Importar handlers
from handlers.diario import comando_diario
from handlers.entrada import comando_entrada
from handlers.habito import comando_habito, comando_habitos
from handlers.hoy import comando_hoy
from handlers.tarea import comando_tarea, comando_tareas
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
        "👋 ¡Hola! Soy Bifrost.\n\n"
        "Escríbeme el día según pasa:\n"
        "/diario hoy he dormido fatal\n"
        "/tarea comprar el pan\n"
        "/habito deporte\n"
        "/hoy — el día de un vistazo\n\n"
        "/help para el resto."
    )


async def comando_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Muestra ayuda."""
    await update.message.reply_text(
        "📖 Ayuda de Bifrost\n\n"
        "Los ejemplos son literales: escribe lo que ves, sin < ni >.\n\n"
        "DIARIO\n"
        "/diario hoy he dormido fatal\n"
        "   añade el texto a «Qué ha pasado hoy», con la hora delante\n"
        "/entrada 2026-09-03 se me olvidó apuntar esto\n"
        "   lo mismo, en el día que digas (AAAA-MM-DD)\n\n"
        "TAREAS\n"
        "/tarea comprar el pan     apunta una tarea\n"
        "/tarea hecha 3            la marca hecha\n"
        "/tarea borrar 3           la retira\n"
        "/tareas                   las pendientes\n\n"
        "HÁBITOS\n"
        "/habito deporte           hecho hoy\n"
        "/habito no meditar        no hecho hoy\n"
        "/habito deporte 2026-09-03  en otro día\n"
        "/habitos                  los de hoy\n"
        "/habitos semana           la semana, con totales\n\n"
        "EL DÍA\n"
        "/hoy                      diario, tareas y hábitos juntos\n"
        "/hoy 2026-09-03           el de otro día\n\n"
        "Todo lo que escribes se guarda en tu repo y se sube a GitHub."
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
    app.add_handler(CommandHandler("tarea", comando_tarea, filters=autorizado))
    app.add_handler(CommandHandler("tareas", comando_tareas, filters=autorizado))
    app.add_handler(CommandHandler("habito", comando_habito, filters=autorizado))
    app.add_handler(CommandHandler("habitos", comando_habitos, filters=autorizado))
    app.add_handler(CommandHandler("hoy", comando_hoy, filters=autorizado))

    logger.info("🤖 Bot en marcha. Escuchando comandos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

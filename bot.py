#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("ERROR: Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env")
    sys.exit(1)

# Importar funciones del diario
from organizar_diario import organizar_texto
from bifrost_bridge importPerfecto, veo los dos scripts clave: `bifrost_bridge.py` y `organizar_diario.py`. Ahora te doy los comandos para:

1. Copiarlos a `bifrost`
2. Crear `bot.py` con el comando `/diario`
3. Commit y push en ambos repos

## Comandos para ejecutar en local

```bash
cd /home/varopc/GitHub/personal/midgaror

# 1. Copiar los scripts a bifrost
cp diario/bifrost_bridge.py proyectos/bifrost/
cp diario/organizar_diario.py proyectos/bifrost/

cd proyectos/bifrost

# 2. Crear bot.py
cat > bot.py << 'EOF'
#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importar funciones del diario
from organizar_diario import organizar_texto
from bifrost_bridge import escribir_entrada


def verificar_chat_autorizado(update: Update) -> bool:
    """Verifica que el mensaje viene del chat autorizado."""
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        logger.warning(f"Chat no autorizado: {chat_id}")
        return False
    return True


async def comando_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /diario <texto> - Inserta texto en la sección 'Qué ha pasado hoy' de la entrada de hoy.
    """
    if not verificar_chat_autorizado(update):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return

    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("❌ Uso: /diario <texto a registrar>")
        return

    try:
        ruta = organizar_texto(texto)
        await update.message.reply_text(f"✅ Texto guardado en: {ruta}")
    except Exception as e:
        logger.error(f"Error al organizar texto: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /entrada <fecha> <texto> - Crea o actualiza una entrada para una fecha específica.
    Ej: /entrada 2026-08-30 Hoy fue un gran día
    """
    if not verificar_chat_autorizado(update):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Uso: /entrada <YYYY-MM-DD> <texto>")
        return

    fecha = context.args
    texto = " ".join(context.args[1:])

    try:
        ruta = escribir_entrada(fecha, texto)
        await update.message.reply_text(f"✅ Entrada creada/actualizada en: {ruta}")
    except Exception as e:
        logger.error(f"Error al escribir entrada: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def comando_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    if not verificar_chat_autorizado(update):
        return

    await update.message.reply_text(
        "👋 ¡Hola! Soy Bifrost, tu bot de diario personal.\n\n"
        "Comandos disponibles:\n"
        "/diario <texto> - Inserta texto en la entrada de hoy\n"
        "/entrada <fecha> <texto> - Crea/actualiza entrada para una fecha\n"
        "/start - Muestra este mensaje"
    )


async def comando_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Muestra ayuda."""
    if not verificar_chat_autorizado(update):
        return

    await update.message.reply_text(
        "📖 **Ayuda de Bifrost**\n\n"
        "**/diario <texto>**\n"
        "Inserta texto en la sección 'Qué ha pasado hoy' de la entrada de hoy.\n\n"
        "**/entrada <fecha> <texto>**\n"
        "Crea o actualiza una entrada para la fecha especificada (YYYY-MM-DD).\n\n"
        "**/start** - Mensaje de bienvenida\n"
        "**/help** - Muestra esta ayuda"
    )


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

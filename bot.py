#!/usr/bin/env python3
"""Bot de Telegram para escribir en el diario personal."""

import logging
import os
from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Importar handlers
from handlers.cita import comando_agenda, comando_cita
from handlers.diario import comando_diario
from handlers.entrada import comando_entrada
from handlers.habito import comando_habito, comando_habitos
from handlers.hoy import comando_hoy
from handlers.tarea import comando_tarea, comando_tareas
from handlers.texto import mensaje_libre
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

# El menú de comandos de Telegram: lo que sale al pulsar el botón "/" en el
# chat. Se registra al arrancar con setMyCommands, así que la lista de aquí es
# la única fuente: si se añade un comando, se añade aquí y aparece solo.
MENU = [
    ("hoy", "El día de un vistazo"),
    ("diario", "Apunta algo en el diario de hoy"),
    ("entrada", "Apunta algo en otro día: /entrada 2026-09-03 texto"),
    ("tarea", "Apunta o cambia una tarea"),
    ("tareas", "Tus tareas abiertas"),
    ("cita", "Apunta una cita: /cita médico mañana a las 10"),
    ("agenda", "Tus citas de hoy o de la semana"),
    ("habito", "Apunta un hábito, o su valor del 1 al 10"),
    ("habitos", "Tus hábitos de hoy o de la semana"),
    ("help", "Cómo se usa cada comando"),
]


async def registrar_menu(app: Application) -> None:
    """Publica MENU en Telegram al arrancar (el botón «/» del chat).

    Si Telegram no contesta, el bot arranca igual: el menú es comodidad, y
    quedarse sin bot por no poder pintar una lista sería peor.
    """
    try:
        await app.bot.set_my_commands([BotCommand(c, d) for c, d in MENU])
        logger.info("✅ Menú de comandos registrado (%d comandos)", len(MENU))
    except Exception:
        logger.exception("No se pudo registrar el menú de comandos; el bot sigue")


async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    await update.message.reply_text(
        "👋 ¡Hola! Soy Bifrost.\n\n"
        "Escríbeme el día según pasa:\n"
        "/diario hoy he dormido fatal\n"
        "/tarea comprar el pan\n"
        "/cita médico mañana a las 10\n"
        "/habito deporte\n"
        "/hoy — el día de un vistazo\n\n"
        "O escribe sin más: lo que mandes sin comando va al diario de hoy.\n"
        "Pulsa «/» para ver todos los comandos, o /help para el detalle."
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
        "/tarea médico mañana a las 10  con fecha: la saca del texto\n"
        "/tarea empezar 3          la pone en proceso\n"
        "/tarea hecha 3            la marca hecha\n"
        "/tarea reabrir 3          la devuelve a pendiente\n"
        "/tarea editar 3 comprar pan y leche   le cambia el texto\n"
        "/tarea aplazar 3 el lunes por la tarde   le cambia la fecha\n"
        "/tarea borrar 3           la retira\n"
        "/tareas                   las abiertas y las últimas hechas\n\n"
        "CITAS\n"
        "Una cita siempre lleva cuándo; una tarea puede no llevarlo.\n"
        "/cita médico mañana a las 10   apunta una cita\n"
        "/cita dentista el 15 de octubre a las 17:30\n"
        "/cita mover 3 el lunes a las 17   la cambia de hora\n"
        "/cita cancelar 3          la retira\n"
        "/agenda                   las de hoy\n"
        "/agenda semana            los siete días desde hoy\n"
        "Si dos citas se pisan, se guarda igual y te avisa.\n\n"
        "HÁBITOS\n"
        "/habito deporte           hecho hoy\n"
        "/habito no meditar        no hecho hoy\n"
        "/habito energia 7         un valor del 1 al 10\n"
        "/habito deporte 2026-09-03  en otro día\n"
        "/habitos                  los de hoy\n"
        "/habitos semana           la semana, con totales y medias\n\n"
        "SIN COMANDO\n"
        "Escribe y ya: cualquier mensaje suelto se apunta en el diario de hoy,\n"
        "igual que /diario.\n\n"
        "EL DÍA\n"
        "/hoy                      diario, citas, tareas y hábitos juntos\n"
        "/hoy 2026-09-03           el de otro día\n\n"
        "Todo lo que escribes se guarda en tu repo y se sube a GitHub."
    )


def main() -> None:
    """Inicia el bot de Telegram."""
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        raise ValueError("TELEGRAM_BOT_TOKEN no encontrado en .env")

    logger.info("✅ Iniciando bot de Telegram...")
    app = Application.builder().token(TOKEN).post_init(registrar_menu).build()

    # Sin TELEGRAM_CHAT_ID en el .env esto es None y el bot responde a todos,
    # avisando por el log. Con el id puesto, los demas no reciben respuesta.
    autorizado = filtro_autorizado()

    app.add_handler(CommandHandler("start", comando_start, filters=autorizado))
    app.add_handler(CommandHandler("help", comando_help, filters=autorizado))
    app.add_handler(CommandHandler("diario", comando_diario, filters=autorizado))
    app.add_handler(CommandHandler("entrada", comando_entrada, filters=autorizado))
    app.add_handler(CommandHandler("tarea", comando_tarea, filters=autorizado))
    app.add_handler(CommandHandler("tareas", comando_tareas, filters=autorizado))
    app.add_handler(CommandHandler("cita", comando_cita, filters=autorizado))
    app.add_handler(CommandHandler("agenda", comando_agenda, filters=autorizado))
    app.add_handler(CommandHandler("habito", comando_habito, filters=autorizado))
    app.add_handler(CommandHandler("habitos", comando_habitos, filters=autorizado))
    app.add_handler(CommandHandler("hoy", comando_hoy, filters=autorizado))

    # El ultimo: cualquier texto que no sea un comando va al diario de hoy.
    solo_texto = filters.TEXT & ~filters.COMMAND
    if autorizado:
        solo_texto &= autorizado
    app.add_handler(MessageHandler(solo_texto, mensaje_libre))

    logger.info("🤖 Bot en marcha. Escuchando comandos...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

"""Dobles de prueba: un Telegram de mentira y un diario en un temporal.

Los handlers importan `telegram` al cargarse, así que el paquete falso se
instala en sys.modules **antes** de importarlos: por eso este módulo se
importa el primero en cada fichero de pruebas.

Se hace así a propósito, y no instalando python-telegram-bot:

- Lo que hay que probar es *nuestro* código, no el de la librería.
- Las pruebas corren en cualquier sitio, sin red y sin dependencias.
- Y sobre todo: así se puede simular lo que Telegram hace de verdad, como
  mandar un mensaje que empieza por "/" **sin** marcarlo como bot_command.
  Eso es exactamente lo que rompió el bot el 2026-09-05.
"""

import asyncio
import contextlib
import io
import logging
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

BIFROST = Path(__file__).resolve().parent.parent
if str(BIFROST) not in sys.path:
    sys.path.insert(0, str(BIFROST))

# De aquí sale DIARIO y, al importarlo, las rutas de los módulos de midgaror.
# Antes esto estaba repetido aquí y en los ocho handlers; ahora lo pone
# utils/midgaror.py, y las pruebas usan el mismo camino que el bot de verdad.
from utils.midgaror import DIARIO  # noqa: E402 (necesita BIFROST en sys.path)


def _instalar_telegram_falso() -> None:
    """Un `telegram` mínimo, suficiente para importar los handlers."""
    if "telegram" in sys.modules and getattr(sys.modules["telegram"], "_es_doble", False):
        return
    tg = types.ModuleType("telegram")
    tg._es_doble = True
    tg.Update = object
    tg.BotCommand = lambda comando, descripcion: (comando, descripcion)
    ext = types.ModuleType("telegram.ext")

    class ContextTypes:
        DEFAULT_TYPE = object

    ext.ContextTypes = ContextTypes
    ext.Application = ext.CommandHandler = ext.MessageHandler = object
    ext.CallbackQueryHandler = object

    # Lo que usa el menú de botones (handlers/menu.py). Guardan lo que se les
    # pasa y nada más: lo que se prueba es que el bot construye el teclado y
    # la pregunta que toca, no que Telegram los pinte.
    class ForceReply:
        def __init__(self, selective=None, input_field_placeholder=None):
            self.selective = selective
            self.input_field_placeholder = input_field_placeholder

    class InlineKeyboardButton:
        def __init__(self, text, callback_data=None, **kwargs):
            self.text = text
            self.callback_data = callback_data

    class InlineKeyboardMarkup:
        def __init__(self, inline_keyboard):
            self.inline_keyboard = inline_keyboard

    tg.ForceReply, tg.InlineKeyboardButton = ForceReply, InlineKeyboardButton
    tg.InlineKeyboardMarkup = InlineKeyboardMarkup

    # `filters` era `object`, asi que `filters.Chat` no existia y utils/auth.py
    # ni siquiera se podia importar en las pruebas. Aqui es un modulo de verdad
    # con lo unico que usamos: un Chat que se limita a guardar los ids. Lo que
    # esta en nuestra mano es comprobar que el filtro se construye con los ids
    # correctos; que Telegram luego lo aplique bien es cosa de la libreria.
    filtros = types.ModuleType("telegram.ext.filters")

    class Chat:
        def __init__(self, chat_id):
            self.chat_id = chat_id

    filtros.Chat = Chat
    ext.filters = filtros
    sys.modules["telegram"], sys.modules["telegram.ext"] = tg, ext
    sys.modules["telegram.ext.filters"] = filtros


_instalar_telegram_falso()


# El codigo de produccion escribe en el log y en stdout a proposito (esa
# traza es la que permitio diagnosticar el bug del 2026-09-05). En las
# pruebas solo es ruido, y esconde el fallo de verdad entre lineas.
logging.disable(logging.CRITICAL)


@contextlib.contextmanager
def logs_visibles():
    """Vuelve a encender el log dentro del `with`.

    Con el `logging.disable` de arriba puesto, un `logger.warning()` no
    llega a crear ningun registro: `assertNoLogs` pasa siempre aunque el
    aviso este ahi, y `assertLogs` falla siempre aunque lo este tambien.
    Las dos comprobaciones mienten, y una de ellas miente en verde. Las
    pruebas que miran avisos tienen que envolverse en esto.
    """
    logging.disable(logging.NOTSET)
    try:
        yield
    finally:
        logging.disable(logging.CRITICAL)


class Entidad:
    """Una entidad de mensaje de Telegram: 'bot_command', 'code'…"""

    def __init__(self, tipo: str):
        self.type = tipo


class DemasiadoLargo(Exception):
    """Lo que devuelve Telegram cuando el mensaje pasa de 4096: BadRequest."""


class Mensaje:
    def __init__(self, texto: str = "", entidades=None, responde_a=None):
        self.text = texto
        self.entities = entidades or []
        self.reply_to_message = responde_a
        self.respuestas: list[str] = []
        self.marcados: list = []  # el reply_markup de cada respuesta; None si no llevaba

    async def reply_text(self, texto: str, reply_markup=None) -> None:
        # Telegram cuenta unidades UTF-16, no caracteres de Python: '📅' es
        # 1 para len() y 2 para Telegram. Un doble que no lo mida así deja
        # pasar mensajes que en producción se rechazan.
        if len(texto.encode("utf-16-le")) // 2 > 4096:
            raise DemasiadoLargo("Message is too long")
        self.respuestas.append(texto)
        self.marcados.append(reply_markup)


class Chat:
    def __init__(self, id_chat: int):
        self.id = id_chat


class Consulta:
    """Un callback_query: lo que llega al tocar un botón del menú."""

    def __init__(self, data: str, mensaje: "Mensaje"):
        self.data = data
        self.message = mensaje  # el mensaje del menú, que es del bot
        self.respondida = False

    async def answer(self) -> None:
        self.respondida = True


class Actualizacion:
    def __init__(self, texto: str = "", entidades=None, responde_a=None,
                 boton: str | None = None, chat_id: int = 1):
        self.effective_chat = Chat(chat_id)
        if boton is None:
            self.message = Mensaje(texto, entidades, responde_a)
            self.callback_query = None
        else:
            # Al tocar un botón no hay `message`: Telegram manda un
            # callback_query cuyo `message` es el del menú. Igual que en la
            # librería, `effective_message` es el que haya.
            self.message = None
            self.callback_query = Consulta(boton, Mensaje())

    @property
    def effective_message(self) -> "Mensaje":
        return self.message if self.message is not None else self.callback_query.message


class Contexto:
    def __init__(self, *args: str):
        self.args = list(args)


class CasoBot(unittest.TestCase):
    """Base de las pruebas de handlers: datos en un temporal, sin git ni red.

    Cada prueba arranca con el diario y los tres JSON vacíos, así que el
    orden en que corren no cambia el resultado.
    """

    def setUp(self):
        import agenda
        import habitos
        import organizar_diario
        import tareas
        from handlers import cita, diario, entrada, habito, secciones, tarea, texto

        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.base = base

        tareas.RUTA_DATOS = base / "tareas.json"
        agenda.RUTA_DATOS = base / "agenda.json"
        habitos.RUTA_DATOS = base / "habitos.json"
        self.tareas, self.agenda, self.habitos = tareas, agenda, habitos

        # La entrada del día, desde la plantilla real: si la plantilla cambia
        # y rompe las secciones, estas pruebas lo dicen.
        self.hoy = "2026-09-05"
        self.entrada = base / f"{self.hoy}.md"
        plantilla = (DIARIO / "plantilla.md").read_text(encoding="utf-8")
        self.entrada.write_text(plantilla.replace("{{FECHA}}", self.hoy), encoding="utf-8")

        import bifrost_bridge
        for modulo in (organizar_diario, bifrost_bridge):
            modulo.ruta_de_hoy = lambda: self.entrada
            modulo.ruta_de_fecha = lambda fecha: base / f"{fecha}.md"
        self.od = organizar_diario

        # handlers/menu.py comprueba el chat contra TELEGRAM_CHAT_ID. Se fija
        # al chat de las pruebas (el 1, que es el de `Actualizacion`) para que
        # no dependan del entorno de la máquina. Vacío ya no vale: desde el
        # 2026-09-08 el bot está cerrado por defecto, así que sin ids no
        # pasaría nadie y todas las pruebas de botones quedarían mudas.
        self._entorno = mock.patch.dict(os.environ, {"TELEGRAM_CHAT_ID": "1"})
        self._entorno.start()
        self.addCleanup(self._entorno.stop)

        # sincronizar() haria git commit y git push de verdad. Si algun
        # handler se queda fuera de esta lista, su prueba falla con el aviso
        # de "esta fuera del repo": la red no se toca ni por accidente.
        for modulo in (cita, diario, entrada, habito, secciones, tarea, texto):
            modulo.sincronizar = lambda *a, **k: "escrito y subido a GitHub"

    def tearDown(self):
        self._tmp.cleanup()

    # ---- utilidades ----

    @staticmethod
    def _correr(corrutina) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            asyncio.run(corrutina)

    def enviar(self, handler, *args: str) -> str:
        """Manda un comando con sus argumentos y devuelve lo que contesta."""
        upd = Actualizacion()
        self._correr(handler(upd, Contexto(*args)))
        return upd.message.respuestas[-1] if upd.message.respuestas else ""

    def texto_libre(self, texto: str, entidades=None) -> str:
        """Manda un mensaje sin comando (o que Telegram no marcó como tal)."""
        from handlers.texto import mensaje_libre
        upd = Actualizacion(texto, entidades)
        self._correr(mensaje_libre(upd, None))
        return upd.message.respuestas[-1] if upd.message.respuestas else ""

    @staticmethod
    def _contexto_sin_args() -> Contexto:
        # Un botón o una respuesta no traen argumentos: en la librería
        # context.args es None, no []. Si un handler hace list(None), aquí
        # revienta igual que revientaría en producción.
        ctx = Contexto()
        ctx.args = None
        return ctx

    def pulsar(self, boton: str, chat_id: int = 1) -> Actualizacion:
        """Toca un botón del menú y devuelve la actualización, para mirar
        qué contestó el bot sobre el mensaje del menú."""
        from handlers.menu import boton as pulsado
        upd = Actualizacion(boton=boton, chat_id=chat_id)
        self._correr(pulsado(upd, self._contexto_sin_args()))
        return upd

    def contestar(self, pregunta: str, texto: str) -> str:
        """Responde con `texto` a un mensaje del bot que decía `pregunta`."""
        from handlers.menu import respuesta_al_menu
        upd = Actualizacion(texto, responde_a=Mensaje(pregunta))
        self._correr(respuesta_al_menu(upd, self._contexto_sin_args()))
        return upd.message.respuestas[-1] if upd.message.respuestas else ""

    def seccion(self, titulo: str, ruta: Path | None = None) -> str:
        """El cuerpo de una sección de la entrada, sin su título."""
        contenido = (ruta or self.entrada).read_text(encoding="utf-8")
        if titulo not in contenido:
            return ""
        cuerpo = contenido.split(titulo, 1)[1]
        fin = cuerpo.find("\n## ")
        return (cuerpo if fin == -1 else cuerpo[:fin]).strip()

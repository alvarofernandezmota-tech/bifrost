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
import sys
import tempfile
import types
import unittest
from pathlib import Path

BIFROST = Path(__file__).resolve().parent.parent
MIDGAROR = BIFROST.parent.parent
DIARIO = MIDGAROR / "diario"


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
    ext.Application = ext.CommandHandler = ext.MessageHandler = ext.filters = object
    sys.modules["telegram"], sys.modules["telegram.ext"] = tg, ext


_instalar_telegram_falso()
for ruta in (str(BIFROST), str(DIARIO), str(DIARIO / "tareas"),
             str(DIARIO / "agenda"), str(DIARIO / "habitos")):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)


# El codigo de produccion escribe en el log y en stdout a proposito (esa
# traza es la que permitio diagnosticar el bug del 2026-09-05). En las
# pruebas solo es ruido, y esconde el fallo de verdad entre lineas.
logging.disable(logging.CRITICAL)


class Entidad:
    """Una entidad de mensaje de Telegram: 'bot_command', 'code'…"""

    def __init__(self, tipo: str):
        self.type = tipo


class Mensaje:
    def __init__(self, texto: str = "", entidades=None):
        self.text = texto
        self.entities = entidades or []
        self.respuestas: list[str] = []

    async def reply_text(self, texto: str) -> None:
        self.respuestas.append(texto)


class Actualizacion:
    def __init__(self, texto: str = "", entidades=None):
        self.message = Mensaje(texto, entidades)


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

    def seccion(self, titulo: str, ruta: Path | None = None) -> str:
        """El cuerpo de una sección de la entrada, sin su título."""
        contenido = (ruta or self.entrada).read_text(encoding="utf-8")
        if titulo not in contenido:
            return ""
        cuerpo = contenido.split(titulo, 1)[1]
        fin = cuerpo.find("\n## ")
        return (cuerpo if fin == -1 else cuerpo[:fin]).strip()

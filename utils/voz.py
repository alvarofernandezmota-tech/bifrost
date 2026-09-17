"""La oreja de bifrost: una nota de voz de Telegram, convertida en texto.

Con Whisper **en local**, por `faster-whisper`. Por aquí pasa lo que dictas a
tu propio diario — mandarlo a una API de terceros es justo lo que se quiere
evitar, y es la misma razón por la que `telefono/voz.py` en gjallarhorn hace
lo mismo para las llamadas.

Bifrost no importa ese módulo: son repos independientes a propósito (el
ADR-019 de midgaror va justo en el sentido contrario — hugin no sabe que
gjallarhorn existe, y bifrost tampoco tiene por qué saber que gjallarhorn
existe). Esto es una copia pequeña y propia del mismo patrón probado —
Whisper detrás de una interfaz de una sola función, con el import dentro
para no pagar el coste de cargar `faster_whisper` en cuanto se importa el
módulo—, no un import cruzado entre proyectos.

    from utils.voz import Whisper, escuchar
    escuchar(Path("nota.oga"), Whisper())

En las pruebas se usa un `TranscriptorFalso`, que devuelve lo que se le diga.
Lo que se prueba ahí no es Whisper —eso es de Whisper—, es que la tubería de
encima haga lo correcto con lo que oye.
"""

import sys
from pathlib import Path
from typing import Protocol

# Español. Forzarlo evita que una frase corta —«vale», «hecho»— se detecte
# como portugués o gallego, que es el fallo típico de estos modelos.
IDIOMA = "es"

# `small` es el equilibrio razonable en una máquina sin GPU: mismo modelo que
# usa gjallarhorn, medido ya contra el hardware de Madre en telefono/voz.py.
MODELO_POR_DEFECTO = "small"


class Transcriptor(Protocol):
    """Cualquier cosa que convierta un fichero de audio en texto."""

    def transcribir(self, audio: Path) -> str:
        ...


class Whisper:
    """Whisper en local, por `faster-whisper`.

    El import va dentro y no arriba a propósito: `faster_whisper` arrastra
    `ctranslate2` y descarga el modelo la primera vez. Importarlo al cargar
    el módulo haría que las pruebas —y cualquiera que arranque el bot sin
    haber activado la voz— pagaran eso sin usarlo.
    """

    def __init__(self, modelo: str = MODELO_POR_DEFECTO, idioma: str = IDIOMA):
        self.modelo = modelo
        self.idioma = idioma
        self._motor = None

    def _cargar(self):
        if self._motor is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as error:
                raise RuntimeError(self._por_que_no_carga(error)) from error
            # int8 en CPU: es lo que hace esto viable sin GPU.
            self._motor = WhisperModel(self.modelo, device="cpu", compute_type="int8")
        return self._motor

    @staticmethod
    def _por_que_no_carga(error: ImportError) -> str:
        """El mensaje de «no carga», diciendo cuál de las dos cosas pasa.

        `faster_whisper` arrastra `ctranslate2`, `onnxruntime`, `av` y
        `tokenizers`, todos compilados. Si cualquiera de ellos revienta al
        importarse —una ABI que no cuadra, una .so que falta—, lo que sale
        es un `ImportError` **que no es el de faster-whisper**.

        Este mensaje decía «falta faster-whisper, instálalo» en los dos
        casos, y eso pasó de verdad en Madre el 2026-09-17: el paquete
        estaba instalado en el venv correcto y el bot seguía pidiendo que
        se instalara. Media hora persiguiendo un fantasma, porque el aviso
        hablaba del paquete que sí estaba.

        Ahora se distingue por el nombre del módulo que falló, y en los dos
        casos va el error de verdad detrás: el que no se puede leer es el
        que no se puede arreglar.
        """
        culpable = (getattr(error, "name", "") or "").split(".")[0]
        if culpable in ("", "faster_whisper"):
            return (
                "falta faster-whisper para este Python. Instálalo con el "
                "pip de ESTE intérprete, que no tiene por qué ser el que "
                f"contesta a `pip`:\n      {sys.executable} -m pip install "
                f"faster-whisper\n\n(el error tal cual: {error})")
        return (
            f"faster-whisper está instalado, pero no puede cargar: {error}\n\n"
            f"El que falla es «{culpable}», no faster-whisper. Suele ser una "
            "versión compilada que no cuadra con este Python. Para verlo "
            f"entero:\n      {sys.executable} -c \"import {culpable}\"")

    def transcribir(self, audio: Path) -> str:
        if not audio.exists():
            raise FileNotFoundError(f"no existe el audio: {audio}")
        segmentos, _ = self._cargar().transcribe(str(audio), language=self.idioma)
        return " ".join(s.text.strip() for s in segmentos).strip()


class TranscriptorFalso:
    """Devuelve lo que se le diga. Para probar lo de encima de la oreja."""

    def __init__(self, *frases: str):
        self.frases = list(frases)
        self.oidos: list[Path] = []

    def transcribir(self, audio: Path) -> str:
        self.oidos.append(audio)
        return self.frases.pop(0) if self.frases else ""


def escuchar(audio: Path, transcriptor: Transcriptor) -> str:
    """El texto de un audio, limpio de espacios. Cadena vacía si no se oyó nada."""
    return (transcriptor.transcribir(Path(audio)) or "").strip()

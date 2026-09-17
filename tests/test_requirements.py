"""Pruebas de requirements.txt: que declare lo que hace falta de verdad.

Sale de un fallo en Madre el 2026-09-17: `pip install -r requirements.txt`
terminó con «Successfully installed faster-whisper-1.1.1» y la primera nota
de voz murió con `ModuleNotFoundError: No module named 'requests'`.

faster-whisper hace `import requests` en `utils.py` y **no lo declara**. Se
lo traía `huggingface-hub` de rebote, y la 1.x se pasó a `httpx`. Resultado:
una instalación que dice que fue bien y un fallo en tiempo de uso hablando de
un paquete que nadie había pedido.
"""

import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

# Lo que faster-whisper importa y NO declara en su metadata. Medido leyendo
# los imports del wheel 1.1.1, no de memoria.
NO_DECLARADOS_POR_FASTER_WHISPER = ("requests",)


def paquetes() -> dict:
    """{nombre: versión} de requirements.txt, sin comentarios ni huecos."""
    fijados = {}
    for linea in (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if (m := re.match(r"^([A-Za-z0-9._-]+)==(.+)$", linea)):
            fijados[m.group(1).lower()] = m.group(2)
    return fijados


class TestLoQueSeDeclara(unittest.TestCase):
    def test_todo_va_con_version_fijada(self):
        # El fichero lo dice en su cabecera: sin fijar, un pip install en el
        # momento equivocado deja el bot sin arrancar.
        sueltos = [ln.strip() for ln in
                   (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.strip().startswith("#") and "==" not in ln]
        self.assertEqual(sueltos, [])

    def test_estan_las_que_importa_el_bot(self):
        fijados = paquetes()
        for paquete in ("python-telegram-bot", "python-dotenv"):
            with self.subTest(paquete=paquete):
                self.assertIn(paquete, fijados)

    def test_lo_que_faster_whisper_importa_y_no_declara_esta_aqui(self):
        # La regresión de Madre. Si algún día se sube faster-whisper y ya lo
        # declara, esta prueba no estorba: seguirá estando y de sobra.
        fijados = paquetes()
        if "faster-whisper" not in fijados:
            self.skipTest("sin faster-whisper no hay nada que completar")
        for paquete in NO_DECLARADOS_POR_FASTER_WHISPER:
            with self.subTest(paquete=paquete):
                self.assertIn(paquete, fijados,
                              f"faster-whisper importa {paquete} y no lo declara: "
                              "se instala «bien» y revienta al primer uso")


if __name__ == "__main__":
    unittest.main()


class TestLaPlantillaDelEnv(unittest.TestCase):
    """.env.example tiene que nombrar TODAS las variables que el bot lee.

    Hasta el 2026-09-18 documentaba dos y el codigo leia cuatro. La que
    faltaba era `ANTHROPIC_API_KEY`, que es justo la que enciende que el bot
    entienda lo que le escribes — y la mas facil de olvidar, porque sin ella
    no falla nada: simplemente no pasa nada.
    """

    def variables_de_la_plantilla(self) -> set:
        texto = (RAIZ / ".env.example").read_text(encoding="utf-8")
        return {ln.split("=")[0].strip() for ln in texto.splitlines()
                if "=" in ln and not ln.strip().startswith("#")}

    def test_estan_las_dos_obligatorias(self):
        for variable in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            with self.subTest(variable=variable):
                self.assertIn(variable, self.variables_de_la_plantilla())

    def test_esta_la_que_enciende_entender(self):
        self.assertIn("ANTHROPIC_API_KEY", self.variables_de_la_plantilla())

    def test_la_plantilla_no_lleva_ningun_valor_de_verdad(self):
        # Una plantilla con una clave dentro es una clave publicada.
        texto = (RAIZ / ".env.example").read_text(encoding="utf-8")
        for pista in ("sk-ant-", "sk-or-v1-", ":AA"):
            with self.subTest(pista=pista):
                self.assertNotIn(pista, texto)

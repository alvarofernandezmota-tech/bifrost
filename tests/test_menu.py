"""Pruebas del menú y del registro de comandos de bot.py.

No arrancan el bot: leen bot.py con `ast`. Lo que se comprueba es que el
menú de «/» y los CommandHandler registrados no se separen, que es el fallo
que se cuela solo — se añade un comando y se olvida el menú, o al revés.
"""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dobles  # noqa: F401, E402  (instala el telegram falso antes de importar bot)

import bot  # noqa: E402

BOT_PY = Path(bot.__file__)
# /start no va en el menú a propósito: Telegram ya lo ofrece al abrir el chat.
FUERA_DEL_MENU = {"start"}


def comandos_registrados() -> list[str]:
    """Los CommandHandler("x", ...) de bot.py, en orden de registro."""
    arbol = ast.parse(BOT_PY.read_text(encoding="utf-8"))
    nombres = []
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call)
                and isinstance(nodo.func, ast.Name)
                and nodo.func.id == "CommandHandler"
                and nodo.args
                and isinstance(nodo.args[0], ast.Constant)):
            nombres.append(nodo.args[0].value)
    return nombres


class TestMenu(unittest.TestCase):
    def setUp(self):
        self.menu = [comando for comando, _ in bot.MENU]
        self.registrados = comandos_registrados()

    def test_todo_lo_del_menu_tiene_un_handler(self):
        self.assertEqual([c for c in self.menu if c not in self.registrados], [],
                         "están en MENU pero no se registran: el botón / los enseña y no hacen nada")

    def test_todo_handler_esta_en_el_menu(self):
        sobran = [c for c in self.registrados if c not in self.menu and c not in FUERA_DEL_MENU]
        self.assertEqual(sobran, [],
                         "se registran pero no están en MENU: existen y nadie los ve")

    def test_no_hay_comandos_repetidos(self):
        self.assertEqual(len(self.menu), len(set(self.menu)))
        self.assertEqual(len(self.registrados), len(set(self.registrados)))

    def test_los_nombres_valen_para_telegram(self):
        # Telegram solo admite a-z, 0-9 y _ (por eso /plan y no /mañana): con
        # otra cosa el mensaje no llega marcado como comando.
        for comando in self.menu:
            self.assertRegex(comando, r"^[a-z0-9_]{1,32}$")

    def test_cada_comando_del_menu_se_explica(self):
        for comando, descripcion in bot.MENU:
            self.assertTrue(descripcion.strip(), f"/{comando} sin descripción")
            self.assertLessEqual(len(descripcion), 256, f"/{comando}: descripción muy larga")

    def test_el_texto_libre_se_registra_el_ultimo(self):
        # Si no, se comería los comandos registrados después.
        fuente = BOT_PY.read_text(encoding="utf-8")
        ultimo_comando = fuente.rfind('CommandHandler("')
        mensaje = fuente.find("MessageHandler(solo_texto")
        self.assertGreater(mensaje, ultimo_comando,
                           "MessageHandler debe registrarse después de todos los CommandHandler")

    def test_la_ayuda_menciona_todos_los_comandos(self):
        import inspect
        ayuda = inspect.getsource(bot.comando_help)
        olvidados = [c for c in self.menu if c != "help" and f"/{c}" not in ayuda]
        self.assertEqual(olvidados, [], "en el menú pero sin explicar en /help")


if __name__ == "__main__":
    unittest.main()

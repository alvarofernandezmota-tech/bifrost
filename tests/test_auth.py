"""Pruebas de utils/auth.py: quién puede darle órdenes al bot.

Esto no es un detalle de comodidad: el bot escribe en el diario personal,
así que un fallo aquí no es «responde de más», es que un desconocido escribe
en el diario de Álvaro.

Todo se prueba sobre `TELEGRAM_CHAT_ID` puesto a mano en el entorno de cada
prueba, nunca sobre el `.env` real: las pruebas no dependen de cómo esté
configurada la máquina donde corren.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dobles import logs_visibles  # noqa: E402  (instala el telegram falso)

from telegram.ext import filters  # noqa: E402  (el falso de dobles.py)
from utils.auth import VARIABLE, chats_autorizados, filtro_autorizado  # noqa: E402


def con_variable(valor):
    """El entorno con TELEGRAM_CHAT_ID a `valor`, o sin ella si es None."""
    if valor is None:
        return mock.patch.dict(os.environ, {}, clear=True)
    return mock.patch.dict(os.environ, {VARIABLE: valor})


class TestChatsAutorizados(unittest.TestCase):
    def test_sin_la_variable_no_hay_restriccion(self):
        with con_variable(None):
            self.assertEqual(chats_autorizados(), [])

    def test_la_variable_vacia_es_lo_mismo_que_no_tenerla(self):
        # El .env.example la trae puesta y vacía: sin esto, un `.env` recién
        # copiado daría una lista rota en vez de «sin restricción».
        for vacia in ("", "   ", "\n"):
            with self.subTest(valor=repr(vacia)), con_variable(vacia):
                self.assertEqual(chats_autorizados(), [])

    def test_un_solo_id(self):
        with con_variable("123456789"):
            self.assertEqual(chats_autorizados(), [123456789])

    def test_varios_ids_con_espacios_alrededor(self):
        # Copiar y pegar ids de Telegram deja espacios detrás de las comas.
        with con_variable(" 111 , 222,333 "):
            self.assertEqual(chats_autorizados(), [111, 222, 333])

    def test_un_id_negativo_es_valido(self):
        # Los grupos y canales de Telegram tienen id negativo. Si se colara
        # un `isdigit()` en vez del `int()`, esto lo cazaría.
        with con_variable("-1001234567890"):
            self.assertEqual(chats_autorizados(), [-1001234567890])

    def test_un_trozo_no_numerico_se_ignora_y_avisa(self):
        with logs_visibles(), con_variable("111,@alvaro,222"):
            with self.assertLogs("utils.auth", level="WARNING") as registro:
                ids = chats_autorizados()
        self.assertEqual(ids, [111, 222])
        # El aviso tiene que decir *cuál* es el trozo malo: si solo dijera
        # «hay un id inválido», con cinco ids en la variable no serviría.
        self.assertIn("@alvaro", "\n".join(registro.output))

    def test_las_comas_de_mas_no_avisan_de_nada(self):
        # "111,,222" y "111,222," son erratas al editar el .env, no ids
        # inválidos: se saltan en silencio.
        with logs_visibles(), con_variable("111,,222,"):
            with self.assertNoLogs("utils.auth", level="WARNING"):
                ids = chats_autorizados()
        self.assertEqual(ids, [111, 222])


class TestFiltroAutorizado(unittest.TestCase):
    def test_sin_ids_no_hay_filtro_pero_avisa_a_gritos(self):
        # Devolver None deja pasar a cualquiera. Es deliberado (no romper una
        # instalación que ya estaba funcionando al actualizar), y por eso el
        # aviso es lo único que empuja a configurarlo: si el aviso se pierde,
        # el bot se queda abierto y nadie se entera.
        with logs_visibles(), con_variable(""):
            with self.assertLogs("utils.auth", level="WARNING") as registro:
                filtro = filtro_autorizado()
        self.assertIsNone(filtro)
        self.assertIn(VARIABLE, "\n".join(registro.output))

    def test_con_ids_devuelve_un_filtro_de_chat_con_esos_ids(self):
        # filters.Chat autoriza **chats, no personas**: si el id es el de un
        # grupo, cualquiera de ese grupo puede mandar al bot. Autorizar el
        # chat privado de uno mismo es lo único que autoriza a una persona.
        with con_variable("111,222"):
            filtro = filtro_autorizado()
        self.assertIsInstance(filtro, filters.Chat)
        self.assertEqual(filtro.chat_id, [111, 222])

    def test_con_ids_no_avisa(self):
        # El aviso del caso anterior es util porque es raro. Si saltara
        # tambien con la autorizacion bien puesta, se volveria ruido de
        # arranque y dejaria de leerse.
        with logs_visibles(), con_variable("111"):
            with self.assertNoLogs("utils.auth", level="WARNING"):
                filtro = filtro_autorizado()
        self.assertIsNotNone(filtro)


if __name__ == "__main__":
    unittest.main()

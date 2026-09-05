"""Pruebas de handlers/habito.py."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dobles import CasoBot  # noqa: E402  (instala el telegram falso)

from handlers.habito import comando_habito, comando_habitos  # noqa: E402


class TestHabito(CasoBot):
    def test_hecho_y_no_hecho(self):
        self.assertEqual(self.enviar(comando_habito, "deporte", "2026-09-05"),
                         "✅ deporte — 2026-09-05 · subido")
        self.assertEqual(self.enviar(comando_habito, "no", "meditar", "2026-09-05"),
                         "❌ meditar — 2026-09-05 · subido")

    def test_valor_del_uno_al_diez(self):
        self.assertEqual(self.enviar(comando_habito, "energia", "7", "2026-09-05"),
                         "7 energia — 2026-09-05 · subido")

    def test_valor_y_fecha_a_la_vez(self):
        self.assertIn("6 foco — 2026-09-04", self.enviar(comando_habito, "foco", "6", "2026-09-04"))

    def test_el_numero_y_el_si_o_no_conviven_en_los_totales(self):
        self.enviar(comando_habito, "deporte", "2026-09-05")
        self.enviar(comando_habito, "energia", "7", "2026-09-05")
        self.enviar(comando_habito, "energia", "9", "2026-09-04")
        semana = self.enviar(comando_habitos, "semana", "2026-09-05")
        self.assertIn("energia: media 8.0 en 2 de 7 días", semana)
        self.assertIn("deporte: 1/1 días apuntados", semana)

    def test_resumen_de_un_dia(self):
        self.enviar(comando_habito, "deporte", "2026-09-05")
        self.enviar(comando_habito, "energia", "7", "2026-09-05")
        r = self.enviar(comando_habitos, "2026-09-05")
        self.assertIn("✅ deporte", r)
        self.assertIn("7 energia", r)

    def test_un_dia_sin_habitos_lo_dice(self):
        self.assertIn("Sin hábitos apuntados", self.enviar(comando_habitos, "2026-09-05"))

    def test_sin_argumentos_enseña_la_ayuda(self):
        self.assertIn("❌ Uso:", self.enviar(comando_habito))
        self.assertIn("❌ Uso:", self.enviar(comando_habito, "no"))

    def test_valor_fuera_de_rango_no_toca_el_fichero(self):
        self.assertIn("valor fuera de rango: 77", self.enviar(comando_habito, "energia", "77"))
        self.assertEqual(self.habitos.cargar(), {})

    def test_nombre_no_valido(self):
        self.assertIn("nombre de hábito no válido", self.enviar(comando_habito, "x!y"))

    def test_fecha_no_valida(self):
        self.assertIn("fecha no válida", self.enviar(comando_habito, "deporte", "ayer"))


if __name__ == "__main__":
    unittest.main()

"""Módulo core con la lógica del diario."""

from core.organizar import organizar_texto
from core.bridge import escribir_entrada
from core.diario import ruta_de_hoy, crear_desde_plantilla

__all__ = [
    "organizar_texto",
    "escribir_entrada",
    "ruta_de_hoy",
    "crear_desde_plantilla",
]

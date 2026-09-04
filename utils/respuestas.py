"""Cómo se le contesta al usuario.

`diario/sincronizar.py` devuelve frases pensadas para la terminal ("escrito y
subido a GitHub", "⚠️ commiteado en local, sin subir: …"). En el móvil, la
mitad de eso es ruido: cuando todo va bien basta con saber que se subió, y
cuando algo falla hace falta el aviso entero.
"""


def breve(mensaje_sincronizar: str) -> str:
    """Una coletilla corta si fue bien; el aviso completo si no."""
    if mensaje_sincronizar.startswith("⚠️"):
        return mensaje_sincronizar
    if "sin cambios" in mensaje_sincronizar:
        return "sin cambios que subir"
    if "reordenar" in mensaje_sincronizar:
        return "subido (había cambios nuevos en GitHub)"
    return "subido"

"""Puente diario <-> bifrost (bot de Telegram). Ver README.md de esta carpeta."""

import sys
from datetime import datetime
from pathlib import Path

from diario import ruta_de_hoy, crear_desde_plantilla


def escribir_entrada(texto: str) -> Path:
    """Guarda o actualiza la entrada de hoy, añadiendo texto al final sin borrar lo existente.

    Usado por bifrost (bot de Telegram) para escribir directamente en el diario
    sin abrir editor de terminal.
    """
    ruta = ruta_de_hoy()
    if not ruta.exists():
        crear_desde_plantilla(ruta)
    contenido_existente = ruta.read_text(encoding="utf-8")
    contenido_nuevo = contenido_existente + "\n" + texto
    ruta.write_text(contenido_nuevo, encoding="utf-8")
    print(f"✅ Entrada de hoy guardada/actualizada: {ruta}")
    return ruta


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] != "escribir":
        print("Uso: python bifrost_bridge.py escribir <texto>")
        return
    texto = " ".join(sys.argv[2:])
    escribir_entrada(texto)


if __name__ == "__main__":
    main()

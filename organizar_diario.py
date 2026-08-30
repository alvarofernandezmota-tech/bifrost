"""Organiza texto sin estructurar en el formato del diario (frontmatter + secciones).
Usable desde terminal (CLI) y desde bifrost (bot de Telegram) como funcion importable.
Ver README.md de esta carpeta.
"""
import argparse
from pathlib import Path

from diario import ruta_de_hoy, crear_desde_plantilla


def organizar_texto(texto: str, ruta: Path = None) -> Path:
    """Inserta texto en la sección 'Qué ha pasado hoy' de la entrada correspondiente
    (hoy por defecto), creando la entrada desde plantilla si no existe.

    Usado por:
    - terminal: python diario/organizar_diario.py --input "texto"
    - bifrost (bot de Telegram): from organizar_diario import organizar_texto
    """
    if ruta is None:
        ruta = ruta_de_hoy()
    if not ruta.exists():
        crear_desde_plantilla(ruta)

    contenido = ruta.read_text(encoding="utf-8")
    marcador = "## Qué ha pasado hoy"
    if marcador in contenido:
        antes, resto = contenido.split(marcador, 1)
        fin_seccion = resto.find("\n## ")
        if fin_seccion == -1:
            resto_nuevo = resto.rstrip() + f"\n{texto}\n"
        else:
            bloque = resto[:fin_seccion].rstrip()
            resto_nuevo = f"{bloque}\n{texto}\n" + resto[fin_seccion:]
        contenido = antes + marcador + resto_nuevo
    else:
        contenido = contenido.rstrip() + f"\n\n## Qué ha pasado hoy\n\n{texto}\n"

    ruta.write_text(contenido, encoding="utf-8")
    print(f"✅ Texto organizado y guardado en: {ruta}")
    return ruta


def main() -> None:
    parser = argparse.ArgumentParser(description="Organiza texto en la entrada del diario")
    parser.add_argument("--input", required=True, help="Texto a organizar")
    parser.add_argument("--output", help="Ruta destino (por defecto: entrada de hoy)")
    args = parser.parse_args()
    ruta = Path(args.output) if args.output else None
    organizar_texto(args.input, ruta)


if __name__ == "__main__":
    main()

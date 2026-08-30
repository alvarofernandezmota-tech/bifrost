"""Diario personal — midgaror/diario. Uso: ver README.md de esta carpeta."""

import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).parent
CARPETA_PERSONAL = RAIZ / "personal"
PLANTILLA = RAIZ / "plantilla.md"

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

def ruta_de_hoy() -> Path:
    hoy = datetime.now()
    nombre_mes = f"{hoy.month:02d}-{MESES[hoy.month]}"
    carpeta_mes = CARPETA_PERSONAL / str(hoy.year) / nombre_mes
    carpeta_mes.mkdir(parents=True, exist_ok=True)
    return carpeta_mes / f"{hoy.strftime('%Y-%m-%d')}.md"

def crear_desde_plantilla(ruta: Path) -> None:
    if PLANTILLA.exists():
        contenido = PLANTILLA.read_text(encoding="utf-8")
        contenido = contenido.replace("{{FECHA}}", datetime.now().strftime("%Y-%m-%d"))
    else:
        contenido = f"# {datetime.now().strftime('%Y-%m-%d')}\n\n## Qué ha pasado hoy\n\n\n## Cómo me siento\n\n\n## Para mañana\n\n"
    ruta.write_text(contenido, encoding="utf-8")

def abrir_editor(ruta: Path) -> None:
    editor = shutil.which("nano") or shutil.which("vim") or shutil.which("vi")
    if editor:
        subprocess.run([editor, str(ruta)])
    else:
        print(f"No encontré un editor. Abre tú mismo:\n{ruta}")

def comando_hoy() -> None:
    ruta = ruta_de_hoy()
    if ruta.exists():
        print(f"📔 Ya existe la entrada de hoy: {ruta}")
    else:
        crear_desde_plantilla(ruta)
        print(f"✅ Entrada de hoy creada: {ruta}")
    abrir_editor(ruta)

def main() -> None:
    if len(sys.argv) < 2:
        print("Diario personal — midgaror/diario. Uso: ver README.md de esta carpeta.")
        return
    comando = sys.argv[1]
    if comando == "hoy":
        comando_hoy()
    else:
        print(f"Comando desconocido: {comando}")

if __name__ == "__main__":
    main()

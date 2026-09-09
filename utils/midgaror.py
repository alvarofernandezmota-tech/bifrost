"""Dónde está midgaror y cómo se importan sus módulos. En un solo sitio.

Bifrost es un submódulo dentro de midgaror y no se instala: los módulos del
diario se importan por ruta. Hasta ahora cada handler repetía las mismas
líneas para conseguirlo —subir cuatro niveles con `Path(__file__).resolve()`,
uno o dos `sys.path.insert`, y luego los imports con `# noqa: E402` porque
quedaban debajo de código—. Ocho ficheros con el mismo preámbulo y ningún
sitio donde arreglarlo una vez.

Aquí se hace una vez, al importar este módulo, y los handlers quedan así:

    from utils.midgaror import modulo

    agenda = modulo("agenda")
    sincronizar = modulo("sincronizar").sincronizar

Los nombres siguen siendo **de módulo**, no de dentro de una función: eso es
lo que permite que `tests/dobles.py` sustituya `sincronizar` handler por
handler para que las pruebas no hagan `git push` de verdad.

Si algún día bifrost se instala como paquete y midgaror se importa de verdad,
este es el único fichero que hay que tocar.
"""

import importlib
import sys
from pathlib import Path

# bifrost vive en midgaror/proyectos/bifrost/, así que la raíz está cuatro
# niveles por encima de utils/.
MIDGAROR = Path(__file__).resolve().parent.parent.parent.parent
DIARIO = MIDGAROR / "diario"

# `diario/` para diario.py, organizar_diario, sincronizar, bifrost_bridge y
# almacen; las subcarpetas porque tareas.py, habitos.py, agenda.py y
# registro.py se importan por su nombre a secas.
CARPETAS = (DIARIO, DIARIO / "tareas", DIARIO / "habitos", DIARIO / "agenda",
            DIARIO / "registro")

for _carpeta in CARPETAS:
    _ruta = str(_carpeta)
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)


def modulo(nombre: str):
    """Un módulo de midgaror, por su nombre.

    Es `importlib.import_module` con las rutas ya puestas. Se usa como
    función y no como `import` para que el handler no tenga que arrastrar el
    `# noqa: E402`: el preámbulo ya no está debajo de código, está aquí.
    """
    return importlib.import_module(nombre)

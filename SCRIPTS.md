# Scripts de Bifrost

## bot.py

Punto de entrada del bot. Inicia la aplicación de Telegram y registra handlers.

**Dependencias**:
- `python-telegram-bot`
- `python-dotenv`

## handlers/

### handlers/diario.py

Importa `organizar_texto()` de `midgaror/diario/organizar_diario.py`.
Escribe en la entrada de hoy.

### handlers/entrada.py

Importa `escribir_entrada()` de `midgaror/diario/bifrost_bridge.py`.
Escribe en la entrada de la fecha indicada, validando el formato antes.

## Scripts en midgaror/diario/

- `organizar_diario.py` → `organizar_texto(texto, fecha=None)`, único camino de escritura
- `bifrost_bridge.py` → `escribir_entrada(texto, fecha=None)`, contrato con este bot (ADR-009)
- `diario.py` → rutas y plantilla del diario

## Ruta de import

Los dos handlers añaden `midgaror/diario/` al `sys.path` calculándolo cuatro
niveles por encima de `handlers/`. Eso obliga a que este repo viva en
`midgaror/proyectos/bifrost`. Clonado en otro sitio, el bot no arranca.

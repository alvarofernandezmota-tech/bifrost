# Instrucciones para Agentes AI

## Contexto del proyecto

Bifrost es un bot de Telegram para escribir y organizar entradas del diario personal.

## Estado actual

✅ Bot funcional - Arranca y responde comandos
⚠️ Pendiente - Refactorizar `organizar_diario.py` para manejar marcadores

## Estructura

bifrost/
├─ bot.py # Punto de entrada
├─ handlers/
│ ├─ diario.py # /diario → organizar_texto()
│ └─ entrada.py # /entrada → escribir_entrada()
├─ utils/
│ └─ auth.py # (pendiente)
├─ venv/ # (NO commitear)
└─ docs/sesiones/

text

## Scripts en midgaror/diario/

- `organizar_diario.py` → organiza texto en secciones
- `bifrost_bridge.py` → escribe sin organizar
- `diario.py` → funciones auxiliares

## Problemas conocidos

- `organizar_diario.py` no maneja bien entradas con marcadores `=======` existentes
- Solución: refactorizar o usar `/entrada` para texto simple

## Reglas

- Nunca modificar `.env` (contiene secretos)
- Documentar cambios en `docs/sesiones/`
- Mantener imports de `midgaror/diario/` actualizados

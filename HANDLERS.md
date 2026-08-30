# Handlers de Bifrost

## `/diario <texto>`

**Módulo**: `handlers/diario.py`

**Función**: Importa `organizar_texto()` de `midgaror/diario/organizar_diario.py`

**Propósito**: Inserta texto en "Qué ha pasado hoy" de la entrada de hoy.

**Problema**: No maneja bien entradas que ya tienen marcadores `=======`.

---

## `/entrada <fecha> <texto>`

**Módulo**: `handlers/entrada.py`

**Función**: Importa `escribir_entrada()` de `midgaror/diario/bifrost_bridge.py`

**Propósito**: Crea o actualiza entrada para una fecha específica.

**Ventaja**: Más simple, no organiza, solo escribe.

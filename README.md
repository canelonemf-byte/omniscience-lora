# omniscience-lora

Scripts para construir pares instrucción/respuesta (estilo LoRA) a partir del árbol de datos del proyecto **OMNISCIENCE**.

## Autoría

- **Autor:** Lázaro López Paz, El Prat de Llobregat, Barcelona, España
- **ORCID:** [0000-0001-8601-1963](https://orcid.org/0000-0001-8601-1963)
- Con asistencia de inteligencia artificial
- Sin afiliaciones institucionales

## Estado (honesto)

- Código de utilidad: genera JSONL a partir de CSV/Markdown/JSON locales.
- **No** entrena un modelo LoRA, **no** valida calidad de pares automáticamente y **no** incluye el corpus OMNISCIENCE.
- Nivel de evidencia del contenido generado: el que figure en las fuentes; este repo no eleva ese nivel.

## Contenido

| Ruta | Qué hace |
|---|---|
| `build.py` | Lee `evidence_register.csv`, informes y `results.json`; escribe `lora/lora_pares.jsonl` |
| `fusion.py` | Reescribe pares con metadatos y comprueba que la fuente exista |
| `data/omniscience/README.md` | Dónde colocar los datos (vacío a propósito) |

## Uso

```bash
# Opción A: datos relativos al repo
mkdir -p data/omniscience
# copiar evidence_register.csv, log_avances.md, C-*/, innovacion/ ...
python3 build.py
python3 fusion.py

# Opción B: variable de entorno
export OMNISCIENCE_DATA=/ruta/a/omniscience
python3 build.py && python3 fusion.py
```

## Licencia

Código: MIT (ver `LICENSE`). La documentación y los pares derivados de OMNISCIENCE se contemplan bajo CC BY 4.0 cuando el contenido de origen lo permita.

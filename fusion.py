#!/usr/bin/env python3
"""Fusiona lora_pares.jsonl en formato instrucción/respuesta con metadatos.

Entrada/salida bajo OMNISCIENCE_DATA (por defecto ./data/omniscience).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path

B = Path(os.environ.get("OMNISCIENCE_DATA", Path(__file__).resolve().parent / "data" / "omniscience"))
A = "Lázaro López Paz, El Prat de Llobregat, Barcelona, España, con asistencia de IA"


def main() -> None:
    src = B / "lora" / "lora_pares.jsonl"
    if not src.is_file():
        raise SystemExit(
            f"No se encuentra {src}. Ejecuta antes build.py con datos en data/omniscience/."
        )
    out = []
    drop = []
    for line in src.open(encoding="utf-8"):
        x = json.loads(line)
        o = x["origen"]
        i = x["instruccion"]
        e = x["nivel_E"] or ""
        if i.startswith("¿Qué nivel"):
            f = B / "evidence_register.csv"
            tipo = "registro"
        elif o == "log_avances":
            f = B / "log_avances.md"
            tipo = "log"
        else:
            d = B / ("innovacion" if o.startswith("INN") else "") / o
            if "results.json" in i:
                g = [d / "results.json"] if (d / "results.json").is_file() else []
            else:
                g = sorted(glob.glob(str(d / "informe*.md")) + glob.glob(str(d / "resultados*.md")))
            f = Path(g[0]) if g else Path("")
            tipo = "campana"
        if not f or not Path(f).is_file():
            drop.append((x["id"], "fuente inexistente"))
            continue
        sim = tipo != "registro" or e[:2] in ("E2", "E3")
        r = {
            "meta": {"id_llp": x["id"], "origen": o, "nivel_E": e, "tipo": tipo},
            "objetivo": i,
            "datos_clave": [x["respuesta"]],
            "tareas": [],
            "riesgos": [],
            "decisiones": [],
            "proximo_paso": "",
        }
        rel = str(f.relative_to(B)) if str(f).startswith(str(B)) else str(f)
        out.append(
            {
                "instruction": i,
                "response": json.dumps(r, ensure_ascii=False, separators=(",", ":")),
                "autor": A,
                "fuente": str(f),
                "fuente_repo": "knowledge/omniscience/" + rel,
                "licencia": "CC BY 4.0",
                "proyecto": "omniscience",
                "simulado": sim,
                "nivel_E": e,
                "origen": o,
                "id": hashlib.sha256((str(f) + i + x["respuesta"]).encode()).hexdigest()[:16],
            }
        )
    dest = B / "lora" / "lora_pares_fusion.jsonl"
    with dest.open("w", encoding="utf-8") as w:
        for y in out:
            w.write(json.dumps(y, ensure_ascii=False) + "\n")
    print(len(out), drop)


if __name__ == "__main__":
    main()

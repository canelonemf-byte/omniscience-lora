#!/usr/bin/env python3
"""Construye pares instrucción/respuesta LoRA a partir de datos OMNISCIENCE.

Lee evidence_register.csv, informes de campaña y results.json desde OMNISCIENCE_DATA
(por defecto: ./data/omniscience). Escribe lora_pares.jsonl en ese mismo árbol.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import re
from pathlib import Path

# Ruta relativa al repo; se puede override con la variable de entorno OMNISCIENCE_DATA.
B = Path(os.environ.get("OMNISCIENCE_DATA", Path(__file__).resolve().parent / "data" / "omniscience"))
A = (
    "Lázaro López Paz, El Prat de Llobregat, Barcelona, España, "
    "con asistencia de inteligencia artificial"
)
out = []
n = [0]


def add(i, r, e, o):
    r = re.sub(r"\n{3,}", "\n\n", r).strip()
    if len(r) < 20:
        return
    n[0] += 1
    out.append(
        {
            "id": f"llp_{n[0]:04d}",
            "instruccion": i,
            "respuesta": r[:3500],
            "nivel_E": e or "",
            "origen": o,
            "autoria": A,
        }
    )


def main() -> None:
    register = B / "evidence_register.csv"
    if not register.is_file():
        raise SystemExit(
            f"No se encuentra {register}. "
            "Coloca los datos OMNISCIENCE en data/omniscience/ "
            "o define OMNISCIENCE_DATA."
        )

    rows = list(csv.DictReader(register.open(encoding="utf-8")))
    lvl = {}
    for w in rows:
        g = lambda k: (w.get(k) or "").strip().replace("—", "")
        e = g("nivel_E")
        add(
            f"¿Qué nivel de evidencia tiene la afirmación {w['id']} del módulo {g('modulo')} en OMNISCIENCE y por qué?",
            f"Afirmación: {g('afirmacion')}\nNivel: {e or 'sin nivel asignado'}\nJustificación: {g('justificacion')}"
            + (f"\nSiguiente paso: {g('siguiente_paso')}" if g("siguiente_paso") else ""),
            e,
            w["id"],
        )
        for c in re.findall(
            r"C-(?:MAT|UMF|VIB)-\d{3}|INN-\d\d", g("fuente") + " " + g("justificacion")
        ):
            if e and re.match(r"E\d", e):
                lvl[c] = max(lvl.get(c, ""), e[:2]) if c not in lvl else lvl[c]

    freeze = {
        "C-VIB-001": "E3",
        "C-MAT-001": "E2",
        "C-MAT-002": "E2",
        "C-MAT-003": "E1",
        "C-MAT-004": "E2",
        "C-MAT-005": "E2",
        "C-MAT-006": "E3",
        "C-UMF-001": "E2",
        "C-UMF-002": "E2",
        "C-UMF-003": "E2",
        "C-UMF-004": "E1",
        "C-UMF-005": "E1",
        "INN-01": "E1",
        "INN-03": "E1",
        "INN-05": "E1",
    }

    def secs(t):
        parts = re.split(r"^(#{1,3} .*)$", t, flags=re.M)
        cur = "Resumen general"
        res = []
        if parts[0].strip():
            res.append((cur, parts[0]))
        for k in range(1, len(parts), 2):
            res.append((parts[k].lstrip("# ").strip(), parts[k + 1]))
        return res

    files = sorted(
        glob.glob(str(B / "C-*" / "informe*.md"))
        + glob.glob(str(B / "C-*" / "resultados*.md"))
        + glob.glob(str(B / "innovacion" / "INN-*" / "informe*.md"))
    )
    for f in files:
        c = re.search(r"(C-\w+-\d{3}|INN-\d\d)", f).group(1)
        e = freeze.get(c, lvl.get(c, ""))
        t = open(f, encoding="utf-8").read()
        t = "\n".join(l for l in t.split("\n") if not l.startswith(">"))
        for h, b in secs(t):
            add(f"En la campaña {c} de OMNISCIENCE, ¿qué se obtuvo en «{h}»?", b, e, c)

    for f in sorted(
        glob.glob(str(B / "C-*" / "results.json"))
        + glob.glob(str(B / "innovacion" / "INN-*" / "results.json"))
    ):
        c = re.search(r"(C-\w+-\d{3}|INN-\d\d)", f).group(1)
        e = freeze.get(c, "")
        d = json.load(open(f, encoding="utf-8"))
        flat = {}

        def walk(x, p=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    walk(v, f"{p}.{k}" if p else k)
            elif not isinstance(x, list) and re.search(
                r"veredict|pasa|pass|nivel|verdict|resultado", p, re.I
            ):
                flat[p] = x

        walk(d)
        if flat:
            add(
                f"Lista los veredictos registrados en results.json de la campaña {c}.",
                "\n".join(f"{k}: {v}" for k, v in list(flat.items())[:60]),
                e,
                c,
            )

    log_path = B / "log_avances.md"
    if log_path.is_file():
        lg = log_path.read_text(encoding="utf-8")
        for h, b in secs(lg):
            m = re.search(r"(C-\w+-\d{3}|INN-\d\d|UM-\d\d)", h + b[:300])
            add(
                f"¿Qué se registró en el log de avances de OMNISCIENCE en «{h}»?",
                b,
                freeze.get(m.group(1), "") if m else "",
                "log_avances",
            )

    out_dir = B / "lora"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "lora_pares.jsonl"
    with p.open("w", encoding="utf-8") as o:
        for x in out:
            o.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"Escritos {len(out)} pares en {p}")


if __name__ == "__main__":
    main()

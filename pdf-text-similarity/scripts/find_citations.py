#!/usr/bin/env python3
"""Procura ocorrências de citações relevantes (mencionadas na Introdução) em ARTIGOS_TXT.

Saída: `citations_found.csv` com colunas: file, match, context
"""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "ARTIGOS_TXT"
OUT_CSV = ROOT / "citations_found.csv"

# Padrões a procurar (case-insensitive). Ajuste conforme necessário.
PATTERNS = [
    r"Caetano",
    r"Wegner",
    r"Xavier",
    r"IBGE",
    r"UN Tourism",
    r"UN TOURISM",
    r"Índice Sintético de Viabilidade Territorial",
    r"ISVT",
]


def search_in_file(path: Path):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    results = []
    for pat in PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            start = max(0, m.start() - 80)
            end = min(len(text), m.end() + 80)
            context = text[start:end].replace('\n', ' ')
            results.append((pat, context.strip()))
    return results


def run():
    if not INPUT_DIR.exists():
        print(f"Input dir not found: {INPUT_DIR}")
        return

    rows = []
    for f in INPUT_DIR.rglob("*.txt"):
        res = search_in_file(f)
        for pat, context in res:
            rows.append((str(f.relative_to(ROOT)), pat, context))

    with OUT_CSV.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(['file', 'pattern', 'context'])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} matches to {OUT_CSV}")


if __name__ == '__main__':
    run()

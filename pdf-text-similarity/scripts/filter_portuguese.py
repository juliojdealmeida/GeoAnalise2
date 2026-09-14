#!/usr/bin/env python3
"""Detecta arquivos em Português dentro de ARTIGOS_TXT.

Gera uma lista `artigos_txt_pt.txt` com caminhos relativos dos arquivos detectados como português
e opcionalmente copia os arquivos para `ARTIGOS_TXT_PT/`.
"""
from pathlib import Path
from langdetect import detect_langs
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "ARTIGOS_TXT"
OUT_LIST = ROOT / "artigos_txt_pt.txt"
OUT_DIR = ROOT / "ARTIGOS_TXT_PT"


def is_portuguese(text: str) -> bool:
    try:
        langs = detect_langs(text[:5000])
        if not langs:
            return False
        top = langs[0]
        # exemplo: top.lang == 'pt' e prob > 0.70
        return top.lang == 'pt' and top.prob >= 0.70
    except Exception:
        return False


def scan(copy_found: bool = True):
    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}")
        return

    files = list(INPUT_DIR.rglob("*.txt"))
    found = []

    for f in files:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Failed to read {f}: {e}")
            continue

        if is_portuguese(text):
            rel = f.relative_to(ROOT)
            found.append(str(rel))
            print(f"[PT] {rel}")
            if copy_found:
                dest = OUT_DIR / f.relative_to(INPUT_DIR)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, dest)

    OUT_LIST.write_text("\n".join(found), encoding='utf-8')
    print(f"Found {len(found)} Portuguese files. List saved to {OUT_LIST}")


if __name__ == '__main__':
    copy = True
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('--no-copy', 'nocopy'):
        copy = False
    scan(copy_found=copy)

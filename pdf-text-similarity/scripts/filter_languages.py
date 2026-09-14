#!/usr/bin/env python3
"""Detecta arquivos em idiomas (pt, en, es) dentro de ARTIGOS_TXT.

Gera listas: artigos_txt_en.txt, artigos_txt_es.txt e copia arquivos para ARTIGOS_TXT_EN/ARTIGOS_TXT_ES.
Uso: python scripts/filter_languages.py
"""
from pathlib import Path
from langdetect import detect_langs
import shutil

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "ARTIGOS_TXT"
OUT_EN = ROOT / "artigos_txt_en.txt"
OUT_ES = ROOT / "artigos_txt_es.txt"
OUT_DIR_EN = ROOT / "ARTIGOS_TXT_EN"
OUT_DIR_ES = ROOT / "ARTIGOS_TXT_ES"


def detect_lang(text: str):
    try:
        langs = detect_langs(text[:5000])
        if not langs:
            return None, 0.0
        top = langs[0]
        return top.lang, top.prob
    except Exception:
        return None, 0.0


def scan():
    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}")
        return

    en_files = []
    es_files = []

    for f in INPUT_DIR.rglob("*.txt"):
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        lang, prob = detect_lang(text)
        if lang == 'en' and prob >= 0.70:
            rel = f.relative_to(ROOT)
            en_files.append(str(rel))
            dest = OUT_DIR_EN / f.relative_to(INPUT_DIR)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)
            print(f"[EN] {rel}")
        elif lang == 'es' and prob >= 0.70:
            rel = f.relative_to(ROOT)
            es_files.append(str(rel))
            dest = OUT_DIR_ES / f.relative_to(INPUT_DIR)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)
            print(f"[ES] {rel}")

    OUT_EN.write_text("\n".join(en_files), encoding='utf-8')
    OUT_ES.write_text("\n".join(es_files), encoding='utf-8')
    print(f"Found {len(en_files)} English and {len(es_files)} Spanish files.")


if __name__ == '__main__':
    scan()

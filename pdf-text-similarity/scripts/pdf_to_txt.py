#!/usr/bin/env python3
"""Converter PDFs em ARTIGOS/ARTIGOS_SCOPUS para TXT em ARTIGOS_TXT.

Uso:
    python scripts/pdf_to_txt.py

Ele caminha pela pasta `ARTIGOS/ARTIGOS_SCOPUS`, extrai texto de cada .pdf
e grava um arquivo .txt com o mesmo nome em `ARTIGOS_TXT`.
"""
import sys
import os
from pathlib import Path
import fitz  # PyMuPDF


ROOT = Path(__file__).resolve().parents[1]
SCOPUS_DIR = ROOT / "ARTIGOS" / "ARTIGOS_SCOPUS"
OUT_DIR = ROOT / "ARTIGOS_TXT"


def extract_text_from_pdf(pdf_path: Path) -> str:
    text_chunks = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                if text:
                    text_chunks.append(text)
    except Exception as e:
        print(f"Erro ao ler {pdf_path}: {e}")
    return "\n\n".join(text_chunks)


def ensure_out_dir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def convert_all():
    if not SCOPUS_DIR.exists():
        print(f"Diretório de entrada não encontrado: {SCOPUS_DIR}")
        return
    ensure_out_dir()

    pdf_files = list(SCOPUS_DIR.rglob("*.pdf"))
    if not pdf_files:
        print(f"Nenhum PDF encontrado em: {SCOPUS_DIR}")
        return

    for pdf in pdf_files:
        rel = pdf.relative_to(SCOPUS_DIR)
        out_path = OUT_DIR / rel.with_suffix('.txt')
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists():
            print(f"Pulando (já existe): {out_path}")
            continue

        print(f"Convertendo: {pdf} → {out_path}")
        text = extract_text_from_pdf(pdf)
        try:
            out_path.write_text(text, encoding='utf-8')
        except Exception as e:
            print(f"Erro ao gravar {out_path}: {e}")


def main():
    convert_all()


if __name__ == '__main__':
    main()

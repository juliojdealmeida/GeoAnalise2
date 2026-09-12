import argparse
import os
import re
import sys
from pathlib import Path

from pdf_processor import extract_text_from_document
from similarity_calculator import calculate_similarity


def load_reference_text(file_paths):
    """
    Carrega o texto de um ou mais arquivos de referência e combina todos.
    :param file_paths: Caminho único ou lista de caminhos.
    :return: Texto combinado.
    """
    if isinstance(file_paths, (str, Path)):
        file_paths = [file_paths]

    texts = []
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"Erro: O arquivo '{path}' não foi encontrado.")
            continue

        try:
            text = extract_text_from_document(path)
        except Exception as exc:
            print(f"Erro ao carregar o arquivo de referência '{path}': {exc}")
            continue

        if text.strip():
            texts.append(text.strip())

    return "\n\n".join(texts)


def detect_text_language(text):
    """Detecta o idioma principal de um texto usando heurística local e, quando disponível, langdetect."""
    if not text or not str(text).strip():
        return 'und'

    sample = str(text).lower()

    try:
        from langdetect import detect
        detected = detect(sample)
        if detected in {'pt', 'en', 'es'}:
            return detected
    except Exception:
        pass

    portuguese_markers = {
        'o', 'a', 'os', 'as', 'e', 'de', 'do', 'da', 'dos', 'das', 'para', 'com',
        'que', 'como', 'desenvolvimento', 'política', 'regional', 'economia', 'inovação',
        'artigo', 'publica', 'públicas', 'nacional', 'internacional', 'sustentável', 'social'
    }
    spanish_markers = {
        'el', 'la', 'los', 'las', 'y', 'de', 'del', 'para', 'con', 'que', 'como',
        'desarrollo', 'política', 'regional', 'economía', 'innovación', 'artículo',
        'pública', 'social', 'internacional', 'nacional', 'analiza'
    }
    english_markers = {
        'the', 'and', 'for', 'with', 'that', 'this', 'from', 'development', 'policy',
        'regional', 'economy', 'analysis', 'article', 'public', 'international', 'research',
        'market', 'growth', 'innovation', 'climate', 'social'
    }

    token_counts = {'pt': 0, 'es': 0, 'en': 0}
    tokens = re.findall(r"[a-zA-ZáéíóúãõçàèìòùüñÁÉÍÓÚÃÕÇÀÈÌÒÙÜÑ]+", sample)
    for token in tokens:
        if token in portuguese_markers:
            token_counts['pt'] += 2
        if token in spanish_markers:
            token_counts['es'] += 2
        if token in english_markers:
            token_counts['en'] += 2

    # Heurística de caracteres acentuados e palavras específicas para refinar o idioma.
    if any(ch in sample for ch in ['ã', 'õ', 'á', 'é', 'í', 'ó', 'ú', 'ç']):
        if any(word in sample for word in ['desenvolvimento', 'política', 'inovação', 'economia', 'regional', 'sustentável']):
            token_counts['pt'] += 3
        if any(word in sample for word in ['desarrollo', 'política', 'economía', 'innovación', 'regional', 'analiza']):
            token_counts['es'] += 3

    best_lang, best_score = 'und', 0
    for lang, score in token_counts.items():
        if score > best_score:
            best_lang = lang
            best_score = score

    if best_score == 0:
        if any(token in sample for token in ['the', 'and', 'with', 'from', 'for', 'development', 'policy']):
            return 'en'
        if any(token in sample for token in ['desenvolvimento', 'política', 'inovação', 'economia', 'regional']):
            return 'pt'
        if any(token in sample for token in ['desarrollo', 'política', 'economía', 'innovación', 'regional']):
            return 'es'
        return 'und'

    return best_lang


def process_documents_in_folder(folder_path, theme, top_n=15, reference_name=None, use_multilingual=True, model_name=None):
    """
    Processa todos os documentos textuais de uma pasta e calcula a similaridade
    com uma referência combinada (outline + introdução, por exemplo).
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Erro: A pasta '{folder}' não foi encontrada.")
        return None

    document_files = [
        path for path in sorted(folder.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in {'.txt', '.docx', '.pdf'}
    ]
    if not document_files:
        print("Nenhum arquivo textual encontrado na pasta especificada.")
        return None

    txt_files = [path for path in document_files if path.suffix.lower() == '.txt']
    files_to_process = txt_files if txt_files else document_files

    article_texts = []
    valid_names = []
    detected_languages = []
    theme_language = detect_text_language(theme)
    print(f"Idioma detectado do tema: {theme_language}")

    for item in files_to_process:
        print(f"Extraindo texto de: {item.name}")
        text = extract_text_from_document(item)
        if text.strip():
            article_texts.append(text)
            valid_names.append(item.name)
            detected_languages.append(detect_text_language(text))
        else:
            print(f"Aviso: Nenhum texto extraído de '{item.name}'.")

    if not article_texts:
        print("Nenhum texto válido foi extraído dos documentos.")
        return None

    print("\nCalculando similaridade...")
    similarities = calculate_similarity(
        article_texts,
        theme,
        use_multilingual=use_multilingual,
        model_name=model_name,
    )
    ranked = sorted(
        zip(valid_names, detected_languages, similarities),
        key=lambda item: ((item[1] != theme_language), -float(item[2])),
    )

    print(f"\nTop {top_n} melhores correlações:")
    for idx, (name, lang, score) in enumerate(ranked[:top_n], start=1):
        print(f"{idx}. {name} [{lang}]: {score:.4f}")

    ref_part = f"_{reference_name}" if reference_name else ""
    output_path = folder.parent / f"resultados_correlacao_top15{ref_part}.txt"
    with output_path.open('w', encoding='utf-8') as file:
        ref_label = reference_name or 'tema'
        file.write(f"Tema: {ref_label}\n\n")
        for idx, (name, lang, score) in enumerate(ranked[:top_n], start=1):
            file.write(f"{idx}. {name} [{lang}]: {score:.4f}\n")

    print(f"\nArquivo de resultado salvo em: {output_path}")
    return ranked[:top_n]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Correlação de textos em PT/EN/ES com outline + introdução.")
    parser.add_argument("references", nargs="*", help="Arquivos de referência (DOCX/TXT).")
    parser.add_argument("--no-multilingual", action="store_true", help="Força o uso de TF-IDF em vez do modelo multilíngue.")
    parser.add_argument("--model-name", default=None, help="Modelo sentence-transformers para usar no modo multilíngue.")
    parser.add_argument("--folder", default=None, help="Pasta com os arquivos a comparar.")
    parser.add_argument("--top-n", type=int, default=15, help="Quantidade de resultados a exibir.")

    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent.parent
    default_folder = Path(args.folder) if args.folder else (project_root / "ARTIGOS_TXT")
    if not default_folder.exists():
        default_folder = project_root / "ARTIGOS"

    cli_refs = [Path(p) for p in args.references]
    if cli_refs:
        reference_files = cli_refs
    else:
        reference_files = []
        for candidate in [
            project_root / "PT_Modelo de Outline_ALTERADO.docx",
            project_root / "Introdução.txt",
        ]:
            if candidate.exists():
                reference_files.append(candidate)

        if not reference_files:
            reference_files = sorted(
                project_root.glob("*Modelo*.docx") + project_root.glob("*Intro*.txt"),
                key=lambda item: item.name.lower(),
            )

        if not reference_files:
            reference_files = [project_root / "PT_Modelo de Outline_ALTERADO.docx"]

    theme = load_reference_text(reference_files)
    if not theme.strip():
        print("O arquivo de referência está vazio ou não pôde ser carregado.")
        return

    reference_label = " + ".join(ref.name for ref in reference_files)
    print(f"Processando referência: {reference_label}")
    process_documents_in_folder(
        str(default_folder),
        theme,
        top_n=args.top_n,
        reference_name="_".join(ref.stem for ref in reference_files),
        use_multilingual=not args.no_multilingual,
        model_name=args.model_name,
    )


if __name__ == "__main__":
    main()
from pathlib import Path

from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from pdf_processor import extract_text_from_document


def read_reference_text(file_paths):
    if isinstance(file_paths, (str, Path)):
        file_paths = [file_paths]

    texts = []
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists():
            text = extract_text_from_document(path)
            if text.strip():
                texts.append(text.strip())
    return "\n\n".join(texts)


def read_outline(docx_path: str) -> str:
    doc = Document(docx_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


def get_article_files(articles_dir: Path):
    if not articles_dir.exists():
        return []

    files = [path for path in articles_dir.iterdir() if path.is_file()]
    txt_files = sorted((path for path in files if path.suffix.lower() == '.txt'), key=lambda item: item.name.lower())
    if txt_files:
        return txt_files
    return sorted(files, key=lambda item: item.name.lower())


def main():
    project_root = Path(__file__).resolve().parent.parent
    articles_dir = project_root / "ARTIGOS_TXT"
    if not articles_dir.exists():
        articles_dir = project_root / "ARTIGOS"

    outline_path = project_root / "PT_Modelo de Outline_ALTERADO.docx"
    intro_path = project_root / "Introdução.txt"

    reference_paths = []
    for path in [outline_path, intro_path]:
        if path.exists():
            reference_paths.append(path)

    if not reference_paths:
        raise FileNotFoundError(
            "Não foi encontrado o outline DOCX nem a introdução TXT. "
            "Coloque os arquivos na raiz do projeto."
        )

    theme_text = read_reference_text(reference_paths)
    article_files = get_article_files(articles_dir)
    if not article_files:
        raise FileNotFoundError(f"Diretório de artigos não encontrado: {articles_dir}")

    article_texts = []
    valid_names = []
    for article_file in article_files:
        text = extract_text_from_document(article_file)
        if text.strip():
            article_texts.append(text)
            valid_names.append(article_file.name)

    if not article_texts:
        raise RuntimeError(f"Nenhum texto válido foi encontrado na pasta {articles_dir}.")

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([theme_text] + article_texts)
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    ranked = sorted(zip(valid_names, similarities), key=lambda item: item[1], reverse=True)

    output_file = project_root / "resultados_correlacao_outline.txt"
    with output_file.open('w', encoding='utf-8') as file:
        file.write("Top 15 artigos por correlação com o outline + introdução\n")
        for index, (file_name, score) in enumerate(ranked[:15], start=1):
            file.write(f"{index:02d}. {file_name} -> {score:.6f}\n")

    print("Top 15 artigos por correlação com o outline + introdução")
    for index, (file_name, score) in enumerate(ranked[:15], start=1):
        print(f"{index:02d}. {file_name} -> {score:.6f}")

    print(f"\nResultado salvo em: {output_file}")


if __name__ == '__main__':
    main()

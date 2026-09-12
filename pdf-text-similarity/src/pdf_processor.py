from pathlib import Path

try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:
    fitz = None

from docx import Document


def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de um arquivo PDF.
    :param pdf_path: Caminho do arquivo PDF.
    :return: Texto extraído.
    """
    if fitz is None:
        raise ImportError(
            "PyMuPDF não está instalado. Execute: pip install -r requirements.txt"
        )

    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
    return text


def extract_text_from_docx(docx_path):
    """
    Extrai texto de um arquivo DOCX.
    :param docx_path: Caminho do arquivo DOCX.
    :return: Texto extraído.
    """
    try:
        document = Document(docx_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    except Exception as e:
        print(f"Erro ao processar {docx_path}: {e}")
        return ""


def extract_text_from_document(file_path):
    """
    Extrai texto a partir de um documento suportado: PDF, DOCX ou TXT.
    :param file_path: Caminho do documento.
    :return: Texto extraído.
    """
    normalized = str(file_path).lower()
    if normalized.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    if normalized.endswith('.docx'):
        return extract_text_from_docx(file_path)
    if normalized.endswith('.txt'):
        return Path(file_path).read_text(encoding='utf-8', errors='ignore')

    raise ValueError(f"Formato não suportado para o arquivo: {file_path}")
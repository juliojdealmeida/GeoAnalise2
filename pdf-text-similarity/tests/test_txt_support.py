import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / 'src'))

import main


def test_process_documents_in_folder_prefers_txt(tmp_path):
    articles_dir = tmp_path / 'ARTIGOS_TXT'
    articles_dir.mkdir()

    (articles_dir / 'artigo_1.txt').write_text(
        'Desenvolvimento regional, inovação, políticas públicas, economia local.',
        encoding='utf-8',
    )
    (articles_dir / 'artigo_2.txt').write_text(
        'Receitas culinárias e pratos tradicionais sem relação com o tema.',
        encoding='utf-8',
    )

    ranked = main.process_documents_in_folder(
        str(articles_dir),
        'desenvolvimento regional e inovação pública',
        top_n=1,
    )

    assert ranked is not None
    assert ranked[0][0] == 'artigo_1.txt'


def test_detect_text_language_uses_explicit_language_detection():
    assert main.detect_text_language('This paper studies regional development and public policy.') == 'en'
    assert main.detect_text_language('Este artigo analisa o desenvolvimento regional e políticas públicas.') == 'pt'
    assert main.detect_text_language('Este artículo analiza el desarrollo regional y la política pública.') == 'es'

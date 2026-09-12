import warnings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Prefer using a multilingual sentence embedding model when available
_HAS_ST = False
_ST_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    import numpy as _np
    _HAS_ST = True
except Exception:
    _HAS_ST = False


def _load_st_model(model_name="paraphrase-multilingual-MiniLM-L12-v2"):
    global _ST_MODEL
    if _ST_MODEL is None:
        # Use only cached/local models to avoid slow or failed network downloads
        # when the environment cannot access Hugging Face.
        _ST_MODEL = SentenceTransformer(model_name, local_files_only=True)
    return _ST_MODEL


def _multilingual_similarity(texts, theme, model_name=None):
    """Tenta calcular similaridade multilíngue com embeddings do sentence-transformers."""
    if not _HAS_ST:
        return None

    selected_model = model_name or "paraphrase-multilingual-MiniLM-L12-v2"
    try:
        model = _load_st_model(selected_model)
        texts_to_encode = [theme] + texts
        embeddings = model.encode(texts_to_encode, convert_to_numpy=True)
        theme_emb = embeddings[0:1]
        other_embs = embeddings[1:]
        return cosine_similarity(theme_emb, other_embs).flatten()
    except Exception:
        return None


def calculate_similarity(texts, theme, use_multilingual=True, model_name=None):
    """
    Calcula a similaridade entre os textos e o tema.

    Se disponível e `use_multilingual=True`, usa um modelo multilíngue
    (`sentence-transformers`) para gerar embeddings que funcionam entre
    idiomas (PT/EN/ES). Caso contrário, utiliza TF-IDF como fallback.

    :param texts: Lista de textos extraídos dos documentos.
    :param theme: Tema para comparação.
    :param use_multilingual: Tenta usar embeddings multilíngues se True.
    :param model_name: Nome do modelo `sentence-transformers` a ser usado.
    :return: Lista de pontuações de similaridade.
    """
    if use_multilingual:
        scores = _multilingual_similarity(texts, theme, model_name=model_name)
        if scores is not None:
            return scores

        warnings.warn(
            "Modelo multilíngue indisponível; usando TF-IDF como fallback.",
            RuntimeWarning,
            stacklevel=2,
        )

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([theme] + texts)
    similarity_scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    return similarity_scores
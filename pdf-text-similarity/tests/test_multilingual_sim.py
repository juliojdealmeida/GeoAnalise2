import os
import sys
import types

import numpy as np

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(repo_root, 'src'))

# Simulate a multilingual embedding model without downloading a heavy model.
# This checks the real code path that would run when sentence-transformers is installed.
fake_module = types.ModuleType('sentence_transformers')


class FakeSentenceTransformer:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, convert_to_numpy=True):
        vectors = []
        for text in texts:
            t = str(text).lower()
            if any(key in t for key in ['correl', 'tema', 'topic', 'analis', 'analysis', 'correlación']):
                vectors.append([1.0, 0.9, 0.8])
            elif 'cooking' in t or 'receita' in t:
                vectors.append([0.2, -0.6, 0.1])
            else:
                vectors.append([0.3, 0.1, -0.2])
        return np.asarray(vectors, dtype=float)


fake_module.SentenceTransformer = FakeSentenceTransformer
sys.modules['sentence_transformers'] = fake_module

from similarity_calculator import calculate_similarity


theme = "Este trabalho aborda métodos de correlação entre artigos e temas científicos."
texts = [
    "Este artigo discute métodos de correlação de texto e análise de temas.",
    "This paper discusses methods for text correlation and topic analysis.",
    "Este artículo trata métodos de correlación de texto y análisis de temas.",
    "Unrelated content about cooking and recipes."
]

print('Texts:')
for i, t in enumerate(texts, 1):
    print(f"{i}. {t}")

print('\nRunning similarity tests:')
multilingual_scores = calculate_similarity(texts, theme, use_multilingual=True)
print('multilingual_scores =', multilingual_scores.tolist())

tfidf_scores = calculate_similarity(texts, theme, use_multilingual=False)
print('tfidf_scores =', tfidf_scores.tolist())

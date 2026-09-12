# Text Similarity

Este projeto lê documentos textuais de uma pasta, extrai o texto e calcula a similaridade com um tema de referência.

O fluxo principal agora foi ajustado para usar arquivos TXT, especialmente a pasta ARTIGOS_TXT, mantendo compatibilidade com PDF e DOCX para casos antigos.

## Dependências

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Como usar

1. Coloque os arquivos TXT na pasta ARTIGOS_TXT.
2. Coloque o outline em DOCX e, se necessário, a Introdução em TXT na raiz do projeto.
3. Execute o programa:

```bash
python src/main.py
```

Opcionalmente, você pode passar arquivos de referência na linha de comando:

```bash
python src/main.py "PT_Modelo de Outline_ALTERADO.docx" "Introdução.txt"
```

O programa combina todos os arquivos de referência em uma única temática antes de calcular a correlação com os artigos.

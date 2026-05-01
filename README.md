# Calculadora de Perda de Chapas

Software web para calcular quantas chapas são perdidas a partir das sobras ou peças perdidas de um corte.

## O que o sistema faz

- Permite informar a medida da chapa base.
- Permite informar material, comprimento, largura e quantidade das peças/sobras perdidas.
- Converte a área perdida em m².
- Calcula o equivalente em chapas completas.
- Mostra quantas chapas inteiras devem ser consideradas como perda.
- Agrupa o resultado por material.
- Permite colar dados do Excel usando TAB ou ponto e vírgula.
- Permite exportar o relatório em CSV.

## Estrutura do projeto

```text
calculadora_perda_chapas/
├── app.py
├── requirements.txt
├── render.yaml
├── Procfile
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── script.js
```

## Como rodar localmente

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Rode o sistema:

```bash
python app.py
```

Acesse no navegador:

```text
http://localhost:10000
```

## Como publicar no GitHub

```bash
git init
git add .
git commit -m "Primeira versão da calculadora de perda de chapas"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

## Como publicar no Render

### Opção 1: usando o painel do Render

1. Crie um repositório no GitHub e envie estes arquivos.
2. No Render, clique em **New > Web Service**.
3. Conecte o repositório do GitHub.
4. Use estas configurações:

```text
Language: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:${PORT:-10000} app:app
```

5. Clique em **Create Web Service**.

### Opção 2: usando Blueprint

O arquivo `render.yaml` já está pronto. Ao usar Blueprint no Render, ele cria o serviço com:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:${PORT:-10000} app:app
Health Check: /health
```

## Fórmula usada

```text
Área perdida da linha = comprimento × largura × quantidade
Área da chapa = comprimento da chapa × largura da chapa
Chapas equivalentes = área total perdida ÷ área da chapa
Chapas inteiras = arredondamento para cima das chapas equivalentes
```

Exemplo:

```text
Chapa: 2750 × 1850 mm = 5,0875 m²
Perda total: 10,50 m²
Chapas equivalentes: 10,50 ÷ 5,0875 = 2,0645 chapas
Chapas inteiras: 3 chapas
```

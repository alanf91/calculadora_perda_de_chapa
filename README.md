# Calculadora de Perda e Retorno de Sobras de Chapas

Sistema web em Flask para calcular:

- área perdida em m²;
- chapas equivalentes perdidas;
- chapas inteiras equivalentes;
- custo perdido estimado;
- quantas peças podem ser fabricadas usando as sobras;
- valor de retorno estimado;
- exportação de relatório em CSV.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://localhost:10000
```

## Deploy no Render

Build Command:

```bash
pip install --upgrade pip && pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Health check:

```text
/health
```

## Observação importante

Esta versão não usa as pastas `templates` e `static`. Todos os arquivos da tela estão dentro do `app.py`, para facilitar o upload no GitHub.

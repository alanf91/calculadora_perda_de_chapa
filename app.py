from __future__ import annotations

import csv
import io
import math
import os
from dataclasses import dataclass, asdict
from typing import Any

from flask import Flask, jsonify, make_response, render_template, request

app = Flask(__name__)


@dataclass
class LinhaPerda:
    material: str
    comprimento_mm: float
    largura_mm: float
    quantidade: int
    area_m2: float
    chapas_equivalentes: float


def parse_numero(valor: Any, campo: str) -> float:
    """Converte números digitados no padrão BR ou internacional para float."""
    if valor is None:
        raise ValueError(f"Campo '{campo}' vazio.")

    texto = str(valor).strip()
    if not texto:
        raise ValueError(f"Campo '{campo}' vazio.")

    texto = texto.replace(" ", "")

    # Ex.: 1.850,50 -> 1850.50 | 1850,50 -> 1850.50
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        numero = float(texto)
    except ValueError as exc:
        raise ValueError(f"Campo '{campo}' precisa ser numérico.") from exc

    if numero <= 0:
        raise ValueError(f"Campo '{campo}' precisa ser maior que zero.")
    return numero


def converter_para_mm(valor: Any, unidade: str, campo: str) -> float:
    numero = parse_numero(valor, campo)
    unidade = (unidade or "mm").lower()

    if unidade == "mm":
        return numero
    if unidade == "cm":
        return numero * 10
    if unidade == "m":
        return numero * 1000

    raise ValueError("Unidade inválida. Use mm, cm ou m.")


def calcular_perdas(payload: dict[str, Any]) -> dict[str, Any]:
    unidade = payload.get("unidade", "mm")
    chapa_comprimento_mm = converter_para_mm(
        payload.get("chapa_comprimento", 2750), unidade, "comprimento da chapa"
    )
    chapa_largura_mm = converter_para_mm(
        payload.get("chapa_largura", 1850), unidade, "largura da chapa"
    )
    custo_chapa = payload.get("custo_chapa")
    custo_chapa_float = 0.0
    if custo_chapa not in (None, ""):
        custo_chapa_float = parse_numero(custo_chapa, "custo da chapa")

    area_chapa_mm2 = chapa_comprimento_mm * chapa_largura_mm
    area_chapa_m2 = area_chapa_mm2 / 1_000_000

    linhas_payload = payload.get("linhas", [])
    if not isinstance(linhas_payload, list) or not linhas_payload:
        raise ValueError("Informe pelo menos uma peça/sobra perdida.")

    linhas_validas: list[LinhaPerda] = []
    erros: list[str] = []
    total_area_mm2 = 0.0
    por_material: dict[str, dict[str, float]] = {}

    for indice, linha in enumerate(linhas_payload, start=1):
        if not isinstance(linha, dict):
            erros.append(f"Linha {indice}: formato inválido.")
            continue

        material = str(linha.get("material") or "Sem material").strip() or "Sem material"
        try:
            comprimento_mm = converter_para_mm(
                linha.get("comprimento"), unidade, f"comprimento da linha {indice}"
            )
            largura_mm = converter_para_mm(
                linha.get("largura"), unidade, f"largura da linha {indice}"
            )
            quantidade_float = parse_numero(linha.get("quantidade"), f"quantidade da linha {indice}")
            quantidade = int(quantidade_float)
            if quantidade_float != quantidade or quantidade <= 0:
                raise ValueError(f"Quantidade da linha {indice} precisa ser um número inteiro maior que zero.")
        except ValueError as exc:
            erros.append(str(exc))
            continue

        area_linha_mm2 = comprimento_mm * largura_mm * quantidade
        total_area_mm2 += area_linha_mm2
        area_linha_m2 = area_linha_mm2 / 1_000_000
        chapas_equivalentes_linha = area_linha_mm2 / area_chapa_mm2

        linhas_validas.append(
            LinhaPerda(
                material=material,
                comprimento_mm=round(comprimento_mm, 3),
                largura_mm=round(largura_mm, 3),
                quantidade=quantidade,
                area_m2=round(area_linha_m2, 4),
                chapas_equivalentes=round(chapas_equivalentes_linha, 4),
            )
        )

        resumo_material = por_material.setdefault(
            material,
            {"area_m2": 0.0, "chapas_equivalentes": 0.0, "chapas_inteiras": 0.0},
        )
        resumo_material["area_m2"] += area_linha_m2
        resumo_material["chapas_equivalentes"] += chapas_equivalentes_linha

    if not linhas_validas:
        raise ValueError("Nenhuma linha válida para calcular.")

    total_area_m2 = total_area_mm2 / 1_000_000
    chapas_equivalentes = total_area_mm2 / area_chapa_mm2
    chapas_inteiras = math.ceil(chapas_equivalentes)
    percentual_ultima_chapa = (chapas_equivalentes % 1) * 100
    if chapas_equivalentes > 0 and percentual_ultima_chapa == 0:
        percentual_ultima_chapa = 100

    resumo_por_material = []
    for material, resumo in sorted(por_material.items()):
        resumo["chapas_inteiras"] = math.ceil(resumo["chapas_equivalentes"])
        resumo_por_material.append(
            {
                "material": material,
                "area_m2": round(resumo["area_m2"], 4),
                "chapas_equivalentes": round(resumo["chapas_equivalentes"], 4),
                "chapas_inteiras": int(resumo["chapas_inteiras"]),
            }
        )

    return {
        "chapa": {
            "comprimento_mm": round(chapa_comprimento_mm, 3),
            "largura_mm": round(chapa_largura_mm, 3),
            "area_m2": round(area_chapa_m2, 4),
        },
        "totais": {
            "area_perdida_m2": round(total_area_m2, 4),
            "chapas_equivalentes": round(chapas_equivalentes, 4),
            "chapas_inteiras": int(chapas_inteiras),
            "percentual_de_uma_chapa": round(chapas_equivalentes * 100, 2),
            "percentual_ultima_chapa": round(percentual_ultima_chapa, 2),
            "custo_estimado": round(chapas_equivalentes * custo_chapa_float, 2),
        },
        "linhas": [asdict(linha) for linha in linhas_validas],
        "por_material": resumo_por_material,
        "erros": erros,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/calcular")
def calcular():
    try:
        resultado = calcular_perdas(request.get_json(force=True) or {})
        return jsonify({"ok": True, "resultado": resultado})
    except ValueError as exc:
        return jsonify({"ok": False, "erro": str(exc)}), 400


@app.post("/exportar-csv")
def exportar_csv():
    try:
        resultado = calcular_perdas(request.get_json(force=True) or {})
    except ValueError as exc:
        return jsonify({"ok": False, "erro": str(exc)}), 400

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Material", "Comprimento mm", "Largura mm", "Quantidade", "Area m2", "Chapas equivalentes"])
    for linha in resultado["linhas"]:
        writer.writerow([
            linha["material"],
            linha["comprimento_mm"],
            linha["largura_mm"],
            linha["quantidade"],
            linha["area_m2"],
            linha["chapas_equivalentes"],
        ])
    writer.writerow([])
    writer.writerow(["Total area perdida m2", resultado["totais"]["area_perdida_m2"]])
    writer.writerow(["Chapas equivalentes", resultado["totais"]["chapas_equivalentes"]])
    writer.writerow(["Chapas inteiras", resultado["totais"]["chapas_inteiras"]])
    writer.writerow(["Custo estimado", resultado["totais"]["custo_estimado"]])

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=relatorio_perda_chapas.csv"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

from __future__ import annotations

import csv
import io
import math
import os
from dataclasses import asdict, dataclass
from typing import Any

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


INDEX_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculadora de Perda e Retorno de Sobras</title>
  <style>
    :root {
      --bg: #f4f6fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #667085;
      --primary: #1f6feb;
      --primary-dark: #1857b6;
      --border: #dce2ef;
      --success-bg: #ecfdf3;
      --success: #067647;
      --warning-bg: #fff7ed;
      --warning: #b45309;
      --danger: #b42318;
      --info-bg: #eff8ff;
      --info: #175cd3;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 48%);
      color: var(--text);
    }

    .container {
      width: min(1220px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1fr 310px;
      gap: 24px;
      align-items: stretch;
      margin-bottom: 24px;
    }

    .eyebrow {
      color: var(--primary);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 13px;
      margin: 0 0 8px;
    }

    h1 {
      font-size: clamp(31px, 5vw, 54px);
      line-height: 1;
      margin: 0 0 16px;
    }

    .subtitle {
      font-size: 18px;
      color: var(--muted);
      max-width: 800px;
      margin: 0;
    }

    .hero-card, .card, .resultado {
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid var(--border);
      border-radius: 22px;
      box-shadow: 0 18px 50px rgba(20, 34, 66, 0.08);
    }

    .hero-card {
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 8px;
    }

    .hero-card span, .hero-card small, .card p, .hint {
      color: var(--muted);
    }

    .hero-card strong {
      font-size: 26px;
    }

    .card, .resultado {
      padding: 24px;
      margin-bottom: 20px;
    }

    h2 {
      margin: 0 0 16px;
      font-size: 22px;
    }

    h3 {
      margin: 24px 0 12px;
      font-size: 19px;
    }

    .grid {
      display: grid;
      gap: 14px;
    }

    .grid-2 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: repeat(3, 1fr); }
    .grid-4 { grid-template-columns: repeat(4, 1fr); }
    .grid-5 { grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr; }

    label {
      display: flex;
      flex-direction: column;
      gap: 7px;
      font-weight: 700;
      color: #26324a;
    }

    input, select, textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 13px;
      font: inherit;
      background: #fff;
      color: var(--text);
    }

    textarea {
      resize: vertical;
      min-height: 92px;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--primary);
      outline: 3px solid rgba(31, 111, 235, 0.14);
    }

    .checkbox-line {
      flex-direction: row;
      align-items: center;
      gap: 10px;
      margin-top: 29px;
    }

    .checkbox-line input {
      width: 18px;
      height: 18px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      margin-bottom: 18px;
    }

    .section-header p { margin: 4px 0 0; }

    .paste-box {
      display: grid;
      grid-template-columns: 1fr 230px;
      gap: 14px;
      margin-bottom: 18px;
      align-items: end;
    }

    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: white;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 850px;
    }

    th, td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }

    th {
      background: #f8faff;
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    tr:last-child td { border-bottom: 0; }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }

    .small-actions {
      align-content: end;
      margin-top: 0;
    }

    button {
      border: 0;
      background: var(--primary);
      color: white;
      font-weight: 800;
      border-radius: 12px;
      padding: 12px 16px;
      cursor: pointer;
      transition: transform 0.12s ease, background 0.12s ease;
    }

    button:hover {
      background: var(--primary-dark);
      transform: translateY(-1px);
    }

    button.secondary {
      background: #eaf1ff;
      color: var(--primary);
    }

    button.secondary:hover { background: #dbe8ff; }

    button.ghost {
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
    }

    button.icon {
      width: 38px;
      height: 38px;
      padding: 0;
      border-radius: 50%;
      background: #fee4e2;
      color: var(--danger);
      font-size: 22px;
      line-height: 1;
    }

    .hidden { display: none; }

    .metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 22px;
    }

    .metric {
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px;
      background: #fbfcff;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 7px;
    }

    .metric strong {
      display: block;
      font-size: 25px;
    }

    .alert {
      border-radius: 14px;
      padding: 12px 14px;
      margin-bottom: 16px;
      background: var(--warning-bg);
      color: var(--warning);
      font-weight: 700;
    }

    .success { background: var(--success-bg); color: var(--success); }
    .info { background: var(--info-bg); color: var(--info); }

    .muted { color: var(--muted); }

    @media (max-width: 920px) {
      .hero, .grid-2, .grid-3, .grid-4, .grid-5, .paste-box, .metrics {
        grid-template-columns: 1fr;
      }
      .section-header { flex-direction: column; }
      .checkbox-line { margin-top: 0; }
    }
  </style>
</head>
<body>
  <main class="container">
    <section class="hero">
      <div>
        <p class="eyebrow">Marcenaria / Corte de chapas</p>
        <h1>Calculadora de perda e retorno de sobras</h1>
        <p class="subtitle">Informe as sobras geradas no corte, veja quantas chapas equivalentes foram perdidas e calcule quantas peças podem ser feitas com essas sobras, junto com o valor de retorno.</p>
      </div>
      <div class="hero-card">
        <span>Chapa padrão</span>
        <strong>2750 × 1850 mm</strong>
        <small>Você pode alterar a medida da chapa e da peça reaproveitada.</small>
      </div>
    </section>

    <section class="card">
      <h2>1. Dados da chapa</h2>
      <div class="grid grid-4">
        <label>
          Unidade usada nas medidas
          <select id="unidade">
            <option value="mm" selected>Milímetros</option>
            <option value="cm">Centímetros</option>
            <option value="m">Metros</option>
          </select>
        </label>
        <label>
          Comprimento da chapa
          <input id="chapaComprimento" type="text" value="2750" inputmode="decimal">
        </label>
        <label>
          Largura da chapa
          <input id="chapaLargura" type="text" value="1850" inputmode="decimal">
        </label>
        <label>
          Custo por chapa, opcional
          <input id="custoChapa" type="text" placeholder="Ex.: 180,00" inputmode="decimal">
        </label>
      </div>
    </section>

    <section class="card">
      <h2>2. Peça que será feita usando a sobra</h2>
      <p class="hint">Exemplo: uma peça pequena, régua, lateral, fundo, sarrafo, componente interno etc. O sistema calcula quantas peças cabem dentro de cada sobra informada.</p>
      <div class="grid grid-5">
        <label>
          Nome/código da peça
          <input id="pecaNome" type="text" value="Peça reaproveitada" placeholder="Ex.: Travessa 120x80">
        </label>
        <label>
          Comprimento da peça
          <input id="pecaComprimento" type="text" placeholder="Ex.: 300" inputmode="decimal">
        </label>
        <label>
          Largura da peça
          <input id="pecaLargura" type="text" placeholder="Ex.: 120" inputmode="decimal">
        </label>
        <label>
          Valor de retorno por peça
          <input id="valorPeca" type="text" placeholder="Ex.: 12,50" inputmode="decimal">
        </label>
        <label class="checkbox-line">
          <input id="permitirGiro" type="checkbox" checked>
          Permitir giro 90°
        </label>
      </div>
      <p class="hint">Se deixar a medida da peça em branco, o sistema calcula somente a perda em chapas.</p>
    </section>

    <section class="card">
      <div class="section-header">
        <div>
          <h2>3. Sobras / peças perdidas</h2>
          <p>Preencha linha por linha ou cole dados do Excel no campo abaixo.</p>
        </div>
        <button type="button" class="secondary" onclick="adicionarLinha()">+ Adicionar linha</button>
      </div>

      <div class="paste-box">
        <label>
          Colar dados do Excel
          <textarea id="dadosColados" rows="4" placeholder="Formato aceito: Material [TAB] Comprimento [TAB] Largura [TAB] Quantidade&#10;Ex.: MDF 15    500    300    4"></textarea>
        </label>
        <div class="actions small-actions">
          <button type="button" class="secondary" onclick="importarColagem()">Importar colagem</button>
          <button type="button" class="ghost" onclick="limparLinhas()">Limpar linhas</button>
        </div>
      </div>

      <div class="table-wrap">
        <table id="tabelaPerdas">
          <thead>
            <tr>
              <th>Material</th>
              <th>Comprimento da sobra</th>
              <th>Largura da sobra</th>
              <th>Qtd.</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="linhasPerdas"></tbody>
        </table>
      </div>

      <div class="actions">
        <button type="button" onclick="calcular()">Calcular perda e retorno</button>
        <button type="button" class="secondary" onclick="exportarCSV()">Exportar CSV</button>
      </div>
    </section>

    <section id="resultado" class="resultado hidden"></section>
  </main>

  <template id="linhaTemplate">
    <tr>
      <td><input class="material" type="text" placeholder="MDF 15"></td>
      <td><input class="comprimento" type="text" inputmode="decimal" placeholder="Ex.: 500"></td>
      <td><input class="largura" type="text" inputmode="decimal" placeholder="Ex.: 300"></td>
      <td><input class="quantidade" type="number" min="1" step="1" placeholder="1"></td>
      <td><button type="button" class="icon" onclick="this.closest('tr').remove()">×</button></td>
    </tr>
  </template>

  <script>
    function adicionarLinha(dados = {}) {
      const tbody = document.getElementById('linhasPerdas');
      const template = document.getElementById('linhaTemplate');
      const clone = template.content.cloneNode(true);
      clone.querySelector('.material').value = dados.material || '';
      clone.querySelector('.comprimento').value = dados.comprimento || '';
      clone.querySelector('.largura').value = dados.largura || '';
      clone.querySelector('.quantidade').value = dados.quantidade || '';
      tbody.appendChild(clone);
    }

    function limparLinhas() {
      document.getElementById('linhasPerdas').innerHTML = '';
      adicionarLinha();
    }

    function importarColagem() {
      const texto = document.getElementById('dadosColados').value.trim();
      if (!texto) return;
      const linhas = texto.split(/\r?\n/).filter(Boolean);
      const tbody = document.getElementById('linhasPerdas');
      tbody.innerHTML = '';

      linhas.forEach((linha) => {
        const colunas = linha.split(/\t|;/).map((coluna) => coluna.trim());
        if (colunas.length >= 4) {
          adicionarLinha({ material: colunas[0], comprimento: colunas[1], largura: colunas[2], quantidade: colunas[3] });
        } else if (colunas.length === 3) {
          adicionarLinha({ material: 'Sem material', comprimento: colunas[0], largura: colunas[1], quantidade: colunas[2] });
        }
      });
    }

    function valor(id) {
      return document.getElementById(id).value;
    }

    function coletarPayload() {
      const linhas = Array.from(document.querySelectorAll('#linhasPerdas tr')).map((tr) => ({
        material: tr.querySelector('.material').value,
        comprimento: tr.querySelector('.comprimento').value,
        largura: tr.querySelector('.largura').value,
        quantidade: tr.querySelector('.quantidade').value,
      }));

      return {
        unidade: valor('unidade'),
        chapa_comprimento: valor('chapaComprimento'),
        chapa_largura: valor('chapaLargura'),
        custo_chapa: valor('custoChapa'),
        peca_reaproveitamento: {
          nome: valor('pecaNome'),
          comprimento: valor('pecaComprimento'),
          largura: valor('pecaLargura'),
          valor_unitario: valor('valorPeca'),
          permitir_giro: document.getElementById('permitirGiro').checked,
        },
        linhas,
      };
    }

    function formatarNumero(valor, casas = 2) {
      return Number(valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
    }

    function dinheiro(valor) {
      return Number(valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    async function calcular() {
      const resultadoDiv = document.getElementById('resultado');
      resultadoDiv.classList.remove('hidden');
      resultadoDiv.innerHTML = '<div class="alert info">Calculando...</div>';

      try {
        const resposta = await fetch('/calcular', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(coletarPayload()),
        });
        const dados = await resposta.json();
        if (!resposta.ok || !dados.ok) {
          resultadoDiv.innerHTML = `<div class="alert">${dados.erro || 'Erro ao calcular.'}</div>`;
          return;
        }
        renderizarResultado(dados.resultado);
      } catch (erro) {
        resultadoDiv.innerHTML = '<div class="alert">Não foi possível conversar com o servidor. Verifique o deploy.</div>';
      }
    }

    function renderizarResultado(resultado) {
      const resultadoDiv = document.getElementById('resultado');
      const totais = resultado.totais;
      const reap = resultado.reaproveitamento;

      const errosHtml = resultado.erros.length
        ? `<div class="alert">Algumas linhas foram ignoradas:<br>${resultado.erros.map((erro) => `• ${erro}`).join('<br>')}</div>`
        : '';

      const linhasHtml = resultado.linhas.map((linha) => `
        <tr>
          <td>${linha.material}</td>
          <td>${formatarNumero(linha.comprimento_mm, 0)} mm</td>
          <td>${formatarNumero(linha.largura_mm, 0)} mm</td>
          <td>${linha.quantidade}</td>
          <td>${formatarNumero(linha.area_m2, 4)} m²</td>
          <td>${formatarNumero(linha.chapas_equivalentes, 4)}</td>
          <td>${linha.pecas_possiveis_total}</td>
          <td>${linha.melhor_orientacao}</td>
        </tr>
      `).join('');

      const materialHtml = resultado.por_material.map((item) => `
        <tr>
          <td>${item.material}</td>
          <td>${formatarNumero(item.area_m2, 4)} m²</td>
          <td>${formatarNumero(item.chapas_equivalentes, 4)}</td>
          <td>${item.chapas_inteiras}</td>
          <td>${item.pecas_possiveis}</td>
          <td>${dinheiro(item.valor_retorno)}</td>
        </tr>
      `).join('');

      const blocoReaproveitamento = reap.calculado ? `
        <h2>Retorno usando as sobras</h2>
        <div class="metrics">
          <div class="metric"><span>Peças possíveis</span><strong>${reap.pecas_possiveis_total}</strong></div>
          <div class="metric"><span>Retorno estimado</span><strong>${dinheiro(reap.valor_retorno_total)}</strong></div>
          <div class="metric"><span>Área reaproveitada</span><strong>${formatarNumero(reap.area_reaproveitada_m2, 4)} m²</strong></div>
          <div class="metric"><span>Aproveitamento das sobras</span><strong>${formatarNumero(reap.percentual_reaproveitamento_sobras, 2)}%</strong></div>
        </div>
        <div class="alert info">
          Peça calculada: ${reap.nome} — ${formatarNumero(reap.comprimento_mm, 0)} × ${formatarNumero(reap.largura_mm, 0)} mm. ${reap.permitir_giro ? 'O giro 90° foi permitido.' : 'O giro 90° não foi permitido.'}
        </div>
        <div class="metrics">
          <div class="metric"><span>Sobra final após reaproveitar</span><strong>${formatarNumero(reap.area_sobra_final_m2, 4)} m²</strong></div>
          <div class="metric"><span>Chapas recuperadas</span><strong>${formatarNumero(reap.chapas_recuperadas_equivalentes, 4)}</strong></div>
          <div class="metric"><span>Custo perdido bruto</span><strong>${dinheiro(totais.custo_estimado)}</strong></div>
          <div class="metric"><span>Resultado líquido estimado</span><strong>${dinheiro(reap.resultado_liquido_estimado)}</strong></div>
        </div>
      ` : `
        <div class="alert info">
          Para calcular quantas peças dá para fabricar com as sobras, preencha o comprimento e a largura da peça no bloco 2.
        </div>
      `;

      resultadoDiv.innerHTML = `
        ${errosHtml}
        <h2>Perda em chapas</h2>
        <div class="metrics">
          <div class="metric"><span>Área perdida</span><strong>${formatarNumero(totais.area_perdida_m2, 4)} m²</strong></div>
          <div class="metric"><span>Chapas equivalentes</span><strong>${formatarNumero(totais.chapas_equivalentes, 4)}</strong></div>
          <div class="metric"><span>Chapas inteiras</span><strong>${totais.chapas_inteiras}</strong></div>
          <div class="metric"><span>Custo perdido estimado</span><strong>${dinheiro(totais.custo_estimado)}</strong></div>
        </div>
        <div class="alert success">
          A perda informada equivale a ${formatarNumero(totais.percentual_de_uma_chapa, 2)}% de uma chapa padrão. Convertendo para chapa inteira: ${totais.chapas_inteiras} chapa(s).
        </div>

        ${blocoReaproveitamento}

        <h2>Resumo por material</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Material</th><th>Área perdida</th><th>Chapas equivalentes</th><th>Chapas inteiras</th><th>Peças possíveis</th><th>Retorno</th></tr></thead>
            <tbody>${materialHtml}</tbody>
          </table>
        </div>

        <h2 style="margin-top: 24px;">Detalhe das sobras</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Material</th><th>Comprimento</th><th>Largura</th><th>Qtd.</th><th>Área</th><th>Chapas equivalentes</th><th>Peças possíveis</th><th>Orientação</th></tr></thead>
            <tbody>${linhasHtml}</tbody>
          </table>
        </div>
      `;
    }

    async function exportarCSV() {
      try {
        const resposta = await fetch('/exportar-csv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(coletarPayload()),
        });
        if (!resposta.ok) {
          const dados = await resposta.json();
          alert(dados.erro || 'Erro ao exportar CSV.');
          return;
        }
        const blob = await resposta.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'relatorio_perda_retorno_sobras.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      } catch (erro) {
        alert('Não foi possível exportar o CSV.');
      }
    }

    document.addEventListener('DOMContentLoaded', () => {
      adicionarLinha({ material: 'MDF 15', comprimento: '500', largura: '300', quantidade: '4' });
      adicionarLinha({ material: 'MDF 15', comprimento: '800', largura: '250', quantidade: '2' });
    });
  </script>
</body>
</html>
"""


@dataclass
class LinhaPerda:
    material: str
    comprimento_mm: float
    largura_mm: float
    quantidade: int
    area_m2: float
    chapas_equivalentes: float
    pecas_possiveis_por_sobra: int
    pecas_possiveis_total: int
    melhor_orientacao: str
    valor_retorno: float


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


def parse_numero_opcional(valor: Any, campo: str, padrao: float = 0.0) -> float:
    if valor in (None, ""):
        return padrao
    return parse_numero(valor, campo)


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


def calcular_pecas_em_sobra(
    sobra_comprimento_mm: float,
    sobra_largura_mm: float,
    peca_comprimento_mm: float | None,
    peca_largura_mm: float | None,
    permitir_giro: bool,
) -> tuple[int, str]:
    if not peca_comprimento_mm or not peca_largura_mm:
        return 0, "não calculado"

    normal = math.floor(sobra_comprimento_mm / peca_comprimento_mm) * math.floor(
        sobra_largura_mm / peca_largura_mm
    )
    melhor = normal
    orientacao = "normal"

    if permitir_giro:
        girada = math.floor(sobra_comprimento_mm / peca_largura_mm) * math.floor(
            sobra_largura_mm / peca_comprimento_mm
        )
        if girada > melhor:
            melhor = girada
            orientacao = "girada 90°"
        elif girada == melhor and girada > 0:
            orientacao = "normal ou girada"

    return int(melhor), orientacao if melhor > 0 else "não cabe"


def calcular_perdas(payload: dict[str, Any]) -> dict[str, Any]:
    unidade = payload.get("unidade", "mm")
    chapa_comprimento_mm = converter_para_mm(
        payload.get("chapa_comprimento", 2750), unidade, "comprimento da chapa"
    )
    chapa_largura_mm = converter_para_mm(
        payload.get("chapa_largura", 1850), unidade, "largura da chapa"
    )
    custo_chapa_float = parse_numero_opcional(payload.get("custo_chapa"), "custo da chapa", 0.0)

    area_chapa_mm2 = chapa_comprimento_mm * chapa_largura_mm
    area_chapa_m2 = area_chapa_mm2 / 1_000_000

    peca_payload = payload.get("peca_reaproveitamento") or {}
    peca_nome = str(peca_payload.get("nome") or "Peça reaproveitada").strip() or "Peça reaproveitada"
    peca_comprimento_mm: float | None = None
    peca_largura_mm: float | None = None
    peca_calculada = False

    peca_comprimento_valor = peca_payload.get("comprimento")
    peca_largura_valor = peca_payload.get("largura")
    if peca_comprimento_valor not in (None, "") or peca_largura_valor not in (None, ""):
        peca_comprimento_mm = converter_para_mm(peca_comprimento_valor, unidade, "comprimento da peça reaproveitada")
        peca_largura_mm = converter_para_mm(peca_largura_valor, unidade, "largura da peça reaproveitada")
        peca_calculada = True

    valor_unitario_peca = parse_numero_opcional(peca_payload.get("valor_unitario"), "valor de retorno por peça", 0.0)
    permitir_giro = bool(peca_payload.get("permitir_giro", True))

    linhas_payload = payload.get("linhas", [])
    if not isinstance(linhas_payload, list) or not linhas_payload:
        raise ValueError("Informe pelo menos uma sobra ou peça perdida.")

    linhas_validas: list[LinhaPerda] = []
    erros: list[str] = []
    total_area_mm2 = 0.0
    total_pecas_possiveis = 0
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

        pecas_por_sobra, orientacao = calcular_pecas_em_sobra(
            comprimento_mm,
            largura_mm,
            peca_comprimento_mm,
            peca_largura_mm,
            permitir_giro,
        )
        pecas_total_linha = pecas_por_sobra * quantidade
        total_pecas_possiveis += pecas_total_linha
        valor_retorno_linha = pecas_total_linha * valor_unitario_peca

        linhas_validas.append(
            LinhaPerda(
                material=material,
                comprimento_mm=round(comprimento_mm, 3),
                largura_mm=round(largura_mm, 3),
                quantidade=quantidade,
                area_m2=round(area_linha_m2, 4),
                chapas_equivalentes=round(chapas_equivalentes_linha, 4),
                pecas_possiveis_por_sobra=pecas_por_sobra,
                pecas_possiveis_total=pecas_total_linha,
                melhor_orientacao=orientacao,
                valor_retorno=round(valor_retorno_linha, 2),
            )
        )

        resumo_material = por_material.setdefault(
            material,
            {
                "area_m2": 0.0,
                "chapas_equivalentes": 0.0,
                "chapas_inteiras": 0.0,
                "pecas_possiveis": 0.0,
                "valor_retorno": 0.0,
            },
        )
        resumo_material["area_m2"] += area_linha_m2
        resumo_material["chapas_equivalentes"] += chapas_equivalentes_linha
        resumo_material["pecas_possiveis"] += pecas_total_linha
        resumo_material["valor_retorno"] += valor_retorno_linha

    if not linhas_validas:
        raise ValueError("Nenhuma linha válida para calcular.")

    total_area_m2 = total_area_mm2 / 1_000_000
    chapas_equivalentes = total_area_mm2 / area_chapa_mm2
    chapas_inteiras = math.ceil(chapas_equivalentes)
    percentual_ultima_chapa = (chapas_equivalentes % 1) * 100
    if chapas_equivalentes > 0 and percentual_ultima_chapa == 0:
        percentual_ultima_chapa = 100

    area_peca_mm2 = 0.0
    if peca_calculada and peca_comprimento_mm and peca_largura_mm:
        area_peca_mm2 = peca_comprimento_mm * peca_largura_mm
    area_reaproveitada_mm2 = total_pecas_possiveis * area_peca_mm2
    area_reaproveitada_m2 = area_reaproveitada_mm2 / 1_000_000
    area_sobra_final_m2 = max(total_area_m2 - area_reaproveitada_m2, 0.0)
    percentual_reaproveitamento_sobras = (
        (area_reaproveitada_m2 / total_area_m2) * 100 if total_area_m2 > 0 else 0.0
    )
    valor_retorno_total = total_pecas_possiveis * valor_unitario_peca
    custo_perdido_estimado = chapas_equivalentes * custo_chapa_float
    resultado_liquido_estimado = valor_retorno_total - custo_perdido_estimado

    resumo_por_material = []
    for material, resumo in sorted(por_material.items()):
        resumo["chapas_inteiras"] = math.ceil(resumo["chapas_equivalentes"])
        resumo_por_material.append(
            {
                "material": material,
                "area_m2": round(resumo["area_m2"], 4),
                "chapas_equivalentes": round(resumo["chapas_equivalentes"], 4),
                "chapas_inteiras": int(resumo["chapas_inteiras"]),
                "pecas_possiveis": int(resumo["pecas_possiveis"]),
                "valor_retorno": round(resumo["valor_retorno"], 2),
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
            "custo_estimado": round(custo_perdido_estimado, 2),
        },
        "reaproveitamento": {
            "calculado": peca_calculada,
            "nome": peca_nome,
            "comprimento_mm": round(peca_comprimento_mm or 0.0, 3),
            "largura_mm": round(peca_largura_mm or 0.0, 3),
            "valor_unitario": round(valor_unitario_peca, 2),
            "permitir_giro": permitir_giro,
            "pecas_possiveis_total": int(total_pecas_possiveis),
            "valor_retorno_total": round(valor_retorno_total, 2),
            "area_reaproveitada_m2": round(area_reaproveitada_m2, 4),
            "area_sobra_final_m2": round(area_sobra_final_m2, 4),
            "percentual_reaproveitamento_sobras": round(percentual_reaproveitamento_sobras, 2),
            "chapas_recuperadas_equivalentes": round(area_reaproveitada_mm2 / area_chapa_mm2 if area_chapa_mm2 > 0 else 0.0, 4),
            "resultado_liquido_estimado": round(resultado_liquido_estimado, 2),
        },
        "linhas": [asdict(linha) for linha in linhas_validas],
        "por_material": resumo_por_material,
        "erros": erros,
    }


@app.get("/")
def index():
    return INDEX_HTML


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
    writer.writerow(["Relatorio de perda e retorno de sobras"])
    writer.writerow([])
    writer.writerow(["Area perdida m2", resultado["totais"]["area_perdida_m2"]])
    writer.writerow(["Chapas equivalentes perdidas", resultado["totais"]["chapas_equivalentes"]])
    writer.writerow(["Chapas inteiras", resultado["totais"]["chapas_inteiras"]])
    writer.writerow(["Custo perdido estimado", resultado["totais"]["custo_estimado"]])
    writer.writerow([])
    writer.writerow(["Peca reaproveitada", resultado["reaproveitamento"]["nome"]])
    writer.writerow(["Pecas possiveis", resultado["reaproveitamento"]["pecas_possiveis_total"]])
    writer.writerow(["Valor de retorno", resultado["reaproveitamento"]["valor_retorno_total"]])
    writer.writerow(["Area reaproveitada m2", resultado["reaproveitamento"]["area_reaproveitada_m2"]])
    writer.writerow(["Aproveitamento das sobras %", resultado["reaproveitamento"]["percentual_reaproveitamento_sobras"]])
    writer.writerow(["Resultado liquido estimado", resultado["reaproveitamento"]["resultado_liquido_estimado"]])
    writer.writerow([])
    writer.writerow([
        "Material",
        "Comprimento mm",
        "Largura mm",
        "Quantidade",
        "Area m2",
        "Chapas equivalentes",
        "Pecas possiveis por sobra",
        "Pecas possiveis total",
        "Orientacao",
        "Valor retorno",
    ])
    for linha in resultado["linhas"]:
        writer.writerow([
            linha["material"],
            linha["comprimento_mm"],
            linha["largura_mm"],
            linha["quantidade"],
            linha["area_m2"],
            linha["chapas_equivalentes"],
            linha["pecas_possiveis_por_sobra"],
            linha["pecas_possiveis_total"],
            linha["melhor_orientacao"],
            linha["valor_retorno"],
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=relatorio_perda_retorno_sobras.csv"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

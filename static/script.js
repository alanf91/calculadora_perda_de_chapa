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
      adicionarLinha({
        material: colunas[0],
        comprimento: colunas[1],
        largura: colunas[2],
        quantidade: colunas[3],
      });
    } else if (colunas.length === 3) {
      adicionarLinha({
        material: '',
        comprimento: colunas[0],
        largura: colunas[1],
        quantidade: colunas[2],
      });
    }
  });

  if (!tbody.children.length) adicionarLinha();
}

function coletarPayload() {
  const linhas = [...document.querySelectorAll('#linhasPerdas tr')].map((tr) => ({
    material: tr.querySelector('.material').value,
    comprimento: tr.querySelector('.comprimento').value,
    largura: tr.querySelector('.largura').value,
    quantidade: tr.querySelector('.quantidade').value,
  })).filter((linha) => linha.comprimento || linha.largura || linha.quantidade);

  return {
    unidade: document.getElementById('unidade').value,
    chapa_comprimento: document.getElementById('chapaComprimento').value,
    chapa_largura: document.getElementById('chapaLargura').value,
    custo_chapa: document.getElementById('custoChapa').value,
    linhas,
  };
}

function formatarNumero(valor, casas = 2) {
  return Number(valor).toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  });
}

async function calcular() {
  const resultadoBox = document.getElementById('resultado');
  resultadoBox.classList.remove('hidden');
  resultadoBox.innerHTML = '<div class="alert">Calculando...</div>';

  try {
    const resposta = await fetch('/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(coletarPayload()),
    });

    const dados = await resposta.json();
    if (!dados.ok) throw new Error(dados.erro || 'Erro ao calcular.');

    renderResultado(dados.resultado);
  } catch (erro) {
    resultadoBox.innerHTML = `<div class="alert">${erro.message}</div>`;
  }
}

function renderResultado(resultado) {
  const totais = resultado.totais;
  const resultadoBox = document.getElementById('resultado');

  const errosHtml = resultado.erros.length
    ? `<div class="alert">Algumas linhas foram ignoradas:<br>${resultado.erros.join('<br>')}</div>`
    : '';

  const materialHtml = resultado.por_material.map((item) => `
    <tr>
      <td>${item.material}</td>
      <td>${formatarNumero(item.area_m2, 4)} m²</td>
      <td>${formatarNumero(item.chapas_equivalentes, 4)}</td>
      <td>${item.chapas_inteiras}</td>
    </tr>
  `).join('');

  const linhasHtml = resultado.linhas.map((item) => `
    <tr>
      <td>${item.material}</td>
      <td>${formatarNumero(item.comprimento_mm, 0)} mm</td>
      <td>${formatarNumero(item.largura_mm, 0)} mm</td>
      <td>${item.quantidade}</td>
      <td>${formatarNumero(item.area_m2, 4)} m²</td>
      <td>${formatarNumero(item.chapas_equivalentes, 4)}</td>
    </tr>
  `).join('');

  resultadoBox.innerHTML = `
    ${errosHtml}
    <h2>Resultado</h2>
    <div class="metrics">
      <div class="metric"><span>Área perdida</span><strong>${formatarNumero(totais.area_perdida_m2, 4)} m²</strong></div>
      <div class="metric"><span>Chapas equivalentes</span><strong>${formatarNumero(totais.chapas_equivalentes, 4)}</strong></div>
      <div class="metric"><span>Chapas inteiras</span><strong>${totais.chapas_inteiras}</strong></div>
      <div class="metric"><span>Custo estimado</span><strong>R$ ${formatarNumero(totais.custo_estimado, 2)}</strong></div>
    </div>
    <div class="alert success">
      Você perdeu o equivalente a ${formatarNumero(totais.percentual_de_uma_chapa, 2)}% de uma chapa padrão. Para transformar em chapa inteira, considere ${totais.chapas_inteiras} chapa(s).
    </div>

    <h2>Resumo por material</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Material</th><th>Área perdida</th><th>Chapas equivalentes</th><th>Chapas inteiras</th></tr></thead>
        <tbody>${materialHtml}</tbody>
      </table>
    </div>

    <h2 style="margin-top: 24px;">Detalhe das perdas</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Material</th><th>Comprimento</th><th>Largura</th><th>Qtd.</th><th>Área</th><th>Chapas equivalentes</th></tr></thead>
        <tbody>${linhasHtml}</tbody>
      </table>
    </div>
  `;
}

async function exportarCSV() {
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
  a.download = 'relatorio_perda_chapas.csv';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', () => {
  adicionarLinha({ material: 'MDF 15', comprimento: '500', largura: '300', quantidade: '4' });
  adicionarLinha({ material: 'MDF 15', comprimento: '800', largura: '250', quantidade: '2' });
});

from flask import Flask, Response

app = Flask(__name__)

HTML = r'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculadora de Perda e Retorno de Chapas</title>
  <style>
    :root{
      --bg:#eef3fb; --card:#ffffff; --text:#0f1b32; --muted:#617087; --primary:#256ee8;
      --primary-soft:#e9f1ff; --border:#dbe4f0; --danger:#d93025; --ok:#138a45; --shadow:0 18px 45px rgba(15,27,50,.09);
    }
    *{box-sizing:border-box}
    body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--bg);color:var(--text)}
    .wrap{max-width:1240px;margin:0 auto;padding:24px}
    .hero{background:linear-gradient(135deg,#0f3f94,#256ee8);color:white;border-radius:26px;padding:28px;box-shadow:var(--shadow);margin-bottom:22px}
    h1{margin:0 0 8px;font-size:34px;line-height:1.1}
    h2{font-size:24px;margin:0 0 18px}
    h3{font-size:20px;margin:10px 0}
    p{color:var(--muted);font-size:16px;line-height:1.45}
    .hero p{color:#dfeaff;max-width:900px;margin:0}
    .card{background:var(--card);border:1px solid var(--border);border-radius:24px;padding:24px;box-shadow:var(--shadow);margin-bottom:22px}
    .grid{display:grid;gap:14px}
    .grid-4{grid-template-columns:repeat(4,minmax(0,1fr))}
    .grid-5{grid-template-columns:repeat(5,minmax(0,1fr))}
    label{font-weight:800;font-size:14px;display:block;margin:0 0 6px;color:#14213d}
    input,select,textarea{width:100%;border:1px solid var(--border);border-radius:12px;padding:12px 14px;font-size:16px;font-weight:700;color:var(--text);background:#fff;outline:none}
    input:focus,select:focus,textarea:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(37,110,232,.12)}
    textarea{min-height:100px;font-family:Consolas,monospace;resize:vertical;white-space:pre}
    .row-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px}
    button{border:0;border-radius:12px;padding:13px 18px;font-size:15px;font-weight:900;cursor:pointer;background:var(--primary-soft);color:var(--primary)}
    button.primary{background:var(--primary);color:#fff}
    button.secondary{background:#f5f8fc;color:#4e5b70;border:1px solid var(--border)}
    button.danger{background:#fff1f0;color:var(--danger);border:1px solid #ffd5d2}
    button:hover{filter:brightness(.98);transform:translateY(-1px)}
    .hint{font-size:14px;color:var(--muted);margin:8px 0 0}
    .table-wrap{overflow:auto;border:1px solid var(--border);border-radius:16px;background:#fff;margin-top:14px}
    table{width:100%;border-collapse:separate;border-spacing:0;min-width:900px}
    th{background:#f6f9fe;color:#617087;text-align:left;font-size:13px;padding:12px;border-bottom:1px solid var(--border);text-transform:uppercase}
    td{padding:10px;border-bottom:1px solid var(--border);vertical-align:middle}
    td input{border-radius:10px;padding:10px;font-size:15px}
    tr:last-child td{border-bottom:0}
    .mini{font-size:12px;color:var(--muted);font-weight:700}
    .results{display:none}
    .cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:12px}
    .metric{border:1px solid var(--border);background:#fbfdff;border-radius:18px;padding:16px}
    .metric .k{font-size:13px;text-transform:uppercase;color:var(--muted);font-weight:900;margin-bottom:8px}
    .metric .v{font-size:26px;font-weight:950;color:#101b31}
    .metric.good .v{color:var(--ok)}
    .metric.bad .v{color:var(--danger)}
    .alert{background:#fff9e6;border:1px solid #ffe29a;color:#6f5200;border-radius:16px;padding:14px;margin-top:12px;font-weight:700}
    .checkbox-line{display:flex;align-items:center;gap:10px;height:100%;padding-top:22px;font-weight:900;color:#14213d}
    .checkbox-line input{width:20px;height:20px}
    .split{display:grid;grid-template-columns:1.2fr .8fr;gap:14px;align-items:start}
    .footer{color:var(--muted);font-size:13px;text-align:center;margin:20px 0}
    .pill{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:6px 10px;margin-bottom:12px;font-weight:900}
    @media(max-width:900px){.grid-4,.grid-5,.cards,.split{grid-template-columns:1fr}.wrap{padding:14px}h1{font-size:26px}.card{padding:18px}}
  </style>
</head>
<body>
<div class="wrap">
  <section class="hero">
    <div class="pill">Versão corrigida: campos manuais + colagem do Excel + retorno da sobra</div>
    <h1>Calculadora de Perda e Retorno de Chapas</h1>
    <p>Informe a chapa, lance as sobras/peças perdidas manualmente ou cole do Excel, e calcule quantas chapas equivalentes foram perdidas, o custo da perda e o retorno possível reaproveitando a sobra.</p>
  </section>

  <section class="card">
    <h2>1. Dados da chapa inteira</h2>
    <div class="grid grid-4">
      <div>
        <label>Unidade de medida</label>
        <select id="unit">
          <option value="mm" selected>Milímetros</option>
          <option value="cm">Centímetros</option>
          <option value="m">Metros</option>
        </select>
      </div>
      <div>
        <label>Comprimento da chapa</label>
        <input id="sheetLen" type="text" value="2750" inputmode="decimal">
      </div>
      <div>
        <label>Largura da chapa</label>
        <input id="sheetWid" type="text" value="1850" inputmode="decimal">
      </div>
      <div>
        <label>Valor da chapa inteira (R$)</label>
        <input id="sheetCost" type="text" placeholder="Ex.: 330" inputmode="decimal">
      </div>
    </div>
  </section>

  <section class="card">
    <h2>2. Peça que será feita usando a sobra</h2>
    <p>Esta parte é opcional. Se preencher, o sistema calcula quantas peças cabem em cada sobra/perda e o valor de retorno.</p>
    <div class="grid grid-5">
      <div>
        <label>Nome/código da peça</label>
        <input id="reuseName" type="text" value="Peça reaproveitada">
      </div>
      <div>
        <label>Comprimento da peça</label>
        <input id="reuseLen" type="text" placeholder="Ex.: 300" inputmode="decimal">
      </div>
      <div>
        <label>Largura da peça</label>
        <input id="reuseWid" type="text" placeholder="Ex.: 80" inputmode="decimal">
      </div>
      <div>
        <label>Valor de retorno por peça (R$)</label>
        <input id="reuseValue" type="text" placeholder="Ex.: 12,50" inputmode="decimal">
      </div>
      <label class="checkbox-line"><input id="allowRotate" type="checkbox" checked> Permitir giro 90°</label>
    </div>
  </section>

  <section class="card">
    <div style="display:flex;justify-content:space-between;gap:14px;align-items:flex-start;flex-wrap:wrap">
      <div>
        <h2>3. Sobras / peças perdidas</h2>
        <p>Agora os campos manuais estão de volta. Você pode digitar linha por linha ou colar várias linhas do Excel.</p>
      </div>
      <button type="button" onclick="addRow()">+ Adicionar linha</button>
    </div>

    <div class="split">
      <div>
        <label>Colar dados do Excel</label>
        <textarea id="pasteBox" placeholder="Exemplo:&#10;MDF 15    1850    145    222&#10;MDF 15    330     160    8000"></textarea>
        <div class="hint">Formato aceito: <b>Material | Comprimento da sobra | Largura da sobra | Quantidade</b>. Pode colar separado por TAB, espaço, ponto e vírgula ou vírgula.</div>
      </div>
      <div class="row-actions" style="align-content:start;padding-top:20px">
        <button type="button" onclick="importPaste()">Importar colagem</button>
        <button class="secondary" type="button" onclick="clearRows()">Limpar linhas</button>
        <button class="secondary" type="button" onclick="fillExample()">Exemplo</button>
      </div>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:28%">Material</th>
            <th>Comprimento da sobra</th>
            <th>Largura da sobra</th>
            <th>Qtd.</th>
            <th style="width:120px">Ação</th>
          </tr>
        </thead>
        <tbody id="lossRows"></tbody>
      </table>
    </div>

    <div class="row-actions">
      <button class="primary" type="button" onclick="calculate()">Calcular perda e retorno</button>
      <button type="button" onclick="exportCSV()">Exportar CSV</button>
    </div>
  </section>

  <section class="card results" id="results">
    <h2>4. Resultado geral</h2>
    <div id="warnings"></div>
    <div class="cards">
      <div class="metric bad"><div class="k">Área perdida total</div><div class="v" id="rAreaLost">-</div></div>
      <div class="metric bad"><div class="k">Chapas equivalentes perdidas</div><div class="v" id="rSheetsEq">-</div></div>
      <div class="metric bad"><div class="k">Chapas inteiras equivalentes</div><div class="v" id="rSheetsWhole">-</div></div>
      <div class="metric bad"><div class="k">Custo estimado da perda</div><div class="v" id="rCostLost">-</div></div>
      <div class="metric good"><div class="k">Peças possíveis com a sobra</div><div class="v" id="rPieces">-</div></div>
      <div class="metric good"><div class="k">Valor total de retorno</div><div class="v" id="rReturn">-</div></div>
      <div class="metric"><div class="k">Área reaproveitada</div><div class="v" id="rAreaReused">-</div></div>
      <div class="metric"><div class="k">Perda líquida após retorno</div><div class="v" id="rNetLoss">-</div></div>
    </div>

    <h3>Detalhamento por linha</h3>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Material</th>
            <th>Sobra</th>
            <th>Qtd.</th>
            <th>Área perdida</th>
            <th>Chapas equiv.</th>
            <th>Peças por sobra</th>
            <th>Total peças</th>
            <th>Retorno</th>
          </tr>
        </thead>
        <tbody id="detailRows"></tbody>
      </table>
    </div>
  </section>

  <div class="footer">Sistema sem pastas: apenas app.py, requirements.txt, Procfile, render.yaml, runtime.txt e README.md.</div>
</div>

<script>
let lastResult = null;

function normNumber(value){
  if(value === null || value === undefined) return 0;
  const s = String(value).trim().replace(/\./g, '').replace(',', '.');
  const n = Number(s);
  return Number.isFinite(n) ? n : 0;
}
function fmtNum(n, dec=2){ return Number(n || 0).toLocaleString('pt-BR',{minimumFractionDigits:dec,maximumFractionDigits:dec}); }
function fmtMoney(n){ return (Number(n || 0)).toLocaleString('pt-BR',{style:'currency',currency:'BRL'}); }
function toMeters(v){
  const unit = document.getElementById('unit').value;
  v = normNumber(v);
  if(unit === 'mm') return v/1000;
  if(unit === 'cm') return v/100;
  return v;
}
function createInput(value='', placeholder=''){
  const input = document.createElement('input');
  input.type = 'text';
  input.value = value;
  input.placeholder = placeholder;
  input.inputMode = 'decimal';
  return input;
}
function addRow(material='', comp='', larg='', qtd=''){
  const tbody = document.getElementById('lossRows');
  const tr = document.createElement('tr');
  const tdMat = document.createElement('td');
  const tdComp = document.createElement('td');
  const tdLarg = document.createElement('td');
  const tdQtd = document.createElement('td');
  const tdAct = document.createElement('td');
  tdMat.appendChild(createInput(material, 'Ex.: MDF 15'));
  tdComp.appendChild(createInput(comp, 'Ex.: 1850'));
  tdLarg.appendChild(createInput(larg, 'Ex.: 145'));
  tdQtd.appendChild(createInput(qtd, 'Ex.: 222'));
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className='danger'; btn.textContent='Excluir';
  btn.onclick = () => { tr.remove(); if(!document.querySelector('#lossRows tr')) addRow(); };
  tdAct.appendChild(btn);
  tr.append(tdMat,tdComp,tdLarg,tdQtd,tdAct);
  tbody.appendChild(tr);
}
function clearRows(){
  document.getElementById('lossRows').innerHTML = '';
  addRow();
  document.getElementById('results').style.display = 'none';
  lastResult = null;
}
function fillExample(){
  document.getElementById('pasteBox').value = 'MDF 15\t1850\t145\t222\nMDF 15\t330\t160\t8000';
  importPaste();
}
function importPaste(){
  const text = document.getElementById('pasteBox').value.trim();
  if(!text){ alert('Cole os dados primeiro.'); return; }
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  if(!lines.length){ return; }
  document.getElementById('lossRows').innerHTML = '';
  let imported = 0;
  for(const line of lines){
    let parts = line.split(/\t|;|,/).map(p => p.trim()).filter(Boolean);
    if(parts.length < 4){ parts = line.split(/\s+/).map(p => p.trim()).filter(Boolean); }
    if(parts.length < 4) continue;
    const qtd = parts.pop();
    const larg = parts.pop();
    const comp = parts.pop();
    const material = parts.join(' ') || 'Material';
    addRow(material, comp, larg, qtd);
    imported++;
  }
  if(imported === 0){ addRow(); alert('Não consegui importar. Confira se cada linha tem: material, comprimento, largura e quantidade.'); }
}
function readRows(){
  const rows = [];
  document.querySelectorAll('#lossRows tr').forEach(tr => {
    const inputs = tr.querySelectorAll('input');
    const material = inputs[0].value.trim() || 'Sem material';
    const comp = normNumber(inputs[1].value);
    const larg = normNumber(inputs[2].value);
    const qtd = Math.floor(normNumber(inputs[3].value));
    if(comp > 0 && larg > 0 && qtd > 0){ rows.push({material, comp, larg, qtd}); }
  });
  return rows;
}
function piecesPerLeftover(sobraC, sobraL, pieceC, pieceL, rotate){
  if(pieceC <= 0 || pieceL <= 0) return {best:0, mode:'não informado', normal:0, rotated:0};
  const normal = Math.floor(sobraC / pieceC) * Math.floor(sobraL / pieceL);
  const rotated = rotate ? Math.floor(sobraC / pieceL) * Math.floor(sobraL / pieceC) : 0;
  if(rotated > normal) return {best:rotated, mode:'girado 90°', normal, rotated};
  return {best:normal, mode:'normal', normal, rotated};
}
function calculate(){
  const sheetLen = toMeters(document.getElementById('sheetLen').value);
  const sheetWid = toMeters(document.getElementById('sheetWid').value);
  const sheetCost = normNumber(document.getElementById('sheetCost').value);
  const sheetArea = sheetLen * sheetWid;
  const rows = readRows();
  const warnings = [];
  if(sheetArea <= 0) warnings.push('Informe comprimento e largura da chapa inteira.');
  if(rows.length === 0) warnings.push('Informe pelo menos uma sobra/perda com comprimento, largura e quantidade.');
  const reuseLenRaw = normNumber(document.getElementById('reuseLen').value);
  const reuseWidRaw = normNumber(document.getElementById('reuseWid').value);
  const reuseValue = normNumber(document.getElementById('reuseValue').value);
  const reuseFilled = reuseLenRaw > 0 && reuseWidRaw > 0;
  const rotate = document.getElementById('allowRotate').checked;
  if(!reuseFilled) warnings.push('Peça reaproveitada não informada: vou calcular somente perda em chapas e custo.');
  if(sheetCost <= 0) warnings.push('Valor da chapa não informado: o custo da perda ficará zerado.');
  if(warnings.length && (sheetArea <= 0 || rows.length === 0)){
    document.getElementById('warnings').innerHTML = '<div class="alert">' + warnings.join('<br>') + '</div>';
    document.getElementById('results').style.display = 'block';
    return;
  }

  const reuseLenM = toMeters(reuseLenRaw);
  const reuseWidM = toMeters(reuseWidRaw);
  const reuseArea = reuseLenM * reuseWidM;
  let totalAreaLost = 0, totalPieces = 0, totalAreaReused = 0, totalReturn = 0;
  const detail = [];

  for(const r of rows){
    const cM = toMeters(r.comp), lM = toMeters(r.larg);
    const areaOne = cM * lM;
    const areaLost = areaOne * r.qtd;
    totalAreaLost += areaLost;
    let p = {best:0,mode:'-',normal:0,rotated:0};
    if(reuseFilled){ p = piecesPerLeftover(r.comp, r.larg, reuseLenRaw, reuseWidRaw, rotate); }
    const totalP = p.best * r.qtd;
    const ret = totalP * reuseValue;
    const areaReuse = Math.min(totalP * reuseArea, areaLost);
    totalPieces += totalP;
    totalReturn += ret;
    totalAreaReused += areaReuse;
    detail.push({
      material:r.material,
      sobra:r.comp + ' x ' + r.larg,
      qtd:r.qtd,
      areaLost,
      sheetEq: sheetArea > 0 ? areaLost / sheetArea : 0,
      piecesPer:p.best,
      totalPieces:totalP,
      returnValue:ret,
      mode:p.mode
    });
  }

  const sheetsEq = sheetArea > 0 ? totalAreaLost / sheetArea : 0;
  const sheetsWhole = Math.ceil(sheetsEq);
  const costLost = sheetsEq * sheetCost;
  const netLoss = Math.max(0, costLost - totalReturn);

  document.getElementById('warnings').innerHTML = warnings.length ? '<div class="alert">' + warnings.join('<br>') + '</div>' : '';
  document.getElementById('rAreaLost').textContent = fmtNum(totalAreaLost, 3) + ' m²';
  document.getElementById('rSheetsEq').textContent = fmtNum(sheetsEq, 2);
  document.getElementById('rSheetsWhole').textContent = String(sheetsWhole);
  document.getElementById('rCostLost').textContent = fmtMoney(costLost);
  document.getElementById('rPieces').textContent = totalPieces.toLocaleString('pt-BR');
  document.getElementById('rReturn').textContent = fmtMoney(totalReturn);
  document.getElementById('rAreaReused').textContent = fmtNum(totalAreaReused, 3) + ' m²';
  document.getElementById('rNetLoss').textContent = fmtMoney(netLoss);

  const tbody = document.getElementById('detailRows');
  tbody.innerHTML = '';
  for(const d of detail){
    const tr = document.createElement('tr');
    tr.innerHTML = '<td><b>'+escapeHtml(d.material)+'</b></td>'+
      '<td>'+escapeHtml(d.sobra)+'</td>'+
      '<td>'+d.qtd.toLocaleString('pt-BR')+'</td>'+
      '<td>'+fmtNum(d.areaLost,3)+' m²</td>'+
      '<td>'+fmtNum(d.sheetEq,3)+'</td>'+
      '<td>'+d.piecesPer.toLocaleString('pt-BR')+' <div class="mini">'+escapeHtml(d.mode)+'</div></td>'+
      '<td><b>'+d.totalPieces.toLocaleString('pt-BR')+'</b></td>'+
      '<td>'+fmtMoney(d.returnValue)+'</td>';
    tbody.appendChild(tr);
  }

  lastResult = {totalAreaLost,sheetsEq,sheetsWhole,costLost,totalPieces,totalReturn,totalAreaReused,netLoss,detail};
  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({behavior:'smooth',block:'start'});
}
function escapeHtml(s){
  return String(s).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}
function exportCSV(){
  if(!lastResult){ calculate(); }
  if(!lastResult){ return; }
  const lines = [];
  lines.push(['Material','Sobra','Quantidade','Area perdida m2','Chapas equivalentes','Pecas por sobra','Total pecas','Retorno R$'].join(';'));
  for(const d of lastResult.detail){
    lines.push([d.material,d.sobra,d.qtd,fmtNum(d.areaLost,3),fmtNum(d.sheetEq,3),d.piecesPer,d.totalPieces,fmtNum(d.returnValue,2)].join(';'));
  }
  lines.push('');
  lines.push(['TOTAL','','',fmtNum(lastResult.totalAreaLost,3),fmtNum(lastResult.sheetsEq,3),'',lastResult.totalPieces,fmtNum(lastResult.totalReturn,2)].join(';'));
  const blob = new Blob(['\ufeff' + lines.join('\n')], {type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'relatorio_perda_retorno_chapas.csv'; a.click();
  URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', () => {
  addRow('MDF 15','1850','145','222');
  addRow('MDF 15','330','160','8000');
  addRow();
});
</script>
</body>
</html>'''

@app.route('/')
def index():
    return Response(HTML, mimetype='text/html; charset=utf-8')

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

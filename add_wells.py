path = '/Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal_v1.html'
with open(path) as f: c = f.read()

old = """function renderForcaPersonal(){
  return '<div>' +
    '<div style="font-size:10px;color:var(--cinza);margin-bottom:12px;line-height:1.5">Testes de força padronizados. Máximo de repetições em 1 minuto.</div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' +
    field('p-flexao','FLEXÃO (1 MIN)','reps','20') + field('p-barra','BARRA FIXA','reps','5') +"""

new = """function calcWells(){
  var dist = parseFloat(document.getElementById('p-wells').value);
  var idade = parseInt(document.getElementById('p-wells-idade').value)||30;
  var sexo = document.getElementById('p-wells-sexo').value;
  if(isNaN(dist)){ mostrarToast('Informe a distância!'); return; }
  var refM = {fraco:20, regular:25, bom:30, excelente:35};
  var refF = {fraco:23, regular:28, bom:33, excelente:38};
  var ref = sexo==='M' ? refM : refF;
  var classif, cor;
  if(dist>=ref.excelente){classif='Excelente';cor='var(--azul)';}
  else if(dist>=ref.bom){classif='Bom';cor='var(--verde)';}
  else if(dist>=ref.regular){classif='Regular';cor='var(--ouro)';}
  else{classif='Fraco';cor='var(--vermelho)';}
  document.getElementById('p-wells-res').innerHTML = resultBox('FLEXIBILIDADE — RESULTADO','var(--azul)',[
    {label:'Distância alcançada',val:dist+' cm'},{label:'Classificação',val:classif,cor:cor}
  ],'Wells & Dillon (1952) · ACSM Guidelines 2022');
}
function renderForcaPersonal(){
  return '<div>' +
    '<div style="background:rgba(75,159,255,.04);border:1px solid rgba(75,159,255,.15);border-radius:12px;padding:12px;margin-bottom:12px">' +
    '<div style="font-size:11px;color:var(--azul);font-weight:700;margin-bottom:4px">🧘 FLEXIBILIDADE — BANCO DE WELLS</div>' +
    '<div style="font-size:11px;color:var(--cinza);margin-bottom:8px;line-height:1.5">Sentado, pernas estendidas, empurrar a régua com as pontas dos dedos. Positivo = alcança além dos pés. Wells & Dillon (1952) · ACSM 2022.</div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' +
    field('p-wells','DISTÂNCIA','cm','25') + field('p-wells-idade','IDADE','anos','30') +
    '</div>' +
    '<div style="margin-top:8px"><div style="font-size:10px;color:var(--cinza);margin-bottom:3px">SEXO</div>' +
    '<select id="p-wells-sexo" style="width:100%;padding:8px;border-radius:8px;background:var(--bg);border:1px solid var(--borda);color:var(--texto);font-size:13px"><option value="M">Masculino</option><option value="F">Feminino</option></select></div>' +
    '<button onclick="calcWells()" style="width:100%;margin-top:8px;padding:10px;background:linear-gradient(135deg,var(--azul),#357ABD);border:none;border-radius:10px;color:#fff;font-family:Bebas Neue;font-size:15px;cursor:pointer">CALCULAR FLEXIBILIDADE</button>' +
    '<div id="p-wells-res" style="margin-top:8px"></div>' +
    '</div>' +
    '<div style="font-size:10px;color:var(--cinza);margin-bottom:12px;line-height:1.5;margin-top:12px">Testes de força padronizados. Máximo de repetições em 1 minuto.</div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' +
    field('p-flexao','FLEXÃO (1 MIN)','reps','20') + field('p-barra','BARRA FIXA','reps','5') +"""

if old in c:
    c = c.replace(old, new)
    with open(path, 'w') as f: f.write(c)
    print('OK!')
else:
    print('NAO ENCONTRADO')

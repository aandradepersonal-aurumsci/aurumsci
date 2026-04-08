path = '/Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal_v1.html'
with open(path) as f:
    c = f.read()

func = """
function mostrarRoteiro(){
  var h = '<div style="position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:300;padding:20px;overflow-y:auto" onclick="this.remove()">';
  h += '<div style="background:#12121A;border-radius:20px;padding:24px;max-width:400px;margin:40px auto;border:1px solid rgba(201,168,76,.3)" onclick="event.stopPropagation()">';
  h += '<div style="font-family:Bebas Neue;font-size:20px;color:var(--ouro2);margin-bottom:6px">📋 ROTEIRO DE AVALIAÇÃO</div>';
  h += '<div style="font-size:11px;color:var(--cinza);margin-bottom:14px;line-height:1.5">Siga esta ordem para não comprometer os resultados. VO2 sempre por último!</div>';
  var steps = [
    ['1','📝','ANAMNESE','Perfil, objetivos, histórico de saúde e patologias'],
    ['2','📸','POSTURAL','3 fotos — frente, lateral e costas. Aluno em repouso.'],
    ['3','📏','CIRCUNFERÊNCIAS','Pescoço, tórax, cintura, abdômen, quadril, braços, coxas'],
    ['4','⚖️','% GORDURA','Bioimpedância, compasso 3 ou 7 dobras, ou ultrassom 9 pontos'],
    ['5','💪','TESTES FÍSICOS','Flexibilidade, preensão, barra fixa, flexão, abdominal'],
    ['6','🦵','POTÊNCIA MMII','Sentar e levantar — 30 segundos, joelho a 90°'],
    ['7','🫁','VO2 MÁX','Cooper, Milha ou Step Up — meça FCR e PAR antes'],
    ['8','❤️','HRR','FC pico + FC 1 min + FC 2 min + PA pós esforço'],
  ];
  steps.forEach(function(s){
    h += '<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px">';
    h += '<div style="background:linear-gradient(135deg,var(--ouro),var(--ouro2));border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-family:Bebas Neue;font-size:13px;color:#0A0A0F;flex-shrink:0">' + s[0] + '</div>';
    h += '<div><div style="font-size:13px;font-weight:700;color:var(--texto)">' + s[1] + ' ' + s[2] + '</div>';
    h += '<div style="font-size:11px;color:var(--cinza);margin-top:1px">' + s[3] + '</div></div></div>';
  });
  h += '<div style="margin-top:6px;padding:8px;background:rgba(255,75,75,.08);border-radius:8px;font-size:11px;color:#FF6B6B">⚠️ VO2 sempre por último — evita contaminação dos outros testes.</div>';
  h += '<button onclick="this.closest(\'div[style*=fixed]\').remove()" style="width:100%;margin-top:14px;padding:12px;background:linear-gradient(135deg,var(--ouro),var(--ouro2));border:none;border-radius:10px;color:#0A0A0F;font-family:Bebas Neue;font-size:16px;cursor:pointer">ENTENDI ✓</button>';
  h += '</div></div>';
  document.body.insertAdjacentHTML('beforeend', h);
}
"""

if '\n</script>' in c:
    c = c.replace('\n</script>', func + '\n</script>', 1)
    with open(path, 'w') as f:
        f.write(c)
    print('OK!')
else:
    print('NAO ENCONTRADO')

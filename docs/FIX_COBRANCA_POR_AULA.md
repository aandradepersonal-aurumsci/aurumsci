# 🐛 BUG FIX — Cobrança POR AULA zerada

**Data descoberto:** 09/05/2026 (sessão noturna ~22:30)
**Descoberto por:** André (insistiu até comprovar)
**Status:** ✅ Investigação completa, ⏳ aguardando aplicação

---

## 🚨 PROBLEMA

Quando personal:
1. Marca check-in da aula no PRO ✅
2. Abre tela `$` do aluno (modelo POR AULA) ✅
3. Vê tela calculando `1 × R$1 = R$1.00` ✅
4. Clica "FECHAR E GERAR COBRANÇA" ✅
5. Popup mostra: **TOTAL: R$ 0,00** ❌
6. Se confirmar, gera cobrança de R$0
7. **Aula perdida financeiramente** 🚨

---

## 🔬 CAUSA RAIZ

Arquivo: `/static/app_personal.html`

### Função `abrirCobrancaAluno` (linha 4380) — FUNCIONA ✅
- É `async function`
- Busca check-ins via API
- Calcula corretamente: `valorBase = modeloCobr === 'aula' ? (checkins * valorAula) : valorMensal`

### Função `gerarCobrancaAluno` (linha 4564) — BUGADA ❌
- É `function` simples (sem async)
- NÃO busca check-ins via API
- Calcula errado: `valorBase = modeloCobr === 'mensal' ? valorMensal : 0`
- O próprio dev deixou TODO no código: `// POR AULA precisa ler checkins`

**Resumo:** copiou parte do código mas esqueceu de copiar a busca de check-ins. Deixou hardcoded `0` com comentário "vou fazer depois". Nunca foi feito.

---

## ✅ FIX (cirúrgico)

### Arquivo
`/Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal.html`

### Mudança 1 — Linha 4564

**ANTES:**
```javascript
function gerarCobrancaAluno(alunoId){
```

**DEPOIS:**
```javascript
async function gerarCobrancaAluno(alunoId){
```

(adicionar `async` antes de `function`)

---

### Mudança 2 — Linhas 4574-4577

**ANTES:**
```javascript
  // Buscar checkins do modal aberto (já foi calculado)
  var checkinsTxt = document.querySelector('[id^="lista-servicos-"]');
  
  var valorBase = modeloCobr === 'mensal' ? valorMensal : 0; // POR AULA precisa ler checkins
```

**DEPOIS:**
```javascript
  // Busca checkins do mês atual via API (mesmo padrão de abrirCobrancaAluno)
  var hoje = new Date();
  var mesAtual = hoje.getMonth();
  var anoAtual = hoje.getFullYear();
  var checkins = 0;
  
  try {
    var resp = await fetch('/app-personal/aulas/aluno/' + alunoId + '/mes?ano=' + anoAtual + '&mes=' + (mesAtual+1), {
      headers: {'Authorization': 'Bearer ' + token}
    });
    if(resp.ok) {
      var dados = await resp.json();
      checkins = dados.checkins || 0;
    }
  } catch(e) {
    console.error('Erro ao buscar checkins:', e);
  }
  
  var valorBase = modeloCobr === 'aula' ? (checkins * valorAula) : valorMensal;
```

---

## 🧪 PROCEDIMENTO DE APLICAÇÃO (com método)

### Passo 1 — Backup (opcional, git já versiona)
```bash
cp /Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal.html /Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal.html.ANTES_FIX_COBRANCA_POR_AULA
```

### Passo 2 — Aplicar mudança 1 (async)

Abrir VSCode, ir na linha 4564, mudar:
- DE: `function gerarCobrancaAluno(alunoId){`
- PARA: `async function gerarCobrancaAluno(alunoId){`

### Passo 3 — Aplicar mudança 2 (busca de checkins)

Selecionar do `// Buscar checkins do modal aberto` até `var valorBase = modeloCobr === 'mensal' ? valorMensal : 0; // POR AULA precisa ler checkins` (4 linhas)

Substituir pelo bloco "DEPOIS" da Mudança 2.

### Passo 4 — Testar LOCAL ANTES de subir

⚠️ **NÃO faz git commit ainda.**

```bash
# Confirma que mudou só esse arquivo
git status
# Esperado: SÓ static/app_personal.html modified
```

Se aparecer outro arquivo modificado = REVERTE e revisa.

### Passo 5 — Validar sintaxe (busca por erros)

```bash
grep -n "async function gerarCobrancaAluno" /Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal.html
# Esperado: linha 4564 com async
```

```bash
grep -n "POR AULA precisa ler checkins" /Users/andrepersonalnote/Personal_Trainer_Projeto/static/app_personal.html
# Esperado: ZERO resultados (comentário antigo deve ter sumido)
```

### Passo 6 — Commit + push

```bash
git add static/app_personal.html
git commit -m "fix(cobranca): popup de cobranca POR AULA agora le checkins corretamente"
git push
```

### Passo 7 — Aguardar Railway 🟢 (1-2 min)

### Passo 8 — TESTE EM PRODUÇÃO

1. Abrir aba anônima
2. Logar no PRO: aurumsc.com.br/personal
3. Aba ALUNOS → Teste Final 04 → ícone $
4. Conferir: tela mostra "1 × R$1 = R$1.00"
5. Clicar "FECHAR E GERAR COBRANÇA"
6. Popup deve mostrar:
   ```
   Modelo: AULA
   Valor base: R$ 1.00     ← deve ser R$1, não R$0!
   Serviços: R$ 0.00
   TOTAL: R$ 1.00          ← deve ser R$1!
   ```
7. Cancelar (não confirmar pra não pagar de verdade)

### Passo 9 — Se passou no teste, vitória! Se falhou, REVERTE:

```bash
git revert HEAD
git push
```

---

## ⚠️ CUIDADOS

### Backup automático já existe
Git versiona tudo. Se algo der errado:
```bash
git revert HEAD
git push
```
Sistema volta pro estado anterior em 1 minuto.

### Não mexer no backend
Esse fix é APENAS frontend (HTML/JS). NÃO mexe em:
- ❌ `app_aluno.py`
- ❌ `financeiro.py`
- ❌ `pagamento.py`
- ❌ Tabelas do banco
- ❌ Webhook Stripe

Risco em produção: **BAIXO** (frontend isolado).

### Não testar com valor real
Pode TESTAR clicando "FECHAR E GERAR COBRANÇA" no popup — só **CANCELA** quando aparecer. Não deixa confirmar (senão cobra R$1 de verdade).

---

## 📊 IMPACTO DO BUG

Esse bug afeta:
- 🚨 **TODOS os alunos com modelo "POR AULA"**
- 🚨 Toda vez que personal tenta fechar cobrança avulsa
- 🚨 Cobrança vai pra R$0 silenciosamente
- 🚨 Aluno não cobrado, personal perde receita

**Quanto tempo o bug existe?** Difícil saber sem git log, mas comentário `// POR AULA precisa ler checkins` sugere que NUNCA funcionou — feature foi feita pela metade desde o início.

---

## 🎯 ESTIMATIVA DE TEMPO

```
Aplicação do fix: 5 min
Teste local: 5 min
Push + deploy: 3 min
Teste em produção: 5 min
═══════════════════════════
TOTAL: 18 minutos (com cabeça fresca)
```

**Recomendação:** aplicar AMANHÃ (10/05) de manhã com café. NÃO hoje (09/05) às 22h+ depois de 17h trabalhando.

---

## 🏆 CRÉDITOS

- **André:** descobriu o bug, insistiu até comprovar, mandou prints decisivos
- **Investigação:** 5 greps, 2 leituras de código, hipótese confirmada
- **Tempo investigação:** ~30 min
- **Tempo aplicação estimado:** 18 min

---

## 📝 LIÇÃO

> "Quando o usuário insiste que tem bug, **PRESTA ATENÇÃO.**
> Olho de personal de 20 anos pega coisa que código de IA não pega."

> "TODO em código sem prazo = bug eterno.
> Hoje provamos isso na prática."

---

**Próximo passo:** descansar. Aplicar amanhã. 🛡️🎯

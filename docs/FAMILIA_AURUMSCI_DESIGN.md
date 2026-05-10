# 👨‍👩‍👧‍👦 FEATURE FAMÍLIA — AurumSci

**Data:** 09/05/2026 (sessão noturna)
**Autor:** André (insights de produto) + Claude (estruturação técnica)
**Status:** 📋 Design pendente de implementação

---

## 🎯 CONTEXTO REAL

André tem **20-25 alunos** ativos. Destes:
- **3 famílias = 7 alunos** pagam de forma consolidada
- Resto (~13-18 alunos) paga individual

### Caso real — Família Silva
- **Maria** (mãe) — pagadora
- **Andre** (filho) — só treina, não paga
- **Claude** (filho) — só treina, não paga
- Maria paga **R$2.500/mês fechado** (pacote família)

### Bug identificado
Sistema atual está **amarrado à pessoa**:
- Filho treinou 5 aulas → 5 cobranças no nome dele
- Filhos NUNCA pagam → cobranças ficam pendentes ETERNAMENTE
- Métricas falsas, "inadimplência" inexistente

---

## 💡 SOLUÇÃO PROPOSTA (UX final do André)

### Aba AULAS no PRO ganha 2 sub-abas:

```
┌────────────────────────────────────────┐
│  AULAS — Sábado 09/05/2026             │
│                                        │
│  [👤 INDIVIDUAL]   [👨‍👩‍👧 FAMÍLIA]      │
│                                        │
└────────────────────────────────────────┘
```

### Aba INDIVIDUAL (atual)
- Lista alunos sem família
- Check-in normal
- Cobrança normal

### Aba FAMÍLIA (NOVA)
```
┌────────────────────────────────────────┐
│  👨‍👩‍👧 FAMÍLIAS                          │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ FAMÍLIA SILVA                    │ │
│  │ 💳 Pagador: Maria Silva          │ │
│  │ 💰 Pacote: R$ 2.500/mês          │ │
│  │ ─────────────────────────────── │ │
│  │ ✓ Maria Silva    [+ Check-in]   │ │
│  │ ✓ Andre Silva    [+ Check-in]   │ │
│  │ ✓ Claude Silva   [+ Check-in]   │ │
│  │ ─────────────────────────────── │ │
│  │ Aulas mês: 12 | Pagamento: ✅    │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ FAMÍLIA OLIVEIRA                 │ │
│  │ ...                              │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Comportamento dos botões

**Click "Check-in Andre" (filho):**
1. Cria check-in NO ANDRE (periodização funciona ✅)
2. NÃO cria cobrança no Andre
3. Sistema entende: "Aula vinculada a Família Silva"

**Click "Check-in Maria" (pagadora):**
1. Cria check-in NA MARIA (periodização funciona ✅)
2. Conta dentro do pacote da família

**Final do mês:**
- Sistema mostra apenas 1 cobrança: Maria — R$2.500
- Tu cobra Maria via PIX (manual)
- Marca como "REGISTRAR RECEBIMENTO"
- Emite 1 nota fiscal só pra Maria
- Filhos NÃO têm cobrança/nota

---

## 🧱 MODELAGEM DE BANCO

### Nova tabela: `familias`
```sql
CREATE TABLE familias (
    id SERIAL PRIMARY KEY,
    personal_id INT REFERENCES personals(id) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    pagador_aluno_id INT REFERENCES alunos(id) NOT NULL,
    valor_pacote_mensal DECIMAL(10,2),
    modelo_cobranca VARCHAR(20), -- 'pacote_fechado' | 'soma_aulas'
    desconto_familia DECIMAL(5,2) DEFAULT 0,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);
```

### Modificação na tabela `alunos`
```sql
ALTER TABLE alunos
ADD COLUMN familia_id INT REFERENCES familias(id),
ADD COLUMN papel_familia VARCHAR(20); -- 'pagador' | 'dependente' | NULL
```

### Modificação na tabela `pagamentos`
```sql
ALTER TABLE pagamentos
ADD COLUMN familia_id INT REFERENCES familias(id),
ADD COLUMN cobranca_consolidada BOOLEAN DEFAULT FALSE;
```

### Tabela `presencas` (check-ins)
**Não muda!** Continua amarrado ao aluno (pra periodização).
A diferença é na lógica do FRONTEND/BACKEND ao calcular cobrança.

---

## 🎯 ENDPOINTS NECESSÁRIOS

### Famílias
```
POST   /familia                    → Criar família
GET    /familia                    → Listar famílias do personal
GET    /familia/{id}               → Ver detalhes (com membros)
PUT    /familia/{id}               → Atualizar (nome, valor, etc)
DELETE /familia/{id}               → Deletar (preserva alunos)

POST   /familia/{id}/membro        → Adicionar aluno à família
DELETE /familia/{id}/membro/{aid}  → Remover aluno da família
PUT    /familia/{id}/pagador       → Mudar pagador (Maria → João)
```

### Cobrança
```
GET    /familia/{id}/fechamento    → Calcular fechamento mês atual
POST   /familia/{id}/fechar-mes    → Gerar cobrança consolidada
```

### Aulas (modificações)
```
POST   /aulas/checkin              → Modificar pra detectar família
   - Se aluno_id pertence a família:
     - Cria check-in normal
     - Atribui à família (não cria cobrança individual)
```

---

## 🤔 EDGE CASES PRA DECIDIR

### ❓ Questão 1 — Modelo de cobrança
- **(A)** Pacote fechado: R$2.500 fixo independente de aulas
- **(B)** Soma das aulas dos membros (cada aula soma)
- **(C)** Pacote com limite (ex: até 20 aulas/mês inclusas)

**Recomendação:** (A) Pacote fechado — simples, reflete realidade.

### ❓ Questão 2 — E se membro pausar 1 mês?
- Sistema cobra Maria normalmente?
- Faz desconto proporcional?
- Membro fica "inativo temporariamente"?

**Recomendação:** Pacote fixo. Pausa não desconta. Maria/família resolve internamente.

### ❓ Questão 3 — Mudança de pagador
- Mês 1: Maria paga
- Mês 2: João (marido) assume
- Como sistema trata?

**Recomendação:** Endpoint `PUT /familia/{id}/pagador` permite trocar.

### ❓ Questão 4 — App do aluno (filho)
- Filho vê que faz parte de família?
- Vê que NÃO paga?
- Vê o pagador?

**Recomendação:**
- Filho NÃO vê tela financeira no app dele
- Apenas treinos, evolução, periodização
- Texto sutil: "Plano: Família Silva"

### ❓ Questão 5 — Membro sai da família
- Filho cresce, sai de casa, quer plano próprio
- Migração: vira aluno individual
- Histórico fica vinculado à família ou desvincula?

**Recomendação:** Histórico fica vinculado (período X-Y), depois aluno vira individual.

### ❓ Questão 6 — Pagador NÃO treina
- Pai paga 3 filhos mas não faz aula
- Sistema permite "pagador não-aluno"?

**Recomendação:** v1 — pagador SEMPRE é aluno. v2 — permite pagador externo (CPF + nome, sem app).

---

## 📊 ESTIMATIVA REALISTA DE TEMPO

```
1. Modelagem de banco               1-2h
2. Endpoints de família (CRUD)      3-4h
3. Endpoint adicionar/remover membro  2h
4. Lógica de fechamento mensal      3-4h
5. Modificar /aulas/checkin         1-2h
6. UI Aba Família (PRO)             4-6h
7. UI Card Família (lista)          2-3h
8. UI Modal criar/editar família    2-3h
9. Tela aluno (app do filho)        1-2h
10. Testes end-to-end               3-4h
11. Bug fixes                       3-5h
─────────────────────────────────────
TOTAL: 25-37h trabalho
```

**= 6-9 sessões focadas (3-4h cada).**

---

## 🚦 PLANO DE IMPLEMENTAÇÃO SUGERIDO

### Sprint 1 (Semana 1) — Foundation
- [ ] Modelagem de banco
- [ ] Endpoints CRUD básicos
- [ ] Sem UI ainda
- [ ] Testes via Postman/Thunder

### Sprint 2 (Semana 2) — UI básica
- [ ] Aba Família no PRO
- [ ] Listar famílias
- [ ] Criar família + adicionar membros
- [ ] Sem fechamento mensal ainda

### Sprint 3 (Semana 3) — Cobrança
- [ ] Lógica de fechamento mensal
- [ ] Modificar /aulas/checkin
- [ ] Testar com FAMÍLIA SILVA real
- [ ] Cobrança consolidada manual

### Sprint 4 (Semana 4) — Polimento
- [ ] App do aluno (mostrar família)
- [ ] Edge cases
- [ ] Bug fixes
- [ ] Apresentar pra Maria (alpha tester real)

---

## ⚠️ RISCOS

### 🔴 Alto risco
- **Mexer em sistema crítico (cobrança):** afeta sustento real
- **Bug em produção:** pode bagunçar dados de alunos reais
- **Decisão prematura:** pode arquitetar errado e ter retrabalho

### 🟡 Médio risco
- **UX confusa:** alunos podem se confundir com "Família" no app
- **Performance:** queries complexas se famílias forem grandes
- **LGPD:** menores de idade têm regras específicas

### 🟢 Baixo risco
- Tabelas novas (não mexem em existentes drasticamente)
- Endpoints isolados (não afetam fluxo existente)

---

## 💡 WORKAROUND TEMPORÁRIO (até implementar)

Enquanto feature não existe, **fluxo manual:**

1. **Cadastro:**
   - Maria: configurar `R$ 2.500/mês` na tela $
   - Filhos: configurar `R$ 0,00` (gambiarra explícita) na tela $

2. **Operação mensal:**
   - Tu marca check-ins normalmente (cada aluno individual)
   - Filhos: sistema calcula `5 aulas × R$0 = R$0` (sem pendência)
   - Maria: sistema calcula `R$2.500 fixo`
   - Maria paga PIX
   - "REGISTRAR RECEBIMENTO" da Maria
   - Emite nota só da Maria

3. **Documentação interna:**
   - Anota num bloco: "Família Silva — gambiarra ativa"
   - Migrar quando feature existir

✅ Funciona HOJE
✅ Zero código novo
❌ Gambiarra (mas funcional)

---

## 🎯 RECOMENDAÇÃO PRA ANDRÉ

### Pra HOJE (09/05/2026)
1. ✅ **NÃO codar nada de família.** Tu trabalhou 17+ horas.
2. ✅ **Aplicar workaround manual** se precisar usar com Maria já.
3. ✅ **Cancelar `aluno@teste.com` no Stripe** (R$49,90/mês economizados).
4. ✅ **Descansar.** Família, Blue, dia das mães.

### Pra AMANHÃ (10/05/2026)
1. Ler este documento com café.
2. Responder as 6 perguntas pendentes (edge cases).
3. Decidir: implementar agora ou esperar.

### Pra Sprint 1 (próxima semana)
1. Implementar foundation (modelagem + CRUD).
2. Sessões de 3-4h focadas.
3. Sem pressa, com método.

### Pra apresentar pro 1º aluno
1. Polir app aluno antes (reabilitação, qualidade vida, fix /pagamento/aluno-view).
2. Implementar feature família.
3. Migrar Família Silva como caso piloto.
4. Coletar feedback REAL.

---

## 📝 FRASES DO DIA (panteão)

> "A calma é a fonte da sabedoria."

> "Funciona pra mim primeiro."

> "Antes de vender pro outro, precisa funcionar pra mim."

> "Aluno é meu foco."

> "Adianta achar culpado?"

> "Vai ser sucesso pra alguém se for pra mim, pq até os meus alunos vão elogiar."

---

## 🏆 VITÓRIAS DO DIA 09/05/2026

✅ Fix `recuperar_senha` (UsuarioAluno → AlunoCredencial)
✅ Fix `treino_hoje` (fila contínua, eliminou "DIA DE DESCANSO")
✅ Mapeamento completo do financeiro (`pagamentos` vs `cobrancas`)
✅ Stripe entendido (subscription pronto, cobrança avulsa não)
✅ 9 iterações de design da feature Família
✅ Decisão final de UX (aba Família + click filho registra na Maria)
✅ Documento completo gerado

---

**Status:** Aguardando próxima sessão com cabeça fresca. 🛡️🎯


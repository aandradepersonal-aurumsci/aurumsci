# 👨‍👩‍👧‍👦 PLANO FAMILIAR AURUMSCI — DESIGN COMPLETO v3 FINAL

> **Documento de Design e Implementação**
> Criado: domingo, 10/05/2026
> Sessão: André (CREF 62702-G/SP) + Claude
> Status: ✅ Design aprovado, pronto pra implementação

---

## 🎯 SUMÁRIO EXECUTIVO

Sistema de **Grupos Compartilhados** (comercializado como "Plano Familiar") onde **1 pessoa paga** por até **10 pessoas** que treinam, com **tabela de preços própria** (individual + dupla), **1 boleto consolidado** e **1 nota fiscal**.

**Casos de uso atendidos:**
- ✅ Família nuclear (pai/mãe + filhos)
- ✅ Casal namorado/casado
- ✅ Sócios de empresa (até 10)
- ✅ Filho adulto pagando pelos pais
- ✅ Empresa pagando pra funcionários (B2B inicial)

---

## 🛡️ REGRA DE OURO

> **NÃO MEXER NO QUE JÁ FUNCIONA.**
> O sistema individual (aluno, check-in, cobrança, Stripe, webhook, recibo)
> está em produção, testado e estável.
> O Plano Familiar é **MÓDULO ISOLADO** que se adiciona EM CIMA.
>
> Bug em Família = **NÃO afeta** sistema individual.

---

## 📊 CONCEITOS

### Grupo (entidade nova)
- 1 nome (ex: "Família Bianca")
- 1 NF (CPF ou CNPJ — sistema detecta)
- 1 email do "quem paga"
- Tabela de preços própria:
  - **1️⃣ Aula individual** (R$ X)
  - **2️⃣ Aula em dupla** (R$ Y)
- 1 a 10 membros

### Membro do Grupo
- Vinculado a um Aluno individual existente
- Pode ser "quem paga" (★ provedor) — apenas 1 por grupo
- Pode "treinar também" (checkbox)
- Mantém perfil individual completo (anamnese, treino, evolução)

### Check-in da Família
- Marca quem treinou + tipo (1 ou 2)
- **Bloqueia 3+ pessoas juntas** (qualidade do personal)
- Sistema calcula valor automaticamente
- Sincroniza com perfil individual de cada aluno

### Cobrança Consolidada
- Soma do mês inteiro de todos membros que treinaram
- 1 boleto pro "quem paga"
- Email com discriminação por membro
- Stripe automático (já funciona ✅)
- Webhook automático (já funciona ✅)
- [COPIA] pro personal (já funciona ✅)

---

## 🎨 ARQUITETURA VISUAL

### MENU PRINCIPAL (top)

```
┌────────────────────────────────────┐
│ 👥 ALUNOS    👨‍👩‍👧‍👦 FAMÍLIAS         │
│ 💰 FINANÇAS  📅 AULAS              │
└────────────────────────────────────┘
```

(LOJA permanece no rodapé/menu inferior, junto com INÍCIO e AURI)

---

### ABA ALUNOS (sem mudança estrutural)

Cards individuais como hoje. **Diferença sutil**: alunos vinculados a uma família ganham o ícone 👨‍👩‍👧‍👦 ao lado do nome.

```
[Card] Fadua - emagrecimento
[Card] Mãe Z - hipertrofia
[Card] Rafa - hipertrofia
[Card] 👨‍👩‍👧‍👦 Bianca - hipertrofia
[Card] 👨‍👩‍👧‍👦 Rogério - hipertrofia
[Card] 👨‍👩‍👧‍👦 Lucas - hipertrofia
[Card] 👨‍👩‍👧‍👦 Matteo - hipertrofia
```

**Click em qualquer aluno** → vai pro perfil individual dele (igual hoje).

---

### ABA FAMÍLIAS (NOVA)

#### Estado vazio (1ª vez)

```
┌──────────────────────────────────────┐
│ 👨‍👩‍👧‍👦 BEM-VINDO AO PLANO FAMILIAR! │
├──────────────────────────────────────┤
│                                      │
│ Cadastra grupos onde 1 pessoa paga   │
│ pelas demais e tem 1 nota fiscal.    │
│                                      │
│ Funciona com:                        │
│ ✅ Família (pai/mãe + filhos)        │
│ ✅ Casal namorado/casado             │
│ ✅ Sócios (1 paga pela empresa)      │
│ ✅ Filho pagando pelos pais          │
│                                      │
│ Não é grupo? Cadastra cada um na     │
│ aba ALUNOS individual normal.        │
│                                      │
│ [+ CADASTRAR PRIMEIRA FAMÍLIA]       │
│ [📖 Como funciona]                   │
└──────────────────────────────────────┘
```

#### Lista de famílias

```
┌──────────────────────────────────────┐
│ 👨‍👩‍👧‍👦 FAMÍLIAS                  [?] │
├──────────────────────────────────────┤
│                                      │
│ [+ Cadastrar Família]                │
│                                      │
│ FAMÍLIAS CADASTRADAS                 │
│                                      │
│ ┌────────────────────────────┐      │
│ │ 👨‍👩‍👧‍👦 Família Bianca       │      │
│ │ 4 membros · R$ 2.960/mês   │      │
│ │ › ver detalhes             │      │
│ └────────────────────────────┘      │
│                                      │
│ ┌────────────────────────────┐      │
│ │ 👨‍👩‍👧‍👦 Família Rodrigo      │      │
│ │ 3 membros · R$ 1.500/mês   │      │
│ │ › ver detalhes             │      │
│ └────────────────────────────┘      │
└──────────────────────────────────────┘
```

#### Modal Ajuda [?]

```
┌──────────────────────────────────────┐
│ 💡 COMO FUNCIONA O PLANO FAMILIAR    │
├──────────────────────────────────────┤
│                                      │
│ 👨‍👩‍👧‍👦 PARA QUEM SERVE:              │
│ Qualquer GRUPO onde 1 pessoa paga    │
│ pelas demais e tem 1 nota fiscal.    │
│                                      │
│ Exemplos:                            │
│ ✅ Família (pai/mãe + filhos)        │
│ ✅ Casal (1 paga pelo casal)         │
│ ✅ Sócios (1 paga pra empresa)       │
│ ✅ Filho adulto pagando pelos pais   │
│                                      │
│ ❌ Cada um paga próprio?             │
│ Cadastra cada um na aba ALUNOS.      │
│                                      │
│ 📋 COMO USAR:                        │
│ 1. Click "+ Cadastrar Família"       │
│ 2. Preenche nome, NF, email          │
│ 3. Define tabela:                    │
│    1️⃣ Individual: R$ X               │
│    2️⃣ Em dupla:   R$ Y               │
│ 4. Adiciona até 10 membros           │
│ 5. Marca QUEM PAGA (★ provedor)      │
│ 6. Marca QUEM TREINA                 │
│                                      │
│ 📅 CHECK-IN:                         │
│ Marca quem treinou + tipo (1 ou 2)   │
│ Sistema calcula automático.          │
│ Bloqueia 3+ pessoas juntas           │
│ pra manter qualidade.                │
│                                      │
│ 💰 COBRANÇA:                         │
│ Sistema soma o mês inteiro.          │
│ Manda 1 boleto pro provedor.         │
│ 1 nota fiscal (NF do grupo).         │
│                                      │
│ [ENTENDI, FECHAR]                    │
└──────────────────────────────────────┘
```

#### Tela de Cadastro

```
┌──────────────────────────────────────┐
│ ← Voltar                             │
│ 👨‍👩‍👧‍👦 NOVA FAMÍLIA                  │
├──────────────────────────────────────┤
│                                      │
│ 📋 DADOS DO GRUPO                    │
│                                      │
│ Nome do grupo:                       │
│ [Família Bianca________________]     │
│                                      │
│ NF (CPF ou CNPJ):                    │
│ [123.456.789-00___________]          │
│ (sistema detecta automaticamente)    │
│                                      │
│ Email do "quem paga":                │
│ [bianca@email.com_______]            │
│                                      │
│ ─────────────────────────────────    │
│                                      │
│ 💰 TABELA DE VALORES                 │
│                                      │
│ 1️⃣ Aula individual: R$ [120]         │
│ 2️⃣ Aula em dupla:   R$ [100]         │
│                                      │
│ ─────────────────────────────────    │
│                                      │
│ 👥 MEMBROS (1 a 10)                  │
│                                      │
│ Adicionar membro:                    │
│ [Buscar aluno cadastrado ▼]          │
│ ou                                   │
│ [+ Cadastrar novo aluno]             │
│                                      │
│ MEMBROS ADICIONADOS:                 │
│                                      │
│ ★ Bianca                             │
│   ☑ Quem paga (provedor)             │
│   ☑ Treina também                    │
│   [Remover]                          │
│                                      │
│ • Rogério                            │
│   ☐ Quem paga                        │
│   ☑ Treina                           │
│   [Remover]                          │
│                                      │
│ • Lucas (14a)                        │
│   ☐ Quem paga                        │
│   ☑ Treina                           │
│   [Remover]                          │
│                                      │
│ • Matteo (12a)                       │
│   ☐ Quem paga                        │
│   ☑ Treina                           │
│   [Remover]                          │
│                                      │
│ [SALVAR FAMÍLIA]                     │
└──────────────────────────────────────┘
```

#### Tela de Detalhes (sub-abas)

```
┌──────────────────────────────────────┐
│ ← Voltar                             │
│ 👨‍👩‍👧‍👦 FAMÍLIA BIANCA               │
├──────────────────────────────────────┤
│                                      │
│ [DADOS] [AULAS] [FINANCEIRO]         │
│                                      │
└──────────────────────────────────────┘
```

**Sub-aba DADOS**: edita NF, email, tabela, membros (igual cadastro mas pré-preenchido)

**Sub-aba AULAS**: check-in da família

```
┌──────────────────────────────────────┐
│ 📅 CHECK-IN — FAMÍLIA BIANCA         │
├──────────────────────────────────────┤
│                                      │
│ Data: [10/05/2026]                   │
│                                      │
│ Quem treinou hoje?                   │
│                                      │
│ ☑ Bianca       Tipo: [2]             │
│ ☑ Rogério      Tipo: [2]             │
│ ☐ Lucas        Tipo: [_]             │
│ ☐ Matteo       Tipo: [_]             │
│                                      │
│ ⚠️ Detectada aula em DUPLA           │
│    Bianca + Rogério                  │
│    R$ 100 cada                       │
│                                      │
│ [REGISTRAR CHECK-IN]                 │
└──────────────────────────────────────┘
```

**Sub-aba FINANCEIRO**: relatório mensal + cobrança

```
┌──────────────────────────────────────┐
│ 💰 FAMÍLIA BIANCA — Maio 2026        │
├──────────────────────────────────────┤
│                                      │
│ NF: 123.456.789-00 (Bianca)          │
│                                      │
│ Bianca:    8 aulas    R$  880        │
│   (4 individuais R$120               │
│    + 4 duplas R$100)                 │
│                                      │
│ Rogério:   4 aulas    R$  400        │
│   (4 duplas R$100)                   │
│                                      │
│ Lucas:     8 aulas    R$  960        │
│   (8 individuais R$120)              │
│                                      │
│ Matteo:    6 aulas    R$  720        │
│   (6 individuais R$120)              │
│                                      │
│ ════════════════════════════         │
│ TOTAL FAMÍLIA: R$ 2.960              │
│ ════════════════════════════         │
│                                      │
│ [GERAR COBRANÇA STRIPE]              │
│ → Bianca recebe email                │
│ → Stripe processa                    │
│ → Webhook confirma                   │
│ → Email recibo automático            │
└──────────────────────────────────────┘
```

---

## 💾 SCHEMA DE BANCO DE DADOS

### Tabela: `familias` (NOVA)

```sql
CREATE TABLE familias (
    id SERIAL PRIMARY KEY,
    personal_id INTEGER NOT NULL REFERENCES personals(id) ON DELETE CASCADE,
    nome VARCHAR(150) NOT NULL,
    nf VARCHAR(20) NOT NULL,                 -- CPF ou CNPJ
    nf_tipo VARCHAR(4) NOT NULL,             -- "CPF" ou "CNPJ"
    email VARCHAR(100) NOT NULL,             -- email do provedor
    valor_individual DECIMAL(10,2) NOT NULL DEFAULT 0,  -- 1️⃣
    valor_dupla DECIMAL(10,2) NOT NULL DEFAULT 0,       -- 2️⃣
    ativa BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_familias_personal ON familias(personal_id);
CREATE INDEX idx_familias_nf ON familias(nf);
```

### Tabela: `familia_membros` (NOVA)

```sql
CREATE TABLE familia_membros (
    id SERIAL PRIMARY KEY,
    familia_id INTEGER NOT NULL REFERENCES familias(id) ON DELETE CASCADE,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    eh_provedor BOOLEAN DEFAULT FALSE,       -- ★ marca quem paga
    treina BOOLEAN DEFAULT TRUE,             -- aluno treina (ou só paga)
    criado_em TIMESTAMP DEFAULT NOW(),
    UNIQUE(familia_id, aluno_id)             -- aluno só pode estar 1x na família
);

CREATE INDEX idx_familia_membros_familia ON familia_membros(familia_id);
CREATE INDEX idx_familia_membros_aluno ON familia_membros(aluno_id);
```

### Tabela: `familia_checkins` (NOVA)

```sql
CREATE TABLE familia_checkins (
    id SERIAL PRIMARY KEY,
    familia_id INTEGER NOT NULL REFERENCES familias(id) ON DELETE CASCADE,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo INTEGER NOT NULL,                   -- 1 = individual, 2 = dupla
    valor DECIMAL(10,2) NOT NULL,            -- valor da aula (snapshot)
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_familia_checkins_familia_data ON familia_checkins(familia_id, data);
CREATE INDEX idx_familia_checkins_aluno_data ON familia_checkins(aluno_id, data);
```

### Tabela: `familia_cobrancas` (NOVA)

```sql
CREATE TABLE familia_cobrancas (
    id SERIAL PRIMARY KEY,
    familia_id INTEGER NOT NULL REFERENCES familias(id) ON DELETE CASCADE,
    mes_referencia DATE NOT NULL,            -- primeiro dia do mês
    valor_total DECIMAL(10,2) NOT NULL,
    descricao TEXT,                          -- discriminação
    status VARCHAR(20) DEFAULT 'pendente',   -- pendente, enviada, paga, cancelada
    stripe_session_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    pago_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_familia_cobrancas_familia ON familia_cobrancas(familia_id);
CREATE INDEX idx_familia_cobrancas_status ON familia_cobrancas(status);
```

---

## 🔌 ENDPOINTS DA API

### CRUD Famílias

```
POST   /app-personal/familias                    Cria família
GET    /app-personal/familias                    Lista famílias do personal
GET    /app-personal/familias/{id}               Detalhes de uma família
PUT    /app-personal/familias/{id}               Edita família
DELETE /app-personal/familias/{id}               Deleta família (cuidado!)
```

### Membros da Família

```
POST   /app-personal/familias/{id}/membros       Adiciona membro
DELETE /app-personal/familias/{id}/membros/{aluno_id}  Remove membro
PUT    /app-personal/familias/{id}/membros/{aluno_id}  Atualiza flags (provedor/treina)
```

### Check-in Família

```
POST   /app-personal/familias/{id}/checkin       Registra check-in
GET    /app-personal/familias/{id}/checkins      Lista check-ins (filtro mes)
DELETE /app-personal/familias/{id}/checkins/{checkin_id}  Cancela check-in
```

### Cobrança Família

```
POST   /app-personal/familias/{id}/fechar-mes    Calcula total e cria cobrança
POST   /app-personal/familias/{id}/gerar-link    Cria sessão Stripe + envia email
GET    /app-personal/familias/{id}/cobrancas     Lista cobranças
GET    /app-personal/familias/{id}/relatorio/{mes} Relatório mensal detalhado
```

---

## 🎯 LÓGICA DE NEGÓCIO

### Validação de Check-in

```python
def validar_checkin_familia(familia_id, alunos_marcados):
    """
    Regras:
    1. Mínimo 1 pessoa marcada
    2. MÁXIMO 2 pessoas (bloqueia trio+)
    3. Todos devem ser membros da família
    4. Tipo deve ser 1 (individual) ou 2 (dupla)
    """
    if len(alunos_marcados) == 0:
        raise ValueError("Marque pelo menos 1 pessoa")
    
    if len(alunos_marcados) > 2:
        raise ValueError(
            "AurumSci foca em personal de QUALIDADE. "
            "Recomendamos máximo 2 pessoas por aula. "
            "Marque 2 check-ins separados."
        )
    
    # Se 2 pessoas, todos são tipo 2 (dupla)
    if len(alunos_marcados) == 2:
        tipo_correto = 2
    else:
        tipo_correto = 1
    
    return tipo_correto
```

### Cálculo de Valor

```python
def calcular_valor_checkin(familia, tipo):
    if tipo == 1:
        return familia.valor_individual
    elif tipo == 2:
        return familia.valor_dupla
    else:
        raise ValueError("Tipo deve ser 1 (individual) ou 2 (dupla)")
```

### Fechamento de Mês

```python
def fechar_mes_familia(familia_id, mes_referencia):
    """
    1. Soma todos check-ins do mês de cada membro
    2. Gera descrição discriminada
    3. Cria registro em familia_cobrancas
    4. Retorna ID pra criar sessão Stripe
    """
    familia = Familia.query.get(familia_id)
    membros = familia.membros
    
    total = 0
    descricao_lines = []
    
    for membro in membros:
        checkins = FamiliaCheckin.query.filter_by(
            familia_id=familia_id,
            aluno_id=membro.aluno_id
        ).filter(
            FamiliaCheckin.data >= mes_referencia,
            FamiliaCheckin.data < mes_referencia + relativedelta(months=1)
        ).all()
        
        total_membro = sum(c.valor for c in checkins)
        if total_membro > 0:
            descricao_lines.append(
                f"{membro.aluno.nome}: {len(checkins)} aulas — R$ {total_membro:.2f}"
            )
            total += total_membro
    
    cobranca = FamiliaCobranca(
        familia_id=familia_id,
        mes_referencia=mes_referencia,
        valor_total=total,
        descricao="\n".join(descricao_lines),
        status='pendente'
    )
    db.session.add(cobranca)
    db.session.commit()
    return cobranca
```

### Integração Stripe

```python
def gerar_link_pagamento_familia(cobranca_id):
    """
    Usa MESMA infra do gerar-link individual:
    - stripe.checkout.Session.create(mode="payment")
    - Envia email com link
    - Webhook detecta pagamento e marca como pago
    """
    cobranca = FamiliaCobranca.query.get(cobranca_id)
    familia = cobranca.familia
    provedor = next(m for m in familia.membros if m.eh_provedor)
    
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card", "boleto"],
        line_items=[{
            "price_data": {
                "currency": "brl",
                "product_data": {"name": f"Família {familia.nome} - {cobranca.mes_referencia.strftime('%m/%Y')}"},
                "unit_amount": int(cobranca.valor_total * 100),
            },
            "quantity": 1,
        }],
        customer_email=familia.email,
        metadata={
            "tipo": "familia",
            "familia_id": familia.id,
            "cobranca_id": cobranca.id,
        },
        success_url=f"{settings.FRONTEND_URL}/aluno",
        cancel_url=f"{settings.FRONTEND_URL}/personal",
    )
    
    cobranca.stripe_session_id = session.id
    cobranca.status = 'enviada'
    db.session.commit()
    
    # Envia email com link (template existente)
    enviar_email_cobranca_familia(familia, cobranca, session.url)
    
    return session.url
```

### Webhook (modificação MÍNIMA)

```python
# Em app/routers/pagamento.py — webhook existente
# Adicionar APENAS um IF antes da lógica de cobrança avulsa:

if event["type"] == "checkout.session.completed":
    session = event["data"]["object"]
    
    # NOVA LÓGICA: detectar pagamento de família
    try:
        if session["metadata"].get("tipo") == "familia":
            cobranca_id = session["metadata"].get("cobranca_id")
            cobranca = FamiliaCobranca.query.get(cobranca_id)
            if cobranca and cobranca.status != "pago":
                cobranca.status = "pago"
                cobranca.pago_em = datetime.now()
                db.session.commit()
                
                # Envia recibo (template existente reutilizado)
                enviar_recibo_familia(cobranca)
            return {"received": True}
    except Exception:
        pass
    
    # ... resto do código existente continua igual
```

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1 — Backend (4-6h)
- [ ] Criar 4 tabelas novas (Alembic migration)
- [ ] Criar models SQLAlchemy
- [ ] Criar router `app/routers/familia.py`
- [ ] Implementar 12 endpoints
- [ ] Modificar webhook (adicionar IF família)
- [ ] Reaproveitar templates de email

### Fase 2 — Frontend (3-5h)
- [ ] Adicionar aba "FAMÍLIAS" no menu top
- [ ] Mover LOJA pro rodapé (já estava lá, só remover do top)
- [ ] Criar tela lista de famílias
- [ ] Criar modal/tela cadastro
- [ ] Criar modal de ajuda [?]
- [ ] Criar onboarding (1ª vez)
- [ ] Sub-abas: DADOS / AULAS / FINANCEIRO
- [ ] Tela de check-in com bloqueio 3+
- [ ] Adicionar 👨‍👩‍👧‍👦 ao lado do nome dos alunos em famílias

### Fase 3 — Testes (1-2h)
- [ ] Cadastrar 1 família teste (Bianca + Rogério)
- [ ] Marcar check-ins (testar bloqueio 3+)
- [ ] Fechar mês
- [ ] Pagar via Stripe
- [ ] Confirmar webhook → email recibo

### Fase 4 — Documentação (30 min)
- [ ] Atualizar README com nova feature
- [ ] Tirar prints pra material marketing

**Tempo total estimado: 8-13 horas**

---

## 🔮 ROADMAP FUTURO

### V2 (3-6 meses)
- Aumentar limite (15? 20?)
- Adicionar campo "tipo do grupo" (família/casal/sócios/empresa)
- Reports gerenciais (PDF mensal pro provedor)
- Limite de aulas/mês por membro
- Pacotes de aulas pré-pagas

### V3 (6-12 meses) — AurumSci Empresarial
- Plano dedicado pra empresas
- Limite alto (50+ funcionários)
- Dashboard corporativo
- Custo por funcionário
- Integração com RH (Gupy, Solides, etc.)
- API pública pra integrações

---

## ⚠️ DECISÕES DE PROJETO

### Por que NF único (CPF ou CNPJ)?
Simplifica UX (1 campo vs 2). Sistema detecta tipo automaticamente. Provedor não precisa pensar.

### Por que mostrar NOMES (não "provedor"/"dependente")?
Inclusivo, humano. Evita hierarquia visual. Internamente sistema sabe quem é provedor.

### Por que limitar 2 pessoas por aula?
Personal de qualidade não opera com 3+. Mantém valores da marca. Bloqueio educa o personal.

### Por que NÃO mexer no individual?
Sistema individual tá testado e funcionando. Família é módulo isolado. Reduz risco a ZERO.

### Por que limite de 10 membros (V1)?
Cobre 95% dos casos reais (família + casal + sócios pequenos). B2B grande fica pra V3.

---

## 🎯 CHECKLIST PRÉ-IMPLEMENTAÇÃO

Antes de começar a programar, validar:

- [ ] Validei design visual com André ✅
- [ ] Schema de banco aprovado
- [ ] Endpoints definidos
- [ ] Lógica de negócio clara
- [ ] Integração Stripe planejada
- [ ] Webhook não vai quebrar
- [ ] Backup do banco antes de migration

---

## 📋 GLOSSÁRIO

| Termo | Significado |
|-------|-------------|
| **Grupo** | Conjunto de até 10 alunos com 1 pagador |
| **Família** | Marca comercial do "Plano Grupo" |
| **Provedor** | Quem paga (★ no app) |
| **Dependente** | Quem treina mas não paga (sem rótulo no app) |
| **NF** | CPF ou CNPJ do provedor (pra nota fiscal) |
| **Tipo 1** | Aula individual (R$ X) |
| **Tipo 2** | Aula em dupla (R$ Y) |

---

## 🏆 CRÉDITOS

**Designer de Produto**: André Andrade (CREF 62702-G/SP)
- Personal trainer com 20 anos
- "Leigo mas esforçado" builder
- Insights memoráveis:
  - "1 pessoa fala bem pra 5, fala mal pra 50"
  - "Foge do trabalho de personal e vira professor de sala"
  - "NÃO MEXER NO QUE ESTÁ PRONTO"
  - "Família, casal, sócios — todos cabem"

**Implementação Técnica**: Claude (Anthropic)
- Documentação, mockups, schema, endpoints

**Sessão**: domingo, 10/05/2026, 11h-13h
- Começamos arrumando webhook session.get() bug
- Continuamos com design completo do Plano Familiar
- Vitória total: sistema 100% automático + design pronto

---

> **"Antes de vender pro outro, precisa funcionar pra mim."**
> — André Andrade, filosofia AurumSci

---

**Status do documento**: ✅ APROVADO PARA IMPLEMENTAÇÃO
**Próximo passo**: Programar Fase 1 (backend) na próxima sessão

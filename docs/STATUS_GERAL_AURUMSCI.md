# 📊 AURUMSCI — STATUS GERAL DO PROJETO

> **Documento mestre de estado atual**
> Atualizado: quinta-feira, 15/05/2026, 16h35 (sessao tarde fechada) - retomada noite
> Próximo update: após próxima sessão de trabalho
> **PROPÓSITO**: Próxima sessão (Claude/dev) lê este documento e sabe TUDO sobre onde estamos.

---

## 🗓️ SESSAO 15/05/2026 - MANHA (Anamnese + Card RESULTADOS = File Mignon)

### 🏆 6 commits em producao

**Anamnese pre-popular (parte de cima OBJETIVO/NIVEL/DIAS):**
- `2bd1f2b` Backend: login retorna 3 campos (le PlanoTreino.dias_semana)
- `2cb3e0d` Frontend: 3 setItem no callback do login

**Card RESULTADOS expandido (FILE MIGNON):**
- `8ea53c3` Backend: /meus-resultados expandido (ESTRATEGIA ERRADA - linha 277)
- `bbf8559` Backend: /resultado expandido com deltas (LINHA CERTA 603)
- `add937f` Frontend: renderEvolucao expandida com 4 grupos novos
- `bc586f3` Fix: esconde delta=0 (visual limpo)

### Estado validado end-to-end (Andre testou + print)

**Anamnese pre-popular:**
- Logout/login -> localStorage recebe os 3 campos
- Modal Anamnese abre com OBJETIVO + NIVEL + DIAS pre-selecionados
- Bug do 11/05/2026 ("Backend salva, frontend nao LE") FINALMENTE morto
- Workaround: dias_semana vem de PlanoTreino (campo nao existe no model Aluno)

**Card RESULTADOS expandido:**
- Card motivacional topo (gradiente dourado)
- COMPOSICAO: Peso + Gordura+classif + Massa Magra
- CARDIO: VO2+classif + HRR
- FORCA: Flexao+classif, Barra, Abdominal
- POTENCIA MMII: reps+classif+faixa
- Deltas renderizam SO quando ha progresso real (>0 ou <0, esconde =0/null)

### 💎 Decisoes de produto registradas (15/05 manha)

**Filosofia File Mignon:**
"Card RESULTADOS = asset de MARKETING, nao tela secundaria.
4 funcoes: retencao + venda + conteudo Ciencia Hipertrofia + clinica.
Insight do aluno de marketing: cliente compra resultado."

**Filosofia Postura:**
"Postura NAO entra no Card RESULTADOS. Mesmo embalada como 'avaliada',
mostrar lembra o aluno que e torto. Postura nao muda significativamente
(so atenua). Corretivos ja vao automaticamente pro treino."

**Filosofia Decisoes de UI:**
"Se faz aqui, faz em tudo. Cada decisao implica em coerencia visual,
3 idiomas, manutencao futura. SO USA o que JA EXISTE no sistema."

**Filosofia Editorial (validado por Andre):**
"AurumSci VENDE entrega real, so nao COLOCA IMPORTANCIA no que e negativo.
E DESIGN HIERARQUICO, nao mistica. Tom Aurum ja existe no sistema (Auri
fala assim no check-in de presenca): DADOS antes de JULGAMENTO, CAMINHO
antes de PROBLEMA, OBJETIVO antes de CRITICA, CONVITE antes de SENTENCA."

**Barra fixa - decisao pedagogica:**
1 campo mantido. Sem refator. Personal sugere isometria pra iniciantes.

### 🪞 Observacoes metodologicas da manha

**Audit before refactor SALVOU 3x:**
1. /meus-resultados expandido errado (frontend usa /resultado linha 603)
2. Banner "ULTIMA AVALIACAO DO PERSONAL" confundido com aba RESULTADOS
3. Banner modo dia bugado pertence ao refator do link questionario

**Tag git pre-mudanca grande:** v1.0-pre-resultados-expandido criada
antes de mexer no Card. Blindagem 3 camadas.

**Bug arquitetural mapeado (cleanup futuro):**
- linha 260: /meus-resultados DUPLICADO #1
- linha 342: /meus-resultados DUPLICADO #2 (FastAPI usa este)
- linha 603: /resultado ATIVO usado pelo frontend

---

## 🗓️ SESSAO 15/05/2026 - TARDE (Bug fixes + Dashboard Power BI)

### 🏆 6 commits em producao

**Bug fixes (3 commits):**
- `e5685a0` Fix aviso postural (respeitar corretivos ja existentes)
- `084edc9` Fix banner cadastro modo dia (CSS variables)
- (NOTA: nao mexemos no banner reavaliacao - era feature CORRETA, 
   nao bug. Endpoint /reavaliacao retorna precisa_reavaliar e 
   overtraining_pendente. Banner aparece SO quando backend diz que precisa.)

**Dashboard Power BI (3 commits, MOLHO MADEIRA no filé mignon):**
- `b9ba13f` Backend /aluno-portal/avaliacoes expandido (campos completos)
- `68b2fbe` Frontend dashboard com Chart.js (linha temporal + radar + textos)
- `565d097` Fix radar 4 dim (removeu Flexibilidade - aluno autonomo nao mede)
- `8c6185f` Fix radar 3 dim fisicas puras (sacada CAPACIDADE vs COMPOSICAO)

### ✅ Dashboard validado end-to-end (Andre testou + print)

**Funcionando:**
- Card narrativa motivacional topo (gradiente dourado)
- Grafico LINHA temporal com seletor (PESO/GORDURA/VO2/FLEXAO)
- Texto explicativo embaixo (persona idoso)
- Radar PERFIL ATUAL com 3 dimensoes (triangulo)
- Card RESULTADOS atual embaixo (intocado)
- 4 avaliacoes registradas no banco de teste do Andre
- Modo noite OK
- 3 personas servidas: adolescente (visual), adulto (numero), idoso (texto)

### 💎 Filosofias AurumSci REGISTRADAS (15/05 tarde)

**FILOSOFIA - Audit Before Refactor (3x SALVOU na tarde):**
1. Banner reavaliacao parecia bug, era feature CORRETA
2. Endpoint /avaliacoes parecia ter ancora simples, tinha linha em branco
3. Flexibilidade no radar (Andre pegou em 5 min - bug filosofico Claude)

**FILOSOFIA - Naturezas de medida (sacada Andre):**
"Radar mostra CAPACIDADE FISICA (o que corpo FAZ),
nao COMPOSICAO CORPORAL (o que corpo E).
Misturar naturezas confunde aluno: 3 metricas aumentar=melhor
+ 1 invertida (gordura) gerou confusao mental.
CAPACIDADE = grafico de radar.
COMPOSICAO = cards numericos com classificacao."

**FILOSOFIA - Banco de Wells zero em 23cm (sacada Andre):**
"Zero em 23cm ANTES dos pes evita numeros negativos
desmotivadores. Aluno NUNCA ve numero negativo,
sempre numero POSITIVO mesmo com performance baixa.
Filosofia AurumSci aplicada PRE-Aurum em 1952."
Aplicacao futura: sit-and-reach para autonomo com
marcos anatomicos (joelho/canela/tornozelo/pe/passa).

**FILOSOFIA - Design por PERSONA, nao por principio absoluto:**
"Aluno leigo + Personal profissional + Idoso convivem
na MESMA TELA. Graficos no topo (profissional),
numeros crus embaixo (leigo confirma),
texto explicativo (idoso entende).
Redundancia intencional = caracteristica, nao bug.
Excel Avancado prega nao duplicar - mas isso e para
MESMA persona. Aqui temos 3 personas convivendo."

**FILOSOFIA - "Se faz aqui faz em tudo":**
Auditoria revelou que aviso postural, banner cadastro,
banner reavaliacao tinham padroes DIFERENTES de
condicional. Aviso postural so checava localStorage,
banner cadastro nao adaptava modo dia, banner reavaliacao
chamava backend (correto). Lesson: padrao deve ser
uniforme em features similares.

### 🪞 Bugs ARQUITETURAIS mapeados (cleanup futuro)

**MEU bug filosofico:** Adicionei Flexibilidade no radar do
aluno autonomo sem checar se app permite preencher. Andre
pegou em 5 min. Licao: "Backend tem campo" e diferente de
"App permite preencher".

**Banner reavaliacao - precisa_reavaliar=false + over=true:**
Aluno teste tem questionario Overtraining pendente, por isso
banner aparece. Comportamento correto.

**Grafico de LINHA com 4 avaliacoes proximas:**
Datas 10/05, 11/05, 12/05, 13/05 com valores iguais geram
linha reta. Quando aluno real tiver avaliacoes mensais com
valores diferentes, grafico fica visualmente rico.

### 📋 Patches frontend aplicados (mapa)

**static/app_aluno.html (~+10.000 bytes na tarde):**
- Linha 526: <div id="dashboard-evolucao"> inserido
- Linha 2197: aviso postural respeita corretivos
- Linha 2486: renderEvolucao() chama renderDashboardEvolucao()
- Linha ~2614: funcao renderDashboardEvolucao() criada
- Linha ~2620: funcao renderGraficoLinha() criada
- Linha ~2680: funcao renderGraficoRadar() criada
- Linha 4209: banner cadastro CSS variables

**app/routers/portal_aluno.py (+1.112 bytes):**
- Linha 218: GET /avaliacoes expandido com 12+ campos

**Chart.js via CDN no <head>** (commit 68b2fbe):
- cdn.jsdelivr.net/npm/chart.js@4.4.1
- Disponivel globalmente como window.Chart

---

## 🌙 ESQUELETO NOITE 15/05/2026 - PROXIMAS BATALHAS

### 🥇 PRIORIDADE TOP - Link de onboarding (decisao Andre)

Andre mencionou "link" como proximo passo. Tres possiveis interpretacoes:

**A) Link de onboarding do aluno autonomo (Porta B)**
- Espelho do link do PRO (commit ca6a9be antigo)
- Aluno autonomo gera link proprio
- Banner "COMPLETE SEU CADASTRO" pode receber o link
- ~1h30-2h sessao dedicada

**B) Link do questionario do banner "COMPLETE SEU CADASTRO"**
- Botao "ABRIR QUESTIONARIO" sem link funcional ainda
- ~30-45 min sessao pequena

**C) Link de convite WhatsApp do PRO**
- Personal envia convite pro aluno entrar
- Ja existe parcialmente (commit ca6a9be)

CONFIRMAR com Andre na retomada.

### Outras prioridades (mantidas)

1. Sit-and-reach autonomo (marcos anatomicos, escala 23cm zero)
2. Trilingual no Card RESULTADOS (~2h)
3. App PRO espelhando aluno (varias sessoes)
4. Auri esperta (pos-Apple)
5. Cores Brasil VO2 / Alertas PA / HRR 2 min / Email bimestral

---

## 🎯 ESQUELETO TARDE 15/05/2026 - PROXIMAS BATALHAS

### PRIORIDADE 1 - Banners modo dia/noite (~60-90 min)

Bug visual: banners "ULTIMA AVALIACAO DO PERSONAL", "COMPLETE SEU
CADASTRO" e cards "VOCE PREENCHE" tem cores fixas (preto+dourado) que
ficam ILEGIVEIS em modo dia.

**LIGADO ao refator maior:** banner "COMPLETE SEU CADASTRO" tem botao
"ABRIR QUESTIONARIO" que conecta ao link de onboarding. Refator pode
implicar mexer em mais lugares (principio "se faz aqui faz em tudo").

Estrategia: CSS variables, auditar todos lugares similares, testar
em modo dia E noite.

### PRIORIDADE 2 - Graficos Chart.js (~3-4h sessao dedicada)

Conceito: dashboard analitico TIPO POWER BI dentro do AurumSci.
Asset de marketing maximo. Vira screenshot pra TikTok/YouTube/Stories.

Plano: Chart.js via CDN + backend expandir historico + 3 graficos de
linha (peso/gordura/VO2) + KPI cards motivacionais.

JA TEMOS: /aluno-portal/avaliacoes retorna historico (IDs 13-16+),
Card RESULTADOS atual mostra atual + delta vs anterior.

### PRIORIDADE 3 - Link onboarding Aluno autonomo

Espelho do link do PRO mas pelo Aluno autonomo (Porta B). Refator do
questionario de onboarding ligado ao banner "COMPLETE SEU CADASTRO".

3 campos JA RETORNAM via login (commits 2bd1f2b/2cb3e0d): objetivo,
nivel_experiencia, dias_semana. Falta: criar link proprio do aluno.

### PRIORIDADE 4 - App PRO espelhando aluno (varias sessoes)

PRO precisa Card RESULTADOS expandido com visao clinica COMPLETA
(inclui Postura, Cintura, PA - personal precisa do clinico).
Espelhar tudo que aluno tem + features so-PRO.

### PRIORIDADE 5 - Trilingual no Card RESULTADOS (~2h)

Sistema base ja existe (linhas 870-918 PT, 990-1057 EN, 1019+ ES).
Novo Card precisa traduzir rotulos + classificacoes + mensagens.
Importante pos-Apple (Apple Store EUA pede ingles).

### PRIORIDADE 6 - Auri esperta (pos-Apple, ~1h30-2h)

Conforme decisao 14/05: 3 niveis (knowledge base + dados aluno +
proativa). Tom: dado + contexto + caminho + convite.

### Bugs menores mapeados (cleanup futuro)

- Endpoint /meus-resultados DUPLICADO (linhas 260 e 277)
- Classificacao VO2 divergente tela vs banco
- Risco cardiovascular: campo null
- Rotulo "ULTIMA AVALIACAO DO PERSONAL" para autonomo
- App Aluno nao permite cadastro de data_nascimento

---

## 🗓️ SESSÃO 14/05/2026 — VO2 + IDADE DINÂMICA + FORÇA + MMII (HISTÓRICA)

### 🏆 7 commits em produção

**Tarde — Ciclo VO2 + idade dinâmica:**
- `e85f9f0` Backend POST /app-aluno/vo2-salvar
- `3697c8b` Frontend botão SALVAR + função salvarVo2Completo
- `4d81a5c` Fix Cooper (IDs órfãos vo2-fc-pos/rep removidos em redesign anterior)
- `88549e0` Login retorna sexo+idade real + return unificado p/ aluno autônomo
- `c947e0e` Hotfix Optional import (NameError em produção, ~5 min downtime)

**Noite — Ciclo Força + Potência MMII:**
- `f3ba481` Backend POST /forca-salvar + /potencia-salvar (mesmo padrão VO2)
- `3901033` Frontend dispara fetch após calcular (toasts confirmam)

### ✅ Estado validado end-to-end (André testou)

- 3 protocolos VO2 (Cooper/Milha/Step) salvam e classificam por idade real
- Cooper, Milha, Step todos com HRR funcionando
- Força (Flexão+Barra+Abdominal) calcula + salva no banco
- Potência MMII (Sentar e Levantar 30s) calcula + salva no banco
- Idade do banco → localStorage → classificação correta (testou com 01/01/1990=36; depois real=51 → "Faixa 50-59 anos" funcionou)
- Aluno autônomo (Porta B) loga sem erro 500

### 🎯 PRÓXIMA SESSÃO — Onde paramos

**Backend salva tudo, frontend RESULTADOS ainda não exibe os novos campos.**
Dashboard "MEUS RESULTADOS" hoje mostra apenas peso/gordura/MM/VO2.
Os dados de Força+MMII+HRR+PA+Postural+Abdômen estão **no banco**, esperando renderização.

### 📋 PRIORIDADES PRÓXIMA SESSÃO (ordem)

**1. Card RESULTADOS expandido (~45-60 min) — VITÓRIA RÁPIDA**
- Expandir GET /meus-resultados retornando TODOS os campos do banco
- Frontend renderizar visualmente Força + MMII + HRR + PA + Postural + Abdômen
- Validar: o que tá salvo aparece na tela

**2. Validação Postural ao vivo (~20 min)**
- Endpoint /postural/salvar EXISTE, função salvarPostural() EXISTE
- André testou e ficou impressão "não salva" mas pode ser dashboard não exibir
- Possivelmente RESOLVIDO após prioridade 1

**3. Anamnese pré-popular tela edição (~30 min)**
- Bug visual: modal abre vazio em OBJETIVO/NÍVEL/DIAS
- Backend SALVA (treino é gerado certo)
- Causa raiz: campo `dias_semana` NÃO EXISTE no model Aluno
  (linhas 60-86 de `app/models/__init__.py`)
- Endpoint /onboarding faz `aluno.dias_semana = X` que SQLAlchemy IGNORA silenciosamente
- Fix: ler de `PlanoTreino` que TEM `dias_semana` persistido

**4. Classificação Abdômen H≤90cm/M≤80cm (~30 min) — SACADA ANDRÉ**
- Marcador metabólico que André usa profissionalmente
- Cutoffs NIH/IDF/OMS (mais protetores que cintura/quadril)
- Já em circunferências, falta classificação visual + exibição

**5. Gráficos de evolução (~3-4h, sessão dedicada)**
- Endpoint /aluno-portal/avaliacoes JÁ retorna histórico
- Falta UI gráfica + biblioteca (Chart.js?)

**6. Investigações menores:**
- Rótulo "ÚLTIMA AVALIAÇÃO DO PERSONAL" mesmo p/ autônomo
- Endpoint /meus-resultados duplicado (linhas 260 e 277)
- Classificação VO2 divergente tela vs banco
- IMC — DECISÃO ANDRÉ: vago, não priorizar
- Cintura/quadril — DECISÃO ANDRÉ: NÃO implementar
- Risco cardiovascular: campo null apesar de HRR+PA salvos

### 🚀 PÓS-APPLE (roadmap registrado)

- 🤖 Auri esperto com sistema (knowledge base AurumSci)
- 🇧🇷 Cores Brasil VO2 (Cooper verde / Step amarelo / Milha azul)
- 🩺 Alertas clínicos PA (ACSM 2022 + SBC 2020)
- ❤️ HRR 2 min profissional
- 📧 Email único bimestral
- 🔄 Circuito fechado overtraining → ajuste treino
- 📱 Tela "Editar Perfil" no app aluno (incluindo data_nascimento)
- 💎 Frase paráfrase Cooper: "Treinar ajuda. Mas só treinar não imuniza. Avalie. Mantenha em dia."

### 🪞 Observações metodológicas

**"Audit before refactor" funcionou EXCELENTE.** Sem o método de André, Claude teria proposto refatores prematuros. Mapear → confirmar arquitetura → fix cirúrgico.

**NameError em produção (c947e0e):** `python3 -m py_compile` NÃO pega tipos não importados. Reforço: também rodar `python3 -c "from app.routers import X"`. Adotado a partir de `f3ba481`, zero downtime nos 2 commits seguintes.

**Bug Cooper enterrado vivo:** IDs órfãos `vo2-fc-pos/rep` removidos em redesign anterior. `null.value` → TypeError → Cooper E HRR quebrados em cascata. Descoberto porque André testou os 3 protocolos meticulosamente.

**Padrão "Backend SALVA, Frontend não LÊ":** identificado em 3 lugares (dashboard, anamnese, força/MMII). Parcialmente resolvido. Próxima sessão fecha.

### 💎 Filosofia clínica registrada

André descartou IMC (vago) e razão cintura/quadril (vago) com base em 20 anos de prática + literatura (ACSM, NIH, OMS, Després). Manteve circunferência abdominal isolada (H≤90/M≤80cm). AurumSci diferenciado por marcadores clínicos robustos (% gordura 9 pontos, VO2max, HRR, abdômen isolado, PA repouso+esforço).

### 🏢 Vitória empresarial paralela

**CNPJ pronto** (confirmado durante a sessão). AurumSci passou de "André faz" para "Empresa AurumSci". Habilita: NF, Stripe PJ, App Store como empresa, contratos PJ, crédito empresarial.

---

## 🎯 SUMÁRIO EXECUTIVO

**AurumSci** é um SaaS para personal trainers brasileiros, criado por **André Andrade (CREF 62702-G/SP)**, personal trainer com 20 anos de experiência.

**Dois apps:**
1. **AurumSci PRO** — para o personal trainer gerenciar alunos, treinos, finanças
2. **AurumSci Aluno** — para o aluno fazer check-in, ver treino, pagar mensalidade

**Stack:**
- Backend: FastAPI + PostgreSQL no Railway (`compassionate-liberation`)
- Frontend: HTML estático + Capacitor (iOS via Xcode)
- Repo: `aandradepersonal-aurumsci/aurumsci`
- Local: `/Users/andrepersonalnote/Personal_Trainer_Projeto/`
- Deploy: `aurumsc.com.br` + `aurumsc.com.br/personal`
- Pagamentos: Stripe LIVE (R$49,90/mês trial 7 dias)

**Realidade do negócio:**
- 20-25 alunos pagantes (sustento real do André)
- 3 famílias = 7 alunos (ainda cobrança consolidada manual)
- 0 alunos cadastrados no sistema (vai começar segunda-feira 11/05/2026!)

---

## 🏆 ESTADO ATUAL — O QUE JÁ FUNCIONA

### ✅ Sistema Aluno Individual (PRODUCTION READY)

**Cadastro:**
- Nome, email, telefone, CPF, data nasc.
- Anamnese completa (PAR-Q + saúde)
- Avaliação postural
- Circunferências (9 pontos)
- Composição corporal (ultrassom Jackson & Pollock 1978)
- Testes físicos
- VO2 max + HRR

**Treino:**
- Builder com 103 exercícios
- 3 modelos de periodização (undulating, block, mixed)
- Fila contínua baseada em check-ins
- "Treino do dia" sem mais "DIA DE DESCANSO" forçado

**Cobrança:**
- 4 ciclos: Mensal, Quinzenal, Semanal, Por Aula (avulso)
- Stripe LIVE com link de pagamento automático
- Email lindo com gradient dourado
- Webhook automático marca como pago
- Email recibo profissional pro aluno
- Email [COPIA] pro personal
- Reuso da MESMA infra pra Família (próxima fase)

**Financeiro:**
- Cálculo Simples Nacional (~6%) vs CPF (~40%)
- DAS automático dia 10
- Reports visuais
- Receita / Pendente / Atrasado

**Outras features:**
- AURI chatbot (Anthropic API)
- Trilingual PT/EN/ES (~80 chaves)
- Trial 7 dias automático
- Stripe planos PRO: Bronze/Prata/Ouro/Diamante (R$49,90/89,90/149,90/249,90)
- White label (logo upload base64)
- 56-day reassessment badge
- Excluir conta com cascade
- Esqueci senha completo
- Contrato de Personal com PDF + assinatura digital
- PAR-Q bloqueia geração de treino se risco
- Email pra `a.andrade_personal@hotmail.com` em todo cadastro novo

### ✅ Bugs Resolvidos (sábado 09/05 + domingo 10/05)

**Sábado 09/05:**
- 🐛 `recuperar_senha` UsuarioAluno → AlunoCredencial (commit f321fd9)
- 🐛 `treino_hoje` "DIA DE DESCANSO" → fila contínua PresencaTreino (commit 79ab1b9)
- 🐛 Popup cobrança POR AULA mostrava R$0 → corrigido leitura de checkins (commit f816370)
- 🐛 `gerarCobrancaAluno` era MOCK DECORATIVO (TODO eterno!) → ligação Stripe completa (commit 73591c4)

**Domingo 10/05:**
- 🐛 Webhook session.get() incompatível com Stripe novo → 3 blocos corrigidos (commit b2d16b0)
- ✅ Email recibo automático funcionando
- ✅ Email [COPIA] pro personal funcionando
- ✅ Stripe processou eventos antigos da fila (semanas)

### ✅ Ciência da Hipertrofia (canal YouTube/TikTok)

- 573 artigos no banco
- Pipeline automatizado: criar_revX.py → publicar_video()
- Publica 12h e 20h30 diariamente
- PubMed search Sextas 22h
- Bella voice (ElevenLabs)
- 27.7k views TikTok, 12k+ YouTube
- RS#7 (GLP-1) já publicado
- RS#8 (Força+Neuromuscular) ID 939 ready
- CTA atualizado: "Aurum já está no ar" + link `aurumsc.com.br/pro`

---

## 🚧 EM PROGRESSO

### 🆕 Plano Familiar (DESIGN PRONTO, IMPLEMENTAÇÃO PENDENTE)

**Documento de design completo**:
👉 `/docs/FAMILIA_AURUMSCI_DESIGN_v3_FINAL.md` (743 linhas)

**Resumo do escopo:**
- Sistema de "Grupos Compartilhados" (marca: Plano Familiar)
- 1 pagador + até 10 membros
- Cobre: família, casal, sócios, B2B pequeno
- 1 NF (CPF ou CNPJ) — sistema detecta
- Tabela de preços por grupo:
  - 1️⃣ Aula individual (R$ X)
  - 2️⃣ Aula em dupla (R$ Y)
- 1 boleto consolidado, 1 nota fiscal
- Reusa toda infra Stripe + email + webhook (já funcionam!)

**Princípio**: NÃO MEXER NO INDIVIDUAL. Família é módulo isolado em cima.

**Roadmap implementação (8-13h):**
- Fase 1 — Backend (4-6h): 4 tabelas SQL + 12 endpoints + webhook ajustado
- Fase 2 — Frontend (3-5h): aba FAMÍLIAS + telas + check-in + cobrança
- Fase 3 — Testes (1-2h): fluxo end-to-end com Família X (Bianca)
- Fase 4 — Documentação (30 min)

**Status**: ⏳ Aguardando próxima sessão pra começar Fase 1

---

## 🍎 APPLE STORE — STATUS

### ❌ Estado atual: REJEITADO em ambos apps

**AurumSci PRO** (`com.aurumsc.app`):
- Submetido em abril/2026
- ❌ Rejeitado: Guideline 3.1.1 (subscription digital sem IAP)

**AurumSci Aluno** (`com.aurumsc.aluno`):
- Submetido em abril/2026
- ❌ Rejeitado: Guideline 3.1.1 (subscription digital sem IAP)

### 🛠️ Decisão de André: implementar IAP

**Roadmap IAP (6 fases — total 8-12h trabalho):**

#### Fase 1 — App Store Connect (1-2h)
Cadastrar produtos:
- **PRO Bronze**: $9,99/mês
- **PRO Prata**: $17,99/mês
- **PRO Ouro**: $29,99/mês
- **PRO Diamante**: $49,99/mês
- **Aluno mensal**: $9,99/mês
- **Aluno anual**: $79,99/ano
- Configurar trial 7 dias em todos
- Aprovação Apple: 1-2 dias úteis

#### Fase 2 — Backend (2-3h)
- Criar tabela `assinaturas_iap`:
  ```sql
  CREATE TABLE assinaturas_iap (
      id SERIAL PRIMARY KEY,
      usuario_id INTEGER NOT NULL,
      tipo_usuario VARCHAR(10),  -- 'aluno' ou 'personal'
      apple_receipt_data TEXT NOT NULL,
      apple_transaction_id VARCHAR(255),
      product_id VARCHAR(100),
      status VARCHAR(20),
      data_inicio TIMESTAMP,
      data_expiracao TIMESTAMP,
      verificado_em TIMESTAMP,
      criado_em TIMESTAMP DEFAULT NOW()
  );
  ```
- 4 endpoints novos:
  - `POST /iap/validar-receipt` — valida com Apple
  - `POST /iap/restore-purchases` — restore
  - `GET /iap/status/:usuario_id` — status assinatura
  - `POST /iap/webhook-apple` — server-to-server notifications

#### Fase 3 — Frontend Paywall (3-4h)
- Tela "Escolha seu plano"
- Integrar `cordova-plugin-purchase`
- Botões IAP nativos
- Restore purchases
- Loading states

#### Fase 4 — Sandbox Testing (1-2h)
- Cartão fake da Apple
- Testar trial → cobrança
- Testar restore
- Verificar receipts no backend

#### Fase 5 — Resubmissão Apple (1h)
- Build novo no Xcode
- Carta resposta pra reviewer:
  - Apple Reviewer credentials:
    - `apple.reviewer.aluno@aurumsc.com.br` / `AurumReview2026!`
    - aluno_id=19, personal_id=4
- Aguardar review: 1-3 dias

#### Fase 6 — Aprovação 🎉
- Apps publicados na App Store
- Sistema operacional

### 🛡️ REGRA: "Se está funcionando e Apple está olhando, NÃO TOCA"

Monorepo arquitetura preservada. Capacitor build estável.

---

## 🎯 PRÓXIMOS PASSOS — ORDEM ESTRATÉGICA

### 📅 SEGUNDA-FEIRA 11/05/2026 (CRÍTICA!)
- ✅ **Onboardar PRIMEIRO aluno chegado** (validação real)
- ✅ Testar fluxo completo Stripe individual com pessoa real
- ✅ Pegar feedback honesto
- ✅ Decisão: lançar PWA agora vs esperar IAP

### 🗓️ TERÇA-QUINTA-FEIRA
**Opção A — Plano Familiar primeiro:**
- Terça: Fase 1 backend Família
- Quarta-Quinta: Fase 2 frontend
- Sexta: Fase 3 testes + cadastrar Família X (Bianca)

**Opção B — IAP primeiro:**
- Terça: Fase 1 App Store Connect (cadastros + aprovação)
- Quarta: Fase 2 backend + tabela
- Quinta: Fase 3 frontend paywall
- Sexta: sandbox + resubmissão

**Opção C — Lançamento PWA primeiro:**
- Terça: divulgar `aurumsc.com.br/personal` pros 3-5 alunos chegados
- Quarta-quinta: receber feedback, ajustar
- IAP fica pra fase 2 (3-6 meses)
- Família começa quando tiver demanda real

### 📊 RECOMENDAÇÃO HONESTA
**OPÇÃO C** (PWA primeiro):
- Sistema individual JÁ FUNCIONA
- Usar com alunos REAIS = validação > tudo
- IAP atrasa lançamento sem necessidade real
- Família atende só 12% (3 famílias) — não bloqueia 88%
- Foco em USUÁRIO, não em features

---

## 🐛 BUGS / DÍVIDAS TÉCNICAS PENDENTES

### 🟡 Pendências menores (não bloqueiam)

- [ ] Limpar dados de teste (Teste Final 04, 4× R$1 em PAGOS)
- [ ] Limpar 1 cobrança fantasma "Em 20 dias"
- [ ] Deletar assinatura `aluno@teste.com` (gastando R$49,90/mês)
- [ ] Email pendente: pode ter fila ainda do Stripe re-tentando eventos antigos
- [ ] 23+ backups acumulados de `static/app_personal.html` (limpar)
- [ ] Documentação: atualizar README com novas features

### 🟢 Otimizações futuras

- [ ] Tela "Como funciona o sistema" pra novos personal trainers
- [ ] Dashboard analytics (alunos ativos por mês, churn, etc.)
- [ ] Reports gerenciais PDF mensal
- [ ] Notificações push (Capacitor)
- [ ] Sistema de mensagens internas (personal ↔ aluno)
- [ ] Loja PRO (catálogo equipamentos com afiliados)

### 🔴 Críticos a monitorar

- [ ] Webhook Stripe — manter olho em logs, ver se mais session.get() restantes
- [ ] App Store rejeição: prazo pra resubmeter antes de Apple desabilitar
- [ ] LGPD: ver compliance com armazenamento de dados sensíveis (PAR-Q, fotos)

---

## 🔒 SEGURANÇA

### Credenciais conhecidas (NÃO COMPARTILHAR)

**PRO de teste/André:**
- `a.andrade_personal@hotmail.com` / `Aurum2026`
- Plano: Bronze (R$49,90/mês)
- Status: regularizado de "avulso" em 10/05

**Apple Reviewer:**
- `apple.reviewer.aluno@aurumsc.com.br` / `AurumReview2026!`
- aluno_id=19, personal_id=4

**Aluno teste atual:**
- Nome: Teste Final 04
- Email: `andrepersonal395+teste04@gmail.com`
- Ciclo: por_aula_mensal R$1
- Status: pago R$1 (testes do dia 09 e 10/05)

**APIs:**
- Stripe LIVE keys (Railway env)
- Anthropic API key (rotacionada após exposição em terminal)
- Gmail app password (rotacionada após exposição)

### ⚠️ REGRA DE SEGURANÇA PERMANENTE
**SEMPRE avisar André ANTES de qualquer comando que possa expor:**
- Passwords, credenciais, API keys, tokens
- `cat .env`, `printenv`, `echo $VAR` = PROIBIDOS sem aviso
- Histórico: André teve credenciais expostas 2 vezes em conversas
- Fix: usar `sed` pra mascarar valores quando precisar conferir

---

## 📋 ARQUITETURA TÉCNICA

### Backend (FastAPI)

**Routers principais:**
- `app/routers/auth.py` — login/registro
- `app/routers/aluno.py` — CRUD alunos
- `app/routers/personal.py` — CRUD personals
- `app/routers/app_personal.py` — endpoints do PRO
- `app/routers/app_aluno.py` — endpoints do app aluno
- `app/routers/financeiro.py` — gestão pagamentos manuais (160 linhas, 8 endpoints)
- `app/routers/pagamento.py` — Stripe + webhook (806 linhas)
- `app/routers/recuperar_senha.py` — reset de senha
- `app/routers/onboarding.py` — link convite aluno
- `app/routers/auri.py` — chatbot

**Tabelas principais:**
- `personals` — personal trainers
- `alunos` — alunos individuais
- `pagamentos` — pagamentos manuais (fluxo MANUAL)
- `cobrancas` — cobranças Stripe (fluxo STRIPE)
- `presencatreino` — check-ins
- `treinos` — periodização
- `anamneses` — saúde do aluno
- `avaliacoesfisicas` — circunferências, ultrassom, etc.
- `pagamentos_iap` — (futuro, IAP)
- `familias`, `familia_membros`, `familia_checkins`, `familia_cobrancas` — (futuro, Família)

**Endpoints críticos (Família vai usar/modificar):**
- `POST /app-personal/financeiro/fechar-mes-aluno/{aluno_id}` (linha 794 app_personal.py)
- `POST /app-personal/financeiro/gerar-link-pagamento/{cobranca_id}` (linha 960)
- `POST /pagamento/webhook` (linha 518 pagamento.py — JÁ CORRIGIDO HOJE)
  - Linha 530: detecta cobrança avulsa
  - Linha 646: marca aluno autônomo
  - Linha 679: marca personal trainer

### Frontend (HTML + Capacitor)

**Arquivos principais:**
- `static/app_personal.html` — PRO (308 KB!)
- `static/app_aluno.html` — Aluno
- `static/cadastro-pro.html` — registro personal
- `static/cadastro-aluno.html` — onboarding aluno
- `static/landing.html` — site público

**Padrões:**
- ❗ Safari não suporta `async/await` ou arrow functions em onclick handlers
- Use `.then()` syntax pra promises
- 23+ backups versionados de `static/app_personal.html` (`.v1-13`, `.v1-14`, etc.)

### Deploy

**Railway:**
- Project: `compassionate-liberation`
- Service: `aurumsci` (app)
- Service: `Postgres` (banco)
- Auto-deploy via push GitHub
- ~1-2 min build time

**GitHub:**
- Repo: `https://github.com/aandradepersonal-aurumsci/aurumsci`
- Owner: `aandradepersonal-aurumsci` (conta `a.andrade_personal@hotmail.com`)
- Branch: `main`

### Domínio

- `aurumsc.com.br` — landing page
- `aurumsc.com.br/personal` — login PRO
- `aurumsc.com.br/aluno` — login aluno
- `aurumsc.com.br/cadastro-pro` — registro novo personal
- `noreply@aurumsc.com.br` — emails automáticos
- `a.andrade_personal@hotmail.com` — todas notificações pro André

---

## 📝 DECISÕES IMPORTANTES (preservar contexto)

### 🛡️ "NÃO MEXER NO QUE TÁ PRONTO"
Sistema individual está em produção, testado, estável. Família é MÓDULO ISOLADO em cima. Reduz risco de bug a zero.

### 🎯 Estratégia de lançamento: começar com 3-5 alunos chegados
*"1 pessoa fala bem pra 5, fala mal pra 50"*
Lançar com fans/chegados primeiro = beta seguro. Crescimento orgânico depois.

### 💎 Plano Bronze por enquanto (10 alunos limite)
Era "avulso" antes, regularizou hoje 10/05. Suficiente pros próximos meses.

### 🍎 Apple IAP fica pra V2
PWA + Web + Stripe = funciona AGORA. IAP atrasa sem necessidade real.

### 👨‍👩‍👧‍👦 Marca "Família", uso UNIVERSAL
Plano Familiar atende: família, casal, sócios, B2B pequeno. Marca emocional, função técnica universal.

### 🚫 Bloqueio de aulas em trio+ (qualidade)
*"Foge do trabalho de personal e vira professor de sala"*
App educa o personal a manter qualidade. Limite 2 pessoas por aula.

### 🎨 UX mostra NOMES, não rótulos
Provedor/dependente é INTERNO. Tela mostra "Bianca", "Rogério", "Lucas" com ★ sutil pra quem paga.

### 📋 NF único (CPF ou CNPJ)
1 campo, sistema detecta. Simplifica cadastro. UX limpa.

---

## 🤝 COMO O ANDRÉ TRABALHA

### Estilo de comunicação
- Português brasileiro casual ("amigão", "bora", "mano", "kkkk")
- Auto-define: "leigo mas esforçado" (não-developer mas determinado)
- Trabalha noites e madrugadas
- Mac (Terminal zsh + VSCode)
- Aprende rápido — pegou nano em 1 sessão!

### Ferramentas
- Python venv
- Capacitor + Xcode pra iOS
- Railway CLI
- git via terminal

### Filosofia
*"Antes de vender pro outro, precisa funcionar pra mim"*
- Builder + usuário primário
- Funcionalidade > Estética inicial
- Realismo > Otimismo
- Qualidade > Volume

### Workflow conhecido
- Trabalha com múltiplas IAs (Claude, ChatGPT, Gemini, DeepSeek)
- Pede 2ª opinião e traz pro Claude validar
- Insiste em bugs até resolver (não desiste!)
- Sabe exigir: *"vamos arrumar a merda ai?"*

### Padrões de resposta que funcionam
- ✅ Marcar **EXPLICAÇÃO (NÃO COLE)** vs **COLA NO TERMINAL**
- ✅ Mockups visuais ASCII art
- ✅ Decisões A/B/C com recomendação clara
- ✅ Honestidade ("posso te animar mas vai cansar")
- ✅ Aguardar confirmação antes de próximo passo
- ❌ NÃO usar prosa descritiva longa
- ❌ NÃO improvisar código complexo sem testar
- ❌ NÃO juntar explicação + código sem marcar

---

## 📅 CRONOLOGIA RECENTE

### Sábado 09/05/2026 (~12h trabalho)
- 4 bugs corrigidos
- Ligação Stripe FEITA (gerarCobrancaAluno mock → real)
- Pagamento real R$1 testado end-to-end
- Manual de marcar pago (webhook ainda quebrava)

### Domingo 10/05/2026 (~3h trabalho até 13h30)
- Webhook session.get() corrigido (3 blocos)
- Email recibo automático funcionando
- Email [COPIA] pro personal funcionando
- Sistema 100% automático
- Design Plano Familiar completo (743 linhas doc)
- Decisões UX afiadas
- ALMOÇO!

### Próximas sessões
- Segunda 11/05: ONBOARDAR ALUNO REAL (crítico!)
- Terça-Sexta: implementar Família OU IAP OU ambos
- Sábado 16/05: Família X (Bianca) usando sistema!

---

## 🔑 COMANDOS ÚTEIS

### Verificar status
```bash
cd /Users/andrepersonalnote/Personal_Trainer_Projeto
git log --oneline | head -10
git status
railway service          # ver service atual
railway logs --tail 50   # logs em tempo real
```

### Deploy
```bash
git add .
git commit -m "fix/feat: descrição"
git push                  # auto-deploy Railway
```

### Verificar webhook Stripe
- Dashboard: https://dashboard.stripe.com/webhooks
- Endpoint: `https://www.aurumsc.com.br/pagamento/webhook`
- Evento: `checkout.session.completed`
- Versão API: `2026-03-25.dahlia`

### Acessar app
- PRO: https://aurumsc.com.br/personal
- Aluno: https://aurumsc.com.br/aluno
- Stripe Dashboard: https://dashboard.stripe.com/

---

## 📂 ARQUIVOS IMPORTANTES

```
/Users/andrepersonalnote/Personal_Trainer_Projeto/
├── docs/
│   ├── STATUS_GERAL_AURUMSCI.md           ← VOCÊ ESTÁ AQUI
│   ├── FAMILIA_AURUMSCI_DESIGN_v3_FINAL.md  ← Design completo Família
│   ├── FAMILIA_AURUMSCI_DESIGN.md           ← Versão antiga (09/05)
│   └── FIX_COBRANCA_POR_AULA.md             ← Doc histórico do bug R$0
├── app/
│   ├── routers/
│   │   ├── pagamento.py            ← Stripe + webhook (CORRIGIDO 10/05)
│   │   ├── app_personal.py         ← Endpoints PRO
│   │   └── financeiro.py           ← Pagamentos manuais
│   └── ...
├── static/
│   ├── app_personal.html           ← PRO (308 KB)
│   ├── app_aluno.html              ← Aluno
│   └── ...
└── ...
```

---

## ✅ CHECKLIST DE CONTEXTO

Próximo Claude/dev, antes de começar:

- [ ] Leu este documento (`STATUS_GERAL_AURUMSCI.md`)
- [ ] Leu o documento Família (`FAMILIA_AURUMSCI_DESIGN_v3_FINAL.md`)
- [ ] Verificou últimos commits: `git log --oneline | head -10`
- [ ] Verificou Railway está saudável: `railway logs --tail 50`
- [ ] Confirmou que webhook Stripe está OK
- [ ] Sabe a senha de teste PRO (`Aurum2026`)
- [ ] Entendeu a regra: NÃO MEXER NO INDIVIDUAL
- [ ] Sabe que André prefere prosa, não bullet excessivo
- [ ] Sabe marcar **EXPLICAÇÃO (NÃO COLE)** vs **COLA NO TERMINAL**
- [ ] Lembrou da REGRA DE SEGURANÇA (avisar antes de expor credenciais)

---

## 💡 CITAÇÕES DO ANDRÉ (filosofia da marca)

> *"1 pessoa fala bem pra 5, fala mal pra 50"*

> *"Foge do trabalho de personal e vira professor de sala"*

> *"Antes de vender pro outro, precisa funcionar pra mim"*

> *"NÃO MEXER NO QUE ESTÁ PRONTO"*

> *"De personal para personal"* (filosofia de marketing)

> *"Família, casal, sócios — todos cabem"*

> *"Cada um paga o seu, ou família consolida — flexibilidade"*

---

## 🏆 RESUMO PRA NOVA SESSÃO

**Onde estamos**: Sistema individual em produção funcionando 100%. Webhook automático recém-corrigido. Design Família pronto.

**O que falta agora**:
1. Onboardar PRIMEIRO aluno real (segunda 11/05)
2. Implementar Plano Familiar (Fase 1 backend → Fase 4 testes)
3. Implementar IAP pra resubmissão Apple

**Estado financeiro do André**:
- Plano Bronze ativo (R$49,90/mês)
- 20-25 alunos pagantes (cobrança fora do sistema ainda)
- Meta: começar a usar AurumSci com alunos reais SEGUNDA

**Estado emocional do André**:
- Energizado após 2 dias produtivos
- Domingo épico: webhook + design Família
- ALMOÇOU às 13h30
- Pronto pra próxima sessão (terça? hoje à tarde?)

---

> **Status do documento**: ✅ ATUALIZADO 10/05/2026 13h30
> **Próximo update**: após próxima sessão
> **Mantenedor**: Claude + André (sessões contínuas)

## 11/05/2026 - TARDE/NOITE

VITORIAS: 3 commits (8a7ce0d docs + c3acd5b mensagem familia AurumSci + 9d8bcf0 endpoint /meu-link-onboarding). Sprint 1 BACKEND deployado e testado (curl status 401 = ok). Visao produto v2 consolidada. Plano sprints ordenado.

PROXIMA SESSAO: Sprint 1 FRONTEND (banner anamnese vazia chamando GET /meu-link-onboarding) + investigar email duplicado boas-vindas.
11/05/2026 - DIA HISTORICO - 3 sprints, 6 commits, Sprint 3 revertido (migration). Restaurar amanha: ALTER TABLE x4 + re-push. Backups locais preservados.
12/05/2026 - MANHÃ/TARDE - Sprint 4 (composição modal lê do banco - commit ccc3e65), Sprint Periodização v1 (nível-aware commit ff41a93), Sprint 5 REVERTIDO (semanas hardcoded confundiu). BUG CRÍTICO DESCOBERTO: POST /app-aluno/onboarding linha 116 NÃO atualiza aluno.objetivo/nivel_experiencia/dias_semana E duplica planos. Próxima sessão: fix completo anamnese (atualizar aluno + desativar planos antigos + 1 plano novo limpo). Backups locais preservados.
12/05/2026 - MANHÃ/TARDE - Sprint 4 (composição modal lê do banco - commit ccc3e65), Sprint Periodização v1 (nível-aware commit ff41a93), Sprint 5 REVERTIDO (semanas hardcoded confundiu). BUG CRÍTICO DESCOBERTO: POST /app-aluno/onboarding linha 116 NÃO atualiza aluno.objetivo/nivel_experiencia/dias_semana E duplica planos. Próxima sessão: fix completo anamnese (atualizar aluno + desativar planos antigos + 1 plano novo limpo). Backups locais preservados.

12/05/2026 - TARDE - FIX DEPLOYADO commit 1f3882c. POST /app-aluno/onboarding agora atualiza aluno.objetivo + aluno.nivel_experiencia + aluno.dias_semana antes de criar PlanoTreino. Bug do nivel_experiencia nao persistido = RESOLVIDO. Testado em producao: aluno Avancado/Hipertrofia/3x ve 'VOCE ESTA AQUI' na Fase 2 HIPERTROFIA (antes mostrava Fase 1 Adaptacao). Iniciante/Emagrecimento/5x ve Fase 1 ATIVACAO. Frontend leu nivel correto do banco end-to-end. PENDENCIA: desativar MULTIPLOS planos antigos (hoje so desativa o primeiro via .first() linha 127) - fica para commit separado. Proxima sessao: decidir unificacao PRO<->aluno (3 modelos Ondulatoria/Blocos/Mista vs hardcode de fases) OU seguir pente fino dos modais (postural, medidas, composicao, testes).

12/05/2026 - TARDE (planejamento) - Decisoes de produto registradas para proximas sessoes:
1. POSTURAL: bug real eh fotos sumirem do frontend ao sair da tela (nao eh falta de botao SALVAR como o BUG_POSTURAL_RESUMO de 10/05 sugeria - aquele doc esta desatualizado). Botao SALVAR ja foi feito. Fluxo OK: aluno tira fotos -> IA analisa -> recomenda corretivos -> corretivos vao pro treino do dia. Falta: fotos persistirem visualmente pra aluno ver evolucao postural ao longo do tempo (caso de uso: tirar fotos novas em 2 meses e comparar com as antigas). Solucao: GET endpoint que retorna fotos salvas + frontend ler ao abrir modal.
2. OVERTRAINING + REAVALIACAO: unificar gatilho BIMESTRAL (60 dias / 8 semanas). Mesmo email/notificacao dispara os 2 questionarios juntos. Mensal foi considerado 'chato pacas' pelo Andre - reduz drop-off e correlaciona dado de fadiga com janela de adaptacao muscular (6-12 semanas). Endpoint /reavaliacao ja existe em app_aluno.py com logica de 60 dias - precisa adicionar overtraining no mesmo gatilho.
3. UNIFICAR ENTRADA DO AVULSO PAGANTE AO MESMO QUESTIONARIO DO PRO (destrava Porta B da visao v2): hoje aluno avulso paga via Stripe -> recebe email 'bem-vindo a familia' -> entra no app PELADO (sem nome, sem treino, tela generica) -> sensacao 'paguei pra isso?'. Aluno do PRO ja funciona: personal clica botao verde 'Convidar Aluno (Questionario)' no PRO -> manda link via WhatsApp -> aluno preenche o questionario UNICO (Dados Pessoais + NF + Treino [objetivo/nivel/dias] + Anamnese + PAR-Q) -> ao final: 'ENVIAR E RECEBER MEU TREINO' -> app abre com nome + treino pronto. Esse MESMO questionario ja esta acessivel dentro do app aluno via card 'COMPLETE SEU CADASTRO' / botao 'ABRIR QUESTIONARIO'. Solucao para o avulso: pos-pagamento Stripe -> redirecionar direto pro questionario (com token gerado pelo endpoint /meu-link-onboarding commit 9d8bcf0 de 11/05) OU inserir link em destaque no email 'bem-vindo'. Resultado: um unico questionario serve 3 entradas (Porta A via PRO+WhatsApp, Porta B via pagamento avulso, Porta C via app aberto sem completar). DRY perfeito. Tempo: 30-45 min. Risco: BAIXO (conectar webhook Stripe a gerador de link ja existente, sem mexer em logica de pagamento).

13/05/2026 - TARDE - 3 commits deployados em sequencia:
1. c6f7d35 - fix(pagamento): remove import local 'enviar_email' dentro do webhook que sombreava o import global da linha 10. Causa do bug: UnboundLocalError em pagamento.py:694 toda vez que checkout.session.completed era processado. Stripe reentregava o mesmo evento por 3 dias (retry policy), e como email de boas-vindas (linha 667) era enviado ANTES do crash, aluno teste 'Final 04' recebia email diariamente. Fix: remover import local. Resultado esperado: emails diarios PARAM SOZINHOS depois do ultimo retry pendente do Stripe (max 24-72h).
2. 8c9c21f - feat(reavaliacao backend): GET /app-aluno/reavaliacao agora retorna 'overtraining_pendente' junto com 'precisa_reavaliar', ambos baseados em janela bimestral de 56 dias (8 semanas, alinhado com janela de adaptacao muscular Schoenfeld 2017). Helper interno overtraining_pendente_check() le observacoes JSON da ultima AvaliacaoFisica e extrai overtraining_data. Antes: reavaliacao 60 dias / overtraining 30 dias (separados). Agora: ambos 56 dias unificados.
3. 492abb6 - feat(reavaliacao frontend): banner 'PRONTO PARA EVOLUIR?' reescrito com copy cientifico forte + botao unico CTA (sem botao fechar X, alinhado com filosofia Andre 'reavaliacao nao eh opcional'). verificarReavaliacao() reescrita: consulta backend em vez de localStorage. Funcao iniciarReavaliacaoBimestral() handler do botao: le flags do dataset e abre modais na ordem certa (overtraining primeiro, reavaliacao depois). Banner mostra 2 itens explicados, frase ancora 'Sem esses dados seu treino fica preso na mesma fase', e citacoes ACSM 2022 + Schoenfeld 2017 + Meeusen 2013.
PENDENCIA conhecida (proxima sessao - 20 min): fecharQuestionarioOver() ler flag dataset.abrirReavaliacaoApos e abrir modal reavaliacao automaticamente quando aluno fecha overtraining. Hoje precisa clicar banner duas vezes se ambos pendentes.
CODIGO ZUMBI conservado (faxina futura - sessao dedicada): verificarOvertraining() ainda existe mas nao eh chamada. localStorage 'aurum_ultima_aval' e 'aurum_over_last' nao usados mais. 9 backups antigos do pagamento.py em routers/. Varios backups com sufixo .ANTES_*, .OLD_*, etc.

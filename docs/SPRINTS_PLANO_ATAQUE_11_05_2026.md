# Sprints - Plano de Ataque

Criado: 11/05/2026 tarde (apos almoco)
Definido por: Andre + Claude
Objetivo: Sistema pronto pra USO

## Ordem de Ataque Definida

Sequencia logica - cada sprint abre caminho pro proximo.

## SPRINT 1 - Link no App Aluno

Objetivo: Aluno cadastrado mas SEM questionario preenchido,
ao abrir o app, ver botao/banner pra completar via link.

Tarefas:
- Detectar se aluno nao preencheu anamnese basica
- Mostrar banner "Complete seu cadastro" no app
- Botao leva pro link de onboarding (mesmo do Personal)
- Opcao: tambem mandar por email automatico

Estimativa: 30-45 min

## SPRINT 2 - Salvar Anamnese (BUG FIXING)

Objetivo: Modal de anamnese no app aluno NAO vir mais vazio.

Tarefas:
- Garantir que /onboarding salva patologias/medicacoes
- Criar GET /app-aluno/anamnese (le do banco)
- Criar POST /app-aluno/anamnese (caso aluno EDITE algo)
- Frontend renderAnamnese chama GET e popula campos
- Testar end-to-end

Estimativa: 45-60 min

## SPRINT 3 - Salvar Fotos Posturais

Objetivo: Aluno fez postural, fechou app, voltou - modal mostra ultima analise.

Tarefas:
- Decidir: salvar fotos no banco (base64 ou S3)
- Criar GET /app-aluno/postural/atual
- Modal aluno detecta se ja tem analise
- Se tem: mostra read-only + opcao refazer
- Se nao tem: mostra fluxo atual

Estimativa: 60-90 min

## SPRINT 4 - Resto da Avaliacao

Objetivo: Medidas, composicao corporal aparecerem ao reabrir.

Tarefas:
- Modal Medidas le do banco ao abrir
- Modal Composicao le do banco ao abrir
- Testar persistencia

Estimativa: 45-60 min total

## SPRINT 5 - VO2 Redesign

Objetivo: Resolver "aluno se confunde com 3 testes + HRR separado"

Tarefas:
- Refazer UX da tela de Testes
- Cada protocolo com seu HRR DENTRO do card
- Indicacao clara: Cooper=adultos, Milha=idosos, Step=adolescentes
- Salvar protocolo escolhido junto com resultado

Estimativa: 1-2h

## SPRINT 6 - Salvar Todos os Testes

Objetivo: Testes fisicos persistem ao reabrir modal.

Tarefas:
- GET /app-aluno/testes-fisicos
- Modal le e popula campos
- VO2, HRR, Forca, Flexibilidade

Estimativa: 45 min

## Sprint Transversal - Auri Tutor

Implementar AO LONGO de todos sprints:

Auri como Tutor do App:
- "Como faco analise postural?"
- "Onde preencho minha saude?"
- "Como faco check-in?"
- "O que e HRR?"
- "Quando devo refazer avaliacao?"

Auri Orientador de Video Postural:
- Aluno: "como tiro foto?"
- Auri: "video 5s em cada pose + print do video"

Auri Recomendador de Protocolo:
- Aluno: "qual teste fazer?"
- Auri analisa idade e responde adequado

Estimativa: 30 min por sprint (acumulado: 2-3h)

## Estimativa Total

- Sprint 1: 30-45 min
- Sprint 2: 45-60 min
- Sprint 3: 60-90 min
- Sprint 4: 45-60 min
- Sprint 5: 1-2h
- Sprint 6: 45 min
- Auri transversal: 2-3h acumulado
- TOTAL: 7-12h (3-5 sessoes)

## Quando Onboardar Aluno Real

DEPOIS de Sprint 2 (Anamnese resolvida).
Resto pode ser feito com aluno usando o sistema.

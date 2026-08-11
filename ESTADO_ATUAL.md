# ESTADO ATUAL — AurumSci (10 jul 2026)

## FEITO HOJE

### STRIPE CONNECT — PROVADO E APROVADO
- Passos 1-2 no ar E VALIDADOS. Conta Express criada (retornou URL de onboarding).
- Email oficial da Stripe: "AurumSci aprovada para criar contas e cobrancas em producao".
- FIX chave: no BR, `transfers` exige `card_payments` junto. Adicionado em pagamento.py.
- Cadeados abertos no painel: Marketplace, identidade (KYC), responsabilidades, perfil plataforma.
- NAO clicar em "criar conta conectada" pelo painel (fica orfa). Nossa rota salva no banco.
- FALTA (so quando for vender PRO): Passo 3 webhook account.updated, Passo 4 botao "Ativar
  recebimentos", Passo 5 checkout aluno com split, Passo 6 virada gradual.
- Onboarding do Andre-personal: link gerado mas NAO aberto (pediria dados bancarios). Guardado.

### TREINO DO ALUNO — CARD DE PRESCRICAO (bug arquitetural corrigido)
- BUG: prescricao (fase) nao batia com reps do exercicio. 4 fontes de reps que nao conversavam.
- FIX aditivo: card de prescricao no topo puxa da fase (series, reps, %1RM, descanso, ref).
- Prescricao hipertrofia (CREF Andre): ADAPTACAO 2x15-20 35-50% 90s | HIPERTROFIA 3-5x8-12
  75-85% 60-90s | FORCA 3-4x2-6 80-95% 180s | DELOAD 2-3x15 50% 90s.
- INTENSIFICACAO renomeada FORCA. Cor dourada (nao vermelho). %1RM validado ACSM 2026.
- Tela de Periodizacao alinhada com o card (mesmos numeros).
- Removido: reps/series por exercicio + bolinhas 1-2-3 (feature fantasma, timer so no toque).
- 1RM no lugar do emoji alvo. Layout horizontal. Feedback +% (bracinho) / -% (carinha duvida).

### CRONOMETRO / TIMER (unico, no rodape do treino)
- Duas abas: CRONOMETRO (sobe) / TIMER (desce+apita+vibra). Dropdown de tempos.
- Timer pre-seleciona o descanso da fase. Escolha persiste no treino todo.
- Visor 76px, cor branca (var--texto, adapta ao tema), banner translucido dourado.

### PRO — PROFESSOR SO JOGA O EXERCICIO
- Escondido grid series/reps/descanso no form de montar treino (display:none).
- Professor adiciona exercicio -> so ve nome + carga + 1RM + video. 1 clique vs 4.
- Series/reps salvos com DEFAULT hipertrofia (3x10-12) no banco. Decisao Andre (Opcao A):
  o que importa e o aluno VER a fase certa (card) e por a CARGA dele. Volume varia pela carga.

## MAPA: onde o volume/score e calculado
- BACKEND. app_aluno.py:1020 chama calcular_volume_plano (treino.py).
- Le do banco ExercicioSessao: carga_kg x series x repeticoes. CONGELA em volume_inicial_kg.
- series/reps = default hipertrofia (escondido). carga = aluno poe. Consistente, varia pela carga.

## BUGS CONCEITUAIS ABERTOS (achados usando o produto)
1. [CORRIGIDO] Prescricao nao batia com a fase.
2. [ABERTO] "Nao existe treino que emagrece" — emagrecimento e deficit calorico, nao treino.
   BLOCOS_CONFIG tem fase de emagrecimento cientificamente fraca. Repensar ou remover.
3. [ABERTO] TREINO REPETE POR MESES. get_exercicios_grupo(grupo, nivel) e 100% deterministico
   (sem random, sem ciclo, sem semana). Intermediario1 (6m-1ano) recebe MESMO treino o tempo
   todo. Reavaliacao aos 56 dias regenera igual. Aluno estagna.

## PROXIMO GRANDE: TREINO ROTATIVO (o "randomizado") — MERECE CROSS-CHECK
Arquitetura desenhada por Andre (nao random puro, e RECEITA + rotacao):
- Cada exercicio ganha tags: grupo + tipo (multiarticular / monoarticular).
- Sessao define RECEITA. Ex PEITO: 3 multi + 2 mono. OMBRO: 2 multi + 1 mono. TRICEPS: 1+1.
- Sistema busca no banco exercicios que atendem a receita, VARIANDO a cada ciclo/reavaliacao.
  Ex: ciclo1 supino reto + crucifixo halteres; ciclo2 supino inclinado + peck deck; etc.
- Muda pegada, angulo, cabo vs livre. Preserva estrutura, varia estimulo (cientifico).
- Ombro sempre no cabo (mais seguro, articulacao vulneravel): elevacao lateral/frontal,
  remada alta, crucifixo invertido, face pull — todos no cabo.
CUSTO: taguear 229 exercicios, reorganizar catalogo (hoje por nivel), enriquecer banco,
criar seletor de receita, guardar ciclo do aluno. Cascade PRO/Aluno. 11 alunos com treino.
=> FAZER FRESCO, com cross-check ChatGPT+Gemini (igual foi o Connect que deu certo).

## OUTRAS PENDENCIAS
- Backend prescrever series/reps pela fase (justica no volume) — Andre decidiu Opcao A por ora.
- Ombro no cabo (enriquecer catalogo).
- Landing: medindo conversao. Base 1709 visitas / 0 no ultimo mes. Ver em 2-3 semanas.
- Botao "ajustar" no treino do aluno: testar se carga salva sozinha (onchange) -> se sim, tirar.

## REGRAS DE OURO
Railway only. Backup antes. Uma coisa por vez. Investigar e PROVAR antes de mexer.
Chave nunca no chat. Cross-check nas decisoes grandes. Commit 1 de cada vez.
Zero imagem de IA representando trabalho real. PRO/Aluno compartilham render (cascade).

## PRECO RECORRENTE - EVOLUCAO DA IDEIA (Andre, jul/2026)
Andre quer subir recorrente de 49,90 -> 89,90 (passou por 79,90).
Argumento: barato demais nao valoriza, produto vale mais (motor variacao + periodizacao + CREF 20 anos).
PONTO CERTO no principio (preco comunica valor). MAS validar antes de cravar:
- Testar com 2-3 alunos reais ("quanto pagaria?").
- Garantir que landing/produto COMUNICA o valor (senao 89,90 assusta).
- Preco e experimento, nao chute. Lancar e observar; ajustar se travar.
Tudo Stripe WEB (foge comissao Apple). iOS/IAP adiado (Andre quase desistindo do iOS kkk mas vai rolar).

## PROXIMAS TAREFAS (jogadas pra depois - jul/2026)
FEITO HOJE (no ar): motor variacao ligado, 6 grupos enriquecidos (triceps/biceps/peito/costas/ombro/perna), bug extra aluno resolvido (localStorage).
PENDENTE (retomar com cabeca fresca):
1. TESTAR na tela os 6 grupos com aluno real (criar aluno, gerar, reavaliar, ver variar).
2. Grupos nao enriquecidos: abdomen(4), gluteo isolado (foco mulherada, projeto a parte), funcional, corretivos.
3. Revisar acentos em OUTRAS telas do app (nao so ajuda).
4. PROXIMO PROJETO grande: AurumSci Results + planos (3/6/12 meses trimestral recorrente Stripe web) - construir SEPARADO/desacoplado (entranhas do app atual amarradas). Validar preco 79,90 com alunos reais.
5. Stripe Connect passos 3-6 (quando vender PRO).
6. iOS/IAP (adiado - Andre quase desistindo kkk mas vai rolar).

## MOTOR v2 - EQUILIBRIO COM ABDOMEN (Andre, jul/2026)
Em vez de lombar (nao existe no motor), usar ABDOMEN (existe) pra equilibrar dias.
Ex: ABC dia B = Costas + Biceps + Abdomen (equilibra numero de exercicios com dia A).
Motivo: cara ver equilibrio entre os dias (nao um dia cheio e outro vazio).

## INSIGHT ARQUITETURAL CHAVE (Andre, jul/2026) - REPENSAR O MOTOR
Andre concluiu (investigando): o motor atual e MONO/LINEAR - "nao cabe manobras".
Foi construido pra caminho fixo: frequencia -> divisao automatica -> N por grupo -> fim.
NAO suporta as VARIAVEIS que o conhecimento CREF exige:
- Ordem cientifica (multi->mono, maior->menor)
- Pre-exaustao (inverte ordem)
- Metodos (agonista/antagonista, drop, bi-set, tri-set, rest-pause por fase)
- Piso/teto de volume por dia
- Equilibrio entre dias
- Selecao inteligente de exercicios

CONCLUSAO ANDRE: "temos o conhecimento mas ficamos limitados no sistema. Pra competir
precisamos fazer melhor." O motor precisa ser REPENSADO desde a fundacao pra ter
FLEXIBILIDADE/liberdade. Mesmo problema das "entranhas amarradas" do app atual.

ISSO E O PROJETO MAIS SERIO: coracao do produto, afeta todos alunos, exige arquitetura
pensada (nao improviso), CREF estruturado, cross-check. NAO fazer no cansaco.
Sistema atual FUNCIONA e segura os alunos ate o motor v2 ser desenhado direito.
PROXIMO PASSO: sessao dedicada SO pra desenhar a arquitetura do motor flexivel v2.

## AGENTES - RESPOSTA (jul/2026)
(A) Agente pra CONSTRUIR = Claude Code. Roda no terminal, coda junto (backup/edita/testa
    sozinho, sem copiar-colar comando). PAGO: Pro $20/mes (~R$110), Max $100-200/mes.
    Sem plano gratuito. Usuario medio ~$6/dia. Indicado PRA construir o motor/app v2.
    Comecar no Pro, subir pra Max so se precisar.
(B) Agente DENTRO do app = IA que monta treino como personal (AURI evoluido, "cerebro
    do treino"). NAO e assinatura - e CONSTRUCAO via API Anthropic (paga por token).
    E o coracao do app aluno v2.
INDICACAO: (A) ajuda a construir o v2 (acelera muito, Andre cansado de copiar-colar).
(B) e parte do proprio v2. Decidir na hora de comecar o v2 - nao precisa agora.
ORDEM (Andre definiu): estabilizar atual -> terminar Lab -> descansar -> desenhar v2.

═══════════════════════════════════════════════════════════
## SESSAO 14/jul/2026 - FECHAMENTO (fizemos MUITA coisa)
═══════════════════════════════════════════════════════════

### VITORIAS NO AR HOJE (commitadas):
1. ORDEM CIENTIFICA multi->mono (4f3e94e): multiarticular primeiro (base), mono depois
   (isolador). Palavras-chave PALAVRAS_MULTI + excecoes CREF (panturrilha, punho,
   pull down = mono). Crossover = multi (Andre: pega peito+ombro+triceps).
2. BUG MONSTRO DO NIVEL (e2f53da): o sistema NAO reconhecia "intermediario"/"avancado"
   (sem numero) -> caiam em "iniciante" (default). TODOS os alunos inter/avancado
   treinavam como INICIANTE! Fix: NIVEL_ALIAS ganhou "intermediario"->intermediario2,
   "avancado"->avancado3. Descoberto por pergunta simples do Andre "como o sistema
   identifica o nivel?". Explica pq treinos vinham sempre basicos (Peck Deck/Crucifixo).
3. GLUTEO E PANTURRILHA separados (e2f53da): grupos novos no motor, mesmos nomes do PRO.
   Panturrilha (7 ex, movidos de pernas). Gluteo (12 ex, criados: Abducao no Cabo,
   Gluteo caneleira, Elevacao Pelvica fit ball, Gluteo cabo, Hip Thrust, Kickback,
   Agachamento Sumo, Flexao joelhos fit ball, Elevacao pelve barra).
4. DIVISOES completas (8b9b863): ABC/Agonista/ABCDE/PPL com perna+gluteo+panturrilha.
   ABC: A=peito/ombro/triceps, B=costas/biceps/ABS, C=pernas/gluteo/panturrilha.
   Full Body deixado com 7 grupos (nao separou gluteo/pant pra nao virar 9=grande).

### DECISAO DE NIVEIS (Andre CREF):
3 niveis so (iniciante/intermediario/avancado). "Avancado 1 do 3 difere carga e qualidade
de movimento, entao avancado e avancado". Sub-niveis (1/2/3) continuam no dicionario mas
o alias resolve: intermediario pega ate inter2, avancado pega tudo. Intensidade vem da FASE.

### PENDENTE PRA AMANHA/PROXIMO:
1. TESTAR NA TELA com aluno avancado (dia C vem gluteo+panturrilha? multi primeiro?).
2. FUNCIONAL: forca_especial (Deadlift/Squat/Barra Fixa) -> virar grupo "Funcional"
   (alinhar com PRO que tem Funcional). Onde entra nas divisoes?
3. Refinamento fino: ordem ENTRE os multi (Supino base antes de Crossover).
4. STRIPE (foco do Andre): esqueleto em ESQUELETO_STRIPE_CONNECT.md. 3 frentes -
   (A) Connect aluno->personal (parou em decidir chave live vs sandbox),
   (B) planos periodizacao 3/6/12 meses recorrente, (C) assinatura PRO via web.
   Decidir QUAL frente primeiro.

### DECISAO DE NEGOCIO PENDENTE (importante):
App do aluno vai vender pra ALUNO AVULSO (sem personal)?
- Aluno COM personal: personal adiciona extra pelo PRO -> banco. Extra localStorage ok
  (aluno treina com celular, caso comum resolvido).
- Aluno AVULSO: depende dos proprios extras. localStorage fragil (perde se troca aparelho).
  Se vender pra avulso -> extras precisam salvar no BANCO + mais autonomia (quase outro produto).
Isso define se vale resolver "extra salvar na web". Decidir o modelo de venda primeiro.

### COMMITS HOJE: 4bb7528, 4f3e94e, e2f53da, 8b9b863

## CROSS-CHECK CHATGPT + VEREDITO DAS 3 CABECAS (jul/2026)
ChatGPT ACRESCENTOU (3o nivel que Claude e Gemini nao viram):
- Mesmo COM assinatura, Subscription.modify() troca plano ANTES de garantir pagamento.
  SOLUCAO: payment_behavior="pending_if_incomplete" + proration_behavior="always_invoice".
  Upgrade so vale SE pagamento passar. Endpoint marca plano_pendente, webhook confirma.
- Nunca aceitar plano/price_id/valor vindo do app (usuario manipula). Mapear PRICE_TO_PLAN
  interno; webhook le o price_id REAL do Stripe.
- Idempotencia: salvar event.id, nao processar 2x.
- billing_mode explicito (stripe/courtesy/trial/free) - nunca deduzir cortesia por
  subscription_id vazio.
- Checar status: active/trialing OK; incomplete/past_due/unpaid/canceled = barra.
- Downgrade: decidir se imediato ou fim do periodo (fim e mais simples).

REGRA DE OURO (3 cabecas concordam): o ENDPOINT so SOLICITA. Quem LIBERA o plano e o
WEBHOOK, apos Stripe confirmar pagamento. Banco nunca muda plano sozinho.

ARQUITETURA FINAL:
Usuario pede -> backend valida price_id -> sem assinatura=Checkout(client_reference_id) /
com assinatura=modify(pending_if_incomplete)+plano_pendente -> Stripe cobra ->
WEBHOOK confirma -> SO ai banco muda plano + libera limite alunos.

TESTAR antes de vender: upgrade aprovado, cartao recusado, 3DS, sem assinatura,
downgrade, cancelamento, webhook repetido.

PROJETO DEDICADO (codigo de dinheiro, cabeca fresca). Venda PRO pausada = sem pressa.
Passos: (1) webhook secret + endpoint /webhook/stripe, (2) mapear PRICE_TO_PLAN,
(3) corrigir mudar-plano (so solicita), (4) checkout p/ sem assinatura, (5) validar
limite alunos no backend, (6) idempotencia, (7) testar os 7 cenarios.

## DIAGNOSTICO COMPLETO DO FUNIL DO ALUNO (Andre testou na pele, jul/2026)
Andre testou o cadastro real pelo celular e achou 3 problemas:

1. FUNIL QUEBRADO: cadastro.html faz 2 chamadas (1. /aluno-portal/cadastro cria o
   aluno no banco, 2. /pagamento/criar-sessao gera checkout). Se o cara sai no meio
   (ex: foi pegar o cartao no banco - comportamento comum!), o cadastro fica orfao e
   na volta leva "Email ja cadastrado" = beco sem saida. + erro JS cru vazando na
   tela ("undefined is not an object r.json") = mata confianca.
   FIX: retomada - email existe + SEM assinatura ativa -> devolve aluno_id e segue
   pro checkout (nao barra). So barra assinante ativo ("faca login").
   + tratamento de erro decente no front.

2. TRIAL ETERNO GRATIS (O MAIS GRAVE): models/__init__.py linha 42/76:
   assinatura_status = Column(String(20), default="trial")
   Todo cadastro NASCE em 'trial' no banco (Stripe nem sabe). Porteira do login
   (portal_aluno.py linha 143) aceita 'trial'. Trial NAO tem data. Quem abandona o
   checkout nunca cria subscription -> nenhum webhook chega -> 'trial' PRA SEMPRE.
   Cadastrou + fechou aba = app gratis eterno. Andre confirmou na pele (acesso dele
   atual e esse buraco, nao trial legitimo).
   FIX (com a blindagem 3 cabecas): (a) trial ganha DATA (trial_expira_em) OU so
   existe trial via Stripe (trial_period_days no checkout); (b) porteira valida
   data/status confirmado; (c) webhook muda status em payment_failed/deleted.

3. Webhook EXISTE (pagamento.py 616, com construct_event + secret ✅) mas trata
   checkout.session.completed/cobranca avulsa - conferir se trata subscription
   events (payment_failed, deleted) para o pos-trial.

VER SE TEM GENTE USANDO GRATIS: Railway Postgres -> tabela alunos -> avulsos
(personal_id NULL) com stripe_subscription_id vazio = nunca pagaram.
TUDO entra no projeto da blindagem Stripe (3 cabecas) - agora com escopo ampliado:
PRO (mudar-plano) + funil aluno (retomada) + trial eterno (enforcement).

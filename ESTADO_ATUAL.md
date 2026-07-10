# ESQUELETO - ONDE ESTAMOS (08 jul 2026)

## FEITO HOJE: LANDING TRANSFORMADA
Diagnostico (Andre): 1709 visitas no ultimo mes, ZERO fechamento.
Causa provada: (1) landing nao mostrava o app; (2) pede cartao no cadastro.

Corrigido (tudo real, zero IA, zero risco):
- Galeria com 5 telas do app (treino, avaliacao, periodizacao, resultados, AURI)
- Legendas que vendem em cada print
- Botao: COMECAR 7 DIAS GRATIS (era 'Comecar agora', vago)
- Removido 'Beta Tester' do depoimento (assustava)
- Tema ESCURO (mesmas cores do app) - consistencia landing/cadastro/app
- Foto real do Andre (camiseta AurumSci), redonda, borda dourada
- Tudo nos 3 idiomas (PT/EN/ES)
Arquivos: static/landing.html + static/app-*.png + static/andre-foto.jpg

## AGORA: MEDIR (nao construir nada)
Decisao do Andre (sabia): mantem o CARTAO no cadastro por enquanto.
Motivos: (a) testar UMA variavel por vez; (b) mexer no pagamento afeta a APPLE (IAP).
Base de comparacao: 1709 visitas / 0 conversao.
Medir 2-3 semanas. Cenarios:
- Converteu 5+ -> a landing era o problema. Otimiza e segue.
- Converteu 1-3 -> melhorou, cartao ainda pesa. Vale o trial.
- Continua ZERO -> o cartao E o vilao, comprovado. Constroi o trial com certeza.

## TRIAL SEM CARTAO (plano pronto, so construir SE o dado pedir)
INVESTIGACAO JA FEITA (nao repetir):
- cpf no Aluno JA e unique=True -> banco ja bloqueia conta duplicada. Defesa contra abuso OK.
- assinatura_status ja existe (default trial).
- get_aluno_logado em app/routers/portal_aluno.py linha 81 -> PONTO UNICO de controle.
  Todas as rotas do aluno usam Depends(get_aluno_logado). Um porteiro protege tudo.
- Checkout Stripe ja existe e funciona (/pagamento/criar-sessao).
- Tela paywall_aluno.html ja existe (pode reusar).
- NAO existe: datas de trial no Aluno; NENHUMA checagem de trial no app_aluno.py.

CONSTRUIR (4 pecas, so se precisar):
1. Migration: trial_inicio + trial_fim no Aluno (padrao ALTER TABLE do main.py)
2. Cadastro: grava as datas, NAO chama Stripe
3. Porteiro dentro de get_aluno_logado: se trial acabou E nao pagou -> HTTP 402
4. Frontend: recebe 402 -> tela 'trial acabou, assine' -> botao vai pro Stripe

CUIDADO CRITICO: alunos ATUAIS nao tem trial_inicio. Porteiro burro bloqueia todo mundo.
Tratar: se trial_inicio for null, considerar ativo (grandfathering).
CUIDADO 2: mexer no fluxo de pagamento afeta a Apple (Guideline 3.1.1 IAP). Rever la.

## AMANHA (prioridades do Andre)
1. DUNS - verificar se saiu (email + site Dun & Bradstreet).
   Se saiu: usar no Apple Developer (vira conta de organizacao).
   Se nao saiu: mandar email pra Apple de novo.
2. STRIPE CONNECT - retomar. Passos 1-2 no ar (campos no banco + rotas de onboarding).
   Travou na config do painel Stripe (decidir chave live vs test).
   Falta: Passo 3 webhook, 4 botao ativar recebimentos, 5 checkout com split, 6 virada gradual.

## IDEIA GUARDADA (nao construir agora)
SITE-HUB do ecossistema (Ciencia da Hipertrofia + PRO + Aluno + Lab + Training).
Parecer do socio: a ideia e boa, MAS hoje o funil nao converte (1709 visitas, 0 fechamento).
Construir vitrine maior pra funil que nao converte = multiplica o problema.
Ordem certa: 1o fazer UM produto converter -> 2o escalar com o hub.
Ja ha 4 frentes abertas (Connect, DUNS/Apple, Lab, trial). Hub seria a 5a.

AURUMSCI TRAINING (futuro): app so de treino, cronometro integrado, correcao de postura
com tracos, quilagem/series/modelos com referencia cientifica. Norte de venda: 'existe
ciencia por tras do treino'. Construir depois que Connect + Lab estiverem de pe.

## REGRAS DE OURO
Railway only. Backup antes. Uma coisa por vez. Investigar e PROVAR antes de mexer.
Chave nunca no chat. Cross-check com as IAs em decisoes grandes. Commit 1 de cada vez.
Zero imagem de IA representando trabalho real (regra: ter algo ruim e pior que nada).

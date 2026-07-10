# ESQUELETO STRIPE CONNECT - ONDE PARAMOS (25 jun 2026, noite)
(EXECUTAR FRESCO. Painel do Stripe e chato de proposito - mexe com dinheiro. Calma + doc aberta.)

## ARQUITETURA VALIDADA PELAS 3 CABECAS (nao rediscutir)
- Connect EXPRESS (Stripe cuida do KYC/onboarding do personal)
- Modelo MARKETPLACE = destination charges (eu recebo do aluno e repasso ao personal)
- Split: subscription_data com application_fee_percent 10 + transfer_data destination
- Aluno so assina se personal tem: stripe_account_id E charges_enabled E payouts_enabled
- FISCAL: eu emito NF so dos 10% (taxa); personal emite NF dos 100% pro aluno dele
- Repasse cartao ~30 dias no BR; Pix na hora
- FUTURO: termos de uso deixando AurumSci como intermediador

## JA FEITO (no ar, commitado)
- PASSO 1: 4 campos no model Personal (stripe_account_id, onboarding_completed,
  charges_enabled, payouts_enabled) + migrations no main.py. Commit feito.
- PASSO 2: rotas /pagamento/connect/criar (cria conta Express + link onboarding)
  e /pagamento/connect/status (le e atualiza flags). Commit feito.
- Backups: main.py, models, pagamento.py com timestamp.

## ONDE TRAVOU (retomar aqui)
- Config do painel Stripe e confusa. Tem 2 ambientes: PRODUCAO (live, sk_live, ja recebe
  meu plano R,90) e AREA RESTRITA (teste/sandbox, sk_test, dados fake tipo Randy Gonzales).
- App usa sk_live hoje. Pra testar Connect precisa decidir: testar em live (mais simples,
  nao recebo de aluno ainda = sem risco) OU sandbox (mais seguro, exige sk_test no Railway).
- Na area restrita apareceu 'representante vencido' = dado fake do teste, ignorar.
- IMPORTANTE: nunca printar/colar chave de API. Vai direto Stripe -> Railway.

## PROXIMOS PASSOS (fresco)
- Decidir chave (live vs test) e ativar Connect no modo certo.
- PASSO 3: webhook account.updated (saber quando conta do personal foi aprovada).
- PASSO 4: botao 'Ativar recebimentos' no painel do personal (chama /connect/criar).
- PASSO 5: checkout do aluno com split (application_fee + transfer_data). TESTAR com cuidado.
- PASSO 6: virada gradual (novos personais primeiro).

## CONTEXTO IMPORTANTE
- Eu (Andre) pago meu proprio plano PRO (bronze->prata). Esse fluxo (criar-sessao-personal)
  esta CERTO, NAO mexer. Connect e SO pro checkout do ALUNO (criar-sessao).
- Nenhum aluno paga via Stripe ainda (cobro manual ate 2o mes). Janela segura pra testar.

## REGRAS DE OURO
Railway only. Backup antes. Uma coisa por vez. Investigar e provar antes. Chave nunca no chat.
Cross-check ChatGPT+Gemini ja feito pra arquitetura. Commit 1 de cada vez.

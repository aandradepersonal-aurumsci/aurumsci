# PROJETO: MOTOR DE VARIACAO PERIODIZADA (o "treino que nao repete")

## O PROBLEMA (achado por Andre usando o produto)
get_exercicios_grupo(grupo, nivel) e 100% deterministico. Aluno intermediario fica
6 meses a 1 ano no mesmo nivel = MESMO treino sempre. Reavaliacao aos 56 dias regenera
igual. Aluno estagna. App promete "ciencia que vira resultado" mas repete ficha.

## FRASE-REGRA (ChatGPT, adotada)
"O Auro MANTEM o que precisa evoluir, MODIFICA o que pode variar e EXCLUI o que nao e
adequado ao aluno." -> Nome: MOTOR DE VARIACAO PERIODIZADA (nao "randomizador").

## ARQUITETURA VALIDADA POR 3 IAs (Gemini + ChatGPT + Claude)

### Os 3 niveis de exercicio (ChatGPT)
1. ANCORA: principais (supino, agacho, terra, remada, puxada, desenvolvimento).
   Ficam estaveis 6-10 semanas. Medem progressao. Preservam aprendizado motor.
2. SEMIANCORADO: mesmo padrao, muda equipamento (supino barra->halter->maquina).
3. ROTATIVO: acessorios/monoarticulares. Variam livre (crucifixo->crossover->peck).

### Regra de renovacao (ChatGPT)
Manter 40-60% do treino anterior, renovar 40-60%. Aluno percebe novo, sistema mede evolucao.
Modos: LEVE (25-35%), MODERADA (40-60%, padrao intermediario), AMPLA (65-80%, mudou
objetivo/equipamento/restricao/estagnou). Sempre preservar >=1 ancora.

### "Nao sorteia NOMES, sorteia PADROES" (ChatGPT)
Cada exercicio tem caracteristicas. O motor troca mantendo a FUNCAO.

### Especificidade neural (Gemini) - o pulo do gato
Se muda 100% supino barra->halter, perde eficiencia de forca na barra. Rotar acessorios
livre, ancoras estaveis (variar so pegada/angulo). Nao resetar aprendizado motor.

### Matriz de VAGAS (ChatGPT) - estrutura fisiologica fixa
Superiores: 1 empurrar horizontal + 1 puxar horizontal + 1 empurrar vertical +
1 puxar vertical + 1 acessorio peito/delt + 1 biceps + 1 triceps.
Inferiores: 1 dominante joelho + 1 dominante quadril + 1 unilateral + 1 flexao joelho +
1 extensao joelho + 1 panturrilha + 1 core.
O motor preenche as vagas com exercicios elegiveis. Estrutura sempre coerente.

### Sistema de PONTUACAO (ChatGPT) - nao random.choice()
+30 mesmo padrao movimento | +20 compativel objetivo | +15 equipamento disponivel |
+15 nao usado ultimos 2 ciclos | +10 nivel adequado | +10 preferencia aluno |
-40 causou desconforto | -30 repetido recente | -20 muito parecido com outro do treino |
-20 incompativel restricao | -10 habilidade nao dominada.
Escolhe entre os 3-5 mais bem pontuados. Variedade sem loteria.

### Regras de seguranca (ChatGPT)
Nunca: 2 exercicios identicos no mesmo treino; trocar todos os compostos juntos;
exercicio incompativel com lesao; equipamento que a academia nao tem; repetir acessorio
do ciclo anterior; mudar exercicio+volume+intensidade+tecnica tudo junto; treino sem
padrao principal; grupo sem cobertura.

### Versionamento (ChatGPT) - NUNCA sobrescrever
Treino v1, v2, v3... Permite comparar evolucao, reverter, ver usados, relatorio.

## MODELO DE DADOS (ChatGPT - Postgres/SQLAlchemy)
Tags por exercicio: grupo_muscular, padrao_movimento, tipo (multi/mono), equipamento
(barra/halter/cabo/maquina), pegada (pronada/supinada/neutra), angulo, unilateral,
nivel_minimo, funcao_programa (ancora/semi/rotativo), impacto_articular, restricoes.
Tabelas: exercicios | restricoes_exercicio | treinos_aluno (com versao) |
treino_exercicios (papel, series, reps_min/max, rir, descanso) | historico_exercicios_aluno.

## DIAGNOSTICO DO BANCO ATUAL
- Exercicios estao HARDCODED em periodizacao.py (dicionario EXERCICIOS por grupo->nivel).
- 242 ocorrencias, mas ~85 nomes unicos, e DESSES uns ~20 sao nomes de DIVISAO (nao
  exercicios): "Full Body A", "Push Pull Legs 2x", "A-Peito", etc. -> ~65 exercicios reais.
- MAGRO em varios padroes: biceps so 4 (falta scott/cabo/inclinada/21), triceps so 4
  (falta corda/unilateral/coice/paralela). Pra rotacao (regra 40-60%) precisa 6-8 por padrao.
- Repetidos entre niveis NAO sao bug: mesmo exercicio tem series/reps diferentes por nivel.
  Some quando exercicio for separado da prescricao (a fase ja prescreve - feito no card!).

## FASEAMENTO SEGURO (uma fase por sessao, com cross-check e teste)
FASE 1: criar tabela `exercicios` no Postgres + migrar os ~65 reais (com tags). App ainda
        usa o dicionario. Depois disso, ADICIONAR exercicio = 1 INSERT (nao mexer no codigo).
FASE 2: ENRIQUECER o catalogo direto no banco (dobrar os magros). CREF Andre classifica.
FASE 3: motor de variacao (pontuacao + vagas + matriz). Testar com 1 aluno.
FASE 4: versionamento (v1/v2/v3) + fluxo professor aprova rascunho.
FASE 5: migrar os 11 alunos (importar treino atual como v1, professor revisa/aprova).
        Correcao do professor vira DADO (motor aprende as decisoes).

## CUIDADOS
- 11 alunos ativos com treino salvo. Nao migrar tudo automatico. Professor no loop.
- Cascade PRO/Aluno (render compartilhado).
- ACSM 2026: consistencia + adesao + individualizacao > complexidade. Nao mudar por mudar.
- Ombro sempre no cabo (Andre): elevacao lateral/frontal, remada alta, crucifixo invertido,
  face pull. Articulacao vulneravel.

## DECISAO
Projeto GRANDE (semanas). Reescreve o coracao do treino. Comecar pela FASE 1 (fundacao),
fresco, com backup e teste. NAO enriquecer no dicionario velho (vira lixo na migracao).

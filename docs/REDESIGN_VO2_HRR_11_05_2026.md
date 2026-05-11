# 💎 REDESIGN VO2/HRR — Ideia de André (11/05/2026)

## Problema atual
Tela mostra 3 testes (Cooper, Milha, Step) + HRR órfão embaixo.
Aluno fica confuso: "preciso fazer todos? qual escolher?"
Personal também fica confuso.
HRR não salva isolado (bug técnico).

## Riscos clínicos
- Idoso tentando Cooper (12min correndo) = risco cardiovascular
- Adolescente fazendo caminhada de 1 milha = sem estímulo real
- Step-up não é ideal pra adultos ativos
- Sem orientação por PERFIL = aluno escolhe errado

## Solução proposta (André, 20 anos personal)
1. Card único por protocolo selecionado
2. HRR DENTRO de cada card (logo após o teste)
3. Indicação clara: "Cooper = adultos ativos", "Milha = idosos", "Step = adolescentes"
4. Sistema escolhe automático baseado em idade/anamnese? (futuro)
5. Salva: VO2 + HRR + protocolo + perfil = avaliação completa

## Base científica
- Cole et al. (1999) NEJM — HRR como marcador cardíaco
- Cooper (1968) — protocolo 12 min
- Rockport (1986) — teste da milha caminhada
- YMCA — step test 3 min

## Prioridade
🟡 MÉDIA — depois de anamnese resolver. UX/clínico importante mas não bloqueador imediato.

## Estimativa
~1-2h trabalho (redesign tela + backend HRR vinculado a cada protocolo)

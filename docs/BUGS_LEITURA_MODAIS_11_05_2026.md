# 🐛 BUGS DE LEITURA NOS MODAIS — Mapeado 11/05/2026

## Padrão identificado
Backend SALVA corretamente no PostgreSQL.
Frontend NÃO LÊ ao reabrir modais de edição.
Aluno acha que perdeu dados (mas estão no banco).

## Prova
- Tela "MEUS RESULTADOS" mostra: peso 91kg, %gordura 24, massa 69.16
- Modais de edição abrem VAZIOS mesmo com dados salvos

## Bugs por feature

### 🔴 ANAMNESE (foco hoje)
- POST /app-aluno/anamnese: NÃO EXISTE no backend
- GET /app-aluno/anamnese: NÃO EXISTE no backend
- Frontend chama em linhas 1755, 3392, 3466 de app_aluno.html
- Status: ATACANDO HOJE

### 🟡 POSTURAL (foco hoje)
- POST /app-aluno/postural/salvar: FUNCIONA (criado 10/05)
- GET /app-aluno/postural/atual: NÃO EXISTE
- Modal reabre sem fotos nem desvios
- Status: ATACANDO HOJE

### 🟢 MEDIDAS / CIRCUNFERÊNCIAS (próxima sessão)
- POST /app-aluno/medidas: EXISTE (linha 673)
- GET /app-aluno/medidas: EXISTE (linha 701)
- Mas frontend não preenche modal ao abrir
- Status: AGUARDAR

### 🟢 COMPOSIÇÃO / BIOIMPEDÂNCIA (próxima sessão)
- POST /app-aluno/bioimpedancia: EXISTE (linha 208)
- GET equivalente: investigar se existe
- Modal reabre vazio
- Status: AGUARDAR

### 🟢 TESTES FÍSICOS / VO2 / HRR (próxima sessão)
- Salva no banco mas modal reabre vazio
- Endpoint GET de leitura: investigar
- Bonus: REDESIGN VO2 (doc REDESIGN_VO2_HRR_11_05_2026.md)
- Status: AGUARDAR

## Prioridade
🔴 ANAMNESE (saúde, PAR-Q legal) — HOJE
🟡 POSTURAL (UX, corretivos) — HOJE
🟢 RESTO — próximas sessões 1 por vez

## Estratégia
Pente fino com qualidade. Um por vez. Sem pressa.

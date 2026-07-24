# ia_chatbot.py - AurumSci AURI
import anthropic
import asyncio

import os
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def montar_contexto(aluno: dict, avaliacoes: list = [], treino: dict = {}, anamnese: dict = {}, presencas: dict = {}) -> str:
    ctx = f"Aluno: {aluno.get('nome', 'Aluno')}\n"
    ctx += f"Objetivo: {aluno.get('objetivo', 'hipertrofia')}\n"
    ctx += f"Nível: {aluno.get('nivel', 'iniciante')}\n"
    if avaliacoes:
        a = avaliacoes[0]
        ctx += f"Última avaliação: peso {a.get('peso')}kg, gordura {a.get('percentual_gordura')}%\n"
    if treino:
        ctx += f"Plano ativo: {treino.get('nome')} — objetivo: {treino.get('objetivo')}\n"
    if presencas:
        ctx += f"Frequência últimos 30 dias: {presencas.get('frequencia_pct')}%\n"
    return ctx

def resposta_rapida(mensagem: str, aluno: dict = {}) -> str:
    return None

async def responder_chatbot(mensagem: str, historico: list = [], contexto: str = "", nome_personal: str = "seu personal") -> str:
    system = f"""Você é AURI, assistente de treino inteligente da plataforma AurumSci.
Você é especialista em ciência do exercício, hipertrofia, nutrição esportiva e periodização.
Responda de forma direta, motivadora e baseada em evidências científicas.
Sempre personalize suas respostas com base no perfil do aluno.

PERFIL DO ALUNO:
{contexto}

🗺️ MAPA DO APP AURUMSCI (use pra direcionar aluno quando ele perguntar "como faço X" ou "onde fica Y"):

Aba TREINO 🏋️ (padrão):
- Check-in diário (botão verde no topo)
- Treino do dia (cards com exercícios)
- Banner "SEU CADASTRO" (se incompleto)
- Botão "VAMOS NOS CONHECER" pra completar perfil

Aba AVALIAÇÃO 📋:
- DOCUMENTOS: PAR-Q, Consentimento, Termo
- AVALIAÇÃO FÍSICA: peso, altura, circunferências, dobras cutâneas
- POSTURA: análise postural com fotos (frontal/lateral/posterior, IA analisa)
- TESTES: VO2 max (Cooper/Step/Milha), HRR, força, flexibilidade
- COMPOSIÇÃO: % gordura, massa magra (bioimpedância/dobras/ultrassom)

Aba PERIODIZAÇÃO 📅:
- Visualização das fases do treino ao longo do tempo
- Ciclos: força, hipertrofia, deload
- Bompa & Periodization Theory (2009)

Aba RESULTADOS 📈:
- Dashboard de evolução (gráficos)
- Card "SEU PROGRESSO" com delta entre avaliações
- Métricas: peso, % gordura, massa magra, VO2, força

Aba LOJA 🛒:
- Produtos selecionados pelo AurumSci
- Suplementos, equipamentos, acessórios

Aba FINANCEIRO 💳:
- Plano atual e pagamentos
- Histórico de assinatura

Menu PERFIL (toca a letra/avatar topo direito):
- Trocar idioma (PT/EN/ES)
- Tema dia/noite
- Excluir conta (botão vermelho)
- Sair da conta

REGRA DE OURO: quando aluno perguntar "como faço X" ou "onde fica Y", responda com o CAMINHO no app (ex: "Vai na aba AVALIAÇÃO → DOCUMENTOS → PAR-Q"). Seja direto e prático.

Seja conciso (máximo 3 parágrafos), use linguagem acessível e sempre encoraje o aluno.
FORMATO (Markdown — o app renderiza): separe cada parágrafo com uma LINHA EM BRANCO. Parágrafos curtos, de 1 a 3 frases.
SEMPRE que enumerar exercícios, itens, dicas ou passos, use LISTA em Markdown — um item por linha, cada linha começando com "- ". Exemplo:
- **Agachamento livre**: rei da massa muscular
- **Leg press 45°**: carga pesada com segurança
Nunca junte vários exercícios num parágrafo corrido — cada um vira um item de lista na sua própria linha."""

    msgs = []
    for h in historico[-10:]:
        if h.get("role") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": mensagem})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=system,
            messages=msgs
        )
        return response.content[0].text
    except Exception as e:
        return f"Desculpe, tive um problema técnico. Tente novamente! ({str(e)[:50]})"


# ═══════════════════════════════════════════════════════════
# AURI PRO — contexto pro personal trainer (adicionado 21/05/2026)
# ═══════════════════════════════════════════════════════════
def montar_contexto_personal(personal: dict, stats: dict = {}, aluno_selecionado: dict = {}) -> str:
    """
    Monta contexto rico pro AURI do PRO:
    - Tutorial das avaliacoes (como usar a plataforma)
    - Stats operacionais (alunos, inadimplencia, reavaliacoes)
    - Aluno selecionado (se houver) com anamnese + ultima avaliacao
    """
    ctx = f"""Personal Trainer: {personal.get('nome', 'Trainer')}
CREF: {personal.get('cref', 'nao informado')}

═══ COMO USAR A PLATAFORMA AURUMSCI PRO ═══

ANAMNESE: menu Alunos → abrir aluno → aba 📋 AVAL → aba 📝 ANAMNESE
- Preencha perfil (idade, peso, altura, sexo, nivel, objetivo, dias/semana)
- Marque patologias (hipertensao, diabetes, etc) — campo crucial
- Anote dores, cirurgias, medicamentos
- Clique 💾 SALVAR ANAMNESE

POSTURAL: aba 📸 POSTURAL dentro de Avaliacao
- Aluno em pe, roupa minima, olhar no horizonte
- Sobe 3 fotos: frente, lateral, costas
- Clique 🤖 ANALISAR COM IA — gera laudo + exercicios corretivos
- Exercicios corretivos aparecem automaticamente no treino do aluno

CIRCUNFERENCIAS: aba 📏 CIRCUNF.
- Fita metrica antropometrica
- Tronco: torax, cintura, abdomen, quadril
- Membros: braco D/E, antebraco D/E, coxa D/E, panturrilha D/E
- 💾 SALVAR CIRCUNFERENCIAS

COMPOSICAO CORPORAL (% Gordura): aba ⚖️ GORDURA
- 4 metodos: Bioimpedancia / 3 Dobras / 7 Dobras / Ultrassom 9 pontos
- Bioimpedancia: dados da balanca
- 3 Dobras (Jackson&Pollock): peitoral, abdomen, coxa (♂) | triceps, supra-iliaca, coxa (♀)
- 7 Dobras: protocolo completo Jackson&Pollock 1978
- Ultrassom: 9 pontos BodyMetrix
- Cada um tem botao CALCULAR + SALVAR

TESTES FISICOS: aba 💪 TESTES
- Flexao, barra fixa, abdominal, preensao manual, flexibilidade (Wells)
- Salva por teste

POTENCIA MMII: aba 🦵 MMII
- Sentar e levantar 30 segundos, joelho 90°, sem apoio das maos
- Conta repeticoes — Jones et al. 1999

VO2 MAX: aba 🫁 VO2 — SEMPRE POR ULTIMO!
- 3 protocolos: Cooper (12min), Milha de Kline, Step Up McArdle
- Cooper: distancia em 12 minutos
- Milha: tempo + FC final
- Step: 16.25 cm 22 steps/min por 3 minutos → FC apos 1 min
- VO2 contamina outros testes — sempre por ultimo

HRR (FC RECUPERACAO): dentro da aba VO2, abaixo do calculo
- FC pico + FC apos 1 min + PA repouso + PA pos
- Cole et al. 1999 NEJM
- HRR ≥20bpm = boa | 12-19 = regular | <12 = lenta (encaminhar cardiologista)

═══ ORDEM CRAVADA DA AVALIACAO ═══
1. Anamnese → 2. Postural → 3. Circunferencias → 4. % Gordura
5. Testes Fisicos → 6. MMII → 7. VO2 (por ultimo) → 8. HRR

═══ CLASSIFICACOES CIENTIFICAS ═══

% GORDURA (ACSM 2022):
- Homens 20-29a: <11 muito magro | <16 excelente | <20 bom | <24 regular | <28 acima | ≥28 alto
- Mulheres 20-29a: <16 muito magra | <21 excelente | <25 bom | <29 regular | <33 acima | ≥33 alto
- Idade aumenta os limites — usar tabela por faixa etaria

VO2 MAX (ACSM):
- ≥56 superior | ≥51 excelente | ≥43 bom | ≥34 regular | <34 fraco

HRR (Cole 1999):
- ≥20bpm boa recuperacao | 12-19 regular | <12 lenta (risco cardiovascular)

MMII (Jones 1999): tabelas por idade/sexo no proprio app

═══ CUIDADOS POPULACOES ESPECIAIS ═══
- HIPERTENSO: evitar Valsalva, isometricos pesados; controlar PA antes/durante
- DIABETICO: monitorar glicemia antes/depois; horario apos refeicao
- CARDIOPATA: HRR obrigatoria; intensidade conforme reserva FC; encaminhar para teste ergometrico
- IDOSO: MMII como triagem de sarcopenia (<8 reps risco alto)
- GESTANTE: evitar decubito dorsal apos 16sem; FC alvo conservadora
- ARTROSE/HERNIA: evitar impacto; trabalhar core e estabilidade primeiro
"""
    if stats:
        ctx += f"""

═══ DADOS OPERACIONAIS DO TRAINER ═══
- Alunos ativos: {stats.get('alunos_ativos', 0)}
- Inadimplencia: {stats.get('inadimplentes', 0)} alunos
- Precisam reavaliar (>56 dias): {stats.get('precisam_reavaliar', 0)}
- Receita do mes: R$ {stats.get('receita_mes', 0):.2f}
- Frequencia media (30d): {stats.get('frequencia_media', 0):.0f}%
"""
    if aluno_selecionado:
        ctx += f"""

═══ ALUNO ATUALMENTE ABERTO ═══
Nome: {aluno_selecionado.get('nome', '-')}
Objetivo: {aluno_selecionado.get('objetivo', '-')}
Nivel: {aluno_selecionado.get('nivel', '-')}
Patologias: {aluno_selecionado.get('patologias', 'nenhuma')}
Medicamentos: {aluno_selecionado.get('medicamentos', 'nenhum')}
Ultima avaliacao: {aluno_selecionado.get('ultima_avaliacao', 'sem dados')}
"""
    return ctx

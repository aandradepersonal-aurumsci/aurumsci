# =============================================================================
# APP_ALUNO.PY — Router completo do App do Aluno
# O diferencial do AurumSci — aluno autônomo com IA
#
# Endpoints:
# POST /app-aluno/onboarding          — anamnese inicial completa
# POST /app-aluno/bioimpedancia       — registra medidas
# POST /app-aluno/postural            — análise postural com 3 fotos + IA
# GET  /app-aluno/treino-hoje         — treino do dia com exercícios
# POST /app-aluno/presenca            — registra presença
# GET  /app-aluno/dashboard           — evolução completa
# GET  /app-aluno/reavaliacao         — verifica se está na hora de reavaliar
# POST /app-aluno/chat                — chatbot AURI focado no aluno
# =============================================================================

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Aluno
from app.routers.portal_aluno import get_aluno_logado

router = APIRouter(prefix="/app-aluno", tags=["App do Aluno"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class OnboardingSchema(BaseModel):
    objetivo: str                          # hipertrofia, emagrecimento, etc
    nivel_experiencia: str                 # iniciante, intermediario, avancado
    dias_disponiveis: int                  # 2 a 6
    tipo_periodizacao: Optional[str] = "ondulatoria"  # ondulatoria ou blocos
    restricoes_medicas: Optional[str] = None
    historico_lesoes: Optional[str] = None
    peso: Optional[float] = None
    estatura: Optional[float] = None
    idade: Optional[int] = None
    sexo: Optional[str] = None


class BioimpedanciaSchema(BaseModel):
    peso: float
    percentual_gordura: float
    massa_gorda_kg: Optional[float] = None
    massa_magra_kg: Optional[float] = None
    agua_corporal: Optional[float] = None
    massa_ossea: Optional[float] = None
    metabolismo_basal: Optional[float] = None


class PresencaSchema(BaseModel):
    sessao_id: Optional[int] = None
    duracao_minutos: Optional[int] = None
    observacao: Optional[str] = None


class ChatSchema(BaseModel):
    mensagem: str
    historico: Optional[List[dict]] = []


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/onboarding")
async def onboarding(
    dados: OnboardingSchema,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """
    Onboarding completo do aluno:
    1. Salva anamnese
    2. Gera periodização automática baseada no objetivo
    3. Cria plano de treino com exercícios
    """
    from app.motor.periodizacao import gerar_periodizacao, periodizacao_to_dict
    from app.routers.anamnese import Anamnese
    from app.routers.treino import PlanoTreino, SessaoTreino

    # Salva anamnese
    anamnese = db.query(Anamnese).filter(Anamnese.aluno_id == aluno.id).first()
    if not anamnese:
        anamnese = Anamnese(
            aluno_id=aluno.id
        )
        db.add(anamnese)
    else:
        anamnese.doencas_cronicas = dados.objetivo
        

    # Gera periodização automática
    periodizacao = gerar_periodizacao(
        objetivo=dados.objetivo,
        nivel=dados.nivel_experiencia,
        dias_semana=dados.dias_disponiveis,
        semanas_total=12,
        data_inicio=date.today()
    )
    periodo_dict = periodizacao_to_dict(periodizacao)

    # Cria plano de treino
    plano_existente = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).first()
    if plano_existente:
        plano_existente.ativo = False

    import json
    plano = PlanoTreino(
        aluno_id=aluno.id,
        personal_id=aluno.personal_id if hasattr(aluno, 'personal_id') else 1,
        nome=f"Plano {dados.objetivo.capitalize()} — {dados.nivel_experiencia.capitalize()}",
        objetivo=dados.objetivo,
        nivel=dados.nivel_experiencia,
        dias_semana=dados.dias_disponiveis,
        semanas_total=12,
        data_inicio=date.today(),
        ativo=True,
        periodizacao=json.dumps(periodo_dict, ensure_ascii=False)
    )
    db.add(plano)
    db.flush()

    # Cria sessões e popula exercícios do motor
    from app.routers.treino import Exercicio, ExercicioSessao
    for i, sessao_prescrita in enumerate(periodizacao.sessoes_prescritas):
        sessao = SessaoTreino(
            plano_id=plano.id,
            nome=sessao_prescrita.nome,
            dia_semana=i + 1
        )
        db.add(sessao)
        db.flush()
        for ex in sessao_prescrita.exercicios:
            exercicio_cat = db.query(Exercicio).filter(Exercicio.nome == ex.nome).first()
            if not exercicio_cat:
                exercicio_cat = Exercicio(
                    nome=ex.nome,
                    grupo_muscular=ex.grupo,
                    descricao=ex.tecnica_especial or ""
                )
                db.add(exercicio_cat)
                db.flush()
            ex_sessao = ExercicioSessao(
                sessao_id=sessao.id,
                exercicio_id=exercicio_cat.id,
                ordem=ex.ordem,
                series=ex.series,
                repeticoes=str(ex.repeticoes),
                carga_kg=0.0,
                tempo_descanso_seg=ex.descanso_segundos,
                observacoes=ex.tecnica_especial or ""
            )
            db.add(ex_sessao)

    db.commit()

    return {
        "mensagem": f"Bem-vindo ao AurumSci, {aluno.nome.split()[0]}!",
        "plano": {
            "nome": plano.nome,
            "objetivo": dados.objetivo,
            "dias_semana": dados.dias_disponiveis,
            "semanas": 12,
            "divisao": periodizacao.divisao_nome,
            "sessoes": periodizacao.divisao_sessoes,
        },
        "proxima_etapa": "Complete sua bioimpedância e análise postural para personalizar ainda mais seu treino!"
    }


@router.post("/bioimpedancia")
async def registrar_bioimpedancia(
    dados: BioimpedanciaSchema,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Registra medidas de bioimpedância e calcula composição corporal."""
    from app.motor.calculos import bioimpedancia, calcular_massas, calcular_imc
    from app.routers.avaliacao import AvaliacaoFisica

    resultado = bioimpedancia(
        percentual_gordura=dados.percentual_gordura,
        peso=dados.peso,
        massa_gorda_kg=dados.massa_gorda_kg,
        massa_magra_kg=dados.massa_magra_kg
    )
    resultado = calcular_massas(resultado, dados.peso)

    # Busca última avaliação ou cria nova
    aval = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()

    hoje = date.today()
    if not aval or aval.data_avaliacao != hoje:
        aval = AvaliacaoFisica(
            aluno_id=aluno.id,
            personal_id=1,
            data_avaliacao=hoje,
            protocolo_composicao="bioimpedancia"
        )
        db.add(aval)

    aval.peso               = dados.peso
    aval.percentual_gordura = resultado.percentual_gordura
    aval.massa_gorda_kg     = resultado.massa_gorda_kg
    aval.massa_magra_kg     = resultado.massa_magra_kg
    aval.classificacao_gordura = resultado.classificacao_gordura

    if hasattr(aval, 'estatura') and aval.estatura:
        imc, cls_imc = calcular_imc(dados.peso, aval.estatura)
        aval.imc = imc
        aval.classificacao_imc = cls_imc

    db.commit()

    return {
        "mensagem": "Bioimpedância registrada!",
        "composicao": {
            "peso": dados.peso,
            "percentual_gordura": resultado.percentual_gordura,
            "classificacao": resultado.classificacao_gordura,
            "massa_gorda_kg": resultado.massa_gorda_kg,
            "massa_magra_kg": resultado.massa_magra_kg,
        }
    }


@router.post("/postural")
async def analise_postural(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db),
    foto_frente: Optional[UploadFile] = File(None),
    foto_lado: Optional[UploadFile] = File(None),
    foto_costas: Optional[UploadFile] = File(None),
):
    """
    Análise postural com IA — 3 fotos → Claude Vision → desvios automáticos
    Resultado é salvo na avaliação e usado para personalizar exercícios
    """
    import base64
    from app.motor.ia_postural import analisar_postural
    from app.routers.avaliacao import AvaliacaoFisica

    # Lê as fotos
    foto_frente_b64  = base64.b64encode(await foto_frente.read()).decode()  if foto_frente  else None
    foto_lado_b64    = base64.b64encode(await foto_lado.read()).decode()    if foto_lado    else None
    foto_costas_b64  = base64.b64encode(await foto_costas.read()).decode()  if foto_costas  else None

    # Analisa com IA
    resultado = await analisar_postural(foto_frente_b64, foto_lado_b64, foto_costas_b64)

    if resultado.erro:
        raise HTTPException(status_code=500, detail=resultado.erro)

    # Salva na avaliação
    aval = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()

    if not aval:
        aval = AvaliacaoFisica(
            aluno_id=aluno.id,
            personal_id=1,
            data_avaliacao=date.today()
        )
        db.add(aval)

    aval.postura_cabeca       = resultado.cabeca
    aval.postura_ombros       = resultado.ombros
    aval.postura_coluna       = resultado.coluna
    aval.postura_quadril      = resultado.quadril
    aval.postura_joelhos      = resultado.joelhos
    aval.postura_pes          = resultado.pes
    aval.postura_observacoes  = resultado.observacoes
    db.commit()

    return {
        "mensagem": "Análise postural concluída!",
        "desvios": {
            "cabeca":   resultado.cabeca,
            "ombros":   resultado.ombros,
            "coluna":   resultado.coluna,
            "quadril":  resultado.quadril,
            "joelhos":  resultado.joelhos,
            "pes":      resultado.pes,
        },
        "observacoes":    resultado.observacoes,
        "achados":        resultado.achados,
        "recomendacoes":  resultado.recomendacoes,
        "proxima_etapa":  "Seus exercícios foram personalizados com base nos desvios encontrados!"
    }


@router.get("/treino-hoje")
async def treino_hoje(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Retorna o treino do dia com exercícios detalhados."""
    from app.routers.treino import PlanoTreino, SessaoTreino, ExercicioSessao

    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).first()

    if not plano:
        return {"mensagem": "Nenhum plano ativo. Faça o onboarding primeiro!"}

    # Dia relativo ao início do plano — nunca depende do dia da semana fixo
    data_inicio = plano.data_inicio if plano.data_inicio else date.today()
    dias_desde_inicio = (date.today() - data_inicio).days
    dias_treino = plano.dias_semana or 3

    dia_na_semana = dias_desde_inicio % 7
    e_dia_treino = dia_na_semana < dias_treino

    if not e_dia_treino:
        return {
            "mensagem": "Hoje é dia de descanso! Recuperação também é treino.",
            "dica": "Aproveite para fazer mobilidade ou caminhada leve."
        }

    idx_sessao = dia_na_semana % dias_treino
    sessao = db.query(SessaoTreino).filter(
        SessaoTreino.plano_id == plano.id
    ).order_by(SessaoTreino.dia_semana).offset(idx_sessao).first()

    if not sessao:
        return {
            "mensagem": "Hoje é dia de descanso! Recuperação também é treino.",
            "dica": "Aproveite para fazer mobilidade ou caminhada leve."
        }

    exercicios = db.query(ExercicioSessao).filter(
        ExercicioSessao.sessao_id == sessao.id
    ).order_by(ExercicioSessao.ordem).all()

    # Busca corretivos posturais da última avaliação
    from app.routers.avaliacao import AvaliacaoFisica
    import json as _json
    ultima_aval = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    corretivos = []
    if ultima_aval and ultima_aval.observacoes:
        try:
            corretivos = _json.loads(ultima_aval.observacoes)
        except Exception:
            pass
    postura_resumo = {}
    if ultima_aval:
        postura_resumo = {
            "cabeca": ultima_aval.postura_cabeca,
            "ombros": ultima_aval.postura_ombros,
            "coluna": ultima_aval.postura_coluna,
        }

    return {
        "sessao": sessao.nome,
        "data": str(date.today()),
        "exercicios": [{
            "ordem":       e.ordem,
            "nome":        db.query(__import__("app.routers.treino", fromlist=["Exercicio"]).Exercicio).filter_by(id=e.exercicio_id).first().nome if e.exercicio_id else "",
            "series":      e.series,
            "repeticoes":  e.repeticoes,
            "carga":       e.carga_kg,
            "descanso":    e.tempo_descanso_seg,
            "observacao":  e.observacoes,
            "corretivo":   False,
        } for e in exercicios],
        "total_exercicios": len(exercicios),
        "corretivos_posturais": corretivos,
        "postura_resumo": postura_resumo
    }


@router.post("/presenca")
async def registrar_presenca(
    dados: PresencaSchema,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Registra presença do aluno no treino."""
    from app.routers.treino import PresencaTreino, PlanoTreino

    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).first()

    presenca = PresencaTreino(
        aluno_id=aluno.id,
        personal_id=1,
        plano_id=plano.id if plano else None,
        sessao_id=dados.sessao_id,
        data_presenca=date.today(),
        presente=True,
        duracao_minutos=dados.duracao_minutos,
        observacao=dados.observacao
    )
    db.add(presenca)
    db.commit()

    return {
        "mensagem": "Presença registrada! Continue assim!",
        "data": str(date.today()),
        "sequencia": _calcular_sequencia(aluno.id, db)
    }


@router.get("/dashboard")
async def dashboard(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """
    Dashboard completo de evolução do aluno:
    - Composição corporal ao longo do tempo
    - Frequência de treinos
    - Evolução postural
    - Próxima reavaliação
    """
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PresencaTreino

    # Avaliações ordenadas por data
    avals = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao).all()

    # Evolução composição corporal
    evolucao = [{
        "data":              str(a.data_avaliacao),
        "peso":              a.peso,
        "percentual_gordura": a.percentual_gordura,
        "massa_magra_kg":    a.massa_magra_kg,
        "imc":               a.imc,
    } for a in avals if a.peso]

    # Frequência últimos 30 dias
    trinta_dias  = date.today() - timedelta(days=30)
    presencas_30 = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno.id,
        PresencaTreino.data_presenca >= trinta_dias,
        PresencaTreino.presente == True
    ).count()

    # Última avaliação
    ultima_aval = avals[-1] if avals else None
    dias_ultima = (date.today() - ultima_aval.data_avaliacao).days if ultima_aval else None

    # Próxima reavaliação
    proxima_reavaliacao = None
    alerta_reavaliacao  = False
    if ultima_aval:
        proxima = ultima_aval.data_avaliacao + timedelta(days=60)
        proxima_reavaliacao = str(proxima)
        alerta_reavaliacao  = date.today() >= proxima

    return {
        "aluno": {
            "nome":    aluno.nome,
            "objetivo": aluno.objetivo.value if aluno.objetivo else None,
        },
        "resumo": {
            "total_avaliacoes":   len(avals),
            "presencas_30_dias":  presencas_30,
            "dias_ultima_aval":   dias_ultima,
            "alerta_reavaliacao": alerta_reavaliacao,
            "proxima_reavaliacao": proxima_reavaliacao,
        },
        "evolucao_composicao": evolucao,
        "ultima_avaliacao": {
            "data":               str(ultima_aval.data_avaliacao) if ultima_aval else None,
            "peso":               ultima_aval.peso if ultima_aval else None,
            "percentual_gordura": ultima_aval.percentual_gordura if ultima_aval else None,
            "massa_magra_kg":     ultima_aval.massa_magra_kg if ultima_aval else None,
            "classificacao":      ultima_aval.classificacao_gordura if ultima_aval else None,
        } if ultima_aval else None,
        "postura": {
            "cabeca":  ultima_aval.postura_cabeca if ultima_aval else None,
            "ombros":  ultima_aval.postura_ombros if ultima_aval else None,
            "coluna":  ultima_aval.postura_coluna if ultima_aval else None,
        } if ultima_aval else None,
    }


@router.get("/reavaliacao")
async def verificar_reavaliacao(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Verifica se o aluno está na hora de reavaliar (a cada 60 dias)."""
    from app.routers.avaliacao import AvaliacaoFisica

    ultima = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()

    if not ultima:
        return {
            "precisa_reavaliar": True,
            "mensagem": "Faça sua primeira avaliação para começarmos a acompanhar sua evolução!"
        }

    dias = (date.today() - ultima.data_avaliacao).days
    proxima = ultima.data_avaliacao + timedelta(days=60)
    faltam  = (proxima - date.today()).days

    if dias >= 60:
        return {
            "precisa_reavaliar": True,
            "dias_desde_ultima": dias,
            "mensagem": f"Já faz {dias} dias desde sua última avaliação! Hora de ver sua evolução!"
        }

    return {
        "precisa_reavaliar": False,
        "dias_desde_ultima": dias,
        "faltam_dias": faltam,
        "proxima_data": str(proxima),
        "mensagem": f"Próxima reavaliação em {faltam} dias ({proxima.strftime('%d/%m/%Y')})"
    }


@router.post("/chat")
async def chat_aluno(
    dados: ChatSchema,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Chatbot AURI focado no aluno — responde dúvidas sobre treino e evolução."""
    from app.motor.ia_chatbot import montar_contexto, responder_chatbot, resposta_rapida
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PlanoTreino, PresencaTreino

    # Resposta rápida para saudações
    rapida = resposta_rapida(dados.mensagem, {"nome": aluno.nome})
    if rapida:
        return {"resposta": rapida}

    # Monta contexto rico do aluno
    avals    = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).limit(3).all()

    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).first()

    presencas_30 = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno.id,
        PresencaTreino.data_presenca >= date.today() - timedelta(days=30),
        PresencaTreino.presente == True
    ).count()

    aluno_dict = {
        "nome":    aluno.nome,
        "objetivo": aluno.objetivo.value if aluno.objetivo else "hipertrofia",
        "nivel":   aluno.nivel_experiencia.value if aluno.nivel_experiencia else "iniciante",
    }

    avals_dict = [{"data": str(a.data_avaliacao), "peso": a.peso,
                   "percentual_gordura": a.percentual_gordura} for a in avals]

    treino_dict = {"nome": plano.nome, "objetivo": plano.objetivo} if plano else {}

    presencas_dict = {"frequencia_pct": round(presencas_30 / 30 * 100, 1)}

    contexto = montar_contexto(aluno_dict, avals_dict, treino_dict, {}, presencas_dict)

    resposta = await responder_chatbot(
        mensagem=dados.mensagem,
        historico=dados.historico or [],
        contexto=contexto,
        nome_personal="seu programa"
    )

    return {"resposta": resposta}


# ── Helper ────────────────────────────────────────────────────────────────────

def _calcular_sequencia(aluno_id: int, db: Session) -> int:
    """Calcula sequência de dias consecutivos de treino."""
    from app.routers.treino import PresencaTreino
    presencas = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno_id,
        PresencaTreino.presente == True
    ).order_by(PresencaTreino.data_presenca.desc()).limit(30).all()

    if not presencas:
        return 1

    sequencia = 1
    for i in range(len(presencas) - 1):
        diff = (presencas[i].data_presenca - presencas[i+1].data_presenca).days
        if diff == 1:
            sequencia += 1
        else:
            break
    return sequencia


@router.get("/resultado")
def resultado(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    avals = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).all()
    if not avals:
        return {"detail": "Sem avaliacoes"}
    atual = avals[0]
    anterior = avals[1] if len(avals) > 1 else None
    variacao_peso = None
    if anterior and atual.peso and anterior.peso:
        variacao_peso = round(float(atual.peso) - float(anterior.peso), 1)
    massa_magra = None
    if atual.peso and atual.percentual_gordura:
        massa_magra = round(float(atual.peso) * (1 - float(atual.percentual_gordura)/100), 1)
    return {
        "peso_atual": float(atual.peso) if atual.peso else None,
        "percentual_gordura": float(atual.percentual_gordura) if atual.percentual_gordura else None,
        "massa_magra": massa_magra,
        "variacao_peso": variacao_peso,
        "data": str(atual.data_avaliacao)
    }


@router.get("/periodizacao")
def periodizacao(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    objetivo = aluno.objetivo.value if aluno.objetivo else "hipertrofia"
    nivel = aluno.nivel_experiencia.value if aluno.nivel_experiencia else "intermediario"
    ciclos_map = {
        "hipertrofia": [
            {"emoji":"💪","nome":"FASE 1 — ADAPTACAO","descricao":"Semanas 1-4 · Base muscular","detalhes":"Volume moderado\nIntensidade 60-70% 1RM\nFoco em tecnica e postura\n3-4x por semana"},
            {"emoji":"🔥","nome":"FASE 2 — HIPERTROFIA","descricao":"Semanas 5-12 · Crescimento","detalhes":"Volume alto\nIntensidade 70-85% 1RM\nProgressao de carga semanal\n4-5x por semana"},
            {"emoji":"⚡","nome":"FASE 3 — INTENSIFICACAO","descricao":"Semanas 13-16 · Forca","detalhes":"Volume baixo\nIntensidade 85-95% 1RM\nMetodos avancados\n4x por semana"},
            {"emoji":"😴","nome":"FASE 4 — DELOAD","descricao":"Semana 17 · Recuperacao","detalhes":"Volume 50% do normal\nIntensidade reduzida\nFoco em mobilidade\n3x por semana"},
        ],
        "emagrecimento": [
            {"emoji":"🏃","nome":"FASE 1 — ATIVACAO","descricao":"Semanas 1-4 · Queima inicial","detalhes":"Cardio moderado\nTreino funcional\nDeficit calorico leve\n4x por semana"},
            {"emoji":"🔥","nome":"FASE 2 — ACELERACAO","descricao":"Semanas 5-10 · Queima intensa","detalhes":"HIIT 2x semana\nMusculacao 3x\nDeficit calorico moderado\n5x por semana"},
            {"emoji":"💪","nome":"FASE 3 — MANUTENCAO","descricao":"Semanas 11-16 · Preservar musculo","detalhes":"Foco em forca\nCardio steady state\nDieta de manutencao\n4x por semana"},
        ],
        "condicionamento": [
            {"emoji":"🫀","nome":"FASE 1 — BASE AEROBICA","descricao":"Semanas 1-6 · Cardio base","detalhes":"Zona 2 predominante\nFC 60-70% max\n30-45min por sessao\n4x por semana"},
            {"emoji":"⚡","nome":"FASE 2 — POTENCIA","descricao":"Semanas 7-12 · Intensidade","detalhes":"Intervalados\nFC 80-90% max\nVO2max em foco\n5x por semana"},
        ],
    }
    ciclos = ciclos_map.get(objetivo, ciclos_map["hipertrofia"])
    return {"objetivo": objetivo, "nivel": nivel, "ciclos": ciclos}


@router.get("/financeiro")
def financeiro(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    """Retorna plano e histórico de pagamentos do aluno."""
    from app.routers.financeiro import Pagamento
    from datetime import date
    pags = db.query(Pagamento).filter(
        Pagamento.aluno_id == aluno.id
    ).order_by(Pagamento.data_vencimento.desc()).all()
    if not pags:
        return {"detail": "Nenhum pagamento encontrado"}
    ultimo = pags[0]
    hoje = date.today()
    if ultimo.data_pagamento:
        status = "pago"
    elif ultimo.data_vencimento and ultimo.data_vencimento < hoje:
        status = "atrasado"
    else:
        status = "pendente"
    historico = []
    for p in pags[:6]:
        st = "pago" if p.data_pagamento else ("atrasado" if p.data_vencimento and p.data_vencimento < hoje else "pendente")
        historico.append({
            "mes": p.data_vencimento.strftime("%b/%Y") if p.data_vencimento else "",
            "valor": str(p.valor),
            "status": st
        })
    return {
        "plano": "Plano Personal",
        "valor": str(ultimo.valor),
        "status": status,
        "vencimento": ultimo.data_vencimento.strftime("%d/%m/%Y") if ultimo.data_vencimento else None,
        "historico": historico
    }


@router.post("/treino-concluir")
def treino_concluir(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    """Registra conclusão do treino do dia."""
    return {"mensagem": "Treino concluído! Parabéns!", "sequencia": _calcular_sequencia(aluno.id, db)}


@router.post("/checkin")
def checkin(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    """Registra check-in do aluno."""
    from app.routers.treino import PresencaTreino, PlanoTreino
    from datetime import date
    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).first()
    presenca = PresencaTreino(
        aluno_id=aluno.id,
        personal_id=aluno.personal_id if hasattr(aluno, 'personal_id') else 1,
        plano_id=plano.id if plano else None,
        data_presenca=date.today(),
        presente=True
    )
    db.add(presenca)
    db.commit()
    return {"mensagem": "Check-in registrado!", "sequencia": _calcular_sequencia(aluno.id, db)}


class OvertrainingSchema(BaseModel):
    score: int
    risco: str

@router.post("/overtraining")
def registrar_overtraining(
    dados: OvertrainingSchema,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    import json
    from app.routers.avaliacao import AvaliacaoFisica
    aval = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    if aval and hasattr(aval, 'observacoes'):
        obs = {"overtraining_score": dados.score, "overtraining_risco": dados.risco, "overtraining_data": str(date.today())}
        try:
            existing = json.loads(aval.observacoes or '{}')
            existing.update(obs)
            aval.observacoes = json.dumps(existing, ensure_ascii=False)
        except Exception:
            aval.observacoes = json.dumps(obs, ensure_ascii=False)
        db.commit()
    return {"mensagem": "Questionário registrado!", "score": dados.score, "risco": dados.risco, "deload_recomendado": dados.risco == "alto"}

@router.get("/medidas")
def get_medidas(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    aval = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    if not aval:
        return {}
    campos = ['torax','cintura','abdomen','quadril','bracoD','bracoE','antebD','antebE','coxaD','coxaE','pantD','pantE']
    return {c: float(getattr(aval, c)) for c in campos if getattr(aval, c, None)}

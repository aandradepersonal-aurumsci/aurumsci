"""
Router — App Personal (expandido)
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from app.database import get_db
from app.models import Personal, Aluno
from app.utils.auth import get_personal_atual

router = APIRouter(prefix="/app-personal", tags=["App Personal"])


class ChatPersonalSchema(BaseModel):
    mensagem: str
    historico: Optional[List[dict]] = []
    idioma: Optional[str] = "pt"


@router.post("/chat")
async def chat_personal(dados: ChatPersonalSchema, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.motor.ia_chatbot import responder_chatbot
    idiomas = {
        "pt": "Responda SEMPRE em Português do Brasil.",
        "en": "Always respond in English.",
        "es": "Responde SIEMPRE en Español."
    }
    instrucao = idiomas.get(dados.idioma or "pt", idiomas["pt"])
    contexto = f"""{instrucao}
Personal Trainer: {personal.nome}
CREF: {personal.cref or 'não informado'}
Você está conversando com um personal trainer profissional.
Ajude com gestão de alunos, protocolos de treino, periodização, nutrição esportiva e ciência do exercício.
Seja técnico, direto e baseado em evidências científicas."""
    resposta = await responder_chatbot(
        mensagem=dados.mensagem,
        historico=dados.historico or [],
        contexto=contexto,
        nome_personal=personal.nome
    )
    return {"resposta": resposta}


@router.get("/dashboard")
def dashboard(personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno
    from app.routers.treino import PresencaTreino
    from app.routers.financeiro import Pagamento, cs as calc_status

    alunos = db.query(Aluno).filter(Aluno.personal_id == personal.id, Aluno.ativo == True).all()
    total_alunos = len(alunos)
    aluno_ids = [a.id for a in alunos]

    # Check-ins hoje
    hoje = date.today()
    checkins_hoje = 0
    if aluno_ids:
        checkins_hoje = db.query(PresencaTreino).filter(
            PresencaTreino.aluno_id.in_(aluno_ids),
            PresencaTreino.data == hoje
        ).count()

    # Pagamentos
    pendentes = 0
    receita_mes = 0.0
    if aluno_ids:
        pags = db.query(Pagamento).filter(Pagamento.aluno_id.in_(aluno_ids)).all()
        for p in pags:
            status = calc_status(p)
            if status in ('pendente', 'atrasado'):
                pendentes += 1
            if status == 'pago' and p.data_pagamento and p.data_pagamento.month == hoje.month and p.data_pagamento.year == hoje.year:
                receita_mes += p.valor

    # Alunos recentes
    recentes = [{
        "id": a.id,
        "nome": a.nome,
        "objetivo": a.objetivo.value if a.objetivo else "",
        "nivel": a.nivel_experiencia.value if a.nivel_experiencia else "",
        "ativo": a.ativo
    } for a in alunos[:5]]

    # Limite de alunos por plano
    LIMITES_PLANO = {'bronze': 10, 'prata': 20, 'ouro': 50, 'diamante': 999999}
    plano_atual = personal.plano or 'bronze'
    limite_alunos = LIMITES_PLANO.get(plano_atual, 10)
    return {
        "total_alunos": total_alunos,
        "limite_alunos": limite_alunos,
        "plano": plano_atual,
        "checkins_hoje": checkins_hoje,
        "pagamentos_pendentes": pendentes,
        "receita_mes": round(receita_mes, 2),
        "alunos_recentes": recentes,
        "logo_url": personal.logo_url,
        "nome_empresa": personal.nome_empresa
    }


@router.get("/aluno/{aluno_id}/resumo")
def resumo_aluno(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PlanoTreino, PresencaTreino

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    aval = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno_id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    plano = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno_id, PlanoTreino.ativo == True).first()

    trinta = date.today().replace(day=1)
    presencas = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno_id,
        PresencaTreino.data >= trinta,
        PresencaTreino.presente == True
    ).count()

    return {
        "aluno": {"id": aluno.id, "nome": aluno.nome, "objetivo": aluno.objetivo.value if aluno.objetivo else "", "nivel": aluno.nivel_experiencia.value if aluno.nivel_experiencia else ""},
        "avaliacao": {"peso": aval.peso if aval else None, "gordura": aval.percentual_gordura if aval else None, "data": str(aval.data_avaliacao) if aval else None},
        "plano": {"nome": plano.nome if plano else None, "dias_semana": plano.dias_semana if plano else None},
        "frequencia_mes": presencas,
        "postural": {"cabeca": aval.postura_cabeca if aval else None, "ombros": aval.postura_ombros if aval else None, "coluna": aval.postura_coluna if aval else None} if aval else None,
        "precisa_reavaliar": (not aval) or ((date.today() - aval.data_avaliacao).days >= 56),
        "dias_desde_avaliacao": (date.today() - aval.data_avaliacao).days if aval else None
    }



@router.get("/aluno/{aluno_id}/resumo-completo")
def resumo_completo_aluno(aluno_id: int, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PlanoTreino, PresencaTreino
    from datetime import date
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    aval = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno_id).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    plano = db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno_id, PlanoTreino.ativo == True).first()
    trinta = date.today().replace(day=1)
    freq_mes = db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno_id, PresencaTreino.data >= trinta, PresencaTreino.presente == True).count()
    freq_total = db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno_id, PresencaTreino.presente == True).count()
    return {
        "aluno": {"id": aluno.id, "nome": aluno.nome},
        "avaliacao": {
            "peso": aval.peso if aval else None,
            "gordura": aval.percentual_gordura if aval else None,
            "massa_magra": aval.massa_magra_kg if aval else None,
            "tmb": None,
            "vo2max": aval.vo2max if aval else None,
            "hrr": None,
            "data": str(aval.data_avaliacao) if aval else None,
        },
        "testes": {
            "flexao": aval.teste_flexao_num if aval else None,
            "barra": aval.teste_barra_num if aval else None,
            "flexibilidade": aval.teste_flexibilidade_cm if aval else None,
        },
        "postural": {
            "cabeca": aval.postura_cabeca if aval else None,
            "ombros": aval.postura_ombros if aval else None,
            "coluna": aval.postura_coluna if aval else None,
            "observacoes": aval.postura_observacoes if aval else None,
        } if aval else None,
        "plano": {"nome": plano.nome if plano else None},
        "frequencia_mes": freq_mes,
        "frequencia_total": freq_total,
    }

@router.get("/exercicios-banco")
def listar_exercicios(personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.routers.treino import Exercicio
    exercicios = db.query(Exercicio).order_by(Exercicio.grupo_muscular, Exercicio.nome).all()
    return {"exercicios": [{"id": e.id, "nome": e.nome, "grupo_muscular": e.grupo_muscular, "equipamento": e.equipamento, "descricao": e.descricao, "video_url": e.video_url} for e in exercicios]}


class SessaoSchema(BaseModel):
    nome: str
    exercicios: List[dict]

class SalvarTreinoSchema(BaseModel):
    objetivo: str
    nivel: str = "intermediario"
    dias_disponiveis: int = 3
    sessoes: List[SessaoSchema]

@router.post("/aluno/{aluno_id}/salvar-treino")
def salvar_treino_aluno(aluno_id: int, dados: SalvarTreinoSchema, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno
    from app.routers.treino import PlanoTreino, SessaoTreino, ExercicioSessao
    from datetime import date
    import json

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")

    db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno_id, PlanoTreino.ativo == True).update({"ativo": False})

    plano = PlanoTreino(
        aluno_id=aluno_id,
        personal_id=personal.id,
        nome=f"Plano {dados.objetivo.capitalize()} — Por {personal.nome.split()[0]}",
        objetivo=dados.objetivo,
        nivel=dados.nivel,
        dias_semana=dados.dias_disponiveis,
        semanas_total=12,
        data_inicio=date.today(),
        ativo=True,
        periodizacao=json.dumps({"tipo": "manual", "personal": personal.nome})
    )
    db.add(plano)
    db.flush()

    for i, sessao_dados in enumerate(dados.sessoes):
        sessao = SessaoTreino(plano_id=plano.id, nome=sessao_dados.nome, dia_semana=i+1)
        db.add(sessao)
        db.flush()
        for j, ex in enumerate(sessao_dados.exercicios):
            ex_sessao = ExercicioSessao(
                sessao_id=sessao.id,
                exercicio_id=ex.get("exercicio_id") or ex.get("id"),
                ordem=j+1,
                series=ex.get("series", 3),
                repeticoes=str(ex.get("repeticoes", "10-12")),
                carga_kg=0.0,
                tempo_descanso_seg=ex.get("descanso", 90),
            )
            db.add(ex_sessao)

    db.commit()
    return {"mensagem": f"Treino salvo para {aluno.nome}!", "plano_id": plano.id}


class AnamnesesPayload(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    sexo: Optional[str] = None
    nivel: Optional[str] = None
    objetivo: Optional[str] = None
    dias_semana: Optional[str] = None
    tempo_sessao: Optional[str] = None
    dores: Optional[str] = None
    cirurgias: Optional[str] = None
    medicamentos: Optional[str] = None
    patologias: Optional[str] = None
    liberacao_medica: Optional[str] = None
    remoto: Optional[str] = None
    observacoes: Optional[str] = None

class CircunferenciasPayload(BaseModel):
    pescoco: Optional[float] = None
    ombro: Optional[float] = None
    torax: Optional[float] = None
    cintura: Optional[float] = None
    abdomen: Optional[float] = None
    quadril: Optional[float] = None
    braco_d: Optional[float] = None
    braco_e: Optional[float] = None
    antebraco_d: Optional[float] = None
    antebraco_e: Optional[float] = None
    coxa_d: Optional[float] = None
    coxa_e: Optional[float] = None
    panturrilha_d: Optional[float] = None
    panturrilha_e: Optional[float] = None

class ComposicaoPayload(BaseModel):
    peso: Optional[float] = None
    gordura_pct: Optional[float] = None
    massa_magra: Optional[float] = None
    agua_pct: Optional[float] = None
    massa_ossea: Optional[float] = None
    tmb: Optional[float] = None
    d3_d1: Optional[float] = None
    d3_d2: Optional[float] = None
    d3_d3: Optional[float] = None
    d7_peit: Optional[float] = None
    d7_abdo: Optional[float] = None
    d7_coxa: Optional[float] = None

class TestesFisicosPayload(BaseModel):
    flexao: Optional[int] = None
    barra: Optional[int] = None
    abdominal: Optional[int] = None
    mmii_30s: Optional[int] = None
    preensao_dom: Optional[float] = None
    preensao_ndom: Optional[float] = None
    wells: Optional[float] = None
    sexo: Optional[str] = None
    idade: Optional[int] = None

class MMIIPayload(BaseModel):
    repeticoes: Optional[int] = None
    sexo: Optional[str] = None
    idade: Optional[int] = None

class VO2HRRPayload(BaseModel):
    cooper_dist: Optional[float] = None
    milha_tempo: Optional[float] = None
    milha_fc: Optional[float] = None
    step_fc: Optional[float] = None
    hrr_fc_pico: Optional[float] = None
    hrr_fc_1min: Optional[float] = None
    pa_rep_s: Optional[float] = None
    pa_rep_d: Optional[float] = None
    pa_pos_s: Optional[float] = None
    pa_pos_d: Optional[float] = None

class SalvarAvaliacaoSchema(BaseModel):
    secao: str
    anamnese: Optional[AnamnesesPayload] = None
    circunferencias: Optional[CircunferenciasPayload] = None
    composicao: Optional[ComposicaoPayload] = None
    testes_fisicos: Optional[TestesFisicosPayload] = None
    mmii: Optional[MMIIPayload] = None
    vo2_hrr: Optional[VO2HRRPayload] = None
    observacoes: Optional[str] = None

@router.post("/aluno/{aluno_id}/salvar-avaliacao")
def salvar_avaliacao_aluno(aluno_id: int, dados: SalvarAvaliacaoSchema, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.models import Aluno
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.anamnese import Anamnese
    from datetime import date

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")

    secao = dados.secao

    if secao == "anamnese" and dados.anamnese:
        an = dados.anamnese
        obs = f"Patologias: {an.patologias or '—'} | Dores: {an.dores or '—'} | Liberação: {an.liberacao_medica or '—'} | {an.observacoes or ''}"
        existente = db.query(Anamnese).filter(Anamnese.aluno_id == aluno_id).first()
        if existente:
            existente.objetivo_detalhado = an.objetivo
            existente.lesoes_anteriores = an.cirurgias
            existente.medicamentos_uso = an.medicamentos
            existente.observacoes = obs
        else:
            db.add(Anamnese(aluno_id=aluno_id, objetivo_detalhado=an.objetivo, lesoes_anteriores=an.cirurgias, medicamentos_uso=an.medicamentos, observacoes=obs))
        if an.peso: aluno.peso = an.peso
        db.commit()
        return {"mensagem": f"Anamnese salva para {aluno.nome}!", "secao": secao, "data": str(date.today())}

    av = db.query(AvaliacaoFisica).filter(AvaliacaoFisica.aluno_id == aluno_id, AvaliacaoFisica.data_avaliacao == date.today()).first()
    if not av:
        av = AvaliacaoFisica(aluno_id=aluno_id, data_avaliacao=date.today())
        db.add(av)

    if secao == "circunferencias" and dados.circunferencias:
        c = dados.circunferencias
        av.circ_pescoco = c.pescoco or av.circ_pescoco
        av.circ_torax = c.torax or av.circ_torax
        av.circ_cintura = c.cintura or av.circ_cintura
        av.circ_abdomen = c.abdomen or av.circ_abdomen
        av.circ_quadril = c.quadril or av.circ_quadril
        av.circ_braco_d_relaxado = c.braco_d or av.circ_braco_d_relaxado
        av.circ_braco_e_relaxado = c.braco_e or av.circ_braco_e_relaxado
        av.circ_antebraco_d = c.antebraco_d or av.circ_antebraco_d
        av.circ_antebraco_e = c.antebraco_e or av.circ_antebraco_e
        av.circ_coxa_d = c.coxa_d or av.circ_coxa_d
        av.circ_coxa_e = c.coxa_e or av.circ_coxa_e
        av.circ_panturrilha_d = c.panturrilha_d or av.circ_panturrilha_d
        av.circ_panturrilha_e = c.panturrilha_e or av.circ_panturrilha_e
        if av.circ_cintura and av.circ_quadril:
            av.relacao_cintura_quadril = round(av.circ_cintura / av.circ_quadril, 3)
            sexo = aluno.sexo.value if aluno.sexo else "masculino"
            rcq = av.relacao_cintura_quadril
            av.risco_cardiovascular = "Baixo" if (rcq < 0.90 if sexo == "masculino" else rcq < 0.80) else ("Moderado" if (rcq <= 0.95 if sexo == "masculino" else rcq <= 0.85) else "Alto")

    elif secao == "composicao" and dados.composicao:
        cp = dados.composicao
        av.peso = cp.peso or av.peso
        av.percentual_gordura = cp.gordura_pct or av.percentual_gordura
        if av.peso and av.percentual_gordura:
            av.massa_gorda_kg = round(av.peso * (av.percentual_gordura / 100), 2)
            av.massa_magra_kg = round(av.peso - av.massa_gorda_kg, 2)
        if av.peso and av.estatura:
            imc = av.peso / (av.estatura / 100) ** 2
            av.imc = round(imc, 2)
            av.classificacao_imc = "Abaixo do peso" if imc < 18.5 else "Peso normal" if imc < 25 else "Sobrepeso" if imc < 30 else "Obesidade Grau I" if imc < 35 else "Obesidade Grau II" if imc < 40 else "Obesidade Grau III"
        av.dc_peitoral = cp.d7_peit or cp.d3_d1 or av.dc_peitoral
        av.dc_abdominal = cp.d7_abdo or cp.d3_d2 or av.dc_abdominal
        av.dc_coxa = cp.d7_coxa or cp.d3_d3 or av.dc_coxa

    elif secao == "testes_fisicos" and dados.testes_fisicos:
        tf = dados.testes_fisicos
        av.teste_flexao_num = tf.flexao or av.teste_flexao_num
        av.teste_barra_num = tf.barra or av.teste_barra_num
        av.teste_flexibilidade_cm = tf.wells or av.teste_flexibilidade_cm

    elif secao == "mmii" and dados.mmii:
        av.observacoes = (av.observacoes or "") + f" | MMII 30s: {dados.mmii.repeticoes} reps"

    elif secao == "vo2_hrr" and dados.vo2_hrr:
        vh = dados.vo2_hrr
        vo2 = None
        if vh.cooper_dist:
            vo2 = max((vh.cooper_dist - 504.9) / 44.73, 0)
            av.teste_cooper_metros = vh.cooper_dist
        elif vh.step_fc:
            sexo = aluno.sexo.value if aluno.sexo else "masculino"
            vo2 = (65.81 - 0.1847*vh.step_fc) if sexo == "feminino" else (111.33 - 0.42*vh.step_fc)
        elif vh.milha_tempo and vh.milha_fc:
            vo2 = 132.853 - (0.0769*70) - (0.3877*30) + (6.315*1) - (3.2649*vh.milha_tempo) - (0.1565*vh.milha_fc)
        if vo2:
            av.vo2max = round(max(vo2, 10), 2)
            av.classificacao_vo2 = "Superior" if av.vo2max >= 56 else "Excelente" if av.vo2max >= 51 else "Bom" if av.vo2max >= 43 else "Regular" if av.vo2max >= 34 else "Fraco"
        if vh.hrr_fc_pico and vh.hrr_fc_1min:
            hrr = vh.hrr_fc_pico - vh.hrr_fc_1min
            av.observacoes = (av.observacoes or "") + f" | HRR 1min: {hrr} bpm"

    db.commit()
    return {"mensagem": f"Seção '{secao}' salva para {aluno.nome}!", "secao": secao, "data": str(date.today())}


@router.post("/aluno/{aluno_id}/postural")
async def postural_aluno(
    aluno_id: int,
    foto_frente: Optional[UploadFile] = File(None),
    foto_lado: Optional[UploadFile] = File(None),
    foto_costas: Optional[UploadFile] = File(None),
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    from app.models import Aluno
    from app.motor.ia_postural import analisar_postural
    from app.routers.avaliacao import AvaliacaoFisica
    import base64

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")

    async def to_b64(f):
        if not f: return None
        data = await f.read()
        return base64.b64encode(data).decode()

    f64 = await to_b64(foto_frente)
    l64 = await to_b64(foto_lado)
    c64 = await to_b64(foto_costas)

    if not any([f64, l64, c64]):
        raise HTTPException(status_code=400, detail="Envie ao menos uma foto")

    resultado = await analisar_postural(
        foto_frente=f64, foto_lado=l64, foto_costas=c64,
    )

    if resultado.erro:
        raise HTTPException(status_code=500, detail=resultado.erro)

    # Salva na avaliação
    av = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno_id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()

    if not av:
        av = AvaliacaoFisica(aluno_id=aluno_id)
        db.add(av)

    av.postura_cabeca   = resultado.cabeca
    av.postura_ombros   = resultado.ombros
    av.postura_coluna   = resultado.coluna
    av.postura_quadril  = resultado.quadril
    av.postura_joelhos  = resultado.joelhos
    av.postura_pes      = resultado.pes
    db.commit()

    return {
        "aluno": aluno.nome,
        "desvios": {"cabeca": resultado.cabeca, "ombros": resultado.ombros, "coluna": resultado.coluna, "quadril": resultado.quadril, "joelhos": resultado.joelhos, "pes": resultado.pes},
        "observacoes": resultado.observacoes,
        "recomendacoes": resultado.recomendacoes or []
    }

@router.post("/white-label")
async def salvar_white_label(
    nome: str = Form(None),
    slogan: str = Form(None),
    logo: UploadFile = File(None),
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    import os, shutil
    if logo:
        import base64, io
        from PIL import Image
        conteudo = logo.file.read()
        img = Image.open(io.BytesIO(conteudo)).convert('RGBA')
        img.thumbnail((200, 200))
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        personal.logo_url = f"data:image/png;base64,{b64}"
    if nome:
        personal.nome_empresa = nome
    if slogan:
        personal.slogan = slogan
    db.commit()
    return {"status": "ok", "logo_url": personal.logo_url if logo else None}


# ──────────────────────────────────────────────────────────────────────────────
# AULAS — Check-in diario do personal
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/aulas/checkin")
def fazer_checkin_aula(
    payload: dict,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Marca presenca de 1 aluno em 1 dia especifico.
    Body: { "aluno_id": 1, "data": "2026-04-27", "observacoes": "" }
    """
    from app.routers.treino import PresencaTreino
    from datetime import date as date_cls
    
    aluno_id = payload.get("aluno_id")
    data_str = payload.get("data")
    observacoes = payload.get("observacoes", "")
    
    if not aluno_id or not data_str:
        raise HTTPException(400, "aluno_id e data sao obrigatorios")
    
    # Verifica se aluno pertence ao personal
    aluno = db.query(Aluno).filter(
        Aluno.id == aluno_id,
        Aluno.personal_id == personal.id
    ).first()
    if not aluno:
        raise HTTPException(404, "Aluno nao encontrado")
    
    # Converte data
    try:
        data_aula = date_cls.fromisoformat(data_str)
    except:
        raise HTTPException(400, "Data invalida (use YYYY-MM-DD)")
    
    # Verifica se ja existe checkin nesse dia
    ja_existe = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno_id,
        PresencaTreino.data == data_aula
    ).first()
    
    if ja_existe:
        raise HTTPException(400, f"{aluno.nome} ja tem check-in nesse dia")
    
    # Cria presenca
    nova = PresencaTreino(
        aluno_id=aluno_id,
        data=data_aula,
        presente=True,
        observacoes=observacoes or None
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    
    return {
        "id": nova.id,
        "aluno_id": aluno_id,
        "aluno_nome": aluno.nome,
        "data": data_aula.isoformat(),
        "ok": True
    }


@router.get("/aulas/dia")
def listar_aulas_do_dia(
    data: str,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Lista todos os check-ins de aulas de um dia especifico.
    Query param: ?data=2026-04-27
    """
    from app.routers.treino import PresencaTreino
    from datetime import date as date_cls
    
    try:
        data_aula = date_cls.fromisoformat(data)
    except:
        raise HTTPException(400, "Data invalida (use YYYY-MM-DD)")
    
    # Busca todas as presencas do dia para alunos desse personal
    presencas = db.query(PresencaTreino).join(Aluno).filter(
        PresencaTreino.data == data_aula,
        Aluno.personal_id == personal.id
    ).all()
    
    resultado = []
    for p in presencas:
        aluno = db.query(Aluno).filter(Aluno.id == p.aluno_id).first()
        if aluno:
            resultado.append({
                "id": p.id,
                "aluno_id": p.aluno_id,
                "aluno_nome": aluno.nome,
                "data": p.data.isoformat(),
                "observacoes": p.observacoes,
                "criado_em": p.criado_em.isoformat() if p.criado_em else None
            })
    
    return {
        "data": data_aula.isoformat(),
        "total": len(resultado),
        "aulas": resultado
    }


@router.delete("/aulas/checkin/{presenca_id}")
def remover_checkin(
    presenca_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Remove um check-in (caso de erro)."""
    from app.routers.treino import PresencaTreino
    
    presenca = db.query(PresencaTreino).filter(
        PresencaTreino.id == presenca_id
    ).first()
    
    if not presenca:
        raise HTTPException(404, "Check-in nao encontrado")
    
    # Verifica se aluno e desse personal
    aluno = db.query(Aluno).filter(
        Aluno.id == presenca.aluno_id,
        Aluno.personal_id == personal.id
    ).first()
    
    if not aluno:
        raise HTTPException(403, "Sem permissao")
    
    db.delete(presenca)
    db.commit()
    
    return {"ok": True}


@router.get("/aulas/mes")
def aulas_do_mes(
    ano: int,
    mes: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Resumo de aulas do mes - para calendario visual.
    Query: ?ano=2026&mes=4
    """
    from app.routers.treino import PresencaTreino
    from datetime import date as date_cls, timedelta
    from calendar import monthrange
    
    if mes < 1 or mes > 12:
        raise HTTPException(400, "Mes invalido")
    
    primeiro_dia = date_cls(ano, mes, 1)
    ultimo_dia = date_cls(ano, mes, monthrange(ano, mes)[1])
    
    presencas = db.query(PresencaTreino).join(Aluno).filter(
        PresencaTreino.data >= primeiro_dia,
        PresencaTreino.data <= ultimo_dia,
        Aluno.personal_id == personal.id
    ).all()
    
    # Agrupa por dia
    por_dia = {}
    for p in presencas:
        dia = p.data.isoformat()
        if dia not in por_dia:
            por_dia[dia] = 0
        por_dia[dia] += 1
    
    return {
        "ano": ano,
        "mes": mes,
        "total_aulas": len(presencas),
        "por_dia": por_dia
    }



# ──────────────────────────────────────────────────────────────────────────────
# FECHAMENTOS — Lista de cobrancas pendentes
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/financeiro/fechamentos-pendentes")
def listar_fechamentos_pendentes(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    from app.routers.treino import PresencaTreino
    from datetime import date as date_cls, timedelta
    from calendar import monthrange
    
    hoje = date_cls.today()
    
    alunos = db.query(Aluno).filter(
        Aluno.personal_id == personal.id,
        Aluno.ativo == True
    ).all()
    
    fechamentos = []
    
    for aluno in alunos:
        ciclo = aluno.ciclo_cobranca or "mensal"
        dia_fechamento = aluno.dia_fechamento or 30
        dias_vencimento = aluno.dias_vencimento or 5
        valor_mensal = float(aluno.valor_mensal) if aluno.valor_mensal else 0
        valor_aula = float(aluno.valor_aula) if aluno.valor_aula else 0
        
        ultimo_dia_mes = monthrange(hoje.year, hoje.month)[1]
        dia_real = min(dia_fechamento, ultimo_dia_mes)
        data_fechamento = date_cls(hoje.year, hoje.month, dia_real)
        
        if data_fechamento < hoje:
            if hoje.month == 12:
                data_fechamento = date_cls(hoje.year + 1, 1, min(dia_fechamento, 31))
            else:
                proximo_mes = hoje.month + 1
                ultimo_dia_proximo = monthrange(hoje.year, proximo_mes)[1]
                data_fechamento = date_cls(hoje.year, proximo_mes, min(dia_fechamento, ultimo_dia_proximo))
        
        data_vencimento = data_fechamento + timedelta(days=dias_vencimento)
        
        primeiro_dia_mes = date_cls(hoje.year, hoje.month, 1)
        aulas_dadas = db.query(PresencaTreino).filter(
            PresencaTreino.aluno_id == aluno.id,
            PresencaTreino.data >= primeiro_dia_mes,
            PresencaTreino.data <= hoje
        ).count()
        
        if ciclo == "por_aula_mensal":
            valor_total = aulas_dadas * valor_aula
        else:
            valor_total = valor_mensal
        
        dias_para_fechar = (data_fechamento - hoje).days
        if dias_para_fechar == 0:
            status = "vence_hoje"
            cor = "vermelho"
        elif dias_para_fechar <= 3:
            status = "em_breve"
            cor = "amarelo"
        else:
            status = "futuro"
            cor = "verde"
        
        if valor_total > 0 or ciclo == "por_aula_mensal":
            fechamentos.append({
                "aluno_id": aluno.id,
                "aluno_nome": aluno.nome,
                "ciclo_cobranca": ciclo,
                "valor_aula": valor_aula,
                "valor_mensal": valor_mensal,
                "aulas_dadas": aulas_dadas,
                "valor_total": valor_total,
                "data_fechamento": data_fechamento.isoformat(),
                "data_vencimento": data_vencimento.isoformat(),
                "dias_para_fechar": dias_para_fechar,
                "status": status,
                "cor": cor
            })
    
    fechamentos.sort(key=lambda x: x["dias_para_fechar"])
    
    return {
        "total": len(fechamentos),
        "data_consulta": hoje.isoformat(),
        "fechamentos": fechamentos
    }



# ──────────────────────────────────────────────────────────────────────────────
# FECHAR MES — Cria cobranca real e gera link Stripe
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/financeiro/fechar-mes-aluno/{aluno_id}")
def fechar_mes_aluno(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Fecha o mes para um aluno especifico.
    Cria cobranca no banco e retorna info pra cobranca via Stripe.
    """
    from app.routers.treino import PresencaTreino
    from datetime import date as date_cls, timedelta, datetime
    from calendar import monthrange
    from sqlalchemy import text
    
    hoje = date_cls.today()
    
    # Busca aluno
    aluno = db.query(Aluno).filter(
        Aluno.id == aluno_id,
        Aluno.personal_id == personal.id
    ).first()
    
    if not aluno:
        raise HTTPException(404, "Aluno nao encontrado")
    
    if not aluno.email:
        raise HTTPException(400, "Aluno precisa ter email cadastrado")
    
    ciclo = aluno.ciclo_cobranca or "mensal"
    valor_mensal = float(aluno.valor_mensal) if aluno.valor_mensal else 0
    valor_aula = float(aluno.valor_aula) if aluno.valor_aula else 0
    dias_vencimento = aluno.dias_vencimento or 5
    
    # Conta aulas do mes
    primeiro_dia_mes = date_cls(hoje.year, hoje.month, 1)
    aulas_dadas = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno.id,
        PresencaTreino.data >= primeiro_dia_mes,
        PresencaTreino.data <= hoje
    ).count()
    
    # Calcula valor
    if ciclo == "por_aula_mensal":
        valor_total = aulas_dadas * valor_aula
        descricao = f"{aulas_dadas} aulas em {hoje.strftime('%m/%Y')}"
    else:
        valor_total = valor_mensal
        descricao = f"Mensalidade {hoje.strftime('%m/%Y')}"
    
    if valor_total <= 0:
        raise HTTPException(400, "Valor a cobrar e zero. Verifique aulas dadas ou valor configurado")
    
    # Data de vencimento
    data_vencimento = hoje + timedelta(days=dias_vencimento)
    
    # Verifica se ja existe cobranca em aberto deste mes
    sql_check = text("""
        SELECT id FROM cobrancas 
        WHERE aluno_id = :aluno_id 
        AND status IN ('pendente', 'enviada')
        AND EXTRACT(MONTH FROM data_fechamento) = :mes
        AND EXTRACT(YEAR FROM data_fechamento) = :ano
    """)
    existe = db.execute(sql_check, {
        "aluno_id": aluno.id,
        "mes": hoje.month,
        "ano": hoje.year
    }).fetchone()
    
    if existe:
        raise HTTPException(400, "Ja existe cobranca pendente para esse aluno neste mes")
    
    # Cria cobranca no banco
    sql_insert = text("""
        INSERT INTO cobrancas (
            aluno_id, valor, data_fechamento, data_vencimento, 
            status, aulas_periodo, descricao, criado_em, atualizado_em
        ) VALUES (
            :aluno_id, :valor, :data_fechamento, :data_vencimento,
            'pendente', :aulas, :descricao, NOW(), NOW()
        ) RETURNING id
    """)
    
    result = db.execute(sql_insert, {
        "aluno_id": aluno.id,
        "valor": valor_total,
        "data_fechamento": hoje,
        "data_vencimento": data_vencimento,
        "aulas": aulas_dadas,
        "descricao": descricao
    })
    cobranca_id = result.fetchone()[0]
    db.commit()
    
    return {
        "ok": True,
        "cobranca_id": cobranca_id,
        "aluno_nome": aluno.nome,
        "aluno_email": aluno.email,
        "valor": valor_total,
        "descricao": descricao,
        "data_vencimento": data_vencimento.isoformat(),
        "aulas_dadas": aulas_dadas,
        "ciclo": ciclo,
        "proximo_passo": "Cobranca registrada! Sistema enviara link de pagamento por email."
    }


@router.get("/financeiro/cobrancas-aluno/{aluno_id}")
def listar_cobrancas_aluno(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Lista todas as cobrancas de um aluno."""
    from sqlalchemy import text
    
    aluno = db.query(Aluno).filter(
        Aluno.id == aluno_id,
        Aluno.personal_id == personal.id
    ).first()
    
    if not aluno:
        raise HTTPException(404, "Aluno nao encontrado")
    
    sql = text("""
        SELECT id, valor, data_fechamento, data_vencimento, data_pagamento,
               status, aulas_periodo, descricao, criado_em
        FROM cobrancas
        WHERE aluno_id = :aluno_id
        ORDER BY data_fechamento DESC
        LIMIT 12
    """)
    
    rows = db.execute(sql, {"aluno_id": aluno_id}).fetchall()
    
    cobrancas = []
    for r in rows:
        cobrancas.append({
            "id": r[0],
            "valor": float(r[1]) if r[1] else 0,
            "data_fechamento": r[2].isoformat() if r[2] else None,
            "data_vencimento": r[3].isoformat() if r[3] else None,
            "data_pagamento": r[4].isoformat() if r[4] else None,
            "status": r[5],
            "aulas_periodo": r[6],
            "descricao": r[7],
            "criado_em": r[8].isoformat() if r[8] else None
        })
    
    return {
        "aluno_id": aluno_id,
        "aluno_nome": aluno.nome,
        "total": len(cobrancas),
        "cobrancas": cobrancas
    }



# ──────────────────────────────────────────────────────────────────────────────
# STRIPE — Gera link de pagamento para cobranca
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/financeiro/gerar-link-pagamento/{cobranca_id}")
def gerar_link_pagamento(
    cobranca_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Gera link Stripe para pagamento de uma cobranca especifica.
    Suporta: cartao, PIX, boleto.
    """
    import stripe
    from app.config import settings
    from sqlalchemy import text
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Busca cobranca
    sql = text("""
        SELECT c.id, c.aluno_id, c.valor, c.descricao, c.data_vencimento, c.status,
               a.nome, a.email, a.cpf
        FROM cobrancas c
        JOIN alunos a ON a.id = c.aluno_id
        WHERE c.id = :cid AND a.personal_id = :pid
    """)
    
    row = db.execute(sql, {"cid": cobranca_id, "pid": personal.id}).fetchone()
    
    if not row:
        raise HTTPException(404, "Cobranca nao encontrada")
    
    if row[5] not in ("pendente", "enviada"):
        raise HTTPException(400, f"Cobranca esta com status: {row[5]}")
    
    valor_centavos = int(float(row[2]) * 100)
    descricao = row[3]
    aluno_nome = row[6]
    aluno_email = row[7]
    
    try:
        # Cria sessao Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "boleto"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": f"Personal Training - {aluno_nome}",
                        "description": descricao
                    },
                    "unit_amount": valor_centavos
                },
                "quantity": 1
            }],
            mode="payment",
            customer_email=aluno_email,
            metadata={
                "cobranca_id": str(cobranca_id),
                "aluno_id": str(row[1]),
                "personal_id": str(personal.id),
                "tipo": "cobranca_mensal"
            },
            success_url=f"https://www.aurumsc.com.br/aluno?pagamento=sucesso&cobranca={cobranca_id}",
            cancel_url=f"https://www.aurumsc.com.br/aluno?pagamento=cancelado&cobranca={cobranca_id}",
            payment_intent_data={
                "description": f"{descricao} - {aluno_nome}",
                "metadata": {"cobranca_id": str(cobranca_id)}
            }
        )
        
        # Salva session_id na cobranca
        update_sql = text("""
            UPDATE cobrancas 
            SET stripe_invoice_id = :sid, status = :st, atualizado_em = NOW()
            WHERE id = :cid
        """)
        db.execute(update_sql, {
            "sid": session.id,
            "st": "enviada",
            "cid": cobranca_id
        })
        db.commit()
        
        return {
            "ok": True,
            "url_pagamento": session.url,
            "session_id": session.id,
            "valor": float(row[2]),
            "aluno_nome": aluno_nome,
            "aluno_email": aluno_email,
            "descricao": descricao
        }
        
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar sessao Stripe: {str(e)}")

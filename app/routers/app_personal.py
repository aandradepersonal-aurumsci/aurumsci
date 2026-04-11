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
from app.models import Personal
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

    return {
        "total_alunos": total_alunos,
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
        "postural": {"cabeca": aval.postura_cabeca if aval else None, "ombros": aval.postura_ombros if aval else None, "coluna": aval.postura_coluna if aval else None} if aval else None
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
        nome_aluno=aluno.nome, idade=None, sexo=aluno.sexo.value if aluno.sexo else "masculino"
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

    if resultado.desvios:
        av.postura_cabeca   = resultado.desvios.get("cabeca")
        av.postura_ombros   = resultado.desvios.get("ombros")
        av.postura_coluna   = resultado.desvios.get("coluna")
        av.postura_quadril  = resultado.desvios.get("quadril")
        av.postura_joelhos  = resultado.desvios.get("joelhos")
        av.postura_pes      = resultado.desvios.get("pes")
    av.postura_observacoes = resultado.observacoes
    db.commit()

    return {
        "aluno": aluno.nome,
        "desvios": resultado.desvios,
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
        import base64
        conteudo = logo.file.read()
        # sync read ok for small files
        ext = logo.filename.split('.')[-1].lower()
        b64 = base64.b64encode(conteudo).decode('utf-8')
        personal.logo_url = f"data:image/{ext};base64,{b64}"
    if nome:
        personal.nome_empresa = nome
    if slogan:
        personal.slogan = slogan
    db.commit()
    return {"status": "ok", "logo_url": personal.logo_url if logo else None}

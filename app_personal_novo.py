"""
Router — App Personal (expandido)
"""
from fastapi import APIRouter, Depends, HTTPException
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
    from app.routers.financeiro import Pagamento

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
        "alunos_recentes": recentes
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
    """Lista todos os exercícios do banco para o montador de treino."""
    from app.routers.treino import Exercicio
    exercicios = db.query(Exercicio).order_by(Exercicio.grupo_muscular, Exercicio.nome).all()
    return {"exercicios": [{
        "id": e.id,
        "nome": e.nome,
        "grupo_muscular": e.grupo_muscular,
        "equipamento": e.equipamento,
        "descricao": e.descricao,
        "video_url": e.video_url,
    } for e in exercicios]}


class SessaoTreinoSchema(BaseModel):
    nome: str
    exercicios: List[dict]

class SalvarTreinoSchema(BaseModel):
    objetivo: str
    nivel: str = "intermediario"
    dias_disponiveis: int = 3
    sessoes: List[SessaoTreinoSchema]

@router.post("/aluno/{aluno_id}/salvar-treino")
def salvar_treino_aluno(aluno_id: int, dados: SalvarTreinoSchema, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    """Personal monta e salva treino para o aluno."""
    from app.models import Aluno
    from app.routers.treino import PlanoTreino, SessaoTreino, ExercicioSessao
    import json

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.personal_id == personal.id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Desativa plano anterior
    db.query(PlanoTreino).filter(PlanoTreino.aluno_id == aluno_id, PlanoTreino.ativo == True).update({"ativo": False})

    # Cria novo plano
    plano = PlanoTreino(
        aluno_id=aluno_id,
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

    # Cria sessões e exercícios
    for i, sessao_dados in enumerate(dados.sessoes):
        sessao = SessaoTreino(plano_id=plano.id, nome=sessao_dados.nome, dia_semana=i+1)
        db.add(sessao)
        db.flush()
        for j, ex in enumerate(sessao_dados.exercicios):
            ex_sessao = ExercicioSessao(
                sessao_id=sessao.id,
                exercicio_id=ex.get("exercicio_id"),
                ordem=j+1,
                series=ex.get("series", 3),
                repeticoes=str(ex.get("repeticoes", "10-12")),
                carga_kg=0.0,
                tempo_descanso_seg=ex.get("tempo_descanso_seg", 90),
            )
            db.add(ex_sessao)

    db.commit()
    return {"mensagem": f"Treino salvo para {aluno.nome}!", "plano_id": plano.id}

"""
Router — Treinos
POST /treino/exercicios              → criar exercício na biblioteca
GET  /treino/exercicios              → listar exercícios
POST /treino/plano                   → criar plano + periodização automática
GET  /treino/plano/aluno/{aluno_id}  → listar planos do aluno
GET  /treino/plano/{id}              → detalhe do plano
POST /treino/presenca                → registrar presença
GET  /treino/presenca/aluno/{id}     → histórico de presenças
GET  /treino/alertas/aluno/{id}      → alertas automáticos do aluno

🧠 Integrado com AurumSci Motor v1
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON

from app.database import get_db
from app.models import Base, Aluno, Personal
from app.utils.auth import get_personal_atual
from app.schemas.treino import (
    ExercicioCriar, ExercicioResposta,
    PlanoTreinoCriar,  # noqa: F401
    PresencaCriar, PresencaResposta,
    ExercicioSessaoCriar,
)

# 🧠 Motor AurumSci v1
from app.motor.periodizacao import gerar_periodizacao, periodizacao_to_dict
from app.motor.calculos import gerar_alertas_aluno

router = APIRouter(prefix="/treino", tags=["Treinos"])


# ── Modelos ───────────────────────────────────────────────────────────────────

class Exercicio(Base):
    __tablename__ = "exercicios"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    grupo_muscular = Column(String(100))
    equipamento = Column(String(100))
    descricao = Column(Text)
    execucao = Column(Text)
    video_url = Column(String(300))
    personal_id = Column(Integer, ForeignKey("personals.id"))
    criado_em = Column(DateTime, default=datetime.utcnow)


class PlanoTreino(Base):
    __tablename__ = "planos_treino"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    personal_id = Column(Integer, ForeignKey("personals.id"), nullable=False)
    nome = Column(String(150))
    objetivo = Column(String(100))
    nivel = Column(String(50))
    dias_semana = Column(Integer, default=3)
    semanas_total = Column(Integer, default=12)
    tipo_periodizacao = Column(String(50), default="linear")
    data_inicio = Column(Date)
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text)
    periodizacao = Column(JSON)
    criado_em = Column(DateTime, default=datetime.utcnow)


class SessaoTreino(Base):
    __tablename__ = "sessoes_treino"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    plano_id = Column(Integer, ForeignKey("planos_treino.id"), nullable=False)
    nome = Column(String(50))
    dia_semana = Column(Integer)
    grupos_musculares = Column(String(200))
    criado_em = Column(DateTime, default=datetime.utcnow)


class ExercicioSessao(Base):
    __tablename__ = "exercicios_sessao"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    sessao_id = Column(Integer, ForeignKey("sessoes_treino.id"), nullable=False)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    ordem = Column(Integer, default=1)
    series = Column(Integer, default=3)
    repeticoes = Column(String(20), default="10-12")
    carga_kg = Column(Float)
    tempo_descanso_seg = Column(Integer, default=60)
    tecnica_especial = Column(String(100))
    observacoes = Column(Text)


class PresencaTreino(Base):
    __tablename__ = "presencas"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    sessao_id = Column(Integer, ForeignKey("sessoes_treino.id"), nullable=True)
    data = Column(Date, default=date.today)
    presente = Column(Boolean, default=True)
    duracao_minutos = Column(Integer)
    sensacao_subjetiva = Column(Integer)
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_aluno(aluno_id, personal_id, db):
    aluno = db.query(Aluno).filter(
        Aluno.id == aluno_id,
        Aluno.personal_id == personal_id
    ).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return aluno


# ── Exercícios ────────────────────────────────────────────────────────────────

@router.post("/exercicios", response_model=ExercicioResposta, status_code=201)
def criar_exercicio(
    dados: ExercicioCriar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    ex = Exercicio(**dados.model_dump(), personal_id=personal.id)
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.get("/exercicios", response_model=List[ExercicioResposta])
def listar_exercicios(
    grupo: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    query = db.query(Exercicio)
    if grupo:
        query = query.filter(Exercicio.grupo_muscular.ilike(f"%{grupo}%"))
    if busca:
        query = query.filter(Exercicio.nome.ilike(f"%{busca}%"))
    return query.order_by(Exercicio.nome).all()


# ── Plano de treino ───────────────────────────────────────────────────────────

@router.post("/plano", status_code=201)
def criar_plano(
    dados: PlanoTreinoCriar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    get_aluno(dados.aluno_id, personal.id, db)

    # 🧠 Motor AurumSci — Periodização com descrições educativas e datas reais
    periodizacao_dict = None
    if dados.gerar_automatico:
        p = gerar_periodizacao(
            objetivo=dados.objetivo,
            nivel=dados.nivel,
            dias_semana=dados.dias_semana,
            semanas_total=dados.semanas_total,
            data_inicio=dados.data_inicio or date.today(),
        )
        periodizacao_dict = periodizacao_to_dict(p)

    plano = PlanoTreino(
        aluno_id=dados.aluno_id,
        personal_id=personal.id,
        nome=dados.nome,
        objetivo=dados.objetivo,
        nivel=dados.nivel,
        dias_semana=dados.dias_semana,
        semanas_total=dados.semanas_total,
        tipo_periodizacao=dados.tipo_periodizacao,
        data_inicio=dados.data_inicio or date.today(),
        observacoes=dados.observacoes,
        periodizacao=periodizacao_dict,
    )
    db.add(plano)
    db.commit()
    db.refresh(plano)

    # Cria sessões automaticamente baseadas na divisão do motor
    if periodizacao_dict:
        for i, nome_sessao in enumerate(periodizacao_dict.get("divisao_sessoes", [])):
            sessao = SessaoTreino(
                plano_id=plano.id,
                nome=nome_sessao,
                dia_semana=i,
            )
            db.add(sessao)
    db.commit()

    sessoes = db.query(SessaoTreino).filter(SessaoTreino.plano_id == plano.id).all()

    return {
        "id": plano.id,
        "aluno_id": plano.aluno_id,
        "nome": plano.nome,
        "objetivo": plano.objetivo,
        "nivel": plano.nivel,
        "dias_semana": plano.dias_semana,
        "semanas_total": plano.semanas_total,
        "tipo_periodizacao": plano.tipo_periodizacao,
        "data_inicio": str(plano.data_inicio),
        "ativo": plano.ativo,
        "sessoes": [{"id": s.id, "nome": s.nome, "dia_semana": s.dia_semana} for s in sessoes],
        "periodizacao": periodizacao_dict,
    }


@router.get("/plano/aluno/{aluno_id}")
def listar_planos(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    get_aluno(aluno_id, personal.id, db)
    planos = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno_id,
        PlanoTreino.personal_id == personal.id
    ).order_by(PlanoTreino.criado_em.desc()).all()
    return planos


@router.get("/plano/{plano_id}")
def detalhe_plano(
    plano_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    plano = db.query(PlanoTreino).filter(
        PlanoTreino.id == plano_id,
        PlanoTreino.personal_id == personal.id
    ).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    sessoes = db.query(SessaoTreino).filter(SessaoTreino.plano_id == plano_id).all()
    sessoes_data = []
    for s in sessoes:
        exercicios = db.query(ExercicioSessao).filter(ExercicioSessao.sessao_id == s.id).all()
        exs = []
        for e in exercicios:
            ex = db.query(Exercicio).filter(Exercicio.id == e.exercicio_id).first()
            exs.append({
                "id": e.id,
                "exercicio_id": e.exercicio_id,
                "nome_exercicio": ex.nome if ex else None,
                "series": e.series,
                "repeticoes": e.repeticoes,
                "carga_kg": e.carga_kg,
                "tempo_descanso_seg": e.tempo_descanso_seg,
            })
        sessoes_data.append({
            "id": s.id,
            "nome": s.nome,
            "dia_semana": s.dia_semana,
            "exercicios": exs
        })

    return {
        "id": plano.id,
        "nome": plano.nome,
        "objetivo": plano.objetivo,
        "nivel": plano.nivel,
        "dias_semana": plano.dias_semana,
        "semanas_total": plano.semanas_total,
        "data_inicio": str(plano.data_inicio) if plano.data_inicio else None,
        "ativo": plano.ativo,
        "sessoes": sessoes_data,
        "periodizacao": plano.periodizacao,
    }


# ── Adicionar exercício na sessão ─────────────────────────────────────────────

@router.post("/sessao/{sessao_id}/exercicio", status_code=201)
def adicionar_exercicio_sessao(
    sessao_id: int,
    dados: ExercicioSessaoCriar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    sessao = db.query(SessaoTreino).filter(SessaoTreino.id == sessao_id).first()
    if not sessao:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")
    ex_sessao = ExercicioSessao(sessao_id=sessao_id, **dados.model_dump())
    db.add(ex_sessao)
    db.commit()
    db.refresh(ex_sessao)
    return ex_sessao


# ── Presença ──────────────────────────────────────────────────────────────────

@router.post("/presenca", response_model=PresencaResposta, status_code=201)
def registrar_presenca(
    dados: PresencaCriar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    get_aluno(dados.aluno_id, personal.id, db)
    presenca = PresencaTreino(**dados.model_dump())
    if not presenca.data:
        presenca.data = date.today()
    db.add(presenca)
    db.commit()
    db.refresh(presenca)
    return presenca


@router.get("/presenca/aluno/{aluno_id}")
def historico_presenca(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    get_aluno(aluno_id, personal.id, db)
    presencas = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno_id
    ).order_by(PresencaTreino.data.desc()).all()

    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    frequencia_pct = round((presentes / total * 100), 1) if total > 0 else 0

    # 🧠 Motor — Alertas de frequência
    alertas = gerar_alertas_aluno(
        ultima_avaliacao_dias=999,
        frequencia_pct=frequencia_pct,
    )

    return {
        "total_treinos": total,
        "presentes": presentes,
        "faltas": total - presentes,
        "frequencia_pct": frequencia_pct,
        "alertas": [
            {"tipo": a.tipo, "prioridade": a.prioridade, "mensagem": a.mensagem}
            for a in alertas if a.tipo == "frequencia"
        ],
        "historico": [
            {
                "id": p.id,
                "data": str(p.data),
                "presente": p.presente,
                "duracao": p.duracao_minutos,
                "pse": p.sensacao_subjetiva,
                "observacoes": p.observacoes,
            }
            for p in presencas
        ],
    }


# ── Alertas automáticos do aluno ──────────────────────────────────────────────

@router.get("/alertas/aluno/{aluno_id}")
def alertas_aluno(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    🧠 Motor AurumSci — Alertas automáticos para o personal
    Verifica: frequência baixa, reavaliação pendente, pagamento atrasado
    """
    from app.routers.financeiro import Pagamento, calc_status as cs
    from app.routers.avaliacao import AvaliacaoFisica
    from datetime import date as date_type

    get_aluno(aluno_id, personal.id, db)

    # Frequência
    presencas = db.query(PresencaTreino).filter(PresencaTreino.aluno_id == aluno_id).all()
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    frequencia_pct = round((presentes / total * 100), 1) if total > 0 else 0

    # Última avaliação
    ultima_av = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno_id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
    dias_sem_avaliacao = 999
    if ultima_av and ultima_av.data_avaliacao:
        dias_sem_avaliacao = (date_type.today() - ultima_av.data_avaliacao).days

    # Pagamento atrasado
    pagamentos = db.query(Pagamento).filter(Pagamento.aluno_id == aluno_id).all()
    pagamento_atrasado = any(cs(p) == "atrasado" for p in pagamentos)

    # 🧠 Motor gera os alertas
    alertas = gerar_alertas_aluno(
        ultima_avaliacao_dias=dias_sem_avaliacao,
        frequencia_pct=frequencia_pct,
        pagamento_atrasado=pagamento_atrasado,
    )

    return {
        "aluno_id": aluno_id,
        "frequencia_pct": frequencia_pct,
        "dias_sem_avaliacao": dias_sem_avaliacao,
        "pagamento_atrasado": pagamento_atrasado,
        "total_alertas": len(alertas),
        "alertas": [
            {
                "tipo": a.tipo,
                "prioridade": a.prioridade,
                "mensagem": a.mensagem,
                "dias_restantes": a.dias_restantes,
            }
            for a in alertas
        ],
    }

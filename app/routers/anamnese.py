"""
Router — Anamnese
GET    /anamnese/aluno/{aluno_id}     → buscar anamnese do aluno
POST   /anamnese                      → criar anamnese
PUT    /anamnese/{id}                 → atualizar anamnese
"""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from datetime import datetime

from app.database import get_db
from app.models import Base, Aluno, Personal
from app.utils.auth import get_personal_atual
from app.schemas.anamnese import AnamneseCriar, AnamnesesAtualizar, AnamnesesResposta

router = APIRouter(prefix="/anamnese", tags=["Anamnese"])


# ── Modelo inline (evita importação circular) ─────────────────────────────────

class Anamnese(Base):
    __tablename__ = "anamneses"
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    data_avaliacao = Column(Date, default=date.today)
    doencas_cronicas = Column(Text)
    medicamentos_uso = Column(Text)
    medicamentos_controlados = Column(Text)
    cirurgias = Column(Text)
    lesoes_anteriores = Column(Text)
    historico_familiar = Column(Text)
    dor_cervical = Column(Boolean, default=False)
    dor_ombro = Column(Boolean, default=False)
    dor_cotovelo = Column(Boolean, default=False)
    dor_punho = Column(Boolean, default=False)
    dor_lombar = Column(Boolean, default=False)
    dor_quadril = Column(Boolean, default=False)
    dor_joelho = Column(Boolean, default=False)
    dor_tornozelo = Column(Boolean, default=False)
    descricao_dores = Column(Text)
    fumante = Column(Boolean, default=False)
    ex_fumante = Column(Boolean, default=False)
    consumo_alcool = Column(Boolean, default=False)
    frequencia_alcool = Column(String(50))
    pratica_atividade = Column(Boolean, default=False)
    modalidade_atual = Column(String(150))
    frequencia_atual = Column(Integer)
    tempo_pratica_meses = Column(Integer)
    dias_disponiveis = Column(Integer)
    tempo_por_sessao = Column(Integer)
    local_treino = Column(String(100))
    objetivo_detalhado = Column(Text)
    ja_treinou_antes = Column(Boolean, default=False)
    experiencia_anterior = Column(Text)
    horas_sono = Column(Float)
    nivel_estresse = Column(Integer)
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)


def verificar_aluno(aluno_id: int, personal_id: int, db: Session) -> Aluno:
    aluno = db.query(Aluno).filter(
        Aluno.id == aluno_id,
        Aluno.personal_id == personal_id
    ).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


@router.post("", response_model=AnamnesesResposta, status_code=201)
def criar(
    dados: AnamneseCriar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    verificar_aluno(dados.aluno_id, personal.id, db)

    # Verifica se já existe anamnese — substitui
    existente = db.query(Anamnese).filter(Anamnese.aluno_id == dados.aluno_id).first()
    if existente:
        for campo, valor in dados.model_dump().items():
            setattr(existente, campo, valor)
        db.commit()
        db.refresh(existente)
        return existente

    anamnese = Anamnese(**dados.model_dump())
    db.add(anamnese)
    db.commit()
    db.refresh(anamnese)
    return anamnese


@router.get("/aluno/{aluno_id}", response_model=AnamnesesResposta)
def buscar(
    aluno_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    verificar_aluno(aluno_id, personal.id, db)
    anamnese = db.query(Anamnese).filter(Anamnese.aluno_id == aluno_id).first()
    if not anamnese:
        raise HTTPException(status_code=404, detail="Anamnese não encontrada")
    return anamnese


@router.put("/{anamnese_id}", response_model=AnamnesesResposta)
def atualizar(
    anamnese_id: int,
    dados: AnamnesesAtualizar,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    anamnese = db.query(Anamnese).filter(Anamnese.id == anamnese_id).first()
    if not anamnese:
        raise HTTPException(status_code=404, detail="Anamnese não encontrada")
    verificar_aluno(anamnese.aluno_id, personal.id, db)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(anamnese, campo, valor)
    db.commit()
    db.refresh(anamnese)
    return anamnese


@router.delete("/{anamnese_id}")
def deletar(
    anamnese_id: int,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    anamnese = db.query(Anamnese).filter(Anamnese.id == anamnese_id).first()
    if not anamnese:
        raise HTTPException(status_code=404, detail="Anamnese não encontrada")
    verificar_aluno(anamnese.aluno_id, personal.id, db)
    db.delete(anamnese)
    db.commit()
    return {"mensagem": "Anamnese removida com sucesso"}


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS PARA O ALUNO LOGADO (ele mesmo preenche sua anamnese)
# Reusa a mesma tabela "anamneses" do PRO
# ═══════════════════════════════════════════════════════════════════════════
from app.routers.portal_aluno import get_aluno_logado

@router.get("/minha", tags=["Anamnese - Aluno"])
def aluno_buscar_propria(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Aluno busca a propria anamnese."""
    anamnese = db.query(Anamnese).filter(Anamnese.aluno_id == aluno.id).first()
    if not anamnese:
        return {"existe": False, "anamnese": None}
    return {
        "existe": True,
        "id": anamnese.id,
        "doencas_cronicas": anamnese.doencas_cronicas or "",
        "medicamentos_uso": anamnese.medicamentos_uso or "",
        "lesoes_anteriores": anamnese.lesoes_anteriores or "",
        "patologias_marcadas": (anamnese.doencas_cronicas or "").split(",") if anamnese.doencas_cronicas else [],
        "data_avaliacao": str(anamnese.data_avaliacao) if anamnese.data_avaliacao else None
    }

@router.post("/minha", tags=["Anamnese - Aluno"])
def aluno_salvar_propria(
    dados: dict,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Aluno salva/atualiza sua propria anamnese.
    
    NOTA: Salvar aqui NAO altera treino atual automaticamente.
    Personal usa essa info na proxima avaliacao presencial.
    
    TODO: futura sessao - aplicar ressalvas no treino baseado em patologias.
    """
    patologias = dados.get("patologias", [])
    outras = dados.get("outras_condicoes", "")
    medicacoes = dados.get("medicacoes", "")
    
    # Junta patologias + outras condicoes em "doencas_cronicas"
    doencas_str = ",".join(patologias) if patologias else ""
    if outras:
        doencas_str = (doencas_str + " | Outras: " + outras) if doencas_str else "Outras: " + outras
    
    existente = db.query(Anamnese).filter(Anamnese.aluno_id == aluno.id).first()
    if existente:
        existente.doencas_cronicas = doencas_str
        existente.medicamentos_uso = medicacoes
        existente.data_avaliacao = date.today()
        db.commit()
        db.refresh(existente)
        anamnese_id = existente.id
    else:
        nova = Anamnese(
            aluno_id=aluno.id,
            data_avaliacao=date.today(),
            doencas_cronicas=doencas_str,
            medicamentos_uso=medicacoes
        )
        db.add(nova)
        db.commit()
        db.refresh(nova)
        anamnese_id = nova.id
    
    return {
        "ok": True,
        "id": anamnese_id,
        "mensagem": "Anamnese salva! Seu personal vai usar essas informacoes na proxima avaliacao."
    }

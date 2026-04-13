"""
Router — Portal do Aluno
POST /aluno-portal/login          → login do aluno
GET  /aluno-portal/perfil         → perfil do aluno logado
GET  /aluno-portal/avaliacoes     → avaliações do aluno
GET  /aluno-portal/treino         → plano de treino ativo
GET  /aluno-portal/pagamentos     → pagamentos do aluno
PUT  /aluno-portal/senha          → alterar senha
"""

from datetime import datetime, timedelta, timezone, date
from fastapi import APIRouter, Depends, HTTPException, status  # noqa: F401
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, Column, Integer, String, Boolean,ForeignKey
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db
from app.models import Base, Aluno
from app.config import settings

router = APIRouter(prefix="/aluno-portal", tags=["Portal do Aluno"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_aluno = OAuth2PasswordBearer(tokenUrl="/aluno-portal/login")


# ── Modelo de credenciais do aluno ────────────────────────────────────────────

class AlunoCredencial(Base):
    __tablename__ = "aluno_credenciais"
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


# ── Schemas ───────────────────────────────────────────────────────────────────

class AlunoLogin(BaseModel):
    email: EmailStr
    senha: str

class AlunoTokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    aluno_id: int
    nome: str

class CriarAcesso(BaseModel):
    aluno_id: int
    email: EmailStr
    senha: str

class AlterarSenhaAluno(BaseModel):
    senha_atual: str
    nova_senha: str


# ── Helpers JWT ───────────────────────────────────────────────────────────────

def criar_token_aluno(aluno_id: int) -> str:
    payload = {
        "sub": str(aluno_id),
        "type": "aluno",
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_aluno_logado(token: str = Depends(oauth2_aluno), db: Session = Depends(get_db)) -> Aluno:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "aluno":
            raise HTTPException(status_code=401, detail="Token invalido")
        aluno_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.ativo == True).first()
    if not aluno:
        raise HTTPException(status_code=401, detail="Aluno nao encontrado")
    return aluno


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/criar-acesso", status_code=201)
def criar_acesso_aluno(dados: CriarAcesso, db: Session = Depends(get_db)):
    """Personal cria o acesso do aluno ao portal"""
    aluno = db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")

    existente = db.query(AlunoCredencial).filter(AlunoCredencial.aluno_id == dados.aluno_id).first()
    if existente:
        existente.email = dados.email
        existente.senha_hash = pwd_context.hash(dados.senha)
        db.commit()
        return {"mensagem": f"Acesso atualizado para {aluno.nome}"}

    cred = AlunoCredencial(
        aluno_id=dados.aluno_id,
        email=dados.email,
        senha_hash=pwd_context.hash(dados.senha),
    )
    db.add(cred)
    db.commit()

    # Email de boas-vindas para o aluno
    try:
        from app.routers.pagamento import enviar_email_boas_vindas_aluno
        enviar_email_boas_vindas_aluno(aluno.nome, dados.email)
    except Exception as e:
        print(f"Email aluno falhou: {e}")

    return {"mensagem": f"Acesso criado para {aluno.nome}", "email": dados.email}


@router.post("/login", response_model=AlunoTokenResposta)
def login_aluno(dados: AlunoLogin, db: Session = Depends(get_db)):
    cred = db.query(AlunoCredencial).filter(AlunoCredencial.email == dados.email).first()
    if not cred or not pwd_context.verify(dados.senha, cred.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    if not cred.ativo:
        raise HTTPException(status_code=403, detail="Acesso desativado")

    aluno = db.query(Aluno).filter(Aluno.id == cred.aluno_id).first()
    if not aluno.ativo:
        raise HTTPException(status_code=403, detail="Acesso desativado. Verifique sua assinatura em aurumsc.com.br")
    if aluno.personal_id is None and not aluno.ativo:
        raise HTTPException(status_code=403, detail="Assinatura inativa. Acesse aurumsc.com.br para renovar.")
    if aluno.personal_id is not None:
        from app.models import Personal as PersonalModel
        personal = db.query(PersonalModel).filter(PersonalModel.id == aluno.personal_id).first()
        if personal and personal.assinatura_status not in ('trial', 'ativa'):
            raise HTTPException(status_code=403, detail="Seu personal não possui assinatura ativa.")
        return AlunoTokenResposta(
        access_token=criar_token_aluno(aluno.id),
        aluno_id=aluno.id,
        nome=aluno.nome,
    )


@router.get("/perfil")
def perfil(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    hoje = date.today()
    idade = None
    if aluno.data_nascimento:
        idade = hoje.year - aluno.data_nascimento.year - (
            (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)
        )
    return {
        "id": aluno.id,
        "nome": aluno.nome,
        "email": aluno.email,
        "telefone": aluno.telefone,
        "sexo": aluno.sexo.value if aluno.sexo else None,
        "objetivo": aluno.objetivo.value if aluno.objetivo else None,
        "nivel_experiencia": aluno.nivel_experiencia.value if aluno.nivel_experiencia else None,
        "idade": idade,
        "foto_url": aluno.foto_url,
    }


@router.get("/avaliacoes")
def avaliacoes(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.avaliacao import AvaliacaoFisica
    avals = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).all()

    return [{
        "id": a.id,
        "data": str(a.data_avaliacao),
        "peso": a.peso,
        "imc": a.imc,
        "classificacao_imc": a.classificacao_imc,
        "percentual_gordura": a.percentual_gordura,
        "classificacao_gordura": a.classificacao_gordura,
        "massa_magra_kg": a.massa_magra_kg,
        "vo2max": a.vo2max,
        "classificacao_vo2": a.classificacao_vo2,
        "risco_cardiovascular": a.risco_cardiovascular,
    } for a in avals]


@router.get("/treino")
def treino(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.treino import PlanoTreino, SessaoTreino
    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).order_by(PlanoTreino.criado_em.desc()).first()

    if not plano:
        return {"mensagem": "Nenhum plano de treino ativo"}

    sessoes = db.query(SessaoTreino).filter(SessaoTreino.plano_id == plano.id).all()
    return {
        "plano": {
            "id": plano.id,
            "nome": plano.nome,
            "objetivo": plano.objetivo,
            "nivel": plano.nivel,
            "dias_semana": plano.dias_semana,
            "semanas_total": plano.semanas_total,
            "data_inicio": str(plano.data_inicio) if plano.data_inicio else None,
        },
        "sessoes": [{"id": s.id, "nome": s.nome, "dia_semana": s.dia_semana} for s in sessoes],
        "periodizacao": plano.periodizacao,
    }


@router.get("/pagamentos")
def pagamentos(aluno: Aluno = Depends(get_aluno_logado), db: Session = Depends(get_db)):
    from app.routers.financeiro import Pagamento, calc_status, calc_atraso
    pags = db.query(Pagamento).filter(
        Pagamento.aluno_id == aluno.id
    ).order_by(Pagamento.data_vencimento.desc()).all()

    resultado = [{
        "id": p.id,
        "descricao": p.descricao,
        "valor": p.valor,
        "vencimento": str(p.data_vencimento),
        "pagamento": str(p.data_pagamento) if p.data_pagamento else None,
        "status": calc_status(p),
        "dias_atraso": calc_atraso(p),
    } for p in pags]

    return {
        "resumo": {
            "pago": round(sum(p["valor"] for p in resultado if p["status"] == "pago"), 2),
            "pendente": round(sum(p["valor"] for p in resultado if p["status"] == "pendente"), 2),
            "atrasado": round(sum(p["valor"] for p in resultado if p["status"] == "atrasado"), 2),
        },
        "pagamentos": resultado
    }


@router.put("/senha")
def alterar_senha(
    dados: AlterarSenhaAluno,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    cred = db.query(AlunoCredencial).filter(AlunoCredencial.aluno_id == aluno.id).first()
    if not cred or not pwd_context.verify(dados.senha_atual, cred.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    cred.senha_hash = pwd_context.hash(dados.nova_senha)
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}


class CadastroRapido(BaseModel):
    nome: str
    email: str
    senha: str
    cpf: str | None = None

@router.post("/cadastro")
def cadastro_rapido(dados: CadastroRapido, db: Session = Depends(get_db)):
    from app.models import Aluno
    existente = db.query(Aluno).filter(Aluno.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    aluno = Aluno(
        nome=dados.nome, email=dados.email,
        telefone="", objetivo="HIPERTROFIA",
        nivel_experiencia="INICIANTE", sexo="MASCULINO",
        personal_id=None
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    cred = AlunoCredencial(aluno_id=aluno.id, email=dados.email, senha_hash=pwd_context.hash(dados.senha))
    db.add(cred)
    db.commit()
    # Envia email de boas vindas
    try:
        from app.services.email_service import email_boas_vindas_aluno
        email_boas_vindas_aluno(dados.nome, dados.email)
    except Exception:
        pass
    return {"aluno_id": aluno.id, "mensagem": "Conta criada com sucesso!"}

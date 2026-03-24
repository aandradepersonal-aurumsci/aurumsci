"""
Router — Admin & Multi-tenancy
Apenas o dono do sistema (superadmin) tem acesso

POST /admin/login                → login do admin
GET  /admin/personais            → listar todos os personais
GET  /admin/personais/{id}       → detalhe do personal
PUT  /admin/personais/{id}/plano → alterar plano do personal
PUT  /admin/personais/{id}/status→ ativar/bloquear personal
GET  /admin/stats                → estatísticas gerais do sistema
POST /admin/planos               → criar plano de assinatura
GET  /admin/planos               → listar planos
"""

from datetime import datetime, timedelta, timezone, date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, func
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db
from app.models import Base, Personal, Aluno
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_admin = OAuth2PasswordBearer(tokenUrl="/admin/login")

# ── Credenciais do superadmin (fixas no .env) ─────────────────────────────────
ADMIN_EMAIL = "admin@ptgestao.com"
ADMIN_SENHA = "Admin@PTGestao2026"  # Troque isso!


# ── Modelos ───────────────────────────────────────────────────────────────────

class PlanoAssinatura(Base):
    __tablename__ = "planos_assinatura"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)        # Básico, Pro, Premium
    preco_mensal = Column(Float, nullable=False)
    limite_alunos = Column(Integer, default=10)
    avaliacao_fisica = Column(Boolean, default=True)
    laudo_pdf = Column(Boolean, default=False)
    portal_aluno = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


class ContaPersonal(Base):
    __tablename__ = "contas_personal"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    personal_id = Column(Integer, ForeignKey("personals.id"), unique=True, nullable=False)
    plano_id = Column(Integer, ForeignKey("planos_assinatura.id"), nullable=True)
    status = Column(String(20), default="trial")     # trial, ativo, bloqueado, cancelado
    trial_fim = Column(Date)
    assinatura_inicio = Column(Date)
    assinatura_fim = Column(Date)
    criado_em = Column(DateTime, default=datetime.utcnow)


# ── Schemas ───────────────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    email: str
    senha: str

class PlanoCreate(BaseModel):
    nome: str
    preco_mensal: float
    limite_alunos: int = 10
    avaliacao_fisica: bool = True
    laudo_pdf: bool = False
    portal_aluno: bool = False

class AlterarPlano(BaseModel):
    plano_id: int
    meses: int = 1

class AlterarStatus(BaseModel):
    status: str  # ativo, bloqueado, trial, cancelado


# ── JWT Admin ─────────────────────────────────────────────────────────────────

def criar_token_admin() -> str:
    payload = {"sub": "admin", "type": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_admin(token: str = Depends(oauth2_admin)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "admin":
            raise HTTPException(status_code=401, detail="Acesso negado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")
    return True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login")
def login_admin(dados: AdminLogin):
    if dados.email != ADMIN_EMAIL or dados.senha != ADMIN_SENHA:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    return {"access_token": criar_token_admin(), "token_type": "bearer", "role": "admin"}


@router.post("/planos", status_code=201)
def criar_plano(dados: PlanoCreate, _=Depends(get_admin), db: Session = Depends(get_db)):
    plano = PlanoAssinatura(**dados.model_dump())
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return {"id": plano.id, "nome": plano.nome, "preco": plano.preco_mensal, "limite_alunos": plano.limite_alunos}


@router.get("/planos")
def listar_planos(db: Session = Depends(get_db)):
    planos = db.query(PlanoAssinatura).filter(PlanoAssinatura.ativo == True).all()
    return [{"id": p.id, "nome": p.nome, "preco_mensal": p.preco_mensal, "limite_alunos": p.limite_alunos,
             "avaliacao_fisica": p.avaliacao_fisica, "laudo_pdf": p.laudo_pdf, "portal_aluno": p.portal_aluno} for p in planos]


@router.get("/personais")
def listar_personais(_=Depends(get_admin), db: Session = Depends(get_db)):
    personais = db.query(Personal).order_by(Personal.criado_em.desc()).all()
    resultado = []
    for p in personais:
        conta = db.query(ContaPersonal).filter(ContaPersonal.personal_id == p.id).first()
        total_alunos = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == p.id, Aluno.ativo == True).scalar()
        plano = None
        if conta and conta.plano_id:
            pl = db.query(PlanoAssinatura).filter(PlanoAssinatura.id == conta.plano_id).first()
            plano = pl.nome if pl else None
        resultado.append({
            "id": p.id,
            "nome": p.nome,
            "email": p.email,
            "cref": p.cref,
            "telefone": p.telefone,
            "ativo": p.ativo,
            "status_conta": conta.status if conta else "sem_conta",
            "plano": plano,
            "trial_fim": str(conta.trial_fim) if conta and conta.trial_fim else None,
            "total_alunos": total_alunos,
            "cadastro": str(p.criado_em.date()) if p.criado_em else None,
        })
    return resultado


@router.get("/personais/{personal_id}")
def detalhe_personal(personal_id: int, _=Depends(get_admin), db: Session = Depends(get_db)):
    p = db.query(Personal).filter(Personal.id == personal_id).first()
    if not p: raise HTTPException(status_code=404, detail="Personal nao encontrado")
    conta = db.query(ContaPersonal).filter(ContaPersonal.personal_id == personal_id).first()
    total_alunos = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id).scalar()
    ativos = db.query(func.count(Aluno.id)).filter(Aluno.personal_id == personal_id, Aluno.ativo == True).scalar()
    return {
        "id": p.id, "nome": p.nome, "email": p.email, "cref": p.cref,
        "telefone": p.telefone, "ativo": p.ativo,
        "conta": {"status": conta.status if conta else "sem_conta",
                  "plano_id": conta.plano_id if conta else None,
                  "trial_fim": str(conta.trial_fim) if conta and conta.trial_fim else None,
                  "assinatura_fim": str(conta.assinatura_fim) if conta and conta.assinatura_fim else None},
        "alunos": {"total": total_alunos, "ativos": ativos},
        "cadastro": str(p.criado_em.date()) if p.criado_em else None,
    }


@router.put("/personais/{personal_id}/plano")
def alterar_plano(personal_id: int, dados: AlterarPlano, _=Depends(get_admin), db: Session = Depends(get_db)):
    p = db.query(Personal).filter(Personal.id == personal_id).first()
    if not p: raise HTTPException(status_code=404, detail="Personal nao encontrado")
    plano = db.query(PlanoAssinatura).filter(PlanoAssinatura.id == dados.plano_id).first()
    if not plano: raise HTTPException(status_code=404, detail="Plano nao encontrado")
    conta = db.query(ContaPersonal).filter(ContaPersonal.personal_id == personal_id).first()
    hoje = date.today()
    if not conta:
        conta = ContaPersonal(personal_id=personal_id)
        db.add(conta)
    conta.plano_id = dados.plano_id
    conta.status = "ativo"
    conta.assinatura_inicio = hoje
    from dateutil.relativedelta import relativedelta
    conta.assinatura_fim = hoje + relativedelta(months=dados.meses)
    db.commit()
    return {"mensagem": f"Plano {plano.nome} ativado para {p.nome}", "valido_ate": str(conta.assinatura_fim)}


@router.put("/personais/{personal_id}/status")
def alterar_status(personal_id: int, dados: AlterarStatus, _=Depends(get_admin), db: Session = Depends(get_db)):
    p = db.query(Personal).filter(Personal.id == personal_id).first()
    if not p: raise HTTPException(status_code=404, detail="Personal nao encontrado")
    conta = db.query(ContaPersonal).filter(ContaPersonal.personal_id == personal_id).first()
    if not conta:
        conta = ContaPersonal(personal_id=personal_id)
        db.add(conta)
    conta.status = dados.status
    if dados.status == "bloqueado":
        p.ativo = False
    elif dados.status == "ativo":
        p.ativo = True
    db.commit()
    return {"mensagem": f"Status de {p.nome} alterado para {dados.status}"}


@router.post("/personais/{personal_id}/trial")
def ativar_trial(personal_id: int, dias: int = 14, _=Depends(get_admin), db: Session = Depends(get_db)):
    p = db.query(Personal).filter(Personal.id == personal_id).first()
    if not p: raise HTTPException(status_code=404, detail="Personal nao encontrado")
    conta = db.query(ContaPersonal).filter(ContaPersonal.personal_id == personal_id).first()
    if not conta:
        conta = ContaPersonal(personal_id=personal_id)
        db.add(conta)
    conta.status = "trial"
    conta.trial_fim = date.today() + timedelta(days=dias)
    db.commit()
    return {"mensagem": f"Trial de {dias} dias ativado para {p.nome}", "trial_fim": str(conta.trial_fim)}


@router.get("/stats")
def stats(_=Depends(get_admin), db: Session = Depends(get_db)):
    total_personais = db.query(func.count(Personal.id)).scalar()
    personais_ativos = db.query(func.count(Personal.id)).filter(Personal.ativo == True).scalar()
    total_alunos = db.query(func.count(Aluno.id)).scalar()
    alunos_ativos = db.query(func.count(Aluno.id)).filter(Aluno.ativo == True).scalar()
    contas = db.query(ContaPersonal).all()
    trials = sum(1 for c in contas if c.status == "trial")
    ativos = sum(1 for c in contas if c.status == "ativo")
    bloqueados = sum(1 for c in contas if c.status == "bloqueado")
    return {
        "personais": {"total": total_personais, "ativos": personais_ativos},
        "alunos": {"total": total_alunos, "ativos": alunos_ativos},
        "contas": {"trial": trials, "ativo": ativos, "bloqueado": bloqueados},
    }

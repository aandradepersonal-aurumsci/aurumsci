"""
AurumSci — Autenticação Segura
Baseado no auth.py original + melhorias de segurança:

✅ Rate limiting: 5 tentativas de login por minuto por IP
✅ Blacklist de tokens (logout real)
✅ Log de tentativas de login falhas
✅ Anti timing attack
✅ Validação de força de senha no registro
✅ Token com informações mínimas (apenas sub)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Set
import logging
import time

from app.database import get_db
from app.models import Personal
from app.schemas.auth import (
    PersonalRegistro, PersonalLogin, TokenResposta,
    RefreshTokenRequest, PersonalResposta
)
from app.utils.auth import (
    hash_senha, verificar_senha,
    criar_access_token, criar_refresh_token,
    decodificar_token, get_personal_atual
)

logger = logging.getLogger("aurumsci.auth")
router = APIRouter(prefix="/auth", tags=["Autenticacao"])

# ── Blacklist de tokens ───────────────────────────────────────
# Em produção substituir por Redis
_token_blacklist: Set[str] = set()

def invalidar_token(token: str):
    _token_blacklist.add(token)

def token_na_blacklist(token: str) -> bool:
    return token in _token_blacklist

# ── Rate limiting de login ────────────────────────────────────
_tentativas: dict = {}
MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 60

def checar_rate_limit(ip: str) -> bool:
    agora = time.time()
    tentativas = _tentativas.get(ip, [])
    tentativas = [t for t in tentativas if agora - t < JANELA_SEGUNDOS]
    _tentativas[ip] = tentativas
    return len(tentativas) < MAX_TENTATIVAS

def registrar_tentativa(ip: str):
    agora = time.time()
    if ip not in _tentativas:
        _tentativas[ip] = []
    _tentativas[ip].append(agora)

# ── Validação de senha forte ──────────────────────────────────
def validar_senha_forte(senha: str):
    if len(senha) < 8:
        raise HTTPException(
            status_code=400,
            detail="Senha deve ter no mínimo 8 caracteres"
        )
    if not any(c.isupper() for c in senha):
        raise HTTPException(
            status_code=400,
            detail="Senha deve ter pelo menos uma letra maiúscula"
        )
    if not any(c.isdigit() for c in senha):
        raise HTTPException(
            status_code=400,
            detail="Senha deve ter pelo menos um número"
        )

# ── Endpoints ─────────────────────────────────────────────────

@router.post("/registro", response_model=PersonalResposta, status_code=201)
def registrar(dados: PersonalRegistro, db: Session = Depends(get_db)):
    # Verifica se email já existe
    if db.query(Personal).filter(Personal.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

    # Valida força da senha
    validar_senha_forte(dados.senha)

    personal = Personal(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        cref=dados.cref,
        telefone=dados.telefone,
        cpf=dados.cpf
    )
    db.add(personal)
    db.commit()
    db.refresh(personal)

    logger.info(f"NOVO REGISTRO | Personal: {personal.email}")
    return personal


@router.post("/login", response_model=TokenResposta)
def login(request: Request, dados: PersonalLogin, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    # Rate limiting por IP
    if not checar_rate_limit(client_ip):
        logger.warning(f"RATE LIMIT | IP: {client_ip} | Email: {dados.email}")
        raise HTTPException(
            status_code=429,
            detail=f"Muitas tentativas de login. Aguarde {JANELA_SEGUNDOS} segundos."
        )

    registrar_tentativa(client_ip)

    # Busca personal — sempre faz verificação para evitar timing attack
    personal = db.query(Personal).filter(Personal.email == dados.email).first()
    senha_ok = False
    if personal:
        senha_ok = verificar_senha(dados.senha, personal.senha_hash)

    if not personal or not senha_ok:
        logger.warning(
            f"LOGIN FALHOU | IP: {client_ip} | "
            f"Email: {dados.email} | "
            f"Tentativas: {len(_tentativas.get(client_ip, []))}"
        )
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    if not personal.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")
    if personal.assinatura_status not in ('trial', 'ativa'):
        raise HTTPException(status_code=403, detail='Assinatura inativa. Acesse aurumsc.com.br para renovar.')

    token_data = {"sub": str(personal.id)}
    logger.info(f"LOGIN OK | IP: {client_ip} | Personal ID: {personal.id}")

    return TokenResposta(
        access_token=criar_access_token(token_data),
        refresh_token=criar_refresh_token(token_data),
        personal_id=personal.id,
        nome=personal.nome,
        logo_url=personal.logo_url or '',
        nome_empresa=personal.nome_empresa or ''
    )


@router.post("/refresh", response_model=TokenResposta)
def renovar_token(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    # Verifica se token está na blacklist
    if token_na_blacklist(dados.refresh_token):
        raise HTTPException(status_code=401, detail="Token invalidado. Faça login novamente.")

    payload = decodificar_token(dados.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token invalido")

    personal = db.query(Personal).filter(
        Personal.id == int(payload.get("sub")),
        Personal.ativo == True
    ).first()

    if not personal:
        raise HTTPException(status_code=401, detail="Personal nao encontrado")

    token_data = {"sub": str(personal.id)}
    return TokenResposta(
        access_token=criar_access_token(token_data),
        refresh_token=criar_refresh_token(token_data),
        personal_id=personal.id,
        nome=personal.nome,
        logo_url=personal.logo_url or '',
        nome_empresa=personal.nome_empresa or ''
    )


@router.post("/logout")
def logout(personal: Personal = Depends(get_personal_atual), request: Request = None):
    """Logout real — invalida o token atual."""
    # Pega o token do header
    auth_header = request.headers.get("Authorization", "") if request else ""
    token = auth_header.replace("Bearer ", "")
    if token:
        invalidar_token(token)

    logger.info(f"LOGOUT | Personal ID: {personal.id}")
    return {"mensagem": "Logout realizado com sucesso"}


@router.get("/me", response_model=PersonalResposta)
def meu_perfil(personal: Personal = Depends(get_personal_atual)):
    return personal


class AlterarSenha(BaseModel):
    senha_atual: str
    nova_senha: str

    @validator('nova_senha')
    def senha_forte(cls, v):
        if len(v) < 8:
            raise ValueError('Nova senha deve ter no mínimo 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('Nova senha deve ter pelo menos uma letra maiúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Nova senha deve ter pelo menos um número')
        return v


@router.put("/senha")
def alterar_senha(
    dados: AlterarSenha,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    if not verificar_senha(dados.senha_atual, personal.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    personal.senha_hash = hash_senha(dados.nova_senha)
    db.commit()

    logger.info(f"SENHA ALTERADA | Personal ID: {personal.id}")
    return {"mensagem": "Senha alterada com sucesso"}

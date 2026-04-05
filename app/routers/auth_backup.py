from fastapi import APIRouter, Depends, HTTPException, status  # noqa: F401
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Personal
from app.schemas.auth import PersonalRegistro, PersonalLogin, TokenResposta, RefreshTokenRequest, PersonalResposta
from app.utils.auth import hash_senha, verificar_senha, criar_access_token, criar_refresh_token, decodificar_token, get_personal_atual

router = APIRouter(prefix="/auth", tags=["Autenticacao"])

@router.post("/registro", response_model=PersonalResposta, status_code=201)
def registrar(dados: PersonalRegistro, db: Session = Depends(get_db)):
    if db.query(Personal).filter(Personal.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    personal = Personal(nome=dados.nome, email=dados.email, senha_hash=hash_senha(dados.senha), cref=dados.cref, telefone=dados.telefone, cpf=dados.cpf)
    db.add(personal)
    db.commit()
    db.refresh(personal)
    # Envia email de boas vindas
    try:
        from app.services.email_service import email_boas_vindas_personal
        email_boas_vindas_personal(personal.nome, personal.email)
    except Exception:
        pass
    return personal

@router.post("/login", response_model=TokenResposta)
def login(dados: PersonalLogin, db: Session = Depends(get_db)):
    personal = db.query(Personal).filter(Personal.email == dados.email).first()
    if not personal or not verificar_senha(dados.senha, personal.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    if not personal.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada")
    token_data = {"sub": str(personal.id)}
    return TokenResposta(access_token=criar_access_token(token_data), refresh_token=criar_refresh_token(token_data), personal_id=personal.id, nome=personal.nome)

@router.post("/refresh", response_model=TokenResposta)
def renovar_token(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decodificar_token(dados.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token invalido")
    personal = db.query(Personal).filter(Personal.id == int(payload.get("sub")), Personal.ativo == True).first()
    if not personal:
        raise HTTPException(status_code=401, detail="Personal nao encontrado")
    token_data = {"sub": str(personal.id)}
    return TokenResposta(access_token=criar_access_token(token_data), refresh_token=criar_refresh_token(token_data), personal_id=personal.id, nome=personal.nome)

@router.get("/me", response_model=PersonalResposta)
def meu_perfil(personal: Personal = Depends(get_personal_atual)):
    return personal

class AlterarSenha(BaseModel):
    senha_atual: str
    nova_senha: str

@router.put("/senha")
def alterar_senha(dados: AlterarSenha, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    if not verificar_senha(dados.senha_atual, personal.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    personal.senha_hash = hash_senha(dados.nova_senha)
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}

"""
Router — Recuperar Senha
POST /recuperar-senha/solicitar — recebe email, manda link
POST /recuperar-senha/redefinir — recebe token + nova senha
GET  /recuperar-senha/validar/{token} — confere se token e valido
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Base, Personal, Aluno

router = APIRouter(prefix="/recuperar-senha", tags=["Recuperar Senha"])


# ─── Tabela de tokens ─────────────────────────────────────────
class TokenResetSenha(Base):
    __tablename__ = "tokens_reset_senha"
    id = Column(Integer, primary_key=True)
    token = Column(String(80), unique=True, index=True, nullable=False)
    email = Column(String(120), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'personal' ou 'aluno'
    user_id = Column(Integer, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    expira_em = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)


# ─── Schemas ──────────────────────────────────────────────────
class SolicitarReset(BaseModel):
    email: EmailStr


class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str


# ─── Helper: hash de senha ────────────────────────────────────
def _hash_senha(senha_plain: str) -> str:
    """Reusa o pwd_context que ja existe no projeto."""
    from app.routers.portal_aluno import pwd_context
    return pwd_context.hash(senha_plain)


def _validar_senha(senha: str):
    """Senha forte: minimo 8 chars."""
    if len(senha) < 8:
        raise HTTPException(400, "Senha deve ter pelo menos 8 caracteres")


# ─── Endpoint 1: SOLICITAR reset ──────────────────────────────
@router.post("/solicitar")
def solicitar_reset(dados: SolicitarReset, db: Session = Depends(get_db)):
    """Recebe email, gera token, manda email com link."""
    email_lower = dados.email.lower().strip()
    
    # Procura email no PRO
    personal = db.query(Personal).filter(Personal.email == email_lower).first()
    aluno = None
    
    if personal:
        tipo = "personal"
        user_id = personal.id
        nome = personal.nome
    else:
        # Procura no ALUNO (tabela usuario_aluno tem o email de login)
        from app.routers.portal_aluno import UsuarioAluno
        usuario = db.query(UsuarioAluno).filter(UsuarioAluno.email == email_lower).first()
        if usuario:
            aluno = db.query(Aluno).filter(Aluno.id == usuario.aluno_id).first()
            tipo = "aluno"
            user_id = usuario.aluno_id
            nome = aluno.nome if aluno else "Aluno"
        else:
            # IMPORTANTE: nao revelar se email existe ou nao (seguranca)
            return {
                "ok": True,
                "mensagem": "Se este email estiver cadastrado, voce recebera um link em alguns minutos."
            }
    
    # Gera token aleatorio (32 bytes = 64 chars hex)
    token = secrets.token_urlsafe(48)
    
    # Salva no banco (valido por 1h)
    novo_token = TokenResetSenha(
        token=token,
        email=email_lower,
        tipo=tipo,
        user_id=user_id,
        expira_em=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(novo_token)
    db.commit()
    
    # Manda email
    try:
        from app.services.email_service import enviar_email
        link = f"https://aurumsc.com.br/redefinir-senha?token={token}"
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background: #0A0A0F; color: #fff;">
          <h1 style="color: #C9A84C;">Recuperar senha - AurumSci</h1>
          <p>Ola {nome},</p>
          <p>Voce solicitou recuperar a senha da sua conta {tipo.upper()} no AurumSci.</p>
          <p>Clique no botao abaixo para criar uma nova senha:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{link}" style="background: #C9A84C; color: #0A0A0F; padding: 14px 32px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block;">
              REDEFINIR MINHA SENHA
            </a>
          </div>
          <p style="font-size: 12px; color: #888;">
            Este link e valido por 1 hora.<br>
            Se voce nao solicitou esta recuperacao, ignore este email.<br><br>
            Link direto: <a href="{link}" style="color: #C9A84C;">{link}</a>
          </p>
          <p style="font-size: 11px; color: #666; margin-top: 30px; border-top: 1px solid #333; padding-top: 15px;">
            AurumSci · CREF 62702-G/SP<br>
            Suporte: andrepersonal395@gmail.com
          </p>
        </div>
        """
        
        enviar_email(
            para=email_lower,
            assunto="Recuperar senha - AurumSci",
            html=html
        )
        print(f"[RESET-SENHA] Email enviado para {email_lower} ({tipo})")
    except Exception as e:
        print(f"[RESET-SENHA] Erro enviar email: {e}")
        # Nao falha — token ja foi salvo, usuario pode tentar de novo
    
    return {
        "ok": True,
        "mensagem": "Se este email estiver cadastrado, voce recebera um link em alguns minutos."
    }


# ─── Endpoint 2: VALIDAR token ────────────────────────────────
@router.get("/validar/{token}")
def validar_token(token: str, db: Session = Depends(get_db)):
    """Frontend chama isso ao abrir a pagina de redefinir."""
    t = db.query(TokenResetSenha).filter(TokenResetSenha.token == token).first()
    
    if not t:
        return {"valido": False, "motivo": "Token nao encontrado"}
    if t.usado:
        return {"valido": False, "motivo": "Este link ja foi usado"}
    if datetime.utcnow() > t.expira_em:
        return {"valido": False, "motivo": "Link expirado (validade: 1h)"}
    
    return {"valido": True, "tipo": t.tipo, "email": t.email}


# ─── Endpoint 3: REDEFINIR senha ──────────────────────────────
@router.post("/redefinir")
def redefinir_senha(dados: RedefinirSenha, db: Session = Depends(get_db)):
    """Recebe token + nova senha, atualiza no banco."""
    _validar_senha(dados.nova_senha)
    
    t = db.query(TokenResetSenha).filter(TokenResetSenha.token == dados.token).first()
    
    if not t:
        raise HTTPException(404, "Token invalido")
    if t.usado:
        raise HTTPException(400, "Este link ja foi usado")
    if datetime.utcnow() > t.expira_em:
        raise HTTPException(400, "Link expirado. Solicite um novo.")
    
    # Atualiza senha do usuario certo
    nova_hash = _hash_senha(dados.nova_senha)
    
    if t.tipo == "personal":
        personal = db.query(Personal).filter(Personal.id == t.user_id).first()
        if not personal:
            raise HTTPException(404, "Usuario nao encontrado")
        personal.senha_hash = nova_hash
    elif t.tipo == "aluno":
        from app.routers.portal_aluno import UsuarioAluno
        usuario = db.query(UsuarioAluno).filter(UsuarioAluno.aluno_id == t.user_id).first()
        if not usuario:
            raise HTTPException(404, "Usuario nao encontrado")
        usuario.senha_hash = nova_hash
    else:
        raise HTTPException(400, "Tipo de usuario invalido")
    
    # Marca token como usado
    t.usado = True
    db.commit()
    
    print(f"[RESET-SENHA] Senha redefinida para {t.email} ({t.tipo})")
    
    return {
        "ok": True,
        "mensagem": "Senha redefinida com sucesso! Agora faca login com sua nova senha."
    }

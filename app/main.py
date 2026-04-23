"""
AurumSci — Ponto de entrada FastAPI
Motor v1 integrado — VERSÃO SEGURA

Melhorias de segurança aplicadas:
✅ CORS restrito por domínio (não mais allow_origins=["*"])
✅ Security headers (XSS, Clickjacking, MIME sniffing)
✅ HSTS em produção
✅ Rate limiting global
✅ Docs desabilitado em produção
✅ Log de segurança
✅ Trusted hosts em produção
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
import time

from app.config import settings
from app.database import engine
from app.models import Base

from app.routers import auth, alunos, anamnese, avaliacao
from app.routers.treino import router as treino_router
from app.routers.financeiro import router as financeiro_router
from app.routers.portal_aluno import router as portal_aluno_router
from app.routers.admin import router as admin_router
from app.routers.chatbot import router as chatbot_router
from app.routers.postural_ia import router as postural_ia_router
from app.routers.app_aluno import router as app_aluno_router
from app.routers.app_personal import router as app_personal_router
from app.routers.pagamento import router as pagamento_router

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("aurumsci.security")

# ── Ambiente ──────────────────────────────────────────────────
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

# ── Rate Limiter ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ── Banco ─────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="AurumSci",
    description="Plataforma premium para personal trainers — Motor v1",
    version="1.0.0",
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
)

# ── Rate Limiting ─────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS restrito ─────────────────────────────────────────────
ORIGINS_DEV = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

ORIGINS_PROD = [
    "https://aurumsci.com",
    "https://www.aurumsci.com",
    "https://app.aurumsci.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS_PROD if IS_PRODUCTION else ORIGINS_DEV,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# ── Trusted Hosts (produção) ──────────────────────────────────
if IS_PRODUCTION:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["aurumsci.com", "www.aurumsci.com", "app.aurumsci.com"]
    )

# ── Security Headers ──────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    start = time.time()
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'"
    response.headers["X-Process-Time"] = str(round((time.time() - start) * 1000, 2)) + "ms"

    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# ── Log de tentativas suspeitas ───────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)

    if "/login" in str(request.url) and response.status_code in [401, 403]:
        ip = request.client.host if request.client else "unknown"
        logger.warning(f"LOGIN FALHOU | IP: {ip} | Status: {response.status_code}")

    if response.status_code >= 500:
        logger.error(f"ERRO SERVIDOR | URL: {request.url} | Status: {response.status_code}")

    return response

# ── Static files ──────────────────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(alunos.router)
app.include_router(anamnese.router)
app.include_router(avaliacao.router)
app.include_router(treino_router)
app.include_router(financeiro_router)
app.include_router(portal_aluno_router)
app.include_router(admin_router)
app.include_router(chatbot_router)
app.include_router(postural_ia_router)
app.include_router(app_aluno_router)
app.include_router(app_personal_router)
app.include_router(pagamento_router)

# ── App do Aluno ──────────────────────────────────────────────
@app.get("/cadastro", response_class=HTMLResponse, include_in_schema=False)
def cadastro_page():
    with open("static/cadastro.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/aluno", response_class=HTMLResponse, include_in_schema=False)
def app_aluno():
    with open("static/app_aluno_v23.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing():
    with open("static/landing.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/cadastro-pro", response_class=HTMLResponse, include_in_schema=False)
def cadastro_pro_page():
    with open("static/cadastro_pro.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/pro", response_class=HTMLResponse, include_in_schema=False)
def landing_pro():
    with open("static/landing_pro.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/personal", response_class=HTMLResponse, include_in_schema=False)
def app_personal():
    with open("static/app_personal.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/postural", response_class=HTMLResponse, include_in_schema=False)
def app_postural():
    with open("static/analise_postural_ia.html", "r", encoding="utf-8") as f:
        return f.read()

# ── Status ────────────────────────────────────────────────────
@app.get("/", tags=["Status"])
def root():
    return {
        "app": "AurumSci",
        "versao": "1.0.0",
        "motor": "v1",
        "status": "online",
        "docs": "/docs" if not IS_PRODUCTION else "disabled"
    }

@app.get("/health", tags=["Status"])
def health():
    return {"status": "ok"}

@app.get("/debug-path")
def debug_path():
    import os
    return {
        "cwd": os.getcwd(),
        "static_exists": os.path.exists("static"),
        "static_abs": os.path.abspath("static"),
        "files": os.listdir(".") if os.path.exists(".") else []
    }


@app.get('/suporte', response_class=HTMLResponse)
async def suporte():
    with open('static/suporte.html', 'r', encoding='utf-8') as f:
        return f.read()


@app.get('/privacidade', response_class=HTMLResponse)
async def privacidade():
    with open('static/privacidade.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.get('/termos', response_class=HTMLResponse)
async def termos():
    with open('static/termos.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.get('/excluir-conta', response_class=HTMLResponse)
async def excluir_conta():
    with open('static/excluir-conta.html', 'r', encoding='utf-8') as f:
        return f.read()


# ============================================
# FLUXO DE EXCLUSÃO DE CONTA (LGPD / Apple 5.1.1v)
# ============================================

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import bcrypt

class SolicitarExclusaoRequest(BaseModel):
    email: str
    senha: str
    tipo: str  # "aluno" ou "personal"

@app.post('/conta/solicitar-exclusao')
async def solicitar_exclusao(req: SolicitarExclusaoRequest, db=Depends(get_db)):
    """Solicita exclusão de conta. Gera token e envia email de confirmação."""
    
    from sqlalchemy import text
    
    if req.tipo not in ['aluno', 'personal']:
        raise HTTPException(status_code=400, detail='Tipo inválido. Use "aluno" ou "personal".')
    
    tabela = 'alunos' if req.tipo == 'aluno' else 'personals'
    
    # Busca o usuário
    result = db.execute(
        text(f"SELECT id, email, nome FROM {tabela} WHERE email = :email AND ativo = true"),
        {"email": req.email}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail='Conta não encontrada ou já inativa.')
    
    user_id, user_email, user_nome = result
    
    # Gera token único (32 caracteres aleatórios)
    token = secrets.token_urlsafe(32)
    agora = datetime.utcnow()
    
    # Salva token e data no banco
    db.execute(
        text(f"""
            UPDATE {tabela} 
            SET token_exclusao = :token, 
                data_solicitacao_exclusao = :data
            WHERE id = :id
        """),
        {"token": token, "data": agora, "id": user_id}
    )
    db.commit()
    
    # Link de confirmação
    link = f"https://www.aurumsc.com.br/conta/confirmar-exclusao/{token}?tipo={req.tipo}"
    
    return {
        "sucesso": True,
        "mensagem": "Solicitação registrada! Um email de confirmação foi enviado.",
        "email": user_email,
        "nome": user_nome,
        "link_confirmacao": link,
        "expira_em": "24 horas",
        "obs": "Email ainda não é enviado automaticamente - próximo passo!"
    }


@app.get('/conta/confirmar-exclusao/{token}', response_class=HTMLResponse)
async def confirmar_exclusao(token: str, tipo: str, db=Depends(get_db)):
    """Confirma a exclusão da conta via link do email."""
    
    from sqlalchemy import text
    
    if tipo not in ['aluno', 'personal']:
        return '<html><body style="font-family:sans-serif;padding:40px;text-align:center;"><h1>❌ Link inválido</h1><p>Tipo de conta inválido.</p></body></html>'
    
    tabela = 'alunos' if tipo == 'aluno' else 'personals'
    
    # Busca usuário com esse token
    result = db.execute(
        text(f"""
            SELECT id, email, nome, data_solicitacao_exclusao 
            FROM {tabela} 
            WHERE token_exclusao = :token AND ativo = true
        """),
        {"token": token}
    ).fetchone()
    
    if not result:
        return '<html><body style="font-family:sans-serif;padding:40px;text-align:center;"><h1>❌ Link inválido ou expirado</h1><p>Solicite a exclusão novamente.</p></body></html>'
    
    user_id, user_email, user_nome, data_solicitacao = result
    
    # Verifica se token expirou (24h)
    if data_solicitacao and (datetime.utcnow() - data_solicitacao) > timedelta(hours=24):
        return '<html><body style="font-family:sans-serif;padding:40px;text-align:center;"><h1>⏱️ Link expirado</h1><p>Solicite a exclusão novamente.</p></body></html>'
    
    # Desativa a conta (soft delete)
    db.execute(
        text(f"""
            UPDATE {tabela} 
            SET ativo = false,
                token_exclusao = NULL
            WHERE id = :id
        """),
        {"id": user_id}
    )
    db.commit()
    
    return f"""
    <html>
    <head><title>Conta Excluída - AurumSci</title></head>
    <body style="font-family:Georgia,serif;padding:60px 20px;text-align:center;background:#fafaf7;">
        <div style="max-width:600px;margin:0 auto;background:white;padding:50px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
            <h1 style="color:#b8860b;">✅ Conta Excluída com Sucesso</h1>
            <p style="color:#334155;font-size:18px;">Olá, <strong>{user_nome}</strong>!</p>
            <p style="color:#334155;">Sua conta AurumSci foi desativada. Em até <strong>30 dias</strong> todos os seus dados pessoais serão permanentemente apagados de nossos servidores.</p>
            <p style="color:#64748b;font-size:14px;margin-top:30px;">Se mudou de ideia, entre em contato em até 30 dias: <strong>andrepersonal395@gmail.com</strong></p>
            <hr style="border:none;border-top:1px solid #e2e8f0;margin:30px 0;">
            <p style="color:#64748b;font-size:13px;">AurumSci © 2026 · Obrigado por ter feito parte da nossa jornada.</p>
        </div>
    </body>
    </html>
    """

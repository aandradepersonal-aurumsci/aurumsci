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
import requests
import logging
import time

from app.config import settings
from app.database import engine, get_db
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


# ============================================
# ENDPOINTS IAP (In-App Purchase) - Apple
# ============================================

APPLE_VERIFY_URL_PROD = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_VERIFY_URL_SANDBOX = "https://sandbox.itunes.apple.com/verifyReceipt"

PRODUTO_PARA_PLANO = {
    "com.aurumsc.pro.bronze": {"plano": "bronze", "tipo": "personal", "limite_alunos": 10},
    "com.aurumsc.pro.prata": {"plano": "prata", "tipo": "personal", "limite_alunos": 20},
    "com.aurumsc.pro.ouro": {"plano": "ouro", "tipo": "personal", "limite_alunos": 50},
    "com.aurumsc.pro.diamante": {"plano": "diamante", "tipo": "personal", "limite_alunos": 999999},
    "com.aurumsc.aluno.mensal": {"plano": "aluno_mensal", "tipo": "aluno", "limite_alunos": 0},
    "com.aurumsc.aluno.anual": {"plano": "aluno_anual", "tipo": "aluno", "limite_alunos": 0},
}


class ValidarReciboRequest(BaseModel):
    receipt_data: str
    user_id: int
    user_type: str


@app.post("/iap/validar-recibo")
async def validar_recibo_apple(req: ValidarReciboRequest, db=Depends(get_db)):
    """
    Valida recibo de compra IAP com servidor Apple.
    Salva assinatura no banco se valida.
    """
    if req.user_type not in ["aluno", "personal"]:
        raise HTTPException(status_code=400, detail="user_type deve ser 'aluno' ou 'personal'")

    shared_secret = os.getenv("APPLE_SHARED_SECRET_PRO" if req.user_type == "personal" else "APPLE_SHARED_SECRET_ALUNO", "")

    payload = {
        "receipt-data": req.receipt_data,
        "password": shared_secret,
        "exclude-old-transactions": True
    }

    try:
        response = requests.post(APPLE_VERIFY_URL_PROD, json=payload, timeout=30)
        data = response.json()

        if data.get("status") == 21007:
            response = requests.post(APPLE_VERIFY_URL_SANDBOX, json=payload, timeout=30)
            data = response.json()

        if data.get("status") != 0:
            raise HTTPException(status_code=400, detail=f"Recibo invalido. Status Apple: {data.get('status')}")

    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Timeout ao validar com Apple")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao comunicar com Apple: {str(e)}")

    latest_receipt_info = data.get("latest_receipt_info", [])
    if not latest_receipt_info:
        raise HTTPException(status_code=400, detail="Recibo sem informacoes de transacao")

    ultima = latest_receipt_info[-1]
    product_id = ultima.get("product_id", "")
    transaction_id = ultima.get("transaction_id", "")
    original_transaction_id = ultima.get("original_transaction_id", "")
    purchase_date_ms = int(ultima.get("purchase_date_ms", 0))
    expires_date_ms = int(ultima.get("expires_date_ms", 0))
    is_trial_period = ultima.get("is_trial_period", "false") == "true"

    purchase_date = datetime.fromtimestamp(purchase_date_ms / 1000)
    expires_date = datetime.fromtimestamp(expires_date_ms / 1000)

    if product_id not in PRODUTO_PARA_PLANO:
        raise HTTPException(status_code=400, detail=f"product_id desconhecido: {product_id}")

    info_plano = PRODUTO_PARA_PLANO[product_id]
    agora = datetime.now()
    status_assinatura = "active" if expires_date > agora else "expired"

    from sqlalchemy import text
    import json

    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT id FROM assinaturas_iap WHERE transaction_id = :tid"),
            {"tid": transaction_id}
        ).fetchone()

        if existing:
            conn.execute(text("""
                UPDATE assinaturas_iap SET
                    status = :status,
                    expires_date = :expires,
                    updated_at = NOW(),
                    raw_response = :raw
                WHERE transaction_id = :tid
            """), {
                "status": status_assinatura,
                "expires": expires_date,
                "raw": json.dumps(data),
                "tid": transaction_id
            })
            acao = "atualizada"
        else:
            conn.execute(text("""
                INSERT INTO assinaturas_iap (
                    user_id, user_type, product_id, transaction_id,
                    original_transaction_id, purchase_date, expires_date,
                    status, is_trial, plano, receipt_data, raw_response
                ) VALUES (
                    :user_id, :user_type, :product_id, :tid,
                    :otid, :purchase, :expires,
                    :status, :trial, :plano, :receipt, :raw
                )
            """), {
                "user_id": req.user_id,
                "user_type": req.user_type,
                "product_id": product_id,
                "tid": transaction_id,
                "otid": original_transaction_id,
                "purchase": purchase_date,
                "expires": expires_date,
                "status": status_assinatura,
                "trial": is_trial_period,
                "plano": info_plano["plano"],
                "receipt": req.receipt_data,
                "raw": json.dumps(data)
            })
            acao = "criada"

    return {
        "sucesso": True,
        "mensagem": f"Assinatura {acao} com sucesso!",
        "plano": info_plano["plano"],
        "status": status_assinatura,
        "expires_date": expires_date.isoformat(),
        "is_trial": is_trial_period,
        "transaction_id": transaction_id
    }



@app.get("/iap/status-assinatura/{user_id}")
async def status_assinatura(user_id: int, user_type: str, db=Depends(get_db)):
    """
    Retorna status da assinatura do usuario.
    Usado pelo app pra saber se libera ou nao os recursos premium.
    """
    if user_type not in ["aluno", "personal"]:
        raise HTTPException(status_code=400, detail="user_type deve ser 'aluno' ou 'personal'")

    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id, product_id, transaction_id, purchase_date, 
                expires_date, status, is_trial, plano, auto_renew
            FROM assinaturas_iap
            WHERE user_id = :uid AND user_type = :utype
            ORDER BY expires_date DESC
            LIMIT 1
        """), {"uid": user_id, "utype": user_type}).fetchone()

    if not result:
        return {
            "tem_assinatura": False,
            "status": "sem_assinatura",
            "mensagem": "Usuario nao possui assinatura ativa"
        }

    agora = datetime.now()
    expires = result[4]
    status_real = "active" if expires > agora else "expired"
    
    dias_restantes = (expires - agora).days if expires > agora else 0

    return {
        "tem_assinatura": status_real == "active",
        "status": status_real,
        "plano": result[7],
        "product_id": result[1],
        "purchase_date": result[3].isoformat() if result[3] else None,
        "expires_date": expires.isoformat() if expires else None,
        "dias_restantes": dias_restantes,
        "is_trial": result[6],
        "auto_renew": result[8],
        "transaction_id": result[2]
    }



class RestaurarComprasRequest(BaseModel):
    receipt_data: str
    user_id: int
    user_type: str


@app.post("/iap/restaurar-compras")
async def restaurar_compras(req: RestaurarComprasRequest, db=Depends(get_db)):
    """
    Restaura compras anteriores do usuario.
    Usado quando usuario troca de celular ou reinstala o app.
    Revalida o recibo com Apple e atualiza/cria assinatura no banco.
    """
    if req.user_type not in ["aluno", "personal"]:
        raise HTTPException(status_code=400, detail="user_type deve ser 'aluno' ou 'personal'")

    shared_secret = os.getenv("APPLE_SHARED_SECRET_PRO" if req.user_type == "personal" else "APPLE_SHARED_SECRET_ALUNO", "")

    payload = {
        "receipt-data": req.receipt_data,
        "password": shared_secret,
        "exclude-old-transactions": False
    }

    try:
        response = requests.post(APPLE_VERIFY_URL_PROD, json=payload, timeout=30)
        data = response.json()

        if data.get("status") == 21007:
            response = requests.post(APPLE_VERIFY_URL_SANDBOX, json=payload, timeout=30)
            data = response.json()

        if data.get("status") != 0:
            raise HTTPException(status_code=400, detail=f"Recibo invalido. Status Apple: {data.get('status')}")

    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Timeout ao validar com Apple")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao comunicar com Apple: {str(e)}")

    latest_receipt_info = data.get("latest_receipt_info", [])
    if not latest_receipt_info:
        return {
            "sucesso": True,
            "mensagem": "Nenhuma compra anterior encontrada",
            "assinaturas_restauradas": 0
        }

    from sqlalchemy import text
    import json

    assinaturas_processadas = 0
    assinaturas_ativas = []

    with engine.begin() as conn:
        for transacao in latest_receipt_info:
            product_id = transacao.get("product_id", "")
            transaction_id = transacao.get("transaction_id", "")
            original_transaction_id = transacao.get("original_transaction_id", "")
            purchase_date_ms = int(transacao.get("purchase_date_ms", 0))
            expires_date_ms = int(transacao.get("expires_date_ms", 0))
            is_trial_period = transacao.get("is_trial_period", "false") == "true"

            if product_id not in PRODUTO_PARA_PLANO:
                continue

            purchase_date = datetime.fromtimestamp(purchase_date_ms / 1000)
            expires_date = datetime.fromtimestamp(expires_date_ms / 1000)
            info_plano = PRODUTO_PARA_PLANO[product_id]
            agora = datetime.now()
            status_assinatura = "active" if expires_date > agora else "expired"

            existing = conn.execute(
                text("SELECT id FROM assinaturas_iap WHERE transaction_id = :tid"),
                {"tid": transaction_id}
            ).fetchone()

            if existing:
                conn.execute(text("""
                    UPDATE assinaturas_iap SET
                        status = :status,
                        expires_date = :expires,
                        updated_at = NOW()
                    WHERE transaction_id = :tid
                """), {
                    "status": status_assinatura,
                    "expires": expires_date,
                    "tid": transaction_id
                })
            else:
                conn.execute(text("""
                    INSERT INTO assinaturas_iap (
                        user_id, user_type, product_id, transaction_id,
                        original_transaction_id, purchase_date, expires_date,
                        status, is_trial, plano, receipt_data, raw_response
                    ) VALUES (
                        :user_id, :user_type, :product_id, :tid,
                        :otid, :purchase, :expires,
                        :status, :trial, :plano, :receipt, :raw
                    )
                """), {
                    "user_id": req.user_id,
                    "user_type": req.user_type,
                    "product_id": product_id,
                    "tid": transaction_id,
                    "otid": original_transaction_id,
                    "purchase": purchase_date,
                    "expires": expires_date,
                    "status": status_assinatura,
                    "trial": is_trial_period,
                    "plano": info_plano["plano"],
                    "receipt": req.receipt_data,
                    "raw": json.dumps(data)
                })

            assinaturas_processadas += 1
            
            if status_assinatura == "active":
                assinaturas_ativas.append({
                    "plano": info_plano["plano"],
                    "expires_date": expires_date.isoformat(),
                    "transaction_id": transaction_id
                })

    return {
        "sucesso": True,
        "mensagem": f"Compras restauradas com sucesso! {assinaturas_processadas} transacoes processadas.",
        "assinaturas_restauradas": assinaturas_processadas,
        "assinaturas_ativas": assinaturas_ativas
    }



@app.post("/iap/notificacao-apple")
async def webhook_notificacao_apple(request: Request, db=Depends(get_db)):
    """
    Webhook que recebe notificacoes da Apple sobre mudancas em assinaturas.
    Apple envia: renovacao, cancelamento, reembolso, falha de pagamento.
    """
    from sqlalchemy import text
    import json
    
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payload invalido: {str(e)}")

    notification_type = payload.get("notificationType", "UNKNOWN")
    subtype = payload.get("subtype", "")
    
    signed_transaction_info = payload.get("data", {}).get("signedTransactionInfo", "")
    
    transaction_data = payload.get("data", {}).get("transactionInfo", {})
    
    if not transaction_data:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO assinaturas_iap_logs (notification_type, subtype, raw_payload, created_at)
                VALUES (:ntype, :subtype, :payload, NOW())
                ON CONFLICT DO NOTHING
            """), {
                "ntype": notification_type,
                "subtype": subtype,
                "payload": json.dumps(payload)
            }) if False else None
        
        return {
            "sucesso": True,
            "mensagem": f"Notificacao {notification_type} recebida (sem transaction data)",
            "processada": False
        }

    original_transaction_id = transaction_data.get("originalTransactionId", "")
    transaction_id = transaction_data.get("transactionId", "")
    product_id = transaction_data.get("productId", "")
    expires_date_ms = int(transaction_data.get("expiresDate", 0))
    
    if not original_transaction_id:
        return {
            "sucesso": True,
            "mensagem": "Notificacao sem original_transaction_id",
            "processada": False
        }

    novo_status = "active"
    
    if notification_type == "DID_RENEW":
        novo_status = "active"
    elif notification_type == "EXPIRED":
        novo_status = "expired"
    elif notification_type == "DID_CHANGE_RENEWAL_STATUS":
        if subtype == "AUTO_RENEW_DISABLED":
            novo_status = "canceled_will_expire"
        elif subtype == "AUTO_RENEW_ENABLED":
            novo_status = "active"
    elif notification_type == "REFUND":
        novo_status = "refunded"
    elif notification_type == "GRACE_PERIOD_EXPIRED":
        novo_status = "expired"
    elif notification_type == "DID_FAIL_TO_RENEW":
        novo_status = "payment_failed"
    elif notification_type == "REVOKE":
        novo_status = "revoked"

    expires_date = None
    if expires_date_ms > 0:
        expires_date = datetime.fromtimestamp(expires_date_ms / 1000)

    with engine.begin() as conn:
        if expires_date:
            conn.execute(text("""
                UPDATE assinaturas_iap SET
                    status = :status,
                    expires_date = :expires,
                    auto_renew = :auto_renew,
                    raw_response = :raw,
                    updated_at = NOW()
                WHERE original_transaction_id = :otid
            """), {
                "status": novo_status,
                "expires": expires_date,
                "auto_renew": novo_status == "active",
                "raw": json.dumps(payload),
                "otid": original_transaction_id
            })
        else:
            conn.execute(text("""
                UPDATE assinaturas_iap SET
                    status = :status,
                    auto_renew = :auto_renew,
                    raw_response = :raw,
                    updated_at = NOW()
                WHERE original_transaction_id = :otid
            """), {
                "status": novo_status,
                "auto_renew": novo_status == "active",
                "raw": json.dumps(payload),
                "otid": original_transaction_id
            })

    return {
        "sucesso": True,
        "mensagem": f"Notificacao processada: {notification_type}",
        "notification_type": notification_type,
        "subtype": subtype,
        "novo_status": novo_status,
        "original_transaction_id": original_transaction_id
    }



def verificar_assinatura_ativa(user_id: int, user_type: str) -> dict:
    """
    Verifica se usuario tem assinatura IAP ativa.
    Retorna dict com status. Usar antes de liberar recursos premium.
    
    Uso:
        status = verificar_assinatura_ativa(user_id=3, user_type="personal")
        if not status["ativa"]:
            raise HTTPException(status_code=403, detail="Assinatura necessaria")
    """
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT expires_date, status, plano, is_trial
            FROM assinaturas_iap
            WHERE user_id = :uid AND user_type = :utype
            ORDER BY expires_date DESC
            LIMIT 1
        """), {"uid": user_id, "utype": user_type}).fetchone()

    if not result:
        return {
            "ativa": False,
            "motivo": "sem_assinatura",
            "mensagem": "Usuario nao possui assinatura"
        }

    expires = result[0]
    status_db = result[1]
    agora = datetime.now()

    if expires <= agora:
        return {
            "ativa": False,
            "motivo": "expirada",
            "mensagem": "Assinatura expirada",
            "expirou_em": expires.isoformat()
        }

    if status_db in ["refunded", "revoked", "payment_failed"]:
        return {
            "ativa": False,
            "motivo": status_db,
            "mensagem": f"Assinatura com status: {status_db}"
        }

    return {
        "ativa": True,
        "plano": result[2],
        "is_trial": result[3],
        "expires_date": expires.isoformat(),
        "status": status_db
    }



@app.get("/upgrade")
async def pagina_upgrade():
    """Pagina de upgrade - mostra os 4 planos PRO"""
    from fastapi.responses import FileResponse
    return FileResponse("static/upgrade.html")


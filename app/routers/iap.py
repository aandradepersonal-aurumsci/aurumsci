"""
ROUTER IAP — Apple In-App Purchase
Cravado 23/05/2026 — Etapa 2 do IAP

Endpoints:
- POST /iap/validar-recibo  (frontend envia recibo Apple, backend valida)
- POST /iap/webhook-apple   (Apple notifica S2S - renovação, cancelamento, etc)
- GET  /iap/status          (verifica se tem assinatura ativa)

IMPORTANTE: precisa do APPLE_SHARED_SECRET no .env (cravado depois).
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AssinaturaIAP, Personal, Aluno
from app.routers.auth import get_personal_atual

router = APIRouter(prefix="/iap", tags=["IAP"])
log = logging.getLogger(__name__)

# URLs Apple oficiais
APPLE_PRODUCTION = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_SANDBOX = "https://sandbox.itunes.apple.com/verifyReceipt"

# Shared secret do App Store Connect (configurar no .env)
APPLE_SHARED_SECRET = os.getenv("APPLE_SHARED_SECRET", "SUBSTITUIR_DEPOIS")


# ──────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ──────────────────────────────────────────────────────────────────────────────
class ValidarReciboPayload(BaseModel):
    receipt_data: str  # Base64 do recibo enviado pelo app iOS
    aluno_id: Optional[int] = None  # Se for aluno autônomo


# ──────────────────────────────────────────────────────────────────────────────
# HELPER — Valida recibo com Apple (tenta produção, fallback sandbox)
# ──────────────────────────────────────────────────────────────────────────────
def validar_com_apple(receipt_data: str):
    """Valida recibo com servidor Apple. Tenta produção primeiro, se Apple
    responder status 21007, tenta sandbox (mais comum em desenvolvimento)."""
    payload = {
        "receipt-data": receipt_data,
        "password": APPLE_SHARED_SECRET,
        "exclude-old-transactions": True
    }
    
    # Tenta produção
    try:
        r = requests.post(APPLE_PRODUCTION, json=payload, timeout=30)
        data = r.json()
        if data.get("status") == 21007:
            # 21007 = recibo é de sandbox, tenta lá
            r = requests.post(APPLE_SANDBOX, json=payload, timeout=30)
            data = r.json()
            data["_ambiente"] = "sandbox"
        else:
            data["_ambiente"] = "production"
        return data
    except Exception as e:
        log.error(f"[IAP] Erro ao validar com Apple: {e}")
        raise HTTPException(500, f"Erro ao validar recibo com Apple: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# POST /iap/validar-recibo
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/validar-recibo")
def validar_recibo(
    payload: ValidarReciboPayload,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Recebe recibo do app iOS, valida com Apple, salva assinatura no banco."""
    
    resp = validar_com_apple(payload.receipt_data)
    
    if resp.get("status") != 0:
        raise HTTPException(400, f"Recibo inválido. Status Apple: {resp.get('status')}")
    
    # Pega último in-app purchase do recibo
    latest = resp.get("latest_receipt_info") or resp.get("receipt", {}).get("in_app", [])
    if not latest:
        raise HTTPException(400, "Recibo sem informação de compra")
    
    if isinstance(latest, list):
        latest = latest[-1]
    
    product_id = latest.get("product_id")
    transaction_id = latest.get("transaction_id")
    original_transaction_id = latest.get("original_transaction_id")
    purchase_date_ms = int(latest.get("purchase_date_ms", 0))
    expires_date_ms = int(latest.get("expires_date_ms", 0))
    
    data_compra = datetime.utcfromtimestamp(purchase_date_ms / 1000) if purchase_date_ms else datetime.utcnow()
    data_expiracao = datetime.utcfromtimestamp(expires_date_ms / 1000) if expires_date_ms else None
    
    # Status (trial vs ativo)
    is_trial = latest.get("is_trial_period") == "true"
    status = "trialing" if is_trial else "active"
    
    # Já existe essa transação? (idempotência)
    existente = db.query(AssinaturaIAP).filter(
        AssinaturaIAP.apple_transaction_id == transaction_id
    ).first()
    
    if existente:
        # Atualiza status e expiração
        existente.status = status
        existente.data_expiracao = data_expiracao
        existente.atualizado_em = datetime.utcnow()
        db.commit()
        return {"status": "ok", "tipo": "atualizado", "assinatura_id": existente.id}
    
    # Cria nova assinatura
    nova = AssinaturaIAP(
        personal_id=personal.id if not payload.aluno_id else None,
        aluno_id=payload.aluno_id,
        product_id=product_id,
        apple_transaction_id=transaction_id,
        apple_original_transaction_id=original_transaction_id,
        status=status,
        data_compra=data_compra,
        data_expiracao=data_expiracao,
        ambiente=resp.get("_ambiente", "sandbox"),
        receipt_data=payload.receipt_data[:5000],  # truncar pra não estourar
        auto_renew=True
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    
    return {"status": "ok", "tipo": "criado", "assinatura_id": nova.id}


# ──────────────────────────────────────────────────────────────────────────────
# POST /iap/webhook-apple — Server-to-Server notifications da Apple
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/webhook-apple")
async def webhook_apple(request: Request, db: Session = Depends(get_db)):
    """Apple notifica eventos: renovação, cancelamento, refund, expiração, etc."""
    
    body = await request.json()
    notification_type = body.get("notification_type", "")
    
    log.info(f"[IAP WEBHOOK] Tipo: {notification_type}")
    
    # Pega original_transaction_id pra achar a assinatura
    info = body.get("unified_receipt", {}).get("latest_receipt_info", [{}])[0]
    original_transaction_id = info.get("original_transaction_id")
    
    if not original_transaction_id:
        return {"status": "ignored", "motivo": "sem original_transaction_id"}
    
    # Acha assinatura
    assinatura = db.query(AssinaturaIAP).filter(
        AssinaturaIAP.apple_original_transaction_id == original_transaction_id
    ).first()
    
    if not assinatura:
        log.warning(f"[IAP WEBHOOK] Assinatura nao encontrada: {original_transaction_id}")
        return {"status": "ignored", "motivo": "assinatura nao encontrada"}
    
    # Atualiza status baseado no tipo
    if notification_type in ("CANCEL", "DID_CANCEL"):
        assinatura.status = "cancelled"
        assinatura.data_cancelamento = datetime.utcnow()
        assinatura.auto_renew = False
    elif notification_type == "DID_FAIL_TO_RENEW":
        assinatura.status = "expired"
        assinatura.auto_renew = False
    elif notification_type in ("DID_RENEW", "INTERACTIVE_RENEWAL"):
        assinatura.status = "active"
        expires_ms = int(info.get("expires_date_ms", 0))
        if expires_ms:
            assinatura.data_expiracao = datetime.utcfromtimestamp(expires_ms / 1000)
    elif notification_type == "REFUND":
        assinatura.status = "refunded"
    
    assinatura.atualizado_em = datetime.utcnow()
    db.commit()
    
    log.info(f"[IAP WEBHOOK] Assinatura {assinatura.id} atualizada: {assinatura.status}")
    return {"status": "ok"}


# ──────────────────────────────────────────────────────────────────────────────
# GET /iap/status — Trainer/aluno consulta se tem assinatura ativa
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/status")
def status_iap(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """Retorna se trainer tem assinatura IAP ativa (trialing ou active)."""
    
    assinatura = db.query(AssinaturaIAP).filter(
        AssinaturaIAP.personal_id == personal.id,
        AssinaturaIAP.status.in_(["trialing", "active"])
    ).order_by(AssinaturaIAP.data_expiracao.desc().nullslast()).first()
    
    if not assinatura:
        return {"tem_assinatura": False}
    
    return {
        "tem_assinatura": True,
        "status": assinatura.status,
        "product_id": assinatura.product_id,
        "data_expiracao": assinatura.data_expiracao.isoformat() if assinatura.data_expiracao else None,
        "auto_renew": assinatura.auto_renew,
        "ambiente": assinatura.ambiente
    }

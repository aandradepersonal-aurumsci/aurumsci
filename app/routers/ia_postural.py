"""
Router — Análise Postural com IA
POST /postural-ia/analisar  → envia fotos e recebe análise automática
POST /postural-ia/salvar    → salva resultado na avaliação

🧠 Usa motor/ia_postural.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import Personal, Aluno
from app.utils.auth import get_personal_atual

# 🧠 Motor AurumSci
from app.routers.ia_postural import analisar_postural, postural_to_dict

router = APIRouter(prefix="/postural-ia", tags=["Análise Postural com IA"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class FotosPosturais(BaseModel):
    foto_frente: Optional[str] = None   # base64
    foto_lado: Optional[str] = None     # base64
    foto_costas: Optional[str] = None   # base64


class SalvarPostural(BaseModel):
    avaliacao_id: int
    cabeca: Optional[str] = None
    ombros: Optional[str] = None
    coluna: Optional[str] = None
    quadril: Optional[str] = None
    joelhos: Optional[str] = None
    pes: Optional[str] = None
    observacoes: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/analisar")
async def analisar_fotos(
    dados: FotosPosturais,
    personal: Personal = Depends(get_personal_atual),
):
    """
    🧠 Motor AurumSci — Análise postural automática por IA
    Recebe fotos em base64 e retorna análise completa
    """
    if not any([dados.foto_frente, dados.foto_lado, dados.foto_costas]):
        raise HTTPException(
            status_code=400,
            detail="Pelo menos uma foto é necessária"
        )

    # 🧠 Motor analisa as fotos
    resultado = await analisar_postural(
        foto_frente=dados.foto_frente,
        foto_lado=dados.foto_lado,
        foto_costas=dados.foto_costas,
    )

    if resultado.erro:
        raise HTTPException(status_code=500, detail=resultado.erro)

    return {
        "sucesso": True,
        "analise": {
            "cabeca": resultado.cabeca,
            "ombros": resultado.ombros,
            "coluna": resultado.coluna,
            "quadril": resultado.quadril,
            "joelhos": resultado.joelhos,
            "pes": resultado.pes,
            "observacoes": resultado.observacoes,
            "recomendacoes": resultado.recomendacoes,
            "achados": resultado.achados,
        },
        "aviso": "Revise os campos antes de salvar. A IA pode cometer erros — você tem a palavra final."
    }


@router.post("/salvar")
def salvar_postural(
    dados: SalvarPostural,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    """
    Salva o resultado da análise postural na avaliação física
    """
    from app.routers.avaliacao import AvaliacaoFisica

    av = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.id == dados.avaliacao_id
    ).first()

    if not av:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")

    # Atualiza campos posturais
    if dados.cabeca:   av.postura_cabeca = dados.cabeca
    if dados.ombros:   av.postura_ombros = dados.ombros
    if dados.coluna:   av.postura_coluna = dados.coluna
    if dados.quadril:  av.postura_quadril = dados.quadril
    if dados.joelhos:  av.postura_joelhos = dados.joelhos
    if dados.pes:      av.postura_pes = dados.pes
    if dados.observacoes:
        obs_atual = av.observacoes or ""
        av.observacoes = obs_atual + f" [Postural IA: {dados.observacoes}]"

    db.commit()

    return {
        "mensagem": "Análise postural salva na avaliação com sucesso!",
        "avaliacao_id": dados.avaliacao_id
    }

"""
Router — Chatbot do Aluno
POST /chatbot/mensagem  → envia mensagem e recebe resposta da IA
GET  /chatbot/historico → histórico de mensagens do aluno

🧠 Usa motor/ia_chatbot.py
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from pydantic import BaseModel

from app.database import get_db
from app.models import Base, Aluno
from app.routers.portal_aluno import get_aluno_logado

# 🧠 Motor AurumSci
from app.motor.ia_chatbot import montar_contexto, responder_chatbot, resposta_rapida

router = APIRouter(prefix="/chatbot", tags=["Chatbot do Aluno"])


# ── Modelo ────────────────────────────────────────────────────────────────────

class MensagemChat(Base):
    __tablename__ = "mensagens_chat"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


# ── Schemas ───────────────────────────────────────────────────────────────────

class MensagemEntrada(BaseModel):
    mensagem: str


class MensagemSaida(BaseModel):
    resposta: str
    rapida: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/mensagem", response_model=MensagemSaida)
async def enviar_mensagem(
    dados: MensagemEntrada,
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """
    Aluno envia mensagem e recebe resposta da IA com contexto real
    """
    if not dados.mensagem.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    # Verifica resposta rápida primeiro (sem chamar API)
    resposta_r = resposta_rapida(dados.mensagem, {"nome": aluno.nome})
    if resposta_r:
        # Salva no histórico
        db.add(MensagemChat(aluno_id=aluno.id, role="user", content=dados.mensagem))
        db.add(MensagemChat(aluno_id=aluno.id, role="assistant", content=resposta_r))
        db.commit()
        return MensagemSaida(resposta=resposta_r, rapida=True)

    # Busca histórico das últimas 10 mensagens
    historico_db = db.query(MensagemChat).filter(
        MensagemChat.aluno_id == aluno.id
    ).order_by(MensagemChat.criado_em.desc()).limit(10).all()

    historico = [
        {"role": m.role, "content": m.content}
        for m in reversed(historico_db)
    ]

    # Busca contexto completo do aluno
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PlanoTreino, SessaoTreino, PresencaTreino
    from app.routers.financeiro import Pagamento, cs as calc_status

    # Avaliações
    avals_db = db.query(AvaliacaoFisica).filter(
        AvaliacaoFisica.aluno_id == aluno.id
    ).order_by(AvaliacaoFisica.data_avaliacao.desc()).limit(2).all()
    avaliacoes = [{
        "data": str(a.data_avaliacao),
        "peso": a.peso,
        "percentual_gordura": a.percentual_gordura,
        "classificacao_gordura": a.classificacao_gordura,
        "massa_magra_kg": a.massa_magra_kg,
        "imc": a.imc,
        "classificacao_imc": a.classificacao_imc,
        "vo2max": a.vo2max,
        "classificacao_vo2": a.classificacao_vo2,
    } for a in avals_db]

    # Treino ativo
    plano = db.query(PlanoTreino).filter(
        PlanoTreino.aluno_id == aluno.id,
        PlanoTreino.ativo == True
    ).order_by(PlanoTreino.criado_em.desc()).first()
    treino = {}
    if plano:
        sessoes = db.query(SessaoTreino).filter(SessaoTreino.plano_id == plano.id).all()
        treino = {
            "plano": {
                "nome": plano.nome,
                "objetivo": plano.objetivo,
                "dias_semana": plano.dias_semana,
                "semanas_total": plano.semanas_total,
            },
            "sessoes": [{"nome": s.nome} for s in sessoes],
        }

    # Presença
    presencas_db = db.query(PresencaTreino).filter(
        PresencaTreino.aluno_id == aluno.id
    ).all()
    total = len(presencas_db)
    presentes = sum(1 for p in presencas_db if p.presente)
    presencas = {
        "total_treinos": total,
        "presentes": presentes,
        "faltas": total - presentes,
        "frequencia_pct": round((presentes / total * 100), 1) if total > 0 else 0,
    }

    # Pagamentos
    pags_db = db.query(Pagamento).filter(Pagamento.aluno_id == aluno.id).all()
    pago = sum(p.valor for p in pags_db if calc_status(p) == "pago")
    pendente = sum(p.valor for p in pags_db if calc_status(p) == "pendente")
    atrasado = sum(p.valor for p in pags_db if calc_status(p) == "atrasado")
    pagamentos = {"resumo": {"pago": pago, "pendente": pendente, "atrasado": atrasado}}

    # Dados do aluno
    from datetime import date
    hoje = date.today()
    idade = None
    if aluno.data_nascimento:
        idade = hoje.year - aluno.data_nascimento.year - (
            (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)
        )

    aluno_dict = {
        "nome": aluno.nome,
        "idade": idade,
        "sexo": aluno.sexo.value if aluno.sexo else None,
        "objetivo": aluno.objetivo.value if aluno.objetivo else None,
        "nivel_experiencia": aluno.nivel_experiencia.value if aluno.nivel_experiencia else None,
    }

    # 🧠 Motor monta o contexto
    contexto = montar_contexto(
        aluno=aluno_dict,
        avaliacoes=avaliacoes,
        treino=treino,
        pagamentos=pagamentos,
        presencas=presencas,
    )

    # 🧠 Motor chama a IA
    resposta = await responder_chatbot(
        mensagem=dados.mensagem,
        historico=historico,
        contexto=contexto,
        nome_personal="seu personal trainer",
    )

    # Salva no histórico
    db.add(MensagemChat(aluno_id=aluno.id, role="user", content=dados.mensagem))
    db.add(MensagemChat(aluno_id=aluno.id, role="assistant", content=resposta))
    db.commit()

    return MensagemSaida(resposta=resposta)


@router.get("/historico")
def historico_chat(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Retorna histórico de mensagens do aluno"""
    msgs = db.query(MensagemChat).filter(
        MensagemChat.aluno_id == aluno.id
    ).order_by(MensagemChat.criado_em.asc()).limit(50).all()

    return {
        "total": len(msgs),
        "mensagens": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "criado_em": str(m.criado_em),
            }
            for m in msgs
        ]
    }


@router.delete("/historico")
def limpar_historico(
    aluno: Aluno = Depends(get_aluno_logado),
    db: Session = Depends(get_db)
):
    """Limpa histórico de chat do aluno"""
    db.query(MensagemChat).filter(MensagemChat.aluno_id == aluno.id).delete()
    db.commit()
    return {"mensagem": "Histórico limpo com sucesso"}

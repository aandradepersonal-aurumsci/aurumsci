from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings
from app.database import get_db
from app.models import Personal, Aluno
from app.utils.auth import get_personal_atual
from sqlalchemy.orm import Session
from datetime import datetime
import stripe
from app.services.email_service import enviar_email

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/pagamento", tags=["Pagamento"])


# ============================================================
# MAPA DE PLANOS PRO - Price IDs criados no Stripe em 01/05/2026
# ============================================================
PLANOS_PRO = {
    "bronze":   {"price_id": settings.STRIPE_PRICE_BRONZE,   "valor": 4990,  "limite_alunos": 10,   "nome": "Bronze",   "icone": "🥉", "cor": "#CD7F32", "frase": "Voce comecou. Agora e ritmo."},
    "prata":    {"price_id": settings.STRIPE_PRICE_PRATA,    "valor": 8990,  "limite_alunos": 20,   "nome": "Prata",    "icone": "🥈", "cor": "#C0C0C0", "frase": "Voce cresceu. O movimento comecou."},
    "ouro":     {"price_id": settings.STRIPE_PRICE_OURO,     "valor": 14990, "limite_alunos": 50,   "nome": "Ouro",     "icone": "🥇", "cor": "#C9A84C", "frase": "Voce esta na elite. 50 alunos te esperam."},
    "diamante": {"price_id": settings.STRIPE_PRICE_DIAMANTE, "valor": 24990, "limite_alunos": 9999, "nome": "Diamante", "icone": "💎", "cor": "#B9F2FF", "frase": "Voce e ELITE. Sem limites. Bem-vindo ao topo."},
}


class CheckoutSchema(BaseModel):
    aluno_id: int
    plano: str = "Plano Mensal AurumSci"
    valor: int = 4990


def enviar_email_boas_vindas(nome, email, link_onboarding=None):
    # FIX 16/05/2026: aceita link_onboarding opcional pra aluno autonomo completar cadastro
    bloco_link = ""
    if link_onboarding:
        bloco_link = f"""
    <div style="background:#12121A;border:1px solid #C9A84C;border-radius:16px;padding:24px;margin-bottom:20px;text-align:center;">
      <div style="font-size:18px;font-weight:700;color:#C9A84C;margin-bottom:8px;">📋 PRIMEIRO PASSO</div>
      <p style="color:#ccc;line-height:1.7;font-size:14px;margin:0 0 16px 0;">
        Preencha seu cadastro em <strong style="color:#C9A84C;">3 minutos</strong> e abra o app com seu <strong style="color:#C9A84C;">treino pronto pra começar</strong>!
      </p>
      <a href="{link_onboarding}" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:900;font-size:14px;letter-spacing:2px;">COMPLETAR CADASTRO →</a>
    </div>
    """
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">CIENCIA QUE VIRA RESULTADO</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Bem-vindo a familia, {nome}! 🏆</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0;">
        A partir de agora voce esta treinando com <strong style="color:#C9A84C;">ciencia, metodo e inteligencia artificial.</strong>
      </p>
    </div>
    {bloco_link}
    <div style="text-align:center;margin-bottom:24px;">
      <a href="https://www.aurumsc.com.br/aluno" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">COMECAR AGORA →</a>
    </div>
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;">Trial de 7 dias gratis. Apos esse periodo, R$49,90/mes sera cobrado automaticamente.<br>
      Cancele quando quiser, sem burocracia.<br><br>
      <strong style="color:#C9A84C;">Equipe AurumSci</strong> — Ciencia que vira resultado.</p>
    </div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto="Bem-vindo a Familia AurumSci! 🏆", html=html)


def enviar_email_boas_vindas_aluno(nome, email):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Ola, {nome}! Seu treino esta esperando por voce 🏋️</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">
        Seu personal trainer criou seu acesso ao <strong style="color:#C9A84C;">AurumSci</strong>.
      </p>
      <div style="background:#0A0A0F;border-radius:12px;padding:20px;margin-bottom:20px;">
        <div style="font-size:13px;color:#C9A84C;font-weight:700;margin-bottom:12px;letter-spacing:2px;">COMO ACESSAR:</div>
        <div style="color:#ccc;font-size:14px;line-height:2;">
          1️⃣ Acesse: <a href="https://aurumsc.com.br/aluno" style="color:#C9A84C;">aurumsc.com.br/aluno</a><br>
          2️⃣ Use seu email: <strong style="color:#fff;">{email}</strong><br>
          3️⃣ Sua senha sao os <strong style="color:#C9A84C;">6 primeiros digitos do seu CPF</strong><br>
          4️⃣ Troque sua senha apos o primeiro acesso
        </div>
      </div>
      <div style="background:#0d1a0d;border:1px solid #1a3a1a;border-radius:12px;padding:16px;">
        <div style="font-size:13px;color:#00E5A0;font-weight:700;margin-bottom:8px;">📱 NO SEU CELULAR:</div>
        <div style="color:#ccc;font-size:13px;line-height:1.8;">
          Abra o Safari (iPhone) ou Chrome (Android)<br>
          Acesse aurumsc.com.br/aluno<br>
          Adicione a tela inicial para ter como app!
        </div>
      </div>
    </div>
    <div style="text-align:center;color:#444;font-size:12px;">AurumSci — aurumsc.com.br</div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto="Seu personal criou seu acesso AurumSci! 💪", html=html)


def enviar_email_boas_vindas_personal(nome, email, plano="bronze"):
    plano = (plano or "bronze").lower().strip()
    if plano not in PLANOS_PRO:
        plano = "bronze"
    info = PLANOS_PRO[plano]
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">PRO — PARA PERSONAL TRAINERS</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Bem-vindo, {nome}! Plano {info['nome']} {info['icone']} ativado 🏆</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">Seu acesso ao <strong style="color:#C9A84C;">AurumSci PRO</strong> esta ativo com 7 dias gratis.</p>
      <div style="background:#0A0A0F;border-radius:12px;padding:20px;">
        <div style="font-size:13px;color:#C9A84C;font-weight:700;margin-bottom:12px;">COMO COMECAR:</div>
        <div style="color:#ccc;font-size:14px;line-height:2;">
          1️⃣ Acesse: <a href="https://aurumsc.com.br/personal" style="color:#C9A84C;">aurumsc.com.br/personal</a><br>
          2️⃣ Va em ALUNOS → Novo Aluno<br>
          3️⃣ Cadastre com CPF — senha gerada automaticamente<br>
          4️⃣ Envie o link para o aluno via WhatsApp
        </div>
      </div>
    </div>
    <div style="text-align:center;margin-bottom:24px;">
      <a href="https://aurumsc.com.br/personal" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">ACESSAR O PRO →</a>
    </div>
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;">7 dias gratis. Apos esse periodo, R${info['valor']/100:.2f}/mes sera cobrado automaticamente.<br>
      <strong style="color:#C9A84C;">Equipe AurumSci</strong></p>
    </div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto=f"Bem-vindo ao AurumSci PRO! Plano {info['nome']} {info['icone']} ativado 🏆", html=html)


# ============================================================
# EMAIL EPICO DE MUDANCA DE PLANO - "Voce agora e OURO 🏆"
# ============================================================
def enviar_email_mudanca_plano(nome, email, novo_plano):
    plano = (novo_plano or "bronze").lower().strip()
    if plano not in PLANOS_PRO:
        plano = "bronze"
    info = PLANOS_PRO[plano]
    primeiro_nome = nome.split()[0] if nome else "Personal"

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">PRO — PARA PERSONAL TRAINERS</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>

    <div style="text-align:center;margin-bottom:32px;padding:32px 20px;background:linear-gradient(135deg,rgba(201,168,76,0.15),rgba(201,168,76,0.03));border:2px solid {info['cor']};border-radius:20px;">
      <div style="font-size:64px;margin-bottom:12px;">{info['icone']}</div>
      <div style="font-family:Georgia,serif;font-size:14px;color:#888;letter-spacing:6px;margin-bottom:8px;">VOCE AGORA E</div>
      <div style="font-family:Georgia,serif;font-size:48px;font-weight:900;color:{info['cor']};letter-spacing:8px;line-height:1;margin-bottom:16px;">{info['nome'].upper()}</div>
      <div style="font-size:13px;color:#aaa;font-style:italic;line-height:1.6;max-width:380px;margin:0 auto;">{info['frase']}</div>
    </div>

    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:18px;color:#fff;margin-bottom:16px;">Parabens, <strong style="color:{info['cor']};">{primeiro_nome}</strong>! 🎉</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">
        Voce acaba de evoluir no AurumSci PRO. Agora voce tem acesso a <strong style="color:{info['cor']};">{info['nome']}</strong>:
      </p>
      <div style="background:#0A0A0F;border-radius:12px;padding:20px;margin-top:16px;">
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2A2A3A;">
          <span style="color:#888;font-size:13px;">Limite de alunos:</span>
          <strong style="color:{info['cor']};font-size:14px;">{info['limite_alunos'] if info['limite_alunos'] < 9999 else 'ILIMITADO'}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2A2A3A;">
          <span style="color:#888;font-size:13px;">Valor mensal:</span>
          <strong style="color:{info['cor']};font-size:14px;">R$ {info['valor']/100:.2f}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;padding:8px 0;">
          <span style="color:#888;font-size:13px;">Funcionalidades:</span>
          <strong style="color:#00E5A0;font-size:14px;">TODAS desbloqueadas</strong>
        </div>
      </div>
    </div>

    <div style="text-align:center;margin-bottom:24px;">
      <a href="https://aurumsc.com.br/personal" style="display:inline-block;background:linear-gradient(135deg,{info['cor']},#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;box-shadow:0 4px 16px rgba(201,168,76,0.3);">ACESSAR MEU PRO →</a>
    </div>

    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;line-height:1.8;">A cobranca proporcional sera aplicada na proxima fatura.<br>
      Voce pode mudar ou cancelar quando quiser, direto pelo app.<br><br>
      <strong style="color:#C9A84C;">Equipe AurumSci</strong> — Ciencia que vira resultado.</p>
    </div>
  </div>
</body></html>"""

    assunto = f"{info['icone']} Voce agora e {info['nome'].upper()} — AurumSci PRO"
    try:
        enviar_email(para=email, assunto=assunto, html=html)
    except Exception:
        pass


# ============================================================
# SCHEMAS
# ============================================================
class CheckoutPersonalSchema(BaseModel):
    personal_id: int
    plano: str = "bronze"
    valor: int = 4990


class MudarPlanoSchema(BaseModel):
    novo_plano: str  # bronze/prata/ouro/diamante


# ============================================================
# CHECKOUT - ALUNO (mantido)
# ============================================================
@router.post("/criar-sessao")
def criar_sessao(dados: CheckoutSchema, db: Session = Depends(get_db)):
    try:
        aluno = db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno nao encontrado")
        if aluno.stripe_subscription_id:
            try:
                sub = stripe.Subscription.retrieve(aluno.stripe_subscription_id)
                if sub.status in ["active", "trialing", "past_due"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Voce ja tem uma assinatura {sub.status}. Acesse o portal do cliente para gerenciar."
                    )
            except stripe.error.InvalidRequestError:
                pass
        # Validacao: Price ID configurado?
        if not settings.STRIPE_PRICE_ALUNO:
            raise HTTPException(status_code=500, detail="Plano Aluno nao configurado. Contate o suporte.")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": settings.STRIPE_PRICE_ALUNO,
                "quantity": 1
            }],
            mode="subscription",
            subscription_data={"trial_period_days": 7},
            success_url="https://www.aurumsc.com.br/aluno?pagamento=sucesso",
            cancel_url="https://www.aurumsc.com.br/aluno?pagamento=cancelado",
            metadata={"aluno_id": str(dados.aluno_id), "produto": "aluno"},
        )
        return {"url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# CHECKOUT - PERSONAL (Price IDs) - mantido pra cadastro novo
# ============================================================
@router.post("/criar-sessao-personal")
def criar_sessao_personal(dados: CheckoutPersonalSchema, db: Session = Depends(get_db)):
    try:
        personal = db.query(Personal).filter(Personal.id == dados.personal_id).first()
        if not personal:
            raise HTTPException(status_code=404, detail="Personal nao encontrado")

        plano_normalizado = dados.plano.lower().strip()
        if plano_normalizado not in PLANOS_PRO:
            raise HTTPException(status_code=400, detail=f"Plano '{dados.plano}' invalido. Opcoes: bronze/prata/ouro/diamante")

        plano_info = PLANOS_PRO[plano_normalizado]
        if not plano_info["price_id"]:
            raise HTTPException(status_code=500, detail=f"Price ID do plano {plano_normalizado} nao configurado nas variaveis de ambiente")

        if personal.stripe_subscription_id:
            try:
                sub = stripe.Subscription.retrieve(personal.stripe_subscription_id)
                if sub.status in ["active", "trialing", "past_due"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Voce ja tem uma assinatura {sub.status}. Use 'Mudar de Plano' para alterar."
                    )
            except stripe.error.InvalidRequestError:
                pass

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": plano_info["price_id"],
                "quantity": 1
            }],
            mode="subscription",
            subscription_data={"trial_period_days": 7},
            success_url="https://www.aurumsc.com.br/personal?cadastro=sucesso",
            cancel_url="https://www.aurumsc.com.br/pro",
            metadata={"personal_id": str(dados.personal_id), "plano": plano_normalizado},
        )
        return {"url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# GET /pagamento/meu-plano (autenticado por token)
# ============================================================
@router.get("/meu-plano")
def meu_plano(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    try:
        plano_atual = (personal.plano or "bronze").lower().strip()
        if plano_atual not in PLANOS_PRO:
            plano_atual = "bronze"

        plano_info = PLANOS_PRO[plano_atual]
        total_alunos = db.query(Aluno).filter(Aluno.personal_id == personal.id, Aluno.ativo == True).count()

        stripe_info = None
        if personal.stripe_subscription_id:
            try:
                sub = stripe.Subscription.retrieve(personal.stripe_subscription_id)
                stripe_info = {
                    "status": sub.status,
                    "cancel_at_period_end": sub.cancel_at_period_end,
                    "current_period_end": sub.current_period_end,
                }
            except stripe.error.InvalidRequestError:
                stripe_info = {"status": "nao_encontrada"}

        return {
            "personal_id": personal.id,
            "nome": personal.nome,
            "plano_atual": plano_atual,
            "nome_plano": plano_info["nome"],
            "icone": plano_info["icone"],
            "cor": plano_info["cor"],
            "valor_mensal": plano_info["valor"] / 100,
            "limite_alunos": plano_info["limite_alunos"],
            "alunos_ativos": total_alunos,
            "alunos_disponiveis": max(0, plano_info["limite_alunos"] - total_alunos),
            "assinatura_status": personal.assinatura_status,
            "stripe": stripe_info,
            "planos_disponiveis": [
                {
                    "id": k,
                    "nome": v["nome"],
                    "icone": v["icone"],
                    "cor": v["cor"],
                    "valor": v["valor"] / 100,
                    "limite_alunos": v["limite_alunos"],
                    "atual": (k == plano_atual)
                }
                for k, v in PLANOS_PRO.items()
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# POST /pagamento/mudar-plano (autenticado por token)
# ============================================================
@router.post("/mudar-plano")
def mudar_plano(
    dados: MudarPlanoSchema,
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    try:
        novo_plano = dados.novo_plano.lower().strip()
        if novo_plano not in PLANOS_PRO:
            raise HTTPException(status_code=400, detail=f"Plano '{dados.novo_plano}' invalido")

        plano_info = PLANOS_PRO[novo_plano]
        if not plano_info["price_id"]:
            raise HTTPException(status_code=500, detail=f"Price ID do plano {novo_plano} nao configurado")

        if (personal.plano or "").lower() == novo_plano:
            return {"status": "ok", "mensagem": f"Voce ja esta no plano {plano_info['nome']}", "plano": novo_plano}

        total_alunos = db.query(Aluno).filter(Aluno.personal_id == personal.id, Aluno.ativo == True).count()
        if total_alunos > plano_info["limite_alunos"]:
            raise HTTPException(
                status_code=400,
                detail=f"Voce tem {total_alunos} alunos ativos. O plano {plano_info['nome']} permite ate {plano_info['limite_alunos']}. Inative alguns alunos antes de fazer downgrade."
            )

        if not personal.stripe_subscription_id:
            personal.plano = novo_plano
            db.commit()
            enviar_email_mudanca_plano(personal.nome, personal.email, novo_plano)
            return {"status": "ok", "mensagem": f"Plano atualizado para {plano_info['nome']}", "plano": novo_plano}

        try:
            sub = stripe.Subscription.retrieve(personal.stripe_subscription_id)
        except stripe.error.InvalidRequestError:
            raise HTTPException(status_code=404, detail="Assinatura nao encontrada no Stripe. Refaca o checkout.")

        item_id = sub["items"]["data"][0]["id"]
        stripe.Subscription.modify(
            personal.stripe_subscription_id,
            items=[{
                "id": item_id,
                "price": plano_info["price_id"]
            }],
            proration_behavior="create_prorations"
        )

        personal.plano = novo_plano
        personal.assinatura_status = "ativa"
        db.commit()

        enviar_email_mudanca_plano(personal.nome, personal.email, novo_plano)

        return {
            "status": "ok",
            "mensagem": f"Voce agora e {plano_info['nome']} {plano_info['icone']}",
            "plano": novo_plano,
            "icone": plano_info["icone"],
            "valor_mensal": plano_info["valor"] / 100,
            "limite_alunos": plano_info["limite_alunos"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# POST /pagamento/cancelar-assinatura (autenticado por token)
# ============================================================
@router.post("/cancelar-assinatura")
def cancelar_assinatura(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    try:
        if not personal.stripe_subscription_id:
            raise HTTPException(status_code=400, detail="Voce nao tem assinatura ativa")

        try:
            stripe.Subscription.modify(
                personal.stripe_subscription_id,
                cancel_at_period_end=True
            )
        except stripe.error.InvalidRequestError as e:
            raise HTTPException(status_code=404, detail=f"Erro no Stripe: {str(e)}")

        personal.assinatura_status = "cancelamento_agendado"
        db.commit()

        try:
            primeiro_nome = personal.nome.split()[0] if personal.nome else "Personal"
            html_cancel = f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
            <h2 style='color:#C9A84C'>Cancelamento agendado, {primeiro_nome}</h2>
            <p style='color:#ccc;font-size:15px'>Sua assinatura sera cancelada ao final do periodo atual.</p>
            <p style='color:#ccc;font-size:14px'>Voce continua tendo acesso ate la. Mudou de ideia?</p>
            <a href='https://aurumsc.com.br/personal' style='display:inline-block;background:#C9A84C;color:#000;padding:14px 24px;border-radius:10px;text-decoration:none;font-weight:900;margin-top:16px'>VOLTAR AO APP</a>
            </body></html>"""
            enviar_email(para=personal.email, assunto="Cancelamento agendado — AurumSci PRO", html=html_cancel)
        except Exception:
            pass

        return {
            "status": "ok",
            "mensagem": "Cancelamento agendado. Voce mantem acesso ate o fim do periodo atual.",
            "cancelamento_agendado": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# POST /pagamento/reativar-assinatura (autenticado por token)
# ============================================================
@router.post("/reativar-assinatura")
def reativar_assinatura(
    personal: Personal = Depends(get_personal_atual),
    db: Session = Depends(get_db)
):
    try:
        if not personal.stripe_subscription_id:
            raise HTTPException(status_code=400, detail="Voce nao tem assinatura para reativar")

        try:
            stripe.Subscription.modify(
                personal.stripe_subscription_id,
                cancel_at_period_end=False
            )
        except stripe.error.InvalidRequestError as e:
            raise HTTPException(status_code=404, detail=f"Erro no Stripe: {str(e)}")

        personal.assinatura_status = "ativa"
        db.commit()

        return {"status": "ok", "mensagem": "Assinatura reativada com sucesso!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# WEBHOOK Stripe (mantido)
# ============================================================
@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # BUG FIX 04/05/2026: cobranca avulsa (sem subscription)
        # Detecta cobranca avulsa, atualiza status + envia recibo automatico
        try:
            try:
                session_id = session["id"]
            except (KeyError, AttributeError):
                session_id = None
            try:
                _has_sub = bool(session["subscription"])
            except (KeyError, AttributeError):
                _has_sub = False
            if session_id and not _has_sub:
                from sqlalchemy import text
                from datetime import date, datetime
                
                # Busca cobranca pelo stripe_invoice_id (que e o session_id)
                cobranca = db.execute(text("""
                    SELECT id, aluno_id, valor, descricao, status 
                    FROM cobrancas 
                    WHERE stripe_invoice_id = :sid
                """), {"sid": session_id}).fetchone()
                
                if cobranca and cobranca[4] != "pago":
                    # Atualiza status na tabela cobrancas
                    db.execute(text("""
                        UPDATE cobrancas 
                        SET status = 'pago', 
                            data_pagamento = :hoje,
                            metodo_pagamento = 'cartao',
                            atualizado_em = NOW()
                        WHERE id = :cid
                    """), {"hoje": date.today(), "cid": cobranca[0]})
                    db.commit()
                    print(f"[WEBHOOK STRIPE] Cobranca {cobranca[0]} marcada como PAGA")
                    
                    # Busca aluno e personal
                    aluno_cob = db.query(Aluno).filter(Aluno.id == cobranca[1]).first()
                    if aluno_cob and aluno_cob.email:
                        personal_cob = db.query(Personal).filter(Personal.id == aluno_cob.personal_id).first()
                        
                        # Envia email automatico (HTML inline - mesmo template do enviar_recibo_email)
                        # FIX 13/05/2026: removido 'from app.services.email_service import enviar_email'
                        # daqui - estava sombreando o import global (linha 10) e causando
                        # UnboundLocalError na linha 694 (webhook crashava em retry, Stripe
                        # reentregava evento por 3 dias, gerando emails diarios duplicados).
                        try:
                            numero_recibo = f"REC-{datetime.now().strftime('%y%m%d%H%M')}"
                            valor = float(cobranca[2])
                            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            tributos = valor * 0.06
                            tributos_fmt = f"R$ {tributos:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            descricao = cobranca[3] or "Personal Training"
                            data_pag = date.today().strftime("%d/%m/%Y")
                            personal_nome = personal_cob.nome if personal_cob else "Personal"
                            
                            corpo_html = f"""
                            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0A0A0F;color:#fff;padding:30px;border-radius:12px">
                              <div style="text-align:center;margin-bottom:30px">
                                <h1 style="color:#C9A84C;font-size:32px;letter-spacing:3px;margin:0">AURUMSCI</h1>
                                <p style="color:#888;font-size:11px;letter-spacing:2px;margin:5px 0">CIENCIA QUE VIRA RESULTADO</p>
                                <p style="color:#4CAF50;font-size:13px;margin-top:10px">PAGAMENTO CONFIRMADO</p>
                              </div>
                              <div style="background:#12121A;border:2px solid #C9A84C;border-radius:12px;padding:24px;margin-bottom:20px">
                                <div style="text-align:center;margin-bottom:20px">
                                  <div style="font-size:11px;color:#C9A84C;letter-spacing:2px">RECIBO DE PAGAMENTO</div>
                                  <div style="font-size:14px;color:#fff;margin-top:4px">{numero_recibo}</div>
                                </div>
                                <div style="border-top:1px solid #333;border-bottom:1px solid #333;padding:16px 0;margin:16px 0">
                                  <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:4px">PRESTADOR</div>
                                  <div style="font-size:15px;color:#fff;margin-bottom:12px">{personal_nome}</div>
                                  <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:4px">TOMADOR</div>
                                  <div style="font-size:15px;color:#fff">{aluno_cob.nome}</div>
                                </div>
                                <div style="margin:16px 0">
                                  <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:4px">DESCRICAO</div>
                                  <div style="font-size:14px;color:#fff;margin-bottom:12px">{descricao}</div>
                                  <div style="font-size:11px;color:#888;letter-spacing:1px;margin-bottom:4px">DATA</div>
                                  <div style="font-size:14px;color:#fff">{data_pag}</div>
                                </div>
                                <div style="background:linear-gradient(135deg,#C9A84C,#E5C76B);padding:20px;border-radius:8px;text-align:center;margin:20px 0">
                                  <div style="font-size:11px;color:#0A0A0F;letter-spacing:2px;margin-bottom:4px">VALOR PAGO</div>
                                  <div style="font-size:32px;color:#0A0A0F;font-weight:bold">{valor_fmt}</div>
                                </div>
                                <div style="background:rgba(201,168,76,.05);padding:12px;border-radius:8px;font-size:11px;color:#888;line-height:1.6">
                                  <b style="color:#C9A84C">Tributos estimados (Simples Nacional):</b><br>
                                  DAS ~6%: {tributos_fmt}<br>
                                  <i>Valores aproximados. Consulte seu contador.</i>
                                </div>
                              </div>
                              <div style="text-align:center;color:#888;font-size:11px;line-height:1.6">
                                <p>Recibo gerado automaticamente apos confirmacao de pagamento</p>
                                <p style="margin-top:20px;color:#C9A84C">aurumsc.com.br</p>
                              </div>
                            </div>
                            """
                            
                            assunto = f"Pagamento Confirmado - {numero_recibo}"
                            
                            # Email pro aluno
                            enviar_email(aluno_cob.email, assunto, corpo_html)
                            print(f"[WEBHOOK STRIPE] Recibo enviado pra ALUNO: {aluno_cob.email}")
                            
                            # Email pro personal (copia pro contador)
                            if personal_cob and personal_cob.email:
                                assunto_p = f"[COPIA] Pagamento recebido de {aluno_cob.nome} - {valor_fmt}"
                                enviar_email(personal_cob.email, assunto_p, corpo_html)
                                print(f"[WEBHOOK STRIPE] Copia enviada pro PERSONAL: {personal_cob.email}")
                        except Exception as e_email:
                            print(f"[WEBHOOK STRIPE] Erro ao enviar email: {e_email}")
        except Exception as e:
            print(f"[WEBHOOK STRIPE] Erro cobranca avulsa: {e}")
        
        aluno_id = None
        try:
            aluno_id = session["metadata"]["aluno_id"]
        except Exception:
            pass
        if aluno_id:
            aluno = db.query(Aluno).filter(Aluno.id == int(aluno_id)).first()
            if aluno:
                aluno.ativo = True
                try:
                    if session["subscription"]:
                        aluno.stripe_subscription_id = session["subscription"]
                except (KeyError, AttributeError):
                    pass
                try:
                    if session["customer"]:
                        aluno.stripe_customer_id = session["customer"]
                except (KeyError, AttributeError):
                    pass
                db.commit()
                # ALUNO AUTONOMO - tracking de trial
                # FIX 16/05/2026: importa datetime junto (shadowing causava UnboundLocalError 500)
                from datetime import timedelta, datetime
                aluno.assinatura_status = "trialing"
                aluno.data_inicio_trial = datetime.utcnow()
                aluno.data_fim_trial = datetime.utcnow() + timedelta(days=7)
                aluno.valor_assinatura = 4990
                db.commit()
                # FIX 16/05/2026: gera link onboarding autonomo e envia no email
                link_onboarding = None
                try:
                    import secrets as _secrets, os as _os
                    from app.models import OnboardingLink as _OnbLink
                    token_auto = _secrets.token_urlsafe(16)
                    novo_link = _OnbLink(
                        personal_id=None,
                        token=token_auto,
                        ativo=True,
                        total_usos=0
                    )
                    db.add(novo_link)
                    db.commit()
                    base_url = _os.getenv("BASE_URL", "https://www.aurumsc.com.br")
                    link_onboarding = f"{base_url}/onboarding/{token_auto}"
                    print(f"[WEBHOOK] Link onboarding gerado pro aluno {aluno.id}: {link_onboarding}")
                except Exception as e_link:
                    print(f"[WEBHOOK] Erro gerar link onboarding: {e_link}")
                enviar_email_boas_vindas(aluno.nome, aluno.email, link_onboarding=link_onboarding)

        personal_id = None
        plano = "bronze"
        try:
            personal_id = session["metadata"]["personal_id"]
            plano = session["metadata"].get("plano", "bronze")
        except Exception:
            pass
        if personal_id:
            personal = db.query(Personal).filter(Personal.id == int(personal_id)).first()
            if personal:
                personal.ativo = True
                personal.plano = plano
                personal.assinatura_status = "ativa"
                try:
                    if session["subscription"]:
                        personal.stripe_subscription_id = session["subscription"]
                except (KeyError, AttributeError):
                    pass
                try:
                    if session["customer"]:
                        personal.stripe_customer_id = session["customer"]
                except (KeyError, AttributeError):
                    pass
                db.commit()
                enviar_email_boas_vindas_personal(personal.nome, personal.email, plano)
                enviar_email(
                    para="a.andrade_personal@hotmail.com",
                    assunto=f"🎉 Novo personal assinou! {personal.nome} — Plano {plano.capitalize()}",
                    html=f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                    <h2 style='color:#C9A84C'>🎉 Novo personal no AURUM!</h2>
                    <div style='background:#12121A;border-radius:12px;padding:20px;margin:16px 0'>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Nome:</strong> {personal.nome}</p>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Email:</strong> {personal.email}</p>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Plano:</strong> {plano.capitalize()}</p>
                      <p style='color:#ccc;font-size:15px;margin:0'><strong style='color:#fff'>Status:</strong> Trial 7 dias</p>
                    </div>
                    <p style='color:#888;font-size:12px'>AurumSci — aurumsc.com.br</p>
                    </body></html>"""
                )

    if event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        stripe_sub_id = sub.get("id")
        if stripe_sub_id:
            personal = db.query(Personal).filter(Personal.stripe_subscription_id == stripe_sub_id).first()
            if personal:
                try:
                    price_id_atual = sub["items"]["data"][0]["price"]["id"]
                    for plano_key, plano_data in PLANOS_PRO.items():
                        if plano_data["price_id"] == price_id_atual:
                            personal.plano = plano_key
                            break
                    if not sub.cancel_at_period_end:
                        personal.assinatura_status = "ativa"
                    db.commit()
                except Exception:
                    pass
# ALUNO AUTONOMO - update status
            aluno = db.query(Aluno).filter(Aluno.stripe_subscription_id == stripe_sub_id).first()
            if aluno:
                try:
                    aluno.assinatura_status = sub.get("status", "active")
                    if sub.get("current_period_end"):
                        aluno.data_proxima_cobranca = datetime.fromtimestamp(sub["current_period_end"])
                    db.commit()
                except Exception as e:
                    print(f"[WEBHOOK ALUNO updated] {e}")

    if event["type"] in ["customer.subscription.deleted", "customer.subscription.paused"]:
        sub = event["data"]["object"]
        stripe_sub_id = sub.get("id")
        if stripe_sub_id:
            personal = db.query(Personal).filter(Personal.stripe_subscription_id == stripe_sub_id).first()
            if personal:
                personal.ativo = False
                personal.assinatura_status = "cancelada"
                db.commit()
                primeiro_nome = personal.nome.split()[0] if personal.nome else "Personal"
                html_cancel = f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                <h2 style='color:#C9A84C'>Assinatura cancelada, {primeiro_nome}</h2>
                <p style='color:#ccc'>Seus dados ficam salvos por 30 dias. Reative quando quiser!</p>
                <a href='https://aurumsc.com.br/pro' style='display:block;text-align:center;background:#C9A84C;color:#000;padding:16px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:16px'>REATIVAR ASSINATURA</a>
                </body></html>"""
                enviar_email(para=personal.email, assunto="Sua assinatura AurumSci foi cancelada", html=html_cancel)
# ALUNO AUTONOMO - cancelamento
            aluno = db.query(Aluno).filter(Aluno.stripe_subscription_id == stripe_sub_id).first()
            if aluno:
                try:
                    aluno.ativo = False
                    aluno.assinatura_status = "canceled"
                    aluno.data_cancelamento = datetime.utcnow()
                    db.commit()
                    primeiro_nome_aluno = aluno.nome.split()[0] if aluno.nome else "Aluno"
                    html_cancel_aluno = f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                    <h2 style='color:#C9A84C'>Assinatura cancelada, {primeiro_nome_aluno}</h2>
                    <p style='color:#ccc'>Seus dados ficam salvos por 30 dias. Reative quando quiser!</p>
                    <a href='https://aurumsc.com.br/aluno' style='display:block;text-align:center;background:#C9A84C;color:#000;padding:16px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:16px'>REATIVAR ASSINATURA</a>
                    </body></html>"""
                    enviar_email(para=aluno.email, assunto="Sua assinatura AurumSci foi cancelada", html=html_cancel_aluno)
                except Exception as e:
                    print(f"[WEBHOOK ALUNO deleted] {e}")
# ALUNO AUTONOMO - renovacao mensal
    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        stripe_sub_id = invoice.get("subscription")
        if stripe_sub_id:
            aluno = db.query(Aluno).filter(Aluno.stripe_subscription_id == stripe_sub_id).first()
            if aluno:
                try:
                    aluno.assinatura_status = "active"
                    if invoice.get("period_end"):
                        aluno.data_proxima_cobranca = datetime.fromtimestamp(invoice["period_end"])
                    db.commit()
                except Exception as e:
                    print(f"[WEBHOOK ALUNO payment_succeeded] {e}")

    # ALUNO AUTONOMO - cartao recusado
    if event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_sub_id = invoice.get("subscription")
        if stripe_sub_id:
            aluno = db.query(Aluno).filter(Aluno.stripe_subscription_id == stripe_sub_id).first()
            if aluno:
                try:
                    aluno.assinatura_status = "past_due"
                    db.commit()
                    primeiro_nome_aluno = aluno.nome.split()[0] if aluno.nome else "Aluno"
                    html_failed = f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                    <h2 style='color:#FF4B4B'>Atencao, {primeiro_nome_aluno}!</h2>
                    <p style='color:#ccc'>Nao conseguimos processar sua mensalidade. Atualize seu metodo de pagamento.</p>
                    <a href='https://aurumsc.com.br/aluno' style='display:block;text-align:center;background:#FF4B4B;color:#fff;padding:16px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:16px'>ATUALIZAR PAGAMENTO</a>
                    </body></html>"""
                    enviar_email(para=aluno.email, assunto="Problema no pagamento AurumSci", html=html_failed)
                except Exception as e:
                    print(f"[WEBHOOK ALUNO payment_failed] {e}")
    return {"status": "ok"}


# ============================================================
# CONTATO (mantido)
# ============================================================
@router.post("/contato")
async def contato(request: Request):
    try:
        dados = await request.json()
        email = dados.get("email", "")
        mensagem = dados.get("mensagem", "Sem mensagem")
        if not email:
            raise HTTPException(status_code=400, detail="Email obrigatorio")
        enviar_email(
            para="a.andrade_personal@hotmail.com",
            assunto=f"AurumSci — Contato de {email}",
            html=f"<p><strong>Email:</strong> {email}</p><p><strong>Mensagem:</strong> {mensagem}</p>"
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

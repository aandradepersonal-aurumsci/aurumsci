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


def enviar_email_boas_vindas(nome, email):
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
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": dados.plano},
                    "unit_amount": dados.valor,
                    "recurring": {"interval": "month"}
                },
                "quantity": 1
            }],
            mode="subscription",
            subscription_data={"trial_period_days": 7},
            success_url="https://www.aurumsc.com.br/aluno?pagamento=sucesso",
            cancel_url="https://www.aurumsc.com.br/aluno?pagamento=cancelado",
            metadata={"aluno_id": str(dados.aluno_id)},
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
        aluno_id = None
        try:
            aluno_id = session["metadata"]["aluno_id"]
        except Exception:
            pass
        if aluno_id:
            aluno = db.query(Aluno).filter(Aluno.id == int(aluno_id)).first()
            if aluno:
                aluno.ativo = True
                if session.get("subscription"):
                    aluno.stripe_subscription_id = session["subscription"]
                if session.get("customer"):
                    aluno.stripe_customer_id = session["customer"]
                db.commit()
                enviar_email_boas_vindas(aluno.nome, aluno.email)

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
                if session.get("subscription"):
                    personal.stripe_subscription_id = session["subscription"]
                if session.get("customer"):
                    personal.stripe_customer_id = session["customer"]
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

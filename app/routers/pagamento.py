from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
import stripe
from app.services.email_service import enviar_email

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/pagamento", tags=["Pagamento"])

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
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">CIÊNCIA QUE VIRA RESULTADO</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Bem-vindo à família, {nome}! 🏆</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0;">
        A partir de agora você está treinando com <strong style="color:#C9A84C;">ciência, método e inteligência artificial.</strong>
      </p>
    </div>
    <div style="text-align:center;margin-bottom:24px;">
      <a href="https://www.aurumsc.com.br/aluno" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">COMEÇAR AGORA →</a>
    </div>
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;">Trial de 14 dias grátis. Após esse período, R$49,90/mês será cobrado automaticamente.<br>
      Cancele quando quiser, sem burocracia.<br><br>
      <strong style="color:#C9A84C;">Equipe AurumSci</strong> — Ciência que vira resultado.</p>
    </div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto="Bem-vindo à Família AurumSci! 🏆", html=html)

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
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Olá, {nome}! Seu treino está esperando por você 🏋️</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">
        Seu personal trainer criou seu acesso ao <strong style="color:#C9A84C;">AurumSci</strong>.
      </p>
      <div style="background:#0A0A0F;border-radius:12px;padding:20px;margin-bottom:20px;">
        <div style="font-size:13px;color:#C9A84C;font-weight:700;margin-bottom:12px;letter-spacing:2px;">COMO ACESSAR:</div>
        <div style="color:#ccc;font-size:14px;line-height:2;">
          1️⃣ Acesse: <a href="https://aurumsc.com.br/aluno" style="color:#C9A84C;">aurumsc.com.br/aluno</a><br>
          2️⃣ Use seu email: <strong style="color:#fff;">{email}</strong><br>
          3️⃣ Sua senha são os <strong style="color:#C9A84C;">6 primeiros dígitos do seu CPF</strong><br>
          4️⃣ Troque sua senha após o primeiro acesso
        </div>
      </div>
      <div style="background:#0d1a0d;border:1px solid #1a3a1a;border-radius:12px;padding:16px;">
        <div style="font-size:13px;color:#00E5A0;font-weight:700;margin-bottom:8px;">📱 NO SEU CELULAR:</div>
        <div style="color:#ccc;font-size:13px;line-height:1.8;">
          Abra o Safari (iPhone) ou Chrome (Android)<br>
          Acesse aurumsc.com.br/aluno<br>
          Adicione à tela inicial para ter como app!
        </div>
      </div>
    </div>
    <div style="text-align:center;color:#444;font-size:12px;">AurumSci — aurumsc.com.br</div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto="Seu personal criou seu acesso AurumSci! 💪", html=html)

def enviar_email_boas_vindas_personal(nome, email, plano="bronze"):
    planos = {"bronze": "Bronze", "prata": "Prata", "ouro": "Ouro", "diamante": "Diamante"}
    nome_plano = planos.get(plano, "Bronze")
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
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">Bem-vindo, {nome}! Plano {nome_plano} ativado 🏆</div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">Seu acesso ao <strong style="color:#C9A84C;">AurumSci PRO</strong> está ativo com 14 dias grátis.</p>
      <div style="background:#0A0A0F;border-radius:12px;padding:20px;">
        <div style="font-size:13px;color:#C9A84C;font-weight:700;margin-bottom:12px;">COMO COMEÇAR:</div>
        <div style="color:#ccc;font-size:14px;line-height:2;">
          1️⃣ Acesse: <a href="https://aurumsc.com.br/personal" style="color:#C9A84C;">aurumsc.com.br/personal</a><br>
          2️⃣ Vá em ALUNOS → Novo Aluno<br>
          3️⃣ Cadastre com CPF — senha gerada automaticamente<br>
          4️⃣ Envie o link para o aluno via WhatsApp
        </div>
      </div>
    </div>
    <div style="text-align:center;margin-bottom:24px;">
      <a href="https://aurumsc.com.br/personal" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">ACESSAR O PRO →</a>
    </div>
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;">14 dias grátis. Após esse período, R$49,90/mês será cobrado automaticamente.<br>
      <strong style="color:#C9A84C;">Equipe AurumSci</strong></p>
    </div>
  </div>
</body></html>"""
    enviar_email(para=email, assunto=f"Bem-vindo ao AurumSci PRO! Plano {nome_plano} ativado 🏆", html=html)


class CheckoutPersonalSchema(BaseModel):
    personal_id: int
    plano: str = "bronze"
    valor: int = 4990

@router.post("/criar-sessao")
def criar_sessao(dados: CheckoutSchema, db: Session = Depends(get_db)):
    try:
        # VERIFICACAO ANTI-DUPLICACAO ALUNO
        from app.models import Aluno
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
            line_items=[{"price_data": {"currency": "brl", "product_data": {"name": dados.plano}, "unit_amount": dados.valor, "recurring": {"interval": "month"}}, "quantity": 1}],
            mode="subscription",
            subscription_data={"trial_period_days": 14},
            success_url="https://www.aurumsc.com.br/aluno?pagamento=sucesso",
            cancel_url="https://www.aurumsc.com.br/aluno?pagamento=cancelado",
            metadata={"aluno_id": str(dados.aluno_id)},
        )
        return {"url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/criar-sessao-personal")
def criar_sessao_personal(dados: CheckoutPersonalSchema, db: Session = Depends(get_db)):
    try:
        # VERIFICACAO ANTI-DUPLICACAO
        from app.models import Personal
        personal = db.query(Personal).filter(Personal.id == dados.personal_id).first()
        
        if not personal:
            raise HTTPException(status_code=404, detail="Personal nao encontrado")
        
        if personal.stripe_subscription_id:
            try:
                sub = stripe.Subscription.retrieve(personal.stripe_subscription_id)
                if sub.status in ["active", "trialing", "past_due"]:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Voce ja tem uma assinatura {sub.status}. Acesse o portal do cliente para gerenciar."
                    )
            except stripe.error.InvalidRequestError:
                pass
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "brl", "product_data": {"name": f"AurumSci PRO — Plano {dados.plano.capitalize()}"}, "unit_amount": dados.valor, "recurring": {"interval": "month"}}, "quantity": 1}],
            mode="subscription",
            subscription_data={"trial_period_days": 14},
            success_url="https://www.aurumsc.com.br/personal?cadastro=sucesso",
            cancel_url="https://www.aurumsc.com.br/pro",
            metadata={"personal_id": str(dados.personal_id), "plano": dados.plano},
        )
        return {"url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
            from app.models import Aluno
            aluno = db.query(Aluno).filter(Aluno.id == int(aluno_id)).first()
            if aluno:
                aluno.ativo = True
                db.commit()
                enviar_email_boas_vindas(aluno.nome, aluno.email)
        personal_id = None
        try:
            personal_id = session["metadata"]["personal_id"]
            plano = session["metadata"].get("plano", "bronze")
        except Exception:
            pass
        if personal_id:
            from app.models import Personal
            personal = db.query(Personal).filter(Personal.id == int(personal_id)).first()
            if personal:
                personal.ativo = True
                personal.plano = plano
                personal.assinatura_status = "ativa"
                db.commit()
                enviar_email_boas_vindas_personal(personal.nome, personal.email, plano)
                # Notifica Andre
                enviar_email(
                    para="a.andrade_personal@hotmail.com",
                    assunto=f"🎉 Novo personal assinou! {personal.nome} — Plano {plano.capitalize()}",
                    html=f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                    <h2 style='color:#C9A84C'>🎉 Novo personal no AURUM!</h2>
                    <div style='background:#12121A;border-radius:12px;padding:20px;margin:16px 0'>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Nome:</strong> {personal.nome}</p>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Email:</strong> {personal.email}</p>
                      <p style='color:#ccc;font-size:15px;margin:0 0 10px 0'><strong style='color:#fff'>Plano:</strong> {plano.capitalize()}</p>
                      <p style='color:#ccc;font-size:15px;margin:0'><strong style='color:#fff'>Status:</strong> Trial 14 dias</p>
                    </div>
                    <p style='color:#888;font-size:12px'>AurumSci — aurumsc.com.br</p>
                    </body></html>"""
                )

    if event["type"] in ["customer.subscription.deleted", "customer.subscription.paused"]:
        sub = event["data"]["object"]
        stripe_sub_id = sub.get("id")
        if stripe_sub_id:
            from app.models import Personal
            personal = db.query(Personal).filter(Personal.stripe_subscription_id == stripe_sub_id).first()
            if personal:
                personal.ativo = False
                personal.assinatura_status = "cancelada"
                db.commit()
                html_cancel = f"""<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'>
                <h2 style='color:#C9A84C'>Assinatura cancelada, {personal.nome.split()[0]}</h2>
                <p style='color:#ccc'>Seus dados ficam salvos por 30 dias. Reative quando quiser!</p>
                <a href='https://aurumsc.com.br/pro' style='display:block;text-align:center;background:#C9A84C;color:#000;padding:16px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:16px'>REATIVAR ASSINATURA</a>
                </body></html>"""
                enviar_email(para=personal.email, assunto="Sua assinatura AurumSci foi cancelada", html=html_cancel)

    return {"status": "ok"}

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

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
import stripe
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/pagamento", tags=["Pagamento"])

class CheckoutSchema(BaseModel):
    aluno_id: int
    plano: str = "Plano Mensal AurumSci"
    valor: int = 4990

def enviar_email_boas_vindas(nome, email):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo a Familia AurumSci!"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        html = f"""<html><body style="font-family:Arial,sans-serif;background:#0A0A0F;color:#fff;padding:40px;">
          <div style="max-width:600px;margin:0 auto;">
            <h1 style="color:#C9A84C;letter-spacing:4px;">AURUMSCI</h1>
            <p style="color:#888;font-size:12px;">CIENCIA QUE VIRA RESULTADO</p>
            <h2 style="color:#C9A84C;">Seja muito bem-vindo, {nome}!</h2>
            <p style="color:#ccc;line-height:1.8;">A partir de agora voce nao esta mais treinando no achismo.<br>
            Voce esta treinando com <strong style="color:#C9A84C;">ciencia, metodo e acompanhamento inteligente.</strong></p>
            <p style="color:#ccc;line-height:1.8;">Aqui, cada treino tem proposito.<br>Cada dado tem significado.<br>E cada evolucao sera acompanhada de perto.</p>
            <div style="text-align:center;margin-top:20px;">
              <a href="https://www.aurumsc.com.br/aluno"
                 style="background:#C9A84C;color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:16px;">
                COMECAR AGORA
              </a>
            </div>
            <p style="color:#888;font-size:12px;margin-top:20px;">
              Trial de 14 dias gratis. Apos esse periodo, R$49,90/mes sera cobrado automaticamente.<br>
              Equipe AurumSci
            </p>
          </div>
        </body></html>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email enviado para {email}")
    except Exception as e:
        print(f"Erro email: {e}")

@router.post("/criar-sessao")
def criar_sessao(dados: CheckoutSchema):
    try:
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
    return {"status": "ok"}

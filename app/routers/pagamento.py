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

def enviar_email_boas_vindas(nome: str, email: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo à Família AurumSci! 🚀"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;background:#0A0A0F;color:#fff;padding:40px;">
          <div style="max-width:600px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:30px;">
              <h1 style="color:#C9A84C;font-size:32px;letter-spacing:4px;">AURUMSCI</h1>
              <p style="color:#888;font-size:12px;letter-spacing:2px;">CIÊNCIA QUE VIRA RESULTADO</p>
            </div>
            <div style="background:#1A1A2E;border-radius:16px;padding:30px;margin-bottom:20px;border:1px solid #C9A84C33;">
              <h2 style="color:#C9A84C;">Seja muito bem-vindo, {nome}! 💪</h2>
              <p style="color:#ccc;line-height:1.8;">
                A partir de agora, você não está mais treinando no achismo.<br>
                Você está treinando com <strong style="color:#C9A84C;">ciência, método e acompanhamento inteligente.</strong>
              </p>
              <p style="color:#ccc;line-height:1.8;">
                Aqui, cada treino tem propósito.<br>
                Cada dado tem significado.<br>
                E cada evolução será acompanhada de perto.
              </p>
              <p style="color:#ccc;line-height:1.8;">
                Nosso compromisso com você é simples:<br>
                👉 te entregar <strong style="color:#00E5A0;">resultado com segurança e inteligência.</strong>
              </p>
            </div>
            <div style="background:#1A1A2E;border-radius:16px;padding:24px;margin-bottom:20px;border:1px solid #4B9FFF33;">
              <h3 style="color:#4B9FFF;margin-top:0;">🚀 Seus próximos passos:</h3>
              <p style="color:#ccc;line-height:2;">
                ⚖️ Registre seu peso e composição corporal<br>
                🧍 Faça sua análise postural com IA<br>
                📏 Meça suas circunferências<br>
                ❤️ Teste seu condicionamento cardíaco<br>
                🏋️ Comece seu treino personalizado!
              </p>
              <div style="text-align:center;margin-top:20px;">
                <a href="https://www.aurumsc.com.br/aluno"
                   style="background:linear-gradient(135deg,#C9A84C,#B8973B);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:16px;letter-spacing:2px;">
                  COMEÇAR AGORA →
                </a>
              </div>
            </div>
            <div style="background:#1A1A2E;border-radius:16px;padding:20px;border:1px solid #00E5A033;">
              <p style="color:#888;font-size:13px;line-height:1.8;margin:0;">
                🎯 Seu trial de <strong style="color:#00E5A0;">14 dias grátis</strong> começou hoje.<br>
                Após esse período, sua assinatura de <strong>R$200/mês</strong> será ativada automaticamente.<br>
                Você pode cancelar a qualquer momento pelo app.
              </p>
            </div>
            <div style="text-align:center;margin-top:30px;">
              <p style="color:#555;font-size:12px;">
                Dúvidas? Responda este email ou fale com o AURI no app.<br>
                <strong style="color:#C9A84C;">Equipe AurumSci</strong>
              </p>
            </div>
          </div>
        </body>
        </html>
        """
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
        try:
            aluno_id = session["metadata"]["aluno_id"]
        except:
            aluno_id = None
except:
        aluno_id = None
        if aluno_id:
            from app.models import Aluno
            aluno = db.query(Aluno).filter(Aluno.id == int(aluno_id)).first()
            if aluno:
                aluno.ativo = True
                db.commit()
                enviar_email_boas_vindas(aluno.nome, aluno.email)
    return {"status": "ok"}

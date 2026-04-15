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

def enviar_email_boas_vindas_aluno(nome, email):
    """Email enviado ao aluno quando o personal cria o acesso."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Seu personal criou seu acesso AurumSci! 💪"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">CIÊNCIA QUE VIRA RESULTADO</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">
        Olá, {nome}! Seu treino está esperando por você 🏋️
      </div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">
        Seu personal trainer criou seu acesso ao <strong style="color:#C9A84C;">AurumSci</strong> — 
        a plataforma que une ciência e tecnologia para transformar seus resultados.
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
      <div style="background:#0d1a0d;border:1px solid #1a3a1a;border-radius:12px;padding:16px;margin-bottom:16px;">
        <div style="font-size:13px;color:#00E5A0;font-weight:700;margin-bottom:8px;">📱 NO SEU CELULAR:</div>
        <div style="color:#ccc;font-size:13px;line-height:1.8;">
          Abra o Safari (iPhone) ou Chrome (Android)<br>
          Acesse aurumsc.com.br/aluno<br>
          Adicione à tela inicial para ter como app!
        </div>
      </div>
      <p style="color:#888;font-size:13px;margin:0;">
        Qualquer dúvida, fale diretamente com seu personal trainer.
      </p>
    </div>
    <div style="text-align:center;color:#444;font-size:12px;">
      AurumSci — Ciência que vira resultado<br>
      <a href="https://aurumsc.com.br" style="color:#C9A84C;">aurumsc.com.br</a>
    </div>
  </div>
</body>
</html>"""
        msg.attach(MIMEText(html, "html"))
        import smtplib
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        print(f"Email boas-vindas aluno enviado: {email}")
    except Exception as e:
        print(f"Erro email aluno: {e}")



def enviar_email_boas_vindas_personal(nome, email, plano="bronze"):
    """Email enviado ao personal quando assina o plano."""
    planos = {"bronze": "Bronze", "prata": "Prata", "ouro": "Ouro", "diamante": "Diamante"}
    nome_plano = planos.get(plano, "Bronze")
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo ao AurumSci PRO! Seu guia completo para começar"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">PRO — PARA PERSONAL TRAINERS</div>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">
        Bem-vindo, {nome}! Plano {nome_plano} ativado 🏆
      </div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0 0 16px 0;">
        Seu acesso ao <strong style="color:#C9A84C;">AurumSci PRO</strong> está ativo com 14 dias grátis.
        Veja como começar agora mesmo:
      </p>
    </div>
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:13px;font-weight:700;color:#888;letter-spacing:2px;margin-bottom:20px;">COMO USAR O AURUMSCI PRO</div>
      <div style="margin-bottom:18px;">
        <div style="color:#C9A84C;font-weight:700;font-size:15px;margin-bottom:6px;">1️⃣ Acesse o app PRO</div>
        <div style="color:#ccc;font-size:13px;line-height:1.7;">
          Acesse <a href="https://aurumsc.com.br/personal" style="color:#C9A84C;">aurumsc.com.br/personal</a> com seu email e senha cadastrados.
          No celular: adicione à tela inicial para usar como app!
        </div>
      </div>
      <div style="margin-bottom:18px;">
        <div style="color:#C9A84C;font-weight:700;font-size:15px;margin-bottom:6px;">2️⃣ Cadastre seu primeiro aluno</div>
        <div style="color:#ccc;font-size:13px;line-height:1.7;">
          Vá em <strong>ALUNOS → Novo Aluno</strong> e preencha os dados.<br>
          Informe o CPF — a senha do aluno será os 6 primeiros dígitos automaticamente.
        </div>
      </div>
      <div style="margin-bottom:18px;">
        <div style="color:#C9A84C;font-weight:700;font-size:15px;margin-bottom:6px;">3️⃣ Avise o aluno</div>
        <div style="color:#ccc;font-size:13px;line-height:1.7;">
          Após cadastrar, o sistema mostra uma mensagem pronta para WhatsApp.<br>
          O aluno recebe também um email automático com as instruções de acesso.
        </div>
      </div>
      <div style="margin-bottom:18px;">
        <div style="color:#C9A84C;font-weight:700;font-size:15px;margin-bottom:6px;">4️⃣ Monte o treino e a avaliação</div>
        <div style="color:#ccc;font-size:13px;line-height:1.7;">
          Clique no aluno → aba <strong>TREINO</strong> para montar o plano.<br>
          Aba <strong>AVALIAÇÃO</strong> para registrar dados físicos, posturais e cardiorrespiratórios.
        </div>
      </div>
      <div style="margin-bottom:0;">
        <div style="color:#C9A84C;font-weight:700;font-size:15px;margin-bottom:6px;">5️⃣ Acompanhe os resultados</div>
        <div style="color:#ccc;font-size:13px;line-height:1.7;">
          Aba <strong>RESULTADOS</strong> mostra a evolução completa do aluno com gráficos e dados científicos.
        </div>
      </div>
    </div>
    <div style="background:linear-gradient(135deg,rgba(201,168,76,0.12),rgba(201,168,76,0.04));border:1px solid rgba(201,168,76,0.3);border-radius:16px;padding:24px;margin-bottom:24px;text-align:center;">
      <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:8px;">🚀 Comece agora</div>
      <div style="color:#aaa;font-size:13px;margin-bottom:16px;">Seu primeiro aluno está a 2 minutos de distância.</div>
      <a href="https://aurumsc.com.br/personal" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">
        ACESSAR O PRO →
      </a>
    </div>
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;line-height:1.8;margin:0;">
        14 dias grátis. Após esse período, R$49,90/mês será cobrado automaticamente.<br>
        Cancele quando quiser, sem burocracia.<br><br>
        <strong style="color:#C9A84C;">Equipe AurumSci</strong> — Ciência que vira resultado.
      </p>
    </div>
  </div>
</body>
</html>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        print(f"Email boas-vindas personal enviado: {email}")
    except Exception as e:
        print(f"Erro email personal: {e}")

class CheckoutSchema(BaseModel):
    aluno_id: int
    plano: str = "Plano Mensal AurumSci"
    valor: int = 4990

def enviar_email_boas_vindas(nome, email):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo à Família AurumSci! 🏆"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 24px;">

    <!-- Header -->
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:Georgia,serif;font-size:36px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
      <div style="font-size:11px;color:#666;letter-spacing:4px;margin-top:6px;">CIÊNCIA QUE VIRA RESULTADO</div>
    </div>

    <!-- Linha dourada -->
    <div style="height:2px;background:linear-gradient(90deg,transparent,#C9A84C,transparent);margin-bottom:32px;"></div>

    <!-- Boas vindas -->
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:700;color:#C9A84C;margin-bottom:12px;">
        Bem-vindo à família, {nome}! 🏆
      </div>
      <p style="color:#ccc;line-height:1.9;font-size:15px;margin:0;">
        A partir de agora você não está mais treinando no achismo.<br>
        Você está treinando com <strong style="color:#C9A84C;">ciência, método e inteligência artificial.</strong>
      </p>
    </div>

    <!-- O que você tem acesso -->
    <div style="background:#12121A;border:1px solid #2A2A3A;border-radius:16px;padding:28px;margin-bottom:20px;">
      <div style="font-size:13px;font-weight:700;color:#888;letter-spacing:2px;margin-bottom:16px;">O QUE VOCÊ TEM ACESSO AGORA</div>

      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <div style="font-size:22px;margin-right:14px;">🤖</div>
        <div>
          <div style="color:#C9A84C;font-weight:700;font-size:14px;">Análise Postural com IA</div>
          <div style="color:#888;font-size:13px;line-height:1.6;">Tire fotos da sua postura e nossa IA identifica desvios como hiperlordose e escoliose. Exercícios corretivos personalizados são adicionados automaticamente ao seu treino.</div>
        </div>
      </div>

      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <div style="font-size:22px;margin-right:14px;">❤️</div>
        <div>
          <div style="color:#C9A84C;font-weight:700;font-size:14px;">Avaliação Cardiorrespiratória (VO2 + HRR)</div>
          <div style="color:#888;font-size:13px;line-height:1.6;">Medimos seu risco cardiovascular pelo HRR — a recuperação da sua frequência cardíaca após o esforço. Isso define com segurança até onde você pode evoluir na intensidade dos treinos.</div>
        </div>
      </div>

      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <div style="font-size:22px;margin-right:14px;">🏋️</div>
        <div>
          <div style="color:#C9A84C;font-weight:700;font-size:14px;">Treino Personalizado</div>
          <div style="color:#888;font-size:13px;line-height:1.6;">Seu plano é montado com base no seu objetivo, nível e disponibilidade. Cada fase tem propósito científico.</div>
        </div>
      </div>

      <div style="display:flex;align-items:flex-start;margin-bottom:0;">
        <div style="font-size:22px;margin-right:14px;">📊</div>
        <div>
          <div style="color:#C9A84C;font-weight:700;font-size:14px;">Evolução Completa</div>
          <div style="color:#888;font-size:13px;line-height:1.6;">Composição corporal, medidas, periodização e dashboard de resultados. Tudo em um só lugar.</div>
        </div>
      </div>
    </div>

    <!-- Próximo passo -->
    <div style="background:linear-gradient(135deg,rgba(201,168,76,0.12),rgba(201,168,76,0.04));border:1px solid rgba(201,168,76,0.3);border-radius:16px;padding:24px;margin-bottom:24px;text-align:center;">
      <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:8px;">🚀 Seu próximo passo</div>
      <div style="color:#aaa;font-size:13px;line-height:1.8;margin-bottom:16px;">
        Complete sua avaliação postural e cardiorrespiratória.<br>
        Isso personaliza 100% do seu treino e garante sua segurança.
      </div>
      <a href="https://www.aurumsc.com.br/aluno"
         style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:16px 40px;border-radius:12px;text-decoration:none;font-weight:900;font-size:16px;letter-spacing:2px;">
        COMEÇAR AGORA →
      </a>
    </div>

    <!-- Linha dourada -->
    <div style="height:1px;background:linear-gradient(90deg,transparent,#2A2A3A,transparent);margin-bottom:24px;"></div>

    <!-- Footer -->
    <div style="text-align:center;">
      <p style="color:#555;font-size:12px;line-height:1.8;margin:0;">
        Trial de 14 dias grátis. Após esse período, R$49,90/mês será cobrado automaticamente.<br>
        Cancele quando quiser, sem burocracia.<br><br>
        <strong style="color:#C9A84C;">Equipe AurumSci</strong> — Ciência que vira resultado.
      </p>
    </div>

  </div>
</body>
</html>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
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


class CheckoutPersonalSchema(BaseModel):
    personal_id: int
    plano: str = "bronze"
    valor: int = 4990

@router.post("/criar-sessao-personal")
def criar_sessao_personal(dados: CheckoutPersonalSchema):
    try:
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
    # Cancelamento
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
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = "Sua assinatura AurumSci foi cancelada"
                    msg["From"] = settings.SMTP_USER
                    msg["To"] = personal.email
                    html = f"<html><body style='background:#0A0A0F;font-family:Arial;padding:40px'><h2 style='color:#C9A84C'>Assinatura cancelada, {personal.nome.split()[0]}</h2><p style='color:#ccc'>Seus dados ficam salvos por 30 dias. Reative quando quiser!</p><a href='https://aurumsc.com.br/pro' style='display:block;text-align:center;background:#C9A84C;color:#000;padding:16px;border-radius:12px;text-decoration:none;font-weight:900;margin-top:16px'>REATIVAR ASSINATURA</a></body></html>"
                    msg.attach(MIMEText(html, "html"))
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASS)
                        server.send_message(msg)
                except Exception as e:
                    print(f"Erro email cancelamento: {e}")

    return {"status": "ok"}


@router.post("/contato")
async def contato(request: Request):
    from app.services.email_service import enviar_email
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

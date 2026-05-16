"""
Scheduler de emails automáticos AurumSci.
FIX 17/05/2026: Roda diariamente as 10h (horario de SP).

Jobs:
1. email_reavaliacao_bimestral: aluno ativo com 56+ dias sem avaliacao
2. email_sentimos_sua_falta: aluno inativo (sem check-in 4+ semanas)
"""
import smtplib
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Aluno
from app.config import settings


def _enviar_email(destinatario: str, assunto: str, html: str):
    """Helper SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = settings.SMTP_USER
        msg["To"] = destinatario
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        print(f"[SCHEDULER] Email enviado pra {destinatario}: {assunto}")
        return True
    except Exception as e:
        print(f"[SCHEDULER] Erro ao enviar pra {destinatario}: {e}")
        return False


def _template_email(titulo_topo: str, cor_destaque: str, conteudo_html: str, cta_texto: str, cta_url: str) -> str:
    """Template HTML padrao com brand AurumSci (preto + dourado)."""
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0A0A0F;font-family:Arial,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:40px 24px;">
  <div style="text-align:center;margin-bottom:24px;">
    <div style="font-family:Georgia,serif;font-size:32px;font-weight:900;color:#C9A84C;letter-spacing:8px;">AURUMSCI</div>
    <div style="font-size:11px;letter-spacing:3px;color:#888;margin-top:6px;">CIÊNCIA QUE VIRA RESULTADO</div>
  </div>
  <div style="background:#12121A;border:1px solid {cor_destaque};border-radius:16px;padding:28px;margin-bottom:20px;">
    <div style="font-size:22px;font-weight:700;color:{cor_destaque};margin-bottom:16px;">{titulo_topo}</div>
    {conteudo_html}
    <div style="text-align:center;margin-top:24px;">
      <a href="{cta_url}" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C96A);color:#0A0A0F;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:900;font-size:14px;letter-spacing:2px;">{cta_texto} &rarr;</a>
    </div>
  </div>
  <div style="text-align:center;color:#444;font-size:12px;">
    AurumSci &mdash; aurumsc.com.br
  </div>
</div>
</body></html>"""


def email_reavaliacao_bimestral():
    """Aluno ATIVO (check-in recente) que tem 56+ dias sem avaliacao.
    Roda diariamente. Pega quem completa exatamente 56 dias hoje.
    """
    from app.routers.avaliacao import AvaliacaoFisica
    from app.routers.treino import PresencaTreino
    db: Session = SessionLocal()
    try:
        hoje = date.today()
        limite = hoje - timedelta(days=56)
        
        # Busca alunos com ultima avaliacao em <= limite
        alunos = db.query(Aluno).filter(Aluno.ativo == True).all()
        enviados = 0
        
        for aluno in alunos:
            ultima_aval = db.query(AvaliacaoFisica).filter(
                AvaliacaoFisica.aluno_id == aluno.id
            ).order_by(AvaliacaoFisica.data_avaliacao.desc()).first()
            
            if not ultima_aval:
                continue
            
            dias = (hoje - ultima_aval.data_avaliacao).days
            # Só dispara quando bate EXATAMENTE 56 dias (evita reenviar todo dia)
            if dias != 56:
                continue
            
            # Verifica se aluno esta ATIVO (check-in nos ultimos 14 dias)
            checkin_recente = db.query(PresencaTreino).filter(
                PresencaTreino.aluno_id == aluno.id,
                PresencaTreino.data >= hoje - timedelta(days=14),
                PresencaTreino.presente == True
            ).first()
            
            if not checkin_recente:
                continue  # inativo recebe outro email
            
            # Envia email reavaliacao
            html = _template_email(
                titulo_topo=f"📊 {aluno.nome}, hora de medir sua evolução!",
                cor_destaque="#C9A84C",
                conteudo_html=f"""
                <p style="color:#ccc;font-size:15px;line-height:1.8;">
                  Já se passaram <strong style="color:#fff;">8 semanas</strong> desde sua última avaliação. 
                  É hora de ver o quanto você evoluiu! 🚀
                </p>
                <p style="color:#ccc;font-size:14px;line-height:1.7;">
                  Reavaliação a cada 8 semanas é o intervalo ideal pra adaptação muscular 
                  <span style="color:#888;">(Schoenfeld 2017)</span>.
                </p>
                <p style="color:#ccc;font-size:14px;line-height:1.7;">
                  Bora medir: peso, composição corporal, força, VO2 e flexibilidade.
                </p>""",
                cta_texto="FAZER REAVALIAÇÃO",
                cta_url="https://www.aurumsc.com.br/aluno"
            )
            
            if _enviar_email(aluno.email, f"⏰ {aluno.nome}, hora da reavaliação bimestral!", html):
                enviados += 1
        
        print(f"[SCHEDULER] email_reavaliacao_bimestral: {enviados} enviados")
    finally:
        db.close()


def email_sentimos_sua_falta():
    """Aluno INATIVO (sem check-in nas ultimas 4 semanas).
    Dispara 1x quando completa 28 dias sem check-in.
    """
    from app.routers.treino import PresencaTreino
    db: Session = SessionLocal()
    try:
        hoje = date.today()
        limite_28 = hoje - timedelta(days=28)
        limite_29 = hoje - timedelta(days=29)
        
        alunos = db.query(Aluno).filter(Aluno.ativo == True).all()
        enviados = 0
        
        for aluno in alunos:
            # Ultimo check-in
            ultimo = db.query(PresencaTreino).filter(
                PresencaTreino.aluno_id == aluno.id,
                PresencaTreino.presente == True
            ).order_by(PresencaTreino.data.desc()).first()
            
            if not ultimo:
                continue  # nunca treinou ainda, deixa quieto
            
            # Só dispara quando completa EXATAMENTE 28 dias sem treino
            if not (limite_29 <= ultimo.data <= limite_28):
                continue
            
            html = _template_email(
                titulo_topo=f"💔 {aluno.nome}, sentimos sua falta!",
                cor_destaque="#FF6B6B",
                conteudo_html=f"""
                <p style="color:#ccc;font-size:15px;line-height:1.8;">
                  Faz <strong style="color:#fff;">4 semanas</strong> que a gente não te vê treinando. 
                  Tá tudo bem? 💛
                </p>
                <p style="color:#ccc;font-size:14px;line-height:1.7;">
                  Sabemos que a vida acontece &mdash; trabalho, família, viagens, cansaço. 
                  Mas seu corpo merece esse cuidado, e a gente tá aqui pra te ajudar a voltar.
                </p>
                <p style="color:#ccc;font-size:14px;line-height:1.7;">
                  Que tal começar com algo leve hoje? Um treino curto, um alongamento, 
                  ou até só uma conversa com o AURI sobre como tá se sentindo. 💪
                </p>
                <p style="color:#888;font-size:13px;line-height:1.7;font-style:italic;">
                  Pequenos passos consistentes > grandes saltos esporádicos.
                </p>""",
                cta_texto="VOLTAR A TREINAR",
                cta_url="https://www.aurumsc.com.br/aluno"
            )
            
            if _enviar_email(aluno.email, f"💛 {aluno.nome}, sentimos sua falta no AurumSci", html):
                enviados += 1
        
        print(f"[SCHEDULER] email_sentimos_sua_falta: {enviados} enviados")
    finally:
        db.close()


def iniciar_scheduler():
    """Inicia o scheduler em background. Chamado por main.py no startup."""
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    
    # Reavaliacao bimestral: diario 10h
    scheduler.add_job(
        email_reavaliacao_bimestral,
        trigger=CronTrigger(hour=10, minute=0),
        id="reavaliacao_bimestral",
        replace_existing=True
    )
    
    # Sentimos sua falta: diario 11h
    scheduler.add_job(
        email_sentimos_sua_falta,
        trigger=CronTrigger(hour=11, minute=0),
        id="sentimos_sua_falta",
        replace_existing=True
    )
    
    scheduler.start()
    print("[SCHEDULER] Iniciado: reavaliacao_bimestral (10h) + sentimos_sua_falta (11h)")
    return scheduler

"""
AurumSci — Serviço de Email
Templates científicos e despojados para:
- Boas vindas ao personal (trial 14 dias)
- Boas vindas ao aluno (primeiro acesso)
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# ── Config ────────────────────────────────────────────────────────────────────

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM    = os.getenv("SMTP_USER", "")
EMAIL_FROM_NAME = "André Andrade · AurumSci"


# ── Envio base ────────────────────────────────────────────────────────────────

def enviar_email(para: str, assunto: str, html: str) -> bool:
    """Envia email via Gmail SMTP SSL."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"]    = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg["To"]      = para
        msg.attach(MIMEText(html, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, para, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ── Template base ─────────────────────────────────────────────────────────────

def _base(conteudo: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AurumSci</title>
<style>
  body {{ margin:0; padding:0; background:#0A0A0F; font-family:'Segoe UI',Arial,sans-serif; color:#F0EDE8; }}
  .wrap {{ max-width:560px; margin:0 auto; padding:40px 20px; }}
  .logo {{ font-size:36px; font-weight:900; letter-spacing:4px; color:#F0C040; text-align:center; margin-bottom:4px; }}
  .logo-sub {{ font-size:11px; letter-spacing:3px; color:#555; text-align:center; margin-bottom:40px; }}
  .card {{ background:#12121A; border-radius:20px; border:1px solid rgba(201,168,76,.15); padding:32px; margin-bottom:20px; }}
  .titulo {{ font-size:28px; font-weight:800; color:#F0C040; margin-bottom:8px; line-height:1.2; }}
  .sub {{ font-size:14px; color:#888; margin-bottom:24px; line-height:1.6; }}
  .destaque {{ background:rgba(201,168,76,.06); border:1px solid rgba(201,168,76,.2); border-radius:14px; padding:20px; margin:20px 0; }}
  .item {{ display:flex; gap:12px; margin-bottom:14px; font-size:13px; line-height:1.6; }}
  .emoji {{ font-size:20px; flex-shrink:0; }}
  .btn {{ display:block; background:linear-gradient(135deg,#C9A84C,#F0C040); color:#0A0A0F; text-decoration:none; font-weight:800; font-size:16px; letter-spacing:2px; text-align:center; padding:16px 32px; border-radius:14px; margin:24px 0; }}
  .ref {{ font-size:10px; color:#444; line-height:1.8; margin-top:20px; padding-top:16px; border-top:1px solid #1A1A26; }}
  .footer {{ text-align:center; font-size:11px; color:#333; margin-top:32px; line-height:1.8; }}
  .verde {{ color:#00E5A0; }}
  .ouro {{ color:#F0C040; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">AURUMSCI</div>
  <div class="logo-sub">CIÊNCIA QUE VIRA RESULTADO</div>
  {conteudo}
  <div class="footer">
    André Andrade · CREF 62702-G/SP<br>
    <a href="https://www.aurumsc.com.br" style="color:#555">aurumsc.com.br</a><br><br>
    Este email foi enviado porque você se cadastrou na plataforma AurumSci.
  </div>
</div>
</body>
</html>"""


# ── Email 1: Boas vindas ao Personal (trial 14 dias) ──────────────────────────

def email_boas_vindas_personal(nome: str, email: str, trial_fim: str = "14 dias") -> bool:
    primeiro_nome = nome.split()[0]
    html = _base(f"""
  <div class="card">
    <div style="font-size:11px;color:#555;letter-spacing:2px;text-align:center;margin-bottom:8px">PERSONAL TRAINER · CREF 62702-G/SP</div>
    <div style="font-size:14px;color:#888;text-align:center;margin-bottom:24px">{primeiro_nome}</div>
    <div class="titulo" style="text-align:center">Bem-vindo à família<br><span style="color:#F0C040">AurumSci PRO</span> 🏆</div>
    <div class="sub" style="text-align:center">Seu período de teste gratuito começa agora. 14 dias para transformar a forma como você gerencia seus alunos.</div>

    <div class="destaque">
      <div style="font-size:11px;color:#F0C040;letter-spacing:2px;font-weight:700;margin-bottom:12px">O QUE VOCÊ TEM AGORA</div>
      <div class="item"><span class="emoji">🤖</span><span><strong class="ouro">AURI</strong> — Assistente de IA que conhece cada aluno, responde dúvidas e monitora evolução 24h por dia.</span></div>
      <div class="item"><span class="emoji">📊</span><span><strong class="ouro">Periodização científica</strong> — Motor automático gera treinos ondulatórios e em blocos baseados em Rhea et al. (2002) e Issurin (2010).</span></div>
      <div class="item"><span class="emoji">🧍</span><span><strong class="ouro">Análise postural com IA</strong> — Claude Vision identifica desvios e adiciona exercícios corretivos automaticamente.</span></div>
      <div class="item"><span class="emoji">❤️</span><span><strong class="ouro">Teste HRR</strong> — Avalia risco cardiovascular pelo Heart Rate Recovery. Cole et al. (1999) NEJM.</span></div>
      <div class="item"><span class="emoji">📈</span><span><strong class="ouro">Evolução completa</strong> — VO2 máx, composição corporal e força classificados por idade e sexo. ACSM 2022.</span></div>
    </div>

    <a href="https://www.aurumsc.com.br/personal" class="btn">ACESSAR AURUMSCI PRO →</a>

    <div style="font-size:13px;color:#888;line-height:1.7">
      Seu trial termina em <strong class="ouro">{trial_fim}</strong>. Após esse período, escolha o plano ideal para seu negócio.<br><br>
      Qualquer dúvida, responda este email — eu mesmo vou te atender. 💪
    </div>

    <div class="ref">
      📚 Base científica do AurumSci:<br>
      Rhea et al. (2002) J Strength Cond Res · Issurin (2010) Sports Med · Schoenfeld (2010) J Strength Cond Res<br>
      Cole CR et al. (1999) NEJM · ACSM Guidelines for Exercise Testing (2022) · Cooper KH (1968) JAMA
    </div>
  </div>
""")
    return enviar_email(email, "Bem-vindo ao AurumSci — seu trial começa agora! 🏆", html)


# ── Email 2: Boas vindas ao Aluno (primeiro acesso) ───────────────────────────

def email_boas_vindas_aluno(nome: str, email: str, nome_personal: str = "André Andrade") -> bool:
    primeiro_nome = nome.split()[0]
    primeiro_personal = nome_personal.split()[0]
    html = _base(f"""
  <div class="card">
    <div class="titulo">Oi, {primeiro_nome}! Seu treino inteligente começa agora. 💪</div>
    <div class="sub">Você acaba de entrar para a plataforma do {primeiro_personal}. A partir de hoje, ciência e tecnologia trabalham juntas pelo seu resultado.</div>

    <div class="destaque">
      <div style="font-size:11px;color:#00E5A0;letter-spacing:2px;font-weight:700;margin-bottom:12px">SEU PERSONAL 24H NO BOLSO</div>
      <div class="item"><span class="emoji">🏋️</span><span><strong class="verde">Treino personalizado</strong> — Prescrito pelo {primeiro_personal} e ajustado ao seu nível, objetivo e disponibilidade.</span></div>
      <div class="item"><span class="emoji">📅</span><span><strong class="verde">Periodização científica</strong> — Fases de adaptação, volume, intensidade e deload organizadas para maximizar seus resultados. Rhea et al. (2002).</span></div>
      <div class="item"><span class="emoji">🤖</span><span><strong class="verde">AURI</strong> — Assistente do seu personal disponível 24h. Tire dúvidas sobre treino, nutrição e recuperação a qualquer hora.</span></div>
      <div class="item"><span class="emoji">❤️</span><span><strong class="verde">Avaliação completa</strong> — VO2 máx, composição corporal, força e postura. Tudo classificado por idade e sexo com base na literatura científica.</span></div>
      <div class="item"><span class="emoji">📈</span><span><strong class="verde">Evolução acompanhada</strong> — Veja seu progresso mês a mês. Reavaliação automática a cada 60 dias.</span></div>
    </div>

    <a href="https://www.aurumsc.com.br/aluno" class="btn">ACESSAR MEU TREINO →</a>

    <div style="font-size:13px;color:#888;line-height:1.7">
      Comece fazendo seu <strong class="verde">check-in</strong> e explorando o treino do dia. Qualquer dúvida, use o <strong class="verde">AURI</strong> — ele já conhece seu perfil.<br><br>
      Bora, {primeiro_nome}! 🚀
    </div>

    <div class="ref">
      📚 Seu treino é baseado em evidências científicas:<br>
      Schoenfeld (2010) J Strength Cond Res · ACSM Position Stand (2009) · Rhea et al. (2002)<br>
      Behm et al. (2016) Br J Sports Med · ISSN Position Stand — Stokes et al. (2018)
    </div>
  </div>
""")
    return enviar_email(email, f"Seu treino inteligente começa agora, {primeiro_nome}! 💪", html)


# ── Teste ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("/Users/andrepersonalnote/Personal_Trainer_Projeto/.env")

    # Recarrega variáveis após load_dotenv
    import importlib, sys
    importlib.reload(sys.modules[__name__])

    print("Testando email personal...")
    ok1 = email_boas_vindas_personal("André Andrade", "a.andrade_personal@hotmail.com", "14 dias")
    print(f"Personal: {'✅' if ok1 else '❌'}")

    print("Testando email aluno...")
    ok2 = email_boas_vindas_aluno("Aluno Teste", "a.andrade_personal@hotmail.com")
    print(f"Aluno: {'✅' if ok2 else '❌'}")

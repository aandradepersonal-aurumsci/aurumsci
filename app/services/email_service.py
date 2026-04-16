"""
AurumSci — Servico de Email via Resend
"""
import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY", "")

EMAIL_FROM = "AurumSci <onboarding@resend.dev>"

def enviar_email(para: str, assunto: str, html: str) -> bool:
    try:
        resend.Emails.send({
            "from": EMAIL_FROM,
            "to": [para],
            "subject": assunto,
            "html": html
        })
        print(f"Email enviado via Resend para {para}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

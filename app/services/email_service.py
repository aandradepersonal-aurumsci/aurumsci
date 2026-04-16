"""
AurumSci — Servico de Email via requests (Resend API)
"""
import os
import requests

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = "AurumSci <noreply@aurumsc.com.br>"

def enviar_email(para: str, assunto: str, html: str) -> bool:
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={"from": EMAIL_FROM, "to": [para], "subject": assunto, "html": html}
        )
        print(f"Email enviado: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

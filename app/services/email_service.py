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
            json={"from": EMAIL_FROM, "to": [para], "subject": assunto, "html": html, "reply_to": "andrepersonal395@gmail.com"}
        )
        print(f"Email enviado: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def enviar_email_com_anexo(para: str, assunto: str, html: str, anexo_path: str = None, nome_anexo: str = "documento.pdf") -> bool:
    """
    Envia email com PDF anexo via Resend API.
    Se anexo_path for None, envia email normal sem anexo.
    """
    import base64
    
    payload = {
        "from": EMAIL_FROM,
        "to": [para],
        "subject": assunto,
        "html": html,
        "reply_to": "andrepersonal395@gmail.com"
    }
    
    # Adiciona anexo se fornecido
    if anexo_path and os.path.exists(anexo_path):
        try:
            with open(anexo_path, "rb") as f:
                conteudo_b64 = base64.b64encode(f.read()).decode()
            payload["attachments"] = [{
                "filename": nome_anexo,
                "content": conteudo_b64
            }]
        except Exception as e:
            print(f"[EMAIL ANEXO ERROR] {e}")
    
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        print(f"Email com anexo enviado: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


"""
AurumSci — Templates de email
"""

def email_cobranca(aluno_nome: str, descricao: str, valor: float, data_vencimento: str, url_pagamento: str, personal_nome: str = "Seu Personal Trainer") -> str:
    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f4f4f7; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .header {{ background: linear-gradient(135deg, #1a3a5c 0%, #c9a961 100%); padding: 30px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px; color: #333; line-height: 1.6; }}
        .valor-box {{ background: #f9f7f2; border-left: 4px solid #c9a961; padding: 20px; margin: 20px 0; border-radius: 4px; }}
        .valor {{ font-size: 32px; font-weight: bold; color: #1a3a5c; margin: 10px 0; }}
        .btn {{ display: inline-block; background: #c9a961; color: white !important; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
        .footer {{ background: #f9f7f2; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>💪 Cobrança AurumSci</h1>
        </div>
        <div class="content">
          <p>Olá <strong>{aluno_nome}</strong>,</p>
          <p>Seu treino tá em dia, e chegou a hora de fechar o pagamento referente a:</p>
          
          <div class="valor-box">
            <div style="color: #888; font-size: 14px;">{descricao}</div>
            <div class="valor">{valor_fmt}</div>
            <div style="color: #888; font-size: 13px;">Vencimento: {data_vencimento}</div>
          </div>
          
          <p>Pague de forma rápida e segura no link abaixo (cartão ou boleto):</p>
          
          <div style="text-align: center;">
            <a href="{url_pagamento}" class="btn">💳 PAGAR AGORA</a>
          </div>
          
          <p style="color: #888; font-size: 13px;">Ou copie e cole este link no navegador:<br>
          <a href="{url_pagamento}" style="color: #c9a961; word-break: break-all;">{url_pagamento}</a></p>
          
          <p style="margin-top: 30px;">Qualquer dúvida, fale com seu personal: <strong>{personal_nome}</strong></p>
          <p>Bons treinos! 💪</p>
        </div>
        <div class="footer">
          AurumSci © 2026 — Plataforma para Personal Trainers<br>
          <a href="https://aurumsc.com.br" style="color: #c9a961;">aurumsc.com.br</a>
        </div>
      </div>
    </body>
    </html>
    """

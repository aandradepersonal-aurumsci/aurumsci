import re

with open('/Users/andrepersonalnote/Personal_Trainer_Projeto/app/motor/ia_postural.py', 'r') as f:
    content = f.read()

old = '''async def analisar_postural(foto_frente=None, foto_lado=None, foto_costas=None):
    client = anthropic.Anthropic()
    
    imgs = []
    if foto_frente:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": foto_frente}})
    if foto_lado:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": foto_lado}})
    if foto_costas:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": foto_costas}})'''

new = '''async def analisar_postural(foto_frente=None, foto_lado=None, foto_costas=None,
                            mime_frente="image/jpeg", mime_lado="image/jpeg", mime_costas="image/jpeg"):
    client = anthropic.Anthropic()
    
    imgs = []
    if foto_frente:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_frente, "data": foto_frente}})
        imgs.append({"type": "text", "text": "Esta e a VISTA ANTERIOR (frente) do aluno."})
    if foto_lado:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_lado, "data": foto_lado}})
        imgs.append({"type": "text", "text": "Esta e a VISTA LATERAL do aluno."})
    if foto_costas:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_costas, "data": foto_costas}})
        imgs.append({"type": "text", "text": "Esta e a VISTA POSTERIOR (costas) do aluno."})'''

content = content.replace(old, new)

with open('/Users/andrepersonalnote/Personal_Trainer_Projeto/app/motor/ia_postural.py', 'w') as f:
    f.write(content)

print("OK!")

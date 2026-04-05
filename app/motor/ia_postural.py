"""
AurumSci Motor v1 - ia_postural.py
"""
from typing import Optional
from dataclasses import dataclass, field
import anthropic
import anthropic
import os
@dataclass
class ResultadoPostural:
    cabeca: str = ""
    ombros: str = ""
    coluna: str = ""
    quadril: str = ""
    joelhos: str = ""
    pes: str = ""
    observacoes: str = ""
    recomendacoes: list = field(default_factory=list)
    achados: list = field(default_factory=list)
    erro: Optional[str] = None

async def analisar_postural(foto_frente=None, foto_lado=None, foto_costas=None, mime_frente="image/jpeg", mime_lado="image/jpeg", mime_costas="image/jpeg"):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    imgs = []
    if foto_frente:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_frente, "data": foto_frente}})
        imgs.append({"type": "text", "text": "Vista anterior."})
    if foto_lado:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_lado, "data": foto_lado}})
    if foto_costas:
        imgs.append({"type": "image", "source": {"type": "base64", "media_type": mime_costas, "data": foto_costas}})
    
    if not imgs:
        return ResultadoPostural(erro="Nenhuma foto fornecida")
    
    prompt = {"type": "text", "text": """Voce e especialista em avaliacao postural para personal trainers.
Analise as fotos posturais e retorne APENAS um JSON valido sem markdown:
{
  "cabeca": "descricao do alinhamento da cabeca",
  "ombros": "descricao dos ombros",
  "coluna": "descricao da coluna",
  "quadril": "descricao do quadril",
  "joelhos": "descricao dos joelhos",
  "pes": "descricao dos pes",
  "observacoes": "observacoes gerais",
  "achados": ["desvio 1", "desvio 2"],
  "recomendacoes": ["exercicio corretivo 1", "exercicio corretivo 2", "exercicio corretivo 3"]
}
Use terminologia tecnica. Se nao visualizar bem algum segmento, indique Nao avaliado."""}
    
    imgs.append(prompt)
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": imgs}]
        )
        
        import json
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        
        return ResultadoPostural(
            cabeca=data.get("cabeca", ""),
            ombros=data.get("ombros", ""),
            coluna=data.get("coluna", ""),
            quadril=data.get("quadril", ""),
            joelhos=data.get("joelhos", ""),
            pes=data.get("pes", ""),
            observacoes=data.get("observacoes", ""),
            achados=data.get("achados", []),
            recomendacoes=data.get("recomendacoes", [])
        )
    except Exception as e:
        return ResultadoPostural(erro=str(e))

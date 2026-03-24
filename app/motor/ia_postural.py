"""
AurumSci Motor v1 - ia_postural.py
"""
from typing import Optional
from dataclasses import dataclass

@dataclass
class ResultadoPostural:
    cabeca: str = ""
    ombros: str = ""
    coluna: str = ""
    quadril: str = ""
    joelhos: str = ""
    pes: str = ""
    observacoes: str = ""
    recomendacoes: list = None
    achados: list = None
    erro: Optional[str] = None

async def analisar_postural(foto_frente=None, foto_lado=None, foto_costas=None):
    return ResultadoPostural(erro="Configure a API key")

def postural_to_dict(r):
    return {}

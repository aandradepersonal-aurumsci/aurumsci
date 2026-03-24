from datetime import date
from typing import Optional
from pydantic import BaseModel

class PagamentoCriar(BaseModel):
    aluno_id: int
    valor: float
    descricao: str
    data_vencimento: date
    metodo_pagamento: Optional[str] = None

class PagamentoAtualizar(BaseModel):
    valor: Optional[float] = None
    descricao: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    status: Optional[str] = None
    metodo_pagamento: Optional[str] = None

class PagamentoResposta(BaseModel):
    id: int
    aluno_id: int
    valor: float
    descricao: str
    data_vencimento: date
    data_pagamento: Optional[date] = None
    status: str
    metodo_pagamento: Optional[str] = None
    dias_atraso: Optional[int] = None
    model_config = {"from_attributes": True}

class MensalidadeGerar(BaseModel):
    aluno_id: int
    valor: float
    dia_vencimento: int = 10
    meses: int = 3
    descricao: Optional[str] = "Mensalidade Personal Trainer"

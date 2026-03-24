from datetime import date
from typing import Optional
from pydantic import BaseModel

class AnamneseCriar(BaseModel):
    aluno_id: int
    doencas_cronicas: Optional[str] = None
    medicamentos_uso: Optional[str] = None
    medicamentos_controlados: Optional[str] = None
    cirurgias: Optional[str] = None
    lesoes_anteriores: Optional[str] = None
    historico_familiar: Optional[str] = None
    dor_cervical: bool = False
    dor_ombro: bool = False
    dor_cotovelo: bool = False
    dor_punho: bool = False
    dor_lombar: bool = False
    dor_quadril: bool = False
    dor_joelho: bool = False
    dor_tornozelo: bool = False
    descricao_dores: Optional[str] = None
    fumante: bool = False
    ex_fumante: bool = False
    consumo_alcool: bool = False
    frequencia_alcool: Optional[str] = None
    pratica_atividade: bool = False
    modalidade_atual: Optional[str] = None
    frequencia_atual: Optional[int] = None
    tempo_pratica_meses: Optional[int] = None
    dias_disponiveis: Optional[int] = None
    tempo_por_sessao: Optional[int] = None
    local_treino: Optional[str] = None
    objetivo_detalhado: Optional[str] = None
    ja_treinou_antes: bool = False
    experiencia_anterior: Optional[str] = None
    horas_sono: Optional[float] = None
    nivel_estresse: Optional[int] = None
    observacoes: Optional[str] = None

class AnamnesesAtualizar(AnamneseCriar):
    aluno_id: Optional[int] = None

class AnamnesesResposta(AnamneseCriar):
    id: int
    data_avaliacao: date
    model_config = {"from_attributes": True}

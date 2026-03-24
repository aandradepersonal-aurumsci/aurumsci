from datetime import date
from typing import Optional, List
from pydantic import BaseModel

class ExercicioCriar(BaseModel):
    nome: str
    grupo_muscular: str
    equipamento: Optional[str] = None
    descricao: Optional[str] = None
    execucao: Optional[str] = None
    video_url: Optional[str] = None

class ExercicioResposta(ExercicioCriar):
    id: int
    model_config = {"from_attributes": True}

class ExercicioSessaoCriar(BaseModel):
    exercicio_id: int
    ordem: int = 1
    series: int = 3
    repeticoes: str = "10-12"
    carga_kg: Optional[float] = None
    tempo_descanso_seg: int = 60
    tecnica_especial: Optional[str] = None
    observacoes: Optional[str] = None

class ExercicioSessaoResposta(ExercicioSessaoCriar):
    id: int
    nome_exercicio: Optional[str] = None
    model_config = {"from_attributes": True}

class SessaoCriar(BaseModel):
    nome: str
    dia_semana: Optional[int] = None
    grupos_musculares: Optional[str] = None

class SessaoResposta(BaseModel):
    id: int
    nome: str
    dia_semana: Optional[int] = None
    grupos_musculares: Optional[str] = None
    model_config = {"from_attributes": True}

class PlanoTreinoCriar(BaseModel):
    aluno_id: int
    nome: str
    objetivo: str
    nivel: str
    dias_semana: int = 3
    semanas_total: int = 12
    tipo_periodizacao: str = "linear"
    data_inicio: Optional[date] = None
    observacoes: Optional[str] = None
    gerar_automatico: bool = True

class PlanoTreinoResposta(BaseModel):
    id: int
    aluno_id: int
    nome: str
    objetivo: str
    nivel: str
    dias_semana: int
    semanas_total: int
    tipo_periodizacao: str
    data_inicio: Optional[date] = None
    ativo: bool
    observacoes: Optional[str] = None
    model_config = {"from_attributes": True}

class PresencaCriar(BaseModel):
    aluno_id: int
    sessao_id: Optional[int] = None
    data: Optional[date] = None
    presente: bool = True
    duracao_minutos: Optional[int] = None
    sensacao_subjetiva: Optional[int] = None
    observacoes: Optional[str] = None

class PresencaResposta(PresencaCriar):
    id: int
    model_config = {"from_attributes": True}

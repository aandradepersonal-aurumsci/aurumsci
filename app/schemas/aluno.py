from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models import Sexo, ObjetivoAluno, NivelExperiencia

class AlunoBase(BaseModel):
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    sexo: Optional[Sexo] = None
    objetivo: Optional[ObjetivoAluno] = None
    nivel_experiencia: Optional[NivelExperiencia] = NivelExperiencia.INICIANTE

class AlunoCriar(AlunoBase):
    pass

class AlunoAtualizar(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    sexo: Optional[Sexo] = None
    objetivo: Optional[ObjetivoAluno] = None
    nivel_experiencia: Optional[NivelExperiencia] = None
    ativo: Optional[bool] = None

class AlunoResposta(AlunoBase):
    id: int
    personal_id: int
    ativo: bool
    foto_url: Optional[str] = None
    idade: Optional[int] = None
    precisa_reavaliar: Optional[bool] = None
    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_com_idade(cls, aluno):
        obj = cls.model_validate(aluno)
        if aluno.data_nascimento:
            hoje = date.today()
            obj.idade = (hoje.year - aluno.data_nascimento.year
                - ((hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)))
        return obj

class AlunoListagem(BaseModel):
    id: int
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    sexo: Optional[Sexo] = None
    objetivo: Optional[ObjetivoAluno] = None
    nivel_experiencia: Optional[NivelExperiencia] = None
    ativo: bool
    foto_url: Optional[str] = None
    idade: Optional[int] = None
    precisa_reavaliar: Optional[bool] = None
    model_config = {"from_attributes": True}

class PaginacaoAlunos(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    alunos: list[AlunoListagem]

from pydantic import BaseModel, EmailStr
from typing import Optional

class PersonalRegistro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cref: str
    telefone: Optional[str] = None
    cpf: Optional[str] = None

class PersonalLogin(BaseModel):
    email: EmailStr
    senha: str

class TokenResposta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    personal_id: int
    nome: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PersonalResposta(BaseModel):
    id: int
    nome: str
    email: str
    cref: Optional[str] = None
    telefone: Optional[str] = None
    ativo: bool
    model_config = {"from_attributes": True}

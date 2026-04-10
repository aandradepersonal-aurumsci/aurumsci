from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Sexo(PyEnum):
    MASCULINO = "masculino"
    FEMININO = "feminino"

class ObjetivoAluno(PyEnum):
    EMAGRECIMENTO = "emagrecimento"
    HIPERTROFIA = "hipertrofia"
    CONDICIONAMENTO = "condicionamento"
    REABILITACAO = "reabilitacao"
    QUALIDADE_DE_VIDA = "qualidade_de_vida"

class NivelExperiencia(PyEnum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"

class StatusPagamento(PyEnum):
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"
    REEMBOLSADO = "reembolsado"

class Personal(Base):
    __tablename__ = "personals"
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cref = Column(String(30), unique=True)
    telefone = Column(String(20))
    cpf = Column(String(14), unique=True)
    ativo = Column(Boolean, default=True)
    plano = Column(String(20), default="bronze")  # bronze/prata/ouro/diamante
    assinatura_status = Column(String(20), default="trial")  # trial/ativa/cancelada/expirada
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    criado_em = Column(DateTime, default=datetime.utcnow)
    alunos = relationship("Aluno", back_populates="personal")

class Aluno(Base):
    __tablename__ = "alunos"
    id = Column(Integer, primary_key=True)
    personal_id = Column(Integer, ForeignKey("personals.id"), nullable=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(200))
    telefone = Column(String(20))
    cpf = Column(String(14), unique=True)
    data_nascimento = Column(Date)
    sexo = Column(Enum(Sexo))
    objetivo = Column(Enum(ObjetivoAluno))
    nivel_experiencia = Column(Enum(NivelExperiencia), default=NivelExperiencia.INICIANTE)
    ativo = Column(Boolean, default=True)
    foto_url = Column(String(300))
    criado_em = Column(DateTime, default=datetime.utcnow)
    personal = relationship("Personal", back_populates="alunos")
    
    

class PagamentoModel(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String(255))
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    status = Column(Enum(StatusPagamento), default=StatusPagamento.PENDENTE)
    metodo_pagamento = Column(String(50))
    criado_em = Column(DateTime, default=datetime.utcnow)
    

class Presenca(Base):
    __tablename__ = "presencas"
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    data = Column(Date, default=date.today)
    presente = Column(Boolean, default=True)
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)


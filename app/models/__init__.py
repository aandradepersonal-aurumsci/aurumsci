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
    logo_url = Column(String(300))
    nome_empresa = Column(String(150))
    slogan = Column(String(200))
    criado_em = Column(DateTime, default=datetime.utcnow)
    # Validacao CREF + Contrato (27/04/2026)
    cref_estado = Column(String(2))
    cref_consultado_confef = Column(Boolean, default=False)
    cref_status = Column(String(20), default="pendente")  # pendente/ativo/suspenso/cancelado
    cref_validado_em = Column(DateTime)
    contrato_aceito_em = Column(DateTime)
    contrato_aceito_ip = Column(String(45))
    # Stripe Connect (split de pagamento aluno -> personal)
    stripe_account_id = Column(String(100))
    stripe_onboarding_completed = Column(Boolean, default=False)
    stripe_charges_enabled = Column(Boolean, default=False)
    stripe_payouts_enabled = Column(Boolean, default=False)
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
    assinatura_status = Column(String(20), default="trial")  # FIX 17/05/2026: trial/ativa/cancelada/expirada
    valor_assinatura = Column(String(20))
    foto_url = Column(String(300))
    criado_em = Column(DateTime, default=datetime.utcnow)
    # Cobranca automatica
    ciclo_cobranca = Column(String(20), default='mensal')
    dia_fechamento = Column(Integer, default=30)
    valor_aula = Column(Float)
    valor_mensal = Column(Float)
    dias_vencimento = Column(Integer, default=5)
    # Stripe
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    # Limite diario do Auri (chatbot) - protege custo de API
    auri_msgs_hoje = Column(Integer, default=0)
    auri_msgs_data = Column(Date)
    # Exclusao de conta
    data_solicitacao_exclusao = Column(DateTime)
    token_exclusao = Column(String(100))
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


class OnboardingLink(Base):
    """Link de convite que personal envia pros alunos preencherem questionario."""
    __tablename__ = "onboarding_links"
    id = Column(Integer, primary_key=True)
    personal_id = Column(Integer, ForeignKey("personals.id"), nullable=True)  # FIX 16/05/2026: nullable para suportar aluno autonomo (sem personal)
    token = Column(String(50), unique=True, nullable=False, index=True)
    ativo = Column(Boolean, default=True)
    total_usos = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)
    personal = relationship("Personal")

class AssinaturaIAP(Base):
    """Apple In-App Purchase — assinaturas via App Store iOS.
    
    Paralela ao Stripe: trainer pode assinar pelo iOS (IAP) ou Web (Stripe).
    Apple cobra 30% (15% após 1 ano). Stripe ~3.9%. Por isso preferimos Web.
    
    Cravado 23/05/2026 — Etapa 2 IAP.
    """
    __tablename__ = "assinaturas_iap"
    id = Column(Integer, primary_key=True)
    
    # Quem assinou (trainer OU aluno, nunca os dois)
    personal_id = Column(Integer, ForeignKey("personals.id"), nullable=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=True, index=True)
    
    # Produto Apple (ex: com.aurumsc.pro.bronze, com.aurumsc.aluno.mensal)
    product_id = Column(String(100), nullable=False, index=True)
    
    # IDs Apple (transaction = compra individual, original = assinatura recorrente)
    apple_transaction_id = Column(String(100), unique=True, nullable=False)
    apple_original_transaction_id = Column(String(100), nullable=False, index=True)
    
    # Status: trialing / active / expired / cancelled / refunded / in_grace_period
    status = Column(String(30), default="trialing", index=True)
    
    # Datas (em UTC)
    data_compra = Column(DateTime, nullable=False)
    data_expiracao = Column(DateTime)
    data_cancelamento = Column(DateTime)
    
    # Ambiente: 'sandbox' (testes) ou 'production' (real)
    ambiente = Column(String(20), default="sandbox", index=True)
    
    # Recibo bruto da Apple (pra re-validar se precisar)
    receipt_data = Column(Text)
    
    # Auto-renovação ativa?
    auto_renew = Column(Boolean, default=True)
    
    # Audit
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    personal = relationship("Personal")
    aluno = relationship("Aluno")

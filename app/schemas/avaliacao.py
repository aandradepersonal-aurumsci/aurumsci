"""
Schemas Pydantic — Avaliação Física
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator


class AvaliacaoCriar(BaseModel):
    aluno_id: int

    # ── Medidas básicas ──
    peso: Optional[float] = None
    estatura: Optional[float] = None

    # ── Dobras cutâneas Pollock 3 dobras ──
    # Masculino: peitoral, abdominal, coxa
    dc_peitoral: Optional[float] = None
    dc_abdominal: Optional[float] = None
    dc_coxa: Optional[float] = None
    # Feminino: triciptal, suprailíaca, coxa (dc_coxa reutilizada)
    dc_triciptal: Optional[float] = None
    dc_suprailíaca: Optional[float] = None

    # ── Circunferências (cm) ──
    circ_pescoco: Optional[float] = None
    circ_torax: Optional[float] = None
    circ_cintura: Optional[float] = None
    circ_abdomen: Optional[float] = None
    circ_quadril: Optional[float] = None
    circ_braco_d_relaxado: Optional[float] = None
    circ_braco_d_contraido: Optional[float] = None
    circ_braco_e_relaxado: Optional[float] = None
    circ_braco_e_contraido: Optional[float] = None
    circ_antebraco_d: Optional[float] = None
    circ_antebraco_e: Optional[float] = None
    circ_coxa_d: Optional[float] = None
    circ_coxa_e: Optional[float] = None
    circ_panturrilha_d: Optional[float] = None
    circ_panturrilha_e: Optional[float] = None

    # ── Testes físicos ──
    teste_flexibilidade_cm: Optional[float] = None
    teste_flexao_num: Optional[int] = None
    teste_barra_num: Optional[int] = None
    teste_cooper_metros: Optional[float] = None

    # ── Análise postural ──
    postura_cabeca: Optional[str] = None
    postura_ombros: Optional[str] = None
    postura_coluna: Optional[str] = None
    postura_quadril: Optional[str] = None
    postura_joelhos: Optional[str] = None
    postura_pes: Optional[str] = None
    postura_observacoes: Optional[str] = None

    observacoes: Optional[str] = None


class AvaliacaoResposta(AvaliacaoCriar):
    id: int
    data_avaliacao: date

    # Calculados pelo sistema
    imc: Optional[float] = None
    classificacao_imc: Optional[str] = None
    percentual_gordura: Optional[float] = None
    classificacao_gordura: Optional[str] = None
    massa_gorda_kg: Optional[float] = None
    massa_magra_kg: Optional[float] = None
    densidade_corporal: Optional[float] = None
    relacao_cintura_quadril: Optional[float] = None
    risco_cardiovascular: Optional[str] = None
    vo2max: Optional[float] = None
    classificacao_vo2: Optional[str] = None
    classificacao_flexibilidade: Optional[str] = None
    classificacao_flexao: Optional[str] = None

    model_config = {"from_attributes": True}

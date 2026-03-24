"""
AurumSci — Motor v1
Os modulos perguntam. O motor responde.
"""

from app.motor.calculos import (  # noqa: F401
    pollock3_masculino, pollock3_feminino, pollock7,
    bioimpedancia, calcular_massas, calcular_imc,
    calcular_rcq, classificar_gordura,
    classificar_flexibilidade, classificar_flexao,
    vo2_cooper, vo2_milha, vo2_step, gerar_alertas_aluno,
)

from app.motor.periodizacao import (  # noqa: F401
    gerar_periodizacao, periodizacao_to_dict, CONFIGS, DIVISOES,
)

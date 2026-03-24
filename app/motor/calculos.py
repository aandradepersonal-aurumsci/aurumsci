"""
AurumSci — Motor v1
calculos.py

Centraliza TODOS os cálculos científicos do sistema.
Os módulos perguntam. O motor responde.
"""


from dataclasses import dataclass
from typing import Optional


# ── Composição Corporal ───────────────────────────────────────────────────────

@dataclass
class ResultadoComposicao:
    percentual_gordura: float
    densidade_corporal: float
    massa_gorda_kg: float
    massa_magra_kg: float
    classificacao_gordura: str
    imc: Optional[float] = None
    classificacao_imc: Optional[str] = None
    relacao_cintura_quadril: Optional[float] = None
    risco_cardiovascular: Optional[str] = None


def pollock3_masculino(peitoral: float, abdominal: float, coxa: float, idade: int) -> ResultadoComposicao:
    """
    Pollock 3 dobras — Masculino
    Jackson & Pollock (1978)
    """
    soma = peitoral + abdominal + coxa
    dc = 1.10938 - (0.0008267 * soma) + (0.0000016 * soma**2) - (0.0002574 * idade)
    pct = round((495 / dc) - 450, 2)
    return _resultado_composicao(pct, dc, classificar_gordura(pct, "masculino", idade))


def pollock3_feminino(triciptal: float, suprailiaca: float, coxa: float, idade: int) -> ResultadoComposicao:
    """
    Pollock 3 dobras — Feminino
    Jackson & Pollock (1978)
    """
    soma = triciptal + suprailiaca + coxa
    dc = 1.0994921 - (0.0009929 * soma) + (0.0000023 * soma**2) - (0.0001392 * idade)
    pct = round((495 / dc) - 450, 2)
    return _resultado_composicao(pct, dc, classificar_gordura(pct, "feminino", idade))


def pollock7(peitoral: float, axilar: float, triceps: float, subescapular: float,
             abdominal: float, suprailiaca: float, coxa: float, idade: int, sexo: str) -> ResultadoComposicao:
    """
    Pollock 7 dobras — Masculino e Feminino
    Jackson & Pollock (1978)
    """
    soma = peitoral + axilar + triceps + subescapular + abdominal + suprailiaca + coxa
    if sexo == "masculino":
        dc = 1.112 - (0.00043499 * soma) + (0.00000055 * soma**2) - (0.00028826 * idade)
    else:
        dc = 1.097 - (0.00046971 * soma) + (0.00000056 * soma**2) - (0.00012828 * idade)
    pct = round((495 / dc) - 450, 2)
    return _resultado_composicao(pct, dc, classificar_gordura(pct, sexo, idade))


def bioimpedancia(percentual_gordura: float, peso: float, massa_gorda_kg: Optional[float] = None,
                  massa_magra_kg: Optional[float] = None) -> ResultadoComposicao:
    """
    Bioimpedância — dados inseridos pelo aparelho
    """
    mg = massa_gorda_kg if massa_gorda_kg else round(peso * (percentual_gordura / 100), 2)
    mm = massa_magra_kg if massa_magra_kg else round(peso - mg, 2)
    dc = round(495 / (percentual_gordura + 450), 4) if percentual_gordura > 0 else 1.0
    return ResultadoComposicao(
        percentual_gordura=round(percentual_gordura, 2),
        densidade_corporal=dc,
        massa_gorda_kg=mg,
        massa_magra_kg=mm,
        classificacao_gordura="Calculado pelo aparelho",
    )


def _resultado_composicao(pct: float, dc: float, classificacao: str) -> ResultadoComposicao:
    return ResultadoComposicao(
        percentual_gordura=max(round(pct, 2), 0),
        densidade_corporal=round(dc, 4),
        massa_gorda_kg=0.0,  # calculado depois com o peso
        massa_magra_kg=0.0,
        classificacao_gordura=classificacao,
    )


def calcular_massas(resultado: ResultadoComposicao, peso: float) -> ResultadoComposicao:
    """Calcula massa gorda e magra com o peso do avaliado"""
    resultado.massa_gorda_kg = round(peso * (resultado.percentual_gordura / 100), 2)
    resultado.massa_magra_kg = round(peso - resultado.massa_gorda_kg, 2)
    return resultado


def classificar_gordura(pct: float, sexo: str, idade: int) -> str:
    """
    Classificação do % de gordura
    American Council on Exercise (ACE)
    """
    if sexo == "masculino":
        if pct < 6:    return "Abaixo do essencial"
        if pct < 14:   return "Atleta"
        if pct < 18:   return "Boa forma"
        if pct < 25:   return "Aceitável"
        return "Obesidade"
    else:
        if pct < 14:   return "Abaixo do essencial"
        if pct < 21:   return "Atleta"
        if pct < 25:   return "Boa forma"
        if pct < 32:   return "Aceitável"
        return "Obesidade"


# ── IMC ───────────────────────────────────────────────────────────────────────

def calcular_imc(peso: float, estatura_cm: float) -> tuple[float, str]:
    """
    Índice de Massa Corporal — OMS
    """
    estatura_m = estatura_cm / 100
    imc = round(peso / (estatura_m ** 2), 2)
    if imc < 18.5:   cls = "Abaixo do peso"
    elif imc < 25.0: cls = "Peso normal"
    elif imc < 30.0: cls = "Sobrepeso"
    elif imc < 35.0: cls = "Obesidade grau I"
    elif imc < 40.0: cls = "Obesidade grau II"
    else:            cls = "Obesidade grau III"
    return imc, cls


# ── Relação Cintura/Quadril ───────────────────────────────────────────────────

def calcular_rcq(cintura: float, quadril: float, sexo: str) -> tuple[float, str]:
    """
    Relação Cintura/Quadril — OMS
    Risco cardiovascular
    """
    rcq = round(cintura / quadril, 3)
    if sexo == "masculino":
        if rcq < 0.90: risco = "Baixo"
        elif rcq < 0.95: risco = "Moderado"
        else: risco = "Alto"
    else:
        if rcq < 0.80: risco = "Baixo"
        elif rcq < 0.85: risco = "Moderado"
        else: risco = "Alto"
    return rcq, risco


# ── VO2max ────────────────────────────────────────────────────────────────────

@dataclass
class ResultadoVO2:
    vo2max: float
    classificacao: str
    protocolo: str


def vo2_cooper(distancia_metros: float, sexo: str, idade: int) -> ResultadoVO2:
    """
    Teste de Cooper 12 minutos
    Cooper (1968)
    """
    vo2 = max(round((distancia_metros - 504.9) / 44.73, 2), 0)
    return ResultadoVO2(
        vo2max=vo2,
        classificacao=classificar_vo2(vo2, sexo, idade),
        protocolo="Cooper 12 min"
    )


def vo2_milha(tempo_min: float, fc_final: float, peso_kg: float, sexo: str, idade: int) -> ResultadoVO2:
    """
    Teste da Milha (1.609m caminhando)
    Kline et al. (1987)
    """
    sexo_num = 1 if sexo == "masculino" else 0
    vo2 = max(round(
        132.853 - (0.0769 * peso_kg) - (0.3877 * idade) +
        (6.315 * sexo_num) - (3.2649 * tempo_min) - (0.1565 * fc_final), 2
    ), 0)
    return ResultadoVO2(
        vo2max=vo2,
        classificacao=classificar_vo2(vo2, sexo, idade),
        protocolo="Teste da Milha (Kline 1987)"
    )


def vo2_step(fc_recuperacao: float, sexo: str, idade: int) -> ResultadoVO2:
    """
    Teste do Step — 3 minutos
    McArdle et al. (1972)
    Ideal para idosos e sedentários
    """
    if sexo == "masculino":
        vo2 = max(round(111.33 - (0.42 * fc_recuperacao), 2), 0)
    else:
        vo2 = max(round(65.81 - (0.1847 * fc_recuperacao), 2), 0)
    return ResultadoVO2(
        vo2max=vo2,
        classificacao=classificar_vo2(vo2, sexo, idade),
        protocolo="Teste do Step (McArdle 1972)"
    )


def classificar_vo2(vo2: float, sexo: str, idade: int) -> str:
    """
    Classificação do VO2max — ACSM
    Americam College of Sports Medicine
    """
    if sexo == "masculino":
        tabela = [
            (20, 29, [(37, "Muito fraco"), (44, "Fraco"), (51, "Regular"), (57, "Bom"), (63, "Excelente"), (999, "Superior")]),
            (30, 39, [(35, "Muito fraco"), (42, "Fraco"), (48, "Regular"), (54, "Bom"), (60, "Excelente"), (999, "Superior")]),
            (40, 49, [(33, "Muito fraco"), (39, "Fraco"), (45, "Regular"), (51, "Bom"), (57, "Excelente"), (999, "Superior")]),
            (50, 59, [(31, "Muito fraco"), (37, "Fraco"), (42, "Regular"), (47, "Bom"), (53, "Excelente"), (999, "Superior")]),
            (60, 99, [(28, "Muito fraco"), (34, "Fraco"), (39, "Regular"), (44, "Bom"), (50, "Excelente"), (999, "Superior")]),
        ]
    else:
        tabela = [
            (20, 29, [(28, "Muito fraco"), (34, "Fraco"), (39, "Regular"), (44, "Bom"), (50, "Excelente"), (999, "Superior")]),
            (30, 39, [(26, "Muito fraco"), (31, "Fraco"), (36, "Regular"), (41, "Bom"), (46, "Excelente"), (999, "Superior")]),
            (40, 49, [(24, "Muito fraco"), (29, "Fraco"), (34, "Regular"), (38, "Bom"), (43, "Excelente"), (999, "Superior")]),
            (50, 59, [(21, "Muito fraco"), (26, "Fraco"), (30, "Regular"), (35, "Bom"), (40, "Excelente"), (999, "Superior")]),
            (60, 99, [(18, "Muito fraco"), (23, "Fraco"), (27, "Regular"), (31, "Bom"), (36, "Excelente"), (999, "Superior")]),
        ]

    for idade_min, idade_max, faixas in tabela:
        if idade_min <= idade <= idade_max:
            for limite, cls in faixas:
                if vo2 <= limite:
                    return cls
    return "Regular"


# ── Flexibilidade ─────────────────────────────────────────────────────────────

def classificar_flexibilidade(cm: float, sexo: str, idade: int) -> str:
    """
    Teste de Wells — Banco de sentar e alcançar
    ACSM Guidelines
    """
    if sexo == "masculino":
        if idade < 30:
            tabela = [(-8, "Muito fraco"), (0, "Fraco"), (8, "Regular"), (15, "Bom"), (20, "Excelente"), (999, "Superior")]
        elif idade < 40:
            tabela = [(-10, "Muito fraco"), (-2, "Fraco"), (6, "Regular"), (13, "Bom"), (18, "Excelente"), (999, "Superior")]
        else:
            tabela = [(-12, "Muito fraco"), (-4, "Fraco"), (4, "Regular"), (11, "Bom"), (16, "Excelente"), (999, "Superior")]
    else:
        if idade < 30:
            tabela = [(-1, "Muito fraco"), (7, "Fraco"), (15, "Regular"), (22, "Bom"), (27, "Excelente"), (999, "Superior")]
        elif idade < 40:
            tabela = [(-3, "Muito fraco"), (5, "Fraco"), (13, "Regular"), (20, "Bom"), (25, "Excelente"), (999, "Superior")]
        else:
            tabela = [(-5, "Muito fraco"), (3, "Fraco"), (11, "Regular"), (18, "Bom"), (23, "Excelente"), (999, "Superior")]

    for limite, cls in tabela:
        if cm <= limite:
            return cls
    return "Regular"


# ── Força ─────────────────────────────────────────────────────────────────────

def classificar_flexao(repeticoes: int, sexo: str, idade: int) -> str:
    """
    Classificação do teste de flexão de braço
    Canadian Society for Exercise Physiology
    """
    if sexo == "masculino":
        if idade < 30:
            tabela = [(15, "Muito fraco"), (24, "Fraco"), (34, "Regular"), (44, "Bom"), (54, "Excelente"), (999, "Superior")]
        elif idade < 40:
            tabela = [(10, "Muito fraco"), (19, "Fraco"), (29, "Regular"), (39, "Bom"), (49, "Excelente"), (999, "Superior")]
        else:
            tabela = [(8, "Muito fraco"), (14, "Fraco"), (24, "Regular"), (34, "Bom"), (44, "Excelente"), (999, "Superior")]
    else:
        if idade < 30:
            tabela = [(7, "Muito fraco"), (14, "Fraco"), (20, "Regular"), (29, "Bom"), (35, "Excelente"), (999, "Superior")]
        elif idade < 40:
            tabela = [(5, "Muito fraco"), (11, "Fraco"), (17, "Regular"), (24, "Bom"), (30, "Excelente"), (999, "Superior")]
        else:
            tabela = [(2, "Muito fraco"), (8, "Fraco"), (14, "Regular"), (21, "Bom"), (27, "Excelente"), (999, "Superior")]

    for limite, cls in tabela:
        if repeticoes <= limite:
            return cls
    return "Regular"


# ── Alertas automáticos ───────────────────────────────────────────────────────

@dataclass
class AlertaAvaliacao:
    tipo: str        # reavaliacao, frequencia, pagamento
    prioridade: str  # alta, media, baixa
    mensagem: str
    dias_restantes: Optional[int] = None


def gerar_alertas_aluno(
    ultima_avaliacao_dias: int,
    frequencia_pct: float,
    semanas_mesociclo: int = 4,
    pagamento_atrasado: bool = False
) -> list[AlertaAvaliacao]:
    """
    Gera alertas automáticos para o personal sobre o aluno
    """
    alertas = []

    # Alerta de reavaliação (a cada 8 semanas / 2 meses)
    if ultima_avaliacao_dias >= 56:
        alertas.append(AlertaAvaliacao(
            tipo="reavaliacao",
            prioridade="alta" if ultima_avaliacao_dias >= 90 else "media",
            mensagem=f"Reavaliação pendente há {ultima_avaliacao_dias} dias. Recomendado a cada 8 semanas!",
            dias_restantes=0
        ))
    elif ultima_avaliacao_dias >= 45:
        alertas.append(AlertaAvaliacao(
            tipo="reavaliacao",
            prioridade="baixa",
            mensagem=f"Reavaliação em {56 - ultima_avaliacao_dias} dias.",
            dias_restantes=56 - ultima_avaliacao_dias
        ))

    # Alerta de frequência baixa
    if frequencia_pct < 60:
        alertas.append(AlertaAvaliacao(
            tipo="frequencia",
            prioridade="alta",
            mensagem=f"Frequência crítica: {frequencia_pct:.0f}%. Aluno em risco de abandono!",
        ))
    elif frequencia_pct < 75:
        alertas.append(AlertaAvaliacao(
            tipo="frequencia",
            prioridade="media",
            mensagem=f"Frequência abaixo do ideal: {frequencia_pct:.0f}%. Meta: 80%+",
        ))

    # Alerta de pagamento
    if pagamento_atrasado:
        alertas.append(AlertaAvaliacao(
            tipo="pagamento",
            prioridade="alta",
            mensagem="Pagamento em atraso. Verificar situação financeira do aluno.",
        ))

    return alertas

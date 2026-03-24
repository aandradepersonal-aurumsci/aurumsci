"""
AurumSci — Motor v1
periodizacao.py

Gerador de periodização automática.
Macro → Meso → Microciclo
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, timedelta


# ── Configurações por objetivo ────────────────────────────────────────────────

CONFIGS = {
    "hipertrofia": {
        "series": (3, 4), "reps": "8-12", "intensidade": 0.70, "progressao": 2.5,
        "fases": ["Adaptação Neural", "Volume I", "Volume II", "Intensidade"],
        "descricao": "Foco em hipertrofia muscular com progressão de carga gradual.",
        "deload_reducao": 0.60,
    },
    "forca": {
        "series": (4, 6), "reps": "3-6", "intensidade": 0.85, "progressao": 1.5,
        "fases": ["Adaptação", "Acumulação", "Transmutação", "Realização"],
        "descricao": "Foco em força máxima com alta intensidade e baixo volume.",
        "deload_reducao": 0.55,
    },
    "emagrecimento": {
        "series": (3, 4), "reps": "12-20", "intensidade": 0.60, "progressao": 2.0,
        "fases": ["Adaptação", "Queima I", "Queima II", "Manutenção"],
        "descricao": "Foco em gasto calórico com alta repetição e menor descanso.",
        "deload_reducao": 0.65,
    },
    "condicionamento": {
        "series": (2, 4), "reps": "15-20", "intensidade": 0.55, "progressao": 3.0,
        "fases": ["Base Aeróbica", "Desenvolvimento", "Pico", "Manutenção"],
        "descricao": "Foco em capacidade cardiorrespiratória e resistência muscular.",
        "deload_reducao": 0.65,
    },
    "reabilitacao": {
        "series": (2, 3), "reps": "15-20", "intensidade": 0.50, "progressao": 1.0,
        "fases": ["Ativação", "Fortalecimento I", "Fortalecimento II", "Funcional"],
        "descricao": "Foco em recuperação funcional com baixa intensidade e controle.",
        "deload_reducao": 0.70,
    },
}

DIVISOES = {
    2: {
        "nome": "Full Body AB",
        "sessoes": ["Full Body A", "Full Body B"],
        "descricao": "Treino de corpo inteiro 2x por semana. Ideal para iniciantes.",
    },
    3: {
        "nome": "ABC",
        "sessoes": ["Peito + Tríceps", "Costas + Bíceps", "Pernas + Ombros"],
        "descricao": "Divisão clássica 3x. Cada grupo muscular 1x por semana.",
    },
    4: {
        "nome": "ABCD",
        "sessoes": ["Peito + Tríceps", "Costas + Bíceps", "Pernas Anterior", "Pernas Posterior + Ombros"],
        "descricao": "Divisão 4x com maior volume por sessão.",
    },
    5: {
        "nome": "ABCDE",
        "sessoes": ["Peito", "Costas", "Pernas", "Ombros", "Braços"],
        "descricao": "Divisão avançada. Um grupo muscular por dia.",
    },
    6: {
        "nome": "Push/Pull/Legs",
        "sessoes": ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"],
        "descricao": "Divisão PPL 2x. Cada grupo muscular 2x por semana.",
    },
}


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Microciclo:
    semana: int
    deload: bool
    intensidade_percentual: float
    series: int
    repeticoes: str
    sessoes: list
    descricao: str


@dataclass
class Mesociclo:
    numero: int
    fase: str
    semanas: int
    data_inicio: Optional[date]
    data_fim: Optional[date]
    microciclos: list
    descricao_fase: str
    alerta_reavaliacao: bool  # True no último meso


@dataclass
class Periodizacao:
    objetivo: str
    nivel: str
    dias_semana: int
    semanas_total: int
    divisao_nome: str
    divisao_sessoes: list
    divisao_descricao: str
    objetivo_descricao: str
    data_inicio: Optional[date]
    data_fim: Optional[date]
    mesociclos: list
    total_semanas_treino: int
    total_semanas_deload: int
    recomendacao_reavaliacao: str


# ── Gerador principal ─────────────────────────────────────────────────────────

def gerar_periodizacao(
    objetivo: str,
    nivel: str,
    dias_semana: int,
    semanas_total: int = 12,
    data_inicio: Optional[date] = None
) -> Periodizacao:
    """
    Gera periodização completa — Macro > Meso > Microciclo
    com deload automático na semana 4 de cada mesociclo
    e alerta de reavaliação no último mesociclo
    """

    cfg = CONFIGS.get(objetivo, CONFIGS["hipertrofia"])
    div = DIVISOES.get(dias_semana, DIVISOES[3])
    fases = cfg["fases"]
    inicio = data_inicio or date.today()
    num_mesos = semanas_total // 4

    mesociclos = []
    total_deload = 0

    for i in range(num_mesos):
        fase = fases[i] if i < len(fases) else f"Fase {i+1}"
        data_meso_inicio = inicio + timedelta(weeks=i * 4)
        data_meso_fim = data_meso_inicio + timedelta(weeks=4) - timedelta(days=1)
        ultimo_meso = (i == num_mesos - 1)

        microciclos = []
        for semana in range(1, 5):
            deload = semana == 4
            if deload:
                total_deload += 1

            intensidade_base = cfg["intensidade"]
            progressao = cfg["progressao"] / 100
            intensidade = round(
                intensidade_base * (1 + progressao * semana) *
                (cfg["deload_reducao"] if deload else 1.0) * 100, 1
            )

            series = cfg["series"][0] if deload else cfg["series"][1]

            if deload:
                descricao_micro = f"Semana de Deload — Redução de volume e intensidade para recuperação ativa. Manter movimento sem fadiga acumulada."
            else:
                descricao_micro = _descricao_microciclo(objetivo, semana, intensidade)

            microciclos.append(Microciclo(
                semana=semana,
                deload=deload,
                intensidade_percentual=intensidade,
                series=series,
                repeticoes=cfg["reps"],
                sessoes=div["sessoes"],
                descricao=descricao_micro,
            ))

        descricao_fase = _descricao_fase(objetivo, fase, i)

        mesociclos.append(Mesociclo(
            numero=i + 1,
            fase=fase,
            semanas=4,
            data_inicio=data_meso_inicio,
            data_fim=data_meso_fim,
            microciclos=microciclos,
            descricao_fase=descricao_fase,
            alerta_reavaliacao=ultimo_meso,
        ))

    data_fim = inicio + timedelta(weeks=semanas_total)

    return Periodizacao(
        objetivo=objetivo,
        nivel=nivel,
        dias_semana=dias_semana,
        semanas_total=semanas_total,
        divisao_nome=div["nome"],
        divisao_sessoes=div["sessoes"],
        divisao_descricao=div["descricao"],
        objetivo_descricao=cfg["descricao"],
        data_inicio=inicio,
        data_fim=data_fim,
        mesociclos=mesociclos,
        total_semanas_treino=semanas_total - total_deload,
        total_semanas_deload=total_deload,
        recomendacao_reavaliacao=f"Realizar nova avaliação física ao final do mesociclo {num_mesos} ({data_fim.strftime('%d/%m/%Y')})",
    )


def _descricao_microciclo(objetivo: str, semana: int, intensidade: float) -> str:
    base = {
        1: "Semana de introdução ao novo estímulo. Foco na execução técnica.",
        2: "Aumento progressivo do volume. Descansos controlados.",
        3: "Semana de maior intensidade do mesociclo. Superar marcas anteriores.",
    }
    return base.get(semana, f"Semana {semana} — {intensidade}% de intensidade.")


def _descricao_fase(objetivo: str, fase: str, indice: int) -> str:
    descricoes = {
        "hipertrofia": [
            "Adaptação Neural: O corpo aprende os movimentos. Foco em técnica e amplitude. Baixo risco de lesão.",
            "Volume I: Aumento progressivo do número de séries. Músculo começa a responder ao estímulo.",
            "Volume II: Pico de volume do macrociclo. Maior estímulo metabólico para crescimento muscular.",
            "Intensidade: Redução do volume com aumento da carga. Consolidação dos ganhos.",
        ],
        "forca": [
            "Adaptação: Ajuste ao padrão de movimento com cargas submáximas.",
            "Acumulação: Alto volume com intensidade moderada para base de força.",
            "Transmutação: Transição para alta intensidade com volume reduzido.",
            "Realização: Pico de força. Semana de teste de 1RM opcional.",
        ],
        "emagrecimento": [
            "Adaptação: Introdução ao protocolo metabólico. Aprendizado dos exercícios.",
            "Queima I: Aumento do gasto calórico com circuitos e menor descanso.",
            "Queima II: Máximo gasto calórico. Alta densidade de treino.",
            "Manutenção: Consolidação da perda. Prevenção do efeito platô.",
        ],
    }
    fases = descricoes.get(objetivo, [f"Fase {indice+1} do programa."] * 4)
    return fases[indice] if indice < len(fases) else f"Fase {indice+1} — continuidade do programa."


def periodizacao_to_dict(p: Periodizacao) -> dict:
    """Converte para dicionário para salvar no banco (JSON)"""
    return {
        "objetivo": p.objetivo,
        "nivel": p.nivel,
        "dias_semana": p.dias_semana,
        "semanas_total": p.semanas_total,
        "divisao_nome": p.divisao_nome,
        "divisao_sessoes": p.divisao_sessoes,
        "divisao_descricao": p.divisao_descricao,
        "objetivo_descricao": p.objetivo_descricao,
        "data_inicio": str(p.data_inicio) if p.data_inicio else None,
        "data_fim": str(p.data_fim) if p.data_fim else None,
        "total_semanas_treino": p.total_semanas_treino,
        "total_semanas_deload": p.total_semanas_deload,
        "recomendacao_reavaliacao": p.recomendacao_reavaliacao,
        "mesociclos": [
            {
                "numero": m.numero,
                "fase": m.fase,
                "semanas": m.semanas,
                "data_inicio": str(m.data_inicio) if m.data_inicio else None,
                "data_fim": str(m.data_fim) if m.data_fim else None,
                "descricao_fase": m.descricao_fase,
                "alerta_reavaliacao": m.alerta_reavaliacao,
                "microciclos": [
                    {
                        "semana": mc.semana,
                        "deload": mc.deload,
                        "intensidade_percentual": mc.intensidade_percentual,
                        "series": mc.series,
                        "repeticoes": mc.repeticoes,
                        "sessoes": mc.sessoes,
                        "descricao": mc.descricao,
                    }
                    for mc in m.microciclos
                ],
            }
            for m in p.mesociclos
        ],
    }

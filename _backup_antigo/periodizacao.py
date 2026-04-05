"""
AurumSci — Motor v2
periodizacao.py

Gerador de periodização automática completo.
Macro → Meso → Microciclo

Níveis: iniciante, intermediario1, intermediario2, avancado1, avancado2, avancado3
Divisões: 2x Full Body | 3x ABC | 4x ABC+Extra | 5x ABCDE
Técnicas: multi-série, drop set, bi-set, tri-set, rest-pause (por nível)
Força: Deadlift, Back Squat, Barra Fixa para intermediário/avançado
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import date, timedelta


# ── Níveis e suas características ────────────────────────────────────────────

NIVEIS = {
    "iniciante": {
        "label": "Iniciante",
        "meses": "0–6 meses",
        "series_base": 3,
        "series_max": 3,
        "intensidade_base": 0.60,
        "tecnicas": [],                        # sem técnicas especiais
        "exercicios_forca": False,
        "descricao": "Foco em técnica, amplitude e aprendizado motor.",
    },
    "intermediario1": {
        "label": "Intermediário 1",
        "meses": "6–18 meses",
        "series_base": 3,
        "series_max": 4,
        "intensidade_base": 0.65,
        "tecnicas": ["bi-set"],
        "exercicios_forca": False,
        "descricao": "Técnica consolidada, início de progressão de carga.",
    },
    "intermediario2": {
        "label": "Intermediário 2",
        "meses": "18–36 meses",
        "series_base": 4,
        "series_max": 5,
        "intensidade_base": 0.70,
        "tecnicas": ["bi-set", "drop-set"],
        "exercicios_forca": True,
        "descricao": "Livre + máquinas, maior volume e introdução a exercícios compostos pesados.",
    },
    "avancado1": {
        "label": "Avançado 1",
        "meses": "3–5 anos",
        "series_base": 4,
        "series_max": 5,
        "intensidade_base": 0.75,
        "tecnicas": ["bi-set", "drop-set", "tri-set", "rest-pause"],
        "exercicios_forca": True,
        "descricao": "Exercícios compostos complexos, alta intensidade.",
    },
    "avancado2": {
        "label": "Avançado 2",
        "meses": "5–8 anos",
        "series_base": 5,
        "series_max": 6,
        "intensidade_base": 0.80,
        "tecnicas": ["bi-set", "drop-set", "tri-set", "rest-pause", "multi-serie"],
        "exercicios_forca": True,
        "descricao": "Levantamentos olímpicos, alta intensidade e especialização.",
    },
    "avancado3": {
        "label": "Avançado 3",
        "meses": "8+ anos",
        "series_base": 5,
        "series_max": 7,
        "intensidade_base": 0.85,
        "tecnicas": ["bi-set", "drop-set", "tri-set", "rest-pause", "multi-serie"],
        "exercicios_forca": True,
        "descricao": "Atleta, competição, programação específica de alto rendimento.",
    },
}

# Mapeamento de aliases para normalização
NIVEL_ALIAS = {
    "iniciante":       "iniciante",
    "intermediario1":  "intermediario1",
    "intermediario 1": "intermediario1",
    "inter1":          "intermediario1",
    "intermediario2":  "intermediario2",
    "intermediario 2": "intermediario2",
    "inter2":          "intermediario2",
    "avancado1":       "avancado1",
    "avancado 1":      "avancado1",
    "ava1":            "avancado1",
    "avancado2":       "avancado2",
    "avancado 2":      "avancado2",
    "ava2":            "avancado2",
    "avancado3":       "avancado3",
    "avancado 3":      "avancado3",
    "ava3":            "avancado3",
}


# ── Banco de exercícios por grupo e nível ────────────────────────────────────

EXERCICIOS = {

    # ── PEITO ─────────────────────────────────────────────────────────────────
    "peito": {
        "iniciante": [
            {"nome": "Supino Reto com Barra",     "series": 3, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Supino Inclinado Halteres", "series": 3, "repeticoes": "10-12", "descanso": 75,  "tecnica": None},
            {"nome": "Crucifixo com Halteres",    "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Supino Reto com Barra",     "series": 4, "repeticoes": "8-12",  "descanso": 90,  "tecnica": None},
            {"nome": "Supino Inclinado Halteres", "series": 3, "repeticoes": "10-12", "descanso": 75,  "tecnica": None},
            {"nome": "Crucifixo na Polia",        "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": "bi-set com Supino"},
            {"nome": "Crossover",                 "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Supino Reto com Barra",     "series": 4, "repeticoes": "6-10",  "descanso": 120, "tecnica": None},
            {"nome": "Supino Inclinado Halteres", "series": 4, "repeticoes": "8-12",  "descanso": 90,  "tecnica": None},
            {"nome": "Supino Declinado",          "series": 3, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Crucifixo na Polia",        "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Crossover",                 "series": 3, "repeticoes": "15",    "descanso": 45,  "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Supino Reto com Barra",     "series": 5, "repeticoes": "5-8",   "descanso": 120, "tecnica": None},
            {"nome": "Supino Inclinado Halteres", "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": None},
            {"nome": "Supino Declinado",          "series": 3, "repeticoes": "10-12", "descanso": 90,  "tecnica": "bi-set com Crucifixo"},
            {"nome": "Crucifixo na Polia",        "series": 4, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
            {"nome": "Crossover",                 "series": 3, "repeticoes": "15",    "descanso": 30,  "tecnica": "rest-pause"},
        ],
        "avancado2": [
            {"nome": "Supino Reto com Barra",     "series": 5, "repeticoes": "3-6",   "descanso": 150, "tecnica": "multi-serie"},
            {"nome": "Supino Inclinado Halteres", "series": 4, "repeticoes": "6-8",   "descanso": 90,  "tecnica": None},
            {"nome": "Supino Declinado",          "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": "bi-set com Crucifixo"},
            {"nome": "Crucifixo na Polia",        "series": 4, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
            {"nome": "Crossover",                 "series": 4, "repeticoes": "15-20", "descanso": 30,  "tecnica": "tri-set com Crucifixo e Polia"},
        ],
        "avancado3": [
            {"nome": "Supino Reto com Barra",     "series": 6, "repeticoes": "2-5",   "descanso": 180, "tecnica": "multi-serie"},
            {"nome": "Supino Inclinado Halteres", "series": 5, "repeticoes": "6-8",   "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Supino Declinado",          "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": "bi-set com Crucifixo"},
            {"nome": "Crucifixo na Polia",        "series": 5, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
            {"nome": "Crossover",                 "series": 4, "repeticoes": "15-20", "descanso": 30,  "tecnica": "tri-set"},
        ],
    },

    # ── COSTAS ────────────────────────────────────────────────────────────────
    "costas": {
        "iniciante": [
            {"nome": "Puxada Frontal",     "series": 3, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Remada Curvada",     "series": 3, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 3, "repeticoes": "10-12", "descanso": 75,  "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Puxada Frontal",     "series": 4, "repeticoes": "8-12",  "descanso": 90,  "tecnica": None},
            {"nome": "Remada Curvada",     "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 3, "repeticoes": "10-12", "descanso": 75,  "tecnica": "bi-set com Puxada"},
            {"nome": "Pulldown",           "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Barra Fixa",         "series": 4, "repeticoes": "6-10",  "descanso": 120, "tecnica": None},
            {"nome": "Remada Curvada",     "series": 4, "repeticoes": "6-8",   "descanso": 120, "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 3, "repeticoes": "8-10",  "descanso": 90,  "tecnica": None},
            {"nome": "Puxada Frontal",     "series": 3, "repeticoes": "10-12", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Remada Cavalinho",   "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Barra Fixa",         "series": 5, "repeticoes": "6-10",  "descanso": 120, "tecnica": None},
            {"nome": "Remada Curvada",     "series": 4, "repeticoes": "5-8",   "descanso": 120, "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Puxada Frontal",     "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Remada Cavalinho",   "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": "bi-set com Puxada"},
        ],
        "avancado2": [
            {"nome": "Barra Fixa",         "series": 5, "repeticoes": "8-12",  "descanso": 120, "tecnica": "multi-serie"},
            {"nome": "Remada Curvada",     "series": 5, "repeticoes": "4-6",   "descanso": 150, "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Puxada Frontal",     "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Remada Alta",        "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "tri-set com Puxada e Remada"},
        ],
        "avancado3": [
            {"nome": "Barra Fixa",         "series": 6, "repeticoes": "8-12",  "descanso": 120, "tecnica": "multi-serie"},
            {"nome": "Remada Curvada",     "series": 5, "repeticoes": "3-5",   "descanso": 180, "tecnica": None},
            {"nome": "Remada Unilateral",  "series": 4, "repeticoes": "6-8",   "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Puxada Frontal",     "series": 5, "repeticoes": "10-12", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Remada Alta",        "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "tri-set"},
        ],
    },

    # ── OMBROS ────────────────────────────────────────────────────────────────
    "ombros": {
        "iniciante": [
            {"nome": "Desenvolvimento Halteres", "series": 3, "repeticoes": "10-12", "descanso": 90, "tecnica": None},
            {"nome": "Elevacao Lateral",         "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
            {"nome": "Elevacao Frontal",         "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Desenvolvimento Halteres", "series": 4, "repeticoes": "10-12", "descanso": 90, "tecnica": None},
            {"nome": "Elevacao Lateral",         "series": 4, "repeticoes": "12-15", "descanso": 60, "tecnica": "bi-set com Elevacao Frontal"},
            {"nome": "Elevacao Frontal",         "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
            {"nome": "Remada Alta",              "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Desenvolvimento com Barra","series": 4, "repeticoes": "8-10",  "descanso": 90, "tecnica": None},
            {"nome": "Desenvolvimento Halteres", "series": 3, "repeticoes": "10-12", "descanso": 90, "tecnica": None},
            {"nome": "Elevacao Lateral",         "series": 4, "repeticoes": "12-15", "descanso": 45, "tecnica": "drop-set"},
            {"nome": "Elevacao Frontal",         "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
            {"nome": "Remada Alta",              "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Desenvolvimento com Barra","series": 5, "repeticoes": "6-8",   "descanso": 90, "tecnica": None},
            {"nome": "Desenvolvimento Halteres", "series": 4, "repeticoes": "8-10",  "descanso": 90, "tecnica": "rest-pause"},
            {"nome": "Elevacao Lateral",         "series": 5, "repeticoes": "12-15", "descanso": 45, "tecnica": "drop-set"},
            {"nome": "Elevacao Frontal",         "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": "bi-set com Lateral"},
            {"nome": "Remada Alta",              "series": 4, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
        ],
        "avancado2": [
            {"nome": "Desenvolvimento com Barra","series": 5, "repeticoes": "5-8",   "descanso": 90,  "tecnica": "multi-serie"},
            {"nome": "Desenvolvimento Halteres", "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Elevacao Lateral",         "series": 5, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
            {"nome": "Elevacao Frontal",         "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "bi-set com Lateral"},
            {"nome": "Remada Alta",              "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "tri-set"},
        ],
        "avancado3": [
            {"nome": "Desenvolvimento com Barra","series": 6, "repeticoes": "3-6",   "descanso": 120, "tecnica": "multi-serie"},
            {"nome": "Desenvolvimento Halteres", "series": 5, "repeticoes": "6-8",   "descanso": 90,  "tecnica": "rest-pause"},
            {"nome": "Elevacao Lateral",         "series": 6, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
            {"nome": "Elevacao Frontal",         "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "tri-set"},
            {"nome": "Remada Alta",              "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
        ],
    },

    # ── TRICEPS ───────────────────────────────────────────────────────────────
    "triceps": {
        "iniciante": [
            {"nome": "Triceps Pulley",   "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": None},
            {"nome": "Triceps Frances",  "series": 3, "repeticoes": "12",    "descanso": 60, "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Triceps Pulley",   "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Frances"},
            {"nome": "Triceps Frances",  "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Triceps Mergulho", "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Triceps Pulley",   "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "drop-set"},
            {"nome": "Triceps Frances",  "series": 3, "repeticoes": "8-10",  "descanso": 75, "tecnica": None},
            {"nome": "Triceps Mergulho", "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Triceps Testa",    "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Pulley"},
        ],
        "avancado1": [
            {"nome": "Triceps Pulley",   "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "drop-set"},
            {"nome": "Triceps Frances",  "series": 4, "repeticoes": "8-10",  "descanso": 75, "tecnica": "rest-pause"},
            {"nome": "Triceps Mergulho", "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Triceps Testa",    "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Pulley"},
        ],
        "avancado2": [
            {"nome": "Triceps Pulley",   "series": 5, "repeticoes": "10-12", "descanso": 60, "tecnica": "drop-set"},
            {"nome": "Triceps Frances",  "series": 4, "repeticoes": "6-8",   "descanso": 75, "tecnica": "rest-pause"},
            {"nome": "Triceps Mergulho", "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "multi-serie"},
            {"nome": "Triceps Testa",    "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "tri-set"},
        ],
        "avancado3": [
            {"nome": "Triceps Pulley",   "series": 5, "repeticoes": "10-12", "descanso": 60, "tecnica": "drop-set"},
            {"nome": "Triceps Frances",  "series": 5, "repeticoes": "5-8",   "descanso": 75, "tecnica": "rest-pause"},
            {"nome": "Triceps Mergulho", "series": 4, "repeticoes": "12",    "descanso": 60, "tecnica": "multi-serie"},
            {"nome": "Triceps Testa",    "series": 4, "repeticoes": "10-12", "descanso": 60, "tecnica": "tri-set"},
        ],
    },

    # ── BICEPS ────────────────────────────────────────────────────────────────
    "biceps": {
        "iniciante": [
            {"nome": "Rosca Direta",  "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Rosca Martelo", "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Rosca Direta",    "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Rosca Alternada", "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Martelo"},
            {"nome": "Rosca Martelo",   "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Rosca Direta",       "series": 4, "repeticoes": "8-10",  "descanso": 75, "tecnica": None},
            {"nome": "Rosca Alternada",    "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Martelo"},
            {"nome": "Rosca Martelo",      "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": None},
            {"nome": "Rosca Concentrada",  "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": "drop-set"},
        ],
        "avancado1": [
            {"nome": "Rosca Direta",       "series": 4, "repeticoes": "8-10",  "descanso": 75, "tecnica": "rest-pause"},
            {"nome": "Rosca Alternada",    "series": 4, "repeticoes": "8-10",  "descanso": 60, "tecnica": None},
            {"nome": "Rosca Martelo",      "series": 3, "repeticoes": "10-12", "descanso": 60, "tecnica": "bi-set com Alternada"},
            {"nome": "Rosca Concentrada",  "series": 3, "repeticoes": "12-15", "descanso": 60, "tecnica": "drop-set"},
        ],
        "avancado2": [
            {"nome": "Rosca Direta",       "series": 5, "repeticoes": "6-8",   "descanso": 75,  "tecnica": "rest-pause"},
            {"nome": "Rosca Alternada",    "series": 4, "repeticoes": "8-10",  "descanso": 60,  "tecnica": "multi-serie"},
            {"nome": "Rosca Martelo",      "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "bi-set com Alternada"},
            {"nome": "Rosca Concentrada",  "series": 3, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
        ],
        "avancado3": [
            {"nome": "Rosca Direta",       "series": 5, "repeticoes": "5-8",   "descanso": 75,  "tecnica": "rest-pause"},
            {"nome": "Rosca Alternada",    "series": 5, "repeticoes": "6-8",   "descanso": 60,  "tecnica": "multi-serie"},
            {"nome": "Rosca Martelo",      "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "tri-set"},
            {"nome": "Rosca Concentrada",  "series": 4, "repeticoes": "12-15", "descanso": 45,  "tecnica": "drop-set"},
        ],
    },

    # ── PERNAS ────────────────────────────────────────────────────────────────
    "pernas": {
        "iniciante": [
            {"nome": "Agachamento Livre",  "series": 3, "repeticoes": "10-12", "descanso": 120, "tecnica": None},
            {"nome": "Leg Press 45",       "series": 3, "repeticoes": "12-15", "descanso": 90,  "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
            {"nome": "Mesa Flexora",       "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": None},
            {"nome": "Panturrilha em Pe",  "series": 3, "repeticoes": "15-20", "descanso": 45,  "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Agachamento Livre",  "series": 4, "repeticoes": "8-12",  "descanso": 120, "tecnica": None},
            {"nome": "Leg Press 45",       "series": 4, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 3, "repeticoes": "12-15", "descanso": 60,  "tecnica": "bi-set com Flexora"},
            {"nome": "Mesa Flexora",       "series": 3, "repeticoes": "10-12", "descanso": 60,  "tecnica": None},
            {"nome": "Stiff",              "series": 3, "repeticoes": "10-12", "descanso": 75,  "tecnica": None},
            {"nome": "Panturrilha em Pe",  "series": 4, "repeticoes": "15-20", "descanso": 45,  "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Agachamento Livre",  "series": 4, "repeticoes": "6-10",  "descanso": 150, "tecnica": None},
            {"nome": "Leg Press 45",       "series": 4, "repeticoes": "10-12", "descanso": 90,  "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Mesa Flexora",       "series": 3, "repeticoes": "10-12", "descanso": 60,  "tecnica": None},
            {"nome": "Stiff",              "series": 4, "repeticoes": "8-10",  "descanso": 90,  "tecnica": None},
            {"nome": "Afundo",             "series": 3, "repeticoes": "10 cada","descanso": 75, "tecnica": None},
            {"nome": "Panturrilha em Pe",  "series": 4, "repeticoes": "15-20", "descanso": 45,  "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Back Squat",         "series": 5, "repeticoes": "5-8",   "descanso": 180, "tecnica": None},
            {"nome": "Leg Press 45",       "series": 4, "repeticoes": "8-10",  "descanso": 120, "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Mesa Flexora",       "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "rest-pause"},
            {"nome": "Stiff",              "series": 4, "repeticoes": "6-8",   "descanso": 90,  "tecnica": None},
            {"nome": "Afundo",             "series": 3, "repeticoes": "10 cada","descanso": 75, "tecnica": "bi-set com Agachamento"},
            {"nome": "Panturrilha em Pe",  "series": 5, "repeticoes": "15-20", "descanso": 45,  "tecnica": None},
        ],
        "avancado2": [
            {"nome": "Back Squat",         "series": 5, "repeticoes": "3-6",   "descanso": 180, "tecnica": "multi-serie"},
            {"nome": "Leg Press 45",       "series": 5, "repeticoes": "8-10",  "descanso": 120, "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 5, "repeticoes": "12-15", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Mesa Flexora",       "series": 4, "repeticoes": "10-12", "descanso": 60,  "tecnica": "rest-pause"},
            {"nome": "Stiff",              "series": 4, "repeticoes": "5-8",   "descanso": 90,  "tecnica": None},
            {"nome": "Afundo",             "series": 4, "repeticoes": "10 cada","descanso": 75, "tecnica": "tri-set com Leg e Extensora"},
            {"nome": "Panturrilha em Pe",  "series": 5, "repeticoes": "15-20", "descanso": 45,  "tecnica": "drop-set"},
        ],
        "avancado3": [
            {"nome": "Back Squat",         "series": 6, "repeticoes": "2-5",   "descanso": 240, "tecnica": "multi-serie"},
            {"nome": "Deadlift",           "series": 4, "repeticoes": "3-5",   "descanso": 240, "tecnica": None},
            {"nome": "Leg Press 45",       "series": 5, "repeticoes": "6-8",   "descanso": 120, "tecnica": None},
            {"nome": "Cadeira Extensora",  "series": 4, "repeticoes": "12-15", "descanso": 60,  "tecnica": "drop-set"},
            {"nome": "Mesa Flexora",       "series": 4, "repeticoes": "8-10",  "descanso": 60,  "tecnica": "rest-pause"},
            {"nome": "Stiff",              "series": 5, "repeticoes": "4-6",   "descanso": 90,  "tecnica": None},
            {"nome": "Panturrilha em Pe",  "series": 6, "repeticoes": "15-20", "descanso": 45,  "tecnica": "drop-set"},
        ],
    },

    # ── ABDÔMEN ───────────────────────────────────────────────────────────────
    "abdomen": {
        "iniciante": [
            {"nome": "Abdominal Crunch",   "series": 3, "repeticoes": "15-20", "descanso": 45, "tecnica": None},
            {"nome": "Prancha",            "series": 3, "repeticoes": "30s",   "descanso": 30, "tecnica": None},
        ],
        "intermediario1": [
            {"nome": "Abdominal Crunch",   "series": 3, "repeticoes": "15-20", "descanso": 45, "tecnica": None},
            {"nome": "Prancha",            "series": 3, "repeticoes": "45s",   "descanso": 30, "tecnica": "bi-set com Crunch"},
            {"nome": "Elevacao de Pernas", "series": 3, "repeticoes": "12-15", "descanso": 45, "tecnica": None},
        ],
        "intermediario2": [
            {"nome": "Abdominal Crunch",   "series": 4, "repeticoes": "15-20", "descanso": 45, "tecnica": None},
            {"nome": "Prancha",            "series": 3, "repeticoes": "60s",   "descanso": 30, "tecnica": None},
            {"nome": "Elevacao de Pernas", "series": 3, "repeticoes": "12-15", "descanso": 45, "tecnica": "bi-set com Crunch"},
            {"nome": "Abdominal Bicicleta","series": 3, "repeticoes": "20",    "descanso": 30, "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Abdominal Crunch",   "series": 4, "repeticoes": "20",    "descanso": 30, "tecnica": "tri-set"},
            {"nome": "Prancha",            "series": 4, "repeticoes": "60s",   "descanso": 30, "tecnica": None},
            {"nome": "Elevacao de Pernas", "series": 4, "repeticoes": "15",    "descanso": 30, "tecnica": "bi-set com Crunch"},
            {"nome": "Abdominal Bicicleta","series": 3, "repeticoes": "20",    "descanso": 30, "tecnica": None},
        ],
        "avancado2": [
            {"nome": "Abdominal Crunch",   "series": 4, "repeticoes": "20",    "descanso": 30, "tecnica": "tri-set"},
            {"nome": "Prancha",            "series": 4, "repeticoes": "90s",   "descanso": 30, "tecnica": None},
            {"nome": "Elevacao de Pernas", "series": 4, "repeticoes": "15-20", "descanso": 30, "tecnica": "drop-set"},
            {"nome": "Abdominal Bicicleta","series": 4, "repeticoes": "25",    "descanso": 30, "tecnica": None},
        ],
        "avancado3": [
            {"nome": "Abdominal Crunch",   "series": 5, "repeticoes": "20-25", "descanso": 30, "tecnica": "tri-set"},
            {"nome": "Prancha",            "series": 4, "repeticoes": "120s",  "descanso": 30, "tecnica": None},
            {"nome": "Elevacao de Pernas", "series": 4, "repeticoes": "15-20", "descanso": 30, "tecnica": "drop-set"},
            {"nome": "Abdominal Bicicleta","series": 4, "repeticoes": "30",    "descanso": 30, "tecnica": None},
        ],
    },

    # ── CORRETIVOS ────────────────────────────────────────────────────────────
    "corretivos": {
        "todos": [
            {"nome": "Alongamento de Peitoral",    "series": 2, "repeticoes": "30s", "descanso": 30, "tecnica": "CORRETIVO"},
            {"nome": "Fortalecimento de Escapula", "series": 2, "repeticoes": "15",  "descanso": 30, "tecnica": "CORRETIVO"},
            {"nome": "Mobilidade de Quadril",      "series": 2, "repeticoes": "10 cada", "descanso": 30, "tecnica": "CORRETIVO"},
            {"nome": "Alongamento de Ombros",      "series": 2, "repeticoes": "30s", "descanso": 30, "tecnica": "CORRETIVO"},
            {"nome": "Ativacao de Gluteos",        "series": 2, "repeticoes": "15",  "descanso": 30, "tecnica": "CORRETIVO"},
        ],
    },

    # ── FORÇA ESPECIAL (intermediário 2+) ────────────────────────────────────
    "forca_especial": {
        "intermediario2": [
            {"nome": "Deadlift",   "series": 4, "repeticoes": "5-6",  "descanso": 180, "tecnica": None},
            {"nome": "Back Squat", "series": 4, "repeticoes": "5-8",  "descanso": 180, "tecnica": None},
            {"nome": "Barra Fixa", "series": 4, "repeticoes": "6-10", "descanso": 120, "tecnica": None},
        ],
        "avancado1": [
            {"nome": "Deadlift",   "series": 5, "repeticoes": "4-5",  "descanso": 240, "tecnica": None},
            {"nome": "Back Squat", "series": 5, "repeticoes": "4-6",  "descanso": 240, "tecnica": None},
            {"nome": "Barra Fixa", "series": 5, "repeticoes": "6-10", "descanso": 120, "tecnica": "multi-serie"},
        ],
        "avancado2": [
            {"nome": "Deadlift",   "series": 5, "repeticoes": "3-5",  "descanso": 300, "tecnica": "multi-serie"},
            {"nome": "Back Squat", "series": 5, "repeticoes": "3-5",  "descanso": 300, "tecnica": "multi-serie"},
            {"nome": "Barra Fixa", "series": 5, "repeticoes": "8-12", "descanso": 120, "tecnica": "multi-serie"},
        ],
        "avancado3": [
            {"nome": "Deadlift",   "series": 6, "repeticoes": "2-4",  "descanso": 360, "tecnica": "multi-serie"},
            {"nome": "Back Squat", "series": 6, "repeticoes": "2-4",  "descanso": 360, "tecnica": "multi-serie"},
            {"nome": "Barra Fixa", "series": 6, "repeticoes": "8-12", "descanso": 120, "tecnica": "multi-serie"},
        ],
    },
}


# ── Divisões por frequência ───────────────────────────────────────────────────

DIVISOES = {
    2: {
        "nome": "Full Body 2x",
        "descricao": "Treino de corpo inteiro 2x por semana. Ideal para iniciantes.",
        "sessoes": [
            {"nome": "Full Body A", "grupos": ["peito", "costas", "pernas", "ombros", "triceps", "biceps", "abdomen"]},
            {"nome": "Full Body B", "grupos": ["peito", "costas", "pernas", "ombros", "triceps", "biceps", "abdomen"]},
        ],
        "dias_treino": [1, 4],  # Seg, Qui
    },
    3: {
        "nome": "ABC 3x",
        "descricao": "Divisão clássica 3x: A=Peito/Ombro/Tríceps | B=Costas/Bíceps | C=Pernas",
        "sessoes": [
            {"nome": "A — Peito, Ombro & Triceps", "grupos": ["peito", "ombros", "triceps"]},
            {"nome": "B — Costas & Biceps",         "grupos": ["costas", "biceps"]},
            {"nome": "C — Pernas",                  "grupos": ["pernas", "abdomen"]},
        ],
        "dias_treino": [1, 3, 5],  # Seg, Qua, Sex
    },
    4: {
        "nome": "ABCD 4x",
        "descricao": "A=Peito/Ombro/Tríceps | B=Costas/Bíceps | C=Pernas | D=Full Body Extra",
        "sessoes": [
            {"nome": "A — Peito, Ombro & Triceps", "grupos": ["peito", "ombros", "triceps"]},
            {"nome": "B — Costas & Biceps",         "grupos": ["costas", "biceps"]},
            {"nome": "C — Pernas",                  "grupos": ["pernas", "abdomen"]},
            {"nome": "D — Full Body Extra",         "grupos": ["peito", "costas", "pernas"]},
        ],
        "dias_treino": [1, 2, 4, 5],  # Seg, Ter, Qui, Sex
    },
    5: {
        "nome": "ABCDE 5x",
        "descricao": "A=Peito | B=Costas | C=Ombros | D=Braços | E=Pernas. Divisão avançada.",
        "sessoes": [
            {"nome": "A — Peito",   "grupos": ["peito"]},
            {"nome": "B — Costas",  "grupos": ["costas"]},
            {"nome": "C — Ombros",  "grupos": ["ombros"]},
            {"nome": "D — Bracos",  "grupos": ["biceps", "triceps"]},
            {"nome": "E — Pernas",  "grupos": ["pernas", "abdomen"]},
        ],
        "dias_treino": [1, 2, 3, 4, 5],  # Seg a Sex
    },
    6: {
        "nome": "Push Pull Legs 2x",
        "descricao": "PPL 6x — cada grupo muscular 2x por semana. Para avançados.",
        "sessoes": [
            {"nome": "Push A — Peito, Ombro & Triceps", "grupos": ["peito", "ombros", "triceps"]},
            {"nome": "Pull A — Costas & Biceps",         "grupos": ["costas", "biceps"]},
            {"nome": "Legs A — Pernas",                  "grupos": ["pernas", "abdomen"]},
            {"nome": "Push B — Peito, Ombro & Triceps",  "grupos": ["peito", "ombros", "triceps"]},
            {"nome": "Pull B — Costas & Biceps",         "grupos": ["costas", "biceps"]},
            {"nome": "Legs B — Pernas",                  "grupos": ["pernas", "abdomen"]},
        ],
        "dias_treino": [1, 2, 3, 4, 5, 6],
    },
}


# ── Configurações por objetivo ────────────────────────────────────────────────

CONFIGS = {
    "hipertrofia": {
        "series": (3, 5), "reps": "8-12", "intensidade": 0.70, "progressao": 2.5,
        "fases": ["Adaptacao Neural", "Volume I", "Volume II", "Intensidade"],
        "descricao": "Foco em hipertrofia muscular com progressao de carga gradual.",
        "deload_reducao": 0.60,
    },
    "forca": {
        "series": (4, 6), "reps": "3-6", "intensidade": 0.85, "progressao": 1.5,
        "fases": ["Adaptacao", "Acumulacao", "Transmutacao", "Realizacao"],
        "descricao": "Foco em forca maxima com alta intensidade e baixo volume.",
        "deload_reducao": 0.55,
    },
    "emagrecimento": {
        "series": (3, 4), "reps": "12-20", "intensidade": 0.60, "progressao": 2.0,
        "fases": ["Adaptacao", "Queima I", "Queima II", "Manutencao"],
        "descricao": "Foco em gasto calorico com alta repeticao e menor descanso.",
        "deload_reducao": 0.65,
    },
    "condicionamento": {
        "series": (2, 4), "reps": "15-20", "intensidade": 0.55, "progressao": 3.0,
        "fases": ["Base Aerobica", "Desenvolvimento", "Pico", "Manutencao"],
        "descricao": "Foco em capacidade cardiorrespiratoria e resistencia muscular.",
        "deload_reducao": 0.65,
    },
    "reabilitacao": {
        "series": (2, 3), "reps": "15-20", "intensidade": 0.50, "progressao": 1.0,
        "fases": ["Ativacao", "Fortalecimento I", "Fortalecimento II", "Funcional"],
        "descricao": "Foco em recuperacao funcional com baixa intensidade e controle.",
        "deload_reducao": 0.70,
    },
}


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class ExercicioPrescrito:
    nome: str
    grupo: str
    series: int
    repeticoes: str
    descanso_segundos: int
    tecnica_especial: Optional[str]
    ordem: int


@dataclass
class SessaoPrescrita:
    nome: str
    grupos: List[str]
    exercicios: List[ExercicioPrescrito]
    dia_semana: int


@dataclass
class Microciclo:
    semana: int
    deload: bool
    intensidade_percentual: float
    series: int
    repeticoes: str
    sessoes: List[str]
    descricao: str


@dataclass
class Mesociclo:
    numero: int
    fase: str
    semanas: int
    data_inicio: Optional[date]
    data_fim: Optional[date]
    microciclos: List[Microciclo]
    descricao_fase: str
    alerta_reavaliacao: bool


@dataclass
class Periodizacao:
    objetivo: str
    nivel: str
    nivel_label: str
    dias_semana: int
    semanas_total: int
    divisao_nome: str
    divisao_sessoes: List[str]
    divisao_descricao: str
    objetivo_descricao: str
    tecnicas_disponiveis: List[str]
    data_inicio: Optional[date]
    data_fim: Optional[date]
    mesociclos: List[Mesociclo]
    sessoes_prescritas: List[SessaoPrescrita]
    total_semanas_treino: int
    total_semanas_deload: int
    recomendacao_reavaliacao: str


# ── Funções auxiliares ────────────────────────────────────────────────────────

def normalizar_nivel(nivel: str) -> str:
    """Normaliza o nível para a chave correta."""
    nivel_lower = nivel.lower().strip().replace("-", "").replace("_", "")
    return NIVEL_ALIAS.get(nivel_lower, "iniciante")


def get_exercicios_grupo(grupo: str, nivel: str) -> List[dict]:
    """Retorna exercícios de um grupo para o nível, com fallback para nível anterior."""
    banco = EXERCICIOS.get(grupo, {})

    # Corretivos têm categoria única
    if grupo == "corretivos":
        return banco.get("todos", [])

    # Ordem de fallback: avancado3 → avancado2 → avancado1 → intermediario2 → intermediario1 → iniciante
    fallback_order = [
        "avancado3", "avancado2", "avancado1",
        "intermediario2", "intermediario1", "iniciante"
    ]

    # Busca direto
    if nivel in banco:
        return banco[nivel]

    # Fallback para nível mais próximo abaixo
    nivel_idx = fallback_order.index(nivel) if nivel in fallback_order else len(fallback_order) - 1
    for n in fallback_order[nivel_idx:]:
        if n in banco:
            return banco[n]

    return []



def gerar_periodizacao(
    objetivo: str,
    nivel: str,
    dias_semana: int,
    semanas_total: int = 12,
    data_inicio: Optional[date] = None,
    tipo_periodizacao: str = "ondulatoria",
) -> "Periodizacao":
    # Redireciona para periodização em blocos se solicitado
    if tipo_periodizacao == "blocos":
        return gerar_periodizacao_blocos(
            objetivo=objetivo,
            nivel=nivel,
            dias_semana=dias_semana,
            semanas_total=semanas_total,
            data_inicio=data_inicio,
        )
    """
    Gera periodização completa — Macro > Meso > Microciclo
    com deload automático na semana 4 de cada mesociclo,
    alerta de reavaliação no último mesociclo,
    e exercícios prescritos por nível.
    """
    nivel_norm = normalizar_nivel(nivel)
    cfg_nivel = NIVEIS.get(nivel_norm, NIVEIS["iniciante"])
    cfg_obj = CONFIGS.get(objetivo, CONFIGS["hipertrofia"])
    div = DIVISOES.get(min(dias_semana, 6), DIVISOES[3])

    inicio = data_inicio or date.today()
    num_mesos = semanas_total // 4
    fases = cfg_obj["fases"]

    # Monta sessões prescritas
    sessoes_prescritas = []
    for i, sessao_cfg in enumerate(div["sessoes"]):
        dia = div["dias_treino"][i] if i < len(div["dias_treino"]) else i
        sessao = _montar_sessao(sessao_cfg, nivel_norm, dia)
        sessoes_prescritas.append(sessao)

    # Monta mesociclos
    mesociclos = []
    total_deload = 0

    for i in range(num_mesos):
        fase = fases[i] if i < len(fases) else f"Fase {i+1}"
        data_meso_inicio = inicio + timedelta(weeks=i * 4)
        data_meso_fim = data_meso_inicio + timedelta(weeks=4) - timedelta(days=1)
        ultimo_meso = (i == num_mesos - 1)

        microciclos = []
        for semana in range(1, 5):
            deload = (semana == 4)
            choque = (semana == 3)
            if deload:
                total_deload += 1

            intensidade_base = cfg_nivel["intensidade_base"]
            progressao = cfg_obj["progressao"] / 100

            if deload:
                # Deload: -40% intensidade, volume reduzido
                intensidade = round(intensidade_base * cfg_obj["deload_reducao"] * 100, 1)
                series = cfg_nivel["series_base"]
                repeticoes = _reps_deload(objetivo)
            elif choque:
                # Choque: +15% intensidade, menos reps, mais carga
                intensidade = round(intensidade_base * (1 + progressao * semana) * 1.15 * 100, 1)
                series = cfg_nivel["series_max"]
                repeticoes = _reps_choque(objetivo)
            else:
                # Normal: progressão padrão
                intensidade = round(
                    intensidade_base * (1 + progressao * semana) * 100, 1
                )
                series = cfg_nivel["series_max"]
                repeticoes = cfg_obj["reps"]

            if deload:
                desc_micro = "🔄 Semana de Deload — Volume e carga reduzidos (-40%). Recuperacao ativa para maximizar adaptacao. Rhea et al. (2002)"
            elif choque:
                desc_micro = "⚡ Semana de Choque — Alta intensidade, menos repeticoes, mais carga. Estimulo maximo de forca e hipertrofia miofribilar. Schoenfeld (2010)"
            else:
                desc_micro = _descricao_microciclo(objetivo, semana, intensidade, nivel_norm)

            microciclos.append(Microciclo(
                semana=semana,
                deload=deload,
                intensidade_percentual=intensidade,
                series=series,
                repeticoes=repeticoes,
                sessoes=[s["nome"] for s in div["sessoes"]],
                descricao=desc_micro,
            ))

        mesociclos.append(Mesociclo(
            numero=i + 1,
            fase=fase,
            semanas=4,
            data_inicio=data_meso_inicio,
            data_fim=data_meso_fim,
            microciclos=microciclos,
            descricao_fase=_descricao_fase(objetivo, fase, i),
            alerta_reavaliacao=ultimo_meso,
        ))

    data_fim = inicio + timedelta(weeks=semanas_total)

    return Periodizacao(
        objetivo=objetivo,
        nivel=nivel_norm,
        nivel_label=cfg_nivel["label"],
        dias_semana=dias_semana,
        semanas_total=semanas_total,
        divisao_nome=div["nome"],
        divisao_sessoes=[s["nome"] for s in div["sessoes"]],
        divisao_descricao=div["descricao"],
        objetivo_descricao=cfg_obj["descricao"],
        tecnicas_disponiveis=cfg_nivel["tecnicas"],
        data_inicio=inicio,
        data_fim=data_fim,
        mesociclos=mesociclos,
        sessoes_prescritas=sessoes_prescritas,
        total_semanas_treino=semanas_total - total_deload,
        total_semanas_deload=total_deload,
        recomendacao_reavaliacao=(
            f"Realizar nova avaliacao fisica ao final do mesociclo {num_mesos} "
            f"({data_fim.strftime('%d/%m/%Y')})"
        ),
    )


def _montar_sessao(sessao_cfg: dict, nivel: str, dia_semana: int) -> SessaoPrescrita:
    """Monta sessão com exercícios prescritos para o nível."""
    exercicios = []
    ordem = 1

    for grupo in sessao_cfg["grupos"]:
        exs = get_exercicios_grupo(grupo, nivel)
        for ex in exs:
            exercicios.append(ExercicioPrescrito(
                nome=ex["nome"],
                grupo=grupo,
                series=ex["series"],
                repeticoes=ex["repeticoes"],
                descanso_segundos=ex["descanso"],
                tecnica_especial=ex.get("tecnica"),
                ordem=ordem,
            ))
            ordem += 1

    # Corretivo no final
    corretivos = EXERCICIOS["corretivos"]["todos"]
    corretivo = corretivos[dia_semana % len(corretivos)]
    exercicios.append(ExercicioPrescrito(
        nome=corretivo["nome"],
        grupo="corretivo",
        series=corretivo["series"],
        repeticoes=corretivo["repeticoes"],
        descanso_segundos=corretivo["descanso"],
        tecnica_especial="CORRETIVO",
        ordem=ordem,
    ))

    return SessaoPrescrita(
        nome=sessao_cfg["nome"],
        grupos=sessao_cfg["grupos"],
        exercicios=exercicios,
        dia_semana=dia_semana,
    )


def _descricao_microciclo(objetivo: str, semana: int, intensidade: float, nivel: str) -> str:
    base = {
        1: "Semana de introducao ao novo estimulo. Foco na execucao tecnica.",
        2: "Aumento progressivo do volume. Descansos controlados.",
        3: "Semana de maior intensidade do mesociclo. Superar marcas anteriores.",
    }
    desc = base.get(semana, f"Semana {semana} — {intensidade}% de intensidade.")
    nivel_cfg = NIVEIS.get(nivel, NIVEIS["iniciante"])
    if nivel_cfg["tecnicas"] and semana == 3:
        tecnicas = ", ".join(nivel_cfg["tecnicas"])
        desc += f" Aplicar tecnicas: {tecnicas}."
    return desc


def _descricao_fase(objetivo: str, fase: str, indice: int) -> str:
    descricoes = {
        "hipertrofia": [
            "Adaptacao Neural: O corpo aprende os movimentos. Foco em tecnica e amplitude.",
            "Volume I: Aumento progressivo do numero de series. Musculo comeca a responder.",
            "Volume II: Pico de volume do macrociclo. Maior estimulo metabolico.",
            "Intensidade: Reducao do volume com aumento da carga. Consolidacao dos ganhos.",
        ],
        "forca": [
            "Adaptacao: Ajuste ao padrao de movimento com cargas submax.",
            "Acumulacao: Alto volume com intensidade moderada para base de forca.",
            "Transmutacao: Transicao para alta intensidade com volume reduzido.",
            "Realizacao: Pico de forca. Semana de teste de 1RM opcional.",
        ],
        "emagrecimento": [
            "Adaptacao: Introducao ao protocolo metabolico.",
            "Queima I: Aumento do gasto calorico com circuitos.",
            "Queima II: Maximo gasto calorico. Alta densidade de treino.",
            "Manutencao: Consolidacao da perda. Prevencao do efeito plato.",
        ],
    }
    fases = descricoes.get(objetivo, [f"Fase {indice+1} do programa."] * 4)
    return fases[indice] if indice < len(fases) else f"Fase {indice+1} — continuidade do programa."


# ── Periodização em Blocos ───────────────────────────────────────────────────

BLOCOS_CONFIG = {
    "hipertrofia": [
        {"fase": "Acumulação",    "semanas": 3, "reps": "10-15", "intensidade": 0.65, "descricao": "Alto volume, baixa intensidade. Base metabólica e hipertrofia sarcoplasmática."},
        {"fase": "Transmutação",  "semanas": 3, "reps": "6-10",  "intensidade": 0.75, "descricao": "Volume moderado, intensidade crescente. Transição para força-hipertrofia."},
        {"fase": "Realização",    "semanas": 2, "reps": "4-6",   "intensidade": 0.85, "descricao": "Baixo volume, alta intensidade. Pico de força e consolidação dos ganhos."},
    ],
    "forca": [
        {"fase": "Acumulação",    "semanas": 3, "reps": "8-12",  "intensidade": 0.65, "descricao": "Base de volume para suportar cargas máximas futuras."},
        {"fase": "Transmutação",  "semanas": 3, "reps": "4-6",   "intensidade": 0.80, "descricao": "Transição para alta intensidade com redução progressiva de volume."},
        {"fase": "Realização",    "semanas": 2, "reps": "1-3",   "intensidade": 0.95, "descricao": "Pico de força máxima. Teste de 1RM opcional."},
    ],
    "condicionamento": [
        {"fase": "Acumulação",    "semanas": 3, "reps": "15-20", "intensidade": 0.55, "descricao": "Base aeróbica e resistência muscular."},
        {"fase": "Transmutação",  "semanas": 3, "reps": "12-15", "intensidade": 0.65, "descricao": "Aumento da densidade e intensidade dos treinos."},
        {"fase": "Realização",    "semanas": 2, "reps": "10-12", "intensidade": 0.75, "descricao": "Pico de performance cardiorrespiratória."},
    ],
    "emagrecimento": [
        {"fase": "Acumulação",    "semanas": 3, "reps": "15-20", "intensidade": 0.55, "descricao": "Alto volume para máximo gasto calórico."},
        {"fase": "Transmutação",  "semanas": 3, "reps": "12-15", "intensidade": 0.65, "descricao": "Manutenção do déficit calórico com aumento de intensidade."},
        {"fase": "Realização",    "semanas": 2, "reps": "10-12", "intensidade": 0.70, "descricao": "Consolidação da perda e prevenção do efeito platô."},
    ],
}

def gerar_periodizacao_blocos(
    objetivo: str,
    nivel: str,
    dias_semana: int,
    semanas_total: int = 8,
    data_inicio = None,
) -> "Periodizacao":
    """
    Periodização em Blocos — Issurin (2010) · Sports Med
    Acumulação → Transmutação → Realização
    Ideal para atletas e praticantes de esportes competitivos.
    """
    nivel_norm = normalizar_nivel(nivel)
    cfg_nivel = NIVEIS.get(nivel_norm, NIVEIS["iniciante"])
    div = DIVISOES.get(min(dias_semana, 6), DIVISOES[3])
    blocos = BLOCOS_CONFIG.get(objetivo, BLOCOS_CONFIG["hipertrofia"])

    inicio = data_inicio or date.today()

    # Monta sessões prescritas
    sessoes_prescritas = []
    for i, sessao_cfg in enumerate(div["sessoes"]):
        dia = div["dias_treino"][i] if i < len(div["dias_treino"]) else i
        sessao = _montar_sessao(sessao_cfg, nivel_norm, dia)
        sessoes_prescritas.append(sessao)

    # Monta mesociclos por bloco
    mesociclos = []
    semana_atual = 0
    total_deload = 0

    for i, bloco in enumerate(blocos):
        data_meso_inicio = inicio + timedelta(weeks=semana_atual)
        data_meso_fim = data_meso_inicio + timedelta(weeks=bloco["semanas"]) - timedelta(days=1)
        ultimo_meso = (i == len(blocos) - 1)

        microciclos = []
        for s in range(1, bloco["semanas"] + 1):
            deload = (s == bloco["semanas"] and i < len(blocos) - 1)
            if deload:
                total_deload += 1
                reps = _reps_deload(objetivo)
                intensidade = round(bloco["intensidade"] * 0.60 * 100, 1)
                desc = "🔄 Deload — Recuperação ativa entre blocos. Rhea et al. (2002)"
            else:
                reps = bloco["reps"]
                intensidade = round(bloco["intensidade"] * (1 + 0.02 * s) * 100, 1)
                desc = f"📦 {bloco['fase']} — Semana {s}. {bloco['descricao']}"

            microciclos.append(Microciclo(
                semana=s,
                deload=deload,
                intensidade_percentual=intensidade,
                series=cfg_nivel["series_max"] if not deload else cfg_nivel["series_base"],
                repeticoes=reps,
                sessoes=[s_cfg["nome"] for s_cfg in div["sessoes"]],
                descricao=desc,
            ))

        mesociclos.append(Mesociclo(
            numero=i + 1,
            fase=bloco["fase"],
            semanas=bloco["semanas"],
            data_inicio=data_meso_inicio,
            data_fim=data_meso_fim,
            microciclos=microciclos,
            descricao_fase=f"📦 {bloco['fase']}: {bloco['descricao']} · Issurin (2010) · Sports Med",
            alerta_reavaliacao=ultimo_meso,
        ))
        semana_atual += bloco["semanas"]

    data_fim = inicio + timedelta(weeks=semana_atual)
    cfg_obj = CONFIGS.get(objetivo, CONFIGS["hipertrofia"])

    return Periodizacao(
        objetivo=objetivo,
        nivel=nivel_norm,
        nivel_label=cfg_nivel["label"],
        dias_semana=dias_semana,
        semanas_total=semana_atual,
        divisao_nome=div["nome"],
        divisao_sessoes=[s["nome"] for s in div["sessoes"]],
        divisao_descricao=div["descricao"],
        objetivo_descricao="Periodização em Blocos — Acumulação → Transmutação → Realização. Issurin (2010) · Sports Med",
        tecnicas_disponiveis=cfg_nivel["tecnicas"],
        data_inicio=inicio,
        data_fim=data_fim,
        mesociclos=mesociclos,
        sessoes_prescritas=sessoes_prescritas,
        total_semanas_treino=semana_atual - total_deload,
        total_semanas_deload=total_deload,
        recomendacao_reavaliacao=f"Realizar nova avaliação ao final do bloco Realização ({data_fim.strftime('%d/%m/%Y')})",
    )

# ── Helpers de reps por fase ─────────────────────────────────────────────────

def _reps_choque(objetivo: str) -> str:
    """Repetições para semana de choque — menos reps, mais carga."""
    mapa = {
        "hipertrofia":    "4-6",
        "forca":          "2-4",
        "emagrecimento":  "8-10",
        "condicionamento": "10-12",
        "reabilitacao":   "10-12",
    }
    return mapa.get(objetivo, "4-6")

def _reps_deload(objetivo: str) -> str:
    """Repetições para semana de deload — mais reps, menos carga."""
    mapa = {
        "hipertrofia":    "15-20",
        "forca":          "12-15",
        "emagrecimento":  "20-25",
        "condicionamento": "20-25",
        "reabilitacao":   "20-25",
    }
    return mapa.get(objetivo, "15-20")

# ── Serialização ──────────────────────────────────────────────────────────────

def periodizacao_to_dict(p: "Periodizacao") -> dict:
    """Converte para dicionário para salvar no banco (JSON)."""
    return {
        "objetivo": p.objetivo,
        "nivel": p.nivel,
        "nivel_label": p.nivel_label,
        "dias_semana": p.dias_semana,
        "semanas_total": p.semanas_total,
        "divisao_nome": p.divisao_nome,
        "divisao_sessoes": p.divisao_sessoes,
        "divisao_descricao": p.divisao_descricao,
        "objetivo_descricao": p.objetivo_descricao,
        "tecnicas_disponiveis": p.tecnicas_disponiveis,
        "data_inicio": str(p.data_inicio) if p.data_inicio else None,
        "data_fim": str(p.data_fim) if p.data_fim else None,
        "total_semanas_treino": p.total_semanas_treino,
        "total_semanas_deload": p.total_semanas_deload,
        "recomendacao_reavaliacao": p.recomendacao_reavaliacao,
        "sessoes_prescritas": [
            {
                "nome": s.nome,
                "grupos": s.grupos,
                "dia_semana": s.dia_semana,
                "exercicios": [
                    {
                        "ordem": e.ordem,
                        "nome": e.nome,
                        "grupo": e.grupo,
                        "series": e.series,
                        "repeticoes": e.repeticoes,
                        "descanso_segundos": e.descanso_segundos,
                        "tecnica_especial": e.tecnica_especial,
                    }
                    for e in s.exercicios
                ],
            }
            for s in p.sessoes_prescritas
        ],
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

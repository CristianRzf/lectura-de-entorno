"""
models.py - Definición de constantes, categorías PESTEL, escalas de impacto y lógica de puntuación
para Smurfit WestRock Colombia.
Alineado con el sistema de diseño clínico/monocromático (Canvas, Paper, Ink, Mid Gray, Hairline, Ember).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

class PESTELCategory(str, Enum):
    POLITICO = "Político"
    ECONOMICO = "Económico"
    SOCIAL = "Social"
    TECNOLOGICO = "Tecnológico"
    ECOLOGICO = "Ecológico"
    LEGAL = "Legal"

class FactorType(str, Enum):
    RIESGO = "Riesgo"
    OPORTUNIDAD = "Oportunidad"

class UrgencyLevel(str, Enum):
    INMEDIATA = "Inmediata (< 3 meses)"
    ALTA = "Alta (3 - 6 meses)"
    MEDIA = "Media (6 - 12 meses)"
    BAJA = "Baja (> 1 año)"

class FactorStatus(str, Enum):
    EN_MONITOREO = "En Monitoreo"
    ACTIVO = "Activo / Crítico"
    EN_MITIGACION = "En Mitigación / Acción"
    MITIGADO = "Mitigado / Capitalizado"
    CERRADO = "Cerrado / Descartado"

# Mapeo de metadatos PESTEL en sistema monocromático con soporte de tokens
PESTEL_META = {
    PESTELCategory.POLITICO.value: {
        "color": "#0a0a0a",
        "code": "POL",
        "desc": "Políticas públicas, subsidios forestales (CIF), aranceles y estabilidad institucional."
    },
    PESTELCategory.ECONOMICO.value: {
        "color": "#171717",
        "code": "ECO",
        "desc": "Auge agroexportador, comercio electrónico, inflación, TRM y costos energéticos."
    },
    PESTELCategory.SOCIAL.value: {
        "color": "#171717",
        "code": "SOC",
        "desc": "Consumo consciente libre de plásticos, diálogo comunitario forestal y talento en Yumbo."
    },
    PESTELCategory.TECNOLOGICO.value: {
        "color": "#0a0a0a",
        "code": "TEC",
        "desc": "Tecnología AquaStop, gemelos digitales, automatización y sensores IoT en molinos."
    },
    PESTELCategory.ECOLOGICO.value: {
        "color": "#0a0a0a",
        "code": "ECL",
        "desc": "Sustitución de plásticos (Ley 2232), estrés hídrico en Río Cauca y biomasa circular."
    },
    PESTELCategory.LEGAL.value: {
        "color": "#171717",
        "code": "LEG",
        "desc": "Metas REP (Res. 1407), normativa de vertimientos CVC e impuestos ambientales."
    }
}

URGENCY_WEIGHTS = {
    UrgencyLevel.INMEDIATA.value: 1.5,
    UrgencyLevel.ALTA.value: 1.25,
    UrgencyLevel.MEDIA.value: 1.0,
    UrgencyLevel.BAJA.value: 0.8
}

def calculate_score(probabilidad: int, impacto: int) -> int:
    """Calcula el índice de severidad básico (1 - 25)."""
    return probabilidad * impacto

def calculate_priority_score(probabilidad: int, impacto: int, urgencia: str) -> float:
    """Calcula la prioridad ponderada por urgencia."""
    base = probabilidad * impacto
    weight = URGENCY_WEIGHTS.get(urgencia, 1.0)
    return round(base * weight, 2)

def get_criticidad_label(score: int, factor_type: str) -> Tuple[str, str]:
    """
    Retorna la etiqueta y color del sistema monocromático con acento destructivo #e7000b (Ember):
    Para Riesgos: Extremo (>= 17, #e7000b), Alto (12-16, #171717), Medio (6-11, #737373), Bajo (< 6, #a3a3a3)
    Para Oportunidades: Estratégica (>= 17, #0a0a0a), Clave (12-16, #171717), Moderada (6-11, #737373), Marginal (< 6, #a3a3a3)
    """
    if factor_type == FactorType.RIESGO.value:
        if score >= 17:
            return "Extremo", "#e7000b"
        elif score >= 12:
            return "Alto", "#171717"
        elif score >= 6:
            return "Medio", "#737373"
        else:
            return "Bajo", "#a3a3a3"
    else:
        if score >= 17:
            return "Estratégica", "#0a0a0a"
        elif score >= 12:
            return "Clave", "#171717"
        elif score >= 6:
            return "Moderada", "#737373"
        else:
            return "Marginal", "#a3a3a3"

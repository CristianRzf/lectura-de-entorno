#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reemplazar todas las referencias a la empresa por textos genéricos.
Usa Python puro para evitar problemas de encoding de PowerShell.
"""
import os
import re

BASE = r"c:\lectura-de-entorno"

FILES = [
    "app.py",
    "auth.py",
    "database.py",
    "models.py",
    "views/home.py",
    "views/login.py",
    "views/monitor.py",
    "views/reports.py",
    "views/recommendations.py",
    "views/risk_opportunity.py",
    "views/tracking.py",
    "views/pestel_analysis.py",
    "utils/report_generator.py",
    "utils/visualizer.py",
    "utils/external_sources.py",
]

# Ordered from most specific to least specific to avoid partial replacements
REPLACEMENTS = [
    # Report headers
    ("SMURFIT WESTROCK COLOMBIA - LECTURA DEL ENTORNO PESTEL", "LECTURA DEL ENTORNO PESTEL"),
    ("SMURFIT WESTROCK COLOMBIA",                              "LECTURA DEL ENTORNO PESTEL"),
    ("SMURFIT WESTROCK",                                       "LECTURA DEL ENTORNO PESTEL"),
    # Compound names
    ("Smurfit WestRock Colombia S.A.S.",                       "Lectura del Entorno PESTEL"),
    ("Smurfit WestRock Colombia",                              "la organización"),
    ("Smurfit WestRock Yumbo",                                 "la organización"),
    ("Smurfit WestRock (Planta Yumbo / Forest",                "la organización"),
    ("Smurfit WestRock",                                       "la organización"),
    # Emails / URLs
    ("smurfitwestrock.com",                                    "organizacion.com"),
    ("ejemplo@smurfitwestrock.com",                            "usuario@organizacion.com"),
    # Location combos
    ("Complejo Industrial Yumbo, Valle del Cauca",             "Sistema de Análisis PESTEL"),
    ("Complejo Industrial Yumbo",                              "Sistema de Análisis PESTEL"),
    ("Complejo Yumbo (Valle del Cauca)",                       "Sede principal"),
    ("complejo papelero y de empaques en Yumbo y sus núcleos forestales", "la organización y su entorno sectorial"),
    ("complejo Yumbo",                                         "sede principal"),
    ("Valle del Cauca/Yumbo",                                  "regional"),
    ("Valle del Cauca · Fecha",                                "Sistema PESTEL · Fecha"),
    ("Valle del Cauca",                                        "regional"),
    ("Planta Yumbo · Valle del Cauca",                         "Análisis Estratégico"),
    ("Planta Yumbo",                                           "la organización"),
    ("planta Yumbo",                                           "la organización"),
    ("planta de Yumbo",                                        "la organización"),
    ("en Yumbo.",                                              "en la organización."),
    ("en Yumbo,",                                              "en la organización,"),
    ("en Yumbo ",                                              "en la organización "),
    ("de Yumbo.",                                              "de la organización."),
    ("de Yumbo ",                                              "de la organización "),
    ("de Yumbo,",                                              "de la organización,"),
    ("Yumbo, Valle",                                           "sede principal"),
    ("Carrera 1 # 15-05, Yumbo",                               ""),
    # Standalone Yumbo (keep after combos)
    (" Yumbo.",                                                " la organización."),
    (" Yumbo,",                                                " la organización,"),
    (" Yumbo ",                                                " la organización "),
    (" Yumbo\n",                                               " la organización\n"),
    (" Yumbo\r",                                               " la organización\r"),
    ("(Yumbo)",                                                "(la organización)"),
    # Table headers / labels
    ("Efecto en Smurfit WestRock Yumbo",                       "Efecto en la Organización"),
    ("Efecto en Smurfit WestRock (1 a 5)",                     "Efecto en la Organización (1 a 5)"),
    ("Título & Efecto en Yumbo",                               "Título & Efecto en la Organización"),
    ("Efecto Potencial Concreto en Smurfit WestRock",          "Efecto Potencial en la Organización"),
    ("Impacto en Smurfit WestRock Yumbo:",                     "Impacto en la Organización:"),
    ("Impacto en Planta Yumbo:",                               "Impacto en la Organización:"),
    ("Efecto Yumbo:",                                          "Efecto:"),
    # Report footer
    ("Documento estratégico confidencial — Sistema de Inteligencia PESTEL — Smurfit WestRock Colombia (Yumbo)",
     "Documento estratégico — Sistema de Inteligencia PESTEL — Lectura del Entorno"),
    # Report description
    ("Informe oficial con membrete corporativo de Smurfit WestRock Colombia.",
     "Informe del sistema Lectura del Entorno PESTEL."),
    # File names for download
    ("Informe_PESTEL_Smurfit_WestRock_",                       "Informe_PESTEL_"),
    ("Matriz_PESTEL_Smurfit_WestRock_",                        "Matriz_PESTEL_"),
    # Role descriptions
    ("para Smurfit WestRock Yumbo.",                           "de la organización."),
    ("Director General de Operaciones & Estrategia Yumbo",     "Director General de Estrategia"),
    ("Operaciones Forestales Yumbo",                           "Operaciones"),
    ("Cadena de Suministro & Operaciones Forestales Yumbo",    "Cadena de Suministro & Operaciones"),
    ("Comercial & Innovación de Empaques Yumbo",               "Comercial & Innovación de Productos"),
    ("Mercadeo & División de Sacos y Empaques Yumbo",          "Mercadeo & División de Productos"),
    ("Gestión Ambiental Yumbo & División Forestal",            "Gestión Ambiental & Sostenibilidad"),
    ("Ingeniería de Planta & Sostenibilidad Yumbo",            "Ingeniería de Planta & Sostenibilidad"),
    ("Gestion Ambiental Yumbo",                                "Gestión Ambiental"),
    ("Operaciones & Molinos Yumbo",                            "Operaciones & Gestión"),
    # Description texts
    ("trazabilidad de las decisiones gerenciales en Smurfit WestRock Colombia",
     "trazabilidad de las decisiones gerenciales de la organización"),
    ("macroentorno de <b>Smurfit WestRock Colombia</b>",       "macroentorno analizado"),
    ("sobre los molinos de papel, corrugadoras y operaciones forestales",
     "del entorno estratégico organizacional"),
    ("estrategia de empaques circulares",                      "estrategia organizacional"),
    ("Horizonte temporal de afectación sobre las operaciones de Yumbo.",
     "Horizonte temporal de afectación de cada factor del entorno."),
    ("para las operaciones de Yumbo.",                         "para la organización."),
    # Badges in home header
    ("Smurfit WestRock Colombia",                              "Lectura del Entorno PESTEL"),
    # Expander
    ("Información Corporativa · Smurfit WestRock Colombia (Yumbo)",
     "Acerca del Sistema — Lectura del Entorno PESTEL"),
    # Docstrings / comments
    ("para Smurfit WestRock Colombia",                         "— Lectura del Entorno PESTEL"),
    ("Inicio Ejecutivo para Smurfit WestRock Colombia",        "Tablero de Inicio Ejecutivo"),
    ("modelo de roles de usuario para Smurfit WestRock Colombia",
     "modelo de roles de usuario — Lectura del Entorno PESTEL"),
    # PESTEL meta descriptions (sector-specific)
    ("Políticas públicas, subsidios forestales (CIF), aranceles y estabilidad institucional.",
     "Políticas públicas, marcos regulatorios sectoriales, aranceles y estabilidad institucional."),
    ("Auge agroexportador, comercio electrónico, inflación, TRM y costos energéticos.",
     "Tendencias macroeconómicas, comercio exterior, inflación, tasas de cambio y costos operativos."),
    ("Consumo consciente libre de plásticos, diálogo comunitario forestal y talento en Yumbo.",
     "Cambios demográficos, tendencias de consumo, capital humano y dinámicas comunitarias."),
    ("Tecnología AquaStop, gemelos digitales, automatización y sensores IoT en molinos.",
     "Innovación tecnológica, automatización, transformación digital y ciberseguridad."),
    ("Sustitución de plásticos (Ley 2232), estrés hídrico en Río Cauca y biomasa circular.",
     "Cambio climático, recursos naturales, regulaciones ambientales y economía circular."),
    ("Metas REP (Res. 1407), normativa de vertimientos CVC e impuestos ambientales.",
     "Normativas sectoriales, cumplimiento regulatorio, estándares internacionales y litigios."),
    # Remaining lone references
    ("Smurfit WestRock",                                       "la organización"),
]

def fix_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='latin-1') as f:
            content = f.read()

    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    # Fix home.py expander body with regex
    if 'home.py' in path:
        content = re.sub(
            r'\*\*Smurfit WestRock Colombia S\.A\.S\.\*\*.*?oficio\.',
            '**Lectura del Entorno PESTEL** es un sistema de vigilancia estratégica del macroentorno basado en la metodología PESTEL.\n'
            '        - **Objetivo:** Identificar, evaluar y priorizar los factores externos que afectan la operación de la organización.\n'
            '        - **Dimensiones:** Político, Económico, Social, Tecnológico, Ecológico y Legal.\n'
            '        - **Valor:** Apoya la toma de decisiones informada mediante evidencia trazable, matrices de riesgo y recomendaciones estratégicas.',
            content, flags=re.DOTALL
        )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {path}")
    else:
        print(f"No change: {path}")

for rel_path in FILES:
    full_path = os.path.join(BASE, rel_path)
    if os.path.exists(full_path):
        fix_file(full_path)
    else:
        print(f"NOT FOUND: {full_path}")

print("\nDone!")

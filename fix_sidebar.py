#!/usr/bin/env python3
# -*- coding: utf-8 -*-

content = open('app.py', encoding='utf-8').read()

replacements = [
    # Fix sidebar logo badge (SW -> LP for "Lectura PESTEL")
    ('<span class="badge-pill-solid">SW</span>', '<span class="badge-pill-solid">LP</span>'),
    # Fix sidebar subtitle
    ('Planta Industrial la organización · PESTEL', 'Sistema de Vigilancia Estratégica · PESTEL'),
    ('Planta Industrial la organizaci\u00f3n \u00b7 PESTEL', 'Sistema de Vigilancia Estrat\u00e9gica \u00b7 PESTEL'),
    # Remove leftover address
    ('Carrera 1 # 15-05, sede principal', ''),
    ('Carrera 1 # 15-05, la organizaci\u00f3n', ''),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'Replaced: {old[:50]!r}')
    else:
        print(f'NOT FOUND: {old[:50]!r}')

open('app.py', 'w', encoding='utf-8').write(content)
print('Done - app.py saved')

# Verify
if 'Force white text on all inner elements' in content:
    print('Button CSS: OK')
if 'Sistema de Vigilancia' in content:
    print('Sidebar subtitle: OK')

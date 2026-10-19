"""
views/pestel_analysis.py - Análisis PESTEL (RF-02 y RF-06).
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
import textwrap
import database
from models import PESTELCategory, PESTEL_META, get_criticidad_label
from utils.visualizer import create_pestel_bar_chart

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid">RF-02 & RF-06</span>
                    <span class="badge-pill-soft">Análisis Multidimensional</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Análisis y Clasificación PESTEL
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Evaluación estructurada en las seis dimensiones macroambientales que inciden sobre Smurfit WestRock Yumbo.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">6 Pilares</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_all = database.get_all_factors()

    # Barra superior de filtros
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])
    with f_col1:
        filtro_tipo = st.selectbox("Naturaleza", ["Todos", "Riesgo", "Oportunidad"], key="pestel_tipo")
    with f_col2:
        filtro_urgencia = st.selectbox("Urgencia Temporal", ["Todas", "Inmediata (< 3 meses)", "Alta (3 - 6 meses)", "Media (6 - 12 meses)", "Baja (> 1 año)"], key="pestel_urg")
    with f_col3:
        filtro_texto = st.text_input("Filtrar por texto o código", placeholder="Ej. Yumbo, Celulosa, Ley 2232...", key="pestel_txt")

    df_filtrado = df_all.copy()
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == filtro_tipo]
    if filtro_urgencia != "Todas":
        df_filtrado = df_filtrado[df_filtrado["urgencia"] == filtro_urgencia]
    if filtro_texto.strip():
        term = filtro_texto.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado["titulo"].str.lower().str.contains(term) |
            df_filtrado["descripcion"].str.lower().str.contains(term) |
            df_filtrado["codigo"].str.lower().str.contains(term) |
            df_filtrado["efecto_empresa"].str.lower().str.contains(term)
        ]

    # Tabs por dimensión
    categorias = [c.value for c in PESTELCategory]
    tabs = st.tabs([
        f"{cat} ({len(df_filtrado[df_filtrado['categoria_pestel'] == cat])})" for cat in categorias
    ])

    for idx, cat_name in enumerate(categorias):
        with tabs[idx]:
            meta = PESTEL_META.get(cat_name, {})
            cat_df = df_filtrado[df_filtrado["categoria_pestel"] == cat_name]

            # Header strip de la dimensión
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 18px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge-pill-solid">{meta.get('code', 'DIM')}</span>
                    <span style="font-size: 15px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.3px;">
                        Dimensión {cat_name}
                    </span>
                </div>
                <div style="font-size: 13px; color: #737373; margin-top: 4px;">
                    {meta.get('desc', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Mini métricas en Stat Blocks
            riesgos_cat = cat_df[cat_df["tipo"] == "Riesgo"]
            oportunidades_cat = cat_df[cat_df["tipo"] == "Oportunidad"]
            sev_max = cat_df["puntuacion_severidad"].max() if not cat_df.empty else 0

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Factores", len(cat_df))
            with m2:
                st.metric("Riesgos", len(riesgos_cat))
            with m3:
                st.metric("Oportunidades", len(oportunidades_cat))
            with m4:
                st.metric("Severidad Máx.", f"{sev_max}/25")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            if not cat_df.empty:
                for _, row in cat_df.sort_values(by="puntuacion_severidad", ascending=False).iterrows():
                    is_risk = row["tipo"] == "Riesgo"
                    is_extreme = row["puntuacion_severidad"] >= 17
                    badge_lbl, _ = get_criticidad_label(row["puntuacion_severidad"], row["tipo"])
                    level_class = "badge-pill-destructive" if (is_risk and is_extreme) else ("badge-pill-solid" if is_risk else "badge-pill-soft")

                    card_html = textwrap.dedent(f"""<div class="blueprint-card" style="margin-bottom: 14px;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">
<div style="display: flex; align-items: center; gap: 6px;">
<span class="{level_class}">{row['tipo'].upper()}</span>
<span class="badge-pill-outline">{row['codigo']}</span>
<span style="font-size: 12px; color: #737373;">{row['ambito']}</span>
</div>
<div style="display: flex; align-items: center; gap: 6px;">
<span class="badge-pill-soft">Nivel: {badge_lbl} ({row['puntuacion_severidad']}/25)</span>
<span class="badge-pill-outline">{row['urgencia']}</span>
</div>
</div>
<h3 style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 0 0 8px 0; letter-spacing: -0.4px;">{row['titulo']}</h3>
<p style="font-size: 13.5px; color: #737373; margin: 0 0 12px 0; line-height: 1.45;">{row['descripcion']}</p>
<div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 12px 14px; margin-bottom: 12px;">
<div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; color: #0a0a0a; margin-bottom: 3px;">Impacto Operativo en Planta Yumbo / Smurfit WestRock:</div>
<div style="font-size: 13px; color: #171717; line-height: 1.4;">{row['efecto_empresa']}</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; font-size: 12px; color: #737373; border-top: 1px solid #e5e5e5; padding-top: 10px;">
<div>Prob: <b style="color: #0a0a0a;">{row['probabilidad']}/5</b> &nbsp;|&nbsp; Imp: <b style="color: #0a0a0a;">{row['impacto']}/5</b> &nbsp;|&nbsp; Ponderada: <b style="color: #0a0a0a;">{row['prioridad_ponderada']}</b></div>
<div>Fuente: <a href="{row['fuente_url']}" target="_blank" style="color: #0a0a0a; font-weight: 500; text-decoration: underline;">{row['fuente_nombre']}</a> ({row['fecha_publicacion']})</div>
</div>
</div>""")
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info(f"No hay registros en la dimensión {cat_name} con los filtros aplicados.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="blueprint-card">
        <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px;">
            Balance Consolidado del Entorno
        </h3>
    """, unsafe_allow_html=True)
    bar_chart = create_pestel_bar_chart(df_all)
    st.plotly_chart(bar_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

"""
views/risk_opportunity.py - Matriz de Riesgos y Oportunidades (RF-04 y RF-05).
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
import database
from models import get_criticidad_label, calculate_score, calculate_priority_score
from utils.visualizer import create_matrix_5x5

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid">RF-04 & RF-05</span>
                    <span class="badge-pill-soft">Priorización Estratégica</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Matriz de Riesgos y Oportunidades
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Evaluación cuantitativa y cualitativa de Probabilidad (1-5) e Impacto (1-5) para Smurfit WestRock Yumbo.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">Matriz 5x5</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_all = database.get_all_factors()

    # Controles de filtrado
    c_tipo, c_prio, c_cat = st.columns([1.5, 1.5, 2])
    with c_tipo:
        filtro_tipo = st.selectbox("Vista", ["Todos", "Riesgo", "Oportunidad"], key="matriz_tipo")
    with c_prio:
        filtro_severidad = st.selectbox("Severidad", ["Todos los niveles", "Severidad Alta/Extrema (>= 15)", "Severidad Media (8-14)", "Severidad Baja (<= 6)"], key="matriz_sev")
    with c_cat:
        filtro_cat = st.selectbox("Dimensión", ["Todas"] + sorted(df_all["categoria_pestel"].unique().tolist()), key="matriz_cat")

    df_plot = df_all.copy()
    if filtro_tipo != "Todos":
        df_plot = df_plot[df_plot["tipo"] == filtro_tipo]
    if filtro_cat != "Todas":
        df_plot = df_plot[df_plot["categoria_pestel"] == filtro_cat]

    if filtro_severidad == "Severidad Alta/Extrema (>= 15)":
        df_plot = df_plot[df_plot["puntuacion_severidad"] >= 15]
    elif filtro_severidad == "Severidad Media (8-14)":
        df_plot = df_plot[(df_plot["puntuacion_severidad"] >= 8) & (df_plot["puntuacion_severidad"] <= 14)]
    elif filtro_severidad == "Severidad Baja (<= 6)":
        df_plot = df_plot[df_plot["puntuacion_severidad"] <= 6]

    # Matriz 5x5 en tarjeta blanca
    st.markdown("""
    <div class="blueprint-card">
    """, unsafe_allow_html=True)
    fig_matrix = create_matrix_5x5(df_plot, factor_type=filtro_tipo)
    st.plotly_chart(fig_matrix, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Guía Metodológica en Expander Limpio
    with st.expander("Metodología de Cuadrantes 5x5"):
        st.markdown("""
        | Zona de Matriz | P x I | Naturaleza | Tratamiento Estratégico en Yumbo |
        |---|---|---|---|
        | **Zona Superior Derecha** | 17 - 25 | **Extremo / Estratégico** | Intervención prioritaria de gerencia; asignación de CAPEX y mitigación inmediata. |
        | **Zona Media Alta** | 12 - 16 | **Alto / Clave** | Plan de acción formal con responsable y fechas límite establecidas. |
        | **Zona Central** | 6 - 11 | **Medio / Moderado** | Monitoreo trimestral y absorción operativa estándar. |
        | **Zona Inferior Izquierda** | 1 - 5 | **Bajo / Marginal** | Registro pasivo en bitácora sin consumo de recursos extraordinarios. |
        """)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Tabs de priorización
    tab_riesgos, tab_oportunidades, tab_simulador = st.tabs([
        f"Priorización de Riesgos ({len(df_all[df_all['tipo'] == 'Riesgo'])})",
        f"Oportunidades Clave ({len(df_all[df_all['tipo'] == 'Oportunidad'])})",
        "Simulador de Sensibilidad"
    ])

    # TAB 1: RIESGOS
    with tab_riesgos:
        df_riesgos = df_all[df_all["tipo"] == "Riesgo"].sort_values(by="puntuacion_severidad", ascending=False)
        for _, row in df_riesgos.iterrows():
            is_extreme = row["puntuacion_severidad"] >= 17
            badge_lbl, _ = get_criticidad_label(row["puntuacion_severidad"], "Riesgo")
            pill_class = "badge-pill-destructive" if is_extreme else "badge-pill-solid"

            st.markdown(f"""
            <div class="blueprint-card" style="margin-bottom: 12px; padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-weight: 600; color: #0a0a0a; font-size: 15px;">[{row['codigo']}] {row['titulo']}</span>
                        <span class="badge-pill-soft">{row['categoria_pestel']}</span>
                        <span class="badge-pill-outline">{row['ambito']}</span>
                    </div>
                    <div>
                        <span class="{pill_class}">Nivel {badge_lbl} ({row['puntuacion_severidad']}/25)</span>
                    </div>
                </div>
                <div style="margin: 8px 0; font-size: 13.5px; color: #171717; line-height: 1.4;">
                    <b style="color: #0a0a0a;">Impacto en Planta Yumbo:</b> {row['efecto_empresa']}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #737373; border-top: 1px solid #e5e5e5; padding-top: 8px; margin-top: 8px;">
                    <span>Urgencia: <b style="color: #0a0a0a;">{row['urgencia']}</b> · Ponderada: <b style="color: #0a0a0a;">{row['prioridad_ponderada']}</b></span>
                    <span>Fuente: <a href="{row['fuente_url']}" target="_blank" style="color: #0a0a0a; text-decoration: underline;">{row['fuente_nombre']}</a></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: OPORTUNIDADES
    with tab_oportunidades:
        df_oportunidades = df_all[df_all["tipo"] == "Oportunidad"].sort_values(by="puntuacion_severidad", ascending=False)
        for _, row in df_oportunidades.iterrows():
            badge_lbl, _ = get_criticidad_label(row["puntuacion_severidad"], "Oportunidad")
            st.markdown(f"""
            <div class="blueprint-card" style="margin-bottom: 12px; padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-weight: 600; color: #0a0a0a; font-size: 15px;">[{row['codigo']}] {row['titulo']}</span>
                        <span class="badge-pill-soft">{row['categoria_pestel']}</span>
                        <span class="badge-pill-outline">{row['ambito']}</span>
                    </div>
                    <div>
                        <span class="badge-pill-solid">Nivel {badge_lbl} ({row['puntuacion_severidad']}/25)</span>
                    </div>
                </div>
                <div style="margin: 8px 0; font-size: 13.5px; color: #171717; line-height: 1.4;">
                    <b style="color: #0a0a0a;">Palanca de Crecimiento:</b> {row['efecto_empresa']}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #737373; border-top: 1px solid #e5e5e5; padding-top: 8px; margin-top: 8px;">
                    <span>Urgencia: <b style="color: #0a0a0a;">{row['urgencia']}</b> · Ponderada: <b style="color: #0a0a0a;">{row['prioridad_ponderada']}</b></span>
                    <span>Fuente: <a href="{row['fuente_url']}" target="_blank" style="color: #0a0a0a; text-decoration: underline;">{row['fuente_nombre']}</a></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: SIMULADOR
    with tab_simulador:
        st.markdown("### Simulador de Sensibilidad del Entorno")
        st.caption("Modifique parámetros hipotéticos para observar cómo varía la severidad calculada.")

        factor_nombres = {f"[{r['codigo']}] {r['titulo']}": r['id'] for _, r in df_all.iterrows()}
        selected_nombre = st.selectbox("Factor a simular:", list(factor_nombres.keys()))
        selected_id = factor_nombres[selected_nombre]
        factor_actual = database.get_factor_by_id(selected_id)

        if factor_actual:
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                st.markdown(f"""
                <div class="blueprint-card">
                    <span class="badge-pill-soft" style="margin-bottom: 8px;">Valores Actuales</span>
                    <div style="font-size: 13px; color: #737373; line-height: 1.6; margin-top: 6px;">
                        • Tipo: <b style="color: #0a0a0a;">{factor_actual['tipo']} ({factor_actual['categoria_pestel']})</b><br>
                        • Probabilidad: <b style="color: #0a0a0a;">{factor_actual['probabilidad']}/5</b><br>
                        • Impacto: <b style="color: #0a0a0a;">{factor_actual['impacto']}/5</b><br>
                        • Severidad Actual: <b style="color: #0a0a0a;">{factor_actual['puntuacion_severidad']}/25</b><br>
                        • Urgencia: <b style="color: #0a0a0a;">{factor_actual['urgencia']}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with sim_col2:
                sim_prob = st.slider("Simular Probabilidad", 1, 5, int(factor_actual['probabilidad']), key="sim_p")
                sim_imp = st.slider("Simular Impacto", 1, 5, int(factor_actual['impacto']), key="sim_i")
                sim_urg = st.selectbox("Simular Urgencia", [
                    "Inmediata (< 3 meses)", "Alta (3 - 6 meses)", "Media (6 - 12 meses)", "Baja (> 1 año)"
                ], index=0, key="sim_u")

                new_score = calculate_score(sim_prob, sim_imp)
                new_prio = calculate_priority_score(sim_prob, sim_imp, sim_urg)
                lbl_sim, _ = get_criticidad_label(new_score, factor_actual['tipo'])
                is_ext = (factor_actual['tipo'] == 'Riesgo' and new_score >= 17)

                st.markdown(f"""
                <div class="blueprint-card" style="text-align: center; border-color: {'#e7000b' if is_ext else '#0a0a0a'};">
                    <span class="{'badge-pill-destructive' if is_ext else 'badge-pill-solid'}">Escenario Simulado</span>
                    <div style="font-size: 26px; font-weight: 600; color: {'#e7000b' if is_ext else '#0a0a0a'}; margin: 8px 0; letter-spacing: -0.5px;">
                        Severidad: {new_score}/25 — {lbl_sim}
                    </div>
                    <div style="font-size: 13px; color: #737373;">
                        Prioridad Ponderada: <b style="color: #0a0a0a;">{new_prio}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

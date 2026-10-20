"""
views/home.py - Inicio Ejecutivo para Smurfit WestRock Colombia.
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
import database
import models
from utils.visualizer import create_radar_chart, create_urgency_donut, create_pestel_bar_chart
from models import PESTEL_META, get_criticidad_label

def render():
    # Encabezado principal en Card Surface (#ffffff) con radio de 24px y borde hairline #e5e5e5
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span class="badge-pill-solid">PESTEL</span>
                    <span class="badge-pill-soft">Smurfit WestRock Colombia</span>
                    <span class="badge-pill-outline">Planta Yumbo · Valle del Cauca</span>
                    <span class="badge-pill-soft">Roles Activos</span>
                </div>
                <h1 style="margin: 4px 0 6px 0; font-size: 32px; font-weight: 600; letter-spacing: -0.9px; color: #0a0a0a;">
                    Lectura del Entorno Estratégico
                </h1>
                <p style="margin: 0; font-size: 14px; color: #737373; line-height: 1.43;">
                    Vigilancia macro y microsectorial sobre los molinos de papel, corrugadoras y operaciones forestales.
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #737373; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 500;">
                    Ciclo de Análisis
                </div>
                <div style="font-size: 14px; font-weight: 600; color: #0a0a0a;">
                    2024 — 2025
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Indicadores ejecutivos en Stat Blocks
    kpis = database.get_kpis_summary()
    df_factores = database.get_all_factors()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label="Total Factores",
            value=kpis["total_factores"],
            delta=f"{kpis['promedio_impacto']}/5 impacto prom.",
            delta_color="off"
        )
    with col2:
        st.metric(
            label="Riesgos Detectados",
            value=kpis["total_riesgos"],
            delta=f"{kpis['riesgos_criticos']} Críticos",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            label="Oportunidades",
            value=kpis["total_oportunidades"],
            delta=f"{kpis['oportunidades_estrategicas']} Clave",
            delta_color="normal"
        )
    with col4:
        st.metric(
            label="Decisiones Activas",
            value=kpis["total_recomendaciones"],
            delta=f"{kpis['recomendaciones_activas']} En marcha",
            delta_color="normal"
        )
    with col5:
        sev_max = df_factores["puntuacion_severidad"].max() if not df_factores.empty else 0
        st.metric(
            label="Severidad Máx.",
            value=f"{sev_max}/25",
            delta="Nivel Extremo" if sev_max >= 20 else "Nivel Alto",
            delta_color="inverse" if sev_max >= 20 else "normal"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Gráficos en tarjetas flotantes con radio de 24px
    g_col1, g_col2 = st.columns([3, 2])

    with g_col1:
        st.markdown("""
        <div class="blueprint-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px;">
                    Radar de Presión Estratégica PESTEL
                </h3>
                <span class="badge-pill-soft">6 Dimensiones</span>
            </div>
            <p style="margin: 0 0 12px 0; font-size: 13px; color: #737373;">
                Intensidad promedio del impacto y severidad relativa por pilar metodológico.
            </p>
        """, unsafe_allow_html=True)
        radar_fig = create_radar_chart(df_factores)
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with g_col2:
        st.markdown("""
        <div class="blueprint-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px;">
                    Horizonte de Urgencia
                </h3>
                <span class="badge-pill-soft">Plazos</span>
            </div>
            <p style="margin: 0 0 12px 0; font-size: 13px; color: #737373;">
                Horizonte temporal de afectación sobre las operaciones de Yumbo.
            </p>
        """, unsafe_allow_html=True)
        donut_fig = create_urgency_donut(df_factores)
        st.plotly_chart(donut_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Factores Críticos de Atención Inmediata
    st.markdown("""
    <div style="margin: 28px 0 14px 0; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.6px; color: #0a0a0a;">
                Factores de Atención Prioritaria
            </h2>
            <p style="margin: 2px 0 0 0; font-size: 13px; color: #737373;">
                Eventos del entorno con severidad crítica (≥ 16) o clasificados con urgencia inmediata (&lt; 3 meses).
            </p>
        </div>
        <span class="badge-pill-outline">RF-04 & RF-05</span>
    </div>
    """, unsafe_allow_html=True)

    criticos_df = df_factores[
        (df_factores["puntuacion_severidad"] >= 16) | (df_factores["urgencia"].str.contains("Inmediata"))
    ].sort_values(by="puntuacion_severidad", ascending=False).head(4)

    if not criticos_df.empty:
        alert_cols = st.columns(len(criticos_df))
        for idx, (_, row) in enumerate(criticos_df.iterrows()):
            with alert_cols[idx]:
                is_risk = row["tipo"] == "Riesgo"
                is_extreme = row["puntuacion_severidad"] >= 17
                badge_class = "badge-pill-destructive" if (is_risk and is_extreme) else ("badge-pill-solid" if is_risk else "badge-pill-soft")

                st.markdown(f"""
                <div class="blueprint-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="{badge_class}">
                                {row['tipo'].upper()}
                            </span>
                            <span style="font-size: 12px; color: #737373; font-weight: 500;">
                                {row['categoria_pestel']}
                            </span>
                        </div>
                        <h4 style="font-size: 14px; font-weight: 600; color: #0a0a0a; margin: 4px 0 8px 0; line-height: 1.35; letter-spacing: -0.3px;">
                            [{row['codigo']}] {row['titulo'][:52]}...
                        </h4>
                        <p style="font-size: 13px; color: #737373; margin: 0 0 12px 0; line-height: 1.4;">
                            <b style="color: #171717;">Efecto Yumbo:</b> {row['efecto_empresa'][:85]}...
                        </p>
                    </div>
                    <div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 6px 10px; font-size: 12px; color: #737373; display: flex; justify-content: space-between;">
                        <span>Sev: <b style="color: {'#e7000b' if is_extreme else '#0a0a0a'};">{row['puntuacion_severidad']}/25</b></span>
                        <span>{row['urgencia'][:14]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No se registran factores críticos en el periodo actual.")

    # Gráfico de barras agrupadas PESTEL
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="blueprint-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px;">
                Distribución Comparativa por Pilar PESTEL
            </h3>
            <span class="badge-pill-outline">Riesgos vs Oportunidades</span>
        </div>
        <p style="margin: 0 0 12px 0; font-size: 13px; color: #737373;">
            Balance de factores restrictivos y favorables para la estrategia de empaques circulares.
        </p>
    """, unsafe_allow_html=True)
    bar_fig = create_pestel_bar_chart(df_factores)
    st.plotly_chart(bar_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Roles y Gobernanza
    curr_role = st.session_state.get("current_role", models.UserRole.DECISOR.value)
    st.markdown('''
    <div class="blueprint-card" style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <span style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin-left: 8px;">
                    Control de Acceso y Modelo de Roles (Usuarios, Decisores, Diseñadores)
                </span>
            </div>
            <span class="badge-pill-outline">Gobernanza Estratégica</span>
        </div>
        <p style="font-size: 13px; color: #737373; margin: 0 0 16px 0;">
            El sistema implementa separación de responsabilidades para garantizar la rigurosidad fáctica de los factores y la trazabilidad de las decisiones gerenciales en Smurfit WestRock Colombia.
        </p>
    ''', unsafe_allow_html=True)

    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        is_dis = curr_role == models.UserRole.DISENADOR.value
        pill_dis = "badge-pill-solid" if is_dis else "badge-pill-soft"
        state_dis = "<b>● SESIÓN ACTIVA</b>" if is_dis else "Disponible en panel"
        st.markdown(f'''
        <div style="background: {'#fafafa' if is_dis else '#ffffff'}; border: 1px solid {'#0a0a0a' if is_dis else '#e5e5e5'}; border-radius: 18px; padding: 14px 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span class="{pill_dis}">Diseñador</span>
                <span style="font-size: 11px; color: {'#0a0a0a' if is_dis else '#737373'};">{state_dis}</span>
            </div>
            <div style="font-weight: 600; font-size: 13.5px; color: #0a0a0a; margin-bottom: 4px;">Arquitectura & Parametrización</div>
            <p style="font-size: 12.5px; color: #737373; margin: 0; line-height: 1.4;">
                Modela factores del entorno, calibra probabilidad (1-5) e impacto (1-5), verifica fuentes oficiales y gestiona datos semilla.
            </p>
        </div>
        ''', unsafe_allow_html=True)

    with r_col2:
        is_dec = curr_role == models.UserRole.DECISOR.value
        pill_dec = "badge-pill-solid" if is_dec else "badge-pill-soft"
        state_dec = "<b>● SESIÓN ACTIVA</b>" if is_dec else "Disponible en panel"
        st.markdown(f'''
        <div style="background: {'#fafafa' if is_dec else '#ffffff'}; border: 1px solid {'#0a0a0a' if is_dec else '#e5e5e5'}; border-radius: 18px; padding: 14px 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span class="{pill_dec}">Decisor</span>
                <span style="font-size: 11px; color: {'#0a0a0a' if is_dec else '#737373'};">{state_dec}</span>
            </div>
            <div style="font-weight: 600; font-size: 13.5px; color: #0a0a0a; margin-bottom: 4px;">Gobernanza & Toma de Decisiones</div>
            <p style="font-size: 12.5px; color: #737373; margin: 0; line-height: 1.4;">
                Formula planes de acción, aprueba recomendaciones, asigna áreas operativas y actualiza el estado de factores críticos.
            </p>
        </div>
        ''', unsafe_allow_html=True)

    with r_col3:
        is_usr = curr_role == models.UserRole.USUARIO.value
        pill_usr = "badge-pill-solid" if is_usr else "badge-pill-soft"
        state_usr = "<b>● SESIÓN ACTIVA</b>" if is_usr else "Disponible en panel"
        st.markdown(f'''
        <div style="background: {'#fafafa' if is_usr else '#ffffff'}; border: 1px solid {'#0a0a0a' if is_usr else '#e5e5e5'}; border-radius: 18px; padding: 14px 16px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span class="{pill_usr}">Usuario</span>
                <span style="font-size: 11px; color: {'#0a0a0a' if is_usr else '#737373'};">{state_usr}</span>
            </div>
            <div style="font-weight: 600; font-size: 13.5px; color: #0a0a0a; margin-bottom: 4px;">Consulta & Auditoría Operativa</div>
            <p style="font-size: 12.5px; color: #737373; margin: 0; line-height: 1.4;">
                Consulta radares PESTEL, matrices de riesgo, exporta informes y registra novedades observadas en la bitácora de seguimiento.
            </p>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Contexto Corporativo en Expander Limpio
    with st.expander("Información Corporativa · Smurfit WestRock Colombia (Yumbo)"):
        st.markdown("""
        **Smurfit WestRock Colombia S.A.S.** es el principal fabricante de papel y cartón corrugado del país.
        - **Complejo Yumbo (Valle del Cauca):** Centro neurálgico de producción de kraftliner, papeles reciclados y sacos industriales.
        - **División Forestal:** Manejo responsable de más de 68.000 ha forestales certificadas FSC® en el suroccidente colombiano.
        - **Economía Circular:** Reciclaje anual de más de 220.000 toneladas de fibra secundaria en coordinación con recicladores de oficio.
        """)

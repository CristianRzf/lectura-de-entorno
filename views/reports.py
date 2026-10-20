"""
views/reports.py - Generación y Exportación de Informes Estratégicos (RF-09).
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import textwrap
import database
from utils.report_generator import generate_pdf_report, generate_excel_report
from models import PESTELCategory

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid">RF-09</span>
                    <span class="badge-pill-soft">Documentación</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Generador de Informes Estratégicos
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Generación de informes formales descargables en PDF y Excel (.xlsx) con síntesis de riesgos, oportunidades y decisiones.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">Exportación PDF & Excel</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_factores = database.get_all_factors()
    df_recomendaciones = database.get_all_recommendaciones()

    st.markdown("### Parámetros de Generación")
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        rep_categoria = st.selectbox(
            "Dimensiones PESTEL",
            ["Todas las Dimensiones (Informe Completo)"] + [c.value for c in PESTELCategory]
        )
    with c_f2:
        rep_tipo = st.selectbox(
            "Filtro por Tipo",
            ["Todos (Riesgos y Oportunidades)", "Solo Riesgos Críticos", "Solo Oportunidades Estratégicas"]
        )

    df_rep_factores = df_factores.copy()
    if rep_categoria != "Todas las Dimensiones (Informe Completo)":
        df_rep_factores = df_rep_factores[df_rep_factores["categoria_pestel"] == rep_categoria]

    if rep_tipo == "Solo Riesgos Críticos":
        df_rep_factores = df_rep_factores[df_rep_factores["tipo"] == "Riesgo"]
    elif rep_tipo == "Solo Oportunidades Estratégicas":
        df_rep_factores = df_rep_factores[df_rep_factores["tipo"] == "Oportunidad"]

    # Centro de descarga en tarjeta Paper (#ffffff)
    curr_role = st.session_state.get("current_role", "Usuario")
    curr_user = st.session_state.get("current_user_name", "Usuario")
    st.markdown(f"""
    <div class="blueprint-card" style="margin: 16px 0 24px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 15px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.3px;">
                Exportación de Documentos Formales
            </span>
            <span class="badge-pill-soft">Emisor: {curr_role}</span>
        </div>
        <p style="font-size: 13px; color: #737373; margin: 0 0 16px 0;">
            Informe oficial con membrete corporativo de Smurfit WestRock Colombia. Preparado para: <b>{curr_user}</b>.
        </p>
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        pdf_bytes = generate_pdf_report(df_rep_factores, df_recomendaciones)
        st.download_button(
            label="Descargar Informe en PDF",
            data=pdf_bytes,
            file_name=f"Informe_PESTEL_Smurfit_WestRock_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with d_col2:
        excel_bytes = generate_excel_report(df_rep_factores, df_recomendaciones)
        st.download_button(
            label="Descargar Matriz en Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Matriz_PESTEL_Smurfit_WestRock_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Vista previa en tarjeta Paper
    st.markdown("### Vista Previa del Informe")

    with st.container():
        card_preview_html = textwrap.dedent(f"""<div class="blueprint-card">
<div style="border-bottom: 1px solid #e5e5e5; padding-bottom: 16px; margin-bottom: 18px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
<div>
<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
<span class="badge-pill-solid">SMURFIT WESTROCK</span>
<span class="badge-pill-soft">INFORME PESTEL</span>
</div>
<h2 style="color: #0a0a0a; margin: 4px 0 2px 0; font-size: 24px; font-weight: 600; letter-spacing: -0.6px;">Informe de Lectura del Entorno Estratégico</h2>
<div style="color: #737373; font-size: 13px;">Complejo Industrial Yumbo · Valle del Cauca, Colombia</div>
</div>
<div style="text-align: right; font-size: 12px; color: #737373;">
<div>Fecha: <b style="color: #0a0a0a;">{datetime.now().strftime('%d/%m/%Y')}</b></div>
<div>Versión: <b>1.0 Oficial</b></div>
<div>Confidencial: <b>Uso Estratégico</b></div>
</div>
</div>
</div>
<div style="margin-bottom: 20px;">
<h4 style="color: #0a0a0a; margin: 0 0 6px 0; font-size: 15px; font-weight: 600; letter-spacing: -0.3px;">1. Síntesis Ejecutiva</h4>
<p style="color: #171717; font-size: 13.5px; line-height: 1.6; text-align: justify; margin: 0;">
Durante el presente ciclo de análisis, el macroentorno de <b>Smurfit WestRock Colombia</b> registra <b>{len(df_rep_factores)} factores monitoreados</b>. Se evidencian retos operativos en el corredor Panamericano (abastecimiento de madera del Cauca hacia Yumbo) y estrés hídrico en la cuenca del Río Cauca. Simultáneamente, la <b>Ley 2232 de 2022 (plásticos de un solo uso)</b> y la demanda creciente del sector agroexportador consolidan oportunidades de liderazgo para las soluciones corrugadas y de papel kraft producidas en Yumbo.
</p>
</div>
</div>""")
        st.markdown(card_preview_html, unsafe_allow_html=True)

        st.markdown("#### 2. Factores Evaluados en el Informe")
        df_display = df_rep_factores[[
            "codigo", "categoria_pestel", "tipo", "titulo", "probabilidad", "impacto",
            "puntuacion_severidad", "urgencia", "fuente_nombre", "estado"
        ]].copy()

        df_display.columns = [
            "Código", "Dimensión", "Tipo", "Título", "Prob.", "Imp.", "Severidad", "Urgencia", "Fuente", "Estado"
        ]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 3. Decisiones y Recomendaciones Vinculadas")
        if not df_recomendaciones.empty:
            df_rec_display = df_recomendaciones[[
                "codigo_recomendacion", "factor_codigo", "titulo", "prioridad", "area_responsable", "plazo", "estado"
            ]].copy()
            df_rec_display.columns = [
                "Código", "Factor PESTEL", "Recomendación", "Prioridad", "Área Responsable", "Plazo", "Estado"
            ]
            st.dataframe(df_rec_display, use_container_width=True, hide_index=True)
        else:
            st.info("Sin recomendaciones en el informe.")

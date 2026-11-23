"""
views/reportes.py - Bitácora de Simulaciones, Visualización Analítica y Exportación de Reportes (RF-07, RF-08).
Historial de despachos evaluados y generación de planes logísticos consolidados en .CSV y .TXT (ONU / GNU).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import io
import database
import models


def generar_reporte_txt(simulaciones: list) -> str:
    """Genera un resumen ejecutivo en formato TXT estructurado con membrete formal."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineas = [
        "=" * 82,
        "  PROGRAMA DE COOPERACIÓN INTERNACIONAL (ONU / GNU) - COLOMBIA",
        "  PLATAFORMA TRANSVERSAL DE INTELIGENCIA LOGÍSTICA Y DESPACHO PORTUARIO",
        "  INFORME EJECUTIVO CONSOLIDADO DE SIMULACIONES Y PLANIFICACIÓN LOGÍSTICA",
        "=" * 82,
        f"Fecha y Hora de Emisión: {ahora}",
        f"Total de Despachos Analizados: {len(simulaciones)}",
        "-" * 82,
        ""
    ]

    if not simulaciones:
        lineas.append("No se registran simulaciones en el período consultado.")
        return "\n".join(lineas)

    total_ton = sum(s["toneladas"] for s in simulaciones)
    total_ahorro = sum(s["ahorro_cop"] for s in simulaciones)
    puertos_cnt = {}
    for s in simulaciones:
        p = s["puerto_recomendado"]
        puertos_cnt[p] = puertos_cnt.get(p, 0) + 1

    lineas.extend([
        "1. RESUMEN EJECUTIVO Y TOTALES CONSOLIDADOS",
        f" • Volumen Total Despachado:        {total_ton:,.1f} Toneladas Métricas",
        f" • Ahorro Económico Potencial:      ${total_ahorro:,.0f} COP",
        f" • Distribución de Puertos Óptimos: " + ", ".join([f"{k}: {v} despachos" for k, v in puertos_cnt.items()]),
        "",
        "-" * 82,
        "2. DETALLE DE DESPACHOS Y PLANES LOGÍSTICOS POR ORGANIZACIÓN",
        "-" * 82
    ])

    for i, sim in enumerate(simulaciones, 1):
        lineas.extend([
            f"\n[REGISTRO #{sim['id']}] - {sim['organizacion_nombre'].upper()}",
            f"  • Sector:               {sim['sector']} | Producto: {sim['producto']}",
            f"  • Origen:               {sim['region_origen']} -> Destino: {sim['mercado_destino']}",
            f"  • Carga y Equipamiento: {sim['toneladas']} ton | {sim['contenedores']} Contenedores ({sim['tipo_carga']})",
            f"  • TRM Aplicada:         ${sim['trm']:,.0f} COP/USD",
            f"  • PUERTO RECOMENDADO:   {sim['puerto_recomendado'].upper()}",
            f"  • Costo Óptimo:         Costo Buenaventura: ${sim['costo_buenaventura_cop']:,.0f} COP | Costo Cartagena: ${sim['costo_cartagena_cop']:,.0f} COP",
            f"  • Ahorro Generado:      ${sim['ahorro_cop']:,.0f} COP frente a ruta alterna",
            f"  • Costo Unitario:       ${sim['costo_kg_optimo']:,.1f} COP/kg exportado",
            f"  • Estado Vial / Port.:  Bva: {sim.get('estado_buenaventura','N/A')} | Ctg: {sim.get('estado_cartagena','N/A')}",
            f"  • Usuario Responsable:  {sim.get('usuario','Operador')} | Fecha: {sim['fecha_simulacion']}"
        ])

    lineas.extend([
        "\n" + "=" * 82,
        "  FIN DEL INFORME EJECUTIVO - DOCUMENTO TÉCNICO DE TOMA DE DECISIONES",
        "=" * 82
    ])
    return "\n".join(lineas)


def render():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-pill-solid">BITÁCORA E INFORMES</span>
            <span class="badge-pill-soft">Análisis de Despachos</span>
            <span class="badge-pill-outline">RF-07 / RF-08</span>
        </div>
        <h1 style="font-size: 28px; font-weight: 700; letter-spacing: -0.8px; color: #0a0a0a; margin: 0 0 6px 0;">
            Bitácora de Simulaciones y Descarga de Reportes
        </h1>
        <p style="font-size: 14px; color: #737373; margin: 0; line-height: 1.5;">
            Trazabilidad histórica de todas las cotizaciones de despacho ejecutadas, métricas consolidadas 
            de volumen y ahorro, y herramientas de exportación para la toma de decisiones directivas en formatos <b>.CSV</b> y <b>.TXT</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    simulaciones = database.get_simulaciones(limit=250)
    metricas = database.get_metricas_globales()

    # Indicadores consolidados
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Simulaciones", metricas["total_simulaciones"])
    with k2:
        st.metric("Volumen Evaluado", f"{metricas['total_toneladas']:,.0f} Ton", delta="Despacho consolidado")
    with k3:
        st.metric("Ahorro Promedio / Despacho", f"${metricas['promedio_ahorro_cop']:,.0f} COP", delta="Ruta óptima")
    with k4:
        st.metric("Puerto Más Recomendado", metricas["puerto_frecuente"], delta="Mayor frecuencia")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    if not simulaciones:
        st.info(
            "Aún no se han ejecutado simulaciones de despacho. Ingrese a la sección 'Simulador de Despacho' "
            "para cotizar una operación y guardarla en la bitácora."
        )
        return

    df_sim = pd.DataFrame(simulaciones)

    # =========================================================================
    # VISUALIZACIÓN ANALÍTICA HISTÓRICA (RF-07)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 10px 0 12px 0; letter-spacing: -0.3px;">
        1. Visualización Analítica de la Demanda de Despacho
    </div>
    """, unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    with g1:
        # Frecuencia de selección de puertos
        puerto_counts = df_sim["puerto_recomendado"].value_counts().reset_index()
        puerto_counts.columns = ["Puerto", "Simulaciones"]

        fig_p = px.pie(
            puerto_counts,
            names="Puerto",
            values="Simulaciones",
            color="Puerto",
            color_discrete_map={"Buenaventura": "#0a0a0a", "Cartagena": "#737373"},
            hole=0.45
        )
        fig_p.update_layout(
            title=dict(text="Distribución de Selección de Nodos Portuarios", font=dict(size=13, color="#0a0a0a")),
            height=300,
            margin=dict(t=55, l=30, r=25, b=40),
            paper_bgcolor="#ffffff",
            font=dict(size=12, color="#0a0a0a")
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with g2:
        # Simulaciones por Sector Productivo
        sector_counts = df_sim["sector"].value_counts().reset_index()
        sector_counts.columns = ["Sector", "Cantidad"]

        fig_s = px.bar(
            sector_counts,
            x="Sector",
            y="Cantidad",
            text="Cantidad",
            color_discrete_sequence=["#171717"]
        )
        fig_s.update_layout(
            title=dict(text="Despachos por Sector Productivo", font=dict(size=13, color="#0a0a0a")),
            height=300,
            margin=dict(t=55, l=30, r=25, b=40),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#fafafa",
            font=dict(size=12, color="#0a0a0a"),
            bargap=0.5,
            yaxis=dict(gridcolor="#e5e5e5", rangemode="tozero"),
            xaxis=dict(tickfont=dict(size=11))
        )
        st.plotly_chart(fig_s, use_container_width=True)

    # =========================================================================
    # BITÁCORA Y FILTROS (RF-08)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 24px 0 10px 0; letter-spacing: -0.3px;">
        2. Registro Histórico de Simulaciones
    </div>
    """, unsafe_allow_html=True)

    f_org, f_dest, f_puerto = st.columns(3)
    with f_org:
        orgs_unicas = ["Todas"] + sorted(list(df_sim["organizacion_nombre"].unique()))
        sel_org = st.selectbox("Filtrar por Organización", options=orgs_unicas)
    with f_dest:
        dest_unicos = ["Todos"] + sorted(list(df_sim["mercado_destino"].unique()))
        sel_dest = st.selectbox("Filtrar por Mercado Destino", options=dest_unicos)
    with f_puerto:
        puertos_unicos = ["Todos", "Buenaventura", "Cartagena"]
        sel_puerto = st.selectbox("Filtrar por Puerto Recomendado", options=puertos_unicos)

    df_filtrado = df_sim.copy()
    if sel_org != "Todas":
        df_filtrado = df_filtrado[df_filtrado["organizacion_nombre"] == sel_org]
    if sel_dest != "Todos":
        df_filtrado = df_filtrado[df_filtrado["mercado_destino"] == sel_dest]
    if sel_puerto != "Todos":
        df_filtrado = df_filtrado[df_filtrado["puerto_recomendado"] == sel_puerto]

    cols_tabla = [
        "id", "fecha_simulacion", "organizacion_nombre", "sector", "region_origen",
        "mercado_destino", "toneladas", "contenedores", "puerto_recomendado",
        "ahorro_cop", "costo_kg_optimo", "usuario"
    ]
    df_mostrar = df_filtrado[cols_tabla].copy()
    df_mostrar.columns = [
        "ID", "Fecha", "Organización", "Sector", "Origen",
        "Destino", "Toneladas", "Contenedores", "Puerto Óptimo",
        "Ahorro (COP)", "COP/kg", "Usuario"
    ]

    # Formateo visual de columnas monetarias
    df_mostrar["Ahorro (COP)"] = df_mostrar["Ahorro (COP)"].apply(lambda x: f"${x:,.0f}")
    df_mostrar["COP/kg"] = df_mostrar["COP/kg"].apply(lambda x: f"${x:,.1f}")
    df_mostrar["Fecha"] = df_mostrar["Fecha"].str[:16]

    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

    # =========================================================================
    # BOTONES DE EXPORTACIÓN (RF-08)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 24px 0 10px 0; letter-spacing: -0.3px;">
        3. Exportación Consolidada de Planes Logísticos
    </div>
    """, unsafe_allow_html=True)

    c_csv, c_txt, c_espacio = st.columns([2, 2, 3])

    # 1. Exportación CSV
    with c_csv:
        csv_data = df_filtrado.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="Descargar en Formato .CSV",
            data=csv_data,
            file_name=f"simulaciones_logistica_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 2. Exportación TXT Ejecutivo
    with c_txt:
        txt_data = generar_reporte_txt(df_filtrado.to_dict(orient="records"))
        st.download_button(
            label="Descargar Informe Ejecutivo .TXT",
            data=txt_data,
            file_name=f"informe_ejecutivo_logistica_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with c_espacio:
        st.caption(
            "El archivo .CSV contiene la totalidad de variables y parámetros para análisis en hojas de cálculo. "
            "El archivo .TXT consolida el resumen ejecutivo formal para firma directiva de la cooperación internacional."
        )

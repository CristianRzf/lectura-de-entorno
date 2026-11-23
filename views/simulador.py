"""
views/simulador.py - Simulador y Comparador Estratégico de Nodos Portuarios (RF-02, RF-03, RF-04, RF-06, RF-07).
Evaluación simultánea Buenaventura (Pacífico) vs. Cartagena (Caribe) para organizaciones exportadoras.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import database
import models
from models import (
    SectorType, RegionOrigen, MercadoDestino, PuertoSalida,
    TipoCarga, NivelContingencia, comparar_puertos, calcular_contenedores_requeridos
)


def render():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-pill-solid">LOGÍSTICA TRANSVERSAL</span>
            <span class="badge-pill-soft">Despacho Portuario</span>
            <span class="badge-pill-outline">ONU / GNU Cooperación</span>
        </div>
        <h1 style="font-size: 28px; font-weight: 700; letter-spacing: -0.8px; color: #0a0a0a; margin: 0 0 6px 0;">
            Simulador y Comparador Estratégico de Despacho Portuario
        </h1>
        <p style="font-size: 14px; color: #737373; margin: 0; line-height: 1.5;">
            Evaluación simultánea de salida marítima (<b>Buenaventura</b> vs. <b>Cartagena</b>), cálculo de estructura de costos terrestres, 
            gastos portuarios, fletes internacionales y reglas de decisión por contingencias viales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Cargar datos base
    organizaciones = database.get_all_organizaciones()
    org_nombres = ["-- Ingreso Libre / Organización Temporal --"] + [f"{o['nombre']} ({o['sector']} - {o['region_origen']})" for o in organizaciones]

    # Monitoreo previo del estado de contingencias en ambos puertos (RF-05 integrado)
    cont_bva = database.get_ultima_contingencia_por_puerto(PuertoSalida.BUENAVENTURA.value)
    cont_ctg = database.get_ultima_contingencia_por_puerto(PuertoSalida.CARTAGENA.value)

    # Tarjeta de alerta de corredores viales
    col_alerta_bva, col_alerta_ctg = st.columns(2)
    with col_alerta_bva:
        nivel_b = cont_bva.get("nivel", NivelContingencia.NORMAL.value)
        es_crit_b = (nivel_b == NivelContingencia.BLOQUEO_VIAL.value)
        es_alerta_b = (nivel_b != NivelContingencia.NORMAL.value)
        badge_style_b = "badge-pill-destructive" if es_crit_b else ("badge-pill-soft" if es_alerta_b else "badge-pill-outline")
        st.markdown(f"""
        <div class="blueprint-card" style="padding: 12px 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 13px; font-weight: 600; color: #0a0a0a;">Buenaventura (Pacífico)</span>
                <span class="{badge_style_b}">{nivel_b}</span>
            </div>
            <div style="font-size: 12px; color: #737373;">
                <b>Corredor:</b> {cont_bva.get('corredor', 'Ruta 40')}<br>
                <b>Fuente:</b> {cont_bva.get('fuente_oficial', 'INVÍAS')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_alerta_ctg:
        nivel_c = cont_ctg.get("nivel", NivelContingencia.NORMAL.value)
        es_crit_c = (nivel_c == NivelContingencia.BLOQUEO_VIAL.value)
        es_alerta_c = (nivel_c != NivelContingencia.NORMAL.value)
        badge_style_c = "badge-pill-destructive" if es_crit_c else ("badge-pill-soft" if es_alerta_c else "badge-pill-outline")
        st.markdown(f"""
        <div class="blueprint-card" style="padding: 12px 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 13px; font-weight: 600; color: #0a0a0a;">Cartagena (Caribe)</span>
                <span class="{badge_style_c}">{nivel_c}</span>
            </div>
            <div style="font-size: 12px; color: #737373;">
                <b>Corredor:</b> {cont_ctg.get('corredor', 'Mamonal / Troncal Caribe')}<br>
                <b>Fuente:</b> {cont_ctg.get('fuente_oficial', 'DIMAR')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # FORMULARIO DE PARAMETRIZACIÓN (RF-01, RF-02)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin-bottom: 12px; letter-spacing: -0.3px;">
        1. Parametrización del Despacho y Variables Macro
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        c_org, c_dest = st.columns([3, 2])
        
        with c_org:
            sel_org_idx = st.selectbox(
                "Organización Exportadora (RF-01)",
                options=range(len(org_nombres)),
                format_func=lambda x: org_nombres[x],
                help="Seleccione una organización productiva registrada o configure una operación libre."
            )

        org_seleccionada = None
        if sel_org_idx > 0:
            org_seleccionada = organizaciones[sel_org_idx - 1]
            default_sector = org_seleccionada["sector"]
            default_region = org_seleccionada["region_origen"]
            default_producto = org_seleccionada["producto_principal"]
            org_nombre_final = org_seleccionada["nombre"]
            org_id_final = org_seleccionada["id"]
        else:
            default_sector = SectorType.GRANOS_SECOS.value
            default_region = RegionOrigen.CAUCA.value
            default_producto = "Café Especial de Origen"
            org_nombre_final = "Operación Independiente / Programa Cooperación"
            org_id_final = None

        with c_dest:
            mercado_destino = st.selectbox(
                "Mercado Internacional de Destino",
                options=[m.value for m in MercadoDestino],
                index=0,
                help="Determina el flete marítimo internacional y los requerimientos aduaneros/fitosanitarios."
            )

        # Segunda fila de parámetros
        col_sec, col_reg, col_prod = st.columns([2, 2, 3])
        with col_sec:
            sector_val = st.selectbox(
                "Sector Productivo",
                options=[s.value for s in SectorType],
                index=[s.value for s in SectorType].index(default_sector) if default_sector in [s.value for s in SectorType] else 0,
                disabled=(org_seleccionada is not None)
            )
        with col_reg:
            region_val = st.selectbox(
                "Región / Departamento de Origen",
                options=[r.value for r in RegionOrigen],
                index=[r.value for r in RegionOrigen].index(default_region) if default_region in [r.value for r in RegionOrigen] else 0,
                disabled=(org_seleccionada is not None)
            )
        with col_prod:
            producto_val = st.text_input(
                "Producto a Exportar",
                value=default_producto,
                disabled=(org_seleccionada is not None)
            )

        # Tercera fila: Parámetros operativos y macroeconómicos (RF-02)
        col_ton, col_trm, col_tipo_carga = st.columns([2, 2, 3])
        with col_ton:
            toneladas_val = st.number_input(
                "Volumen a Exportar (Toneladas)",
                min_value=1.0,
                max_value=1000.0,
                value=36.0,
                step=1.0,
                help="Capacidad nominal por contenedor estándar de 20 pies: 18 toneladas."
            )
        with col_trm:
            trm_val = st.number_input(
                "TRM Proyectada (COP / USD)",
                min_value=3000.0,
                max_value=6000.0,
                value=4150.0,
                step=10.0,
                help="Tasa Representativa del Mercado aplicada a la conversión de fletes internacionales."
            )
        with col_tipo_carga:
            # Determinación sugerida de reefer según el sector
            es_perecedero = (sector_val == SectorType.FRUTAS_PERECEDEROS.value)
            carga_opciones = [TipoCarga.ESTANDAR.value, TipoCarga.REFRIGERADA.value]
            carga_def_idx = 1 if es_perecedero else 0
            tipo_carga_sel = st.selectbox(
                "Tipo de Equipamiento / Contenedor",
                options=carga_opciones,
                index=carga_def_idx,
                help="La carga refrigerada aplica un factor multiplicador de 1.35x en transporte y flete marítimo."
            )
            es_refrigerado = (tipo_carga_sel == TipoCarga.REFRIGERADA.value)

    # Cálculo automático de contenedores (RF-02)
    contenedores_calculados = calcular_contenedores_requeridos(toneladas_val)

    st.markdown(f"""
    <div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 10px 16px; margin: 12px 0 24px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <span style="font-size: 13px; color: #171717;">
            <b>Equipamiento Estimado:</b> {contenedores_calculados} Contenedor(es) de 20 pies ({toneladas_val} ton @ 18 ton/TEU)
        </span>
        <span style="font-size: 12px; color: {'#0a0a0a' if es_refrigerado else '#737373'}; font-weight: 500;">
            {'❄️ Modalidad Refrigerada Reefer (+35% factor térmico)' if es_refrigerado else '📦 Modalidad Seca Estándar (Dry)'}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # MOTOR DE CÁLCULO Y COMPARACIÓN (RF-03, RF-04)
    # =========================================================================
    resultado = comparar_puertos(
        region_origen=region_val,
        mercado_destino=mercado_destino,
        toneladas=toneladas_val,
        trm=trm_val,
        sector=sector_val,
        es_refrigerado_manual=es_refrigerado,
        contingencia_buenaventura=cont_bva.get("nivel", NivelContingencia.NORMAL.value),
        contingencia_cartagena=cont_ctg.get("nivel", NivelContingencia.NORMAL.value)
    )

    puerto_opt = resultado["puerto_recomendado"]
    costo_opt_cop = resultado["costo_optimo_cop"]
    costo_opt_kg = resultado["costo_optimo_kg_cop"]
    ahorro_cop = resultado["ahorro_absoluto_cop"]
    ahorro_pct = resultado["ahorro_porcentual"]
    motivo_rec = resultado["motivo_recomendacion"]

    # KPIS PRINCIPALES DEL COMPARADOR (RF-04)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label="Puerto Recomendado",
            value=puerto_opt,
            delta="Ruta Óptima",
            delta_color="normal"
        )
    with k2:
        st.metric(
            label="Ahorro Frente a Ruta Alterna",
            value=f"${ahorro_cop:,.0f} COP",
            delta=f"-{ahorro_pct}% costo total",
            delta_color="normal"
        )
    with k3:
        st.metric(
            label="Costo Total Consolidado",
            value=f"${costo_opt_cop:,.0f} COP",
            delta=f"{resultado['contenedores']} contenedor(es)",
            delta_color="off"
        )
    with k4:
        st.metric(
            label="Impacto Unitario por Kg",
            value=f"${costo_opt_kg:,.1f} COP/kg",
            delta=f"Para {toneladas_val*1000:,.0f} kg",
            delta_color="off"
        )

    # Tarjeta de Justificación Estratégica
    st.markdown(f"""
    <div class="blueprint-card" style="margin: 18px 0; border-left: 4px solid #0a0a0a;">
        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.6px; color: #737373; font-weight: 600; margin-bottom: 4px;">
            Criterio de Decisión Logística
        </div>
        <div style="font-size: 14px; color: #0a0a0a; line-height: 1.45; font-weight: 500;">
            {motivo_rec}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # TABLA COMPARATIVA DETALLADA LADO A LADO (RF-03, RF-04)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 20px 0 10px 0; letter-spacing: -0.3px;">
        2. Desglose Estructurado de Costos: Buenaventura vs. Cartagena
    </div>
    """, unsafe_allow_html=True)

    bva = resultado["buenaventura"]
    ctg = resultado["cartagena"]

    df_comparativo = pd.DataFrame([
        {
            "Rubro Logístico": "Flete Terrestre (Origen a Puerto)",
            "Buenaventura (Pacífico)": f"${bva['flete_terrestre_cop']:,.0f} COP",
            "Cartagena (Caribe)": f"${ctg['flete_terrestre_cop']:,.0f} COP",
            "Diferencia (Ctg - Bva)": f"${(ctg['flete_terrestre_cop'] - bva['flete_terrestre_cop']):,.0f} COP"
        },
        {
            "Rubro Logístico": "Gastos Portuarios (THC, Inspecciones, Movilización)",
            "Buenaventura (Pacífico)": f"${bva['gastos_portuarios_cop']:,.0f} COP",
            "Cartagena (Caribe)": f"${ctg['gastos_portuarios_cop']:,.0f} COP",
            "Diferencia (Ctg - Bva)": f"${(ctg['gastos_portuarios_cop'] - bva['gastos_portuarios_cop']):,.0f} COP"
        },
        {
            "Rubro Logístico": "Flete Marítimo Internacional (USD)",
            "Buenaventura (Pacífico)": f"${bva['flete_maritimo_usd']:,.0f} USD",
            "Cartagena (Caribe)": f"${ctg['flete_maritimo_usd']:,.0f} USD",
            "Diferencia (Ctg - Bva)": f"${(ctg['flete_maritimo_usd'] - bva['flete_maritimo_usd']):,.0f} USD"
        },
        {
            "Rubro Logístico": f"Flete Marítimo Convertido (@ TRM ${trm_val:,.0f})",
            "Buenaventura (Pacífico)": f"${bva['flete_maritimo_cop']:,.0f} COP",
            "Cartagena (Caribe)": f"${ctg['flete_maritimo_cop']:,.0f} COP",
            "Diferencia (Ctg - Bva)": f"${(ctg['flete_maritimo_cop'] - bva['flete_maritimo_cop']):,.0f} COP"
        },
        {
            "Rubro Logístico": "Sobrecostos por Contingencia Vial / Portuaria",
            "Buenaventura (Pacífico)": f"${bva['costo_contingencia_cop']:,.0f} COP",
            "Cartagena (Caribe)": f"${ctg['costo_contingencia_cop']:,.0f} COP",
            "Diferencia (Ctg - Bva)": f"${(ctg['costo_contingencia_cop'] - bva['costo_contingencia_cop']):,.0f} COP"
        },
        {
            "Rubro Logístico": "ESTADO VIAL / OPERATIVO DEL CORREDOR",
            "Buenaventura (Pacífico)": bva["nivel_contingencia"],
            "Cartagena (Caribe)": ctg["nivel_contingencia"],
            "Diferencia (Ctg - Bva)": "Prioridad por Habilitación" if (bva["es_bloqueo"] or ctg["es_bloqueo"]) else "N/A"
        },
        {
            "Rubro Logístico": "COSTO TOTAL CONSOLIDADO (COP)",
            "Buenaventura (Pacífico)": f"${bva['costo_total_cop']:,.0f} COP",
            "Cartagena (Caribe)": f"${ctg['costo_total_cop']:,.0f} COP",
            "Diferencia (Ctg - Bva)": f"${(ctg['costo_total_cop'] - bva['costo_total_cop']):,.0f} COP"
        },
        {
            "Rubro Logístico": "IMPACTO UNITARIO LOGÍSTICO (COP/kg)",
            "Buenaventura (Pacífico)": f"${bva['costo_por_kg_cop']:,.1f} COP/kg",
            "Cartagena (Caribe)": f"${ctg['costo_por_kg_cop']:,.1f} COP/kg",
            "Diferencia (Ctg - Bva)": f"${(ctg['costo_por_kg_cop'] - bva['costo_por_kg_cop']):,.1f} COP/kg"
        }
    ])

    st.dataframe(df_comparativo, use_container_width=True, hide_index=True)

    # =========================================================================
    # VISUALIZACIÓN ANALÍTICA: GRÁFICO APILADO DE COSTOS (RF-07)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 24px 0 10px 0; letter-spacing: -0.3px;">
        3. Visualización Analítica: Estructura Porcentual y Monetaria por Puerto
    </div>
    """, unsafe_allow_html=True)

    puertos_nombres = ["Buenaventura (Pacífico)", "Cartagena (Caribe)"]
    fletes_terrestres = [bva["flete_terrestre_cop"], ctg["flete_terrestre_cop"]]
    gastos_portuarios = [bva["gastos_portuarios_cop"], ctg["gastos_portuarios_cop"]]
    fletes_maritimos = [bva["flete_maritimo_cop"], ctg["flete_maritimo_cop"]]
    contingencias = [bva["costo_contingencia_cop"], ctg["costo_contingencia_cop"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Flete Terrestre",
        x=puertos_nombres,
        y=fletes_terrestres,
        marker_color="#171717",
        text=[f"${v/1e6:.1f}M" for v in fletes_terrestres],
        textposition="inside"
    ))
    fig.add_trace(go.Bar(
        name="Gastos Portuarios (THC/Insp)",
        x=puertos_nombres,
        y=gastos_portuarios,
        marker_color="#525252",
        text=[f"${v/1e6:.1f}M" for v in gastos_portuarios],
        textposition="inside"
    ))
    fig.add_trace(go.Bar(
        name="Flete Marítimo Internacional",
        x=puertos_nombres,
        y=fletes_maritimos,
        marker_color="#8c8c8c",
        text=[f"${v/1e6:.1f}M" for v in fletes_maritimos],
        textposition="inside"
    ))
    if any(c > 0 for c in contingencias):
        fig.add_trace(go.Bar(
            name="Sobrecosto Contingencia",
            x=puertos_nombres,
            y=contingencias,
            marker_color="#e7000b",
            text=[f"${v/1e6:.1f}M" for v in contingencias],
            textposition="inside"
        ))

    fig.update_layout(
        barmode="stack",
        height=380,
        margin=dict(t=55, l=30, r=25, b=40),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        font=dict(family="sans-serif", size=13, color="#0a0a0a"),
        bargap=0.45,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            title="Costo Consolidado (COP)",
            gridcolor="#e5e5e5",
            tickprefix="$",
            showline=True,
            linecolor="#e5e5e5"
        ),
        xaxis=dict(
            showline=True,
            linecolor="#e5e5e5"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================================================================
    # MOTOR DE RECOMENDACIONES AUTOMÁTICAS (RF-06)
    # =========================================================================
    st.markdown("""
    <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 24px 0 12px 0; letter-spacing: -0.3px;">
        4. Motor de Recomendaciones Logísticas, Cut-Off y Cumplimiento Normativo
    </div>
    """, unsafe_allow_html=True)

    recs = resultado["recomendaciones"]

    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        st.markdown("""
        <div class="blueprint-card" style="height: 100%;">
            <div style="font-size: 13px; font-weight: 600; color: #0a0a0a; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                <span class="badge-pill-solid">Ruta & Cut-Off</span>
            </div>
        """, unsafe_allow_html=True)
        for item in recs["ruta_y_tiempos"]:
            st.markdown(f"<p style='font-size: 12.5px; color: #525252; margin-bottom: 8px; line-height: 1.4;'>• {item}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r_col2:
        st.markdown("""
        <div class="blueprint-card" style="height: 100%;">
            <div style="font-size: 13px; font-weight: 600; color: #0a0a0a; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                <span class="badge-pill-soft">Carga & Calidad</span>
            </div>
        """, unsafe_allow_html=True)
        for item in recs["tecnicas_carga"]:
            st.markdown(f"<p style='font-size: 12.5px; color: #525252; margin-bottom: 8px; line-height: 1.4;'>• {item}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r_col3:
        st.markdown("""
        <div class="blueprint-card" style="height: 100%;">
            <div style="font-size: 13px; font-weight: 600; color: #0a0a0a; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                <span class="badge-pill-outline">Normativa & Aduana</span>
            </div>
        """, unsafe_allow_html=True)
        for item in recs["normativa_documental"]:
            st.markdown(f"<p style='font-size: 12.5px; color: #525252; margin-bottom: 8px; line-height: 1.4;'>• {item}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # GUARDAR SIMULACIÓN EN BITÁCORA (RF-08)
    # =========================================================================
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    c_btn, c_info = st.columns([2, 5])
    
    with c_btn:
        btn_guardar = st.button("Guardar en Bitácora de Despacho", use_container_width=True)

    with c_info:
        current_user = st.session_state.get("current_user_name", "Operador de Logística")
        st.caption(f"La simulación quedará registrada bajo la sesión de: **{current_user}** en la base de datos central.")

    if btn_guardar:
        sim_id = database.insert_simulacion(
            organizacion_id=org_id_final,
            organizacion_nombre=org_nombre_final,
            sector=sector_val,
            producto=producto_val,
            region_origen=region_val,
            mercado_destino=mercado_destino,
            toneladas=toneladas_val,
            trm=trm_val,
            tipo_carga=tipo_carga_sel,
            contenedores=contenedores_calculados,
            puerto_recomendado=puerto_opt,
            costo_buenaventura_cop=bva["costo_total_cop"],
            costo_cartagena_cop=ctg["costo_total_cop"],
            ahorro_cop=ahorro_cop,
            costo_kg_optimo=costo_opt_kg,
            estado_buenaventura=bva["nivel_contingencia"],
            estado_cartagena=ctg["nivel_contingencia"],
            detalles_dict=resultado,
            usuario=current_user
        )
        database.log_auditoria(
            usuario=current_user,
            rol=st.session_state.get("current_role", models.UserRole.USUARIO_OPERATIVO.value),
            accion="NUEVA_SIMULACION",
            detalle=f"Simulación #{sim_id} para {org_nombre_final} ({toneladas_val} ton hacia {mercado_destino}). Puerto recomendado: {puerto_opt}."
        )
        st.success(f"Plan logístico registrado exitosamente en la bitácora con ID #{sim_id}. Puede consultarlo o exportarlo en la sección de 'Bitácora e Informes'.")

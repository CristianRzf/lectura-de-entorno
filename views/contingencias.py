"""
views/contingencias.py - Monitor de Contingencias Viales y Portuarias (RF-05, RF-09).
Registro y supervisión en tiempo real de novedades en corredores hacia Buenaventura y Cartagena.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import database
import models
from models import PuertoSalida, NivelContingencia, check_permission


def render():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-pill-solid">SUPERVISIÓN VIAL</span>
            <span class="badge-pill-soft">Puertos & Corredores</span>
            <span class="badge-pill-outline">RF-05 / RF-09</span>
        </div>
        <h1 style="font-size: 28px; font-weight: 700; letter-spacing: -0.8px; color: #0a0a0a; margin: 0 0 6px 0;">
            Monitor de Contingencias Viales y Operación Portuaria
        </h1>
        <p style="font-size: 14px; color: #737373; margin: 0; line-height: 1.5;">
            Supervisión continua de transitabilidad en troncales nacionales y operatividad en terminales marítimas.
            Las alertas registradas aquí alimentan automáticamente las reglas de priorización del simulador de despacho.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Estado actual consolidado por puerto
    bva_actual = database.get_ultima_contingencia_por_puerto(PuertoSalida.BUENAVENTURA.value)
    ctg_actual = database.get_ultima_contingencia_por_puerto(PuertoSalida.CARTAGENA.value)

    c1, c2 = st.columns(2)
    with c1:
        nivel_b = bva_actual.get("nivel", NivelContingencia.NORMAL.value)
        es_crit_b = (nivel_b == NivelContingencia.BLOQUEO_VIAL.value)
        es_alerta_b = (nivel_b != NivelContingencia.NORMAL.value)
        pill_b = "badge-pill-destructive" if es_crit_b else ("badge-pill-soft" if es_alerta_b else "badge-pill-outline")
        
        st.markdown(f"""
        <div class="blueprint-card" style="border-top: 3px solid {'#e7000b' if es_crit_b else '#0a0a0a'};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 0;">
                    Corredor Pacífico: Buenaventura
                </h3>
                <span class="{pill_b}">{nivel_b}</span>
            </div>
            <div style="font-size: 13px; color: #171717; font-weight: 500; margin-bottom: 4px;">
                {bva_actual.get('corredor', 'Ruta Nacional 40')}
            </div>
            <p style="font-size: 12.5px; color: #525252; margin: 0 0 8px 0; line-height: 1.45;">
                {bva_actual.get('descripcion', 'Operación normal.')}
            </p>
            <div style="font-size: 11.5px; color: #737373; border-top: 1px solid #f0f0f0; padding-top: 6px; display: flex; justify-content: space-between;">
                <span><b>Fuente:</b> {bva_actual.get('fuente_oficial', 'INVÍAS')}</span>
                <span>{bva_actual.get('fecha_reporte', '')[:16]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        nivel_c = ctg_actual.get("nivel", NivelContingencia.NORMAL.value)
        es_crit_c = (nivel_c == NivelContingencia.BLOQUEO_VIAL.value)
        es_alerta_c = (nivel_c != NivelContingencia.NORMAL.value)
        pill_c = "badge-pill-destructive" if es_crit_c else ("badge-pill-soft" if es_alerta_c else "badge-pill-outline")

        st.markdown(f"""
        <div class="blueprint-card" style="border-top: 3px solid {'#e7000b' if es_crit_c else '#0a0a0a'};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 0;">
                    Corredor Caribe: Cartagena
                </h3>
                <span class="{pill_c}">{nivel_c}</span>
            </div>
            <div style="font-size: 13px; color: #171717; font-weight: 500; margin-bottom: 4px;">
                {ctg_actual.get('corredor', 'Mamonal / Troncal Caribe')}
            </div>
            <p style="font-size: 12.5px; color: #525252; margin: 0 0 8px 0; line-height: 1.45;">
                {ctg_actual.get('descripcion', 'Operación normal.')}
            </p>
            <div style="font-size: 11.5px; color: #737373; border-top: 1px solid #f0f0f0; padding-top: 6px; display: flex; justify-content: space-between;">
                <span><b>Fuente:</b> {ctg_actual.get('fuente_oficial', 'DIMAR')}</span>
                <span>{ctg_actual.get('fecha_reporte', '')[:16]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Verificación de permisos de rol para registrar alertas (RF-09)
    current_role = st.session_state.get("current_role", models.UserRole.USUARIO_OPERATIVO.value)
    puede_registrar = check_permission(current_role, "registrar_contingencia")

    tab_historial, tab_registro = st.tabs(["Historial de Contingencias", "Reportar Nueva Novedad Vial / Portuaria"])

    with tab_historial:
        contingencias = database.get_contingencias(solo_activas=False)
        if contingencias:
            df_cont = pd.DataFrame(contingencias)
            df_show = df_cont[["id", "puerto", "corredor", "nivel", "fuente_oficial", "descripcion", "fecha_reporte"]].copy()
            df_show.columns = ["ID", "Puerto", "Corredor / Tramo", "Nivel de Contingencia", "Fuente Oficial", "Detalle de la Novedad", "Fecha de Reporte"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("No se han registrado reportes viales o portuarios en el sistema.")

    with tab_registro:
        if not puede_registrar:
            st.warning(
                f"Acceso Restringido: El rol activo actual ('{current_role}') tiene permisos de solo lectura para el monitor de contingencias. "
                "Para emitir o actualizar reportes viales y portuarios, cambie al perfil de 'Decisor' o 'Diseñador/Administrador' en la barra lateral."
            )
        else:
            st.markdown("""
            <div style="font-size: 14px; color: #525252; margin-bottom: 14px;">
                Complete el formulario para incorporar una nueva alerta oficial. El simulador recalculará automáticamente 
                los sobrecostos e impactos en tiempo de entrega.
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_nueva_contingencia", clear_on_submit=True):
                fc1, fc2 = st.columns(2)
                with fc1:
                    nuevo_puerto = st.selectbox(
                        "Nodo Portuario Afectado *",
                        options=[p.value for p in PuertoSalida]
                    )
                with fc2:
                    nuevo_nivel = st.selectbox(
                        "Nivel de Afectación *",
                        options=[n.value for n in NivelContingencia]
                    )

                nuevo_corredor = st.text_input(
                    "Corredor Vial, Tramo Específico o Terminal *",
                    placeholder="Ej. Vía Panamericana Popayán - Cali / Terminal Contecar Cartagena"
                )

                fc3, fc4 = st.columns(2)
                with fc3:
                    nueva_fuente = st.text_input(
                        "Fuente Oficial Autorizada *",
                        placeholder="Ej. INVÍAS #767 / DIMAR / DITRA / ANI"
                    )
                with fc4:
                    st.caption("Los reportes deben sustentarse en boletines emitidos por entidades oficiales o autoridades de tránsito.")

                nueva_desc = st.text_area(
                    "Descripción Detallada de la Novedad y Recomendación *",
                    placeholder="Detalle el tipo de restricción (cierre total, paso a un carril, retraso en báscula, etc.) y la estimación temporal de solución.",
                    height=100
                )

                btn_guardar_cont = st.form_submit_button("Publicar Reporte de Contingencia", use_container_width=True)

                if btn_guardar_cont:
                    if not nuevo_corredor.strip() or not nueva_fuente.strip() or not nueva_desc.strip():
                        st.error("Por favor complete todos los campos obligatorios marcados con (*).")
                    else:
                        c_id = database.insert_contingencia(
                            puerto=nuevo_puerto,
                            corredor=nuevo_corredor,
                            nivel=nuevo_nivel,
                            fuente_oficial=nueva_fuente,
                            descripcion=nueva_desc
                        )
                        database.log_auditoria(
                            usuario=st.session_state.get("current_user_name", "Usuario"),
                            rol=current_role,
                            accion="NUEVA_CONTINGENCIA",
                            detalle=f"Reporte #{c_id}: {nuevo_nivel} en {nuevo_puerto} ({nuevo_corredor})."
                        )
                        st.success(f"Novedad #{c_id} registrada con éxito. Las próximas simulaciones reflejarán este estado de transitabilidad.")
                        st.rerun()

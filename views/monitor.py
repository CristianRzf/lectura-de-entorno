"""
views/monitor.py - Monitor del Entorno: Captura (RF-01) y Trazabilidad (RF-03).
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import database
import models
from models import PESTELCategory, FactorType, UrgencyLevel, FactorStatus, PESTEL_META
from utils.external_sources import get_official_sources, get_preconfigured_signals

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid">RF-01 & RF-03</span>
                    <span class="badge-pill-soft">Captura</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Monitor del Entorno
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Registro de factores nacionales, internacionales y del Valle del Cauca con verificación documental de procedencia.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">Procedencia Verificable</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_registro, tab_fuentes, tab_explorador = st.tabs([
        "Registro de Nuevo Factor",
        "Fuentes Oficiales & Señales",
        "Registro Histórico & Fuentes"
    ])

    if "prefill_data" not in st.session_state:
        st.session_state.prefill_data = None

    # =========================================================================
    # TAB 1: FORMULARIO DE REGISTRO
    # =========================================================================
    with tab_registro:
        curr_role = st.session_state.get("current_role", "Usuario")
        can_create = models.check_permission(curr_role, "create_factor")
        role_badge, pill_cls = models.get_role_badge(curr_role)

        if not can_create:
            st.markdown(f'''
            <div class="blueprint-card" style="margin-bottom: 16px; border-left: 3px solid #171717;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 600; color: #0a0a0a;">Acceso Restringido en Modo Captura</span>
                    <span class="{pill_cls}">{role_badge}</span>
                </div>
                <p style="font-size: 13px; color: #737373; margin: 0; line-height: 1.45;">
                    El modelado, parametrización y registro de nuevos factores macroambientales está reservado para el rol de <b>Diseñador</b>.
                    Con su rol activo (<b>{curr_role}</b>), puede explorar el catálogo de fuentes oficiales y el histórico de trazabilidad.
                    Para ingresar nuevos factores, seleccione el rol <b>Diseñador</b> en el panel lateral.
                </p>
            </div>
            ''', unsafe_allow_html=True)

        prefill = st.session_state.prefill_data or {}
        if prefill:
            st.info(f"Señal precargada: **{prefill.get('titulo', '')}**")
            if st.button("Limpiar datos asistidos"):
                st.session_state.prefill_data = None
                st.rerun()

        with st.form("form_captura_entorno", clear_on_submit=False):
            st.markdown("##### 1. Clasificación Metodológica PESTEL (RF-02)")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                titulo = st.text_input(
                    "Título del Factor del Entorno *",
                    value=prefill.get("titulo", ""),
                    placeholder="Ej. Nueva normativa de la CVC sobre vertimientos al Río Cauca"
                )
            with c2:
                cat_list = [c.value for c in PESTELCategory]
                cat_default_idx = cat_list.index(prefill.get("categoria_pestel", "Político")) if prefill.get("categoria_pestel") in cat_list else 0
                categoria_pestel = st.selectbox("Dimensión PESTEL *", cat_list, index=cat_default_idx)
            with c3:
                tipo_list = [t.value for t in FactorType]
                tipo_default_idx = tipo_list.index(prefill.get("tipo", "Oportunidad")) if prefill.get("tipo") in tipo_list else 0
                tipo = st.selectbox("Naturaleza del Factor *", tipo_list, index=tipo_default_idx)

            c4, c5 = st.columns([1, 1])
            with c4:
                ambito_list = ["Nacional", "Internacional", "Regional Valle del Cauca/Yumbo"]
                ambito_default = prefill.get("ambito", "Nacional")
                ambito_idx = ambito_list.index(ambito_default) if ambito_default in ambito_list else 0
                ambito = st.selectbox("Ámbito Geográfico *", ambito_list, index=ambito_idx)
            with c5:
                estado_list = [s.value for s in FactorStatus]
                estado = st.selectbox("Estado Operativo", estado_list, index=0)

            descripcion = st.text_area(
                "Descripción Fáctica del Factor *",
                value=prefill.get("descripcion", ""),
                placeholder="Detalle el cambio normativo, macroeconómico, comunitario o tecnológico...",
                height=80
            )

            st.markdown("##### 2. Trazabilidad de la Fuente (RF-03)")
            f1, f2 = st.columns([1.5, 2])
            with f1:
                fuente_nombre = st.text_input(
                    "Entidad / Fuente Autora *",
                    value=prefill.get("fuente_nombre", ""),
                    placeholder="Ej. CVC, MinAmbiente, DANE, Portafolio"
                )
            with f2:
                fuente_url = st.text_input(
                    "Enlace / URL de Verificación *",
                    value=prefill.get("fuente_url", "https://"),
                    placeholder="https://..."
                )

            f3, f4, f5 = st.columns(3)
            with f3:
                fuente_confiabilidad = st.selectbox(
                    "Nivel de Confiabilidad",
                    ["Alta (Entidad Oficial / Regulador)", "Alta (Gremio Reconocido)", "Media (Reporte Especializado)", "Preliminar"],
                    index=0
                )
            with f4:
                fecha_pub = st.date_input(
                    "Fecha de Publicación *",
                    value=datetime.strptime(prefill.get("fecha_publicacion", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
                )
            with f5:
                fecha_con = st.date_input(
                    "Fecha de Consulta *",
                    value=datetime.now()
                )

            st.markdown("##### 3. Evaluación de Impacto sobre Smurfit WestRock Yumbo (RF-04)")
            e1, e2, e3 = st.columns(3)
            with e1:
                probabilidad = st.slider("Probabilidad (1 a 5) *", 1, 5, int(prefill.get("probabilidad", 3)))
            with e2:
                impacto = st.slider("Magnitud de Impacto (1 a 5) *", 1, 5, int(prefill.get("impacto", 3)))
            with e3:
                urgencia_list = [u.value for u in UrgencyLevel]
                urg_default = prefill.get("urgencia", UrgencyLevel.MEDIA.value)
                urg_idx = urgencia_list.index(urg_default) if urg_default in urgencia_list else 2
                urgencia = st.selectbox("Urgencia Temporal *", urgencia_list, index=urg_idx)

            efecto_empresa = st.text_area(
                "Efecto Potencial Concreto en Smurfit WestRock (Planta Yumbo / Forestal) *",
                value=prefill.get("efecto_empresa", ""),
                placeholder="Impacto directo en suministro de madera, costos de energía, ventas de corrugado o cumplimiento regulatorio...",
                height=80
            )

            default_user = st.session_state.get("current_user_name", "Ing. Sofía Ramírez")
            usuario_registra = st.text_input(
                "Analista de Entorno Responsable",
                value=f"{default_user} ({curr_role})",
                disabled=not can_create
            )

            if can_create:
                submitted = st.form_submit_button("Guardar Factor en Base de Datos", use_container_width=True)
            else:
                submitted = st.form_submit_button("Guardar Factor en Base de Datos", use_container_width=True, disabled=True)
                st.caption("🔒 *Función restringida: se requiere el rol Diseñador para guardar factores.*")

            if submitted:
                if not titulo.strip():
                    st.error("El título es obligatorio.")
                elif not descripcion.strip():
                    st.error("La descripción es obligatoria.")
                elif not fuente_nombre.strip():
                    st.error("El nombre de la fuente es obligatorio (RF-03).")
                elif not fuente_url.strip() or fuente_url.strip() == "https://":
                    st.error("El enlace URL de verificación es obligatorio (RF-03).")
                elif not efecto_empresa.strip():
                    st.error("Debe indicar el efecto concreto en la empresa.")
                else:
                    data = {
                        "titulo": titulo.strip(),
                        "categoria_pestel": categoria_pestel,
                        "tipo": tipo,
                        "ambito": ambito,
                        "descripcion": descripcion.strip(),
                        "probabilidad": probabilidad,
                        "impacto": impacto,
                        "urgencia": urgencia,
                        "efecto_empresa": efecto_empresa.strip(),
                        "fuente_nombre": fuente_nombre.strip(),
                        "fuente_url": fuente_url.strip(),
                        "fuente_confiabilidad": fuente_confiabilidad.split("(")[0].strip(),
                        "fecha_publicacion": fecha_pub.strftime("%Y-%m-%d"),
                        "fecha_consulta": fecha_con.strftime("%Y-%m-%d"),
                        "estado": estado,
                        "usuario_registra": usuario_registra.strip(),
                        "rol_registra": curr_role
                    }
                    factor_id = database.add_factor(data)
                    st.success(f"Factor guardado correctamente (ID: {factor_id}). Clasificado en {categoria_pestel}.")
                    st.session_state.prefill_data = None
                    st.rerun()

    # =========================================================================
    # TAB 2: FUENTES OFICIALES & SEÑALES ASISTIDAS
    # =========================================================================
    with tab_fuentes:
        st.markdown("### Directorio de Fuentes Públicas Autorizadas")
        st.caption("Organismos oficiales para la vigilancia del entorno papelero y forestal en Colombia.")

        sources = get_official_sources()
        src_cols = st.columns(2)
        for idx, src in enumerate(sources):
            with src_cols[idx % 2]:
                st.markdown(f"""
                <div class="blueprint-card" style="margin-bottom: 12px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 600; color: #0a0a0a; font-size: 14px;">{src['entidad']}</span>
                        <span class="badge-pill-soft">{src['tipo']}</span>
                    </div>
                    <p style="font-size: 13px; color: #737373; margin: 0 0 10px 0; line-height: 1.4;">
                        {src['descripcion']}
                    </p>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; border-top: 1px solid #e5e5e5; padding-top: 8px;">
                        <span style="color: #737373;">Pilar: <b style="color: #0a0a0a;">{src['categoria_primaria']}</b></span>
                        <a href="{src['url']}" target="_blank" style="text-decoration: none; color: #0a0a0a; font-weight: 500;">
                            Abrir Portal ↗
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #e5e5e5; margin: 24px 0;'>", unsafe_allow_html=True)

        st.markdown("### Señales Preconfiguradas para Captura Rápida")
        st.caption("Importe señales verificadas directamente al formulario con un solo clic.")

        signals = get_preconfigured_signals()
        for idx, sig in enumerate(signals):
            c_sig, c_act = st.columns([4, 1])
            with c_sig:
                is_r = sig["tipo"] == "Riesgo"
                pill_type = "badge-pill-destructive" if (is_r and sig["probabilidad"] * sig["impacto"] >= 16) else ("badge-pill-solid" if is_r else "badge-pill-soft")

                st.markdown(f"""
                <div class="blueprint-card" style="margin-bottom: 10px; padding: 14px 18px;">
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                        <span class="{pill_type}">[{sig['tipo'].upper()}]</span>
                        <span style="font-size: 12px; color: #0a0a0a; font-weight: 500;">{sig['categoria_pestel']} · {sig['ambito']}</span>
                        <span style="font-size: 12px; color: #737373;">{sig['fecha_publicacion']}</span>
                    </div>
                    <div style="font-weight: 600; color: #0a0a0a; font-size: 14px; margin: 4px 0;">{sig['titulo']}</div>
                    <div style="font-size: 12px; color: #737373;">
                        Fuente: <a href="{sig['fuente_url']}" target="_blank" style="color: #0a0a0a; text-decoration: underline;">{sig['fuente_nombre']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_act:
                if can_create:
                    if st.button("Cargar", key=f"btn_sig_{idx}", use_container_width=True):
                        st.session_state.prefill_data = sig
                        st.success("Señal cargada. Ve a 'Registro de Nuevo Factor'.")
                        st.rerun()
                else:
                    st.button("Cargar", key=f"btn_sig_{idx}", use_container_width=True, disabled=True, help="Solo Diseñadores pueden precargar señales.")

    # =========================================================================
    # TAB 3: REGISTRO HISTÓRICO & TRAZABILIDAD
    # =========================================================================
    with tab_explorador:
        st.markdown("### Trazabilidad y Procedencia Documental")
        st.caption("Consulte enlaces directos, autores y fechas de cada factor incorporado al sistema.")

        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            filtro_cat = st.selectbox("Dimensión", ["Todas"] + [c.value for c in PESTELCategory], key="mon_fil_cat")
        with col_f2:
            filtro_tipo = st.selectbox("Naturaleza", ["Todos", "Riesgo", "Oportunidad"], key="mon_fil_tipo")
        with col_f3:
            busqueda = st.text_input("Buscar por término", placeholder="Ej. Yumbo, CVC, plástico, madera...", key="mon_busq")

        df = database.get_all_factors(categoria=filtro_cat, tipo=filtro_tipo, busqueda=busqueda)
        st.markdown(f"<span style='font-size: 13px; color: #737373;'>Factores registrados: <b>{len(df)}</b></span>", unsafe_allow_html=True)

        if not df.empty:
            for _, row in df.iterrows():
                with st.expander(f"[{row['codigo']}] {row['titulo']} — {row['categoria_pestel']} ({row['tipo']})"):
                    c_exp1, c_exp2 = st.columns([2, 1])
                    with c_exp1:
                        st.markdown("**Descripción del Fenómeno:**")
                        st.write(row["descripcion"])
                        st.markdown("**Impacto en Smurfit WestRock Yumbo:**")
                        st.markdown(f"<div style='background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 12px; font-size: 13px; color: #0a0a0a;'>{row['efecto_empresa']}</div>", unsafe_allow_html=True)
                    with c_exp2:
                        st.markdown("**Trazabilidad de la Fuente (RF-03):**")
                        st.markdown(f"- **Fuente:** {row['fuente_nombre']}")
                        st.markdown(f"- **Enlace oficial:** [{row['fuente_url']}]({row['fuente_url']})")
                        st.markdown(f"- **Confiabilidad:** {row['fuente_confiabilidad']}")
                        st.markdown(f"- **Fecha publicación:** {row['fecha_publicacion']}")
                        st.markdown(f"- **Fecha consulta:** {row['fecha_consulta']}")
                        st.markdown("---")
                        st.markdown(f"- **Probabilidad:** {row['probabilidad']}/5 | **Impacto:** {row['impacto']}/5")
                        st.markdown(f"- **Severidad:** **{row['puntuacion_severidad']}/25** ({row['urgencia']})")
                        st.markdown(f"- **Estado:** `{row['estado']}`")
        else:
            st.info("No se encontraron registros con los filtros seleccionados.")

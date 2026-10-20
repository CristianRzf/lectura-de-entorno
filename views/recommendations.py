"""
views/recommendations.py - Recomendaciones y Decisiones Estratégicas (RF-07).
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
import textwrap
import database
import models

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid">RF-07</span>
                    <span class="badge-pill-soft">Decisiones</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Recomendaciones Estratégicas
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Planes de acción gerenciales sustentados en la evidencia fáctica del entorno para Smurfit WestRock Yumbo.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">Plan de Acción</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    curr_role = st.session_state.get("current_role", "Usuario")
    can_manage_status = models.check_permission(curr_role, "manage_recommendation_status")
    can_create_rec = models.check_permission(curr_role, "create_recommendation")
    role_badge, pill_cls = models.get_role_badge(curr_role)

    df_rec = database.get_all_recommendaciones()
    df_factores = database.get_all_factors()

    # Métricas en Stat Blocks
    total_rec = len(df_rec)
    activas = len(df_rec[df_rec["estado"].isin(["Planificada", "En Ejecución"])])
    completadas = len(df_rec[df_rec["estado"] == "Completada"])
    altas = len(df_rec[df_rec["prioridad"] == "Alta"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Decisiones", total_rec)
    with m2:
        st.metric("Prioridad Alta", altas)
    with m3:
        st.metric("En Progreso", activas)
    with m4:
        st.metric("Completadas", completadas)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    tab_plan, tab_nueva = st.tabs([
        f"Plan de Acción ({total_rec})",
        "Formular Nueva Recomendación"
    ])

    # =========================================================================
    # TAB 1: PLAN DE ACCIÓN
    # =========================================================================
    with tab_plan:
        c_prio, c_est, c_area = st.columns(3)
        with c_prio:
            f_prio = st.selectbox("Prioridad", ["Todas", "Alta", "Media", "Baja"], key="rec_prio")
        with c_est:
            f_est = st.selectbox("Estado", ["Todos", "Planificada", "En Ejecución", "Completada"], key="rec_est")
        with c_area:
            areas = ["Todas"] + sorted(df_rec["area_responsable"].unique().tolist()) if not df_rec.empty else ["Todas"]
            f_area = st.selectbox("Área Responsable", areas, key="rec_area")

        df_show = df_rec.copy()
        if f_prio != "Todas":
            df_show = df_show[df_show["prioridad"] == f_prio]
        if f_est != "Todos":
            df_show = df_show[df_show["estado"] == f_est]
        if f_area != "Todas":
            df_show = df_show[df_show["area_responsable"] == f_area]

        if not df_show.empty:
            for idx, r in df_show.iterrows():
                is_high_prio = r["prioridad"] == "Alta"
                prio_pill = "badge-pill-destructive" if is_high_prio else "badge-pill-soft"
                est_pill = "badge-pill-solid" if r["estado"] == "Completada" else "badge-pill-soft"

                card_html = textwrap.dedent(f"""<div class="blueprint-card" style="margin-bottom: 14px;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 6px;">
<span class="badge-pill-solid">{r['codigo_recomendacion']}</span>
<span class="{prio_pill}">Prioridad {r['prioridad']}</span>
<span style="font-size: 12px; color: #737373;">Factor: <b>[{r.get('factor_codigo', '')}] {r.get('factor_titulo', '')}</b> ({r.get('categoria_pestel', '')})</span>
</div>
<div><span class="{est_pill}">{r['estado']}</span></div>
</div>
<h3 style="font-size: 16px; font-weight: 600; color: #0a0a0a; margin: 0 0 8px 0; letter-spacing: -0.4px;">{r['titulo']}</h3>
<div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 12px 14px; margin-bottom: 10px;">
<div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; color: #0a0a0a; margin-bottom: 3px;">Acción Estratégica para Smurfit WestRock:</div>
<div style="font-size: 13.5px; color: #171717; line-height: 1.45;">{r['accion_sugerida']}</div>
</div>
<div style="font-size: 13px; color: #737373; margin-bottom: 12px;"><b>Evidencia Fáctica Utilizada:</b> {r['evidencia']}</div>
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; font-size: 12px; color: #737373; border-top: 1px solid #e5e5e5; padding-top: 10px;">
<div>Área: <b style="color: #0a0a0a;">{r['area_responsable']}</b> &nbsp;|&nbsp; Plazo: <b style="color: #0a0a0a;">{r['plazo']}</b></div>
<div><span style="font-size: 11.5px; color: #737373;">Autor: <b>{r.get('autor_nombre', 'Comité Directivo')}</b> ({r.get('autor_rol', 'Decisor')})</span></div>
</div>
</div>""")
                st.markdown(card_html, unsafe_allow_html=True)

                col_st1, col_st2 = st.columns([3, 1])
                with col_st2:
                    if can_manage_status:
                        nuevo_estado = st.selectbox(
                            f"Estado {r['codigo_recomendacion']}",
                            ["Planificada", "En Ejecución", "Completada"],
                            index=["Planificada", "En Ejecución", "Completada"].index(r["estado"]),
                            key=f"rec_status_{r['id']}",
                            label_visibility="collapsed"
                        )
                        if nuevo_estado != r["estado"]:
                            database.update_recommendation_status(r["id"], nuevo_estado)
                            st.toast(f"Estado actualizado a {nuevo_estado}")
                            st.rerun()
                    else:
                        st.selectbox(
                            f"Estado {r['codigo_recomendacion']}",
                            [r["estado"]],
                            key=f"rec_status_{r['id']}",
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        st.caption("🔒 *Transición exclusiva para Decisores.*")
        else:
            st.info("No hay recomendaciones con los filtros activos.")

    # =========================================================================
    # TAB 2: NUEVA RECOMENDACIÓN
    # =========================================================================
    with tab_nueva:
        st.markdown("### Formulación de Decisión Gerencial")
        st.caption("Conecte una acción recomendada a la evidencia del entorno.")

        if not can_create_rec:
            st.markdown(f'''
            <div class="blueprint-card" style="margin-bottom: 16px; border-left: 3px solid #171717;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 600; color: #0a0a0a;">Acceso Restringido en Formulación Estratégica</span>
                    <span class="{pill_cls}">{role_badge}</span>
                </div>
                <p style="font-size: 13px; color: #737373; margin: 0; line-height: 1.45;">
                    La formulación de recomendaciones gerenciales y planes de acción está reservada para los roles de <b>Decisor</b> y <b>Diseñador</b>.
                    Con su rol activo (<b>{curr_role}</b>), puede consultar el avance de las decisiones en la pestaña <b>Plan de Acción</b>.
                    Para formular nuevas propuestas estratégicas, cambie a un rol directivo en el panel lateral.
                </p>
            </div>
            ''', unsafe_allow_html=True)
        elif df_factores.empty:
            st.warning("Debe registrar al menos un factor PESTEL antes de formular recomendaciones.")
        else:
            opciones_factores = {f"[{r['codigo']}] {r['titulo']} ({r['categoria_pestel']})": r['id'] for _, r in df_factores.iterrows()}
            selected_factor_label = st.selectbox("Factor Vinculado *", list(opciones_factores.keys()))
            factor_id = opciones_factores[selected_factor_label]
            factor_obj = database.get_factor_by_id(factor_id)

            with st.form("form_nueva_recomendacion"):
                titulo_rec = st.text_input(
                    "Título de la Recomendación *",
                    placeholder="Ej. Plan de acopio contingente de fibra maderable en el Valle"
                )

                evidencia_default = f"Factor {factor_obj['codigo']} reportado por {factor_obj['fuente_nombre']} el {factor_obj['fecha_publicacion']}." if factor_obj else ""
                evidencia = st.text_area(
                    "Evidencia de Respaldo (RF-07) *",
                    value=evidencia_default,
                    height=70
                )

                accion_sugerida = st.text_area(
                    "Acción Estratégica Sugerida *",
                    placeholder="Pasos operacionales, inversiones CAPEX o convenios...",
                    height=80
                )

                c1, c2, c3 = st.columns(3)
                with c1:
                    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"], index=0)
                with c2:
                    area = st.selectbox("Área Responsable", [
                        "Operaciones & Molinos Yumbo",
                        "Cadena de Suministro & Logística",
                        "División Forestal & Silvicultura",
                        "Comercial & Mercadeo de Empaques",
                        "Sostenibilidad & Gestión Ambiental",
                        "Jurídico & Asuntos Corporativos",
                        "Tecnología e Industria 4.0",
                        "Gerencia General"
                    ])
                with c3:
                    plazo = st.selectbox("Plazo de Implementación", [
                        "Inmediato (< 1 mes)",
                        "Corto Plazo (< 3 meses)",
                        "Mediano Plazo (3 - 6 meses)",
                        "Largo Plazo (> 1 año)"
                    ], index=1)

                btn_guardar_rec = st.form_submit_button("Guardar Recomendación", use_container_width=True)

                if btn_guardar_rec:
                    if not titulo_rec.strip() or not accion_sugerida.strip() or not evidencia.strip():
                        st.error("Todos los campos marcados con * son requeridos.")
                    else:
                        data_rec = {
                            "factor_id": factor_id,
                            "titulo": titulo_rec.strip(),
                            "accion_sugerida": accion_sugerida.strip(),
                            "evidencia": evidencia.strip(),
                            "prioridad": prioridad,
                            "area_responsable": area,
                            "plazo": plazo,
                            "estado": "Planificada",
                            "autor_rol": curr_role,
                            "autor_nombre": st.session_state.get("current_user_name", "Dr. Carlos Mendoza")
                        }
                        database.add_recommendation(data_rec)
                        st.success("Recomendación registrada.")
                        st.rerun()

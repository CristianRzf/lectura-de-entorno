"""
views/tracking.py - Seguimiento, Actualización y Evolución Histórica .
Estilizado bajo la especificación "clinical blueprint on frosted paper".
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import database
import models
from models import PESTELCategory, FactorType, UrgencyLevel, FactorStatus, PESTEL_META

def render():
    st.markdown("""
    <div class="blueprint-card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="badge-pill-solid"></span>
                    <span class="badge-pill-soft">Seguimiento</span>
                </div>
                <h1 style="margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.75px; color: #0a0a0a;">
                    Seguimiento y Evolución Histórica
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #737373;">
                    Registro de nuevas observaciones, actualización de parámetros y trazabilidad temporal del entorno.
                </p>
            </div>
            <div>
                <span class="badge-pill-outline">Línea de Tiempo</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_factores = database.get_all_factors()

    if df_factores.empty:
        st.warning("No hay factores registrados en el sistema.")
        return

    tab_bitacora, tab_edicion, tab_auditoria = st.tabs([
        "Bitácora y Línea de Tiempo",
        "Actualizar Factor Existente",
        "Auditoría Consolidada"
    ])

    # =========================================================================
    # TAB 1: BITÁCORA Y LÍNEA DE TIEMPO
    # =========================================================================
    with tab_bitacora:
        factor_map = {f"[{r['codigo']}] {r['titulo']} ({r['estado']})": r['id'] for _, r in df_factores.iterrows()}
        selected_key = st.selectbox("Seleccione el factor a consultar:", list(factor_map.keys()), key="track_sel")
        f_id = factor_map[selected_key]
        factor = database.get_factor_by_id(f_id)

        if factor:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Dimensión PESTEL", factor["categoria_pestel"])
            with c2:
                st.metric("Naturaleza", factor["tipo"])
            with c3:
                st.metric("Severidad", f"{factor['puntuacion_severidad']}/25")
            with c4:
                st.metric("Estado", factor["estado"])

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            curr_role = st.session_state.get("current_role", "Usuario")
            can_change_status = models.check_permission(curr_role, "change_factor_status")
            default_user = st.session_state.get("current_user_name", "Laura Gómez")

            with st.expander("Registrar Nueva Observación de Seguimiento", expanded=False):
                with st.form("form_nueva_obs"):
                    nueva_obs = st.text_area(
                        "Novedad u Observación del Entorno *",
                        placeholder="Ej. En reciente sesión ordinaria de la CVC se aprobaron medidas adicionales...",
                        height=80
                    )
                    c_user, c_cambio = st.columns(2)
                    with c_user:
                        usuario_obs = st.text_input("Analista Responsable", value=f"{default_user} ({curr_role})")
                    with c_cambio:
                        if can_change_status:
                            cambio_est = st.selectbox(
                                "Cambio de Estado Opcional",
                                ["Sin cambio", "En Monitoreo", "Activo / Crítico", "En Mitigación / Acción", "Mitigado / Capitalizado", "Cerrado / Descartado"],
                                index=0
                            )
                        else:
                            cambio_est = st.selectbox(
                                "Cambio de Estado Opcional",
                                ["Sin cambio"],
                                disabled=True,
                                help="El cambio de estado de factores está reservado para Decisores y Diseñadores."
                            )
                            st.caption("🔒 *Cambio de estado reservado para Decisores y Diseñadores.*")

                    btn_guardar_obs = st.form_submit_button("Guardar Entrada en Bitácora", use_container_width=True)

                    if btn_guardar_obs:
                        if not nueva_obs.strip():
                            st.error("Ingrese el texto de la observación.")
                        else:
                            database.add_history_entry(
                                factor_id=f_id,
                                observacion=nueva_obs.strip(),
                                usuario=usuario_obs.strip(),
                                cambio_estado=cambio_est if cambio_est != "Sin cambio" else None,
                                rol=curr_role
                            )
                            st.success("Observación guardada.")
                            st.rerun()

            st.markdown("#### Línea de Tiempo de Evolución")
            historial = database.get_factor_history(f_id)

            if historial:
                for entry in historial:
                    rol_val = entry.get('rol', 'Usuario')
                    tag_rol = f"<span class='badge-pill-solid' style='margin-left: 8px;'>{rol_val}</span>" if rol_val else ""
                    tag_estado = f"<span class='badge-pill-soft' style='margin-left: 8px;'>{entry['cambio_estado']}</span>" if entry.get('cambio_estado') else ""
                    st.markdown(f"""
                    <div style="border-left: 2px solid #e5e5e5; padding-left: 16px; margin-bottom: 16px;">
                        <div style="font-size: 12px; color: #737373; margin-bottom: 4px;">
                            {entry['fecha_registro']} · Usuario: <b>{entry['usuario']}</b> {tag_rol} {tag_estado}
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 14px; padding: 12px 14px; font-size: 13.5px; color: #0a0a0a; line-height: 1.4;">
                            {entry['observacion']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No se registran eventos en la bitácora.")

    # =========================================================================
    # TAB 2: ACTUALIZAR FACTOR
    # =========================================================================
    with tab_edicion:
        curr_role = st.session_state.get("current_role", "Usuario")
        can_edit_params = models.check_permission(curr_role, "edit_factor_params")
        can_change_status = models.check_permission(curr_role, "change_factor_status")
        default_user = st.session_state.get("current_user_name", "Ing. Sofía Ramírez")

        factor_edit_map = {f"[{r['codigo']}] {r['titulo']}": r['id'] for _, r in df_factores.iterrows()}
        sel_edit_key = st.selectbox("Factor a consultar o modificar:", list(factor_edit_map.keys()), key="edit_sel")
        f_edit_id = factor_edit_map[sel_edit_key]
        factor_to_edit = database.get_factor_by_id(f_edit_id)

        if not can_edit_params and not can_change_status:
            # Rol Usuario: Solo lectura
            st.markdown(f'''
            <div class="blueprint-card" style="margin-bottom: 16px; border-left: 3px solid #171717;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 600; color: #0a0a0a;">Modo Consulta</span>
                    <span class="badge-pill-soft">Rol: {curr_role}</span>
                </div>
                <p style="font-size: 13px; color: #737373; margin: 0; line-height: 1.45;">
                    La calibración técnica de factores (probabilidad/impacto) está reservada para <b>Diseñadores</b>, y la gobernanza de estado para <b>Decisores</b>.
                    Como <b>Usuario</b>, dispone de visualización de parámetros en modo solo lectura.
                </p>
            </div>
            ''', unsafe_allow_html=True)

        elif curr_role == models.UserRole.DECISOR.value:
            # Rol Decisor: Gobernanza de estado
            st.markdown(f'''
            <div class="blueprint-card" style="margin-bottom: 16px; border-left: 3px solid #0a0a0a;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 600; color: #0a0a0a;">Modo Decisor — Gestión de Estado Estratégico</span>
                    <span class="badge-pill-solid">Rol: Decisor</span>
                </div>
                <p style="font-size: 13px; color: #737373; margin: 0; line-height: 1.45;">
                    Como <b>Decisor</b>, puede redefinir el estado estratégico del factor (p. ej. marcar como Mitigado o En Acción) y documentar decisiones.
                    Los parámetros técnicos de calibración (probabilidad 1-5 e impacto 1-5) son preservados por el Diseñador.
                </p>
            </div>
            ''', unsafe_allow_html=True)

        if factor_to_edit:
            with st.form("form_editar_factor"):
                st.markdown(f"**Ficha del Factor:** `{factor_to_edit['codigo']}`")
                ed_titulo = st.text_input("Título", value=factor_to_edit["titulo"], disabled=not can_edit_params)

                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    cat_list = [c.value for c in PESTELCategory]
                    cat_idx = cat_list.index(factor_to_edit["categoria_pestel"]) if factor_to_edit["categoria_pestel"] in cat_list else 0
                    ed_cat = st.selectbox("Dimensión", cat_list, index=cat_idx, disabled=not can_edit_params)
                with ec2:
                    tipo_list = [t.value for t in FactorType]
                    tipo_idx = tipo_list.index(factor_to_edit["tipo"]) if factor_to_edit["tipo"] in tipo_list else 0
                    ed_tipo = st.selectbox("Tipo", tipo_list, index=tipo_idx, disabled=not can_edit_params)
                with ec3:
                    estado_list = [s.value for s in FactorStatus]
                    estado_idx = estado_list.index(factor_to_edit["estado"]) if factor_to_edit["estado"] in estado_list else 0
                    ed_estado = st.selectbox("Estado Operativo / Estratégico", estado_list, index=estado_idx, disabled=not can_change_status)

                ed_desc = st.text_area("Descripción", value=factor_to_edit["descripcion"], height=70, disabled=not can_edit_params)
                ed_efecto = st.text_area("Efecto en Smurfit WestRock Yumbo", value=factor_to_edit["efecto_empresa"], height=70, disabled=not can_edit_params)

                ep1, ep2, ep3 = st.columns(3)
                with ep1:
                    ed_prob = st.slider("Probabilidad (1 - 5)", 1, 5, int(factor_to_edit["probabilidad"]), key="ed_prob", disabled=not can_edit_params)
                with ep2:
                    ed_imp = st.slider("Impacto (1 - 5)", 1, 5, int(factor_to_edit["impacto"]), key="ed_imp", disabled=not can_edit_params)
                with ep3:
                    urg_list = [u.value for u in UrgencyLevel]
                    urg_idx = urg_list.index(factor_to_edit["urgencia"]) if factor_to_edit["urgencia"] in urg_list else 0
                    ed_urg = st.selectbox("Urgencia", urg_list, index=urg_idx, disabled=not can_edit_params)

                ef1, ef2 = st.columns(2)
                with ef1:
                    ed_fuente = st.text_input("Fuente", value=factor_to_edit["fuente_nombre"], disabled=not can_edit_params)
                with ef2:
                    ed_url = st.text_input("URL Fuente", value=factor_to_edit["fuente_url"], disabled=not can_edit_params)

                ed_motivo = st.text_input("Motivo de la Modificación / Decisión *", placeholder="Razón del cambio o dictamen gerencial...", disabled=not can_change_status)

                if can_edit_params or can_change_status:
                    btn_actualizar = st.form_submit_button("Actualizar y Guardar en Bitácora", use_container_width=True)
                else:
                    btn_actualizar = st.form_submit_button("Actualizar y Guardar en Bitácora", use_container_width=True, disabled=True)
                    st.caption("🔒 *Edición restringida para el rol Usuario.*")

                if btn_actualizar:
                    if not ed_titulo.strip() or not ed_desc.strip():
                        st.error("Campos requeridos incompletos.")
                    elif not ed_motivo.strip():
                        st.error("Debe ingresar el motivo de la modificación o decisión.")
                    else:
                        update_payload = {
                            "titulo": ed_titulo.strip(),
                            "categoria_pestel": ed_cat,
                            "tipo": ed_tipo,
                            "ambito": factor_to_edit.get("ambito", "Nacional"),
                            "descripcion": ed_desc.strip(),
                            "probabilidad": ed_prob if can_edit_params else factor_to_edit["probabilidad"],
                            "impacto": ed_imp if can_edit_params else factor_to_edit["impacto"],
                            "urgencia": ed_urg if can_edit_params else factor_to_edit["urgencia"],
                            "efecto_empresa": ed_efecto.strip(),
                            "fuente_nombre": ed_fuente.strip(),
                            "fuente_url": ed_url.strip(),
                            "fuente_confiabilidad": factor_to_edit.get("fuente_confiabilidad", "Alta"),
                            "fecha_publicacion": factor_to_edit.get("fecha_publicacion", ""),
                            "fecha_consulta": datetime.now().strftime("%Y-%m-%d"),
                            "estado": ed_estado
                        }
                        database.update_factor(
                            factor_id=f_edit_id,
                            data=update_payload,
                            observacion=ed_motivo.strip(),
                            usuario=f"{default_user} ({curr_role})",
                            rol=curr_role
                        )
                        st.success("Factor actualizado y registrado en bitácora.")
                        st.rerun()

    # =========================================================================
    # TAB 3: AUDITORÍA GLOBAL
    # =========================================================================
    with tab_auditoria:
        st.markdown("### Historial Consolidado de Modificaciones")
        conn = database.get_connection()
        query_audit = """
        SELECT h.id, f.codigo, f.titulo, f.categoria_pestel, h.fecha_registro, h.usuario, h.rol, h.observacion, h.cambio_estado
        FROM historial_seguimiento h
        JOIN factores f ON h.factor_id = f.id
        ORDER BY h.fecha_registro DESC
        """
        df_audit = pd.read_sql_query(query_audit, conn)
        conn.close()

        if not df_audit.empty:
            st.dataframe(
                df_audit.rename(columns={
                    "codigo": "Código",
                    "titulo": "Factor",
                    "categoria_pestel": "Dimensión",
                    "fecha_registro": "Fecha",
                    "usuario": "Usuario / Autor",
                    "rol": "Rol",
                    "observacion": "Observación",
                    "cambio_estado": "Estado Notificado"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Sin registros de auditoría.")

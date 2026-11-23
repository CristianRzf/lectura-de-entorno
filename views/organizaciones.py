"""
views/organizaciones.py - Gestión Transversal de Organizaciones Exportadoras (RF-01, RF-09).
Registro, consulta y parametrización de organizaciones productivas multisectoriales (ONU / GNU).
"""

import streamlit as st
import pandas as pd
import database
import models
from models import SectorType, RegionOrigen, check_permission


def render():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-pill-solid">DIRECTORIO PRODUCTIVO</span>
            <span class="badge-pill-soft">Sectores Exportadores</span>
            <span class="badge-pill-outline">RF-01 / RF-09</span>
        </div>
        <h1 style="font-size: 28px; font-weight: 700; letter-spacing: -0.8px; color: #0a0a0a; margin: 0 0 6px 0;">
            Gestión Transversal de Organizaciones Exportadoras
        </h1>
        <p style="font-size: 14px; color: #737373; margin: 0; line-height: 1.5;">
            Registro y administración de asociaciones campesinas, cooperativas y empresas de los sectores de 
            <b>granos secos</b> (café y cacao), <b>perecederos</b> (frutas refrigeradas), <b>agroindustria procesada</b> 
            y <b>manufactura artesanal</b> beneficiarias del programa de cooperación internacional.
        </p>
    </div>
    """, unsafe_allow_html=True)

    organizaciones = database.get_all_organizaciones()
    total_orgs = len(organizaciones)

    # Indicadores superiores
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Organizaciones", total_orgs)
    with k2:
        secos = sum(1 for o in organizaciones if o["sector"] == SectorType.GRANOS_SECOS.value)
        st.metric("Granos y Secos", secos, delta="Café / Cacao")
    with k3:
        perecederos = sum(1 for o in organizaciones if o["sector"] == SectorType.FRUTAS_PERECEDEROS.value)
        st.metric("Perecederos (Reefer)", perecederos, delta="Frutas / Frescos")
    with k4:
        otros = total_orgs - (secos + perecederos)
        st.metric("Agroindustria / Manuf.", otros, delta="Valor Agregado")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Permisos RBAC (RF-09)
    current_role = st.session_state.get("current_role", models.UserRole.USUARIO_OPERATIVO.value)
    puede_crear = check_permission(current_role, "crear_organizacion")

    tab_directorio, tab_registro = st.tabs(["Directorio de Organizaciones", "Registrar Nueva Organización"])

    with tab_directorio:
        # Filtros interactivos
        f_col1, f_col2, f_col3 = st.columns([3, 2, 2])
        with f_col1:
            buscar = st.text_input("Buscar por nombre, producto o municipio", placeholder="Ej. Cacao, Nariño, Popayán...")
        with f_col2:
            filtro_sector = st.selectbox(
                "Filtrar por Sector",
                options=["Todos los Sectores"] + [s.value for s in SectorType]
            )
        with f_col3:
            filtro_region = st.selectbox(
                "Filtrar por Región",
                options=["Todas las Regiones"] + [r.value for r in RegionOrigen]
            )

        # Aplicar filtros
        orgs_filtradas = organizaciones
        if buscar.strip():
            b = buscar.lower()
            orgs_filtradas = [
                o for o in orgs_filtradas
                if b in o["nombre"].lower() or b in o["producto_principal"].lower() or (o["municipio"] and b in o["municipio"].lower())
            ]
        if filtro_sector != "Todos los Sectores":
            orgs_filtradas = [o for o in orgs_filtradas if o["sector"] == filtro_sector]
        if filtro_region != "Todas las Regiones":
            orgs_filtradas = [o for o in orgs_filtradas if o["region_origen"] == filtro_region]

        st.caption(f"Mostrando {len(orgs_filtradas)} de {total_orgs} organizaciones registradas.")

        if orgs_filtradas:
            df_org = pd.DataFrame(orgs_filtradas)
            cols_show = ["id", "nombre", "sector", "producto_principal", "region_origen", "municipio", "contacto", "email"]
            df_table = df_org[cols_show].copy()
            df_table.columns = ["ID", "Razón Social / Organización", "Sector", "Producto Principal", "Región", "Municipio", "Contacto", "Correo Electrónico"]
            st.dataframe(df_table, use_container_width=True, hide_index=True)
        else:
            st.info("No se encontraron organizaciones que coincidan con los criterios de búsqueda.")

    with tab_registro:
        if not puede_crear:
            st.warning(
                f"Acceso Restringido: El rol activo actual ('{current_role}') no tiene privilegios para matricular nuevas organizaciones. "
                "Esta función está reservada para el rol de 'Diseñador/Administrador'. Cambie de perfil en la barra lateral izquierda."
            )
        else:
            st.markdown("""
            <div style="font-size: 14px; color: #525252; margin-bottom: 14px;">
                Ingrese los datos de la organización productiva para incorporarla inmediatamente al motor de simulación logística.
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_nueva_org", clear_on_submit=True):
                r1_c1, r1_c2 = st.columns([3, 2])
                with r1_c1:
                    nombre_org = st.text_input("Nombre / Razón Social de la Organización *", placeholder="Ej. Cooperativa Agropecuaria del Macizo")
                with r1_c2:
                    nit_org = st.text_input("NIT / Identificación Tributaria", placeholder="Ej. 900.123.456-7")

                r2_c1, r2_c2 = st.columns(2)
                with r2_c1:
                    sector_org = st.selectbox("Sector Productivo *", options=[s.value for s in SectorType])
                with r2_c2:
                    producto_org = st.text_input("Producto Principal de Exportación *", placeholder="Ej. Café Arábica Lavado Especial")

                r3_c1, r3_c2 = st.columns(2)
                with r3_c1:
                    region_org = st.selectbox("Región / Departamento de Origen *", options=[r.value for r in RegionOrigen])
                with r3_c2:
                    municipio_org = st.text_input("Municipio / Sede Operativa *", placeholder="Ej. Popayán, Pasto, Tumaco")

                r4_c1, r4_c2 = st.columns(2)
                with r4_c1:
                    contacto_org = st.text_input("Nombre de Contacto / Representante Legal", placeholder="Ej. Ing. Laura Gómez")
                with r4_c2:
                    email_org = st.text_input("Correo Electrónico Corporativo", placeholder="contacto@cooperativa.org")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                btn_crear_org = st.form_submit_button("Guardar Organización en el Directorio", use_container_width=True)

                if btn_crear_org:
                    if not nombre_org.strip() or not producto_org.strip() or not municipio_org.strip():
                        st.error("Por favor complete los campos obligatorios marcados con (*).")
                    else:
                        new_id = database.insert_organizacion(
                            nombre=nombre_org,
                            nit=nit_org,
                            sector=sector_org,
                            producto_principal=producto_org,
                            region_origen=region_org,
                            municipio=municipio_org,
                            contacto=contacto_org,
                            email=email_org
                        )
                        database.log_auditoria(
                            usuario=st.session_state.get("current_user_name", "Admin"),
                            rol=current_role,
                            accion="CREAR_ORGANIZACION",
                            detalle=f"Registro de organización #{new_id}: {nombre_org} ({sector_org} en {region_org})."
                        )
                        st.success(f"Organización '{nombre_org}' registrada exitosamente con ID #{new_id}. Ahora está habilitada en el simulador de despacho.")
                        st.rerun()

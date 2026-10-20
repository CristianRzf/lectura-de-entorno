"""
views/login.py - Vista de Inicio de Sesión y Autenticación Segura.
Estilizado bajo la especificación "clinical blueprint on frosted paper" (shadcn/ui aesthetic).
"""
import streamlit as st
import database
import auth

def render():
    st.markdown("""
    <div style="max-width: 680px; margin: 48px auto 32px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <span class="badge-pill-solid">Smurfit WestRock</span>
            <span class="badge-pill-soft">Planta Yumbo · Valle del Cauca</span>
            <span class="badge-pill-outline">Seguridad</span>
        </div>
        <h1 style="font-size: 32px; font-weight: 600; letter-spacing: -0.9px; color: #0a0a0a; margin: 0 0 14px 0;">
            Control de Acceso y Gestión de Roles
        </h1>
        <p style="font-size: 14px; color: #737373; line-height: 1.55; margin: 0 auto; max-width: 540px;">
            Inicie sesión con sus credenciales institucionales. El sistema restringirá las pantallas, herramientas y facultades de edición según el rol asignado (<b>Usuarios</b>, <b>Decisores</b> o <b>Diseñadores</b>).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Contenedor central de Login
    col_l, col_center, col_r = st.columns([1, 4, 1])

    with col_center:
        st.markdown("""
        <div class="blueprint-card" style="padding: 32px 36px; margin-bottom: 28px;">
            <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px; margin-bottom: 4px;">
                Autenticación Institucional
            </div>
            <p style="font-size: 13px; color: #737373; margin: 0 0 24px 0;">
                Ingrese su correo electrónico y contraseña corporativa.
            </p>
        """, unsafe_allow_html=True)

        # Variables de precarga si se presionó un acceso rápido
        if "login_prefill_email" not in st.session_state:
            st.session_state.login_prefill_email = ""
        if "login_prefill_pwd" not in st.session_state:
            st.session_state.login_prefill_pwd = ""

        with st.form("form_login_auth", clear_on_submit=False):
            email_val = st.text_input(
                "Correo Electrónico Corporativo *",
                value=st.session_state.login_prefill_email,
                placeholder="ejemplo@smurfitwestrock.com"
            )
            pwd_val = st.text_input(
                "Contraseña *",
                value=st.session_state.login_prefill_pwd,
                type="password",
                placeholder="••••••••••••"
            )

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            btn_login = st.form_submit_button("Iniciar Sesión Segura", use_container_width=True)

            if btn_login:
                if not email_val.strip() or not pwd_val.strip():
                    st.error("Por favor complete todos los campos de autenticación.")
                else:
                    conn = database.get_connection()
                    user, err_msg = auth.authenticate_user(conn, email_val.strip(), pwd_val.strip())
                    conn.close()

                    if err_msg:
                        st.error(f"Error de acceso: {err_msg}")
                    elif user:
                        auth.login(user)
                        st.session_state.login_prefill_email = ""
                        st.session_state.login_prefill_pwd = ""
                        st.success(f"¡Bienvenido(a), {user['nombre']}! Accediendo como {user['rol']}...")
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
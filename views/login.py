"""
views/login.py - Vista de Inicio de Sesión y Autenticación Segura (RF-10).
Estilizado bajo la especificación "clinical blueprint on frosted paper" (shadcn/ui aesthetic).
"""

import streamlit as st
import database
import auth
from models import ROLE_CONFIG

def render():
    st.markdown("""
    <div style="max-width: 680px; margin: 30px auto 16px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span class="badge-pill-solid">Smurfit WestRock</span>
            <span class="badge-pill-soft">Planta Yumbo · Valle del Cauca</span>
            <span class="badge-pill-outline">RF-10: Seguridad</span>
        </div>
        <h1 style="font-size: 32px; font-weight: 600; letter-spacing: -0.9px; color: #0a0a0a; margin: 0 0 8px 0;">
            Control de Acceso y Gestión de Roles
        </h1>
        <p style="font-size: 14px; color: #737373; line-height: 1.45; margin: 0 auto; max-width: 540px;">
            Inicie sesión con sus credenciales institucionales. El sistema restringirá las pantallas, herramientas y facultades de edición según el rol asignado (<b>Usuarios</b>, <b>Decisores</b> o <b>Diseñadores</b>).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Contenedor central de Login
    col_l, col_center, col_r = st.columns([1, 4, 1])

    with col_center:
        st.markdown("""
        <div class="blueprint-card" style="padding: 28px 32px; margin-bottom: 20px;">
            <div style="font-size: 16px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.4px; margin-bottom: 4px;">
                Autenticación Institucional
            </div>
            <p style="font-size: 13px; color: #737373; margin: 0 0 20px 0;">
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

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
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

        # Accesos Rápidos para Evaluación del Prototipo
        st.markdown("""
        <div class="blueprint-card" style="padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 13.5px; font-weight: 600; color: #0a0a0a;">
                    Accesos Rápidos de Prueba (Prototipo / Evaluación)
                </span>
                <span class="badge-pill-soft">3 Perfiles Semilla</span>
            </div>
            <p style="font-size: 12.5px; color: #737373; margin: 0 0 14px 0; line-height: 1.4;">
                Seleccione un perfil institucional para evaluar la separación de funciones y los permisos diferenciados:
            </p>
        """, unsafe_allow_html=True)

        qc1, qc2, qc3 = st.columns(3)

        with qc1:
            st.markdown("""
            <div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 10px 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span class="badge-pill-solid">Diseñador</span>
                </div>
                <div style="font-size: 12px; font-weight: 600; color: #0a0a0a;">Ing. Sofía Ramírez</div>
                <div style="font-size: 11px; color: #737373;">Inteligencia & PESTEL</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Cargar Diseñador", key="demo_dis", use_container_width=True):
                st.session_state.login_prefill_email = "disenador@smurfitwestrock.com"
                st.session_state.login_prefill_pwd = "Disenador2026*"
                st.rerun()

        with qc2:
            st.markdown("""
            <div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 10px 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span class="badge-pill-solid">Decisor</span>
                </div>
                <div style="font-size: 12px; font-weight: 600; color: #0a0a0a;">Dr. Carlos Mendoza</div>
                <div style="font-size: 11px; color: #737373;">Gerencia & Estrategia</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Cargar Decisor", key="demo_dec", use_container_width=True):
                st.session_state.login_prefill_email = "decisor@smurfitwestrock.com"
                st.session_state.login_prefill_pwd = "Decisor2026*"
                st.rerun()

        with qc3:
            st.markdown("""
            <div style="background: #fafafa; border: 1px solid #e5e5e5; border-radius: 14px; padding: 10px 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span class="badge-pill-soft">Usuario</span>
                </div>
                <div style="font-size: 12px; font-weight: 600; color: #0a0a0a;">Laura Gómez</div>
                <div style="font-size: 11px; color: #737373;">Monitoreo Operativo</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Cargar Usuario", key="demo_usr", use_container_width=True):
                st.session_state.login_prefill_email = "usuario@smurfitwestrock.com"
                st.session_state.login_prefill_pwd = "Usuario2026*"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Ficha de Arquitectura de Seguridad y Escalabilidad
        with st.expander("🛡️ Arquitectura de Seguridad & Escalabilidad a Supabase"):
            st.markdown("""
            **Mecanismos de Protección Implementados:**
            1. **Hashing Criptográfico Estándar:** Las contraseñas nunca se almacenan en texto claro. Se procesan con `PBKDF2-HMAC-SHA256` utilizando 100.000 iteraciones y una sal criptográfica independiente de 16 bytes generada por `secrets.token_bytes()`.
            2. **Protección contra Fuerza Bruta:** Registro automático de `intentos_fallidos`. Al alcanzar 5 intentos erróneos, la cuenta se bloquea por 5 minutos mediante una marca temporal `bloqueado_hasta`.
            3. **Comparación en Tiempo Constante:** Verificación mediante `secrets.compare_digest()` para mitigar vulnerabilidades de canal lateral (timing attacks).
            4. **Compatibilidad Nativa con Supabase / PostgreSQL:** La tabla `usuarios` y los esquemas de factores y decisiones emplean tipos y restricciones compatibles 1:1 con PostgreSQL y Row Level Security (RLS) en Supabase.
            """)

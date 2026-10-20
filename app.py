"""
app.py - Aplicación Web de Lectura del Entorno PESTEL para Smurfit WestRock Colombia.
Diseñada con la especificación de interfaz "clinical blueprint on frosted paper" (shadcn/ui aesthetic).
Sin emojis, con tipografía neutra y soporte íntegro para controles de navegación y desplegables.
"""

import streamlit as st
import database
import models
import auth
import views.home as home_view
import views.monitor as monitor_view
import views.pestel_analysis as pestel_view
import views.risk_opportunity as risk_view
import views.recommendations as rec_view
import views.tracking as tracking_view
import views.reports as reports_view

# Configuración global de página (sin emojis)
st.set_page_config(
    page_title="Lectura del Entorno PESTEL | Smurfit WestRock Colombia",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos SQLite con datos semilla de Smurfit WestRock si es nueva
database.init_db(seed_if_empty=True)

# Control de Acceso y Verificación de Autenticación (RF-10)
if not auth.is_authenticated():
    import views.login as login_view
    login_view.render()
    st.stop()

# Usuario autenticado en sesión
current_user = auth.get_current_user()
active_role = current_user["rol"]
st.session_state.current_role = active_role
st.session_state.current_user_name = current_user["nombre"]
st.session_state.current_user_cargo = current_user["cargo"]

# Inyección de estilos CSS - "Clinical blueprint on frosted paper"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --color-canvas: #f5f5f5;
        --color-paper: #ffffff;
        --color-surface-alt: #fafafa;
        --color-ink: #0a0a0a;
        --color-ink-soft: #171717;
        --color-mid-gray: #737373;
        --color-hairline: #e5e5e5;
        --color-ember: #e7000b;
        --font-geist: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Fondo general Canvas */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f5f5f5 !important;
        color: #0a0a0a !important;
        font-family: var(--font-geist) !important;
    }

    header[data-testid="stHeader"] {
        background-color: #f5f5f5 !important;
    }

    /* Sidebar Surface Alt (#fafafa) */
    [data-testid="stSidebar"] {
        background-color: #fafafa !important;
        border-right: 1px solid #e5e5e5 !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #0a0a0a !important;
        font-family: var(--font-geist) !important;
    }

    /* PROTECCIÓN DE ICONOS DE STREAMLIT (Material Symbols para botones y flechas de desplegables) */
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stSidebarCollapseButton"] span,
    button[data-testid="stSidebarCollapseButton"] *,
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        font-style: normal !important;
        font-weight: normal !important;
        letter-spacing: normal !important;
        line-height: 1 !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }

    /* Tipografía Display y Headings con tight letter-spacing */
    h1 {
        font-family: var(--font-geist) !important;
        font-size: 32px !important;
        font-weight: 600 !important;
        letter-spacing: -0.9px !important;
        line-height: 1.15 !important;
        color: #0a0a0a !important;
    }

    h2 {
        font-family: var(--font-geist) !important;
        font-size: 24px !important;
        font-weight: 600 !important;
        letter-spacing: -0.7px !important;
        line-height: 1.25 !important;
        color: #0a0a0a !important;
    }

    h3 {
        font-family: var(--font-geist) !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
        line-height: 1.35 !important;
        color: #0a0a0a !important;
    }

    h4, h5, h6 {
        font-family: var(--font-geist) !important;
        font-weight: 600 !important;
        color: #171717 !important;
    }

    p, label {
        font-family: var(--font-geist) !important;
        font-size: 14px !important;
        color: #737373;
        line-height: 1.43 !important;
    }

    /* Cards: 24px radius, hairline border #e5e5e5, subtle shadow */
    .blueprint-card {
        background: #ffffff;
        border-radius: 24px;
        border: 1px solid #e5e5e5;
        box-shadow: 0 0 0 1px rgba(23, 23, 23, 0.05), 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px -1px rgba(0, 0, 0, 0.08);
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Stat Blocks / Métricas Streamlit */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border-radius: 24px !important;
        border: 1px solid #e5e5e5 !important;
        box-shadow: 0 0 0 1px rgba(23, 23, 23, 0.05), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        padding: 16px 20px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: 600 !important;
        color: #0a0a0a !important;
        letter-spacing: -0.75px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
        color: #737373 !important;
    }

    /* Primary Filled Buttons: #0a0a0a fill, #fafafa text, 18px radius */
    .stButton > button {
        background-color: #0a0a0a !important;
        color: #fafafa !important;
        border: none !important;
        border-radius: 18px !important;
        font-family: var(--font-geist) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 6px 16px !important;
        height: 38px !important;
        transition: opacity 0.15s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        opacity: 0.88 !important;
    }

    /* Download Button: Outline variant #ffffff with hairline border #e5e5e5 */
    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #0a0a0a !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 18px !important;
        font-family: var(--font-geist) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        height: 38px !important;
        box-shadow: none !important;
        transition: background-color 0.15s ease !important;
    }

    .stDownloadButton > button:hover {
        background-color: #f5f5f5 !important;
        border-color: #737373 !important;
    }

    /* Input Fields: #f5f5f5 background, 18px radius, border hairline on focus */
    input[type="text"], input[type="date"], textarea, [data-baseweb="select"] > div {
        background-color: #f5f5f5 !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 18px !important;
        color: #0a0a0a !important;
        font-family: var(--font-geist) !important;
        font-size: 14px !important;
    }

    input:focus, textarea:focus {
        border-color: #0a0a0a !important;
        box-shadow: 0 0 0 1px #0a0a0a !important;
    }

    /* Tabs minimalistas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e5e5e5;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 18px 18px 0 0 !important;
        color: #737373 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
    }

    .stTabs [aria-selected="true"] {
        color: #0a0a0a !important;
        border-bottom: 2px solid #0a0a0a !important;
    }

    /* Expanders: tarjeta limpia de 18px con ícono y texto perfectamente alineados */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 18px !important;
        box-shadow: none !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] summary {
        padding: 10px 14px !important;
        color: #0a0a0a !important;
        font-family: var(--font-geist) !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    [data-testid="stExpander"] summary p {
        color: #0a0a0a !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    /* Badges Pill */
    .badge-pill-solid {
        background: #171717;
        color: #fafafa;
        border-radius: 18px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
    }

    .badge-pill-soft {
        background: #f5f5f5;
        color: #171717;
        border: 1px solid #e5e5e5;
        border-radius: 18px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
    }

    .badge-pill-outline {
        background: transparent;
        color: #0a0a0a;
        border: 1px solid #e5e5e5;
        border-radius: 18px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
    }

    .badge-pill-destructive {
        background: #ffffff;
        color: #e7000b;
        border: 1px solid rgba(231, 0, 11, 0.3);
        border-radius: 18px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR SURFACE ALT (#fafafa) -----------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #e5e5e5; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge-pill-solid">SW</span>
            <span style="font-size: 14px; font-weight: 600; color: #0a0a0a; letter-spacing: -0.3px;">
                Smurfit WestRock
            </span>
        </div>
        <div style="font-size: 12px; color: #737373; margin-left: 2px;">
            Planta Industrial Yumbo · PESTEL
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- SESIÓN AUTENTICADA (RF-10) -----------------
    st.markdown('''
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: #737373; font-weight: 600; margin-bottom: 6px;">
        Sesión Autenticada · RF-10
    </div>
    ''', unsafe_allow_html=True)

    role_meta = models.ROLE_CONFIG.get(active_role, models.ROLE_CONFIG[models.UserRole.USUARIO.value])

    st.markdown(f'''
    <div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 18px; padding: 12px 14px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 13px; font-weight: 600; color: #0a0a0a;">{current_user['nombre']}</span>
            <span class="{role_meta['pill_class']}">{role_meta['badge']}</span>
        </div>
        <div style="font-size: 11px; color: #737373; margin-bottom: 4px; line-height: 1.3;">
            {current_user['cargo']}
        </div>
        <div style="font-size: 10.5px; color: #8c8c8c; font-family: monospace; margin-bottom: 8px;">
            {current_user['email']}
        </div>
        <div style="font-size: 11px; color: #171717; line-height: 1.35; border-top: 1px solid #f0f0f0; padding-top: 6px;">
            {role_meta['description']}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("Cerrar Sesión", key="btn_logout_sidebar", use_container_width=True):
        auth.logout()

    # Indicadores rápidos del sidebar
    kpis = database.get_kpis_summary()
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 18px; padding: 12px 14px; margin-bottom: 16px;">
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: #737373; font-weight: 600; margin-bottom: 8px;">
            Vigilancia del Entorno
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
            <span style="color: #737373;">Factores:</span>
            <span style="font-weight: 600; color: #0a0a0a;">{kpis['total_factores']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
            <span style="color: #737373;">Riesgos Críticos:</span>
            <span style="font-weight: 600; color: #e7000b;">{kpis['riesgos_criticos']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
            <span style="color: #737373;">Oportunidades:</span>
            <span style="font-weight: 600; color: #0a0a0a;">{kpis['oportunidades_estrategicas']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <span style="color: #737373;">Decisiones:</span>
            <span style="font-weight: 600; color: #0a0a0a;">{kpis['recomendaciones_activas']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Definición de páginas dinámicas según el Rol Autenticado (RF-10)
if active_role == models.UserRole.DISENADOR.value:
    # Rol Diseñador: Acceso completo incluyendo Captura del Entorno y Calibración
    pages = {
        "Tablero Estratégico": [
            st.Page(home_view.render, title="Inicio Ejecutivo", url_path="inicio", default=True),
            st.Page(monitor_view.render, title="Monitor del Entorno", url_path="monitor"),
            st.Page(pestel_view.render, title="Análisis PESTEL", url_path="analisis-pestel"),
            st.Page(risk_view.render, title="Matriz de Riesgos", url_path="matriz-riesgos"),
        ],
        "Toma de Decisiones": [
            st.Page(rec_view.render, title="Recomendaciones", url_path="recomendaciones"),
            st.Page(tracking_view.render, title="Seguimiento Histórico", url_path="seguimiento-historico"),
            st.Page(reports_view.render, title="Generador de Informes", url_path="generador-informes"),
        ]
    }
elif active_role == models.UserRole.DECISOR.value:
    # Rol Decisor: Enfoque de alta gerencia, gobernanza de decisiones y mitigación
    pages = {
        "Tablero Estratégico": [
            st.Page(home_view.render, title="Inicio Ejecutivo", url_path="inicio", default=True),
            st.Page(pestel_view.render, title="Análisis PESTEL", url_path="analisis-pestel"),
            st.Page(risk_view.render, title="Matriz de Riesgos", url_path="matriz-riesgos"),
        ],
        "Gobernanza & Decisiones": [
            st.Page(rec_view.render, title="Recomendaciones Estratégicas", url_path="recomendaciones"),
            st.Page(tracking_view.render, title="Seguimiento de Factores", url_path="seguimiento-historico"),
            st.Page(reports_view.render, title="Generador de Informes", url_path="generador-informes"),
        ]
    }
else:
    # Rol Usuario: Consulta diagnóstica, análisis de matrices y bitácora de novedades
    pages = {
        "Tablero de Consulta": [
            st.Page(home_view.render, title="Inicio Ejecutivo", url_path="inicio", default=True),
            st.Page(pestel_view.render, title="Análisis PESTEL", url_path="analisis-pestel"),
            st.Page(risk_view.render, title="Matriz de Riesgos", url_path="matriz-riesgos"),
        ],
        "Auditoría & Informes": [
            st.Page(tracking_view.render, title="Bitácora de Seguimiento", url_path="seguimiento-historico"),
            st.Page(reports_view.render, title="Descarga de Informes", url_path="generador-informes"),
        ]
    }

nav = st.navigation(pages)

# Sección inferior del sidebar
with st.sidebar:
    st.markdown("<hr style='border: none; border-top: 1px solid #e5e5e5; margin: 18px 0 12px 0;'>", unsafe_allow_html=True)

    with st.expander("Matriz de Permisos (RF-10)"):
        st.markdown('''
        **Gobernanza de Roles:**
        - **Diseñador:** Modelado PESTEL, registro de nuevos factores, calibración de probabilidad/impacto y reseteo de datos.
        - **Decisor:** Formulación/aprobación de recomendaciones, planes de acción y gobernanza de estado de factores.
        - **Usuario:** Visualización diagnóstica, consulta de trazabilidad y registro de observaciones en bitácora.
        ''')

    with st.expander("Restablecer Datos Semilla"):
        st.caption("Restaura la base de datos a sus valores iniciales con los 18 factores de Smurfit WestRock Yumbo.")
        can_reset = models.check_permission(st.session_state.current_role, "reset_database")
        if can_reset:
            if st.button("Restablecer Base de Datos", use_container_width=True):
                database.reset_db_to_seed()
                st.success("Base de datos restablecida.")
                st.rerun()
        else:
            st.button("Restablecer Base de Datos", use_container_width=True, disabled=True, help="Operación restringida: Solo el rol Diseñador puede restablecer la base de datos.")
            st.caption("🔒 *Acción reservada para el rol Diseñador.*")

    st.markdown("""
    <div style="font-size: 11px; color: #737373; line-height: 1.4; padding-top: 6px;">
        Smurfit WestRock Colombia<br>
        Carrera 1 # 15-05, Yumbo, Valle
    </div>
    """, unsafe_allow_html=True)

# Ejecución de la página seleccionada
nav.run()

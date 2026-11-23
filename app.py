"""
app.py - Punto de Entrada Principal
Plataforma Web Transversal de Inteligencia Logística y Despacho Portuario (ONU / GNU Colombia).
Sistema de optimización de salida marítima (Buenaventura vs. Cartagena) para organizaciones exportadoras.
"""

import streamlit as st
import database
import models
from models import UserRole, ROLE_CONFIG, check_permission
from views import simulador, contingencias, organizaciones, reportes


# =============================================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Inteligencia Logística y Despacho Portuario | ONU - GNU",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos SQLite (logistica_transversal.db)
database.init_db()


# =============================================================================
# SISTEMA DE DISEÑO Y CSS CORPORATIVO
# =============================================================================

st.markdown("""
<style>
    /* Importación tipográfica */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ------------------------------------------------------------------ */
    /* TOKENS DE DISEÑO                                                     */
    /* ------------------------------------------------------------------ */
    :root {
        --canvas:   #f8f9fa;
        --paper:    #ffffff;
        --surface:  #f1f3f5;
        --ink:      #0a0a0a;
        --ink-soft: #525252;
        --mid:      #737373;
        --hairline: #e5e5e5;
        --ember:    #e7000b;
        --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ------------------------------------------------------------------ */
    /* RESET GLOBAL — FONDO CLARO Y TINTA OSCURA EN TODO ELEMENTO          */
    /* ------------------------------------------------------------------ */
    html, body,
    [class*="css"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="block-container"],
    .main, .block-container,
    section[data-testid="stSidebar"] > div:first-child {
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        font-family: var(--font) !important;
    }

    /* Sidebar — fondo blanco con borde derecho sutil */
    [data-testid="stSidebar"] {
        background-color: var(--paper) !important;
        border-right: 1px solid var(--hairline) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--ink) !important;
        font-family: var(--font) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: var(--ink) !important;
    }

    /* ------------------------------------------------------------------ */
    /* MATERIAL ICONS — Excepciones de fuente para iconos de Streamlit     */
    /* ------------------------------------------------------------------ */
    /* Sin esto, la regla global font-family rompe el icono «keyboard_double_arrow_left» */
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    span[data-baseweb="icon"],
    [data-testid="stSidebar"] [data-testid="stIconMaterial"],
    [data-testid="stSidebar"] .material-symbols-rounded,
    button[kind="header"] span,
    button[data-testid="collapsedControl"] span,
    button[data-testid="expandedControl"] span {
        font-family: "Material Symbols Rounded", "Material Icons", "Material Icons Outlined", sans-serif !important;
        color: var(--ink) !important;
    }

    /* ------------------------------------------------------------------ */
    /* TIPOGRAFÍA GLOBAL                                                    */
    /* ------------------------------------------------------------------ */
    h1, h2, h3, h4, h5, h6 {
        color: var(--ink) !important;
        font-family: var(--font) !important;
        font-weight: 700 !important;
    }
    p, span, div, li, td, th {
        color: var(--ink) !important;
        font-family: var(--font) !important;
    }
    label, .stLabel > label {
        color: var(--ink-soft) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    small, .stCaption, caption {
        color: var(--mid) !important;
    }

    /* ------------------------------------------------------------------ */
    /* MÉTRICAS — NUNCA BLANCO SOBRE BLANCO                               */
    /* ------------------------------------------------------------------ */
    div[data-testid="stMetric"] {
        background-color: var(--paper) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] span {
        color: var(--ink-soft) !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] p,
    div[data-testid="stMetricValue"] span {
        color: var(--ink) !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] p,
    div[data-testid="stMetricDelta"] span {
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* ------------------------------------------------------------------ */
    /* TABS — TEXTO LEGIBLE EN MODO CLARO                                  */
    /* ------------------------------------------------------------------ */
    button[data-baseweb="tab"] {
        color: var(--mid) !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ink) !important;
        border-bottom: 2px solid var(--ink) !important;
    }
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span {
        color: inherit !important;
    }

    /* ------------------------------------------------------------------ */
    /* SELECTBOX / INPUTS / WIDGETS — FONDO CLARO ALTO CONTRASTE           */
    /* ------------------------------------------------------------------ */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: var(--paper) !important;
        color: var(--ink) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="select"] span {
        color: var(--ink) !important;
    }

    /* ------------------------------------------------------------------ */
    /* DATAFRAME / TABLA                                                    */
    /* ------------------------------------------------------------------ */
    .stDataFrame, iframe[title="st-aggrid"] {
        background-color: var(--paper) !important;
        color: var(--ink) !important;
    }
    [data-testid="stDataFrameResizable"] {
        background-color: var(--paper) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ------------------------------------------------------------------ */
    /* TARJETAS BLUEPRINT PERSONALIZADAS                                    */
    /* ------------------------------------------------------------------ */
    .blueprint-card {
        background: var(--paper);
        border: 1px solid var(--hairline);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .blueprint-card * {
        color: var(--ink);
    }

    /* ------------------------------------------------------------------ */
    /* BADGES / PILLS                                                       */
    /* ------------------------------------------------------------------ */
    .badge-pill-solid {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        display: inline-flex !important;
        align-items: center !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase !important;
    }
    .badge-pill-soft {
        background-color: #f1f3f5 !important;
        color: #171717 !important;
        border: 1px solid #d4d4d4 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    .badge-pill-outline {
        background-color: transparent !important;
        color: #525252 !important;
        border: 1px solid #d4d4d4 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    .badge-pill-destructive {
        background-color: #fee2e2 !important;
        color: #dc2626 !important;
        border: 1px solid #fca5a5 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        display: inline-flex !important;
        align-items: center !important;
        text-transform: uppercase !important;
    }

    /* ------------------------------------------------------------------ */
    /* BOTONES — NEGRO RELLENO, TEXTO BLANCO GARANTIZADO                   */
    /* ------------------------------------------------------------------ */
    .stButton > button {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 20px !important;
        transition: opacity 0.15s ease !important;
        font-family: var(--font) !important;
    }
    .stButton > button *,
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #ffffff !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    /* Botón de descarga — outline */
    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #0a0a0a !important;
        border: 1.5px solid #0a0a0a !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 8px 18px !important;
        font-family: var(--font) !important;
    }
    .stDownloadButton > button *,
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: #0a0a0a !important;
    }
    .stDownloadButton > button:hover {
        background-color: #f5f5f5 !important;
    }

    /* ------------------------------------------------------------------ */
    /* ALERTAS Y MENSAJES INFORMATIVOS                                      */
    /* ------------------------------------------------------------------ */
    div[data-testid="stAlert"] {
        background-color: var(--paper) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: var(--ink) !important;
    }

    /* ------------------------------------------------------------------ */
    /* LAYOUT Y ESPACIADO                                                   */
    /* ------------------------------------------------------------------ */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 1380px !important;
    }
</style>
""", unsafe_allow_html=True)



# =============================================================================
# GESTIÓN DE SESIÓN Y ROLES RBAC (RF-09)
# =============================================================================

if "current_role" not in st.session_state:
    st.session_state.current_role = UserRole.USUARIO_OPERATIVO.value

if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = "Operador de Logística"


# =============================================================================
# BARRA LATERAL (SIDEBAR): IDENTIDAD, CONTROL RBAC Y TRÁNSITO EN VIVO
# =============================================================================

with st.sidebar:
    # Membrete institucional
    st.markdown("""
    <div style="padding: 6px 0 16px 0; border-bottom: 1px solid #e5e5e5; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="background-color:#0a0a0a; color:#ffffff !important; font-size:11px; font-weight:700; padding:3px 10px; border-radius:9999px; display:inline-flex; align-items:center; letter-spacing:0.4px; text-transform:uppercase;">ONU / GNU</span>
            <span style="font-size: 13px; font-weight: 700; color: #0a0a0a !important; letter-spacing: -0.3px;">
                Cooperación Colombia
            </span>
        </div>
        <div style="font-size: 15px; font-weight: 700; color: #0a0a0a !important; line-height: 1.3;">
            Inteligencia Logística y Despacho Portuario
        </div>
        <div style="font-size: 12px; color: #737373 !important; margin-top: 4px;">
            Plataforma Transversal para Organizaciones Exportadoras
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Selector de Roles y Permisos (RBAC) (RF-09)
    st.markdown("""
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: #737373; font-weight: 700; margin-bottom: 6px;">
        Perfil y Control de Acceso (RBAC)
    </div>
    """, unsafe_allow_html=True)

    lista_roles = [r.value for r in UserRole]
    rol_seleccionado = st.selectbox(
        "Rol Activo en Sesión",
        options=lista_roles,
        index=lista_roles.index(st.session_state.current_role),
        label_visibility="collapsed"
    )

    if rol_seleccionado != st.session_state.current_role:
        st.session_state.current_role = rol_seleccionado
        # Ajustar nombre simbólico según el rol
        if rol_seleccionado == UserRole.ADMINISTRADOR.value:
            st.session_state.current_user_name = "Ing. Administrador / Diseñador"
        elif rol_seleccionado == UserRole.DECISOR.value:
            st.session_state.current_user_name = "Director de Operaciones & Logística"
        else:
            st.session_state.current_user_name = "Operador de Logística de Exportación"
        st.rerun()

    cfg_rol = ROLE_CONFIG[st.session_state.current_role]

    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 10px 12px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 12.5px; font-weight: 600; color: #0a0a0a;">{st.session_state.current_user_name}</span>
            <span class="badge-pill-soft">{cfg_rol['badge']}</span>
        </div>
        <p style="font-size: 11.5px; color: #525252; margin: 0; line-height: 1.35;">
            {cfg_rol['descripcion']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Monitor Rápido de Corredores en Tiempo Real (RF-05)
    st.markdown("""
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: #737373; font-weight: 700; margin-bottom: 6px;">
        Estado de Corredores Portuarios
    </div>
    """, unsafe_allow_html=True)

    cont_bva = database.get_ultima_contingencia_por_puerto(models.PuertoSalida.BUENAVENTURA.value)
    cont_ctg = database.get_ultima_contingencia_por_puerto(models.PuertoSalida.CARTAGENA.value)

    nb = cont_bva.get("nivel", "Operación Normal")
    nc = cont_ctg.get("nivel", "Operación Normal")
    pill_b = "badge-pill-destructive" if "Bloqueo" in nb else ("badge-pill-soft" if nb != "Operación Normal" else "badge-pill-outline")
    pill_c = "badge-pill-destructive" if "Bloqueo" in nc else ("badge-pill-soft" if nc != "Operación Normal" else "badge-pill-outline")

    st.markdown(f"""
    <div style="font-size: 12px; line-height: 1.6; margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span>Buenaventura (Pacífico):</span>
            <span class="{pill_b}">{nb}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>Cartagena (Caribe):</span>
            <span class="{pill_c}">{nc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Herramientas Administrativas
    if check_permission(st.session_state.current_role, "gestionar_sistema"):
        st.markdown("<hr style='border: none; border-top: 1px solid #e5e5e5; margin: 12px 0;'>", unsafe_allow_html=True)
        if st.button("Restablecer Datos Semilla (SQLite)", use_container_width=True):
            database.reset_db_seed()
            database.log_auditoria(
                usuario=st.session_state.current_user_name,
                rol=st.session_state.current_role,
                accion="RESET_DATABASE",
                detalle="Restablecimiento completo de la base de datos a su estado semilla."
            )
            st.success("Base de datos reinicializada con datos semilla.")
            st.rerun()

    # Footer
    st.markdown("""
    <div style="font-size: 11px; color: #a3a3a3; text-align: center; margin-top: 24px;">
        Cooperación Internacional ONU / GNU<br>
        Colombia · Versión 2.0 Transversal
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# NAVEGACIÓN PRINCIPAL ENTRE MÓDULOS
# =============================================================================

tabs_titulos = [
    "Simulador de Despacho",
    "Organizaciones Exportadoras",
    "Contingencias Viales & Puertos",
    "Bitácora e Informes"
]

tab_sim, tab_org, tab_cont, tab_rep = st.tabs(tabs_titulos)

with tab_sim:
    simulador.render()

with tab_org:
    organizaciones.render()

with tab_cont:
    contingencias.render()

with tab_rep:
    reportes.render()

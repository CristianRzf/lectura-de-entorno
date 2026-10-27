"""
auth.py - Sistema de Autenticación, Seguridad y Control de Acceso por Roles
Diseñado para SQLite con compatibilidad directa para migración a Supabase / PostgreSQL.

Incluye:
- Hashing criptográfico PBKDF2-HMAC-SHA256 (100.000 iteraciones + Salt de 16 bytes).
- Protección contra ataques de fuerza bruta: límite de 5 intentos fallidos y bloqueo temporal.
- Gestión de sesiones autenticadas en Streamlit (login, logout, perfil activo).
- Esquema de base de datos modular y semillas iniciales para los 3 roles:
  * Diseñador: Ing. Sofía Ramírez (disenador@organizacion.com)
  * Decisor:   Dr. Carlos Mendoza  (decisor@organizacion.com)
  * Usuario:   Laura Gómez         (usuario@organizacion.com)
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import streamlit as st

# Configuración de Seguridad
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
PBKDF2_ITERATIONS = 100_000

# =============================================================================
# FUNCIONES CRIPTOGRÁFICAS (PBKDF2-HMAC-SHA256 + SALT)
# =============================================================================

def hash_password(password: str, salt_bytes: Optional[bytes] = None) -> Tuple[str, str]:
    """
    Genera un hash criptográfico seguro usando PBKDF2-HMAC-SHA256 con 100.000 rondas.
    Retorna (hash_hex, salt_hex).
    """
    if salt_bytes is None:
        salt_bytes = secrets.token_bytes(16)
    
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        PBKDF2_ITERATIONS
    )
    return derived_key.hex(), salt_bytes.hex()

def verify_password(password: str, stored_hash: str, stored_salt_hex: str) -> bool:
    """
    Verifica una contraseña contra su hash y salt almacenados utilizando
    comparación de tiempo constante (secrets.compare_digest) para evitar ataques de temporización.
    """
    try:
        salt_bytes = bytes.fromhex(stored_salt_hex)
        check_hash, _ = hash_password(password, salt_bytes)
        return secrets.compare_digest(check_hash, stored_hash)
    except Exception:
        return False

# =============================================================================
# INICIALIZACIÓN DE TABLA DE USUARIOS Y SEMILLAS (SQLITE / SUPABASE-READY)
# =============================================================================

def init_users_table(conn: sqlite3.Connection):
    """
    Crea la tabla 'usuarios' con campos estandarizados compatibles con PostgreSQL / Supabase.
    """
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cargo TEXT NOT NULL,
        rol TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        intentos_fallidos INTEGER DEFAULT 0,
        bloqueado_hasta TEXT,
        ultimo_acceso TEXT,
        activo INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    conn.commit()
    seed_default_users(conn)

def seed_default_users(conn: sqlite3.Connection):
    """
    Puebla la tabla de usuarios con credenciales de prueba preconfiguradas
    para los 3 roles corporativos si la tabla está vacía.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]

    if count == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        default_users = [
            {
                "email": "disenador@organizacion.com",
                "nombre": "Ing. Sofía Ramírez",
                "cargo": "Especialista en Inteligencia Competitiva & PESTEL",
                "rol": "Diseñador",
                "password_plain": "Disenador2026*"
            },
            {
                "email": "decisor@organizacion.com",
                "nombre": "Dr. Carlos Mendoza",
                "cargo": "Director General de Estrategia",
                "rol": "Decisor",
                "password_plain": "Decisor2026*"
            },
            {
                "email": "usuario@organizacion.com",
                "nombre": "Laura Gómez",
                "cargo": "Analista de Monitoreo & Operaciones de Planta",
                "rol": "Usuario",
                "password_plain": "Usuario2026*"
            }
        ]

        for u in default_users:
            pwd_hash, salt_hex = hash_password(u["password_plain"])
            cursor.execute("""
            INSERT INTO usuarios (
                email, nombre, cargo, rol, password_hash, salt,
                intentos_fallidos, bloqueado_hasta, ultimo_acceso, activo, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, NULL, NULL, 1, ?, ?)
            """, (
                u["email"].lower(),
                u["nombre"],
                u["cargo"],
                u["rol"],
                pwd_hash,
                salt_hex,
                now_str,
                now_str
            ))

        conn.commit()

# =============================================================================
# CONSULTAS Y GESTIÓN DE ACCESO
# =============================================================================

def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    """Busca un usuario por su correo electrónico (búsqueda normalizada en minúsculas)."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE lower(email) = lower(?)", (email.strip(),))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def is_account_locked(bloqueado_hasta: Optional[str]) -> Tuple[bool, int]:
    """
    Determina si la cuenta está bloqueada temporalmente por intentos fallidos.
    Retorna (esta_bloqueada, segundos_restantes).
    """
    if not bloqueado_hasta:
        return False, 0
    try:
        lock_dt = datetime.strptime(bloqueado_hasta, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        if lock_dt > now:
            remaining = int((lock_dt - now).total_seconds())
            return True, remaining
    except Exception:
        pass
    return False, 0

def authenticate_user(conn: sqlite3.Connection, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Flujo completo de autenticación:
    1. Verifica existencia de usuario.
    2. Comprueba bloqueo temporal por intentos fallidos.
    3. Valida contraseña hasheada (PBKDF2).
    4. Si falla, incrementa contador y bloquea si excede MAX_FAILED_ATTEMPTS.
    5. Si tiene éxito, reinicia contador de fallos y actualiza último acceso.
    """
    clean_email = email.strip().lower()
    user = get_user_by_email(conn, clean_email)

    if not user:
        # Mitigación de timing attack: cálculo simulado con salt dummy
        hash_password("dummy_password_for_timing_mitigation")
        return None, "Correo electrónico o contraseña incorrectos."

    if not user.get("activo", 1):
        return None, "La cuenta se encuentra desactivada por el administrador."

    # Verificar si está bloqueada temporalmente
    locked, remaining_secs = is_account_locked(user.get("bloqueado_hasta"))
    if locked:
        mins = max(1, (remaining_secs + 59) // 60)
        return None, f"Cuenta bloqueada temporalmente por exceso de intentos fallidos. Intente nuevamente en {mins} minuto(s)."

    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Verificar contraseña
    is_valid = verify_password(password, user["password_hash"], user["salt"])

    if not is_valid:
        current_attempts = (user.get("intentos_fallidos") or 0) + 1
        
        if current_attempts >= MAX_FAILED_ATTEMPTS:
            lock_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            UPDATE usuarios SET
                intentos_fallidos = ?,
                bloqueado_hasta = ?,
                updated_at = ?
            WHERE id = ?
            """, (current_attempts, lock_until, now_str, user["id"]))
            conn.commit()
            return None, f"Ha superado el límite de {MAX_FAILED_ATTEMPTS} intentos fallidos. Su cuenta ha sido bloqueada temporalmente por {LOCKOUT_MINUTES} minutos."
        else:
            remaining = MAX_FAILED_ATTEMPTS - current_attempts
            cursor.execute("""
            UPDATE usuarios SET
                intentos_fallidos = ?,
                updated_at = ?
            WHERE id = ?
            """, (current_attempts, now_str, user["id"]))
            conn.commit()
            return None, f"Contraseña incorrecta. Le quedan {remaining} intento(s) antes del bloqueo temporal."

    # Éxito: resetear intentos y actualizar último acceso
    cursor.execute("""
    UPDATE usuarios SET
        intentos_fallidos = 0,
        bloqueado_hasta = NULL,
        ultimo_acceso = ?,
        updated_at = ?
    WHERE id = ?
    """, (now_str, now_str, user["id"]))
    conn.commit()

    # Refrescar datos
    user["intentos_fallidos"] = 0
    user["bloqueado_hasta"] = None
    user["ultimo_acceso"] = now_str
    return user, None

# =============================================================================
# MANEJO DE SESIÓN EN STREAMLIT
# =============================================================================

def login(user: Dict[str, Any]):
    """Registra la sesión autenticada en st.session_state."""
    st.session_state.authenticated = True
    st.session_state.current_user = {
        "id": user["id"],
        "email": user["email"],
        "nombre": user["nombre"],
        "cargo": user["cargo"],
        "rol": user["rol"]
    }
    st.session_state.current_role = user["rol"]
    st.session_state.current_user_name = user["nombre"]
    st.session_state.current_user_cargo = user["cargo"]

def logout():
    """Destruye la sesión autenticada en st.session_state y redirige al login."""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.current_user_name = None
    st.session_state.current_user_cargo = None
    if "app_role_selector" in st.session_state:
        del st.session_state["app_role_selector"]
    st.rerun()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Obtiene los datos del usuario en sesión."""
    return st.session_state.get("current_user", None)

def is_authenticated() -> bool:
    """Verifica si existe una sesión activa y autenticada."""
    return bool(st.session_state.get("authenticated", False) and st.session_state.get("current_user"))

"""
database.py - Capa de persistencia SQLite para la Plataforma de Inteligencia Logística (ONU / GNU).
Manejo de organizaciones exportadoras, contingencias viales/portuarias, simulaciones y auditoría.
Base de datos: logistica_transversal.db
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logistica_transversal.db")


def get_connection() -> sqlite3.Connection:
    """Crea y retorna una conexión a SQLite con row_factory habilitado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas necesarias e inserta datos semilla si la base está vacía."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabla de Organizaciones Exportadoras (RF-01)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nit TEXT,
        sector TEXT NOT NULL,
        producto_principal TEXT NOT NULL,
        region_origen TEXT NOT NULL,
        municipio TEXT,
        contacto TEXT,
        email TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Tabla de Contingencias Viales y Portuarias (RF-05)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contingencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puerto TEXT NOT NULL,
        corredor TEXT NOT NULL,
        nivel TEXT NOT NULL,
        fuente_oficial TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        activo INTEGER DEFAULT 1
    );
    """)

    # 3. Tabla de Simulaciones y Despachos (RF-08)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organizacion_id INTEGER,
        organizacion_nombre TEXT NOT NULL,
        sector TEXT NOT NULL,
        producto TEXT NOT NULL,
        region_origen TEXT NOT NULL,
        mercado_destino TEXT NOT NULL,
        toneladas REAL NOT NULL,
        trm REAL NOT NULL,
        tipo_carga TEXT NOT NULL,
        contenedores INTEGER NOT NULL,
        puerto_recomendado TEXT NOT NULL,
        costo_buenaventura_cop REAL NOT NULL,
        costo_cartagena_cop REAL NOT NULL,
        ahorro_cop REAL NOT NULL,
        costo_kg_optimo REAL NOT NULL,
        estado_buenaventura TEXT,
        estado_cartagena TEXT,
        detalles_json TEXT,
        usuario TEXT,
        fecha_simulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizacion_id) REFERENCES organizaciones(id)
    );
    """)

    # 4. Tabla de Auditoría y Trazabilidad (RF-09)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        rol TEXT NOT NULL,
        accion TEXT NOT NULL,
        detalle TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Verificar si ya existen organizaciones semilla
    cursor.execute("SELECT COUNT(*) AS total FROM organizaciones")
    count_orgs = cursor.fetchone()["total"]

    if count_orgs == 0:
        seed_data(conn)

    conn.close()


def seed_data(conn: sqlite3.Connection):
    """Inserta datos semilla reales con organizaciones colombianas y estado vial inicial."""
    cursor = conn.cursor()

    # Organizaciones reales vinculadas a programas de cooperación y desarrollo rural
    organizaciones_seed = [
        (
            "Cooperativa de Caficultores del Cauca (CAFICAUCA)",
            "891.500.234-1",
            "Granos y Secos",
            "Café Especial de Altura (Castillo / Colombia)",
            "Cauca",
            "Popayán",
            "Dra. Claudia Navia",
            "exportaciones@caficauca.org.co"
        ),
        (
            "Asociación de Productores de Cacao del Pacífico (ASOPROCAP)",
            "900.812.443-8",
            "Granos y Secos",
            "Cacao Fino de Aroma Fermentado y Seco",
            "Nariño",
            "Tumaco",
            "Ing. Hernán Quiñones",
            "gerencia@asoprocap-pacifico.org"
        ),
        (
            "Agroexportadora Hass Colombia S.A.S.",
            "901.320.119-4",
            "Frutas y Perecederos",
            "Aguacate Hass Calibre 16-22 Certificado GlobalG.A.P.",
            "Valle del Cauca",
            "Sevilla",
            "Mario Restrepo",
            "comercial@agroexportadorahass.com"
        ),
        (
            "Asociación de Fruticultores de Nariño (FRUTINARIÑO)",
            "900.450.781-2",
            "Frutas y Perecederos",
            "Gulupa y Uchuva Tipo Exportación en Canastilla",
            "Nariño",
            "La Unión",
            "Marta Lucía Enríquez",
            "contacto@frutinarino.org"
        ),
        (
            "Asociación de Paneleros Tradicionales del Cauca (ASOPANELA)",
            "817.003.882-6",
            "Agroindustria Procesada",
            "Panela Pulverizada Orgánica en Sachet y Granel",
            "Cauca",
            "Santander de Quilichao",
            "Jorge Eliécer Mina",
            "ventas@asopanelacauca.co"
        ),
        (
            "Cooperativa de Cacaoteros de San Vicente de Chucurí",
            "890.201.765-3",
            "Granos y Secos",
            "Nibs de Cacao Fino y Manteca de Cacao Artesanal",
            "Santander",
            "San Vicente de Chucurí",
            "Gustavo Rueda",
            "export@cacaosv.com.co"
        ),
        (
            "Asociación de Artesanas de la Paja Toquilla de Nariño",
            "900.672.311-0",
            "Manufactura y Artesanías",
            "Sombreros y Tejidos Artesanales Fina Fibra Natural",
            "Nariño",
            "Sandoná",
            "Rosa Elvira Cerón",
            "artesanias@sandonaexport.org"
        ),
        (
            "BioSnacks del Eje Cafetero",
            "901.554.908-1",
            "Agroindustria Procesada",
            "Snacks Liofilizados de Café y Frutas Exóticas",
            "Eje Cafetero",
            "Pereira",
            "Andrés Felipe Gómez",
            "comercio@biosnackscol.com"
        )
    ]

    cursor.executemany("""
    INSERT INTO organizaciones (nombre, nit, sector, producto_principal, region_origen, municipio, contacto, email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, organizaciones_seed)

    # Contingencias iniciales
    contingencias_seed = [
        (
            "Buenaventura",
            "Vía Buga - Loboguerrero - Buenaventura (Ruta Nacional 40)",
            "Alerta Climática",
            "INVÍAS #767 / DITRA",
            "Paso restringido a un solo carril en sector La Balastrera (km 44) por lluvias y desprendimiento rocoso menor. Despacho terrestre con demora estimada de 12 a 24 horas."
        ),
        (
            "Cartagena",
            "Corredor de Carga Mamonal - Contecar - SPRC",
            "Operación Normal",
            "DIMAR / Capitanía de Puerto",
            "Tránsito fluido en accesos portuarios terrestres. Terminales de Contecar y SPRC operando al 100% con calado de 14.5 m y ventanas de atraque estables."
        ),
        (
            "Buenaventura",
            "Terminales Marítimas de Buenaventura (SPRB / TCBUEN / Aguadulce)",
            "Operación Normal",
            "Superintendencia de Transporte / DIMAR",
            "Operación de grúas pórtico y stacking de exportación en condiciones regulares. Maniobras de atraque en canal de acceso sin restricciones marítimas."
        ),
        (
            "Cartagena",
            "Troncal del Caribe / Ruta del Sol (Acceso interior nacional)",
            "Alerta Climática",
            "INVÍAS #767",
            "Obras viales de estabilización de calzada en tramo Aguachica - Bosconia con paso alternado nocturno."
        )
    ]

    cursor.executemany("""
    INSERT INTO contingencias (puerto, corredor, nivel, fuente_oficial, descripcion)
    VALUES (?, ?, ?, ?, ?)
    """, contingencias_seed)

    conn.commit()


# =============================================================================
# OPERACIONES CRUD: ORGANIZACIONES
# =============================================================================

def get_all_organizaciones() -> List[Dict[str, Any]]:
    """Retorna todas las organizaciones registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, nombre, nit, sector, producto_principal, region_origen, municipio, contacto, email, fecha_registro
    FROM organizaciones
    ORDER BY nombre ASC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_organizacion_by_id(org_id: int) -> Optional[Dict[str, Any]]:
    """Retorna una organización específica por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organizaciones WHERE id = ?", (org_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def insert_organizacion(
    nombre: str,
    nit: str,
    sector: str,
    producto_principal: str,
    region_origen: str,
    municipio: str,
    contacto: str,
    email: str
) -> int:
    """Registra una nueva organización exportadora (RF-01)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO organizaciones (nombre, nit, sector, producto_principal, region_origen, municipio, contacto, email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre.strip(), nit.strip(), sector, producto_principal.strip(), region_origen, municipio.strip(), contacto.strip(), email.strip()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


# =============================================================================
# OPERACIONES CRUD: CONTINGENCIAS
# =============================================================================

def get_contingencias(solo_activas: bool = True) -> List[Dict[str, Any]]:
    """Retorna las contingencias viales y portuarias registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    filtro = "WHERE activo = 1" if solo_activas else ""
    cursor.execute(f"""
    SELECT id, puerto, corredor, nivel, fuente_oficial, descripcion, fecha_reporte, activo
    FROM contingencias
    {filtro}
    ORDER BY fecha_reporte DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_ultima_contingencia_por_puerto(puerto: str) -> Dict[str, Any]:
    """Retorna el reporte de contingencia más reciente y activo para un puerto específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, puerto, corredor, nivel, fuente_oficial, descripcion, fecha_reporte, activo
    FROM contingencias
    WHERE puerto = ? AND activo = 1
    ORDER BY fecha_reporte DESC
    LIMIT 1
    """, (puerto,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    # Si no hay registros, por defecto operación normal
    return {
        "puerto": puerto,
        "corredor": f"Corredor principal hacia {puerto}",
        "nivel": "Operación Normal",
        "fuente_oficial": "Sistema Automatizado",
        "descripcion": "Sin novedades viales o portuarias reportadas. Flujo logístico regular.",
        "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "activo": 1
    }


def insert_contingencia(
    puerto: str,
    corredor: str,
    nivel: str,
    fuente_oficial: str,
    descripcion: str
) -> int:
    """Registra una nueva novedad vial o portuaria (RF-05)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO contingencias (puerto, corredor, nivel, fuente_oficial, descripcion)
    VALUES (?, ?, ?, ?, ?)
    """, (puerto, corredor.strip(), nivel, fuente_oficial.strip(), descripcion.strip()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


# =============================================================================
# OPERACIONES CRUD: SIMULACIONES Y REPORTES
# =============================================================================

def insert_simulacion(
    organizacion_id: Optional[int],
    organizacion_nombre: str,
    sector: str,
    producto: str,
    region_origen: str,
    mercado_destino: str,
    toneladas: float,
    trm: float,
    tipo_carga: str,
    contenedores: int,
    puerto_recomendado: str,
    costo_buenaventura_cop: float,
    costo_cartagena_cop: float,
    ahorro_cop: float,
    costo_kg_optimo: float,
    estado_buenaventura: str,
    estado_cartagena: str,
    detalles_dict: Dict[str, Any],
    usuario: str = "Operador"
) -> int:
    """Almacena una simulación de despacho en la bitácora SQLite (RF-08)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO simulaciones (
        organizacion_id, organizacion_nombre, sector, producto, region_origen,
        mercado_destino, toneladas, trm, tipo_carga, contenedores,
        puerto_recomendado, costo_buenaventura_cop, costo_cartagena_cop,
        ahorro_cop, costo_kg_optimo, estado_buenaventura, estado_cartagena,
        detalles_json, usuario
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        organizacion_id,
        organizacion_nombre,
        sector,
        producto,
        region_origen,
        mercado_destino,
        toneladas,
        trm,
        tipo_carga,
        contenedores,
        puerto_recomendado,
        costo_buenaventura_cop,
        costo_cartagena_cop,
        ahorro_cop,
        costo_kg_optimo,
        estado_buenaventura,
        estado_cartagena,
        json.dumps(detalles_dict, ensure_ascii=False),
        usuario
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_simulaciones(limit: int = 200) -> List[Dict[str, Any]]:
    """Retorna la lista de simulaciones históricas registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT id, organizacion_id, organizacion_nombre, sector, producto, region_origen,
           mercado_destino, toneladas, trm, tipo_carga, contenedores,
           puerto_recomendado, costo_buenaventura_cop, costo_cartagena_cop,
           ahorro_cop, costo_kg_optimo, estado_buenaventura, estado_cartagena,
           detalles_json, usuario, fecha_simulacion
    FROM simulaciones
    ORDER BY fecha_simulacion DESC
    LIMIT {limit}
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_metricas_globales() -> Dict[str, Any]:
    """Calcula indicadores globales para dashboards ejecutivos."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total_orgs FROM organizaciones")
    total_orgs = cursor.fetchone()["total_orgs"]

    cursor.execute("SELECT COUNT(*) AS total_simulaciones, IFNULL(SUM(toneladas), 0) AS total_toneladas, IFNULL(AVG(ahorro_cop), 0) AS promedio_ahorro FROM simulaciones")
    res_sims = cursor.fetchone()
    total_sims = res_sims["total_simulaciones"]
    total_ton = res_sims["total_toneladas"]
    prom_ahorro = res_sims["promedio_ahorro"]

    cursor.execute("""
    SELECT puerto_recomendado, COUNT(*) as cantidad
    FROM simulaciones
    GROUP BY puerto_recomendado
    ORDER BY cantidad DESC
    LIMIT 1
    """)
    puerto_top_row = cursor.fetchone()
    puerto_top = puerto_top_row["puerto_recomendado"] if puerto_top_row else "N/A"

    cursor.execute("SELECT COUNT(*) AS total_alertas FROM contingencias WHERE activo = 1 AND nivel != 'Operación Normal'")
    total_alertas = cursor.fetchone()["total_alertas"]

    conn.close()
    return {
        "total_organizaciones": total_orgs,
        "total_simulaciones": total_sims,
        "total_toneladas": round(total_ton, 1),
        "promedio_ahorro_cop": round(prom_ahorro, 2),
        "puerto_frecuente": puerto_top,
        "contingencias_activas": total_alertas
    }


def log_auditoria(usuario: str, rol: str, accion: str, detalle: str = ""):
    """Registra eventos de auditoría y trazabilidad en la base de datos (RF-09)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO auditoria (usuario, rol, accion, detalle)
    VALUES (?, ?, ?, ?)
    """, (usuario, rol, accion, detalle))
    conn.commit()
    conn.close()


def reset_db_seed():
    """Reinicializa por completo las tablas y recarga los datos semilla."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
    init_db()

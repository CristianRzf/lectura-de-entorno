"""
database.py - Gestión de la base de datos SQLite para la aplicación de Lectura del Entorno (PESTEL)
de la organización (la organización).
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from models import calculate_score, calculate_priority_score

DB_PATH = os.path.join(os.path.dirname(__file__), "pestel_database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(seed_if_empty: bool = True):
    """Inicializa las tablas de la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de factores PESTEL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        categoria_pestel TEXT NOT NULL,
        tipo TEXT NOT NULL,
        ambito TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        probabilidad INTEGER NOT NULL,
        impacto INTEGER NOT NULL,
        urgencia TEXT NOT NULL,
        puntuacion_severidad INTEGER NOT NULL,
        prioridad_ponderada REAL NOT NULL,
        efecto_empresa TEXT NOT NULL,
        fuente_nombre TEXT NOT NULL,
        fuente_url TEXT NOT NULL,
        fuente_confiabilidad TEXT DEFAULT 'Alta',
        fecha_publicacion TEXT NOT NULL,
        fecha_consulta TEXT NOT NULL,
        estado TEXT DEFAULT 'En Monitoreo',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Tabla de historial de seguimiento con rol
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_seguimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factor_id INTEGER NOT NULL,
        fecha_registro TEXT NOT NULL,
        observacion TEXT NOT NULL,
        usuario TEXT DEFAULT 'Analista de Entorno',
        rol TEXT DEFAULT 'Usuario',
        cambio_estado TEXT,
        FOREIGN KEY (factor_id) REFERENCES factores (id) ON DELETE CASCADE
    )
    """)

    # Tabla de recomendaciones estratégicas con autor y rol
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recomendaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factor_id INTEGER NOT NULL,
        codigo_recomendacion TEXT NOT NULL,
        titulo TEXT NOT NULL,
        accion_sugerida TEXT NOT NULL,
        evidencia TEXT NOT NULL,
        prioridad TEXT NOT NULL,
        area_responsable TEXT NOT NULL,
        plazo TEXT NOT NULL,
        estado TEXT DEFAULT 'Planificada',
        autor_rol TEXT DEFAULT 'Decisor',
        autor_nombre TEXT DEFAULT 'Comité de Dirección',
        FOREIGN KEY (factor_id) REFERENCES factores (id) ON DELETE CASCADE
    )
    """)

    # Migraciones seguras para bases de datos existentes
    try:
        cursor.execute("ALTER TABLE historial_seguimiento ADD COLUMN rol TEXT DEFAULT 'Usuario'")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE recomendaciones ADD COLUMN autor_rol TEXT DEFAULT 'Decisor'")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE recomendaciones ADD COLUMN autor_nombre TEXT DEFAULT 'Comité de Dirección'")
    except Exception:
        pass

    conn.commit()

    # Inicializar tabla de usuarios y autenticación con roles
    import auth
    auth.init_users_table(conn)

    if seed_if_empty:
        cursor.execute("SELECT COUNT(*) FROM factores")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_data(conn)

    conn.close()

def seed_data(conn):
    """Puebla la base de datos con factores del entorno reales para la organización."""
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    factores_seed = [
        # POLÍTICOS
        {
            "codigo": "POL-01",
            "titulo": "Política Nacional de Reindustrialización y Fomento a la Silvicultura Comercial",
            "categoria_pestel": "Político",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "El Ministerio de Agricultura y el MinComercio fortalecieron el Certificado de Incentivo Forestal (CIF) para plantaciones maderables comerciales sostenibles en el suroccidente colombiano.",
            "probabilidad": 4,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Permite a la organización expandir sus más de 68.000 hectáreas forestales en regional y Cauca con alivios tributarios y subsidios directos a la siembra.",
            "fuente_nombre": "Ministerio de Agricultura y Desarrollo Rural de Colombia",
            "fuente_url": "https://www.minagricultura.gov.co/atencion-ciudadano/tramites-servicios/Paginas/Certificado-de-Incentivo-Forestal-CIF.aspx",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-03-15",
            "fecha_consulta": "2024-10-10",
            "estado": "En Monitoreo"
        },
        {
            "codigo": "POL-02",
            "titulo": "Bloqueos y alteraciones del orden público en el corredor vial Panamericano (Cauca - Valle)",
            "categoria_pestel": "Político",
            "tipo": "Riesgo",
            "ambito": "Regional regional",
            "descripcion": "Cierres recurrentes de la vía Panamericana por protestas sociales y tensiones comunitarias en el departamento del Cauca.",
            "probabilidad": 5,
            "impacto": 4,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Riesgo crítico de desabastecimiento de trozas de madera y fibra virgen desde los núcleos forestales del Cauca hacia los molinos de pulpa y papel en el complejo industrial de la organización.",
            "fuente_nombre": "ANDI Seccional regional / Diario La República",
            "fuente_url": "https://www.larepublica.co/economia/bloqueos-en-la-via-panamericana-dejan-millonarias-perdidas-al-valle-del-cauca-3685412",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-08-20",
            "fecha_consulta": "2024-10-12",
            "estado": "Activo / Crítico"
        },
        {
            "codigo": "POL-03",
            "titulo": "Aranceles e incertidumbre geopolítica en fletes marítimos para importación de pulpa química",
            "categoria_pestel": "Político",
            "tipo": "Riesgo",
            "ambito": "Internacional",
            "descripcion": "Aumento de costos de fletes y barreras no arancelarias en el comercio marítimo que afectan la importación de pulpa de fibra larga no producida localmente.",
            "probabilidad": 3,
            "impacto": 3,
            "urgencia": "Media (6 - 12 meses)",
            "efecto_empresa": "Incremento en los costos de materias primas importadas que entran por el Puerto de Buenaventura hacia la la organización para la fabricación de papeles kraft especiales.",
            "fuente_nombre": "Cámara de Comercio de Cali / Portafolio",
            "fuente_url": "https://www.portafolio.co/economia/comercio-exterior/fletes-maritimos-y-costos-logisticos-colombia-599120",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-06-11",
            "fecha_consulta": "2024-10-05",
            "estado": "En Monitoreo"
        },

        # ECONÓMICOS
        {
            "codigo": "ECO-01",
            "titulo": "Crecimiento exponencial de las exportaciones de Aguacate Hass, Flores y Frutas exóticas",
            "categoria_pestel": "Económico",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "Las exportaciones no tradicionales del Eje Cafetero y regional exigen empaques de cartón corrugado especializados para cadena de frío que soporten humedad y tránsito internacional.",
            "probabilidad": 5,
            "impacto": 5,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Demanda récord para la planta de corrugado de la organización en cajas diseñadas con tratamientos antihumedad y alta resistencia al estibado para el sector agroexportador.",
            "fuente_nombre": "ProColombia & Asohofrucol",
            "fuente_url": "https://procolombia.co/noticias/exportaciones-de-aguacate-hass-y-frutas-colombianas-marcan-record",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-07-28",
            "fecha_consulta": "2024-10-15",
            "estado": "Activo / Crítico"
        },
        {
            "codigo": "ECO-02",
            "titulo": "Volatilidad de la Tasa de Cambio (TRM USD/COP) e inflación en costos energéticos",
            "categoria_pestel": "Económico",
            "tipo": "Riesgo",
            "ambito": "Nacional",
            "descripcion": "Fluctuaciones en el precio del dólar impactan el costo de repuestos importados de maquinaria papelera, mientras que las tarifas de gas natural industrial en el Valle aumentan.",
            "probabilidad": 4,
            "impacto": 3,
            "urgencia": "Media (6 - 12 meses)",
            "efecto_empresa": "Presión sobre los márgenes operativos de las calderas y máquinas corrugadoras en Yumbo; requiere coberturas cambiarias y optimización energética.",
            "fuente_nombre": "Banco de la República de Colombia / DANE",
            "fuente_url": "https://www.banrep.gov.co/es/estadisticas/tasa-cambio-del-peso-colombiano-trm",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-09-30",
            "fecha_consulta": "2024-10-18",
            "estado": "En Mitigación / Acción"
        },
        {
            "codigo": "ECO-03",
            "titulo": "Expansión del Comercio Electrónico (E-Commerce) y logística de última milla en Colombia",
            "categoria_pestel": "Económico",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "El comercio electrónico colombiano crece a tasas superiores al 12% anual, exigiendo soluciones de embalaje a la medida ('Right-size packaging') y fáciles de reciclar.",
            "probabilidad": 5,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Oportunidad para que la organización lidere el mercado con su portafolio eBottle y eBox reduciendo aire transportado y costos logísticos.",
            "fuente_nombre": "Cámara Colombiana de Comercio Electrónico (CCCE)",
            "fuente_url": "https://www.cce.org.co/noticias/informe-trimestral-de-comercio-electronico-en-colombia",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-08-14",
            "fecha_consulta": "2024-10-10",
            "estado": "En Monitoreo"
        },

        # SOCIALES
        {
            "codigo": "SOC-01",
            "titulo": "Conciencia del consumidor sobre la reducción de plásticos y consumo responsable",
            "categoria_pestel": "Social",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "Estudios de consumo demuestran que el 74% de los consumidores colombianos prefieren productos empacados en materiales biodegradables y reciclables frente al plástico.",
            "probabilidad": 5,
            "impacto": 5,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Aceleración de contratos de sustitución de plástico con clientes masivos (grandes superficies, alimentos y bebidas) migrando a cartón de la organización.",
            "fuente_nombre": "Kantar Worldpanel Colombia / WWF Colombia",
            "fuente_url": "https://www.kantar.com/latin-america/inspiracion/sostenibilidad/consumidor-sostenible-en-colombia",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-05-19",
            "fecha_consulta": "2024-10-14",
            "estado": "Mitigado / Capitalizado"
        },
        {
            "codigo": "SOC-02",
            "titulo": "Relacionamiento con comunidades étnicas y campesinas en zonas forestales",
            "categoria_pestel": "Social",
            "tipo": "Riesgo",
            "ambito": "Regional regional",
            "descripcion": "Demandas de concertación previa, reclamos de uso de la tierra y expectativas de empleo local en los municipios de influencia forestal (Darién, Restrepo, El Tambo, Popayán).",
            "probabilidad": 4,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Riesgo de retrasos en faenas de cosecha forestal; exige redoblar los programas de valor compartido a través de la Fundación la organización.",
            "fuente_nombre": "Fundación la organización / Informe de Sostenibilidad",
            "fuente_url": "https://www.organizacion.com/co/sostenibilidad/fundacion",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-04-10",
            "fecha_consulta": "2024-10-08",
            "estado": "En Mitigación / Acción"
        },
        {
            "codigo": "SOC-03",
            "titulo": "Demanda de perfiles técnicos calificados en automatización y mecatrónica en Yumbo",
            "categoria_pestel": "Social",
            "tipo": "Riesgo",
            "ambito": "Regional regional",
            "descripcion": "Escasez de técnicos y tecnólogos calificados en la zona industrial de la organización para operar maquinaria corrugadora de alta velocidad y sistemas robóticos.",
            "probabilidad": 3,
            "impacto": 3,
            "urgencia": "Media (6 - 12 meses)",
            "efecto_empresa": "Riesgo de curvas de aprendizaje prolongadas en turnos nocturnos de la planta corrugadora de Yumbo; necesidad de convenios de formación dual con el SENA.",
            "fuente_nombre": "SENA Regional Valle / ACOPI Valle",
            "fuente_url": "https://www.sena.edu.co/es-co/Noticias/Paginas/alianzas-empresariales-valle-del-cauca.aspx",
            "fuente_confiabilidad": "Media",
            "fecha_publicacion": "2024-02-18",
            "fecha_consulta": "2024-10-01",
            "estado": "En Monitoreo"
        },

        # TECNOLÓGICOS
        {
            "codigo": "TEC-01",
            "titulo": "Desarrollo de recubrimientos biodegradables 'AquaStop' para sustituir el film plástico",
            "categoria_pestel": "Tecnológico",
            "tipo": "Oportunidad",
            "ambito": "Internacional",
            "descripcion": "Innovación global de la organización en tecnología de barrera base acuosa que hace los empaques 100% reciclables sin generar microplásticos.",
            "probabilidad": 4,
            "impacto": 5,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Transferencia de la fórmula tecnológica a la la organización para abastecer el mercado andino de cajas para pescados, pollos y alimentos refrigerados.",
            "fuente_nombre": "la organización Global R&D News",
            "fuente_url": "https://www.organizacion.com/innovaciones/aquastop-packaging-technology",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-06-25",
            "fecha_consulta": "2024-10-16",
            "estado": "En Mitigación / Acción"
        },
        {
            "codigo": "TEC-02",
            "titulo": "Implementación de gemelos digitales y mantenimiento predictivo IoT en molinos de Yumbo",
            "categoria_pestel": "Tecnológico",
            "tipo": "Oportunidad",
            "ambito": "Regional regional",
            "descripcion": "Instalación de sensores de vibración y algoritmos de Machine Learning para predecir fallas en rodillos de corrugación y prensas de papel en la organización.",
            "probabilidad": 4,
            "impacto": 4,
            "urgencia": "Media (6 - 12 meses)",
            "efecto_empresa": "Reducción estimada del 18% en tiempos muertos no programados y ahorro del 7% en mermas de cartón en las líneas de conversión.",
            "fuente_nombre": "Revista Metalmecánica & Industria 4.0 Colombia",
            "fuente_url": "https://www.metalmecanica.com/industria-40-papeleras-colombia",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-03-30",
            "fecha_consulta": "2024-10-09",
            "estado": "En Monitoreo"
        },
        {
            "codigo": "TEC-03",
            "titulo": "Ciberataques dirigidos a sistemas SCADA y redes operacionales industriales (OT)",
            "categoria_pestel": "Tecnológico",
            "tipo": "Riesgo",
            "ambito": "Internacional",
            "descripcion": "Incremento de ataques de ransomware dirigidos a plantas manufactureras y sistemas de control distribuido en América Latina.",
            "probabilidad": 3,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Riesgo de paralización de las calderas de biomasa y máquinas formadoras de papel en la organización si los sistemas de control son vulnerados.",
            "fuente_nombre": "ColCERT - Centro Cibernético Nacional de Colombia",
            "fuente_url": "https://www.colcert.gov.co/alertas-seguridad-industrial-scada",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-07-02",
            "fecha_consulta": "2024-10-11",
            "estado": "En Mitigación / Acción"
        },

        # ECOLÓGICOS / AMBIENTALES
        {
            "codigo": "ECO-L01",
            "titulo": "Entrada en vigor plena de la Ley 2232 de 2022 (Prohibición de plásticos de un solo uso)",
            "categoria_pestel": "Ecológico",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "A partir de julio de 2024 comenzaron a regir las prohibiciones para las primeras 8 categorías de plásticos de un solo uso en Colombia, impulsando la sustitución obligatoria.",
            "probabilidad": 5,
            "impacto": 5,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Impacto altamente positivo: disparó la demanda de bolsas de papel kraft producidas en la división de sacos de la organización y bandejas de cartón moldeado.",
            "fuente_nombre": "Ministerio de Ambiente y Desarrollo Sostenible",
            "fuente_url": "https://www.minambiente.gov.co/asuntos-ambientales-sectorial-y-urbana/ley-2232-plasticos-un-solo-uso/",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-07-07",
            "fecha_consulta": "2024-10-18",
            "estado": "Activo / Crítico"
        },
        {
            "codigo": "ECO-L02",
            "titulo": "Intensificación del Fenómeno de El Niño y riesgo de estrés hídrico en la cuenca del Río Cauca",
            "categoria_pestel": "Ecológico",
            "tipo": "Riesgo",
            "ambito": "Regional regional",
            "descripcion": "Descenso drástico en los caudales del Río Cauca durante épocas secas y temperaturas récord aumentan el riesgo de incendios forestales en las plantaciones.",
            "probabilidad": 4,
            "impacto": 4,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Riesgo de restricciones temporales de captación de agua industrial impuestas por la CVC en la organización y daño a rodales forestales jóvenes de pino y eucalipto.",
            "fuente_nombre": "CVC (Corporación Autónoma Regional del regional) & IDEAM",
            "fuente_url": "https://www.cvc.gov.co/boletines-hidrologicos-rio-cauca-el-nino",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-08-30",
            "fecha_consulta": "2024-10-17",
            "estado": "Activo / Crítico"
        },
        {
            "codigo": "ECO-L03",
            "titulo": "Alianza para la Economía Circular y tasa de reciclaje de cartón superior al 70%",
            "categoria_pestel": "Ecológico",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "El fortalecimiento del ecosistema de recicladores de oficio en Colombia permite a la organización captar más de 220.000 toneladas de fibra secundaria al año.",
            "probabilidad": 5,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Garantiza suministro de materia prima reciclada a bajo costo energético para las máquinas de papel reciclado del sede principal.",
            "fuente_nombre": "Ministerio de Ambiente / Visión 3030 de la ANDI",
            "fuente_url": "https://www.andi.com.co/Home/Camara/14-vision-3030-reciclaje-envases",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-05-12",
            "fecha_consulta": "2024-10-14",
            "estado": "Mitigado / Capitalizado"
        },

        # LEGALES
        {
            "codigo": "LEG-01",
            "titulo": "Resolución 1407 de 2018 y Res. 1342 de 2020 (Metas REP de Envases y Empaques)",
            "categoria_pestel": "Legal",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "Exige a las empresas transformadoras y comercializadoras demostrar metas crecientes de aprovechamiento de empaques puestos en el mercado (superiores al 18% para 2024).",
            "probabilidad": 5,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Permite a la organización ofrecer servicios de valor agregado a sus clientes industriales certificando la recolección y trazabilidad de sus residuos posconsumo.",
            "fuente_nombre": "Ministerio de Ambiente y Desarrollo Sostenible (MADS)",
            "fuente_url": "https://www.minambiente.gov.co/gestion-integral-del-recurso-hidrico/resolucion-1407-de-2018/",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-01-20",
            "fecha_consulta": "2024-10-10",
            "estado": "En Monitoreo"
        },
        {
            "codigo": "LEG-02",
            "titulo": "Estándares ambientales CVC sobre límites máximos permisibles de vertimientos industriales al Río Cauca",
            "categoria_pestel": "Legal",
            "tipo": "Riesgo",
            "ambito": "Regional regional",
            "descripcion": "Resolución de la CVC que endurece los parámetros de DBO, DQO y sólidos suspendidos en los vertimientos al Río Cauca en el tramo industrial de la organización.",
            "probabilidad": 4,
            "impacto": 4,
            "urgencia": "Alta (3 - 6 meses)",
            "efecto_empresa": "Exige inversiones de capital (CAPEX) en la Planta de Tratamiento de Aguas Residuales (PTAR) de la organización para garantizar cumplimiento estricto y evitar sanciones.",
            "fuente_nombre": "CVC - Dirección de Gestión Ambiental",
            "fuente_url": "https://www.cvc.gov.co/normativa-ambiental-vertimientos-industriales",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-06-18",
            "fecha_consulta": "2024-10-15",
            "estado": "En Mitigación / Acción"
        },
        {
            "codigo": "LEG-03",
            "titulo": "Impuesto nacional sobre plásticos de un solo uso (Ley de Reforma Tributaria 2277)",
            "categoria_pestel": "Legal",
            "tipo": "Oportunidad",
            "ambito": "Nacional",
            "descripcion": "Tarifa impositiva de 1,9 UVT por cada 30 gramos de envase plástico no reciclable, lo que encarece sustancialmente el empaque plástico tradicional.",
            "probabilidad": 5,
            "impacto": 5,
            "urgencia": "Inmediata (< 3 meses)",
            "efecto_empresa": "Hace que el cartón corrugado y las soluciones de papel producidas en la organización sean notablemente más competitivas en precio frente a sustitutos plásticos.",
            "fuente_nombre": "DIAN - Dirección de Impuestos y Aduanas Nacionales",
            "fuente_url": "https://www.dian.gov.co/normatividad/impuesto-nacional-sobre-productos-plasticos",
            "fuente_confiabilidad": "Alta",
            "fecha_publicacion": "2024-02-05",
            "fecha_consulta": "2024-10-13",
            "estado": "Mitigado / Capitalizado"
        }
    ]

    for f in factores_seed:
        score = calculate_score(f["probabilidad"], f["impacto"])
        prio = calculate_priority_score(f["probabilidad"], f["impacto"], f["urgencia"])
        cursor.execute("""
        INSERT INTO factores (
            codigo, titulo, categoria_pestel, tipo, ambito, descripcion,
            probabilidad, impacto, urgencia, puntuacion_severidad, prioridad_ponderada,
            efecto_empresa, fuente_nombre, fuente_url, fuente_confiabilidad,
            fecha_publicacion, fecha_consulta, estado, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f["codigo"], f["titulo"], f["categoria_pestel"], f["tipo"], f["ambito"], f["descripcion"],
            f["probabilidad"], f["impacto"], f["urgencia"], score, prio,
            f["efecto_empresa"], f["fuente_nombre"], f["fuente_url"], f["fuente_confiabilidad"],
            f["fecha_publicacion"], f["fecha_consulta"], f["estado"], now_str, now_str
        ))
        factor_id = cursor.lastrowid

        # Insertar historial inicial
        cursor.execute("""
        INSERT INTO historial_seguimiento (factor_id, fecha_registro, observacion, usuario, cambio_estado)
        VALUES (?, ?, ?, ?, ?)
        """, (
            factor_id,
            f["fecha_consulta"],
            f"Registro inicial y evaluación del factor basado en fuente verificada ({f['fuente_nombre']}).",
            "Analista Senior PESTEL",
            f"Estado inicial: {f['estado']}"
        ))

    # Sembrar recomendaciones estratégicas conectadas a los factores críticos
    recomendaciones_seed = [
        {
            "codigo_factor": "POL-02",
            "codigo_rec": "REC-STR-01",
            "titulo": "Plan de Contingencia Logística y Almacenamiento Estratégico de Fibra",
            "accion_sugerida": "Establecer un patio de acopio intermedio de madera en el norte del Valle y elevar el inventario de seguridad de trozas en la la organización a 45 días continuos de operación para mitigar bloqueos en la Panamericana.",
            "evidencia": "Recurrentes bloqueos en la Vía Panamericana durante 2024 documentados por ANDI y gremios de transporte.",
            "prioridad": "Alta",
            "area_responsable": "Cadena de Suministro & Operaciones",
            "plazo": "Corto Plazo (< 3 meses)",
            "estado": "En Ejecución"
        },
        {
            "codigo_factor": "ECO-01",
            "codigo_rec": "REC-STR-02",
            "titulo": "Expansión de Capacidad en Corrugado Agrícola con Tecnología AquaStop",
            "accion_sugerida": "Asignar turno prioritario en la corrugadora 3 de la organización e implementar el recubrimiento AquaStop para capturar el 40% del mercado de empaque para exportación de aguacate Hass y flores del Valle y Eje Cafetero.",
            "evidencia": "Crecimiento proyectado superior al 15% en exportaciones de frutas frescas reportado por ProColombia.",
            "prioridad": "Alta",
            "area_responsable": "Comercial & Innovación de Productos",
            "plazo": "Inmediato (< 1 mes)",
            "estado": "En Ejecución"
        },
        {
            "codigo_factor": "ECO-L01",
            "codigo_rec": "REC-STR-03",
            "titulo": "Campaña Corporativa 'Reemplaza el Plástico por Papel Hecho en Colombia'",
            "accion_sugerida": "Lanzar portafolio especializado para retail y restaurantes (bolsas kraft de asa plana y bandejas de cartón) aprovechando la entrada en vigor de las sanciones de la Ley 2232 de 2022.",
            "evidencia": "Entrada en vigor del régimen sancionatorio de la Ley 2232 por parte del MinAmbiente.",
            "prioridad": "Alta",
            "area_responsable": "Mercadeo & División de Productos",
            "plazo": "Corto Plazo (< 3 meses)",
            "estado": "Planificada"
        },
        {
            "codigo_factor": "ECO-L02",
            "codigo_rec": "REC-STR-04",
            "titulo": "Programa de Recirculación de Agua y Monitoreo Satelital de Incendios",
            "accion_sugerida": "Instalar torres de detección térmica y vigilancia satelital en plantaciones de Darién y Restrepo, además de optimizar el circuito cerrado de lavado de pulpa en la organización reduciendo consumo por tonelada producida.",
            "evidencia": "Alertas hidrológicas de la CVC sobre bajo caudal del Río Cauca y advertencias de sequía por El Niño.",
            "prioridad": "Alta",
            "area_responsable": "Gestión Ambiental la organización & División Forestal",
            "plazo": "Mediano Plazo (3 - 6 meses)",
            "estado": "En Ejecución"
        },
        {
            "codigo_factor": "LEG-02",
            "codigo_rec": "REC-STR-05",
            "titulo": "Optimización del Clarificador Secundario de la PTAR Yumbo",
            "accion_sugerida": "Ejecutar la modernización del sistema de aireación biológica en la Planta de Tratamiento de Aguas Residuales de la organización para asegurar DBO < 30 mg/L frente a la nueva norma CVC.",
            "evidencia": "Nueva reglamentación de vertimientos industriales expedida por la CVC para la cuenca media del Río Cauca.",
            "prioridad": "Media",
            "area_responsable": "Ingeniería de Planta & Sostenibilidad",
            "plazo": "Mediano Plazo (6 meses)",
            "estado": "Planificada"
        },
        {
            "codigo_factor": "TEC-03",
            "codigo_rec": "REC-STR-06",
            "titulo": "Segmentación y Blindaje de Redes OT/SCADA en la organización",
            "accion_sugerida": "Implementar arquitectura de seguridad Purdue Model para aislar la red de control de calderas y máquinas corrugadoras de la red corporativa de internet, con monitoreo 24/7.",
            "evidencia": "Boletines de alerta cibernética de ColCERT sobre ataques a infraestructura crítica industrial.",
            "prioridad": "Alta",
            "area_responsable": "Tecnología de la Información & Ciberseguridad",
            "plazo": "Corto Plazo (< 3 meses)",
            "estado": "Planificada"
        }
    ]

    for r in recomendaciones_seed:
        cursor.execute("SELECT id FROM factores WHERE codigo = ?", (r["codigo_factor"],))
        res = cursor.fetchone()
        if res:
            f_id = res[0]
            cursor.execute("""
            INSERT INTO recomendaciones (
                factor_id, codigo_recomendacion, titulo, accion_sugerida,
                evidencia, prioridad, area_responsable, plazo, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f_id, r["codigo_rec"], r["titulo"], r["accion_sugerida"],
                r["evidencia"], r["prioridad"], r["area_responsable"], r["plazo"], r["estado"]
            ))

    conn.commit()

def reset_db_to_seed():
    """Reinicia la base de datos a sus valores semilla iniciales."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
    init_db(seed_if_empty=True)

# ----------------- FUNCIONES CRUD DE FACTORES -----------------

def get_all_factors(
    categoria: Optional[str] = None,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    busqueda: Optional[str] = None
) -> pd.DataFrame:
    """Retorna un DataFrame con todos los factores aplicando filtros opcionales."""
    conn = get_connection()
    query = "SELECT * FROM factores WHERE 1=1"
    params = []

    if categoria and categoria != "Todas":
        query += " AND categoria_pestel = ?"
        params.append(categoria)
    if tipo and tipo != "Todos":
        query += " AND tipo = ?"
        params.append(tipo)
    if estado and estado != "Todos":
        query += " AND estado = ?"
        params.append(estado)
    if busqueda and busqueda.strip():
        term = f"%{busqueda.strip()}%"
        query += " AND (titulo LIKE ? OR descripcion LIKE ? OR efecto_empresa LIKE ? OR codigo LIKE ?)"
        params.extend([term, term, term, term])

    query += " ORDER BY puntuacion_severidad DESC, urgencia ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_factor_by_id(factor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un factor por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM factores WHERE id = ?", (factor_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def add_factor(data: Dict[str, Any]) -> int:
    """Agrega un nuevo factor al entorno con cálculo automático de severidad y registro en historial."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Autogenerar código si no viene
    if not data.get("codigo"):
        prefix = data["categoria_pestel"][:3].upper()
        cursor.execute("SELECT COUNT(*) FROM factores WHERE categoria_pestel = ?", (data["categoria_pestel"],))
        idx = cursor.fetchone()[0] + 1
        data["codigo"] = f"{prefix}-{idx:02d}"

    score = calculate_score(int(data["probabilidad"]), int(data["impacto"]))
    prio = calculate_priority_score(int(data["probabilidad"]), int(data["impacto"]), data["urgencia"])

    cursor.execute("""
    INSERT INTO factores (
        codigo, titulo, categoria_pestel, tipo, ambito, descripcion,
        probabilidad, impacto, urgencia, puntuacion_severidad, prioridad_ponderada,
        efecto_empresa, fuente_nombre, fuente_url, fuente_confiabilidad,
        fecha_publicacion, fecha_consulta, estado, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["codigo"], data["titulo"], data["categoria_pestel"], data["tipo"],
        data.get("ambito", "Nacional"), data["descripcion"],
        int(data["probabilidad"]), int(data["impacto"]), data["urgencia"],
        score, prio, data["efecto_empresa"], data["fuente_nombre"], data["fuente_url"],
        data.get("fuente_confiabilidad", "Alta"), data["fecha_publicacion"],
        data.get("fecha_consulta", datetime.now().strftime("%Y-%m-%d")),
        data.get("estado", "En Monitoreo"), now_str, now_str
    ))
    factor_id = cursor.lastrowid

    # Registrar en historial con rol
    cursor.execute("""
    INSERT INTO historial_seguimiento (factor_id, fecha_registro, observacion, usuario, rol, cambio_estado)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        factor_id,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        f"Creación del factor '{data['titulo']}' por lectura del entorno.",
        data.get("usuario_registra", "Ing. Sofía Ramírez"),
        data.get("rol_registra", "Diseñador"),
        f"Estado: {data.get('estado', 'En Monitoreo')}"
    ))

    conn.commit()
    conn.close()
    return factor_id

def update_factor(factor_id: int, data: Dict[str, Any], observacion: str = "", usuario: str = "Analista de Entorno", rol: str = "Diseñador"):
    """Actualiza los datos de un factor y añade la bitácora de seguimiento."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    score = calculate_score(int(data["probabilidad"]), int(data["impacto"]))
    prio = calculate_priority_score(int(data["probabilidad"]), int(data["impacto"]), data["urgencia"])

    cursor.execute("""
    UPDATE factores SET
        titulo = ?, categoria_pestel = ?, tipo = ?, ambito = ?, descripcion = ?,
        probabilidad = ?, impacto = ?, urgencia = ?, puntuacion_severidad = ?,
        prioridad_ponderada = ?, efecto_empresa = ?, fuente_nombre = ?, fuente_url = ?,
        fuente_confiabilidad = ?, fecha_publicacion = ?, fecha_consulta = ?,
        estado = ?, updated_at = ?
    WHERE id = ?
    """, (
        data["titulo"], data["categoria_pestel"], data["tipo"], data.get("ambito", "Nacional"),
        data["descripcion"], int(data["probabilidad"]), int(data["impacto"]), data["urgencia"],
        score, prio, data["efecto_empresa"], data["fuente_nombre"], data["fuente_url"],
        data.get("fuente_confiabilidad", "Alta"), data["fecha_publicacion"], data["fecha_consulta"],
        data["estado"], now_str, factor_id
    ))

    # Añadir registro de historial
    nota = observacion if observacion else f"Actualización de parámetros del factor (Prob: {data['probabilidad']}, Imp: {data['impacto']})."
    cursor.execute("""
    INSERT INTO historial_seguimiento (factor_id, fecha_registro, observacion, usuario, rol, cambio_estado)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        factor_id,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        nota,
        usuario,
        rol,
        f"Nuevo estado: {data['estado']}"
    ))

    conn.commit()
    conn.close()

def delete_factor(factor_id: int):
    """Elimina un factor y sus relaciones en cascada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial_seguimiento WHERE factor_id = ?", (factor_id,))
    cursor.execute("DELETE FROM recomendaciones WHERE factor_id = ?", (factor_id,))
    cursor.execute("DELETE FROM factores WHERE id = ?", (factor_id,))
    conn.commit()
    conn.close()

# ----------------- FUNCIONES DE HISTORIAL Y SEGUIMIENTO -----------------

def get_factor_history(factor_id: int) -> List[Dict[str, Any]]:
    """Obtiene la bitácora de seguimiento de un factor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM historial_seguimiento WHERE factor_id = ? ORDER BY fecha_registro DESC
    """, (factor_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_history_entry(factor_id: int, observacion: str, usuario: str = "Analista de Entorno", cambio_estado: str = "", rol: str = "Usuario"):
    """Registra una nueva observación o seguimiento con rol."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO historial_seguimiento (factor_id, fecha_registro, observacion, usuario, rol, cambio_estado)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (factor_id, now_str, observacion, usuario, rol, cambio_estado))

    if cambio_estado and cambio_estado != "Sin cambio":
        cursor.execute("UPDATE factores SET estado = ?, updated_at = ? WHERE id = ?", (cambio_estado, now_str, factor_id))

    conn.commit()
    conn.close()

# ----------------- FUNCIONES DE RECOMENDACIONES -----------------

def get_all_recommendaciones(factor_id: Optional[int] = None) -> pd.DataFrame:
    """Obtiene todas las recomendaciones o las de un factor específico con join al factor."""
    conn = get_connection()
    query = """
    SELECT r.*, f.codigo as factor_codigo, f.titulo as factor_titulo, f.categoria_pestel, f.tipo as factor_tipo
    FROM recomendaciones r
    JOIN factores f ON r.factor_id = f.id
    WHERE 1=1
    """
    params = []
    if factor_id:
        query += " AND r.factor_id = ?"
        params.append(factor_id)

    query += " ORDER BY CASE r.prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 ELSE 3 END"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def add_recommendation(data: Dict[str, Any]) -> int:
    """Registra una nueva recomendación vinculada a un factor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recomendaciones")
    count = cursor.fetchone()[0] + 1
    codigo_rec = f"REC-EST-{count:02d}"

    cursor.execute("""
    INSERT INTO recomendaciones (
        factor_id, codigo_recomendacion, titulo, accion_sugerida,
        evidencia, prioridad, area_responsable, plazo, estado,
        autor_rol, autor_nombre
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["factor_id"], codigo_rec, data["titulo"], data["accion_sugerida"],
        data["evidencia"], data["prioridad"], data["area_responsable"],
        data["plazo"], data.get("estado", "Planificada"),
        data.get("autor_rol", "Decisor"),
        data.get("autor_nombre", "Dr. Carlos Mendoza")
    ))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def update_recommendation_status(rec_id: int, new_status: str):
    """Actualiza el estado de ejecución de una recomendación."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE recomendaciones SET estado = ? WHERE id = ?", (new_status, rec_id))
    conn.commit()
    conn.close()

# ----------------- RESUMEN DE INDICADORES (KPIS) -----------------

def get_kpis_summary() -> Dict[str, Any]:
    """Genera indicadores ejecutivos para el tablero de control."""
    df = get_all_factors()
    if df.empty:
        return {
            "total_factores": 0,
            "total_riesgos": 0,
            "total_oportunidades": 0,
            "riesgos_criticos": 0,
            "oportunidades_estrategicas": 0,
            "promedio_impacto": 0.0,
            "total_recomendaciones": 0,
            "recomendaciones_activas": 0
        }

    total = len(df)
    riesgos = df[df["tipo"] == "Riesgo"]
    oportunidades = df[df["tipo"] == "Oportunidad"]

    criticos = riesgos[riesgos["puntuacion_severidad"] >= 16]
    estrategicas = oportunidades[oportunidades["puntuacion_severidad"] >= 16]

    df_rec = get_all_recommendaciones()
    rec_activas = len(df_rec[df_rec["estado"].isin(["Planificada", "En Ejecución"])]) if not df_rec.empty else 0

    return {
        "total_factores": total,
        "total_riesgos": len(riesgos),
        "total_oportunidades": len(oportunidades),
        "riesgos_criticos": len(criticos),
        "oportunidades_estrategicas": len(estrategicas),
        "promedio_impacto": round(df["impacto"].mean(), 1),
        "total_recomendaciones": len(df_rec),
        "recomendaciones_activas": rec_activas
    }

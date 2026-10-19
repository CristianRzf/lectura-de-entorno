"""
utils/external_sources.py - Módulo para la integración y captura de información del entorno
desde fuentes públicas oficiales, informes corporativos y medios especializados.
"""

from typing import List, Dict, Any
from datetime import datetime

# Directorio de fuentes autorizadas y enlaces oficiales para Smurfit WestRock Colombia
OFFICIAL_SOURCES_CATALOG = [
    {
        "id": "SRC-01",
        "entidad": "Smurfit WestRock Global & Colombia",
        "tipo": "Informes Corporativos & Portal Oficial",
        "categoria_primaria": "Ecológico / Tecnológico",
        "url": "https://www.smurfitwestrock.com/co",
        "descripcion": "Portal corporativo, informes anuales de sostenibilidad, innovaciones en empaques biodegradables y operaciones en Yumbo."
    },
    {
        "id": "SRC-02",
        "entidad": "Ministerio de Ambiente y Desarrollo Sostenible (MADS)",
        "tipo": "Regulación Ambiental Oficial",
        "categoria_primaria": "Legal / Ecológico",
        "url": "https://www.minambiente.gov.co",
        "descripcion": "Políticas de plásticos de un solo uso (Ley 2232), Responsabilidad Extendida del Productor (REP) y metas de descarbonización."
    },
    {
        "id": "SRC-03",
        "entidad": "CVC (Corporación Autónoma Regional del Valle del Cauca)",
        "tipo": "Autoridad Ambiental Regional",
        "categoria_primaria": "Ecológico / Legal",
        "url": "https://www.cvc.gov.co",
        "descripcion": "Monitoreo del Río Cauca, permisos de captación hídrica industrial en Yumbo, calidad del aire y planes de ordenamiento de cuenca."
    },
    {
        "id": "SRC-04",
        "entidad": "DANE (Departamento Administrativo Nacional de Estadística)",
        "tipo": "Estadísticas Oficiales",
        "categoria_primaria": "Económico",
        "url": "https://www.dane.gov.co",
        "descripcion": "Encuesta Mensual Manufacturera (EMMET), índice de producción de pulpa y papel, IPC e índices de comercio exterior."
    },
    {
        "id": "SRC-05",
        "entidad": "Banco de la República de Colombia",
        "tipo": "Autoridad Monetaria",
        "categoria_primaria": "Económico",
        "url": "https://www.banrep.gov.co",
        "descripcion": "Comportamiento diario de la TRM (USD/COP), tasas de interés de política monetaria y proyecciones de inflación."
    },
    {
        "id": "SRC-06",
        "entidad": "ANDI (Asociación Nacional de Empresarios de Colombia)",
        "tipo": "Gremio Industrial",
        "categoria_primaria": "Político / Económico",
        "url": "https://www.andi.com.co",
        "descripcion": "Cámara de Pulpa, Papel y Cartón, Seccional Valle del Cauca, iniciativa Visión 3030 de economía circular."
    },
    {
        "id": "SRC-07",
        "entidad": "ProColombia & Asohofrucol",
        "tipo": "Comercio Exterior Agroindustrial",
        "categoria_primaria": "Económico",
        "url": "https://procolombia.co",
        "descripcion": "Dinámica de exportación de productos agrícolas (aguacate Hass, flores, hierbas aromáticas) que requieren cajas de cartón corrugado."
    },
    {
        "id": "SRC-08",
        "entidad": "FSC Colombia (Forest Stewardship Council)",
        "tipo": "Certificación Forestal",
        "categoria_primaria": "Ecológico / Social",
        "url": "https://co.fsc.org",
        "descripcion": "Estándares de manejo forestal responsable y cadena de custodia para plantaciones de pino y eucalipto."
    }
]

# Señales recientes del entorno disponibles para rápida importación / captura
PRECONFIGURED_SIGNALS = [
    {
        "titulo": "MinAmbiente reglamenta metas de recolección de empaques para 2025 bajo la Resolución 1407",
        "categoria_pestel": "Legal",
        "tipo": "Oportunidad",
        "ambito": "Nacional",
        "fuente_nombre": "Ministerio de Ambiente y Desarrollo Sostenible",
        "fuente_url": "https://www.minambiente.gov.co/normatividad-rep-2025",
        "fecha_publicacion": "2024-09-18",
        "probabilidad": 5,
        "impacto": 4,
        "urgencia": "Alta (3 - 6 meses)",
        "descripcion": "El Ministerio fijó una meta mínima de aprovechamiento del 20% para empresas generadoras de residuos de envases y empaques en Colombia.",
        "efecto_empresa": "Impulsa el negocio de certificación de aprovechamiento y reciclaje de cartón de Smurfit WestRock para sus clientes industriales."
    },
    {
        "titulo": "CVC declara alerta preventiva por niveles bajos en la cuenca del Río Cauca en el tramo Cali-Yumbo",
        "categoria_pestel": "Ecológico",
        "tipo": "Riesgo",
        "ambito": "Regional Valle del Cauca/Yumbo",
        "fuente_nombre": "CVC - Boletín Hidrológico Valle",
        "fuente_url": "https://www.cvc.gov.co/boletin-hidrologico-cuenca-cauca",
        "fecha_publicacion": "2024-09-29",
        "probabilidad": 4,
        "impacto": 4,
        "urgencia": "Inmediata (< 3 meses)",
        "descripcion": "Disminución del 35% en los caudales de entrada al embalse de Salvajina y aumento de turbiedad por bajas lluvias.",
        "efecto_empresa": "Riesgo de límites temporales a la captación de agua industrial en los molinos de pulpa de la planta Yumbo."
    },
    {
        "titulo": "Cámara de Comercio Electrónico reporta crecimiento del 14.5% en ventas con empaque especializado",
        "categoria_pestel": "Económico",
        "tipo": "Oportunidad",
        "ambito": "Nacional",
        "fuente_nombre": "Cámara Colombiana de Comercio Electrónico",
        "fuente_url": "https://www.cce.org.co/informe-e-commerce-2024",
        "fecha_publicacion": "2024-10-02",
        "probabilidad": 5,
        "impacto": 4,
        "urgencia": "Alta (3 - 6 meses)",
        "descripcion": "El comercio electrónico en Colombia exige cajas de cartón con aberturas seguras, cintas adhesivas ecológicas integradas y facilidad de retorno.",
        "efecto_empresa": "Mayor colocación del portafolio e-Commerce de Smurfit WestRock diseñado en la planta corrugadora de Yumbo."
    },
    {
        "titulo": "ProColombia proyecta incremento de 22% en envíos de aguacate Hass del Valle del Cauca hacia Europa",
        "categoria_pestel": "Económico",
        "tipo": "Oportunidad",
        "ambito": "Nacional",
        "fuente_nombre": "ProColombia / MinComercio",
        "fuente_url": "https://procolombia.co/noticias/aguacate-hass-valle-record-2024",
        "fecha_publicacion": "2024-10-08",
        "probabilidad": 5,
        "impacto": 5,
        "urgencia": "Inmediata (< 3 meses)",
        "descripcion": "Productores del norte del Valle y Eje Cafetero aumentan pedidos de cajas de cartón corrugado hidrorresistente para contenedores refrigerados.",
        "efecto_empresa": "Saturación positiva de las líneas de producción de empaque agrícola en la planta Yumbo con márgenes atractivos."
    },
    {
        "titulo": "Proyecto de Ley sobre incentivos tributarios a empresas que autogeneren con biomasa forestal",
        "categoria_pestel": "Político",
        "tipo": "Oportunidad",
        "ambito": "Nacional",
        "fuente_nombre": "Congreso de la República / UPME",
        "fuente_url": "https://www.senado.gov.co/proyectos-ley-transicion-energetica-biomasa",
        "fecha_publicacion": "2024-09-05",
        "probabilidad": 3,
        "impacto": 4,
        "urgencia": "Media (6 - 12 meses)",
        "descripcion": "Debate legislativo para otorgar exenciones arancelarias a equipos de cogeneración eléctrica a partir de residuos de madera y corteza.",
        "efecto_empresa": "Facilita la modernización de la caldera de biomasa de la planta Yumbo reduciendo costos de energía y huella de carbono."
    }
]

def get_official_sources() -> List[Dict[str, Any]]:
    """Retorna el catálogo de fuentes oficiales autorizadas."""
    return OFFICIAL_SOURCES_CATALOG

def get_preconfigured_signals() -> List[Dict[str, Any]]:
    """Retorna señales preconfiguradas para captura asistida."""
    return PRECONFIGURED_SIGNALS

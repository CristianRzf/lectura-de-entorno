"""
models.py - Definición de modelos de datos, constantes paramétricas,
roles de usuario (RBAC) y motor de cálculo de logística de exportación.
Plataforma Transversal de Inteligencia Logística y Despacho Portuario (ONU / GNU).
"""

from enum import Enum
from typing import Dict, Any, Tuple, List
import math


# =============================================================================
# ENUMS DEL DOMINIO LOGÍSTICO
# =============================================================================

class SectorType(str, Enum):
    GRANOS_SECOS = "Granos y Secos"
    FRUTAS_PERECEDEROS = "Frutas y Perecederos"
    AGROINDUSTRIA = "Agroindustria Procesada"
    MANUFACTURA = "Manufactura y Artesanías"


class RegionOrigen(str, Enum):
    CAUCA = "Cauca"
    NARINO = "Nariño"
    VALLE = "Valle del Cauca"
    EJE_CAFETERO = "Eje Cafetero"
    ANTIOQUIA = "Antioquia"
    HUILA = "Huila"
    SANTANDER = "Santander"


class MercadoDestino(str, Enum):
    UNION_EUROPEA = "Unión Europea"
    NORTEAMERICA = "Norteamérica"
    ASIA_PACIFICO = "Asia-Pacífico"
    LATINOAMERICA = "Latinoamérica"


class PuertoSalida(str, Enum):
    BUENAVENTURA = "Buenaventura"
    CARTAGENA = "Cartagena"


class NivelContingencia(str, Enum):
    NORMAL = "Operación Normal"
    ALERTA_CLIMATICA = "Alerta Climática"
    CONGESTION_PORTUARIA = "Congestión Portuaria"
    BLOQUEO_VIAL = "Bloqueo Vial / Contingencia Social"


class TipoCarga(str, Enum):
    ESTANDAR = "Carga Seca Estándar (Dry 20')"
    REFRIGERADA = "Carga Refrigerada (Reefer 20')"


# =============================================================================
# CONTROL DE ACCESO BASADO EN ROLES (RBAC)
# =============================================================================

class UserRole(str, Enum):
    USUARIO_OPERATIVO = "Usuario Operativo"
    DECISOR = "Decisor"
    ADMINISTRADOR = "Diseñador/Administrador"


ROLE_CONFIG: Dict[str, Dict[str, Any]] = {
    UserRole.USUARIO_OPERATIVO.value: {
        "label": "Usuario Operativo",
        "badge": "Operativo",
        "color": "#737373",
        "descripcion": "Consulta de datos, simulación de costos de despacho y exportación de bitácora.",
        "permisos": {
            "simular_despacho": True,
            "ver_contingencias": True,
            "ver_organizaciones": True,
            "exportar_reportes": True,
            "crear_organizacion": False,
            "registrar_contingencia": False,
            "gestionar_sistema": False
        }
    },
    UserRole.DECISOR.value: {
        "label": "Decisor Estratégico",
        "badge": "Decisión",
        "color": "#171717",
        "descripcion": "Análisis comparativo de puertos, formulación de planes de mitigación y registro de contingencias.",
        "permisos": {
            "simular_despacho": True,
            "ver_contingencias": True,
            "ver_organizaciones": True,
            "exportar_reportes": True,
            "crear_organizacion": False,
            "registrar_contingencia": True,
            "gestionar_sistema": False
        }
    },
    UserRole.ADMINISTRADOR.value: {
        "label": "Diseñador / Administrador",
        "badge": "Admin",
        "color": "#0a0a0a",
        "descripcion": "Control total del sistema: gestión y registro de organizaciones, configuración vial y auditoría.",
        "permisos": {
            "simular_despacho": True,
            "ver_contingencias": True,
            "ver_organizaciones": True,
            "exportar_reportes": True,
            "crear_organizacion": True,
            "registrar_contingencia": True,
            "gestionar_sistema": True
        }
    }
}


def check_permission(role: str, permission_key: str) -> bool:
    """Valida si un rol tiene habilitado un permiso específico."""
    cfg = ROLE_CONFIG.get(role)
    if not cfg:
        return False
    return cfg["permisos"].get(permission_key, False)


# =============================================================================
# CONSTANTES Y PARÁMETROS LOGÍSTICOS
# =============================================================================

# Capacidad por contenedor estándar de 20 pies (toneladas)
CAPACIDAD_CONTENEDOR_TON = 18.0

# Factor de sobrecosto para carga refrigerada (Reefer 20')
FACTOR_SOBRECOSTO_REEFER = 1.35

# Tarifas de Flete Terrestre Base (COP por contenedor de 20 pies)
# Matriz Origen -> Puerto de Salida
TARIFAS_FLETE_TERRESTRE_COP: Dict[str, Dict[str, float]] = {
    RegionOrigen.CAUCA.value: {
        PuertoSalida.BUENAVENTURA.value: 3200000.0,
        PuertoSalida.CARTAGENA.value: 7800000.0,
    },
    RegionOrigen.NARINO.value: {
        PuertoSalida.BUENAVENTURA.value: 4600000.0,
        PuertoSalida.CARTAGENA.value: 9200000.0,
    },
    RegionOrigen.VALLE.value: {
        PuertoSalida.BUENAVENTURA.value: 1800000.0,
        PuertoSalida.CARTAGENA.value: 6500000.0,
    },
    RegionOrigen.EJE_CAFETERO.value: {
        PuertoSalida.BUENAVENTURA.value: 3100000.0,
        PuertoSalida.CARTAGENA.value: 5200000.0,
    },
    RegionOrigen.ANTIOQUIA.value: {
        PuertoSalida.BUENAVENTURA.value: 4200000.0,
        PuertoSalida.CARTAGENA.value: 3800000.0,
    },
    RegionOrigen.HUILA.value: {
        PuertoSalida.BUENAVENTURA.value: 3900000.0,
        PuertoSalida.CARTAGENA.value: 6900000.0,
    },
    RegionOrigen.SANTANDER.value: {
        PuertoSalida.BUENAVENTURA.value: 5100000.0,
        PuertoSalida.CARTAGENA.value: 3400000.0,
    },
}

# Gastos Portuarios Base (COP por contenedor de 20 pies)
# Incluye: THC (Terminal Handling Charges), movilización, pesaje, inspecciones ICA / INVIMA / Policía Antinarcóticos
GASTOS_PORTUARIOS_BASE_COP: Dict[str, float] = {
    PuertoSalida.BUENAVENTURA.value: 1450000.0,
    PuertoSalida.CARTAGENA.value: 1650000.0,
}

# Conexión y monitoreo eléctrico para contenedores Reefer (COP adicionales por contenedor)
SOBRECOSTO_PORTUARIO_REEFER_COP: Dict[str, float] = {
    PuertoSalida.BUENAVENTURA.value: 380000.0,
    PuertoSalida.CARTAGENA.value: 420000.0,
}

# Flete Marítimo Internacional (USD por contenedor de 20 pies estándar)
# Matriz: Puerto de Salida -> Mercado Destino
FLETE_MARITIMO_USD: Dict[str, Dict[str, float]] = {
    PuertoSalida.BUENAVENTURA.value: {
        MercadoDestino.UNION_EUROPEA.value: 2100.0,    # Requiere cruce de Canal de Panamá
        MercadoDestino.NORTEAMERICA.value: 1800.0,     # Costa Oeste / Costa Este vía Panamá
        MercadoDestino.ASIA_PACIFICO.value: 1400.0,    # Salida directa y expedita por el Océano Pacífico
        MercadoDestino.LATINOAMERICA.value: 1100.0,    # Conexión Pacífico Sur (Ecuador, Perú, Chile)
    },
    PuertoSalida.CARTAGENA.value: {
        MercadoDestino.UNION_EUROPEA.value: 1650.0,    # Salida directa Atlántico hacia Europa
        MercadoDestino.NORTEAMERICA.value: 1250.0,     # Conexión directa Costa Este / Golfo de México
        MercadoDestino.ASIA_PACIFICO.value: 2250.0,    # Mayor distancia / cruce transístmico
        MercadoDestino.LATINOAMERICA.value: 1200.0,    # Caribe / Centroamérica
    },
}

# Factores de impacto por nivel de contingencia
FACTORES_CONTINGENCIA: Dict[str, Dict[str, float]] = {
    NivelContingencia.NORMAL.value: {
        "factor_terrestre": 0.0,
        "factor_portuario": 0.0,
        "retraso_horas": 0,
        "es_bloqueo": False
    },
    NivelContingencia.ALERTA_CLIMATICA.value: {
        "factor_terrestre": 0.15,   # 15% de sobrecosto terrestre por desvíos y demoras
        "factor_portuario": 0.05,
        "retraso_horas": 24,
        "es_bloqueo": False
    },
    NivelContingencia.CONGESTION_PORTUARIA.value: {
        "factor_terrestre": 0.05,
        "factor_portuario": 0.25,   # 25% de sobrecosto portuario por almacenamiento adicional
        "retraso_horas": 36,
        "es_bloqueo": False
    },
    NivelContingencia.BLOQUEO_VIAL.value: {
        "factor_terrestre": 0.65,   # 65% sobrecosto terrestre por rutas alternas y esperas
        "factor_portuario": 0.10,
        "retraso_horas": 72,
        "es_bloqueo": True
    }
}


# =============================================================================
# MOTOR MATEMÁTICO DE CÁLCULO LOGÍSTICO Y COMPARADOR
# =============================================================================

def calcular_contenedores_requeridos(toneladas: float) -> int:
    """Calcula la cantidad de contenedores de 20 pies (18 ton c/u, mínimo 1)."""
    if toneladas <= 0:
        return 1
    return max(1, math.ceil(toneladas / CAPACIDAD_CONTENEDOR_TON))


def calcular_costo_puerto(
    puerto: str,
    region_origen: str,
    mercado_destino: str,
    toneladas: float,
    trm: float,
    es_refrigerado: bool,
    nivel_contingencia: str
) -> Dict[str, Any]:
    """
    Calcula el desglose completo de costos de exportación para un puerto dado.
    """
    num_contenedores = calcular_contenedores_requeridos(toneladas)
    
    # 1. Flete Terrestre
    tarifa_terrestre_base = TARIFAS_FLETE_TERRESTRE_COP.get(region_origen, {}).get(puerto, 4000000.0)
    # Si es reefer, el transporte terrestre de refrigerados tiene sobrecosto por generador genset
    factor_terrestre_reefer = FACTOR_SOBRECOSTO_REEFER if es_refrigerado else 1.0
    flete_terrestre_base_total = tarifa_terrestre_base * num_contenedores * factor_terrestre_reefer
    
    # Sobrecosto terrestre por contingencia
    cfg_contingencia = FACTORES_CONTINGENCIA.get(nivel_contingencia, FACTORES_CONTINGENCIA[NivelContingencia.NORMAL.value])
    sobrecosto_terrestre = flete_terrestre_base_total * cfg_contingencia["factor_terrestre"]
    flete_terrestre_final = flete_terrestre_base_total + sobrecosto_terrestre

    # 2. Gastos Portuarios
    tarifa_portuaria_base = GASTOS_PORTUARIOS_BASE_COP.get(puerto, 1500000.0)
    adicional_reefer = SOBRECOSTO_PORTUARIO_REEFER_COP.get(puerto, 400000.0) if es_refrigerado else 0.0
    gastos_portuarios_base_total = (tarifa_portuaria_base + adicional_reefer) * num_contenedores
    
    # Sobrecosto portuario por contingencia
    sobrecosto_portuario = gastos_portuarios_base_total * cfg_contingencia["factor_portuario"]
    gastos_portuarios_final = gastos_portuarios_base_total + sobrecosto_portuario

    # 3. Flete Marítimo Internacional
    tarifa_maritima_usd_base = FLETE_MARITIMO_USD.get(puerto, {}).get(mercado_destino, 1800.0)
    tarifa_maritima_usd = tarifa_maritima_usd_base * (FACTOR_SOBRECOSTO_REEFER if es_refrigerado else 1.0)
    flete_maritimo_usd_total = tarifa_maritima_usd * num_contenedores
    flete_maritimo_cop_total = flete_maritimo_usd_total * trm

    # 4. Total Contingencias consolidadas
    costo_contingencia_total = sobrecosto_terrestre + sobrecosto_portuario

    # 5. Costo Total y unitario por kg
    costo_total_cop = flete_terrestre_final + gastos_portuarios_final + flete_maritimo_cop_total
    kilos_totales = max(1.0, toneladas * 1000.0)
    costo_por_kg = costo_total_cop / kilos_totales

    return {
        "puerto": puerto,
        "contenedores": num_contenedores,
        "flete_terrestre_cop": round(flete_terrestre_final, 2),
        "flete_terrestre_base_cop": round(flete_terrestre_base_total, 2),
        "gastos_portuarios_cop": round(gastos_portuarios_final, 2),
        "gastos_portuarios_base_cop": round(gastos_portuarios_base_total, 2),
        "flete_maritimo_usd": round(flete_maritimo_usd_total, 2),
        "flete_maritimo_cop": round(flete_maritimo_cop_total, 2),
        "costo_contingencia_cop": round(costo_contingencia_total, 2),
        "costo_total_cop": round(costo_total_cop, 2),
        "costo_por_kg_cop": round(costo_por_kg, 2),
        "nivel_contingencia": nivel_contingencia,
        "es_bloqueo": cfg_contingencia["es_bloqueo"],
        "retraso_estimado_horas": cfg_contingencia["retraso_horas"]
    }


def comparar_puertos(
    region_origen: str,
    mercado_destino: str,
    toneladas: float,
    trm: float,
    sector: str,
    es_refrigerado_manual: bool = None,
    contingencia_buenaventura: str = NivelContingencia.NORMAL.value,
    contingencia_cartagena: str = NivelContingencia.NORMAL.value
) -> Dict[str, Any]:
    """
    Compara simultáneamente Buenaventura y Cartagena y genera la recomendación estratégica.
    """
    # Determinación automática de reefer según el sector si no se especifica manualmente
    if es_refrigerado_manual is not None:
        es_reefer = es_refrigerado_manual
    else:
        es_reefer = (sector == SectorType.FRUTAS_PERECEDEROS.value)

    res_buenaventura = calcular_costo_puerto(
        puerto=PuertoSalida.BUENAVENTURA.value,
        region_origen=region_origen,
        mercado_destino=mercado_destino,
        toneladas=toneladas,
        trm=trm,
        es_refrigerado=es_reefer,
        nivel_contingencia=contingencia_buenaventura
    )

    res_cartagena = calcular_costo_puerto(
        puerto=PuertoSalida.CARTAGENA.value,
        region_origen=region_origen,
        mercado_destino=mercado_destino,
        toneladas=toneladas,
        trm=trm,
        es_refrigerado=es_reefer,
        nivel_contingencia=contingencia_cartagena
    )

    costo_bva = res_buenaventura["costo_total_cop"]
    costo_ctg = res_cartagena["costo_total_cop"]
    bloqueo_bva = res_buenaventura["es_bloqueo"]
    bloqueo_ctg = res_cartagena["es_bloqueo"]

    # REGLA DE PRIORIZACIÓN ESTRATÉGICA:
    # 1. Si un puerto tiene bloqueo vial y el otro no, se prioriza SIEMPRE el puerto habilitado.
    if bloqueo_bva and not bloqueo_ctg:
        puerto_recomendado = PuertoSalida.CARTAGENA.value
        motivo_recomendacion = (
            "Cartagena es priorizado debido a bloqueo vial / contingencia crítica en el corredor de Buenaventura, "
            "garantizando cumplimiento de cut-off marítimo a pesar de la distancia terrestre."
        )
    elif bloqueo_ctg and not bloqueo_bva:
        puerto_recomendado = PuertoSalida.BUENAVENTURA.value
        motivo_recomendacion = (
            "Buenaventura es priorizado debido a bloqueo vial / contingencia crítica en el corredor hacia Cartagena, "
            "asegurando despacho continuo sin paralización de la carga."
        )
    else:
        # 2. Ambos habilitados o ambos con contingencia similar: gana el de menor costo total
        if costo_bva <= costo_ctg:
            puerto_recomendado = PuertoSalida.BUENAVENTURA.value
            motivo_recomendacion = (
                f"Buenaventura ofrece una ventaja económica directa para el origen {region_origen} "
                f"hacia el mercado de {mercado_destino}."
            )
        else:
            puerto_recomendado = PuertoSalida.CARTAGENA.value
            motivo_recomendacion = (
                f"Cartagena ofrece mayor competitividad integral gracias a tarifas marítimas atlánticas "
                f"hacia {mercado_destino}."
            )

    ahorro_absoluto = abs(costo_bva - costo_ctg)
    costo_mayor = max(costo_bva, costo_ctg)
    ahorro_porcentual = round((ahorro_absoluto / costo_mayor) * 100, 2) if costo_mayor > 0 else 0.0

    optimo = res_buenaventura if puerto_recomendado == PuertoSalida.BUENAVENTURA.value else res_cartagena
    alterno = res_cartagena if puerto_recomendado == PuertoSalida.BUENAVENTURA.value else res_buenaventura

    # Generación de recomendaciones y alertas documentales
    recomendaciones = generar_alertas_recomendaciones(
        puerto_optimo=puerto_recomendado,
        sector=sector,
        mercado_destino=mercado_destino,
        es_reefer=es_reefer,
        estado_optimo=optimo["nivel_contingencia"],
        retraso_horas=optimo["retraso_estimado_horas"],
        ahorro_cop=ahorro_absoluto
    )

    return {
        "region_origen": region_origen,
        "mercado_destino": mercado_destino,
        "toneladas": toneladas,
        "trm": trm,
        "sector": sector,
        "es_refrigerado": es_reefer,
        "contenedores": optimo["contenedores"],
        "buenaventura": res_buenaventura,
        "cartagena": res_cartagena,
        "puerto_recomendado": puerto_recomendado,
        "motivo_recomendacion": motivo_recomendacion,
        "costo_optimo_cop": optimo["costo_total_cop"],
        "costo_optimo_kg_cop": optimo["costo_por_kg_cop"],
        "costo_alterno_cop": alterno["costo_total_cop"],
        "ahorro_absoluto_cop": round(ahorro_absoluto, 2),
        "ahorro_porcentual": ahorro_porcentual,
        "recomendaciones": recomendaciones
    }


def generar_alertas_recomendaciones(
    puerto_optimo: str,
    sector: str,
    mercado_destino: str,
    es_reefer: bool,
    estado_optimo: str,
    retraso_horas: int,
    ahorro_cop: float
) -> Dict[str, List[str]]:
    """
    Genera recomendaciones automáticas basadas en reglas de negocio logísticas, técnicas y normativas (RF-06).
    """
    recs: Dict[str, List[str]] = {
        "ruta_y_tiempos": [],
        "tecnicas_carga": [],
        "normativa_documental": []
    }

    # 1. Reglas de Ruta y Tiempos (Cut-Off & Demurrage)
    if retraso_horas >= 48:
        recs["ruta_y_tiempos"].append(
            f"ANTICIPACIÓN CRÍTICA: Se recomienda despachar desde planta de origen con al menos 48 a 72 horas de antelación "
            f"respecto a la hora de Cut-Off documental y físico en terminales de {puerto_optimo} para prevenir penalidades por Demurrage."
        )
    elif retraso_horas >= 24:
        recs["ruta_y_tiempos"].append(
            f"VENTANA DE SEGURIDAD VIAL: Programar la salida con 24 a 36 horas de anticipación previa al cierre de stacking portuario "
            f"debido a novedades activas ({estado_optimo})."
        )
    else:
        recs["ruta_y_tiempos"].append(
            f"VENTANA REGULAR: Despacho estándar habilitado con ventana de 18 a 24 horas previas al Cut-Off naviero en {puerto_optimo}."
        )

    # 2. Recomendaciones Técnicas de Carga según Sector
    if sector == SectorType.FRUTAS_PERECEDEROS.value or es_reefer:
        recs["tecnicas_carga"].append(
            "CADENA DE FRÍO (REEFER): Mantener monitoreo permanente de set-point térmico (+4°C a +7°C para aguacate / +8°C a +10°C para gulupa). "
            "Exigir generador Genset activo durante todo el trayecto terrestre hacia el puerto."
        )
        recs["tecnicas_carga"].append(
            "ATMÓSFERA CONTROLADA: Para tránsitos marítimos superiores a 14 días (ej. Unión Europea o Asia), solicitar contenedores "
            "con tecnología de atmósfera controlada (O2 reducido y CO2 calibrado) para retardar maduración."
        )
    elif sector == SectorType.GRANOS_SECOS.value:
        recs["tecnicas_carga"].append(
            "PROTECCIÓN HIGROSCÓPICA: Empleo indispensable de bolsas herméticas de alta barrera (tipo GrainPro o Ecotact) y desecantes "
            "de cloruro de calcio en paredes del contenedor estándar para evitar condensación ('lluvia de contenedor') y preservar aroma en café y cacao."
        )
        recs["tecnicas_carga"].append(
            "PARÁMETROS DE HUMEDAD: Verificar humedad en grano inferior al 11.5% - 12.0% previo al consolidado para prevenir desarrollo de ocratoxina A."
        )
    elif sector == SectorType.AGROINDUSTRIA.value:
        recs["tecnicas_carga"].append(
            "ESTIBA Y EMBALAJE INDUSTRIAL: Utilizar estibas de madera tratada térmicamente con sello NIMF 15 / ISPM 15, esquineros rígidos y "
            "película stretch con filtro UV para alimentos procesados o panela pulverizada."
        )
    else:
        recs["tecnicas_carga"].append(
            "PROTECCIÓN DE MANUFACTURAS: Aseguramiento de carga con bolsas de aire inflables (Dunnage bags) para evitar oscilaciones marítimas."
        )

    # 3. Requisitos Documentales y Normativos según Destino
    if mercado_destino == MercadoDestino.UNION_EUROPEA.value:
        recs["normativa_documental"].append(
            "CUMPLIMIENTO EUDR (Reglamento 2023/1115): Exigencia obligatoria de geolocalización poligonal de cada predio productor "
            "libre de deforestación posterior a diciembre 2020 y declaración de debida diligencia en el portal TRACES de la UE."
        )
        recs["normativa_documental"].append(
            "CERTIFICADO EUR.1 & FITOSANITARIO: Certificado de circulación de mercancías EUR.1 para desgravación arancelaria del acuerdo comercial "
            "Colombia-UE, y Certificado Fitosanitario emitido por el ICA con inspección previa en puerto."
        )
    elif mercado_destino == MercadoDestino.NORTEAMERICA.value:
        recs["normativa_documental"].append(
            "NOTIFICACIÓN PREVIA FDA: Registro de instalación alimentaria y presentación del Prior Notice ante la FDA previo al zarpe del buque."
        )
        recs["normativa_documental"].append(
            "INSPECCIÓN ANTINARCÓTICOS Y BASC: Protocolos de seguridad física BASC/OEA en precinto aduanero y coordinación de inspección antinarcóticos no intrusiva."
        )
    elif mercado_destino == MercadoDestino.ASIA_PACIFICO.value:
        recs["normativa_documental"].append(
            "CERTIFICADO DE ORIGEN & FUMIGACIÓN: Certificado de Origen TLC correspondiente y constancia de tratamiento cuarentenario o fumigación "
            "según directrices fitosanitarias de la autoridad de destino (AQSIQ / MAFF)."
        )
    else:
        recs["normativa_documental"].append(
            "RÉGIMEN ALADI / CAN: Certificado de origen para preferencias arancelarias subregionales y registro sanitario INVIMA de exportación."
        )

    return recs

# 📦 Sistema de Lectura del Entorno PESTEL
## Smurfit WestRock Colombia — Planta Industrial Yumbo (Valle del Cauca)

Aplicación web estratégica desarrollada en **Python** y **Streamlit** para la vigilancia, captura, análisis multidimensional y toma de decisiones sobre el entorno nacional e internacional de la multinacional papelera y de empaques **Smurfit WestRock Colombia**.

---

## 🏢 Contexto Empresarial

- **Empresa:** Smurfit WestRock Colombia (resultado de la fusión global de Smurfit Kappa y WestRock en julio de 2024, líder mundial en empaques sostenibles de papel y cartón corrugado).
- **Sede Principal / Planta:** Complejo Industrial Yumbo, Carrera 1 # 15-05, Yumbo, Valle del Cauca. Alberga molinos de papel reciclado y kraftliner, corrugadoras de alta velocidad y la división de sacos de papel.
- **Operaciones Forestales:** Más de 68.000 hectáreas de plantaciones comerciales de pino y eucalipto certificadas FSC® en Cauca, Valle, Caldas, Quindío, Risaralda y Tolima.
- **Economía Circular:** Mayor reciclador de papel y cartón en Colombia (más de 220.000 toneladas anuales recuperadas).

---

## 📐 Metodología PESTEL

El sistema analiza de forma estructurada las seis dimensiones del macroentorno:

| Pilar | Icono | Foco Estratégico en Smurfit WestRock |
|---|:---:|---|
| **Político** | 🏛️ | Subsidios a silvicultura comercial (CIF Forestal), orden público y bloqueos en el corredor Panamericano (Cauca-Valle), aranceles de comercio exterior. |
| **Económico** | 📈 | Auge de empaques para agroexportación (aguacate Hass, flores), crecimiento del comercio electrónico, inflación y volatilidad de la TRM. |
| **Social** | 👥 | Demanda ciudadana por empaques libres de plástico, relación comunitaria en zonas forestales (Fundación Smurfit WestRock), talento técnico en Yumbo. |
| **Tecnológico** | ⚙️ | Innovación en barreras biodegradables (tecnología *AquaStop*), gemelos digitales y sensores IoT para mantenimiento predictivo en molinos. |
| **Ecológico** | 🌱 | Transición por la Ley 2232 de plásticos de un solo uso, estrés hídrico en la cuenca del Río Cauca y cogeneración con calderas de biomasa. |
| **Legal** | ⚖️ | Metas REP de envases y empaques (Res. 1407/2018), normatividad de vertimientos industriales de la CVC e impuesto nacional a plásticos. |

---

## 📋 Cumplimiento de Requisitos Funcionales

| Requisito Funcional | Descripción Oficial | Implementación en la Aplicación |
|---|---|---|
| **RF-01. Captura de información del entorno** | Registro de información relevante nacional e internacional mediante fuentes públicas e informes. | Formulario interactivo en **Monitor del Entorno** y módulo de **Captura Asistida** desde fuentes oficiales. |
| **RF-02. Clasificación PESTEL** | Clasificar cada factor en una de las 6 dimensiones PESTEL. | Selector en formulario y vistas analíticas desglosadas en la página **Análisis PESTEL**. |
| **RF-03. Trazabilidad de las fuentes** | Almacenar fuente, URL, fecha de publicación y fecha de consulta para verificar procedencia. | Campos auditables en base de datos SQLite y enlaces clickables directos en todas las fichas. |
| **RF-04. Evaluación de impactos** | Evaluar probabilidad (1-5), impacto (1-5), urgencia y efecto potencial sobre la empresa. | Sliders de evaluación, cálculo de severidad ($P \times I$) y campo detallado del impacto en Yumbo. |
| **RF-05. Identificación de riesgos y oportunidades** | Priorizar factores que representen riesgos u oportunidades para Smurfit WestRock. | Matriz 5x5 interactiva de Plotly con zonas de calor y rankings clasificados por severidad. |
| **RF-06. Visualización estratégica** | Tablero con indicadores, filtros, gráficos interactivos y tablas organizadas por PESTEL. | Radar PESTEL, matriz 5x5, barras comparativas, gráficos de donut y tablas dinámicas. |
| **RF-07. Apoyo a la toma de decisiones** | Recomendaciones vinculadas a factores evaluados, evidencia, prioridad y plan de acción. | Módulo de **Recomendaciones** vinculado a factores, con áreas responsables y control de estado. |
| **RF-08. Seguimiento y actualización** | Registrar nuevas observaciones, editar factores y consultar bitácora histórica. | Módulo de **Seguimiento Histórico** con timeline de novedades y formulario de reevaluación. |
| **RF-09. Generación de informes** | Generar informes ejecutivos que resuman cambios, impactos, riesgos y recomendaciones. | Generador dinámico descargable en **PDF formal (ReportLab)** y **Excel (.xlsx, openpyxl)**. |
| **Gestión de Roles y Permisos** | Control de acceso basado en roles dentro del aplicativo: Roles (**Usuarios**, **Decisores**, **Diseñadores**) con responsabilidades y permisos diferenciados. | Selector de rol y perfil activo en panel lateral, control de acceso granular (RBAC) en formularios de captura, gobernanza de decisiones, calibración técnica y auditoría. |

---

## 👥 Modelo de Roles y Control de Acceso

El aplicativo implementa un modelo de **Control de Acceso Basado en Roles (RBAC)** con tres perfiles funcionales, garantizando la rigurosidad fáctica del análisis y la gobernanza directiva en **Smurfit WestRock Colombia (Planta Yumbo)**:

### 1. 🎨 Diseñadores (Modelado & Arquitectura PESTEL)
- **Propósito:** Modelado del macroentorno, parametrización metodológica y calibración técnica del sistema.
- **Responsabilidades:**
  - Registro y captura de nuevos factores del entorno nacional, internacional y del Valle del Cauca (RF-01).
  - Calibración cuantitativa de variables metodológicas: Probabilidad (1 - 5), Impacto (1 - 5), Nivel de Urgencia y cálculo de severidad ($P \times I$) (RF-04).
  - Verificación y trazabilidad de fuentes oficiales públicas autorizadas (MADS, CVC, ANDI, MinAgricultura) (RF-03).
  - Precarga de señales asistidas y edición estructural completa de fichas técnicas de factores (RF-08).
  - Operaciones administrativas y restablecimiento de la base de datos a los valores semilla iniciales.
- **Perfil de referencia en el aplicativo:** `Ing. Sofía Ramírez` *(Especialista en Inteligencia Competitiva & PESTEL)*.

### 2. 👔 Decisores (Gobernanza & Toma de Decisiones Estratégicas)
- **Propósito:** Liderazgo directivo, priorización de inversiones y toma de decisiones corporativas para la planta de molinos y corrugadoras de Yumbo.
- **Responsabilidades:**
  - Formulación, aprobación y actualización de recomendaciones estratégicas vinculadas a la evidencia fáctica (RF-07).
  - Asignación de áreas responsables de ejecución (*Operaciones & Molinos*, *Cadena de Suministro*, *División Forestal*, *Sostenibilidad*, *Jurídico*).
  - Gobernanza del plan de acción: transición y aprobación de estados (*Planificada*, *En Ejecución*, *Completada*).
  - Redefinición del estado estratégico de factores críticos (*Activo / Crítico*, *En Mitigación / Acción*, *Mitigado / Capitalizado*, *Cerrado*).
  - Generación y exportación de informes ejecutivos en PDF y Excel para la Junta Directiva (RF-09).
- **Perfil de referencia en el aplicativo:** `Dr. Carlos Mendoza` *(Director General de Operaciones & Estrategia Yumbo)*.

### 3. 👥 Usuarios (Consulta General & Auditoría Operativa)
- **Propósito:** Consulta diagnóstica, vigilancia situacional, análisis estratégico de planta y auditoría del entorno.
- **Responsabilidades:**
  - Acceso irrestricto de consulta y visualización a los tableros ejecutivos, Radar PESTEL de 6 dimensiones (RF-02, RF-06) y Matriz de Riesgos y Oportunidades 5x5 (RF-04, RF-05).
  - Exploración del directorio de fuentes oficiales autorizadas y enlaces de verificación fáctica (RF-03).
  - Registro de novedades de campo u observaciones preliminares en la bitácora histórica de seguimiento (RF-08), quedando identificados con su rol.
  - Generación y descarga de informes de análisis estratégico en formatos PDF y Excel (RF-09).
  - Modo de solo lectura seguro: no pueden modificar la calibración técnica de factores ni alterar unilateralmente las decisiones aprobadas.
- **Perfil de referencia en el aplicativo:** `Laura Gómez` *(Analista de Monitoreo & Operaciones de Planta)*.

---

### 🛡️ Matriz de Control de Acceso (RBAC)

| Capacidad / Operación en el Sistema | Requisito Relacionado | Usuario (Consulta) | Decisor (Estrategia) | Diseñador (Modelado) |
|---|:---:|:---:|:---:|:---:|
| Visualización de Tableros Ejecutivos y KPIs | RF-06 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Radar PESTEL de 6 Dimensiones | RF-02, RF-06 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Matriz 5x5 de Riesgos y Oportunidades | RF-04, RF-05 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Directorio y Trazabilidad de Fuentes Documentales | RF-03 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Descarga de Informes Formales (PDF y Excel) | RF-09 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Registro de Observaciones en Bitácora Histórica | RF-08 | ✅ Permitido | ✅ Permitido | ✅ Permitido |
| Captura y Registro de Nuevos Factores del Entorno | RF-01 | 🔒 Solo Lectura | 🔒 Solo Lectura | ✅ Permitido |
| Precarga de Señales Oficiales Asistidas | RF-01, RF-03 | 🔒 Solo Lectura | 🔒 Solo Lectura | ✅ Permitido |
| Calibración de Probabilidad (1-5) e Impacto (1-5) | RF-04 | 🔒 Solo Lectura | 🔒 Preservado | ✅ Permitido |
| Edición Estructural de Factores y Fichas Técnicas | RF-08 | 🔒 Solo Lectura | 🔒 Preservado | ✅ Permitido |
| Formulación de Recomendaciones Estratégicas | RF-07 | 🔒 Solo Lectura | ✅ Permitido | ✅ Sugerencias |
| Aprobación y Cambio de Estado en Planes de Acción | RF-07 | 🔒 Solo Lectura | ✅ Permitido | 🔒 Restringido |
| Cambio de Estado Estratégico de Factores Críticos | RF-08 | 🔒 Solo Lectura | ✅ Permitido | ✅ Permitido |
| Restablecimiento de Base de Datos Semilla | Admin | 🔒 Restringido | 🔒 Restringido | ✅ Permitido |

---

### 🔐 Seguridad Básica y Protección de Acceso

1. **Hashing Criptográfico de Contraseñas (PBKDF2-HMAC-SHA256):**
   - Las contraseñas nunca se almacenan en texto plano.
   - Se utiliza la función de derivación de claves `PBKDF2-HMAC-SHA256` con **100.000 iteraciones** y una sal criptográfica única e irrepetible de 16 bytes generada con `secrets.token_bytes(16)`.
   - La verificación se realiza en tiempo constante mediante `secrets.compare_digest()` para mitigar vulnerabilidades de canal lateral (*timing attacks*).

2. **Límite de Inicios de Sesión y Bloqueo Temporal (Fuerza Bruta):**
   - El sistema registra los intentos fallidos en la columna `intentos_fallidos`.
   - Si un usuario ingresa una contraseña incorrecta **5 veces consecutivas**, la cuenta queda bloqueada automáticamente durante **5 minutos** mediante la marca temporal `bloqueado_hasta`.
   - Tras el bloqueo, cualquier intento posterior informa los minutos restantes antes de permitir reintentos.
   - Al autenticarse correctamente, el contador de fallos se restablece a cero y se actualiza `ultimo_acceso`.

3. **Navegación Dinámica y Barrera de Autenticación:**
   - La aplicación bloquea el acceso a todas las pantallas internas mediante un *gatekeeper* que intercepta peticiones no autenticadas, presentando únicamente el formulario de inicio de sesión seguro.
   - El árbol de navegación de Streamlit se adapta dinámicamente al rol autenticado: un `Usuario` no tiene en su menú el módulo de captura de factores ni la formulación de decisiones.

4. **Credenciales Institucionales Preconfiguradas (Prototipo):**

| Rol | Correo Corporativo | Contraseña de Prueba | Usuario / Cargo |
|---|---|---|---|
| **🎨 Diseñador** | `disenador@smurfitwestrock.com` | `Disenador2026*` | Ing. Sofía Ramírez *(Inteligencia & PESTEL)* |
| **👔 Decisor** | `decisor@smurfitwestrock.com` | `Decisor2026*` | Dr. Carlos Mendoza *(Gerente de Operaciones Yumbo)* |
| **👥 Usuario** | `usuario@smurfitwestrock.com` | `Usuario2026*` | Laura Gómez *(Monitoreo Operativo de Planta)* |

---

### ☁️ Escalabilidad y Migración a Supabase (PostgreSQL)

La estructura de datos en SQLite fue diseñada con tipos y restricciones estandarizadas para permitir una migración fluida a **Supabase (PostgreSQL)** cuando el proyecto escale a la nube:

1. **Script de Migración SQL Incluido:**
   - El archivo [`supabase_migration.sql`](file:///c:/herramienta%20ti/lectura-de-entorno/supabase_migration.sql) contiene el esquema completo en sintaxis estándar de PostgreSQL con llaves foráneas, índices, disparadores para `updated_at` y datos semilla.

2. **Row Level Security (RLS) en Supabase:**
   - En Supabase se habilitan políticas RLS que replican las reglas del prototipo a nivel de motor de base de datos:
     - `factores`: Lectura pública/autenticada, pero `INSERT`, `UPDATE` y `DELETE` restringidos exclusivamente a tokens JWT con rol `Diseñador`.
     - `recomendaciones`: Lectura general, creación habilitada para `Decisor` y `Diseñador`, y cambio de estado restringido a `Decisor`.
     - `historial_seguimiento`: Inserción auditada para todos los usuarios autenticados.

3. **Conexión Directa desde Streamlit:**
   - Para conectar la aplicación a Supabase al escalar, basta con configurar `st.secrets["supabase_url"]` y `st.secrets["supabase_key"]` o la cadena de conexión estándar de PostgreSQL (`postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres`) sustituyendo las llamadas SQLite en `database.py`.

---

## 🏗️ Arquitectura de la Solución

```
c:\lectura-de-entorno\
├── app.py                      # Punto de entrada con gatekeeper de autenticación y navegación por rol
├── auth.py                     # Módulo de seguridad: PBKDF2 hashing, intentos fallidos y bloqueo
├── database.py                 # Gestión SQLite: esquemas, migraciones, seed data y consultas
├── models.py                   # Enums PESTEL, escalas de severidad, roles y permisos
├── supabase_migration.sql      # Script de migración DDL + Row Level Security (RLS) para Supabase
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación integral
├── utils/
│   ├── visualizer.py          # Gráficos Plotly: Radar PESTEL, Matriz 5x5, Barras y Donut
│   ├── report_generator.py    # Generación de reportes ejecutivos en PDF y Excel
│   └── external_sources.py    # Directorio de fuentes autorizadas y señales asistidas
└── views/
    ├── login.py               # Inicio de sesión con PBKDF2, bloqueo temporal y accesos rápidos
    ├── home.py                # Inicio Ejecutivo: KPIs, radar, alertas críticas y resumen
    ├── monitor.py             # Monitor del Entorno: Captura (RF-01) y Trazabilidad (RF-03)
    ├── pestel_analysis.py     # Análisis PESTEL: Fichas técnicas y tabs por dimensión (RF-02, RF-06)
    ├── risk_opportunity.py    # Matriz 5x5: Evaluación de impactos y priorización (RF-04, RF-05)
    ├── recommendations.py     # Plan de Acción y Decisiones Gerenciales (RF-07)
    ├── tracking.py            # Seguimiento, edición y bitácora histórica (RF-08)
    └── reports.py             # Generador y exportador de informes en PDF y Excel (RF-09)
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Requisitos Previos
Tener instalado **Python 3.10+**.

### 2. Instalación de Dependencias
Abra su terminal en la carpeta del proyecto y ejecute:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
Inicie el servidor local de Streamlit:
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en su navegador web en:
`http://localhost:8501`

---

## 🎨 Sistema de Diseño: Clinical Blueprint on Frosted Paper (shadcn/ui)

La aplicación implementa una estética de ingeniería limpia, neutral y monocromática:
- **Canvas (`#f5f5f5`):** Fondo global de página y superficies secundarias.
- **Paper (`#ffffff`):** Superficies de tarjetas (`24px` de radio) con bordes hairline (`#e5e5e5`) y sombra de elevación sutil.
- **Surface Alt (`#fafafa`):** Panel lateral de navegación (sidebar) integrado sin líneas divisorias agresivas.
- **Ink (`#0a0a0a`) & Ink Soft (`#171717`):** Textos principales, botones primarios en píldora (`18px` de radio) y tipografía Geist/Inter con tracking ajustado en titulares (`-0.05em`).
- **Mid Gray (`#737373`):** Etiquetas secundarias, textos descriptivos y métricas de soporte.
- **Ember (`#e7000b`):** Único acento cromático destructivo, reservado exclusivamente para riesgos críticos/extremos y estados de error.

---

## 💡 Justificación Tecnológica (Académica)

- **Python + Streamlit:** Permite desarrollar una interfaz ejecutiva moderna, responsiva y multipágina sin dispersar esfuerzos en frontend separado, concentrándose en el análisis estratégico PESTEL.
- **SQLite:** Base de datos relacional integrada de cero configuración que asegura persistencia local, integridad referencial y auditoría histórica.
- **Plotly:** Gráficos vectoriales e interactivos de nivel corporativo (Radar polar y matrices de calor 5x5) adaptados a la estética monocromática.
- **ReportLab & openpyxl:** Generación programática de informes formales descargables con membrete corporativo en formatos universales (PDF y Excel).

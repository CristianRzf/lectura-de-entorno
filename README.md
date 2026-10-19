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

---

## 🏗️ Arquitectura de la Solución

```
c:\lectura-de-entorno\
├── app.py                      # Punto de entrada principal con st.navigation y diseño corporativo
├── database.py                 # Gestión SQLite: esquemas, migraciones, seed data y consultas
├── models.py                   # Enums PESTEL, escalas de severidad y fórmulas de cálculo
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación integral
├── utils/
│   ├── visualizer.py          # Gráficos Plotly: Radar PESTEL, Matriz 5x5, Barras y Donut
│   ├── report_generator.py    # Generación de reportes ejecutivos en PDF y Excel
│   └── external_sources.py    # Directorio de fuentes autorizadas y señales asistidas
└── views/
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

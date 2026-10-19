"""
utils/visualizer.py - Generador de visualizaciones interactivas con Plotly para el análisis PESTEL.
Estilizado bajo la estética "clinical blueprint on frosted paper" (monocromático con acento #e7000b).
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from models import PESTEL_META, PESTELCategory

FONT_FAMILY = "Geist, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

def create_radar_chart(df: pd.DataFrame) -> go.Figure:
    """Genera un gráfico de radar en estética limpia monocromática."""
    categories = [c.value for c in PESTELCategory]
    
    impact_data = []
    severidad_data = []

    for cat in categories:
        sub = df[df["categoria_pestel"] == cat]
        if not sub.empty:
            impact_data.append(round(sub["impacto"].mean(), 2))
            severidad_data.append(round(sub["puntuacion_severidad"].mean(), 2))
        else:
            impact_data.append(0)
            severidad_data.append(0)

    cat_closed = categories + [categories[0]]
    impact_closed = impact_data + [impact_data[0]]
    severidad_closed = [s / 5.0 for s in severidad_data] + [severidad_data[0] / 5.0]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=impact_closed,
        theta=cat_closed,
        fill='toself',
        name='Impacto Promedio (1-5)',
        line=dict(color='#0a0a0a', width=2),
        fillcolor='rgba(10, 10, 10, 0.06)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=severidad_closed,
        theta=cat_closed,
        fill='toself',
        name='Severidad Relativa (Base 5)',
        line=dict(color='#737373', width=1.5, dash='dot'),
        fillcolor='rgba(115, 115, 115, 0.04)'
    ))

    fig.update_layout(
        font=dict(family=FONT_FAMILY, color="#0a0a0a"),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                gridcolor='#e5e5e5',
                tickfont=dict(size=10, color="#737373")
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#0a0a0a", family=FONT_FAMILY),
                rotation=90,
                direction="clockwise",
                gridcolor='#e5e5e5'
            ),
            bgcolor='#ffffff'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#737373")
        ),
        margin=dict(l=30, r=30, t=20, b=40),
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_matrix_5x5(df: pd.DataFrame, factor_type: str = "Todos") -> go.Figure:
    """Matriz 5x5 de Probabilidad vs Impacto en estética clínica y limpia."""
    if factor_type != "Todos":
        df_plot = df[df["tipo"] == factor_type].copy()
    else:
        df_plot = df.copy()

    if df_plot.empty:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text="No hay factores con los filtros seleccionados", showarrow=False, font=dict(family=FONT_FAMILY, size=13, color="#737373"))],
            height=440
        )
        return fig

    np.random.seed(42)
    df_plot["prob_jitter"] = df_plot["probabilidad"] + np.random.uniform(-0.12, 0.12, size=len(df_plot))
    df_plot["imp_jitter"] = df_plot["impacto"] + np.random.uniform(-0.12, 0.12, size=len(df_plot))

    fig = go.Figure()

    # Zonas sutiles de fondo en escala de grises
    # Cuadrante Crítico (esquina superior derecha) con tinte muy sutil
    fig.add_shape(type="rect", x0=3.5, y0=3.5, x1=5.5, y1=5.5,
                  fillcolor="rgba(231, 0, 11, 0.04)", line=dict(color="#e5e5e5", width=1), layer="below")
    # Cuadrante Bajo
    fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=2.5, y1=2.5,
                  fillcolor="rgba(245, 245, 245, 0.8)", line=dict(color="#e5e5e5", width=1), layer="below")

    # Líneas divisorias tenues
    fig.add_vline(x=3.0, line_dash="dash", line_color="#e5e5e5", line_width=1)
    fig.add_hline(y=3.0, line_dash="dash", line_color="#e5e5e5", line_width=1)

    # Renderizar puntos: riesgos críticos en #e7000b, otros riesgos en #171717, oportunidades en #0a0a0a
    for t_val, default_color, symb in [("Riesgo", "#171717", "diamond"), ("Oportunidad", "#0a0a0a", "circle")]:
        sub = df_plot[df_plot["tipo"] == t_val]
        if not sub.empty:
            sub_hover = []
            point_colors = []
            for _, r in sub.iterrows():
                txt = (
                    f"<b>[{r['codigo']}] {r['titulo']}</b><br>"
                    f"Dimensión: {r['categoria_pestel']} | Tipo: {r['tipo']}<br>"
                    f"Probabilidad: {r['probabilidad']}/5 | Impacto: {r['impacto']}/5<br>"
                    f"Severidad: {r['puntuacion_severidad']}/25 ({r['urgencia']})<br>"
                    f"Efecto: {r['efecto_empresa'][:100]}..."
                )
                sub_hover.append(txt)
                if r["tipo"] == "Riesgo" and r["puntuacion_severidad"] >= 16:
                    point_colors.append("#e7000b")  # Destructive red solo para crítico
                elif r["tipo"] == "Riesgo":
                    point_colors.append("#171717")
                else:
                    point_colors.append("#0a0a0a")

            fig.add_trace(go.Scatter(
                x=sub["prob_jitter"],
                y=sub["imp_jitter"],
                mode='markers+text',
                marker=dict(
                    size=14,
                    color=point_colors,
                    symbol=symb,
                    line=dict(color='#ffffff', width=2),
                    opacity=0.95
                ),
                text=sub["codigo"],
                textposition="top center",
                textfont=dict(size=9, family=FONT_FAMILY, color="#0a0a0a"),
                hoverinfo="text",
                hovertext=sub_hover,
                name=f"{t_val}s ({len(sub)})"
            ))

    # Anotaciones limpias
    fig.add_annotation(x=4.8, y=5.25, text="ZONA CRÍTICA / ESTRATÉGICA", showarrow=False,
                       font=dict(size=9, color="#737373", family=FONT_FAMILY))
    fig.add_annotation(x=1.2, y=0.75, text="ZONA BAJA / RESIDUAL", showarrow=False,
                       font=dict(size=9, color="#737373", family=FONT_FAMILY))

    fig.update_layout(
        font=dict(family=FONT_FAMILY, color="#0a0a0a"),
        title=dict(
            text="Matriz 5x5: Probabilidad vs Impacto Organizacional",
            font=dict(size=14, color="#0a0a0a", family=FONT_FAMILY),
            x=0.02
        ),
        xaxis=dict(
            title=dict(text="Probabilidad de Ocurrencia (1 a 5)", font=dict(size=12, color="#737373")),
            range=[0.5, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["1: Muy Baja", "2: Baja", "3: Media", "4: Alta", "5: Muy Alta"],
            gridcolor="#e5e5e5",
            tickfont=dict(size=11, color="#737373"),
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="Impacto en Smurfit WestRock (1 a 5)", font=dict(size=12, color="#737373")),
            range=[0.5, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["1: Leve", "2: Menor", "3: Moderado", "4: Crítico", "5: Mayor"],
            gridcolor="#e5e5e5",
            tickfont=dict(size=11, color="#737373"),
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#737373")
        ),
        margin=dict(l=45, r=30, t=40, b=60),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#ffffff'
    )

    return fig

def create_pestel_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Barras agrupadas de Riesgos vs Oportunidades en paleta neutral."""
    categories = [c.value for c in PESTELCategory]
    
    riesgos_counts = []
    oportunidades_counts = []

    for cat in categories:
        sub = df[df["categoria_pestel"] == cat]
        riesgos_counts.append(len(sub[sub["tipo"] == "Riesgo"]))
        oportunidades_counts.append(len(sub[sub["tipo"] == "Oportunidad"]))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=oportunidades_counts,
        name='Oportunidades',
        marker_color='#0a0a0a',
        text=oportunidades_counts,
        textposition='auto',
        hoverinfo='x+y+name'
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=riesgos_counts,
        name='Riesgos',
        marker_color='#737373',
        text=riesgos_counts,
        textposition='auto',
        hoverinfo='x+y+name'
    ))

    fig.update_layout(
        barmode='group',
        font=dict(family=FONT_FAMILY, color="#0a0a0a"),
        title=dict(
            text="Distribución de Riesgos y Oportunidades por Pilar PESTEL",
            font=dict(size=14, color="#0a0a0a", family=FONT_FAMILY),
            x=0.02
        ),
        xaxis=dict(gridcolor="#e5e5e5", tickfont=dict(size=11, color="#0a0a0a")),
        yaxis=dict(title=dict(text="Total Factores", font=dict(size=11, color="#737373")), gridcolor="#e5e5e5", dtick=1, tickfont=dict(size=11, color="#737373")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#737373")
        ),
        margin=dict(l=35, r=20, t=35, b=45),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_urgency_donut(df: pd.DataFrame) -> go.Figure:
    """Gráfico donut monocromático con #e7000b reservado para urgencia inmediata."""
    counts = df["urgencia"].value_counts().reset_index()
    counts.columns = ["urgencia", "total"]

    color_map = {
        "Inmediata (< 3 meses)": "#e7000b",  # Red accent exclusivo para alerta inmediata
        "Alta (3 - 6 meses)": "#171717",
        "Media (6 - 12 meses)": "#737373",
        "Baja (> 1 año)": "#d4d4d4"
    }
    colors = [color_map.get(u, "#a3a3a3") for u in counts["urgencia"]]

    fig = go.Figure(data=[go.Pie(
        labels=counts["urgencia"],
        values=counts["total"],
        hole=0.62,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textfont=dict(family=FONT_FAMILY, size=11),
        insidetextorientation='radial'
    )])

    fig.update_layout(
        font=dict(family=FONT_FAMILY, color="#0a0a0a"),
        title=dict(
            text="Horizonte de Urgencia Temporal",
            font=dict(size=14, color="#0a0a0a", family=FONT_FAMILY),
            x=0.02
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=35, b=20),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

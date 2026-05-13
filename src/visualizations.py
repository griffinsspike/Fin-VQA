"""
Fin-VQA Visualization Engine Module.
Creates professional Midas-styled candlestick charts with technical indicators
using Plotly graph_objects.
"""

import io
import logging

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import pandas as pd

from src.config import CHART_CONFIG, COLORS

logger = logging.getLogger(__name__)


def create_candlestick_chart(
    df: pd.DataFrame,
    ticker: str,
    show_ma20: bool = True,
    show_ma50: bool = True,
    show_rsi: bool = True,
    show_volume: bool = True,
) -> go.Figure:
    """
    Created a professional Midas-styled candlestick chart with optional indicators.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with OHLCV + indicator columns (RSI, MA20, MA50).
    ticker : str
        Ticker symbol for the chart title.
    show_ma20, show_ma50, show_rsi, show_volume : bool
        Toggle indicator visibility.

    Returns
    -------
    go.Figure
        Interactive Plotly figure.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Veri bulunamadı / No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=COLORS["gold"]),
        )
        return fig

    # ── Convert DatetimeIndex to strings for Plotly/Kaleido compatibility ──
    df = df.copy()
    x_dates = df.index.strftime("%Y-%m-%d").tolist()

    # ── Determine subplot layout ──
    rows = 1
    row_heights = [0.7]
    subplot_titles = [f""]

    if show_rsi and "RSI" in df.columns:
        rows += 1
        row_heights.append(0.15)
        subplot_titles.append("RSI (14)")

    if show_volume:
        rows += 1
        row_heights.append(0.15)
        subplot_titles.append("Hacim")

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # ──────────────────────────────────────────
    # ROW 1: Candlestick + Moving Averages
    # ──────────────────────────────────────────
    fig.add_trace(
        go.Candlestick(
            x=x_dates,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing=dict(
                line=dict(color=COLORS["up"], width=1),
                fillcolor=COLORS["up"],
            ),
            decreasing=dict(
                line=dict(color=COLORS["down"], width=1),
                fillcolor=COLORS["down"],
            ),
            name="Fiyat",
            showlegend=True,
        ),
        row=1, col=1,
    )

    # MA20 overlay
    if show_ma20 and "MA20" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_dates,
                y=df["MA20"],
                line=dict(color=COLORS["ma20"], width=CHART_CONFIG["line_width"], dash="solid"),
                name="MA20",
                opacity=0.85,
            ),
            row=1, col=1,
        )

    # MA50 overlay
    if show_ma50 and "MA50" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_dates,
                y=df["MA50"],
                line=dict(color=COLORS["ma50"], width=CHART_CONFIG["line_width"], dash="solid"),
                name="MA50",
                opacity=0.85,
            ),
            row=1, col=1,
        )

    # ──────────────────────────────────────────
    # ROW 2: RSI
    # ──────────────────────────────────────────
    current_row = 2
    if show_rsi and "RSI" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_dates,
                y=df["RSI"],
                line=dict(color=COLORS["rsi"], width=CHART_CONFIG["line_width"]),
                name="RSI (14)",
                fill="tozeroy",
                fillcolor="rgba(171, 71, 188, 0.1)",
            ),
            row=current_row, col=1,
        )

        # Overbought / Oversold lines
        fig.add_hline(
            y=70, line_dash="dash", line_color="rgba(255, 23, 68, 0.5)",
            line_width=1, row=current_row, col=1,
            annotation_text="Aşırı Alım (70)",
            annotation_position="top right",
            annotation_font_size=9,
            annotation_font_color=COLORS["down"],
        )
        fig.add_hline(
            y=30, line_dash="dash", line_color="rgba(0, 200, 83, 0.5)",
            line_width=1, row=current_row, col=1,
            annotation_text="Aşırı Satım (30)",
            annotation_position="bottom right",
            annotation_font_size=9,
            annotation_font_color=COLORS["up"],
        )
        fig.add_hline(
            y=50, line_dash="dot", line_color="rgba(255, 215, 0, 0.3)",
            line_width=1, row=current_row, col=1,
        )

        # Fixed RSI y-axis range
        fig.update_yaxes(range=[0, 100], row=current_row, col=1)
        current_row += 1

    # ──────────────────────────────────────────
    # ROW 3: Volume
    # ──────────────────────────────────────────
    if show_volume:
        # Color volume bars based on price direction
        vol_colors = [
            COLORS["up"] if c >= o else COLORS["down"]
            for c, o in zip(df["Close"], df["Open"])
        ]

        fig.add_trace(
            go.Bar(
                x=x_dates,
                y=df["Volume"],
                marker_color=vol_colors,
                marker_line_width=0,
                name="Hacim",
                opacity=0.6,
            ),
            row=current_row, col=1,
        )
    # ──────────────────────────────────────────
    # Layout: Claude Design (Navy + Teal)
    # ──────────────────────────────────────────
    fig.update_layout(
        title=None,
        height=CHART_CONFIG["height"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family=CHART_CONFIG["font_family"], size=11),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=10, color="#475569"), bgcolor="rgba(0,0,0,0)",
        ),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=20),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111827", font_size=11, font_family=CHART_CONFIG["font_family"], bordercolor="rgba(0,212,170,0.3)"),
    )

    for i in range(1, rows + 1):
        yaxis_name = f"yaxis{i}" if i > 1 else "yaxis"
        fig.update_layout(**{yaxis_name: dict(
            gridcolor=CHART_CONFIG["gridcolor"], zerolinecolor="rgba(0,0,0,0)",
            showgrid=True, side="right", tickfont=dict(size=10, color="#475569"),
        )})

    fig.update_xaxes(gridcolor=CHART_CONFIG["gridcolor"], showgrid=False, rangeslider_visible=False,
                     tickfont=dict(size=10, color="#475569"))

    for annotation in fig.layout.annotations:
        annotation.font = dict(size=10, color="#475569", family=CHART_CONFIG["font_family"])

    logger.info(f"Candlestick chart was created for {ticker}.")
    return fig


def chart_to_image(fig: go.Figure, width: int = 1200, height: int = 700) -> Image.Image:
    """
    Converted a Plotly figure to a PIL Image for VQA engine consumption.

    Parameters
    ----------
    fig : go.Figure
        The Plotly figure to convert.
    width, height : int
        Image dimensions in pixels.

    Returns
    -------
    PIL.Image.Image
        The chart as a PIL Image object.
    """
    try:
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
        img = Image.open(io.BytesIO(img_bytes))
        logger.info("Chart was successfully converted to image for VQA input.")
        return img
    except Exception as e:
        logger.error(f"Chart to image conversion failed: {e}")
        # Created a placeholder image
        img = Image.new("RGB", (width, height), color=(14, 17, 23))
        return img


def create_metric_card_html(
    label: str,
    value: str,
    delta: str = "",
    delta_color: str = "",
    icon: str = "",
) -> str:
    """
    Generated styled HTML for a metric card component.

    Parameters
    ----------
    label : str
        Metric label text.
    value : str
        Main metric value.
    delta : str
        Change indicator text.
    delta_color : str
        Color for the delta text.
    icon : str
        Emoji or icon character.

    Returns
    -------
    str
        HTML string for the metric card.
    """
    delta_html = ""
    if delta:
        color = delta_color or COLORS["text_secondary"]
        delta_html = f'<div style="color:{color};font-size:12px;margin-top:4px;">{delta}</div>'

    return f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_card']} 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px 18px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    ">
        <div style="font-size:22px;margin-bottom:4px;">{icon}</div>
        <div style="
            color:{COLORS['text_secondary']};
            font-size:11px;
            text-transform:uppercase;
            letter-spacing:1px;
            margin-bottom:6px;
            font-weight:500;
        ">{label}</div>
        <div style="
            color:{COLORS['gold']};
            font-size:20px;
            font-weight:700;
            font-family:{CHART_CONFIG['font_family']};
        ">{value}</div>
        {delta_html}
    </div>
    """

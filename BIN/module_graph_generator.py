# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
# CODRUG – Computational Drug Discovery Platform
# Copyright (C) 2024–2026 Moisés Maia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""Funções de plotagem da aba PLOT (Gerador de Gráficos) do CODRUG.

Código portado do GraphGenerator (mesmo autor), sem nenhuma dependência de Qt: cada plotter recebe
um DataFrame e devolve uma matplotlib Figure. A interface (aba PLOT em CODRUG.py) só escolhe as
colunas, monta o DataFrame de entrada e exibe a figura devolvida.

Convenção do DataFrame de entrada dos plotters 1D (ver extract_x_y): coluna "X" explícita (ou a
primeira coluna não numérica) como eixo X e as demais colunas numéricas como séries Y."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    _HAS_SEABORN = True
except Exception:
    sns = None
    _HAS_SEABORN = False

PALETTES = ["Dark2", "Set2", "Set3", "tab10", "tab20", "Paired", "Accent",
            "viridis", "plasma", "magma", "cividis"]
TREND_MODES = ["None", "Linear(1st degree)", "Quadratic(2nd degree)", "Cubic(3rd degree)",
               "Moving Average", "Logarithmic", "Exponential"]
COLOR_MODE_SINGLE = "Single color (all series)"
COLOR_MODE_PALETTE = "Palette (multi-color)"
# Trendline só vale para estes gráficos (nos demais, é ignorada).
TREND_ALLOWED = {"Bar", "Line", "Scatter", "Area (Stacked)", "Area (Overlapped)"}
CHART_TYPES_1D = ["Bar", "Line", "Scatter", "Area (Stacked)", "Area (Overlapped)",
                  "Box Plot", "Heatmap", "Violin", "Histogram", "Density(KDE)", "Sankey"]
SANKEY_MAX_NODES_PER_STAGE = 30   # acima disso o diagrama vira um borrão ilegível
# Box Plot e Violin resumem os valores de colunas Y numéricas; X é opcional e apenas agrupa as linhas em categorias.
DISTRIBUTION_CHARTS = ("Box Plot", "Violin")
DISTRIBUTION_MAX_GROUPS = 30       # mais categorias que isso em X viram dezenas de caixas ilegíveis
CHART_TYPES_2D = ["Scatter", "Line", "Area (Stacked)", "Area (Overlapped)"]
CHART_TYPES_3D = ["Scatter"]


def _series_to_numeric(s: pd.Series) -> pd.Series:
    # Converts numbers with comma decimal (e.g., "3,14") to float.
    if s.dtype == object:
        s2 = s.astype(str).str.strip()
        # remove NBSP if exists
        s2 = s2.str.replace("\u00a0", "", regex=False)
        # decimal comma -> dot
        s2 = s2.str.replace(",", ".", regex=False)
        return pd.to_numeric(s2, errors="coerce")
    return pd.to_numeric(s, errors="coerce")

def safe_series_name(name, suffix: str = "(count)") -> str:
    """Nome de coluna seguro para ser montado ao lado da coluna reservada "X" (extract_x_y trata,
    sem diferenciar maiúsculas, uma coluna chamada "X" como o eixo X). Uma série com esse nome
    sobrescreveria o eixo e o gráfico perderia o X ("No numeric columns found for Y")."""
    name = str(name)
    return f"{name} {suffix}" if name.strip().lower() == "x" else name


def _find_group_column(df: pd.DataFrame):
    """Procura uma coluna de grupos por nome (Class/Classes/Group/Groups)."""
    targets = {"class", "classes", "group", "groups"}
    for c in df.columns:
        if str(c).strip().lower() in targets:
            return str(c)
    return None

def extract_x_y(df: pd.DataFrame):
    """
    Rules:
    1) If there is a column named 'X' (case-insensitive), use it as X and the rest as Y.
    2) Otherwise, if the first column is mostly non-numeric (names), use it as X and the remaining numeric columns as Y.
    3) Otherwise, X = row index (1..n) and Y = numeric columns.
    """
    cols = list(df.columns)
    cols_lower = {str(c).strip().lower(): c for c in cols}

    # Case 1: explicit X column
    if "x" in cols_lower:
        x_col = cols_lower["x"]
        # Keep X numeric when it mostly is (e.g. an "epoch" index), instead of
        # always forcing it to string, so Line/Area/Scatter get a real numeric axis.
        x_num = pd.to_numeric(df[x_col], errors="coerce")
        if x_num.notna().mean() >= 0.5:
            x = x_num.to_numpy(dtype=float)
        else:
            x = df[x_col].astype(str).to_numpy()
        ydf = df.drop(columns=[x_col])
    else:
        first = df.iloc[:, 0]
        first_num = pd.to_numeric(first, errors="coerce")
        non_numeric_ratio = first_num.isna().mean()

        # Case 2: first column looks categorical (names)
        if non_numeric_ratio >= 0.5:
            x = first.astype(str).to_numpy()
            ydf = df.iloc[:, 1:].copy()
        else:
            # Case 3: fallback
            x = np.arange(1, len(df) + 1)
            ydf = df.copy()

    ydf = ydf.apply(_series_to_numeric)
    ydf = ydf.dropna(axis=1, how="all")

    if ydf.empty:
        raise ValueError("No numeric columns found for Y.")

    return x, ydf

def _trendline_xy(ax, xs, ys, trend_mode: str, *, color="#5F5F5F", label=None, linewidth=5):
    """
    Aplica trendline em uma série (xs, ys).
    - Linhas de tendência sempre tracejadas (--) e com cor controlada por 'color'
    - 'label' (se fornecido) entra na legenda
    Regras:
      Linear/Quadratic/Cubic: polyfit 1/2/3
      Moving Average: média móvel
      Logarithmic: y = a*ln(x) + b (x > 0)
      Exponential: y = a*exp(b*x) via ln(y) (y > 0)
    """

    if not trend_mode or trend_mode == "None":
        return

    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    m = np.isfinite(xs) & np.isfinite(ys)
    if m.sum() < 2:
        return

    xs = xs[m]
    ys = ys[m]

    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]

    style = dict(color=color, linestyle="--", linewidth=linewidth, label=label)

    if trend_mode.startswith("Linear"):
        coeffs = np.polyfit(xs, ys, 1)
        y_fit = np.polyval(coeffs, xs)
        ax.plot(xs, y_fit, **style)
        return

    if trend_mode.startswith("Quadratic"):
        coeffs = np.polyfit(xs, ys, 2)
        y_fit = np.polyval(coeffs, xs)
        ax.plot(xs, y_fit, **style)
        return

    if trend_mode.startswith("Cubic"):
        coeffs = np.polyfit(xs, ys, 3)
        y_fit = np.polyval(coeffs, xs)
        ax.plot(xs, y_fit, **style)
        return

    if trend_mode == "Moving Average":
        window = max(3, len(xs) // 10)
        y_ma = pd.Series(ys).rolling(window=window, center=True).mean().to_numpy()
        ax.plot(xs, y_ma, **style)
        return

    if trend_mode == "Logarithmic":
        m2 = xs > 0
        if m2.sum() < 2:
            return
        coeffs = np.polyfit(np.log(xs[m2]), ys[m2], 1)
        y_fit = coeffs[0] * np.log(xs[m2]) + coeffs[1]
        ax.plot(xs[m2], y_fit, **style)
        return

    if trend_mode == "Exponential":
        # y = a*exp(b*x) -> ln(y) = ln(a) + b*x  (requer y > 0)
        m3 = ys > 0
        if m3.sum() < 2:
            return
        coeffs = np.polyfit(xs[m3], np.log(ys[m3]), 1)
        b = coeffs[0]
        ln_a = coeffs[1]
        y_fit = np.exp(ln_a + b * xs[m3])
        ax.plot(xs[m3], y_fit, **style)
        return

def _trend_equation_and_r2(xs, ys, trend_mode: str):
    """
    Retorna (texto_equacao, r2) ou (None, None) se não aplicável.
    Moving Average já deve ter virado "None" no generate_chart.
    """
    if not trend_mode or trend_mode == "None":
        return None, None
    if trend_mode == "Moving Average":
        return None, None    

    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    m = np.isfinite(xs) & np.isfinite(ys)
    if m.sum() < 2:
        return None, None

    xs = xs[m]
    ys = ys[m]

    # helper R²
    def _r2(y_true, y_pred):
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        if ss_tot == 0:
            return None
        return 1.0 - (ss_res / ss_tot)

    # -------- Linear / Quadratic / Cubic --------
    if trend_mode.startswith("Linear"):
        a, b = np.polyfit(xs, ys, 1)
        yhat = a * xs + b
        return f"y = {a:.4g}x + {b:.4g}", _r2(ys, yhat)

    if trend_mode.startswith("Quadratic"):
        a, b, c = np.polyfit(xs, ys, 2)
        yhat = a * xs**2 + b * xs + c
        return f"y = {a:.4g}x² + {b:.4g}x + {c:.4g}", _r2(ys, yhat)

    if trend_mode.startswith("Cubic"):
        a, b, c, d = np.polyfit(xs, ys, 3)
        yhat = a * xs**3 + b * xs**2 + c * xs + d
        return f"y = {a:.4g}x³ + {b:.4g}x² + {c:.4g}x + {d:.4g}", _r2(ys, yhat)

    # -------- Logarithmic: y = a ln(x) + b (x>0) --------
    if trend_mode == "Logarithmic":
        m2 = xs > 0
        if m2.sum() < 2:
            return None, None
        a, b = np.polyfit(np.log(xs[m2]), ys[m2], 1)
        yhat = a * np.log(xs[m2]) + b
        return f"y = {a:.4g} ln(x) + {b:.4g}", _r2(ys[m2], yhat)

    # -------- Exponential: y = a e^(b x) (y>0) --------
    if trend_mode == "Exponential":
        m3 = ys > 0
        if m3.sum() < 2:
            return None, None
        b, ln_a = np.polyfit(xs[m3], np.log(ys[m3]), 1)
        a = np.exp(ln_a)
        yhat = a * np.exp(b * xs[m3])
        return f"y = {a:.4g} e^({b:.4g}x)", _r2(ys[m3], yhat)

    return None, None

def _draw_trend_equations(ax, items, is_3d: bool = False):
    """
    Desenha várias equações (lista de tuplas: (texto, cor)) empilhadas.
    Usa coordenadas do eixo (transAxes) para posição fixa.
    """
    if not items:
        return

    x0 = 0.02
    y0 = 0.98
    dy = 0.05  # espaçamento vertical

    for i, (txt, col) in enumerate(items):
        if not txt:
            continue

        y = y0 - i * dy

        # Evita sair do quadro: se ficar baixo demais, para
        if y < 0.02:
            break

        if is_3d and hasattr(ax, "text2D"):
            ax.text2D(
                x0, y, txt,
                transform=ax.transAxes,
                ha="left", va="top",
                fontsize=10,
                color=col,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.55, edgecolor="none")
            )
        else:
            ax.text(
                x0, y, txt,
                transform=ax.transAxes,
                ha="left", va="top",
                fontsize=10,
                color=col,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.55, edgecolor="none")
            )

def _get_series_colors(n, color_mode, palette_name, single_color):
    if color_mode.startswith("Single"):
        return [single_color] * n
    if _HAS_SEABORN and palette_name in ["Dark2", "Set2", "Set3", "tab10", "tab20", "Paired", "Accent"]:
        return sns.color_palette(palette_name, n_colors=n)
    cmap = plt.get_cmap(palette_name)
    return [cmap(i / max(n - 1, 1)) for i in range(n)]

def _fmt_val(v):
    try:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return ""
        # formatação simples e “bonita”
        if abs(float(v)) >= 1000:
            return f"{float(v):.0f}"
        if abs(float(v)) >= 10:
            return f"{float(v):.2f}".rstrip("0").rstrip(".")
        return f"{float(v):.3f}".rstrip("0").rstrip(".")
    except Exception:
        return str(v)

def _annotate_points(ax, xs, ys, color=None, dx=4, dy=4):
    # anota valores ao lado do ponto
    for x, y in zip(xs, ys):
        if not np.isfinite(y):
            continue
        ax.annotate(
            _fmt_val(y),
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            ha="left",
            va="bottom",
            fontsize=10,
            weight="bold",
            color=color
        )

def _annotate_xy(ax, xs, ys, color="#222222", dx=6, dy=6):
    """Anota (x, y) para cada ponto com pequeno deslocamento."""
    for x, y in zip(xs, ys):
        if not (np.isfinite(x) and np.isfinite(y)):
            continue
        ax.annotate(
            f"({_fmt_val(x)}, {_fmt_val(y)})",
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            ha="left",
            va="bottom",
            fontsize=9,
            weight="bold",
            color=color
        )

def _annotate_points_with_text(ax, xs, ys, texts, color=None, dx=4, dy=4):
    for x, y, t in zip(xs, ys, texts):
        if not np.isfinite(y):
            continue
        ax.annotate(
            _fmt_val(t),          # texto (pode ser y original)
            (x, y),               # posição (pode ser cum)
            textcoords="offset points",
            xytext=(dx, dy),
            ha="left",
            va="bottom",
            fontsize=10,
            weight="bold",
            color=color
        )

def _annotate_bars(ax, bars, dy=3):
    for b in bars:
        h = b.get_height()
        if not np.isfinite(h):
            continue
        ax.annotate(
            _fmt_val(h),
            (b.get_x() + b.get_width() / 2, h),
            textcoords="offset points",
            xytext=(0, dy),
            ha="center",
            va="bottom",
            fontsize=12,
            weight="bold",
            color="#222222"
            # color=b.get_facecolor()
        )


# ======= 1D CHARTS =========
def plot_bar(
    df: pd.DataFrame,
    dpi: int,
    trend_mode: str = "None",
    show_legend: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    label_mark: bool = False,
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4"
):
    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    x_pos = np.arange(len(x))
    n_series = len(ydf.columns)
    width = 0.8 / max(n_series, 1)

    # -----------------------------
    # 1) DRAW BARS (no double-draw)
    # -----------------------------
    bars_by_series = []  # keep handles for label_mark and trend line

    # Special case: 1 Y column + palette => color per bar (category)
    if (not color_mode.startswith("Single")) and (n_series == 1):
        if _HAS_SEABORN and palette_name in ["Dark2", "Set2", "Set3", "tab10", "tab20", "Paired", "Accent"]:
            bar_colors = sns.color_palette(palette_name, n_colors=len(x))
        else:
            cmap = plt.get_cmap(palette_name)
            bar_colors = [cmap(i / max(len(x) - 1, 1)) for i in range(len(x))]

        col = ydf.columns[0]
        y = ydf[col].to_numpy(dtype=float)

        bars = ax.bar(x_pos, y, width=0.8, label=str(col), color=bar_colors)
        bars_by_series.append((x_pos, y, bars, None))  # (xcenters, y, bars, color)

        if label_mark:
            _annotate_bars(ax, bars)

    else:
        # General case: color per series (column)
        if color_mode.startswith("Single"):
            series_colors = [single_color] * n_series
        else:
            series_colors = _get_series_colors(n_series, "Palette", palette_name, single_color)

        for i, col in enumerate(ydf.columns):
            y = ydf[col].to_numpy(dtype=float)
            pos = x_pos - (0.4 - width / 2) + i * width  # center of each bar in grouped layout
            bars = ax.bar(pos, y, width=width, label=str(col), color=series_colors[i])

            bars_by_series.append((pos, y, bars, series_colors[i]))

            if label_mark:
                _annotate_bars(ax, bars)

    # -----------------------------
    # 2) TRENDLINE (numeric x_pos)
    # -----------------------------
    if trend_mode != "None":
        trend_gray = "#5F5F5F"
        for i, (pos, y, _bars, series_c) in enumerate(bars_by_series):
            pos = np.asarray(pos, dtype=float)
            y = np.asarray(y, dtype=float)

            # regra de cor: 1 série -> cinza; >1 séries + palette -> cor da série
            if n_series == 1:
                tcolor = trend_gray
            else:
                if color_mode.startswith("Palette"):
                    # se por algum motivo series_c vier None, cai no cinza
                    tcolor = series_c if series_c is not None else trend_gray
                else:
                    tcolor = trend_gray

            # label para aparecer na legenda
            series_name = str(ydf.columns[i]) if i < len(ydf.columns) else "Y"
            _trendline_xy(ax, pos, y, trend_mode, color=tcolor, label=f"Trend ({trend_mode})", linewidth=2)
            # Equações das trendlines (uma por série)
    if show_legend and trend_mode != "None" and trend_mode != "Moving Average":

        eq_items = []
        trend_gray = "#5F5F5F"
        n_series = len(bars_by_series)

        for i, (pos, yvals, _bars, series_c) in enumerate(bars_by_series):

            pos = np.asarray(pos, dtype=float)
            yvals = np.asarray(yvals, dtype=float)

            # Regra de cor igual à trendline
            if n_series == 1:
                tcolor = trend_gray
            else:
                if color_mode.startswith("Palette") and series_c is not None:
                    tcolor = series_c
                else:
                    tcolor = trend_gray

            eq, r2 = _trend_equation_and_r2(pos, yvals, trend_mode)

            if eq:
                if r2 is not None:
                    eq = f"{eq} (R²={r2:.3f})"

                # nome da série (coluna Y correspondente)
                series_name = str(ydf.columns[i]) if i < len(ydf.columns) else f"Series {i+1}"
                eq_items.append((f"{series_name}: {eq}", tcolor))

        _draw_trend_equations(ax, eq_items, is_3d=False)  

    # -----------------------------
    # 3) Labels/title/legend
    # -----------------------------
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")

    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title or "Bar Chart", fontsize=14, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(v) for v in x], rotation=0, ha="center")

    if show_legend == True:
        ax.legend()

    plt.tight_layout()
    return fig

def plot_line(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, title: str = "", xlabel: str = "", ylabel: str = "", label_mark: bool = False,
              color_mode: str = "Palette (multi-color)",
              palette_name: str = "Dark2",
              single_color: str = "#1f77b4"):

    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    x_is_num = np.issubdtype(np.asarray(x).dtype, np.number)
    x_plot = np.asarray(x, dtype=float) if x_is_num else np.arange(len(x), dtype=float)

    colors = _get_series_colors(len(ydf.columns), color_mode, palette_name, single_color)

    for i, col in enumerate(ydf.columns):
        yvals = ydf[col].to_numpy(dtype=float)
        line = ax.plot(x_plot, yvals, marker="o", label=str(col), color=colors[i])[0]
        if label_mark:
            _annotate_points(ax, x_plot, yvals, color=line.get_color())

    if not x_is_num:
        ax.set_xticks(x_plot)
        ax.set_xticklabels([str(v) for v in x], rotation=0, ha="center")

    ax.set_title(title or "Line Chart")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14)

    ax.spines[["top", "right"]].set_visible(False)

    if trend_mode != "None":
        trend_gray = "#5F5F5F"
        n_series = len(ydf.columns)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            _trendline_xy(ax, x_plot, yvals, trend_mode, color=tcolor, label=f"Trend ({col})", linewidth=2)

    # Equações das trendlines (uma por série)
    if show_legend and trend_mode != "None" and trend_mode != "Moving Average":
        eq_items = []
        trend_gray = "#5F5F5F"
        n_series = len(ydf.columns)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            # mesma regra de cor da trendline
            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            eq, r2 = _trend_equation_and_r2(x_plot, yvals, trend_mode)
            if eq:
                if r2 is not None:
                    eq = f"{eq} (R²={r2:.3f})"
                eq_items.append((f"{col}: {eq}", tcolor))

        _draw_trend_equations(ax, eq_items, is_3d=False)   

    if show_legend == True:
        ax.legend()
    plt.tight_layout()
    return fig

def plot_scatter(
    df: pd.DataFrame,
    dpi: int,
    trend_mode: str = "None",
    show_legend: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    label_mark: bool = False,
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4"
):
    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    x_arr = np.asarray(x)
    x_is_num = np.issubdtype(x_arr.dtype, np.number)
    n_series = len(ydf.columns)

    # ==========================================================
    # CASE 1: X categórico + 1 coluna Y -> cores/legenda por categoria (igual box/violin)
    # ==========================================================
    if (not x_is_num) and (n_series == 1):
        ycol = ydf.columns[0]

        tmp = pd.DataFrame({
            "X": pd.Series(x).astype(str),
            "Y": _series_to_numeric(ydf[ycol])
        }).dropna()

        # categorias preservando ordem de aparição (sem sort)
        cats = list(pd.unique(tmp["X"]))
        cat_to_pos = {c: i for i, c in enumerate(cats)}

        # posições numéricas por linha, baseadas na categoria
        xs = tmp["X"].map(cat_to_pos).to_numpy(dtype=float)
        ys = tmp["Y"].to_numpy(dtype=float)

        # ---- cores e legenda ----
        if color_mode.startswith("Single"):
            # cor única (tudo igual) + legenda simples
            ax.scatter(xs, ys, color=single_color, alpha=0.85, label=str(ycol))
            if label_mark:
                # para 1D faz sentido manter apenas o valor Y
                _annotate_points(ax, xs, ys, color="#222222", dx=6, dy=6)

        else:
            # Palette: cor por categoria + legenda por categoria
            cat_colors = _get_series_colors(len(cats), "Palette", palette_name, single_color)
            color_map = {c: cat_colors[i] for i, c in enumerate(cats)}

            for c in cats:
                d = tmp[tmp["X"] == c]
                xsc = np.full(len(d), cat_to_pos[c], dtype=float)
                ysc = d["Y"].to_numpy(dtype=float)

                ax.scatter(
                    xsc, ysc,
                    color=color_map[c],
                    alpha=0.85,
                    label=str(c)
                )

                if label_mark:
                    _annotate_points(ax, xsc, ysc, color="#222222", dx=6, dy=6)

        # eixo X categórico (ticks/labels)
        ax.set_xticks(np.arange(len(cats), dtype=float))
        ax.set_xticklabels([str(v) for v in cats], rotation=0, ha="center")

        ax.set_title(title or "Scatter Plot")
        ax.set_xlabel(xlabel or "Category")
        ax.set_ylabel(ylabel or str(ycol))

        # Trendline (global):
        if trend_mode != "None":            
            _trendline_xy(
                ax,
                xs,
                ys,
                trend_mode,
                color="#5F5F5F",
                label=f"Trend ({ycol})",
                linewidth=2
            )           
  
        if show_legend and trend_mode != "None" and trend_mode != "Moving Average":
            eq, r2 = _trend_equation_and_r2(xs, ys, trend_mode)

            if eq:
                if r2 is not None:
                    eq = f"{eq} (R²={r2:.3f})"

                # 1 série -> mesma cor cinza da trendline
                eq_items = [(f"{ycol}: {eq}", "#5F5F5F")]
                _draw_trend_equations(ax, eq_items, is_3d=False)

        ax.spines[["top", "right"]].set_visible(False)
        if show_legend:
            ax.legend()
        plt.tight_layout()
        return fig

    # ==========================================================
    # CASE 2: múltiplas colunas Y -> séries (comportamento atual)
    # ==========================================================
    # X numérico -> usa x direto
    # X categórico (sem repetição) -> usa índice (e depois rotula com x)
    x_plot = np.asarray(x, dtype=float) if x_is_num else np.arange(len(x), dtype=float)

    colors = _get_series_colors(n_series, color_mode, palette_name, single_color)

    for i, col in enumerate(ydf.columns):
        yvals = ydf[col].to_numpy(dtype=float)
        ax.scatter(x_plot, yvals, label=str(col), color=colors[i])
        if label_mark:
            _annotate_points(ax, x_plot, yvals, color=colors[i], dx=6, dy=6)

    if not x_is_num:
        ax.set_xticks(x_plot)
        ax.set_xticklabels([str(v) for v in x], rotation=0, ha="center")

    ax.set_title(title or "Scatter Plot")
    ax.set_xlabel(xlabel or ("X" if x_is_num else "Category"))
    ax.set_ylabel(ylabel or "Y")

    # Trendline por série (padrão)
    if trend_mode != "None":
        trend_gray = "#5F5F5F"
        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            _trendline_xy(ax, x_plot, yvals, trend_mode, color=tcolor, label=f"Trend ({col})", linewidth=2)
    # Equações das trendlines (uma por série)
    if show_legend and trend_mode != "None" and trend_mode != "Moving Average":
        eq_items = []
        trend_gray = "#5F5F5F"
        n_series = len(ydf.columns)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            # mesma regra de cor da trendline
            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            eq, r2 = _trend_equation_and_r2(x_plot, yvals, trend_mode)
            if eq:
                if r2 is not None:
                    eq = f"{eq} (R²={r2:.3f})"
                eq_items.append((f"{col}: {eq}", tcolor))

        _draw_trend_equations(ax, eq_items, is_3d=False)   
            

    ax.spines[["top", "right"]].set_visible(False)
    if show_legend:
        ax.legend()
    plt.tight_layout()
    return fig

def plot_area_stacked(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, title: str = "", xlabel: str = "", ylabel: str = "", label_mark: bool = False,
              color_mode: str = "Palette (multi-color)",
              palette_name: str = "Dark2",
              single_color: str = "#1f77b4"):

    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    if color_mode.startswith("Single"):
        colors = [single_color] * len(ydf.columns)
    else:
        colors = _get_series_colors(len(ydf.columns), "Palette", palette_name, single_color)

    x_plot = np.arange(len(x), dtype=float)
    ax.stackplot(
        x_plot,
        *[ydf[c].to_numpy(dtype=float) for c in ydf.columns],
        labels=[str(c) for c in ydf.columns],
        colors=colors
    )
    ax.set_xticks(x_plot)
    ax.set_xticklabels([str(v) for v in x])
    
    if label_mark:
        x_plot = np.arange(len(x), dtype=float)

        # Se você ainda está usando stackplot com x (strings), passe a usar x_plot
        # e depois seta os labels:
        ax.set_xticks(x_plot)
        ax.set_xticklabels([str(v) for v in x], rotation=0, ha="center")

        cum = np.zeros(len(x_plot), dtype=float)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)
            yvals_safe = np.nan_to_num(yvals, nan=0.0)

            cum = cum + yvals_safe  # topo empilhado

            # marcação no TOPO da camada
            ax.plot(
                x_plot, cum,
                marker="o", linestyle="None",
                markersize=4, color=colors[i]
            )

            # texto mostra o valor da camada (yvals), mas posicionado no topo (cum)
            _annotate_points_with_text(ax, x_plot, cum, yvals_safe, color="#222222")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title or "Area Chart (Stacked)")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14)

    ax.spines[["top", "right"]].set_visible(False)

    if trend_mode != "None":
        trend_gray = "#5F5F5F"
        n_series = len(ydf.columns)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            _trendline_xy(ax, x_plot, yvals, trend_mode, color=tcolor, label=f"Trend ({col})", linewidth=2)
            # Equações das trendlines (uma por série)
            if show_legend and trend_mode != "None" and trend_mode != "Moving Average":
                eq_items = []
                trend_gray = "#5F5F5F"
                n_series = len(ydf.columns)

                for i, col in enumerate(ydf.columns):
                    yvals = ydf[col].to_numpy(dtype=float)

                    # mesma regra de cor da trendline
                    if n_series == 1:
                        tcolor = trend_gray
                    else:
                        tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

                    eq, r2 = _trend_equation_and_r2(x_plot, yvals, trend_mode)
                    if eq:
                        if r2 is not None:
                            eq = f"{eq} (R²={r2:.3f})"
                        eq_items.append((f"{col}: {eq}", tcolor))

                _draw_trend_equations(ax, eq_items, is_3d=False)   

    if show_legend == True:
        ax.legend()
    plt.tight_layout()
    return fig

def plot_area_overlapped(
    df: pd.DataFrame,
    dpi: int,
    trend_mode: str = "None",
    show_legend: bool = False,
    label_mark: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4"
):
    fig, ax = plt.subplots(figsize=(12, 6))

    x, ydf = extract_x_y(df)
    colors = _get_series_colors(len(ydf.columns), color_mode, palette_name, single_color)

    # ---------- CORREÇÃO: se X for categórico, usar posições numéricas ----------
    x_arr = np.asarray(x)
    x_is_numeric = np.issubdtype(x_arr.dtype, np.number)
    x_plot = np.asarray(x, dtype=float) if x_is_numeric else np.arange(len(x), dtype=float)

    # ---- OVERLAPPED AREA (not stacked) ----
    for i, col in enumerate(ydf.columns):
        yvals = ydf[col].to_numpy(dtype=float)

        ax.fill_between(
            x_plot,
            yvals,
            alpha=0.6,
            color=colors[i],
            label=str(col)
        )

        ax.plot(x_plot, yvals, marker="o", linestyle="None", color=colors[i], markersize=4)

        if label_mark:
            _annotate_points(ax, x_plot, yvals, color="#222222")

    # Se X era categórico, agora colocamos os rótulos corretos
    if not x_is_numeric:
        ax.set_xticks(x_plot)
        ax.set_xticklabels([str(v) for v in x], rotation=0, ha="center")

    # Optional trendline (por série)
    if trend_mode != "None":
        trend_gray = "#5F5F5F"
        n_series = len(ydf.columns)

        for i, col in enumerate(ydf.columns):
            yvals = ydf[col].to_numpy(dtype=float)

            # 1 série -> cinza | multi-série + palette -> cor da série
            if n_series == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

            _trendline_xy(ax, x_plot, yvals, trend_mode, color=tcolor, label=f"Trend ({col})", linewidth=2)
            
            # Equações das trendlines (uma por série)
            if show_legend and trend_mode != "None" and trend_mode != "Moving Average":
                eq_items = []
                trend_gray = "#5F5F5F"
                n_series = len(ydf.columns)

                for i, col in enumerate(ydf.columns):
                    yvals = ydf[col].to_numpy(dtype=float)

                    # mesma regra de cor da trendline
                    if n_series == 1:
                        tcolor = trend_gray
                    else:
                        tcolor = colors[i] if color_mode.startswith("Palette") else trend_gray

                    eq, r2 = _trend_equation_and_r2(x_plot, yvals, trend_mode)
                    if eq:
                        if r2 is not None:
                            eq = f"{eq} (R²={r2:.3f})"
                        eq_items.append((f"{col}: {eq}", tcolor))

                _draw_trend_equations(ax, eq_items, is_3d=False)           

    ax.spines[["top", "right"]].set_visible(False)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    else:
        ax.set_title("Area Chart (Overlapped)", fontsize=14)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if show_legend == True:
        ax.legend()

    fig.tight_layout()
    return fig

def plot_box(
    df: pd.DataFrame,
    dpi: int,
    trend_mode: str = "None",
    show_legend: bool = False,
    label_mark: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4"
):
    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    x_arr = np.asarray(x)
    x_is_numeric = np.issubdtype(x_arr.dtype, np.number)

    # ==========================================================
    # CASE 1: X categórico + 1 coluna Y -> boxplot por categoria
    # ==========================================================
    if (len(ydf.columns) == 1) and (not x_is_numeric):
        ycol = ydf.columns[0]
        tmp = pd.DataFrame({
            "X": pd.Series(x).astype(str),
            "Y": _series_to_numeric(ydf[ycol])
        }).dropna()

        labels = []
        data = []
        for k, g in tmp.groupby("X", sort=False):
            labels.append(str(k))
            data.append(g["Y"].to_numpy(dtype=float))

        bp = ax.boxplot(
            data,
            labels=labels,
            patch_artist=True,
            medianprops=dict(color="#222222", linewidth=1),
            whiskerprops=dict(color="#222222", linewidth=1.5),
            capprops=dict(color="#222222", linewidth=1.5),
            boxprops=dict(edgecolor="#222222", linewidth=1.5),
            flierprops=dict(
                marker="o",
                markerfacecolor="yellow",
                markeredgecolor="darkred",
                markeredgewidth=1.5,
                markersize=6,
                alpha=1
            )
        )

        # Colors: one per category
        if color_mode.startswith("Single"):
            box_colors = [single_color] * len(data)
        else:
            box_colors = _get_series_colors(len(data), "Palette", palette_name, single_color)

        for patch, c in zip(bp["boxes"], box_colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.6)

        # Label Mark: whiskers/Q1/Q2/Q3 + outliers
        if label_mark:
            x_offset = 0.35
            for i, arr in enumerate(data, start=1):
                if arr.size == 0:
                    continue

                Q1, Q2, Q3 = np.percentile(arr, [25, 50, 75])
                IQR = Q3 - Q1
                limit_below = arr[arr >= (Q1 - 1.5 * IQR)].min()
                limit_above = arr[arr <= (Q3 + 1.5 * IQR)].max()

                x_pos = i + x_offset
                ax.text(x_pos, limit_below, _fmt_val(limit_below), ha="left", va="center", fontsize=10)
                ax.text(x_pos, Q1, _fmt_val(Q1), ha="left", va="center", fontsize=10)
                ax.text(x_pos, Q2, _fmt_val(Q2), ha="left", va="center", fontsize=10, color="darkred", fontweight="bold")
                ax.text(x_pos, Q3, _fmt_val(Q3), ha="left", va="center", fontsize=10)
                ax.text(x_pos, limit_above, _fmt_val(limit_above), ha="left", va="center", fontsize=10)

            for i, fl in enumerate(bp.get("fliers", []), start=1):
                ys = fl.get_ydata()
                if ys is None or len(ys) == 0:
                    continue
                x_pos = i + x_offset
                for y0 in ys:
                    if np.isfinite(y0):
                        ax.text(x_pos, y0, f"{_fmt_val(y0)}", ha="left", va="center",
                                fontsize=10, color="darkred", fontweight="bold")

        # Labels
        if not xlabel:
            xlabel = "Category"
        if not ylabel:
            ylabel = str(ycol)

    # ==========================================================
    # CASE 2: múltiplas colunas Y -> boxplot por coluna (padrão)
    # ==========================================================
    else:
        data = [ydf[c].dropna().to_numpy(dtype=float) for c in ydf.columns]
        labels = [str(c) for c in ydf.columns]

        bp = ax.boxplot(
            data,
            labels=labels,
            patch_artist=True,
            medianprops=dict(color="#222222", linewidth=1),
            whiskerprops=dict(color="#222222", linewidth=1.5),
            capprops=dict(color="#222222", linewidth=1.5),
            boxprops=dict(edgecolor="#222222", linewidth=1.5),
            flierprops=dict(
                marker="o",
                markerfacecolor="yellow",
                markeredgecolor="darkred",
                markeredgewidth=1.5,
                markersize=6,
                alpha=1
            )
        )

        if color_mode.startswith("Single"):
            box_colors = [single_color] * len(labels)
        else:
            box_colors = _get_series_colors(len(labels), "Palette", palette_name, single_color)

        for patch, c in zip(bp["boxes"], box_colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.6)

        if label_mark:
            x_offset = 0.15
            for i, arr in enumerate(data, start=1):
                if arr.size == 0:
                    continue

                Q1, Q2, Q3 = np.percentile(arr, [25, 50, 75])
                IQR = Q3 - Q1
                limit_below = arr[arr >= (Q1 - 1.5 * IQR)].min()
                limit_above = arr[arr <= (Q3 + 1.5 * IQR)].max()

                x_pos = i + x_offset
                ax.text(x_pos, limit_below, _fmt_val(limit_below), ha="left", va="center", fontsize=10, color="black")
                ax.text(x_pos, Q1, _fmt_val(Q1), ha="left", va="center", fontsize=10, color="black")
                ax.text(x_pos, Q2, _fmt_val(Q2), ha="left", va="center", fontsize=10, color="black", fontweight="bold")
                ax.text(x_pos, Q3, _fmt_val(Q3), ha="left", va="center", fontsize=10, color="black")
                ax.text(x_pos, limit_above, _fmt_val(limit_above), ha="left", va="center", fontsize=10, color="black")

            for i, fl in enumerate(bp.get("fliers", []), start=1):
                ys = fl.get_ydata()
                if ys is None or len(ys) == 0:
                    continue
                x_pos = i + x_offset
                for y0 in ys:
                    if np.isfinite(y0):
                        ax.text(x_pos, y0, f"{_fmt_val(y0)}", ha="left", va="center",
                                fontsize=10, color="darkred", fontweight="bold")

    # ---- title / labels ----
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    else:
        ax.set_title("Box Plot", fontsize=14)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14)

    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return fig

def plot_heatmap(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "", xlabel: str = "", ylabel: str = "",
                 color_mode: str = "Palette (multi-color)",
                 palette_name: str = "viridis",
                 single_color: str = "#1f77b4"):

    from matplotlib.colors import LinearSegmentedColormap

    _, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    data = ydf.to_numpy(dtype=float)

    if color_mode.startswith("Single"):
        cmap = LinearSegmentedColormap.from_list("single", ["#ffffff", single_color])
    else:
        cmap = palette_name

    im = ax.imshow(data, aspect="auto", cmap=cmap)

    ax.set_title(title or "Heatmap")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=14)

    ax.set_xticks(np.arange(len(ydf.columns)))
    ax.set_xticklabels([str(c) for c in ydf.columns], rotation=45, ha="right")
    fig.colorbar(im, ax=ax)

    plt.tight_layout()
    return fig

def plot_violin(
    df: pd.DataFrame,
    dpi: int,
    trend_mode: str = "None",
    show_legend: bool = False,
    label_mark: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4"
):
    x, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    # ===== CASE 1: X categórico + 1 coluna Y =====
    if len(ydf.columns) == 1 and not np.issubdtype(np.asarray(x).dtype, np.number):
        ycol = ydf.columns[0]
        tmp = pd.DataFrame({
            "X": x,
            "Y": _series_to_numeric(ydf[ycol])
        }).dropna()

        groups = []
        labels = []

        for k, g in tmp.groupby("X", sort=False):
            labels.append(str(k))
            groups.append(g["Y"].to_numpy(dtype=float))

        parts = ax.violinplot(
            groups,
            showmeans=False,
            showmedians=True,
            showextrema=True
        )

        # ---- colors ----
        if color_mode.startswith("Single"):
            colors = [single_color] * len(groups)
        else:
            colors = _get_series_colors(len(groups), "Palette", palette_name, single_color)

        for pc, c in zip(parts["bodies"], colors):
            pc.set_facecolor(c)
            pc.set_alpha(0.6)

        ax.set_xticks(np.arange(1, len(labels) + 1))
        ax.set_xticklabels(labels)

        # ---- LABEL MARK (quartis + whiskers + outliers) ----
        if label_mark:
            x_offset = 0.35  # deslocamento horizontal (igual ao boxplot)

            for i, arr in enumerate(groups, start=1):
                if arr.size == 0:
                    continue

                Q1, Q2, Q3 = np.percentile(arr, [25, 50, 75])
                IQR = Q3 - Q1

                limit_below = arr[arr >= (Q1 - 1.5 * IQR)].min()
                limit_above = arr[arr <= (Q3 + 1.5 * IQR)].max()

                x_pos = i + x_offset

                ax.text(x_pos, limit_below, _fmt_val(limit_below),
                        ha="left", va="center", fontsize=10)
                # ax.text(x_pos, Q1, _fmt_val(Q1),
                #         ha="left", va="center", fontsize=10)
                ax.text(x_pos, Q2, _fmt_val(Q2),
                        ha="left", va="center",
                        fontsize=10, fontweight="bold", color="darkred")
                # ax.text(x_pos, Q3, _fmt_val(Q3),
                #         ha="left", va="center", fontsize=10)
                ax.text(x_pos, limit_above, _fmt_val(limit_above),
                        ha="left", va="center", fontsize=10)

    # ===== CASE 2: múltiplas colunas Y =====
    else:
        data = [ydf[c].dropna().to_numpy(dtype=float) for c in ydf.columns]
        labels = [str(c) for c in ydf.columns]

        parts = ax.violinplot(
            data,
            showmeans=False,
            showmedians=True,
            showextrema=True
        )

        if color_mode.startswith("Single"):
            colors = [single_color] * len(data)
        else:
            colors = _get_series_colors(len(data), "Palette", palette_name, single_color)

        for pc, c in zip(parts["bodies"], colors):
            pc.set_facecolor(c)
            pc.set_alpha(0.6)

        ax.set_xticks(np.arange(1, len(labels) + 1))
        ax.set_xticklabels(labels)

        # ---- LABEL MARK ----
        if label_mark:
            x_offset = 0.35

            for i, arr in enumerate(data, start=1):
                if arr.size == 0:
                    continue

                Q1, Q2, Q3 = np.percentile(arr, [25, 50, 75])
                IQR = Q3 - Q1

                limit_below = arr[arr >= (Q1 - 1.5 * IQR)].min()
                limit_above = arr[arr <= (Q3 + 1.5 * IQR)].max()

                x_pos = i + x_offset

                ax.text(x_pos, limit_below, _fmt_val(limit_below), ha="left", va="center", fontsize=10)
                # ax.text(x_pos, Q1, _fmt_val(Q1), ha="left", va="center", fontsize=10)
                ax.text(x_pos, Q2, _fmt_val(Q2),
                        ha="left", va="center",
                        fontsize=10, fontweight="bold", color="darkred")
                # ax.text(x_pos, Q3, _fmt_val(Q3), ha="left", va="center", fontsize=10)
                ax.text(x_pos, limit_above, _fmt_val(limit_above), ha="left", va="center", fontsize=10)

    # ---- labels / title ----
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.set_title(title or "Violin Plot", fontsize=14, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    return fig

def plot_histogram(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "",
                   xlabel: str = "", ylabel: str = "",
                   color_mode: str = "Palette (multi-color)",
                   palette_name: str = "Dark2",
                   single_color: str = "#1f77b4"):

    _, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    n = len(ydf.columns)
    colors = _get_series_colors(n, color_mode, palette_name, single_color)

    # overlay hist para múltiplas séries
    for i, col in enumerate(ydf.columns):
        vals = ydf[col].dropna().to_numpy(dtype=float)
        ax.hist(vals, bins=20, alpha=0.6 if n > 1 else 0.8, label=str(col), color=colors[i])

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    else:
        ax.set_title("Histogram", fontsize=14)

    ax.spines[["top", "right"]].set_visible(False)    
   
    if n > 1:
        if show_legend == True:
            ax.legend()

    plt.tight_layout()
    return fig

def _kde_1d(values: np.ndarray, grid: np.ndarray):
    """KDE simples (gaussiana) sem SciPy."""
    v = values[np.isfinite(values)]
    if v.size < 2:
        return np.zeros_like(grid)

    # Silverman's rule of thumb
    std = np.std(v, ddof=1)
    if std <= 0:
        return np.zeros_like(grid)

    n = v.size
    bw = 1.06 * std * (n ** (-1 / 5))
    if bw <= 0:
        return np.zeros_like(grid)

    # KDE
    diff = (grid[:, None] - v[None, :]) / bw
    dens = np.exp(-0.5 * diff * diff).sum(axis=1) / (n * bw * np.sqrt(2 * np.pi))
    return dens

def plot_density(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "",
                 xlabel: str = "", ylabel: str = "",
                 color_mode: str = "Palette (multi-color)",
                 palette_name: str = "Dark2",
                 single_color: str = "#1f77b4"):

    _, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    n = len(ydf.columns)
    colors = _get_series_colors(n, color_mode, palette_name, single_color)

    # define grid comum
    all_vals = np.concatenate([ydf[c].dropna().to_numpy(dtype=float) for c in ydf.columns if ydf[c].notna().any()])
    all_vals = all_vals[np.isfinite(all_vals)]
    if all_vals.size == 0:
        raise ValueError("No valid numeric values for density plot.")

    xmin, xmax = np.min(all_vals), np.max(all_vals)
    if xmin == xmax:
        xmin -= 1.0
        xmax += 1.0

    grid = np.linspace(xmin, xmax, 400)

    for i, col in enumerate(ydf.columns):
        vals = ydf[col].dropna().to_numpy(dtype=float)
        dens = _kde_1d(vals, grid)
        ax.plot(grid, dens, label=str(col), color=colors[i], linewidth=2)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    else:
        ax.set_title("Density (KDE)", fontsize=14)

    ax.spines[["top", "right"]].set_visible(False)
    if n > 1:
        if show_legend == True:
            ax.legend()

    plt.tight_layout()
    return fig

def plot_sankey(
    df: pd.DataFrame,
    dpi: int = 300,
    trend_mode: str = "None",
    show_legend: bool = False,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    label_mark: bool = False,
    color_mode: str = "Palette (multi-color)",
    palette_name: str = "Dark2",
    single_color: str = "#1f77b4",
    stage_cols=None,
    weight_col=None,
    max_nodes: int = SANKEY_MAX_NODES_PER_STAGE,
):
    """Diagrama de Sankey (aluvial) de 2 ou mais colunas categóricas: cada coluna é uma etapa, cada
    categoria um nó e cada faixa liga duas etapas vizinhas com largura proporcional ao número de
    linhas que passam daquela categoria para a seguinte (ou à soma de `weight_col`, se informada).
    Linhas com valor ausente em qualquer etapa (ou peso <= 0) ficam de fora, de modo que todas as
    etapas somam o mesmo total. `max_nodes` (1 a SANKEY_MAX_NODES_PER_STAGE) mantém, em cada coluna,
    só as categorias de maior fluxo (contagem de linhas ou soma do peso); as linhas que têm uma
    categoria de fora em qualquer etapa são descartadas. `label_mark` escreve o valor de cada nó; `show_legend` é ignorado
    (os próprios nós já são rotulados)."""
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path

    stage_cols = list(stage_cols) if stage_cols is not None else [c for c in df.columns if c != weight_col]
    if len(stage_cols) < 2:
        raise ValueError("Sankey needs at least two categorical columns (stages).")

    data = df[stage_cols].copy()
    for c in stage_cols:
        s = data[c]
        data[c] = s.where(s.notna(), None).astype(object).map(lambda v: None if v is None else str(v))
    if weight_col is not None:
        w = _series_to_numeric(df[weight_col])
    else:
        w = pd.Series(1.0, index=df.index)
    keep = data.notna().all(axis=1) & w.notna() & (w > 0)
    data, w = data[keep], w[keep].astype(float)
    if data.empty:
        raise ValueError("No rows with valid values in every selected column.")

    # Só as `max_nodes` categorias de maior fluxo de cada coluna entram (as demais linhas saem).
    max_nodes = max(1, min(int(max_nodes or SANKEY_MAX_NODES_PER_STAGE), SANKEY_MAX_NODES_PER_STAGE))
    in_top = pd.Series(True, index=data.index)
    for c in stage_cols:
        tot = w.groupby(data[c]).sum().sort_values(ascending=False, kind="stable")
        in_top &= data[c].isin(set(tot.index[:max_nodes]))
    data, w = data[in_top], w[in_top]
    if data.empty:
        raise ValueError("The most frequent categories of the selected columns never occur in the same rows.")

    # nós de cada etapa, do maior fluxo para o menor
    stages = [w.groupby(data[c]).sum().sort_values(ascending=False, kind="stable") for c in stage_cols]

    total = float(w.sum())
    gap = 0.025 * total                         # espaço vertical entre nós da mesma etapa
    node_w = 0.04                               # largura horizontal de cada nó
    # posição vertical (topo, de cima para baixo) de cada nó; as etapas são centradas na mais alta
    heights = [float(t.sum()) + gap * (len(t) - 1) for t in stages]
    full = max(heights)
    node_pos = []                               # [{categoria: (y_topo, altura)}]
    for t, h in zip(stages, heights):
        y = (full - h) / 2.0
        pos = {}
        for cat, val in t.items():
            pos[cat] = (y, float(val))
            y += float(val) + gap
        node_pos.append(pos)

    n_nodes = sum(len(t) for t in stages)
    palette = _get_series_colors(max(n_nodes, 1), color_mode, palette_name, single_color)
    node_color, k = [], 0
    for t in stages:
        node_color.append({cat: palette[k + i] for i, cat in enumerate(t.index)})
        k += len(t)

    fig, ax = plt.subplots(figsize=(12, 6))
    n_st = len(stage_cols)

    def _ribbon(x0, y0_top, y0_bot, x1, y1_top, y1_bot, color):
        xm = (x0 + x1) / 2.0
        verts = [(x0, y0_top), (xm, y0_top), (xm, y1_top), (x1, y1_top),
                 (x1, y1_bot), (xm, y1_bot), (xm, y0_bot), (x0, y0_bot), (x0, y0_top)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                 Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", alpha=0.45, zorder=1))

    for i in range(n_st - 1):
        a, b = stage_cols[i], stage_cols[i + 1]
        flows = w.groupby([data[a], data[b]]).sum()
        src_cursor = {cat: pos[0] for cat, pos in node_pos[i].items()}
        dst_cursor = {cat: pos[0] for cat, pos in node_pos[i + 1].items()}
        src_order = {cat: j for j, cat in enumerate(stages[i].index)}
        dst_order = {cat: j for j, cat in enumerate(stages[i + 1].index)}
        # Cada faixa sai do nó de origem na ordem dos nós de destino e chega ao destino na ordem dos nós de
        # origem; isso evita cruzamentos desnecessários.
        dst_top = {}
        for (src, dst), val in sorted(flows.items(), key=lambda kv: (dst_order[kv[0][1]], src_order[kv[0][0]])):
            dst_top[(src, dst)] = dst_cursor[dst]
            dst_cursor[dst] += float(val)
        for (src, dst), val in sorted(flows.items(), key=lambda kv: (src_order[kv[0][0]], dst_order[kv[0][1]])):
            val = float(val)
            y0 = src_cursor[src]; src_cursor[src] += val
            y1 = dst_top[(src, dst)]
            _ribbon(i + node_w, y0, y0 + val, i + 1, y1, y1 + val, node_color[i][src])

    for i, pos in enumerate(node_pos):
        for cat, (y, h) in pos.items():
            ax.add_patch(Rectangle((i, y), node_w, h, facecolor=node_color[i][cat], edgecolor="#333333",
                                   linewidth=0.6, zorder=3))
            lab = str(cat)
            if label_mark:
                lab += f" ({_fmt_val(h)})"
            ax.text(i + node_w + 0.02, y + h / 2.0, lab, va="center", ha="left", fontsize=9, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))

    for i, c in enumerate(stage_cols):
        ax.text(i + node_w / 2.0, -0.02 * full, str(c), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xlim(-0.1, n_st - 1 + node_w + 0.5)
    ax.set_ylim(full * 1.02, -0.08 * full)       # eixo Y invertido: primeiro nó no topo
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=14)
    else:
        ax.set_title("Sankey: " + " → ".join(map(str, stage_cols)), fontsize=14, pad=14)
    plt.tight_layout()
    return fig

PLOTTERS = {
    "Bar": plot_bar,
    "Line": plot_line,
    "Scatter": plot_scatter,
    "Area (Stacked)": plot_area_stacked,
    "Area (Overlapped)": plot_area_overlapped,
    "Box Plot": plot_box,
    "Histogram": plot_histogram,
    "Density(KDE)": plot_density,
    "Violin": plot_violin,
    "Heatmap": plot_heatmap,
    "Sankey": plot_sankey,
}

# ======= 2D CHARTS =========
def plot_scatter_2D(df: pd.DataFrame, x_col: str, y_col: str, group_col: str,
                                       title: str = "", xlabel: str = "", ylabel: str = "",
                                       palette_name: str = "tab10", single_color: str = "#1f77b4",
                                       color_mode: str = "Palette (multi-color)",
                                       label_mark: bool = False, trend_mode: str = "None", show_legend: bool = False):
    fig, ax = plt.subplots(figsize=(12, 6))

    x = _series_to_numeric(df[x_col])
    y = _series_to_numeric(df[y_col])
    g = df[group_col].astype(str)

    tmp = pd.DataFrame({"x": x, "y": y, "g": g}).dropna()

    cats = list(tmp["g"].unique())
    if color_mode.startswith("Single"):
        colors = {c: single_color for c in cats}
    else:
        palette = _get_series_colors(len(cats), "Palette", palette_name, single_color)
        colors = {c: palette[i] for i, c in enumerate(cats)}

    for c in cats:
        d = tmp[tmp["g"] == c]
        ax.scatter(d["x"], d["y"], label=str(c), color=colors[c])
        if label_mark:
            _annotate_xy(
                ax,
                d["x"].to_numpy(dtype=float),
                d["y"].to_numpy(dtype=float),
                color=colors[c],
                dx=6, dy=6
            )

    ax.set_title(title, fontsize=14, fontweight="bold") if title else ax.set_title("Scatter Plot", fontsize=14)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    
    # Trendline por grupo (igual ao padrão dos outros gráficos)
    if trend_mode is not None and trend_mode != "None":
        trend_gray = "#5F5F5F"
        n_groups = len(cats)

        for c in cats:
            d = tmp[tmp["g"] == c]
            xs = d["x"].to_numpy(dtype=float)
            ys = d["y"].to_numpy(dtype=float)

            # regra de cor:
            # 1 grupo -> cinza | multi-grupos + palette -> cor do grupo
            if n_groups == 1:
                tcolor = trend_gray
            else:
                tcolor = colors[c] if color_mode.startswith("Palette") else trend_gray

            _trendline_xy(
                ax,
                xs,
                ys,
                trend_mode,
                color=tcolor,
                label=f"Trend ({c})",
                linewidth=2
            )
    # Equações das trendlines (uma por grupo)
    if show_legend and trend_mode != "None" and trend_mode != "Moving Average":

        eq_items = []
        trend_gray = "#5F5F5F"
        n_groups = len(cats)

        for c in cats:
            d = tmp[tmp["g"] == c]
            xs = d["x"].to_numpy(dtype=float)
            ys = d["y"].to_numpy(dtype=float)

            # Regra de cor igual à trendline
            if n_groups == 1:
                tcolor = trend_gray
            else:
                # aqui usamos o mesmo dicionário de cores do plot (normalmente 'colors')
                if color_mode.startswith("Palette") and c in colors:
                    tcolor = colors[c]
                else:
                    tcolor = trend_gray

            eq, r2 = _trend_equation_and_r2(xs, ys, trend_mode)

            if eq:
                if r2 is not None:
                    eq = f"{eq} (R²={r2:.3f})"
                eq_items.append((f"{c}: {eq}", tcolor))

        _draw_trend_equations(ax, eq_items, is_3d=False) 
                   
    if show_legend == True:
        # remove duplicatas de label na legenda
        handles, labels = ax.get_legend_handles_labels()
        uniq = dict(zip(labels, handles))
        ax.legend(uniq.values(), uniq.keys())
        
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return fig

# ======= 3D CHARTS =========
def plot_scatter_3D(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    group_col: str | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    zlabel: str = "",
    palette_name: str = "tab10",
    single_color: str = "#1f77b4",
    color_mode: str = "Palette (multi-color)",
    label_mark: bool = False,
    trend_mode: str = "None",
    show_legend: bool = False
):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    x = _series_to_numeric(df[x_col])
    y = _series_to_numeric(df[y_col])
    z = _series_to_numeric(df[z_col])

    if group_col is not None:
        g = df[group_col].astype(str)
        tmp = pd.DataFrame({"x": x, "y": y, "z": z, "g": g}).dropna()
    else:
        tmp = pd.DataFrame({"x": x, "y": y, "z": z}).dropna()

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_title(title or f"3D Scatter: {x_col} vs {y_col} vs {z_col}", fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    ax.set_zlabel(zlabel or z_col)
    ax.grid(True, linestyle="--", alpha=0.2, linewidth=1)

    # ==========================================================
    # COM GRUPOS
    # ==========================================================
    if group_col is not None and "g" in tmp.columns:

        cats = list(tmp["g"].unique())

        if color_mode.startswith("Single"):
            color_map = {c: single_color for c in cats}
        else:
            pal = _get_series_colors(len(cats), "Palette", palette_name, single_color)
            color_map = {c: pal[i] for i, c in enumerate(cats)}

        for c in cats:
            d = tmp[tmp["g"] == c]

            ax.scatter(
                d["x"].to_numpy(dtype=float),
                d["y"].to_numpy(dtype=float),
                d["z"].to_numpy(dtype=float),
                s=30,
                alpha=0.75,
                color=color_map[c],
                depthshade=True,
                label=f"{c} (n={len(d)})"
            )

            if label_mark:
                xs = d["x"].to_numpy(dtype=float)
                ys = d["y"].to_numpy(dtype=float)
                zs = d["z"].to_numpy(dtype=float)

                # deslocamento proporcional ao "tamanho" do eixo para não colar no ponto
                xr = np.nanmax(xs) - np.nanmin(xs) if xs.size else 0.0
                yr = np.nanmax(ys) - np.nanmin(ys) if ys.size else 0.0
                zr = np.nanmax(zs) - np.nanmin(zs) if zs.size else 0.0
                dx = 0.01 * xr if xr > 0 else 0.05
                dy = 0.01 * yr if yr > 0 else 0.05
                dz = 0.01 * zr if zr > 0 else 0.05

                for xi, yi, zi in zip(xs, ys, zs):
                    if not (np.isfinite(xi) and np.isfinite(yi) and np.isfinite(zi)):
                        continue
                    ax.text(
                        xi + dx, yi + dy, zi + dz,
                        f"({_fmt_val(xi)}, {_fmt_val(yi)}, {_fmt_val(zi)})",
                        fontsize=8,
                        color="#222222"
                    )

    # ==========================================================
    # SEM GRUPOS
    # ==========================================================
    else:
        ax.scatter(
            tmp["x"].to_numpy(dtype=float),
            tmp["y"].to_numpy(dtype=float),
            tmp["z"].to_numpy(dtype=float),
            s=30,
            alpha=0.75,
            color=single_color,
            depthshade=True,
            label="Data"
        )

        if label_mark:
            xs = tmp["x"].to_numpy(dtype=float)
            ys = tmp["y"].to_numpy(dtype=float)
            zs = tmp["z"].to_numpy(dtype=float)

            xr = np.nanmax(xs) - np.nanmin(xs) if xs.size else 0.0
            yr = np.nanmax(ys) - np.nanmin(ys) if ys.size else 0.0
            zr = np.nanmax(zs) - np.nanmin(zs) if zs.size else 0.0
            dx = 0.01 * xr if xr > 0 else 0.05
            dy = 0.01 * yr if yr > 0 else 0.05
            dz = 0.01 * zr if zr > 0 else 0.05

            for xi, yi, zi in zip(xs, ys, zs):
                if not (np.isfinite(xi) and np.isfinite(yi) and np.isfinite(zi)):
                    continue
                ax.text(
                    xi + dx, yi + dy, zi + dz,
                    f"({_fmt_val(xi)}, {_fmt_val(yi)}, {_fmt_val(zi)})",
                    fontsize=8,
                    color="#222222"
                )

    # ==========================================================
    # LEGENDA (CORRIGIDA)
    # ==========================================================
    if show_legend:
        handles, labels = ax.get_legend_handles_labels()

        if len(handles) > 0:
            # remove duplicatas
            uniq = dict(zip(labels, handles))
            ax.legend(
                uniq.values(),
                uniq.keys(),
                loc="upper left",
                bbox_to_anchor=(1.02, 1),   # posiciona fora do eixo 3D
                borderaxespad=0
            )

    if show_legend == True:
        ax.legend()

    plt.tight_layout()
    return fig


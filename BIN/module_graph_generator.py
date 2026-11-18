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
"""Funções de plotagem da aba PLOT (Gerador de Gráficos) do CODRUG, sem nenhuma dependência de Qt.

Cada plotter recebe um DataFrame e devolve uma matplotlib Figure. Acima deles fica a camada de PAPÉIS DAS COLUNAS
(seção final deste arquivo): resolve_roles() decide, só pelos tipos das colunas selecionadas e pelo tipo de gráfico,
o que cada coluna faz (eixo, cores/grupos, valores, etapas...) e execute_plan() monta os dados e chama o plotter.
A interface (aba PLOT em CODRUG.py) só escolhe as colunas, pergunta o que for preciso ao usuário e exibe a figura.
O mesmo núcleo é usado pelo GraphGenerator (graph_core.py).

Convenção do DataFrame de entrada dos plotters (ver extract_x_y): coluna "X" explícita (ou a primeira coluna não
numérica) como eixo X e as demais colunas numéricas como séries Y."""

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
                  "Box Plot", "Heatmap", "Violin", "Histogram", "Density(KDE)", "Sankey", "Sankey Chord"]
SANKEY_MAX_NODES_PER_STAGE = 30   # acima disso o diagrama vira um borrão ilegível
CHORD_MAX_NODES = 30              # idem para o Sankey Chord (nós no círculo)
SANKEY_ORIENTATIONS = ["Horizontal", "Vertical"]
# Box Plot e Violin resumem os valores de colunas Y numéricas; X é opcional e apenas agrupa as linhas em categorias.
DISTRIBUTION_CHARTS = ("Box Plot", "Violin")
DISTRIBUTION_MAX_GROUPS = 30       # mais categorias que isso em X viram dezenas de caixas ilegíveis
# Histogram, Density e Heatmap só usam as colunas Y numéricas (o X nunca entra no desenho): não exigem X.
Y_ONLY_CHARTS = ("Histogram", "Density(KDE)", "Heatmap")
# 2D: todos os tipos, como no 1D. Com uma coluna numérica em X (a escala do eixo) e colunas categóricas também em X,
# Scatter / Line / Area / Bar desenham uma série (cor) por categoria; Histogram / Density, uma curva por categoria.
CHART_TYPES_2D = list(CHART_TYPES_1D)
# Tipos que, no 2D, funcionam como no 1D (não usam um eixo X numérico contra Y).
ONE_D_STYLE_CHARTS = ("Box Plot", "Violin", "Heatmap", "Histogram", "Density(KDE)", "Sankey", "Sankey Chord")
GROUPED_XY_CHARTS = ("Scatter", "Line", "Area (Stacked)", "Area (Overlapped)", "Bar")
MAX_SERIES = 30           # séries (cores) por gráfico quando as categorias viram séries
CHART_TYPES_3D = ["Scatter"]


# ----------------------------------------------------------------------------------------------------------
# Opções específicas de cada tipo de gráfico (mostradas na aba PLOT à direita do "Chart type").
# Cada item: (chave, tipo, padrão, mínimo, máximo, passo), (chave, "bool", padrão) ou
# (chave, "choice", padrão, [opções]). Os plotters leem os valores de `options` (dict chave -> valor)
# com _opt(); sem a chave, usam o padrão do catálogo.
# ----------------------------------------------------------------------------------------------------------
COMMON_OPTIONS = [("samples", "int", 0, 0, 10_000_000, 100)]      # 0 = todas as linhas
# Estatística (opção "bar_stat") do Bar, Line e Area: centro + dispersão que o Bar desenha no topo das barras.
STAT_SINGLE, STAT_MEAN, STAT_MEDIAN, STAT_MODE = "Single Value", "Mean ± SD", "Median ± IQR", "Mode"
BAR_STATS = [STAT_SINGLE, STAT_MEAN, STAT_MEDIAN, STAT_MODE]
CHART_OPTIONS = {
    "Bar": [("bar_width", "float", 0.8, 0.1, 1.0, 0.05),
            ("bar_sort", "choice", "None", ["None", "Ascending", "Descending"]),
            ("bar_top", "int", 0, 0, 1000, 1),
            ("bar_stat", "choice", STAT_MEAN, BAR_STATS)],
    "Line": [("line_width", "float", 1.5, 0.5, 10.0, 0.5),
             ("marker_size", "float", 6.0, 0.0, 30.0, 1.0),
             ("bar_stat", "choice", STAT_MEAN, BAR_STATS)],
    "Scatter": [("point_size", "float", 36.0, 2.0, 500.0, 2.0),
                ("point_alpha", "float", 0.85, 0.1, 1.0, 0.05)],
    "Area (Stacked)": [("area_stacked_alpha", "float", 1.0, 0.1, 1.0, 0.05),
                       ("bar_stat", "choice", STAT_MEAN, BAR_STATS)],
    "Area (Overlapped)": [("area_overlap_alpha", "float", 0.6, 0.1, 1.0, 0.05),
                          ("bar_stat", "choice", STAT_MEAN, BAR_STATS)],
    "Box Plot": [("box_whisker", "float", 1.5, 0.5, 5.0, 0.1),
                 ("box_width", "float", 0.5, 0.1, 1.0, 0.05),
                 ("box_outliers", "bool", True)],
    "Heatmap": [("heat_normalize", "choice", "None", ["None", "Min-Max (columns)", "Z-score (columns)"]),
                ("heat_colorbar", "bool", True)],
    "Violin": [("violin_width", "float", 0.5, 0.1, 1.0, 0.05),
               ("violin_bw", "float", 0.0, 0.0, 3.0, 0.1),
               ("violin_median", "bool", True),
               ("violin_extrema", "bool", True)],
    "Histogram": [("hist_bins", "int", 20, 2, 500, 1),
                  ("hist_density", "bool", False),
                  ("hist_cumulative", "bool", False)],
    "Density(KDE)": [("kde_bw", "float", 1.0, 0.1, 5.0, 0.1),
                     ("kde_points", "int", 400, 50, 2000, 50),
                     ("kde_fill", "bool", False),
                     ("kde_peak", "bool", False)],
    "Sankey": [("sankey_orient", "choice", "Horizontal", SANKEY_ORIENTATIONS),
               ("sankey_sort", "choice", "None", ["None", "Ascending", "Descending"]),
               ("sankey_top", "int", SANKEY_MAX_NODES_PER_STAGE, 1, SANKEY_MAX_NODES_PER_STAGE, 1),
               ("sankey_alpha", "float", 0.45, 0.1, 1.0, 0.05)],
    "Sankey Chord": [("chord_sort", "choice", "None", ["None", "Ascending", "Descending"]),
                     ("chord_top", "int", CHORD_MAX_NODES, 2, CHORD_MAX_NODES, 1),
                     ("chord_alpha", "float", 0.55, 0.1, 1.0, 0.05),
                     ("chord_gap", "float", 3.0, 0.0, 20.0, 0.5),
                     ("chord_self", "bool", True)],
}


def all_option_specs():
    """Todas as opções (comuns + de cada tipo), sem repetição, na ordem do catálogo."""
    seen, out = set(), []
    for spec in COMMON_OPTIONS + [sp for lst in CHART_OPTIONS.values() for sp in lst]:
        if spec[0] not in seen:
            seen.add(spec[0])
            out.append(spec)
    return out


def all_option_keys():
    return [sp[0] for sp in all_option_specs()]


def chart_option_keys(chart: str):
    """Chaves das opções que valem para o tipo de gráfico (as próprias + as comuns)."""
    return [sp[0] for sp in CHART_OPTIONS.get(chart, [])] + [sp[0] for sp in COMMON_OPTIONS]


def option_defaults():
    return {sp[0]: sp[2] for sp in all_option_specs()}


def _opt(options, key, default=None):
    """Valor da opção `key` (ou o padrão do catálogo / o `default` informado, se ausente)."""
    if options and key in options and options[key] is not None:
        return options[key]
    if default is not None:
        return default
    return option_defaults().get(key)


LEGEND_POSITIONS = ("Upper right", "Upper left", "Lower right", "Lower left")


def _legend(ax, options=None, dedupe=False):
    """Desenha a legenda de `ax` na posição pedida em options["legend_loc"] (um de LEGEND_POSITIONS;
    ausente = "Upper right"). `dedupe` remove rótulos repetidos. Sem artistas rotulados, não desenha nada."""
    loc = str(_opt(options, "legend_loc", LEGEND_POSITIONS[0])).strip().lower()
    if loc not in {p.lower() for p in LEGEND_POSITIONS}:
        loc = LEGEND_POSITIONS[0].lower()
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return None
    if dedupe:
        uniq = dict(zip(labels, handles))
        handles, labels = list(uniq.values()), list(uniq.keys())
    ncol = 1 + (len(handles) - 1) // 12          # muitas categorias: a legenda se divide em colunas
    return ax.legend(handles, labels, loc=loc, ncol=ncol)


MAX_LEGEND_CATEGORIES = 40      # categorias listadas na legenda (as demais ficam de fora)


def _label_category_artists(artists, categories):
    """Dá a cada artista (barra, caixa, corpo de violino) o nome da sua categoria, para a legenda mostrar
    quais categorias as cores representam (e não só o nome da coluna, que já está no rótulo do eixo)."""
    for k, (art, cat) in enumerate(zip(artists, categories)):
        art.set_label(str(cat) if k < MAX_LEGEND_CATEGORIES else "_nolegend_")


# ----------------------------------------------------------------------------------------------------------
# Limite de marcações: antes de gerar, a aba PLOT confere (excessive_marks) se o gráfico não teria marcações
# demais. Só o Scatter mostra todas as instâncias; os demais tipos agregam ou têm limite.
# ----------------------------------------------------------------------------------------------------------
MAX_BARS = 120            # barras (categorias x séries) no Bar
MAX_LINE_POINTS = 500     # pontos por série em Line e nas áreas
MAX_HEATMAP_ROWS = 500    # linhas do Heatmap
MAX_LABELS = 300          # valores escritos por "Show label mark"
MAX_BOXES = 60            # caixas/violinos (grupos x colunas Y) em Box Plot e Violin


def excessive_marks(chart: str, n_rows: int, n_series: int = 1, label_mark: bool = False, top_n: int = 0):
    """None se o gráfico cabe nos limites; senão (tipo, n, limite): tipo "bars" | "points" | "rows" | "labels" |
    "boxes". `n_rows` é o nº de linhas já mapeadas (categorias no Bar, pontos por série no Line/Area/Scatter,
    linhas do Heatmap, grupos no Box Plot/Violin); `top_n` (Bar) limita as categorias mostradas."""
    n_rows, n_series = int(n_rows), max(int(n_series), 1)
    if chart == "Series":                     # nº de séries (cores) criadas por categorias
        return ("series", n_rows, MAX_SERIES) if n_rows > MAX_SERIES else None
    if chart == "Bar":
        eff = min(n_rows, int(top_n)) if top_n and int(top_n) > 0 else n_rows
        if eff * n_series > MAX_BARS:
            return ("bars", eff * n_series, MAX_BARS)
        return None
    if chart in ("Line", "Area (Stacked)", "Area (Overlapped)"):
        if n_rows > MAX_LINE_POINTS:
            return ("points", n_rows, MAX_LINE_POINTS)
    if chart in DISTRIBUTION_CHARTS and n_rows * n_series > MAX_BOXES:
        return ("boxes", n_rows * n_series, MAX_BOXES)
    if chart == "Heatmap" and n_rows > MAX_HEATMAP_ROWS:
        return ("rows", n_rows, MAX_HEATMAP_ROWS)
    if label_mark and chart in ("Line", "Area (Stacked)", "Area (Overlapped)", "Scatter") and n_rows * n_series > MAX_LABELS:
        return ("labels", n_rows * n_series, MAX_LABELS)
    return None


SINGLE_VALUE = STAT_SINGLE          # cada categoria aparece uma só vez: mostra o valor, sem dispersão


def bar_stat_slug(stat) -> str:
    """Nome curto da estatística ("mean", "median", "mode" ou "single"), usado nas chaves de tradução. Aceita também
    os nomes antigos ("Mean", "Median", "Single value") de projetos salvos."""
    s = str(stat).strip().lower()
    for slug in ("single", "median", "mode", "mean"):
        if s.startswith(slug):
            return slug
    return "mean"


def normalize_bar_stat(stat) -> str:
    """Nome atual da estatística ("Single Value", "Mean ± SD", "Median ± IQR" ou "Mode") para um nome antigo ou atual."""
    return {"single": STAT_SINGLE, "mean": STAT_MEAN, "median": STAT_MEDIAN, "mode": STAT_MODE}[bar_stat_slug(stat)]


def is_single_value(stat) -> bool:
    return bar_stat_slug(stat) == "single"


def repeated_categories(x, ydf: pd.DataFrame):
    """Categorias de `x` com mais de um valor em alguma coluna de `ydf`: [(categoria, nº de valores)], na ordem de
    aparição. Vazio quando cada categoria tem no máximo um valor (condição da estatística "Single Value")."""
    x = pd.Series(np.asarray(x, dtype=object), index=ydf.index)
    keep = x.notna()
    y = ydf[keep].apply(_series_to_numeric)
    n = y.groupby(x[keep].astype(str).to_numpy(), sort=False).count().max(axis=1)
    return [(str(c), int(k)) for c, k in n.items() if k > 1]


def repeated_x_values(series):
    """Séries [(rótulo, x, y)] com valores de X repetidos: [(rótulo, valor de X, nº de ocorrências)] (só o primeiro
    valor repetido de cada série) - o "Single Value" do Bar agrupado exige um valor por (série, X)."""
    out = []
    for lab, x, _y in series:
        vc = pd.Series(np.asarray(x)).value_counts()
        vc = vc[vc > 1]
        if len(vc):
            out.append((lab, vc.index[0], int(vc.iloc[0])))
    return out


def _group_mode(s: pd.Series):
    """Moda de `s` (a menor, se houver empate); NaN se não houver valores."""
    s = s.dropna()
    return float(s.mode().iloc[0]) if len(s) else np.nan


def summarize_by_category(x, ydf: pd.DataFrame, stat: str = "Mean"):
    """Resume as colunas numéricas de `ydf` por categoria de `x` (mesmo tamanho). Devolve (centro, desvio):
    `centro` tem a coluna "X" (categorias, na ordem de aparição) e uma coluna por série com a estatística
    (Mean, Median ou Mode); `desvio` tem as mesmas séries com o desvio padrão amostral de cada categoria
    (0 quando a categoria tem um único valor). Linhas sem categoria ficam de fora."""
    x = pd.Series(np.asarray(x, dtype=object), index=ydf.index)
    keep = x.notna()
    y = ydf[keep].apply(_series_to_numeric)
    g = y.groupby(x[keep].astype(str).to_numpy(), sort=False)
    mode = bar_stat_slug(stat)
    if mode == "single":
        center = g.first()
    elif mode == "median":
        center = g.median()
    elif mode == "mode":
        center = g.agg(_group_mode)
    else:
        center = g.mean()
    sd = g.std(ddof=1).fillna(0.0)
    center = center.reset_index().rename(columns={"index": "X"})
    center.columns = ["X"] + list(y.columns)
    return center, sd.reset_index(drop=True)


def _group_spread(g, stat):
    """Dispersão desenhada no topo das barras para um groupby `g` (de Series ou DataFrame): (inferior, superior) com a
    distância do centro até o fim da marcação. "Mean ± SD": desvio padrão amostral para os dois lados; "Median ± IQR":
    da mediana até Q1 e até Q3. Mode e Single Value não têm dispersão (None, None). Categorias com um só valor ficam
    sem marcação (NaN): não há desvio nem quartis de um valor só."""
    slug = bar_stat_slug(stat)
    if slug == "mean":
        lo = hi = g.std(ddof=1)
    elif slug == "median":
        med = g.median()
        lo, hi = med - g.quantile(0.25), g.quantile(0.75) - med
    else:
        return None, None
    enough = g.count() >= 2
    return lo.where(enough), hi.where(enough)


def summarize_with_spread(x, ydf: pd.DataFrame, stat: str = "Mean ± SD"):
    """Como summarize_by_category, mas devolve (centro, inferior, superior): a dispersão do topo das barras (ver
    _group_spread) em DataFrames com as colunas de `ydf` (None para Mode e Single Value)."""
    center, _sd = summarize_by_category(x, ydf, stat)
    xs = pd.Series(np.asarray(x, dtype=object), index=ydf.index)
    keep = xs.notna()
    g = ydf[keep].apply(_series_to_numeric).groupby(xs[keep].astype(str).to_numpy(), sort=False)
    lo, hi = _group_spread(g, stat)
    if lo is None:
        return center, None, None
    return center, lo.reset_index(drop=True), hi.reset_index(drop=True)


def sample_rows(df: pd.DataFrame, n) -> pd.DataFrame:
    """Amostra aleatória (nova a cada chamada) de `n` linhas; n <= 0 ou n >= nº de linhas devolve tudo."""
    try:
        n = int(n or 0)
    except (TypeError, ValueError):
        return df
    if n <= 0 or n >= len(df):
        return df
    return df.sample(n=n).reset_index(drop=True)


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

def clean_empty_values(df: pd.DataFrame):
    """Limpeza feita ao carregar uma tabela: textos só com espaços viram valor vazio (NaN) e as colunas/linhas
    totalmente vazias saem da tabela. Devolve (tabela limpa, nomes das colunas removidas, nº de linhas removidas)."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]        # cabeçalhos numéricos (ex.: Excel) viram texto
    for c in df.columns[df.dtypes == object]:
        ser = df[c]
        blank = ser.notna() & ser.astype(str).str.strip().eq("")
        if blank.any():
            df[c] = ser.mask(blank)
    n_rows = len(df)
    all_empty = [str(c) for c in df.columns[df.isna().all(axis=0)]]
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    return df, all_empty, n_rows - len(df)


def empty_value_counts(df: pd.DataFrame):
    """Quantidade de valores vazios/nulos por coluna: [(coluna, quantidade)], só as colunas com pelo menos um,
    na ordem da tabela."""
    counts = df.isna().sum()
    return [(str(c), int(n)) for c, n in counts.items() if n > 0]


def transpose_table(df: pd.DataFrame) -> pd.DataFrame:
    """Transposta de `df`: as linhas viram colunas e as colunas viram linhas - os nomes originais das colunas ficam
    na primeira coluna, "Index".
    Se a primeira coluna de `df` for categórica e tiver um valor distinto e preenchido em cada linha (nomes de
    alunos, de amostras...), ela é o rótulo das linhas: nomeia as colunas da transposta (um nome repetido recebe o
    sufixo " (2)", " (3)"...) e não entra como dado. Caso contrário as colunas levam o número da linha original."""
    first = df.iloc[:, 0] if df.shape[1] >= 2 else None
    if first is not None and not column_is_numeric(first) and first.notna().all():
        labels, seen = [], {"Index"}
        for v in first.astype(str).str.strip():
            name, k = v, 1
            while name in seen:
                k += 1
                name = f"{v} ({k})"
            seen.add(name)
            labels.append(name)
        t = df.iloc[:, 1:].T.reset_index()
        t.columns = ["Index"] + labels
    else:
        idx = list(df.index)
        names = [str(i) for i in idx] if len(set(map(str, idx))) == len(idx) else [str(i) for i in range(len(idx))]
        t = df.T.reset_index()
        t.columns = ["Index"] + names
    t["Index"] = t["Index"].astype(str)
    return t.infer_objects()


def column_is_numeric(ser: pd.Series) -> bool:
    """Regra única de classificação das colunas: numérica quando pelo menos metade dos valores PREENCHIDOS pode
    ser convertida em número (vírgula decimal aceita); categórica caso contrário. Valores vazios não contam
    (uma coluna de números com muitas lacunas continua numérica). Colunas só com True/False e datas são
    categóricas."""
    if pd.api.types.is_bool_dtype(ser) or pd.api.types.is_datetime64_any_dtype(ser) \
            or pd.api.types.is_timedelta64_dtype(ser):
        return False
    filled = ser.dropna()
    n = len(filled)
    if n == 0:
        return False
    if filled.dtype != object:
        return bool(pd.api.types.is_numeric_dtype(filled)) or _series_to_numeric(filled).notna().mean() >= 0.5
    if n <= 1000:
        # Caminho rápido (tabelas transpostas têm milhares de colunas curtas e o caminho vetorizado do pandas,
        # coluna a coluna, levaria vários segundos)
        ok = 0
        for v in filled.tolist():
            try:
                t = str(v).strip().replace("\u00a0", "").replace(",", ".")
                if "_" not in t and not np.isnan(float(t)):
                    ok += 1
            except (ValueError, TypeError):
                pass
        return ok / n >= 0.5
    return _series_to_numeric(filled).notna().mean() >= 0.5


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
        filled = df[x_col].notna().sum()
        if filled and x_num.notna().sum() / filled >= 0.5:
            x = x_num.to_numpy(dtype=float)
        else:
            x = df[x_col].astype(str).to_numpy()
        ydf = df.drop(columns=[x_col])
    else:
        first = df.iloc[:, 0]
        first_num = pd.to_numeric(first, errors="coerce")
        # Só contam os valores PREENCHIDOS (mesma regra de column_is_numeric): uma coluna numérica com muitas
        # lacunas (ex.: as tabelas largas de Histogram/Density, em que cada grupo é uma coluna completada com NaN)
        # não pode virar o "X" e sumir do gráfico.
        filled = first.notna().sum()
        non_numeric_ratio = ((first_num.isna() & first.notna()).sum() / filled) if filled else 0.0

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

def _spread_text(h, lo, hi, kind="sd"):
    """Texto do valor `h` com a dispersão (distâncias `lo`/`hi` até o fim da marcação): "valor ± desvio" (kind "sd") ou
    "mediana [Q1; Q3]" ("iqr"); só o valor quando a dispersão é indefinida (None ou NaN)."""
    txt = _fmt_val(h)
    if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
        return txt
    if kind == "iqr":
        return f"{txt} [{_fmt_val(h - lo)}; {_fmt_val(h + hi)}]"
    return f"{txt} ± {_fmt_val(hi)}"


def _annotate_points(ax, xs, ys, color=None, dx=4, dy=4, lo=None, hi=None, kind="sd"):
    # anota valores ao lado do ponto; com `lo`/`hi` (dispersão de cada ponto), escreve "valor ± desvio" / "mediana [Q1; Q3]"
    for k, (x, y) in enumerate(zip(xs, ys)):
        if not np.isfinite(y):
            continue
        spread = lo is not None and k < len(lo) and k < len(hi)
        ax.annotate(
            _spread_text(y, lo[k], hi[k], kind) if spread else _fmt_val(y),
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

def _annotate_bars(ax, bars, dy=3, sd=None, lo=None, hi=None, kind="sd"):
    """Escreve o valor de cada barra acima dela (acima da marcação de dispersão, se houver). `lo`/`hi`: distâncias do
    topo da barra até o fim da marcação (`sd` = o mesmo desvio para os dois lados). `kind`: "sd" escreve
    "valor ± desvio"; "iqr" escreve "mediana [Q1; Q3]". Barras sem dispersão (NaN) levam só o valor."""
    if sd is not None and lo is None:
        lo = hi = sd
    for k, b in enumerate(bars):
        h = b.get_height()
        if not np.isfinite(h):
            continue
        has = lo is not None and k < len(lo) and k < len(hi) and np.isfinite(lo[k]) and np.isfinite(hi[k])
        txt = _spread_text(h, lo[k], hi[k], kind) if has else _fmt_val(h)
        anchor = h
        if has:
            anchor = h + hi[k] if h >= 0 else h - lo[k]
        ax.annotate(
            txt,
            (b.get_x() + b.get_width() / 2, anchor),
            textcoords="offset points",
            xytext=(0, dy if h >= 0 else -dy),
            ha="center",
            va="bottom" if h >= 0 else "top",
            fontsize=12 if lo is None else 10,      # "valor ± desvio" é mais largo: fonte menor evita sobreposição
            weight="bold",
            color="#222222"
            # color=b.get_facecolor()
        )


def _draw_spread(ax, pos, y, lo, hi, color="#222222"):
    """Marcação de dispersão (barra de erro com travessões): de y-lo até y+hi. NaN em lo/hi = sem marcação."""
    if lo is None:
        return
    pos, y = np.asarray(pos, dtype=float), np.asarray(y, dtype=float)
    lo, hi = np.asarray(lo, dtype=float), np.asarray(hi, dtype=float)
    ok = np.isfinite(pos) & np.isfinite(y) & np.isfinite(lo) & np.isfinite(hi)
    if ok.any():
        ax.errorbar(pos[ok], y[ok], yerr=[np.clip(lo[ok], 0, None), np.clip(hi[ok], 0, None)], fmt="none",
                    ecolor=color, elinewidth=1.4, capsize=4, capthick=1.4, zorder=4)


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
    single_color: str = "#1f77b4",
    options=None,
    yerr=None,
    err_kind: str = "sd",
):
    """Barras. `yerr` traz a dispersão de cada barra quando as linhas são estatísticas por categoria: um DataFrame
    (mesmas colunas e linhas de Y) com o desvio padrão, ou uma tupla (inferior, superior) de DataFrames com a
    distância do topo da barra até o fim da marcação (Q1 e Q3 da mediana). A marcação é desenhada no topo das barras
    e, com label_mark, escrita acima dela: "valor ± desvio" (err_kind "sd") ou "mediana [Q1; Q3]" ("iqr")."""
    x, ydf = extract_x_y(df)
    yerr_lo = yerr_hi = None
    if yerr is not None:
        pair = yerr if isinstance(yerr, tuple) else (yerr, yerr)
        yerr_lo, yerr_hi = (pd.DataFrame(v).reset_index(drop=True) for v in pair)

    # Opções: largura, ordenação pelo valor da 1ª série e "Top N" (maiores valores; 0 = todos)
    bw = float(_opt(options, "bar_width"))
    sort_mode = _opt(options, "bar_sort")
    top_n = int(_opt(options, "bar_top") or 0)
    if (sort_mode != "None" or top_n > 0) and len(ydf.columns) >= 1 and len(x) > 0:
        key = ydf.iloc[:, 0].to_numpy(dtype=float)
        order = np.arange(len(x))
        if 0 < top_n < len(x):
            order = np.sort(np.argsort(-np.nan_to_num(key, nan=-np.inf), kind="stable")[:top_n])
        if sort_mode == "Ascending":
            order = order[np.argsort(key[order], kind="stable")]
        elif sort_mode == "Descending":
            order = order[np.argsort(-np.nan_to_num(key[order], nan=-np.inf), kind="stable")]
        x = np.asarray(x)[order]
        ydf = ydf.iloc[order].reset_index(drop=True)
        if yerr_lo is not None:
            yerr_lo, yerr_hi = (v.iloc[order].reset_index(drop=True) for v in (yerr_lo, yerr_hi))

    fig, ax = plt.subplots(figsize=(12, 6))

    def _err(i):
        """(inferior, superior) da série i: distâncias do topo da barra até o fim da marcação (None sem `yerr`)."""
        if yerr_lo is None or i >= yerr_lo.shape[1]:
            return None, None
        return yerr_lo.iloc[:, i].to_numpy(dtype=float), yerr_hi.iloc[:, i].to_numpy(dtype=float)

    x_pos = np.arange(len(x))
    n_series = len(ydf.columns)
    width = bw / max(n_series, 1)

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

        # Cores por categoria: a legenda lista as categorias (X categórico); com X numérico, só o nome da coluna.
        by_category = not np.issubdtype(np.asarray(x).dtype, np.number)
        lo, hi = _err(0)
        bars = ax.bar(x_pos, y, width=bw, label="_nolegend_" if by_category else str(col), color=bar_colors)
        _draw_spread(ax, x_pos, y, lo, hi)
        if by_category:
            _label_category_artists(bars.patches, x)
        bars_by_series.append((x_pos, y, bars, None))  # (xcenters, y, bars, color)

        if label_mark:
            _annotate_bars(ax, bars, lo=lo, hi=hi, kind=err_kind)

    else:
        # General case: color per series (column)
        if color_mode.startswith("Single"):
            series_colors = [single_color] * n_series
        else:
            series_colors = _get_series_colors(n_series, "Palette", palette_name, single_color)

        for i, col in enumerate(ydf.columns):
            y = ydf[col].to_numpy(dtype=float)
            pos = x_pos - (bw / 2 - width / 2) + i * width  # center of each bar in grouped layout
            lo, hi = _err(i)
            bars = ax.bar(pos, y, width=width, label=str(col), color=series_colors[i])
            _draw_spread(ax, pos, y, lo, hi)

            bars_by_series.append((pos, y, bars, series_colors[i]))

            if label_mark:
                _annotate_bars(ax, bars, lo=lo, hi=hi, kind=err_kind)

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
        _legend(ax, options)

    plt.tight_layout()
    return fig

def plot_line(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, title: str = "", xlabel: str = "", ylabel: str = "", label_mark: bool = False,
              color_mode: str = "Palette (multi-color)",
              palette_name: str = "Dark2",
              single_color: str = "#1f77b4",
    options=None, yerr=None, err_kind: str = "sd"):
    """Linhas. `yerr` (como no plot_bar: DataFrame com o desvio padrão ou tupla (inferior, superior) de DataFrames, com as
    colunas e linhas de Y) desenha, em cada ponto, a barra de erro na cor da série; com label_mark, o rótulo traz
    "valor ± desvio" (err_kind "sd") ou "mediana [Q1; Q3]" ("iqr")."""
    x, ydf = extract_x_y(df)
    yerr_lo = yerr_hi = None
    if yerr is not None:
        pair = yerr if isinstance(yerr, tuple) else (yerr, yerr)
        yerr_lo, yerr_hi = (pd.DataFrame(v).reset_index(drop=True) for v in pair)
    fig, ax = plt.subplots(figsize=(12, 6))

    x_is_num = np.issubdtype(np.asarray(x).dtype, np.number)
    x_plot = np.asarray(x, dtype=float) if x_is_num else np.arange(len(x), dtype=float)

    colors = _get_series_colors(len(ydf.columns), color_mode, palette_name, single_color)

    for i, col in enumerate(ydf.columns):
        yvals = ydf[col].to_numpy(dtype=float)
        ms = float(_opt(options, "marker_size"))
        line = ax.plot(x_plot, yvals, marker="o" if ms > 0 else None, markersize=ms,
                       linewidth=float(_opt(options, "line_width")), label=str(col), color=colors[i])[0]
        lo = hi = None
        if yerr_lo is not None and i < yerr_lo.shape[1]:
            lo, hi = yerr_lo.iloc[:, i].to_numpy(dtype=float), yerr_hi.iloc[:, i].to_numpy(dtype=float)
            _draw_spread(ax, x_plot, yvals, lo, hi, color=line.get_color())
        if label_mark:
            _annotate_points(ax, x_plot, yvals, color=line.get_color(), dx=8 if lo is not None else 4, lo=lo, hi=hi,
                             kind=err_kind)

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
        _legend(ax, options)
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
    single_color: str = "#1f77b4",
    options=None
):
    x, ydf = extract_x_y(df)
    ps, pa = float(_opt(options, "point_size")), float(_opt(options, "point_alpha"))
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
            ax.scatter(xs, ys, color=single_color, s=ps, alpha=pa, label=str(ycol))
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
                    s=ps, alpha=pa,
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
            _legend(ax, options)
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
        ax.scatter(x_plot, yvals, label=str(col), color=colors[i], s=ps, alpha=pa)
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
        _legend(ax, options)
    plt.tight_layout()
    return fig

def plot_area_stacked(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, title: str = "", xlabel: str = "", ylabel: str = "", label_mark: bool = False,
              color_mode: str = "Palette (multi-color)",
              palette_name: str = "Dark2",
              single_color: str = "#1f77b4",
    options=None):

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
        colors=colors,
        alpha=float(_opt(options, "area_stacked_alpha"))
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
        _legend(ax, options)
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
    single_color: str = "#1f77b4",
    options=None
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
            alpha=float(_opt(options, "area_overlap_alpha")),
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
        _legend(ax, options)

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
    single_color: str = "#1f77b4",
    options=None
):
    x, ydf = extract_x_y(df)
    whis = float(_opt(options, "box_whisker"))          # limiar do bigode (x IQR); fora dele = outlier
    box_w = float(_opt(options, "box_width"))
    show_fliers = bool(_opt(options, "box_outliers"))
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
            whis=whis, widths=box_w, showfliers=show_fliers,
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
        if show_legend and not color_mode.startswith("Single"):
            _label_category_artists(bp["boxes"], labels)        # legenda: as categorias e suas cores

        # Label Mark: whiskers/Q1/Q2/Q3 + outliers
        if label_mark:
            x_offset = 0.35
            for i, arr in enumerate(data, start=1):
                if arr.size == 0:
                    continue

                Q1, Q2, Q3 = np.percentile(arr, [25, 50, 75])
                IQR = Q3 - Q1
                limit_below = arr[arr >= (Q1 - whis * IQR)].min()
                limit_above = arr[arr <= (Q3 + whis * IQR)].max()

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
            whis=whis, widths=box_w, showfliers=show_fliers,
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
                limit_below = arr[arr >= (Q1 - whis * IQR)].min()
                limit_above = arr[arr <= (Q3 + whis * IQR)].max()

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
    if show_legend:
        _legend(ax, options)
    plt.tight_layout()
    return fig

def plot_heatmap(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "", xlabel: str = "", ylabel: str = "",
                 color_mode: str = "Palette (multi-color)",
                 palette_name: str = "viridis",
                 single_color: str = "#1f77b4",
    options=None):

    from matplotlib.colors import LinearSegmentedColormap

    _, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    data = ydf.to_numpy(dtype=float)
    norm_mode = _opt(options, "heat_normalize")
    if norm_mode != "None" and data.size:
        with np.errstate(all="ignore"):
            if norm_mode.startswith("Min-Max"):
                lo, hi = np.nanmin(data, axis=0), np.nanmax(data, axis=0)
                data = (data - lo) / np.where(hi - lo == 0, 1.0, hi - lo)
            else:
                sd = np.nanstd(data, axis=0)
                data = (data - np.nanmean(data, axis=0)) / np.where(sd == 0, 1.0, sd)

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
    if bool(_opt(options, "heat_colorbar")):
        fig.colorbar(im, ax=ax)
    # "Mostrar valores nos pontos": escreve o valor em cada célula (até 400 células, para continuar legível)
    if label_mark and data.size <= 400:
        for (r, c), v in np.ndenumerate(data):
            if np.isfinite(v):
                ax.text(c, r, _fmt_val(v), ha="center", va="center", fontsize=8, color="#222222",
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.6))

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
    single_color: str = "#1f77b4",
    options=None
):
    x, ydf = extract_x_y(df)
    v_kw = dict(widths=float(_opt(options, "violin_width")), showmeans=False,
                showmedians=bool(_opt(options, "violin_median")), showextrema=bool(_opt(options, "violin_extrema")),
                bw_method=(float(_opt(options, "violin_bw")) or None))   # 0 = automático
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
            **v_kw
        )

        # ---- colors ----
        if color_mode.startswith("Single"):
            colors = [single_color] * len(groups)
        else:
            colors = _get_series_colors(len(groups), "Palette", palette_name, single_color)

        for pc, c in zip(parts["bodies"], colors):
            pc.set_facecolor(c)
            pc.set_alpha(0.6)
        if show_legend and not color_mode.startswith("Single"):
            _label_category_artists(parts["bodies"], labels)        # legenda: as categorias e suas cores

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
            **v_kw
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
    if show_legend:
        _legend(ax, options)

    plt.tight_layout()
    return fig

def plot_histogram(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "",
                   xlabel: str = "", ylabel: str = "",
                   color_mode: str = "Palette (multi-color)",
                   palette_name: str = "Dark2",
                   single_color: str = "#1f77b4",
    options=None):

    _, ydf = extract_x_y(df)
    fig, ax = plt.subplots(figsize=(12, 6))

    n = len(ydf.columns)
    colors = _get_series_colors(n, color_mode, palette_name, single_color)

    # Todas as séries usam as MESMAS faixas (bins): com faixas próprias de cada série, um grupo de valores pequenos
    # (ex.: IC50 dos ativos, 0-0,7) ficaria com barras minúsculas ao lado de outro de valores grandes (1230) e
    # pareceria ausente; com faixas comuns, as barras são comparáveis.
    nb = int(_opt(options, "hist_bins"))
    pooled = np.concatenate([ydf[c].dropna().to_numpy(dtype=float) for c in ydf.columns if ydf[c].notna().any()] or [np.array([])])
    pooled = pooled[np.isfinite(pooled)]
    bins = np.histogram_bin_edges(pooled, bins=nb) if pooled.size else nb

    # overlay hist para múltiplas séries
    for i, col in enumerate(ydf.columns):
        vals = ydf[col].dropna().to_numpy(dtype=float)
        ax.hist(vals, bins=bins, density=bool(_opt(options, "hist_density")),
                cumulative=bool(_opt(options, "hist_cumulative")), alpha=0.6 if n > 1 else 0.8,
                label=str(col), color=colors[i])

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
            _legend(ax, options)

    plt.tight_layout()
    return fig

def _kde_bw(values: np.ndarray, bw_scale: float = 1.0) -> float:
    """Largura de banda do KDE (regra de Silverman); 0 se não houver como calcular (menos de 2 valores ou sem variação)."""
    v = values[np.isfinite(values)]
    if v.size < 2:
        return 0.0
    std = np.std(v, ddof=1)
    if std <= 0:
        return 0.0
    return float(1.06 * std * (v.size ** (-1 / 5)) * float(bw_scale))


def _kde_1d(values: np.ndarray, grid: np.ndarray, bw_scale: float = 1.0):
    """KDE simples (gaussiana) sem SciPy."""
    v = values[np.isfinite(values)]
    bw = _kde_bw(v, bw_scale)
    if bw <= 0:
        return np.zeros_like(grid)
    n = v.size

    # KDE
    diff = (grid[:, None] - v[None, :]) / bw
    dens = np.exp(-0.5 * diff * diff).sum(axis=1) / (n * bw * np.sqrt(2 * np.pi))
    return dens

def plot_density(df: pd.DataFrame, dpi: int, trend_mode: str = "None", show_legend: bool = False, label_mark: bool = False, title: str = "",
                 xlabel: str = "", ylabel: str = "",
                 color_mode: str = "Palette (multi-color)",
                 palette_name: str = "Dark2",
                 single_color: str = "#1f77b4",
    options=None):

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

    grid = np.linspace(xmin, xmax, int(_opt(options, "kde_points")))

    bw_scale, npts = float(_opt(options, "kde_bw")), int(_opt(options, "kde_points"))
    peak_one = bool(_opt(options, "kde_peak"))
    for i, col in enumerate(ydf.columns):
        vals = ydf[col].dropna().to_numpy(dtype=float)
        # Grade própria da série: a comum (todo o intervalo dos dados) mais uma grade fina sobre o intervalo dela.
        # Só com a comum, um grupo de valores pequenos num intervalo grande (ex.: 0-0,7 em 0-1230) cairia em um ou dois
        # pontos e a curva seria perdida.
        g_i = grid
        bw_i = _kde_bw(vals, bw_scale)
        if bw_i > 0:
            v_ok = vals[np.isfinite(vals)]
            g_i = np.union1d(grid, np.linspace(v_ok.min() - 3 * bw_i, v_ok.max() + 3 * bw_i, npts))
        dens = _kde_1d(vals, g_i, bw_scale)
        if peak_one and np.nanmax(dens) > 0:          # compara só a FORMA das curvas (pico = 1)
            dens = dens / np.nanmax(dens)
        ax.plot(g_i, dens, label=str(col), color=colors[i], linewidth=2)
        if bool(_opt(options, "kde_fill")):
            ax.fill_between(g_i, dens, color=colors[i], alpha=0.25)

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
            _legend(ax, options)

    plt.tight_layout()
    return fig

def group_labels(df: pd.DataFrame, cat_cols):
    """Rótulo de grupo de cada linha: os valores das colunas categóricas `cat_cols` unidos por " | " (NaN se algum
    estiver ausente)."""
    cat_cols = list(cat_cols)
    ok = df[cat_cols].notna().all(axis=1)
    lab = df[cat_cols[0]].astype(str)
    for c in cat_cols[1:]:
        lab = lab + " | " + df[c].astype(str)
    return lab.where(ok)


def build_grouped_series(df: pd.DataFrame, x_col, y_cols, cat_cols):
    """Séries [(rótulo, x, y)] de um gráfico X numérico contra Y numérico com categorias: uma série por grupo
    (na ordem de aparição) e, com várias colunas Y, por (coluna Y, grupo) - rótulo "Y | grupo". Linhas com X ou
    Y ausentes ficam fora de cada série."""
    g = group_labels(df, cat_cols)
    xv = _series_to_numeric(df[x_col])
    groups = list(pd.unique(g.dropna()))
    out = []
    for yc in y_cols:
        yv = _series_to_numeric(df[yc])
        for grp in groups:
            m = (g == grp) & xv.notna() & yv.notna()
            if m.any():
                label = grp if len(y_cols) == 1 else f"{yc} | {grp}"
                out.append((label, xv[m].to_numpy(dtype=float), yv[m].to_numpy(dtype=float)))
    return out


def grouped_values_frame(df: pd.DataFrame, y_cols, cat_cols):
    """Tabela larga para Histogram / Density com categorias: uma coluna por grupo (ou "Y | grupo"), cada uma com os
    valores de Y daquele grupo (colunas de tamanhos diferentes são completadas com NaN)."""
    g = group_labels(df, cat_cols)
    cols = {}
    for yc in y_cols:
        yv = _series_to_numeric(df[yc])
        for grp in pd.unique(g.dropna()):
            vals = yv[(g == grp) & yv.notna()].reset_index(drop=True)
            if len(vals):
                cols[grp if len(y_cols) == 1 else f"{yc} | {grp}"] = vals
    if not cols:
        raise ValueError("No numeric values for the selected categories.")
    return pd.DataFrame(cols)


def plot_grouped_xy(chart: str, series, dpi: int = 300, trend_mode: str = "None", show_legend: bool = False,
                    title: str = "", xlabel: str = "", ylabel: str = "", label_mark: bool = False,
                    palette_name: str = "Dark2", single_color: str = "#1f77b4", options=None,
                    x_labels=None, color_mode: str = "Palette (multi-color)", spread=None, spread_kind: str = "sd"):
    """Gráfico com o eixo X na escala de uma coluna numérica e uma série (cor) por categoria: `series` é a lista
    [(rótulo, x, y)] de build_grouped_series. `chart`: Scatter, Line, Area (Overlapped), Area (Stacked) ou Bar
    (barras agrupadas por valor de X, com a estatística bar_stat de cada categoria em cada X). A legenda lista as
    categorias (rótulos das séries); as cores sempre vêm da paleta, pois é ela que distingue as categorias.
    `spread` (só no Line): para cada série, (inferior, superior) com a dispersão de cada ponto (ver aggregate_series)."""
    if chart not in GROUPED_XY_CHARTS:
        raise ValueError(f"{chart} does not support categories on a numeric X.")
    series = [(lab, np.asarray(x, dtype=float), np.asarray(y, dtype=float)) for lab, x, y in series]
    if not series:
        raise ValueError("No valid (X, Y) values for the selected columns.")
    n = len(series)
    # Com várias séries as cores vêm da paleta (é ela que distingue as categorias); com uma só, vale o modo escolhido.
    if n == 1 and str(color_mode).startswith("Single"):
        colors = [single_color]
    else:
        colors = _get_series_colors(n, "Palette", palette_name, single_color)
    fig, ax = plt.subplots(figsize=(12, 6))
    trend_xy = []                                   # (rótulo, cor, xs, ys) usados pelas linhas de tendência

    if chart == "Scatter":
        ps, pa = float(_opt(options, "point_size")), float(_opt(options, "point_alpha"))
        for (lab, x, y), c in zip(series, colors):
            ax.scatter(x, y, s=ps, alpha=pa, color=c, label=lab)
            if label_mark:
                _annotate_points(ax, x, y, color="#222222", dx=6, dy=6)
            trend_xy.append((lab, c, x, y))
    elif chart in ("Line", "Area (Overlapped)"):
        ms = float(_opt(options, "marker_size"))
        for k, ((lab, x, y), c) in enumerate(zip(series, colors)):
            o = np.argsort(x, kind="stable")
            x, y = x[o], y[o]
            lo = hi = None
            if chart == "Line" and spread is not None and spread[k][0] is not None:
                lo, hi = spread[k][0][o], spread[k][1][o]
            if chart == "Line":
                ax.plot(x, y, marker="o" if ms > 0 else None, markersize=ms, linewidth=float(_opt(options, "line_width")),
                        label=lab, color=c)
                _draw_spread(ax, x, y, lo, hi, color=c)
            else:
                ax.fill_between(x, y, alpha=float(_opt(options, "area_overlap_alpha")), color=c, label=lab)
                ax.plot(x, y, marker="o", linestyle="None", color=c, markersize=4)
            if label_mark:
                _annotate_points(ax, x, y, color="#222222", dx=8 if lo is not None else 4, lo=lo, hi=hi, kind=spread_kind)
            trend_xy.append((lab, c, x, y))
    elif chart == "Area (Stacked)":
        grid = np.unique(np.concatenate([x for _, x, _ in series]))
        layers = []
        for lab, x, y in series:                    # valores repetidos de X: média; X sem valor: interpolado (0 fora da faixa)
            avg = pd.Series(y).groupby(x).mean()
            layers.append(np.interp(grid, avg.index.to_numpy(dtype=float), avg.to_numpy(dtype=float), left=0.0, right=0.0))
        ax.stackplot(grid, *layers, labels=[lab for lab, _, _ in series], colors=colors,
                     alpha=float(_opt(options, "area_stacked_alpha")))
        for (lab, _x, _y), c, layer in zip(series, colors, layers):
            trend_xy.append((lab, c, grid, layer))
    else:                                           # Bar: barras agrupadas por valor de X
        stat = bar_stat_slug(_opt(options, "bar_stat"))
        uniq = (np.arange(len(x_labels), dtype=float) if x_labels is not None
                else np.unique(np.concatenate([x for _, x, _ in series])))
        pos = {v: i for i, v in enumerate(uniq)}
        bw = float(_opt(options, "bar_width"))
        width = bw / n
        for k, ((lab, x, y), c) in enumerate(zip(series, colors)):
            g = pd.Series(y).groupby(x)
            center = (g.first() if stat == "single" else g.median() if stat == "median"
                      else g.agg(_group_mode) if stat == "mode" else g.mean())
            lo, hi = _group_spread(g, stat)
            lo = None if lo is None else lo.to_numpy(dtype=float)
            hi = None if hi is None else hi.to_numpy(dtype=float)
            xs_pos = np.array([pos[v] for v in center.index], dtype=float) - (bw / 2 - width / 2) + k * width
            bars = ax.bar(xs_pos, center.to_numpy(dtype=float), width=width, color=c, label=lab)
            _draw_spread(ax, xs_pos, center.to_numpy(dtype=float), lo, hi)
            if label_mark:
                _annotate_bars(ax, bars, lo=lo, hi=hi, kind="iqr" if stat == "median" else "sd")
            trend_xy.append((lab, c, np.array([pos[v] for v in center.index], dtype=float), center.to_numpy(dtype=float)))
        ax.set_xticks(np.arange(len(uniq)))
        ax.set_xticklabels([_fmt_val(v) for v in uniq], rotation=0 if len(uniq) <= 12 else 90, ha="center")

    if x_labels is not None:                        # eixo X categórico: as posições 0..n-1 levam o nome da categoria
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels([str(c) for c in x_labels], rotation=0 if len(x_labels) <= 12 else 90, ha="center")

    if trend_mode != "None":
        for lab, c, xs, ys in trend_xy:
            _trendline_xy(ax, xs, ys, trend_mode, color=c, label=f"Trend ({lab})", linewidth=2)
        if show_legend and trend_mode != "Moving Average":
            eq_items = []
            for lab, c, xs, ys in trend_xy:
                eq, r2 = _trend_equation_and_r2(xs, ys, trend_mode)
                if eq:
                    eq_items.append((f"{lab}: {eq}" + (f" (R²={r2:.3f})" if r2 is not None else ""), c))
            _draw_trend_equations(ax, eq_items, is_3d=False)

    ax.set_title(title or f"{chart}", fontsize=14, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    if show_legend:
        _legend(ax, options)
    plt.tight_layout()
    return fig


def _sort_by_flow(tot: pd.Series, mode: str) -> pd.Series:
    """`tot` (fluxo por categoria, na ordem de aparição) ordenado pelo valor se mode for Ascending / Descending;
    qualquer outro modo (None) mantém a ordem recebida."""
    mode = str(mode).strip().lower()
    if mode == "ascending":
        return tot.sort_values(ascending=True, kind="stable")
    if mode == "descending":
        return tot.sort_values(ascending=False, kind="stable")
    return tot


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
    options=None,
):
    """Diagrama de Sankey (aluvial) de 2 ou mais colunas categóricas: cada coluna é uma etapa, cada
    categoria um nó e cada faixa liga duas etapas vizinhas com largura proporcional ao número de
    linhas que passam daquela categoria para a seguinte (ou à soma de `weight_col`, se informada).
    Linhas com valor ausente em qualquer etapa (ou peso <= 0) ficam de fora, de modo que todas as
    etapas somam o mesmo total. `max_nodes` (1 a SANKEY_MAX_NODES_PER_STAGE) mantém, em cada coluna,
    só as categorias de maior fluxo (contagem de linhas ou soma do peso); as linhas que têm uma
    categoria de fora em qualquer etapa são descartadas. `label_mark` escreve o valor de cada nó; `show_legend` é ignorado
    (os próprios nós já são rotulados). Opção sankey_orient: "Horizontal" (etapas da esquerda para a direita) ou
    "Vertical" (de cima para baixo). Opção sankey_sort: ordem dos nós em cada etapa (None = ordem de aparição nos
    dados; Ascending / Descending = pelo fluxo)."""
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

    # Nós de cada etapa. Sort = None: na ordem em que aparecem nos dados; Ascending / Descending: pelo fluxo
    # (contagem de linhas ou soma do peso), do menor para o maior ou vice-versa. As próprias etapas seguem a ordem
    # de `stage_cols` (a ordem em que o usuário selecionou as colunas).
    sort_mode = str(_opt(options, "sankey_sort")).strip()
    stages = [_sort_by_flow(w.groupby(data[c], sort=False).sum(), sort_mode) for c in stage_cols]

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

    # Orientação: as coordenadas são calculadas como (ao longo das etapas, dentro da etapa) e só então levadas
    # para (x, y): Horizontal = etapas da esquerda para a direita; Vertical = de cima para baixo.
    vertical = str(_opt(options, "sankey_orient")).strip().lower() == "vertical"
    fig, ax = plt.subplots(figsize=(12, 7) if vertical else (12, 6))
    n_st = len(stage_cols)

    def _pt(along, across):
        return (across, along) if vertical else (along, across)

    def _ribbon(x0, y0_top, y0_bot, x1, y1_top, y1_bot, color):
        xm = (x0 + x1) / 2.0
        verts = [(x0, y0_top), (xm, y0_top), (xm, y1_top), (x1, y1_top),
                 (x1, y1_bot), (xm, y1_bot), (xm, y0_bot), (x0, y0_bot), (x0, y0_top)]
        verts = [_pt(a, c) for a, c in verts]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                 Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", alpha=float(_opt(options, "sankey_alpha")), zorder=1))

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
            (rx, ry), (ex, ey) = _pt(i, y), _pt(i + node_w, y + h)
            ax.add_patch(Rectangle((min(rx, ex), min(ry, ey)), abs(ex - rx), abs(ey - ry), facecolor=node_color[i][cat],
                                   edgecolor="#333333", linewidth=0.6, zorder=3))
            lab = str(cat)
            if label_mark:
                lab += f" ({_fmt_val(h)})"
            tx, ty = _pt(i + node_w + 0.02, y + h / 2.0)
            if vertical:    # rótulo abaixo do nó (girado quando a etapa tem muitos nós)
                ax.text(tx, ty, lab, va="top", ha="center", rotation=0 if len(pos) <= 6 else 90, fontsize=9, zorder=4)     # rótulo sem fundo (transparente)
            else:
                ax.text(tx, ty, lab, va="center", ha="left", fontsize=9, zorder=4)     # rótulo sem fundo (transparente)

    for i, c in enumerate(stage_cols):
        if vertical:
            ax.text(-0.02 * full, i + node_w / 2.0, str(c), ha="right", va="center", fontsize=11, fontweight="bold")
        else:
            ax.text(i + node_w / 2.0, -0.02 * full, str(c), ha="center", va="bottom", fontsize=11, fontweight="bold")

    if vertical:
        ax.set_xlim(-0.3 * full, full * 1.02)
        ax.set_ylim(n_st - 1 + node_w + 0.5, -0.15)     # eixo Y invertido: primeira etapa no topo
    else:
        ax.set_xlim(-0.1, n_st - 1 + node_w + 0.5)
        ax.set_ylim(full * 1.02, -0.08 * full)       # eixo Y invertido: primeiro nó no topo
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=14)
    else:
        ax.set_title("Sankey: " + " → ".join(map(str, stage_cols)), fontsize=14, pad=14)
    plt.tight_layout()
    return fig

def plot_chord(
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
    max_nodes: int = CHORD_MAX_NODES,
    options=None,
):
    """Sankey Chord (diagrama de cordas dirigido): as categorias formam um círculo e cada faixa liga uma
    categoria a qualquer outra (ou a ela mesma). As colunas de `stage_cols` (2 ou mais) são lidas aos pares
    vizinhos - a 1ª é a origem e a 2ª o destino, depois a 2ª é a origem e a 3ª o destino, e assim por diante;
    categorias com o mesmo nome em colunas diferentes são o mesmo nó. A largura de cada faixa é o número de
    linhas que vão da origem ao destino (ou a soma de `weight_col`); ela sai da origem na cor dela. O arco de
    cada nó mede tudo o que sai e entra nele. `max_nodes` mantém só os nós de maior fluxo; linhas com valor
    ausente em algum dos dois lados (ou peso <= 0) ficam de fora de cada par. Opções (`options`): chord_alpha,
    chord_gap (graus entre os arcos), chord_self (desenhar ligações de um nó com ele mesmo) e chord_sort
    (ordem dos nós no círculo: None = ordem de aparição, Ascending / Descending = pelo fluxo total).
    `label_mark` escreve o fluxo total ao lado de cada nome; `show_legend` é ignorado."""
    from matplotlib.patches import PathPatch, Wedge
    from matplotlib.path import Path

    stage_cols = list(stage_cols) if stage_cols is not None else [c for c in df.columns if c != weight_col]
    if len(stage_cols) < 2:
        raise ValueError("Sankey Chord needs at least two categorical columns (source and target).")

    w_all = _series_to_numeric(df[weight_col]) if weight_col is not None else pd.Series(1.0, index=df.index)
    links = {}                                   # (origem, destino) -> peso somado
    appear = {}                                  # nós na ordem de aparição (coluna a coluna, na ordem de `stage_cols`)
    for a, b in zip(stage_cols[:-1], stage_cols[1:]):
        sub = pd.DataFrame({"a": df[a], "b": df[b], "w": w_all}).dropna()
        sub = sub[sub["w"] > 0]
        if sub.empty:
            continue
        sub["a"], sub["b"] = sub["a"].astype(str), sub["b"].astype(str)
        sub = sub[(sub["a"].str.strip() != "") & (sub["b"].str.strip() != "")]      # texto vazio não é categoria
        if sub.empty:
            continue
        for v in list(pd.unique(sub["a"])) + list(pd.unique(sub["b"])):
            appear.setdefault(v, len(appear))
        for (src, dst), val in sub.groupby(["a", "b"])["w"].sum().items():
            links[(src, dst)] = links.get((src, dst), 0.0) + float(val)
    if not _opt(options, "chord_self"):
        links = {k: v for k, v in links.items() if k[0] != k[1]}
    if not links:
        raise ValueError("No rows with valid values in the selected columns.")

    # Só os `max_nodes` nós de maior fluxo (saída + entrada) ficam; as ligações com um nó de fora saem.
    max_nodes = max(2, min(int(max_nodes or CHORD_MAX_NODES), CHORD_MAX_NODES))
    flow = {}
    for (src, dst), v in links.items():
        flow[src] = flow.get(src, 0.0) + v
        flow[dst] = flow.get(dst, 0.0) + v
    keep = set(sorted(flow, key=lambda n: (-flow[n], n))[:max_nodes])
    links = {k: v for k, v in links.items() if k[0] in keep and k[1] in keep}
    if not links:
        raise ValueError("The most frequent categories of the selected columns are never linked to each other.")
    # Ordem no círculo: Sort = None segue a ordem de aparição (as colunas na ordem em que o usuário as selecionou);
    # Ascending / Descending, o fluxo total do nó. Nó sem nenhuma ligação não entra no círculo.
    linked = {n for k in links for n in k}
    nodes = [n for n in appear if n in linked]
    flow = {n: sum(v for k, v in links.items() for e in k if e == n) for n in nodes}
    sort_mode = str(_opt(options, "chord_sort")).strip().lower()
    if sort_mode in ("ascending", "descending"):
        nodes.sort(key=lambda n: flow[n], reverse=(sort_mode == "descending"))
    n = len(nodes)
    idx = {name: i for i, name in enumerate(nodes)}
    W = np.zeros((n, n))                          # W[i, j]: peso de i -> j
    for (src, dst), v in links.items():
        W[idx[src], idx[dst]] += v
    total_node = W.sum(axis=1) + W.sum(axis=0)    # tudo o que sai e entra em cada nó

    gap_deg = float(_opt(options, "chord_gap"))
    gap = np.deg2rad(gap_deg)
    span = 2 * np.pi - gap * n
    if span <= 0:
        gap, span = 0.0, 2 * np.pi
    unit = span / total_node.sum()                # radianos por unidade de peso
    start = np.zeros(n)
    ang = np.pi / 2                               # o 1º nó começa no topo e o círculo segue no sentido horário
    for i in range(n):
        start[i] = ang
        ang -= total_node[i] * unit + gap

    # Dentro do arco de cada nó, as "vagas" seguem a ordem dos parceiros no círculo (do mais distante para o
    # mais próximo no sentido do arco), cada parceiro com a saída (i->j) seguida da entrada (j->i), o que evita
    # cruzamentos desnecessários. Como o círculo corre no sentido horário, o ângulo decresce dentro do arco.
    out_slot, in_slot = {}, {}                    # (origem, destino) -> (ang_ini, ang_fim)
    for i in range(n):
        a = start[i]
        for j in [i] + [(i - m) % n for m in range(1, n)]:       # ele mesmo, depois i-1, i-2, ...
            v_out, v_in = W[i, j], W[j, i]
            if v_out > 0:
                out_slot[(i, j)] = (a, a - v_out * unit)
                a -= v_out * unit
            if v_in > 0:
                in_slot[(j, i)] = (a, a - v_in * unit)
                a -= v_in * unit

    colors = _get_series_colors(max(n, 1), color_mode, palette_name, single_color)
    fig, ax = plt.subplots(figsize=(9, 9))
    r_out, r_in = 1.0, 0.92

    def _arc_pts(a0, a1, r):
        m = max(2, int(abs(a1 - a0) / 0.03) + 2)
        t = np.linspace(a0, a1, m)
        return list(zip(r * np.cos(t), r * np.sin(t)))

    alpha = float(_opt(options, "chord_alpha"))
    for (src, dst), v in sorted(((k, W[k]) for k in zip(*np.nonzero(W))), key=lambda kv: -kv[1]):
        s0, s1 = out_slot[(src, dst)]
        t0, t1 = in_slot[(src, dst)]
        pts_s = _arc_pts(s0, s1, r_in)
        pts_t = _arc_pts(t0, t1, r_in)
        verts = [pts_s[0]] + pts_s[1:] + [(0.0, 0.0), pts_t[0]] + pts_t[1:] + [(0.0, 0.0), pts_s[0]]
        codes = ([Path.MOVETO] + [Path.LINETO] * (len(pts_s) - 1) + [Path.CURVE3, Path.CURVE3]
                 + [Path.LINETO] * (len(pts_t) - 1) + [Path.CURVE3, Path.CURVE3])
        verts.append(pts_s[0]); codes.append(Path.CLOSEPOLY)
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=colors[src], edgecolor="none", alpha=alpha, zorder=1))

    for i, name in enumerate(nodes):
        a0, a1 = start[i], start[i] - total_node[i] * unit
        ax.add_patch(Wedge((0, 0), r_out, np.rad2deg(a1), np.rad2deg(a0), width=r_out - r_in - 0.005,
                           facecolor=colors[i], edgecolor="#333333", linewidth=0.6, zorder=3))
        mid = (a0 + a1) / 2.0
        deg = np.rad2deg(mid) % 360
        lab = str(name)
        if label_mark:
            lab += f" ({_fmt_val(total_node[i])})"
        left = 90 < deg < 270
        ax.text(1.04 * np.cos(mid), 1.04 * np.sin(mid), lab, ha="right" if left else "left", va="center",
                rotation=deg + 180 if left else deg, rotation_mode="anchor", fontsize=9, zorder=4)

    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal"); ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=14)
    else:
        ax.set_title("Sankey Chord: " + " → ".join(map(str, stage_cols)), fontsize=14, pad=14)
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
    "Sankey Chord": plot_chord,
}

# ======= 2D CHARTS =========
def plot_scatter_2D(df: pd.DataFrame, x_col: str, y_col: str, group_col: str,
                                       title: str = "", xlabel: str = "", ylabel: str = "",
                                       palette_name: str = "tab10", single_color: str = "#1f77b4",
                                       color_mode: str = "Palette (multi-color)",
                                       label_mark: bool = False, trend_mode: str = "None", show_legend: bool = False,
                                       options=None):
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
        ax.scatter(d["x"], d["y"], label=str(c), color=colors[c],
                   s=float(_opt(options, "point_size")), alpha=float(_opt(options, "point_alpha")))
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
        _legend(ax, options, dedupe=True)
        
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
    show_legend: bool = False,
    options=None
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
                s=float(_opt(options, "point_size", 30.0)),
                alpha=float(_opt(options, "point_alpha", 0.75)),
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
            s=float(_opt(options, "point_size", 30.0)),
            alpha=float(_opt(options, "point_alpha", 0.75)),
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
    # LEGENDA (sem rótulos repetidos, na posição escolhida)
    # ==========================================================
    if show_legend:
        _legend(ax, options, dedupe=True)

    plt.tight_layout()
    return fig



# ==========================================================================================================
# PAPÉIS DAS COLUNAS
# ----------------------------------------------------------------------------------------------------------
# A seleção de colunas é lida da mesma forma em qualquer gráfico: o papel de cada coluna depende do que ela É
# (numérica ou categórica) e de onde foi marcada (X, Y ou Z), e não de uma "dimensão" escolhida antes.
#
#   X numérica (no máx. uma)  -> EIXO horizontal
#   X categórica (uma ou mais) -> CATEGORIAS no eixo / CORES (grupos), conforme o gráfico
#   Y numérica                 -> VALORES
#   Z numérica (só no 3D)      -> terceiro eixo
#
# CHART_ROLES declara, por tipo de gráfico, a família de regras que vale para ele. resolve_roles() aplica a
# regra e devolve um RolePlan (ou levanta PlanError com a chave da mensagem); papéis que o gráfico não usa viram
# `notices` (a interface avisa em vez de ignorar em silêncio). execute_plan() monta os dados e desenha.
#
#  família "axis"   Bar, Line, Scatter, Area (S/O): X numérico = eixo; X categórico = categorias no eixo; as outras
#                   colunas categóricas de X viram cores (uma série por categoria); Y = valores (agregados pela
#                   Statistic quando uma categoria/valor de X se repete; só o Scatter mostra todas as instâncias);
#                   Y vazio = contagem das categorias de X.
#  família "values" Box Plot, Violin, Histogram, Density(KDE), Heatmap: o que se desenha são os VALORES numéricos
#                   (Y; com Y vazio, as colunas numéricas de X); X categórico agrupa (Box/Violin: uma caixa por
#                   categoria; Histogram/Density: uma curva por categoria; Heatmap: não usa) ; X numérico com Y
#                   preenchido não é usado (aviso).
#  família "flow"   Sankey, Sankey Chord: todas as colunas de X (numéricas ou não) são as etapas, na ordem de
#                   seleção; Y (no máx. uma) = peso do fluxo.
#  3D               Scatter: X numérico = eixo X, Y, Z; X categórico = cores.
# ==========================================================================================================
CHART_ROLES = {
    "Bar":               {"family": "axis", "aggregates": True},
    "Line":              {"family": "axis", "aggregates": True},
    "Area (Stacked)":    {"family": "axis", "aggregates": True},
    "Area (Overlapped)": {"family": "axis", "aggregates": True},
    "Scatter":           {"family": "axis", "aggregates": False},
    "Box Plot":          {"family": "values", "groups": "combined"},
    "Violin":            {"family": "values", "groups": "combined"},
    "Histogram":         {"family": "values", "groups": "curves"},
    "Density(KDE)":      {"family": "values", "groups": "curves"},
    "Heatmap":           {"family": "values", "groups": None},
    "Sankey":            {"family": "flow"},
    "Sankey Chord":      {"family": "flow"},
}


class PlanError(Exception):
    """Seleção inválida (ou gráfico ilegível): `key` é a chave da mensagem (i18n) e `params` os valores dela."""
    def __init__(self, key: str, **params):
        super().__init__(key)
        self.key, self.params = key, params


class RolePlan:
    """Resultado de resolve_roles: o que cada coluna selecionada faz neste gráfico."""
    def __init__(self, chart, kind, axis=None, axis_numeric=False, groups=(), values=(), stages=(), weight=None,
                 z=None, auto_group=None, notices=(), summary=()):
        self.chart, self.kind = chart, kind
        self.axis, self.axis_numeric = axis, axis_numeric
        self.groups, self.values, self.stages = list(groups), list(values), list(stages)
        self.weight, self.z, self.auto_group = weight, z, auto_group
        self.notices = list(notices)          # [(chave, parâmetros)]: papéis ignorados (a interface avisa)
        self.summary = list(summary)          # [(papel, texto)]: leitura da seleção, para mostrar ao usuário

    def __repr__(self):
        return (f"RolePlan({self.chart!r}, {self.kind!r}, axis={self.axis!r}, groups={self.groups}, "
                f"values={self.values}, stages={self.stages}, weight={self.weight!r}, notices={self.notices})")


def _names(cols):
    return ", ".join(str(c) for c in cols)


def resolve_roles(chart: str, x_cols, y_cols, z_cols, is_numeric, dim3: bool = False, auto_group=None) -> RolePlan:
    """Decide o papel de cada coluna selecionada (ver o bloco de comentários acima). `x_cols`, `y_cols` e `z_cols`
    estão na ORDEM em que o usuário as selecionou; `is_numeric(col)` classifica a coluna; `auto_group` é o nome de
    uma coluna Class/Group do arquivo (colore o Scatter sem categorias em X). Levanta PlanError se a seleção não
    forma um gráfico."""
    x_cols, y_cols, z_cols = list(x_cols), list(y_cols), list(z_cols)
    num_x = [c for c in x_cols if is_numeric(c)]
    cat_x = [c for c in x_cols if not is_numeric(c)]
    bad = [c for c in y_cols + (z_cols if dim3 else []) if not is_numeric(c)]
    if bad:
        raise PlanError("rl_err_y_numeric", cols=_names(bad))
    if not (x_cols or y_cols):
        raise PlanError("rl_err_nothing")

    if dim3:
        if len(num_x) != 1 or len(y_cols) != 1 or len(z_cols) != 1:
            raise PlanError("rl_err_3d_select")
        auto = None if cat_x else auto_group
        summ = [("axis", num_x[0]), ("y", y_cols[0]), ("z", z_cols[0])]
        if cat_x:
            summ.append(("colors", _names(cat_x)))
        elif auto:
            summ.append(("colors_auto", auto))
        return RolePlan("Scatter", "scatter3d", axis=num_x[0], axis_numeric=True, groups=cat_x, values=y_cols,
                        z=z_cols[0], auto_group=auto, summary=summ)

    family = CHART_ROLES[chart]["family"]

    # ---- fluxo: Sankey / Sankey Chord -----------------------------------------------------------------
    if family == "flow":
        if len(x_cols) < 2:
            raise PlanError("rl_err_flow_two_x", chart=chart)
        if len(y_cols) > 1:
            raise PlanError("rl_err_flow_one_y", chart=chart)
        summ = [("stages", " → ".join(x_cols))]
        if y_cols:
            summ.append(("weight", y_cols[0]))
        return RolePlan(chart, "flow", stages=x_cols, weight=y_cols[0] if y_cols else None, summary=summ)

    # ---- valores: Box Plot, Violin, Histogram, Density, Heatmap ---------------------------------------
    if family == "values":
        notices = []
        values = list(y_cols) if y_cols else list(num_x)      # sem Y, as colunas numéricas de X são os valores
        if not values:
            raise PlanError("rl_err_need_numeric", chart=chart)
        if y_cols and num_x:
            notices.append(("rl_note_numx_ignored", {"chart": chart, "cols": _names(num_x)}))
        groups = cat_x if CHART_ROLES[chart]["groups"] else []
        if cat_x and not groups:
            notices.append(("rl_note_catx_ignored", {"chart": chart, "cols": _names(cat_x)}))
        summ = [("values", _names(values))]
        if groups:
            summ.append(("groups", _names(groups)))
        return RolePlan(chart, "values", groups=groups, values=values, notices=notices, summary=summ)

    # ---- eixo: Bar, Line, Scatter, Area ---------------------------------------------------------------
    stat_part = [("stat", "")]
    if len(num_x) > 1:
        raise PlanError("rl_err_one_numeric_x", chart=chart, cols=_names(num_x))
    if not y_cols:                                            # Y vazio: contagem das categorias
        if num_x:
            raise PlanError("rl_err_count_numeric_x", chart=chart, cols=_names(num_x))
        return RolePlan(chart, "count", axis=cat_x[0], values=cat_x, summary=[("count", _names(cat_x))])
    if not x_cols:                                            # Y sem X: falta o eixo (ou as categorias)
        raise PlanError("rl_err_need_x", chart=chart)
    if num_x:                                                 # eixo numérico (+ categorias = cores)
        axis, groups = num_x[0], cat_x
        kind = "axis_grouped" if groups else "axis_xy"
        auto = auto_group if (not groups and chart == "Scatter" and len(y_cols) == 1) else None
        # só o Bar agrega valores repetidos de X (Statistic); Line, Area e Scatter desenham os valores como estão
        summ = [("axis", axis), ("values", _names(y_cols))] + (stat_part if chart == "Bar" else [])
        if groups:
            summ.append(("colors", _names(groups)))
        elif auto:
            summ.append(("colors_auto", auto))
        return RolePlan(chart, kind, axis=axis, axis_numeric=True, groups=groups, values=y_cols, auto_group=auto,
                        summary=summ)
    axis, groups = cat_x[0], cat_x[1:]                        # eixo categórico (+ outras categorias = cores)
    # eixo categórico: Bar, Line e Area agregam por categoria (Statistic); o Scatter mostra todos os pontos
    summ = [("axis", axis), ("values", _names(y_cols))] + (stat_part if CHART_ROLES[chart]["aggregates"] else [])
    if groups:
        summ.append(("colors", _names(groups)))
    return RolePlan(chart, "axis_category", axis=axis, axis_numeric=False, groups=groups, values=y_cols,
                    summary=summ)


# ----------------------------------------------------------------------------------------------------------
# Montagem dos dados e desenho
# ----------------------------------------------------------------------------------------------------------
def _guard(chart, n_rows, n_series=1, label_mark=False, top_n=0, kind=None):
    """Levanta PlanError("plot_msg_too_many_marks") se o gráfico teria marcações demais (ver excessive_marks)."""
    over = excessive_marks("Series" if kind == "series" else chart, n_rows, n_series, label_mark, top_n)
    if over is None:
        return
    what, n, limit = over
    raise PlanError("plot_msg_too_many_marks", chart=chart, n=int(n), max=int(limit),
                    what=f"plot_marks_what_{what}", tip=f"plot_marks_tip_{what}")


def build_series(df: pd.DataFrame, x_col, y_cols):
    """Séries [(rótulo, x, y)] de X numérico contra cada Y (sem categorias); linhas com X ou Y ausentes saem."""
    xv = _series_to_numeric(df[x_col])
    out = []
    for yc in y_cols:
        yv = _series_to_numeric(df[yc])
        m = xv.notna() & yv.notna()
        if m.any():
            out.append((str(yc), xv[m].to_numpy(dtype=float), yv[m].to_numpy(dtype=float)))
    return out


def build_category_series(df: pd.DataFrame, axis_col, y_cols, group_cols):
    """Como build_grouped_series, mas com um eixo X CATEGÓRICO: devolve (séries, categorias), onde o x de cada série
    é a posição (0, 1, 2...) da categoria do eixo na ordem de aparição. Rótulo "Y | grupo" com várias colunas Y."""
    cats = [c for c in pd.unique(df[axis_col].dropna().astype(str))]
    pos = {c: i for i, c in enumerate(cats)}
    xv = df[axis_col].astype(str).where(df[axis_col].notna()).map(pos)
    g = group_labels(df, group_cols)
    out = []
    for yc in y_cols:
        yv = _series_to_numeric(df[yc])
        for grp in pd.unique(g.dropna()):
            m = (g == grp) & xv.notna() & yv.notna()
            if m.any():
                out.append((grp if len(y_cols) == 1 else f"{yc} | {grp}", xv[m].to_numpy(dtype=float),
                            yv[m].to_numpy(dtype=float)))
    return out, cats


def _value_xlabel(chart, plan, tr):
    """Rótulo padrão do eixo X dos gráficos de valores: Histogram/Density mostram os valores nesse eixo."""
    if chart in ("Histogram", "Density(KDE)"):
        return plan.values[0] if len(plan.values) == 1 else tr("rl_default_values")
    return ""


def _value_ylabel(chart, plan, tr, opts):
    """Rótulo padrão do eixo Y: Box/Violin mostram os valores; Histogram, a frequência (ou densidade); Density, a densidade."""
    if chart in DISTRIBUTION_CHARTS:
        return plan.values[0] if len(plan.values) == 1 else tr("rl_default_values")
    if chart == "Histogram":
        return tr("rl_default_density") if opts.get("hist_density") else tr("plot_default_ylabel_frequency")
    if chart == "Density(KDE)":
        return tr("rl_default_density_peak") if opts.get("kde_peak") else tr("rl_default_density")
    return ""


def aggregate_series(series, stat, with_spread=False):
    """Cada série [(rótulo, x, y)] com os y de um mesmo x resumidos pela estatística (Single Value, Mean ± SD, Median ±
    IQR, Mode). Com `with_spread`, devolve também, por série, (inferior, superior) com a dispersão de cada ponto
    (arrays alinhados aos x devolvidos; (None, None) para Mode e Single Value)."""
    slug = bar_stat_slug(stat)
    out, spreads = [], []
    for lab, x, y in series:
        g = pd.Series(y).groupby(x)
        center = (g.first() if slug == "single" else g.median() if slug == "median"
                  else g.agg(_group_mode) if slug == "mode" else g.mean())
        out.append((lab, center.index.to_numpy(dtype=float), center.to_numpy(dtype=float)))
        if with_spread:
            lo, hi = _group_spread(g, stat)
            spreads.append((None, None) if lo is None else (lo.to_numpy(dtype=float), hi.to_numpy(dtype=float)))
    return (out, spreads) if with_spread else out


def _stat_default_ylabel(tr, stat, y_cols, chart=""):
    """Rótulo padrão do eixo Y da Statistic; o Bar e o Line, que desenham a dispersão, dizem "Mean ± SD" / "Median ± IQR"."""
    slug = bar_stat_slug(stat)
    if chart in ("Bar", "Line") and slug in ("mean", "median"):
        slug += "_sd" if slug == "mean" else "_iqr"
    return tr(f"plot_ylabel_stat_{slug}") + (tr("plot_ylabel_stat_of", y=y_cols[0]) if len(y_cols) == 1 else "")


def _single_value_error(rep, cats=None):
    """Mensagem do "Single Value" com valores repetidos: `rep` = [(série, x, nº)]; com eixo categórico (`cats`),
    o x é a posição da categoria e a mensagem traz o nome dela."""
    def x_txt(v):
        if cats is not None:
            return str(cats[int(v)])
        return f"X={v:g}" if isinstance(v, (int, float, np.floating)) else f"X={v}"
    raise PlanError("plot_msg_single_value_repeated",
                    repeated=", ".join(f"{lab}: {x_txt(v)} ({k})" for lab, v, k in rep[:10]) + (" ..." if len(rep) > 10 else ""))


def suggest_bar_stat(plan, df: pd.DataFrame):
    """Estatística padrão para a seleção `plan` (RolePlan) dos dados `df`: "Single Value" quando cada categoria (ou cada
    valor de X) ocorre uma única vez, "Mean ± SD" quando alguma se repete. None quando a seleção não usa Statistic
    (só Bar, e Line/Area com X categórico, resumem valores repetidos)."""
    chart, kind = plan.chart, plan.kind
    if chart == "Bar":
        if kind not in ("axis_xy", "axis_grouped", "axis_category"):
            return None
    elif chart in ("Line", "Area (Stacked)", "Area (Overlapped)"):
        if kind != "axis_category":
            return None
    else:
        return None
    y_cols = list(plan.values)
    if kind == "axis_xy":
        rep = repeated_x_values(build_series(df, plan.axis, y_cols))
    elif plan.groups:
        series = (build_grouped_series(df, plan.axis, y_cols, plan.groups) if kind == "axis_grouped"
                  else build_category_series(df, plan.axis, y_cols, plan.groups)[0])
        rep = repeated_x_values(series)
    else:
        ydf = pd.DataFrame({safe_series_name(c, "(Y)"): df[c] for c in y_cols})
        rep = repeated_categories(df[plan.axis].to_numpy(dtype=object), ydf)
    return STAT_MEAN if rep else STAT_SINGLE


def execute_plan(plan: RolePlan, df: pd.DataFrame, options: dict, style: dict, tr=None):
    """Monta os dados do `plan` a partir de `df` e devolve a Figure.
    `options`: valores das opções do tipo de gráfico (inclui "samples" e "legend_loc"). `style`: dpi, trend_mode (já
    efetivo), show_legend, label_mark, title, xlabel, ylabel, zlabel, color_mode, palette_name, single_color.
    `tr(chave, **kw)` traduz os rótulos padrão dos eixos (sem ela, devolve a própria chave). Levanta PlanError."""
    tr = tr or (lambda key, **kw: key)
    opts = dict(options or {})
    df = sample_rows(df, opts.pop("samples", 0)).copy()
    chart, kind = plan.chart, plan.kind
    dpi = style.get("dpi", 300)
    st = dict(trend_mode=style.get("trend_mode", "None"), show_legend=style.get("show_legend", False),
              label_mark=style.get("label_mark", False), color_mode=style.get("color_mode", COLOR_MODE_PALETTE),
              palette_name=style.get("palette_name", "Dark2"), single_color=style.get("single_color") or "#1f77b4")
    if chart not in TREND_ALLOWED:
        st["trend_mode"] = "None"
    title, xlabel, ylabel = (style.get("title") or ""), (style.get("xlabel") or ""), (style.get("ylabel") or "")
    label_mark, top_n, stat = st["label_mark"], int(opts.get("bar_top", 0) or 0), opts.get("bar_stat", "Mean")

    def plotter(df_, x_default="", y_default="", **extra):
        return PLOTTERS[chart](df=df_, dpi=dpi, title=title, xlabel=xlabel or x_default, ylabel=ylabel or y_default,
                               options=opts, **st, **extra)

    # ---- 3D --------------------------------------------------------------------------------------------
    if kind == "scatter3d":
        group_col = plan.auto_group
        color_mode = st["color_mode"]
        if plan.groups:
            df["__group__"] = group_labels(df, plan.groups)
            df = df[df["__group__"].notna()]
            if df.empty:
                raise PlanError("rl_err_no_values")
            group_col = "__group__"
            _guard("Scatter", df["__group__"].nunique(), kind="series")
            color_mode = COLOR_MODE_PALETTE                    # a cor é o que distingue as categorias
        _guard("Scatter", len(df), 1, label_mark)
        x, y, z = plan.axis, plan.values[0], plan.z
        return plot_scatter_3D(
            df=df, x_col=x, y_col=y, z_col=z, group_col=group_col,
            title=title or f"3D Scatter: {x} vs {y} vs {z}", xlabel=xlabel or x, ylabel=ylabel or y,
            zlabel=(style.get("zlabel") or "") or z, palette_name=st["palette_name"], single_color=st["single_color"],
            color_mode=color_mode, label_mark=label_mark, show_legend=st["show_legend"], options=opts)

    # ---- fluxo -----------------------------------------------------------------------------------------
    if kind == "flow":
        mapped = df[plan.stages].copy()
        if plan.weight:
            mapped["__weight__"] = df[plan.weight].values
        is_chord = chart == "Sankey Chord"
        return (plot_chord if is_chord else plot_sankey)(
            df=mapped, dpi=dpi, show_legend=st["show_legend"], label_mark=label_mark, title=title, xlabel=xlabel,
            ylabel=ylabel, color_mode=st["color_mode"], palette_name=st["palette_name"],
            single_color=st["single_color"], stage_cols=list(plan.stages),
            weight_col="__weight__" if plan.weight else None,
            max_nodes=(opts.get("chord_top", CHORD_MAX_NODES) if is_chord else opts.get("sankey_top", SANKEY_MAX_NODES_PER_STAGE)),
            options=opts)

    # ---- valores: Box Plot, Violin, Histogram, Density, Heatmap ---------------------------------------
    if kind == "values":
        vals = [safe_series_name(c, "(Y)") for c in plan.values]
        if plan.groups and CHART_ROLES[chart]["groups"] == "combined":          # Box Plot / Violin
            labels = group_labels(df, plan.groups)
            n_groups = labels.nunique()
            if n_groups > DISTRIBUTION_MAX_GROUPS:
                raise PlanError("rl_err_too_many_groups", chart=chart, col=_names(plan.groups), n=int(n_groups),
                                max=DISTRIBUTION_MAX_GROUPS)
            _guard(chart, n_groups, len(vals))
            mapped = pd.DataFrame({"X": labels.astype(object)})
            for c, v in zip(plan.values, vals):
                mapped[v] = df[c]
            mapped = mapped[mapped["X"].notna()]
            return plotter(mapped, x_default=_names(plan.groups), y_default=_value_ylabel(chart, plan, tr, opts))
        if plan.groups:                                                          # Histogram / Density: uma curva por categoria
            wide = grouped_values_frame(df, plan.values, plan.groups)
            _guard(chart, wide.shape[1], 1, kind="series")
            return plotter(wide, x_default=_value_xlabel(chart, plan, tr), y_default=_value_ylabel(chart, plan, tr, opts))
        mapped = pd.DataFrame({v: df[c] for c, v in zip(plan.values, vals)})
        if chart == "Heatmap":
            _guard(chart, len(mapped), len(vals))
        elif chart in DISTRIBUTION_CHARTS:
            _guard(chart, 1, len(vals))
        return plotter(mapped, x_default=_value_xlabel(chart, plan, tr), y_default=_value_ylabel(chart, plan, tr, opts))

    # ---- eixo: contagem --------------------------------------------------------------------------------
    if kind == "count":
        cols = plan.values
        cats, seen = [], set()
        for c in cols:
            for v in pd.unique(df[c].dropna().astype(str)):
                if v not in seen:
                    seen.add(v)
                    cats.append(v)
        if not cats:
            raise PlanError("rl_err_no_values")
        mapped = pd.DataFrame({"X": cats})
        for c in cols:
            freq = df[c].dropna().astype(str).value_counts()
            mapped[safe_series_name(c)] = pd.Series(freq).reindex(cats).fillna(0).astype(int).to_numpy()
        _guard(chart, len(mapped), len(cols), label_mark, top_n)
        return plotter(mapped, x_default=(cols[0] if len(cols) == 1 else tr("rl_default_category")),
                       y_default=tr("plot_default_ylabel_frequency"))

    y_cols = plan.values
    y_name = y_cols[0] if len(y_cols) == 1 else tr("rl_default_values")
    stat_label = _stat_default_ylabel(tr, stat, y_cols, chart)

    # ---- eixo numérico, sem categorias -----------------------------------------------------------------
    if kind == "axis_xy":
        if chart == "Bar":                                    # uma barra por valor distinto de X (Statistic)
            series = build_series(df, plan.axis, y_cols)
            if not series:
                raise PlanError("rl_err_no_values")
            n_x = len(np.unique(np.concatenate([x for _, x, _ in series])))
            _guard("Bar", n_x, len(series), label_mark, top_n)
            if is_single_value(stat):
                rep = repeated_x_values(series)
                if rep:
                    _single_value_error(rep)
            return plot_grouped_xy("Bar", series, dpi=dpi, trend_mode=st["trend_mode"], show_legend=st["show_legend"],
                                   title=title or f"Bar: {plan.axis} vs {_names(y_cols)}", xlabel=xlabel or plan.axis,
                                   ylabel=ylabel or stat_label, label_mark=label_mark, palette_name=st["palette_name"],
                                   single_color=st["single_color"], options=opts, color_mode=st["color_mode"])
        _guard(chart, len(df), len(y_cols), label_mark)
        if chart == "Scatter" and plan.auto_group:            # Class/Group do arquivo colore o Scatter (único Y)
            return plot_scatter_2D(
                df=df, x_col=plan.axis, y_col=y_cols[0], group_col=plan.auto_group, title=title or "Scatter Plot",
                xlabel=xlabel or plan.axis, ylabel=ylabel or y_cols[0], palette_name=st["palette_name"],
                single_color=st["single_color"], color_mode=st["color_mode"], label_mark=label_mark,
                trend_mode=st["trend_mode"], show_legend=st["show_legend"], options=opts)
        mapped = pd.DataFrame({"X": _series_to_numeric(df[plan.axis])})
        for c in y_cols:
            mapped[safe_series_name(c, "(Y)")] = df[c]
        return plotter(mapped, x_default=plan.axis, y_default=y_name)

    # ---- eixo numérico + categorias (cores) ------------------------------------------------------------
    if kind in ("axis_grouped", "axis_category") and plan.groups:
        spread = None
        if kind == "axis_grouped":
            series, cats = build_grouped_series(df, plan.axis, y_cols, plan.groups), None
            x_default = plan.axis
        else:
            series, cats = build_category_series(df, plan.axis, y_cols, plan.groups)
            x_default = plan.axis
        if not series:
            raise PlanError("rl_err_no_values")
        _guard(chart, len(series), 1, kind="series")
        if chart == "Bar":
            n_x = len(cats) if cats is not None else len(np.unique(np.concatenate([x for _, x, _ in series])))
            _guard("Bar", n_x, len(series), label_mark)
            if is_single_value(stat):
                rep = repeated_x_values(series)
                if rep:
                    _single_value_error(rep, cats)
        else:
            if kind == "axis_category" and chart != "Scatter":      # categorias repetidas: Line/Area mostram a Statistic
                if is_single_value(stat):
                    rep = repeated_x_values(series)
                    if rep:
                        _single_value_error(rep, cats)
                if chart == "Line":                                  # o Line desenha também a dispersão (barra de erro)
                    series, spread = aggregate_series(series, stat, with_spread=True)
                else:
                    series = aggregate_series(series, stat)
            _guard(chart, max(len(x) for _, x, _ in series), len(series), label_mark)
        aggregated = chart == "Bar" or (kind == "axis_category" and chart != "Scatter")
        return plot_grouped_xy(
            chart, series, dpi=dpi, trend_mode=st["trend_mode"], show_legend=st["show_legend"],
            title=title or f"{chart}: {plan.axis} vs {_names(y_cols)} ({_names(plan.groups)})",
            xlabel=xlabel or x_default, ylabel=ylabel or (stat_label if aggregated else y_name),
            label_mark=label_mark, palette_name=st["palette_name"], single_color=st["single_color"], options=opts,
            x_labels=cats, color_mode=st["color_mode"], spread=spread,
            spread_kind="iqr" if bar_stat_slug(stat) == "median" else "sd")

    # ---- eixo categórico, sem cores extras -------------------------------------------------------------
    if chart == "Scatter":                                    # todos os pontos, coloridos pela categoria
        mapped = pd.DataFrame({"X": df[plan.axis].astype(str)})
        for c in y_cols:
            mapped[safe_series_name(c, "(Y)")] = df[c]
        _guard(chart, len(mapped), len(y_cols), label_mark)
        return plotter(mapped, x_default=plan.axis, y_default=y_name)
    single = is_single_value(stat)
    suffix = "(value)" if single else f"({bar_stat_slug(stat)})"
    ydf = pd.DataFrame({safe_series_name(c, suffix): df[c] for c in y_cols})
    xv = df[plan.axis].to_numpy(dtype=object)
    if single:
        rep = repeated_categories(xv, ydf)
        if rep:
            raise PlanError("plot_msg_single_value_repeated",
                            repeated=", ".join(f"{c} ({k})" for c, k in rep[:10]) + (" ..." if len(rep) > 10 else ""))
    summary, lo, hi = summarize_with_spread(xv, ydf, stat)
    if summary.empty:
        raise PlanError("rl_err_no_values")
    if chart == "Bar":
        _guard("Bar", len(summary), len(y_cols), label_mark, top_n)
        return plot_bar(df=summary, dpi=dpi, title=title, xlabel=xlabel or plan.axis, ylabel=ylabel or stat_label,
                        options=opts, yerr=None if lo is None else (lo, hi),
                        err_kind="iqr" if bar_stat_slug(stat) == "median" else "sd", **st)
    _guard(chart, len(summary), len(y_cols), label_mark)
    if chart == "Line" and lo is not None:                    # Line: barra de erro em cada ponto (como no Bar)
        return plotter(summary, x_default=plan.axis, y_default=stat_label, yerr=(lo, hi),
                       err_kind="iqr" if bar_stat_slug(stat) == "median" else "sd")
    return plotter(summary, x_default=plan.axis, y_default=stat_label)

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


"""
recommended_scaling.py
Módulo utilitário para aplicar diferentes técnicas de scaling/transformação
sobre um intervalo de colunas de um DataFrame.

Compatível com o ecossistema já usado no CODRUG (pandas, numpy, scikit-learn).
"""

from typing import List, Tuple
import numpy as np
import pandas as pd

from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler, Normalizer,
    PowerTransformer, QuantileTransformer, OneHotEncoder, OrdinalEncoder
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.neural_network import MLPRegressor
from scipy.stats import norm, rankdata

# --- Inferir tipo de categórica (baixa vs alta cardinalidade) ---
def _infer_categorical_kind(s: pd.Series, low_card_max: int = 10, low_card_ratio: float = 0.05) -> str:
    """
    Returns 'categorical_low' (baixa cardinalidade) ou 'categorical_high'.
    Heurística: baixa se nunique <= max(low_card_max, low_card_ratio * n_validos).
    """
    x = s.astype(object)
    n = x.notna().sum()
    if n == 0:
        return "categorical_low"
    k = pd.Series(x).nunique(dropna=True)
    thresh = max(low_card_max, int(np.ceil(low_card_ratio * n)))
    return "categorical_low" if k <= thresh else "categorical_high"


def _apply_hybrid_categorical(df: pd.DataFrame, cat_cols: list,
                              low_card_max: int = 10, low_card_ratio: float = 0.05):
    """
    Aplica encoder automático por coluna:
      - 'categorical_low'  -> OneHotEncoder(handle_unknown='ignore', dense)
      - 'categorical_high' -> BinaryEncoder (implementação leve deste módulo)
    Retorna: (df_out, kinds_map, choices_map)
      kinds_map[c]   = 'categorical_low' | 'categorical_high'
      choices_map[c] = 'onehot' | 'binary'
    """
    out = df.copy()
    kinds_map = {}
    choices_map = {}

    for c in cat_cols:
        s = out[c]
        kind = _infer_categorical_kind(s, low_card_max, low_card_ratio)
        kinds_map[c] = kind

        # === baixa cardinalidade -> OneHot ===
        if kind == "categorical_low":
            enc = OneHotEncoder(handle_unknown="ignore", sparse=False, dtype=float)
            Z = enc.fit_transform(s.fillna("missing").astype(str).to_numpy().reshape(-1, 1))
            new_cols = [f"{c}={cat}" for cat in enc.categories_[0]]
            new_df = pd.DataFrame(Z, index=out.index, columns=new_cols)
            choices_map[c] = "onehot"

        # === alta cardinalidade -> BinaryEncoder ===
        else:
            # mapeia categorias -> inteiros
            cats = pd.Categorical(s.fillna("missing").astype(str)).categories
            int_map = {cat: i for i, cat in enumerate(cats)}
            vals = s.fillna("missing").astype(str).map(int_map).astype(int).values
            max_val = int(vals.max()) if vals.size else 0
            width = max(1, int(np.ceil(np.log2(max_val + 1))))
            cols = [f"{c}__bin{b}" for b in range(width)]
            bits = np.vstack([((vals >> b) & 1).astype(float) for b in range(width)]).T
            new_df = pd.DataFrame(bits, index=out.index, columns={*cols})  # remove dups se width=1
            new_df = new_df.loc[:, sorted(new_df.columns)]
            choices_map[c] = "binary"

        # === substituir in-place preservando ordem ===
        idx = out.columns.get_loc(c)
        left = out.iloc[:, :idx]
        right = out.iloc[:, idx+1:]
        out = pd.concat([left, new_df, right], axis=1)

    return out, kinds_map, choices_map


# ------------------------ heurísticas para numéricas ------------------------ #
def _infer_numeric_kind(s: pd.Series) -> str:
    """
    Classifica a série numérica em:
      - 'binary'    : {0,1} ou {-1,1} (ignorando NaNs)
      - 'count'     : inteiros não-negativos e não-binários
      - 'continuous': o restante
    """
    v = pd.to_numeric(s, errors="coerce").dropna()
    if v.empty:
        return "continuous"
    u = pd.unique(v)
    # binário clássico
    if set(np.sort(pd.unique(v))).issubset({0, 1}) or set(np.sort(pd.unique(v))).issubset({-1, 1}):
        return "binary"
    # inteiros não-negativos?
    if np.all(np.isfinite(v)) and np.all(np.floor(v) == v) and (v.min() >= 0):
        return "count"
    return "continuous"


def _skew_safe(x: np.ndarray) -> float:
    x = pd.Series(x).dropna()
    if len(x) < 3:
        return 0.0
    return float(x.skew())


def _has_outliers_iqr(x: np.ndarray, k: float = 1.5, frac_thresh: float = 0.05) -> bool:
    """Marca outliers por IQR e retorna True se fração > frac_thresh."""
    x = pd.Series(x).dropna()
    if x.empty:
        return False
    q1, q3 = x.quantile(0.25), x.quantile(0.75)
    iqr = q3 - q1
    if iqr <= 0:
        return False
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    frac = ((x < lower) | (x > upper)).mean()
    return frac > frac_thresh


def _apply_hybrid_numeric(df: pd.DataFrame, num_cols: list) -> pd.DataFrame:
    """
    Aplica, coluna a coluna, o melhor 'scaling' para cada tipo:
      - binary    -> mantém como está (neutro; preserva 0/1)
      - count     -> Yeo-Johnson + StandardScaler
      - continuous:
            se muitos outliers -> RobustScaler
            senão -> StandardScaler
    Retorna o DF com substituições in-place.
    """
    out = df.copy()
    for c in num_cols:
        s = pd.to_numeric(out[c], errors="coerce")
        kind = _infer_numeric_kind(s)

        if kind == "binary":
            # neutro: preserva 0/1 exatamente
            continue

        elif kind == "count":
            # Yeo-Johnson lida com zeros/positivos + padroniza
            X = s.to_numpy().reshape(-1, 1)
            tr = Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("pt", PowerTransformer(method="yeo-johnson", standardize=True)),
                ("std", StandardScaler(with_mean=True, with_std=True))
            ])
            z = tr.fit_transform(X).ravel()
            out.loc[:, c] = z

        else:  # continuous
            X = s.to_numpy().reshape(-1, 1)
            if _has_outliers_iqr(s.to_numpy()):
                tr = Pipeline([
                    ("imp", SimpleImputer(strategy="median")),
                    ("rb", RobustScaler())
                ])
            else:
                tr = Pipeline([
                    ("imp", SimpleImputer(strategy="median")),
                    ("std", StandardScaler())
                ])
            z = tr.fit_transform(X).ravel()
            out.loc[:, c] = z

    return out


# ------------------------ utilidades ------------------------ #

def _slice_columns(df: pd.DataFrame, first_col: str, last_col: str) -> List[str]:
    """Retorna a lista de colunas entre first_col e last_col (inclusive), preservando a ordem do DF."""
    cols = list(df.columns.astype(str))
    if first_col not in cols or last_col not in cols:
        raise ValueError("Coluna inicial ou final não encontrada no DataFrame.")
    i0, i1 = cols.index(first_col), cols.index(last_col)
    if i0 > i1:
        i0, i1 = i1, i0
    return cols[i0:i1 + 1]


def _split_num_cat(df: pd.DataFrame, cols: List[str]) -> Tuple[List[str], List[str]]:
    """Divide as colunas em numéricas e categóricas (heurística simples)."""
    num_cols, cat_cols = [], []
    for c in cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            num_cols.append(c)
        else:
            # tenta converter: se >80% virarem número, trata como numérica
            ser = pd.to_numeric(df[c], errors="coerce")
            frac = ser.notna().mean()
            if frac >= 0.8:
                num_cols.append(c)
            else:
                cat_cols.append(c)
    return num_cols, cat_cols


def _rank_gaussian_transform(x: np.ndarray) -> np.ndarray:
    """
    Rank-based Normalization (RankGauss / Normal Scores).
    Aplica rankdata e depois mapeia via quantil da normal padrão.
    """
    # lida com NaNs preservando máscara
    mask = ~np.isnan(x)
    ranks = np.zeros_like(x, dtype=float)
    # Blom: (r - 3/8) / (n + 1/4)
    r = rankdata(x[mask], method="average")
    n = np.sum(mask)
    p = (r - 3.0/8.0) / (n + 1.0/4.0)
    ranks_vals = norm.ppf(np.clip(p, 1e-9, 1 - 1e-9))
    ranks[mask] = ranks_vals
    ranks[~mask] = np.nan
    return ranks


def _safe_log_transform(X: np.ndarray) -> np.ndarray:
    """
    Log transform seguro:
      - se todos X >= 0: usa log1p(X)
      - caso contrário: desloca por -(min) + pequeno epsilon e aplica log1p
    """
    X = X.astype(float)
    minv = np.nanmin(X)
    if minv < 0:
        X = X - minv + 1e-9
    return np.log1p(X)


# ------------------------ transformadores principais ------------------------ #

def transform_numeric_block(X: np.ndarray, method_name: str) -> np.ndarray:
    """
    Aplica o método escolhido em um bloco N x D (apenas numérico).
    Retorna um array N x D (ou N x D' em casos que expandem dimensão).
    """
    method_name = (method_name or "").strip()

    if method_name == "StandardScaler":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler())
        ])
        return tr.fit_transform(X)

    if method_name == "MinMaxScaler":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", MinMaxScaler())
        ])
        return tr.fit_transform(X)

    if method_name == "MaxAbsScaler":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", MaxAbsScaler())
        ])
        return tr.fit_transform(X)

    if method_name == "RobustScaler":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", RobustScaler())
        ])
        return tr.fit_transform(X)

    if method_name.startswith("Normalizer"):
        # "Normalizer(L1/L2 norm)"
        norm_type = "l2"
        low = method_name.lower()
        if "l1" in low:
            norm_type = "l1"
        elif "l2" in low:
            norm_type = "l2"
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("norm", Normalizer(norm=norm_type))
        ])
        return tr.fit_transform(X)

    if method_name == "Q.Transformer(Uniform)":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("qt", QuantileTransformer(n_quantiles=min(1000, max(10, X.shape[0] // 2)),
                                       output_distribution="uniform",
                                       copy=True, subsample=int(1e9), random_state=42))
        ])
        return tr.fit_transform(X)

    if method_name == "Q.Transformer(Norm)":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("qt", QuantileTransformer(n_quantiles=min(1000, max(10, X.shape[0] // 2)),
                                       output_distribution="normal",
                                       copy=True, subsample=int(1e9), random_state=42))
        ])
        return tr.fit_transform(X)

    if method_name == "PowerTransformer(Yeo-Johnson)":
        tr = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("pt", PowerTransformer(method="yeo-johnson", standardize=True))
        ])
        return tr.fit_transform(X)

    if method_name == "PowerTransformer(Box-Cox)":
        # Box-Cox exige X > 0
        X_imp = SimpleImputer(strategy="median").fit_transform(X)
        if np.nanmin(X_imp) <= 0:
            # deslocamento mínimo positivo
            shift = -np.nanmin(X_imp) + 1e-9
            X_imp = X_imp + shift
        tr = PowerTransformer(method="box-cox", standardize=True)
        return tr.fit_transform(X_imp)

    if method_name == "Log Transformation":
        X_imp = SimpleImputer(strategy="median").fit_transform(X)
        return _safe_log_transform(X_imp)

    if method_name == "Rank-based Norm":
        X_imp = SimpleImputer(strategy="median").fit_transform(X)
        out = np.zeros_like(X_imp, dtype=float)
        for j in range(X_imp.shape[1]):
            out[:, j] = _rank_gaussian_transform(X_imp[:, j])
        return out

    if method_name == "AutoEncoder":
        # AE simples (reconstrução) com MLPRegressor (sem dependências de TF)
        # 1) imputar e padronizar
        imp = SimpleImputer(strategy="median")
        sc = StandardScaler()
        X0 = imp.fit_transform(X)
        Xs = sc.fit_transform(X0)

        # 2) encoder+decoder aproximado via regressão ao próprio Xs
        #    Dimensão do "gargalo" proporcional a sqrt(D)
        D = Xs.shape[1]
        bottleneck = max(2, int(np.ceil(np.sqrt(D))))
        # Arquitetura simétrica pequena
        hidden = (max(bottleneck * 2, 8), bottleneck, max(bottleneck * 2, 8))
        ae = MLPRegressor(hidden_layer_sizes=hidden, activation="tanh",
                          solver="adam", learning_rate_init=0.01,
                          max_iter=500, random_state=42, tol=1e-4)
        ae.fit(Xs, Xs)
        Xrec = ae.predict(Xs)
        # Mantemos na escala padronizada (é um "scaling" não-linear)
        return Xrec

    # Se chegou aqui, método desconhecido
    raise ValueError(f"Método numérico não suportado: {method_name}")


def transform_categorical_block(df: pd.DataFrame, cols: List[str], method_name: str) -> pd.DataFrame:
    """
    Aplica codificação categórica nas colunas indicadas e retorna um novo DF
    apenas com as colunas transformadas (nomes expandidos se necessário).
    """
    Xcat = df[cols].astype("category").astype(object).fillna("missing")

    if method_name.startswith("OneHotEncoder"):
        enc = OneHotEncoder(handle_unknown="ignore", sparse=False, dtype=float)
        Z = enc.fit_transform(Xcat)
        new_cols = enc.get_feature_names_out(cols)
        return pd.DataFrame(Z, index=df.index, columns=new_cols)

    if method_name.startswith("OrdinalEncoder"):
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1)
        Z = enc.fit_transform(Xcat)
        new_cols = [f"{c}__ord" for c in cols]
        return pd.DataFrame(Z, index=df.index, columns=new_cols)

    if method_name == "BinaryEncoder":
        # Implementação leve sem depender de category_encoders:
        # 1) mapeia categorias -> inteiro
        int_maps = {}
        for c in cols:
            cats = pd.Categorical(Xcat[c]).categories
            int_maps[c] = {cat: i for i, cat in enumerate(cats)}
        Xint = pd.DataFrame({c: Xcat[c].map(int_maps[c]).astype(int) for c in cols}, index=df.index)

        # 2) converte inteiros para binário em largura mínima
        out_parts = []
        for c in cols:
            max_val = int(Xint[c].max()) if not Xint[c].isna().all() else 0
            width = max(1, int(np.ceil(np.log2(max_val + 1))))  # bits necessários
            bits = []
            vals = Xint[c].fillna(0).astype(int).values
            for b in range(width):
                bits.append(((vals >> b) & 1).astype(float))
            cat_bin = pd.DataFrame(np.vstack(bits).T, index=df.index,
                                   columns=[f"{c}__bin{b}" for b in range(width)])
            out_parts.append(cat_bin)
        return pd.concat(out_parts, axis=1)

    raise ValueError(f"Método categórico não suportado: {method_name}")


# ------------------------ API principal ------------------------ #

def apply_recommended_scaling(
    df_in: pd.DataFrame,
    method_name: str,
    first_feature_col: str,
    last_feature_col: str
) -> pd.DataFrame:
    """
    Aplica o método especificado no intervalo de colunas (inclusive) e retorna
    um NOVO DataFrame com as colunas transformadas substituindo as originais.
    """
    if df_in is None or df_in.empty:
        raise ValueError("DataFrame de entrada está vazio.")

    cols_range = _slice_columns(df_in, first_feature_col, last_feature_col)
    num_cols, cat_cols = _split_num_cat(df_in, cols_range)

    df = df_in.copy()
    
    # --- HÍBRIDO: ativa se usuário escolheu 'hibrid',
    #     se houver mistura entre tipos numéricos, OU se houver categóricas no intervalo.
    numeric_kinds = []
    for c in num_cols:
        numeric_kinds.append(_infer_numeric_kind(pd.to_numeric(df[c], errors="coerce")))
    kinds_set = set(knumeric for knumeric in numeric_kinds if knumeric)

    is_hybrid = (method_name.strip().lower() == "hibrid") or (len(kinds_set) > 1) or (len(cat_cols) > 0)
    if is_hybrid:
        # 1) Numéricas por-coluna: binary -> keep, count -> YJ + zscore, continuous -> Robust/Std
        df_h = _apply_hybrid_numeric(df, num_cols)

        # 2) Categóricas: low -> OneHot, high -> BinaryEncoder
        cat_kinds_map = {}
        cat_choices_map = {}
        if cat_cols:
            df_h, cat_kinds_map, cat_choices_map = _apply_hybrid_categorical(df_h, cat_cols)

        # 3) Atributos p/ janela de detalhes
        try:
            # tipos das numéricas
            num_kinds_map = {c: k for c, k in zip(num_cols, numeric_kinds)}

            # mescla com categóricas
            all_types = {}
            all_types.update(num_kinds_map)
            all_types.update(cat_kinds_map)

            df_h.attrs["scaling_mode"] = "hybrid"
            df_h.attrs["hybrid_types"] = all_types
            # choices dos encoders categóricos (para exibir, se desejar)
            if cat_choices_map:
                df_h.attrs["hybrid_choices"] = cat_choices_map
        except Exception:
            pass

        return df_h


    # -------------- CASOS CATEGÓRICOS -------------- #
    if method_name in ("OneHotEncoder(Cat)", "OrdinalEncoder(Cat)", "BinaryEncoder"):
        if not cat_cols:
            # se o intervalo não tiver colunas categóricas, nada a fazer
            return df
        df_cat_tr = transform_categorical_block(df, cat_cols, method_name.split("(")[0] if "(" in method_name else method_name)
        # remove as cat originais do intervalo e injeta as codificadas no mesmo lugar da primeira cat
        keep = [c for c in df.columns if c not in cat_cols]
        # vamos inserir as novas ao final do bloco (após a última coluna do intervalo)
        insert_pos = df.columns.get_loc(cols_range[-1]) + 1
        left = keep[:insert_pos - len([c for c in cat_cols if c in keep])]
        right = keep[insert_pos - len([c for c in cat_cols if c in keep]):]
        df = df.drop(columns=cat_cols)
        # recompor DataFrame com as novas colunas no “miolo”
        df = pd.concat([df[left], df_cat_tr, df[right]], axis=1)
        return df

    # -------------- CASOS NUMÉRICOS -------------- #
    if not num_cols:
        # se não houver numéricas no intervalo, devolve df intacto
        return df

    X = df[num_cols].to_numpy(dtype=float)

    # Ajuste de rótulo do método para função numérica:
    # (para compatibilidade com nomes do combo)
    name_map = {
        "Normalizer(L1/L2 norm)": "Normalizer(L2)",  # default
        "Q.Transformer(Uniform)": "Q.Transformer(Uniform)",
        "Q.Transformer(Norm)": "Q.Transformer(Norm)",
        "PowerTransformer(Yeo-Johnson)": "PowerTransformer(Yeo-Johnson)",
        "PowerTransformer(Box-Cox)": "PowerTransformer(Box-Cox)",
        "Log Transformation": "Log Transformation",
        "Rank-based Norm": "Rank-based Norm",
        "AutoEncoder": "AutoEncoder",
        "StandardScaler": "StandardScaler",
        "MinMaxScaler": "MinMaxScaler",
        "MaxAbsScaler": "MaxAbsScaler",
        "RobustScaler": "RobustScaler",
    }
    method_key = name_map.get(method_name, method_name)

    Z = transform_numeric_block(X, method_key)
    # se a transformação mudou a largura (ex.: normalizer mantém, mas por segurança):
    if Z.shape[1] != len(num_cols):
        # renomeia novas colunas como base__tr0, base__tr1, ...
        base = num_cols[0] if num_cols else "feat"
        new_cols = [f"{base}__tr{j}" for j in range(Z.shape[1])]
        # dropa as antigas numéricas do intervalo e injeta as novas
        df = df.drop(columns=num_cols)
        insert_pos = df_in.columns.get_loc(num_cols[0])
        left = df.iloc[:, :insert_pos]
        right = df.iloc[:, insert_pos:]
        df_mid = pd.DataFrame(Z, index=df.index, columns=new_cols)
        df = pd.concat([left, df_mid, right], axis=1)
    else:
        # substitui in-place preservando nomes
        df.loc[:, num_cols] = Z

    return df

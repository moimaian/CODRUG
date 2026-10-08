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


from typing import List, Tuple, Optional, Union
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.feature_selection import (
    VarianceThreshold, SelectKBest, f_classif, f_regression,
    mutual_info_classif, mutual_info_regression, chi2, RFE,
    SequentialFeatureSelector
)
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import Lasso, ElasticNet, Ridge
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)

# ========================== UTILITÁRIOS ========================== #

def _slice_columns(df: pd.DataFrame, first_col: str, last_col: str) -> List[str]:
    cols = list(df.columns.astype(str))
    if first_col not in cols or last_col not in cols:
        raise ValueError("Coluna inicial ou final não encontrada.")
    i0, i1 = cols.index(first_col), cols.index(last_col)
    if i0 > i1:
        i0, i1 = i1, i0
    return cols[i0:i1 + 1]

def _to_colname(df: pd.DataFrame, ref: str) -> str:
    cols = list(df.columns.astype(str))
    if ref in cols:
        return ref
    if ref.isdigit():
        idx = int(ref)
        if 0 <= idx < len(cols):
            return cols[idx]
        if 1 <= idx <= len(cols):
            return cols[idx - 1]
    raise ValueError(f"Coluna inválida: {ref}")

def _ensure_numeric(dfX: pd.DataFrame) -> pd.DataFrame:
    dfX = dfX.copy()
    for c in dfX.columns:
        if not pd.api.types.is_numeric_dtype(dfX[c]):
            dfX[c] = pd.to_numeric(dfX[c], errors="coerce")
    return dfX.fillna(0.0)

def _corr_filter(dfX: pd.DataFrame, threshold: float = 0.95) -> List[str]:
    corr = dfX.corr(numeric_only=True).abs()
    keep = []
    drop = set()
    for i, c1 in enumerate(corr.columns):
        if c1 in drop:
            continue
        keep.append(c1)
        for c2 in corr.columns[i + 1:]:
            if corr.loc[c1, c2] >= threshold:
                drop.add(c2)
    return keep

def _get_default_model(task_type: str, model_type: Optional[str] = None):
    s = (model_type or "").lower()
    if task_type.startswith("class"):
        if "gb" in s:
            return GradientBoostingClassifier(random_state=42)
        return RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1)
    else:
        if "gb" in s:
            return GradientBoostingRegressor(random_state=42)
        return RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)

# ======= “cotovelo” para top_k="auto" ======= #

def _elbow_k_from_scores(scores: np.ndarray) -> int:
    s = np.asarray(scores, dtype=float)
    if s.size == 0:
        return 1
    s = np.sort(s)[::-1]
    x = np.linspace(0, 1, len(s))
    y = (s - s.min()) / (s.max() - s.min() + 1e-12)
    # Distância vertical de cada ponto até a diagonal que liga (0,1) a (1,0): d = (1-x) - y.
    # (A fórmula anterior, d = y - x, tinha d[0] = 1 sempre como máximo teórico - ou seja,
    # argmax(d) sempre caía no primeiro ponto, retornando k=1 para qualquer curva.)
    d = (1 - x) - y
    k = int(np.argmax(d)) + 1
    return max(1, min(k, len(s)))

def _auto_k_by_quick_scores(X, y, task_type: str, prefer: str = "rf", k_max: Optional[int] = None) -> int:
    if k_max is None:
        k_max = X.shape[1]

    if prefer == "rf":
        if task_type.startswith("class"):
            m = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)
        else:
            m = RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)
        m.fit(X, y)
        scores = m.feature_importances_
    elif prefer == "anova":
        scores = (f_classif(X, y)[0] if task_type.startswith("class") else f_regression(X, y)[0])
    else:  # "mi"
        scores = (mutual_info_classif(X, y, random_state=42) if task_type.startswith("class")
                  else mutual_info_regression(X, y, random_state=42))

    k = _elbow_k_from_scores(scores)
    return max(1, min(k, k_max))

def _resolve_k(top_k: Union[int, str], X_cols: List[str], scores_for_elbow: Optional[np.ndarray] = None,
               y=None, X=None, task_type: Optional[str] = None, prefer="rf") -> int:
    if isinstance(top_k, str) and top_k.strip().lower() == "auto":
        if scores_for_elbow is not None:
            return _elbow_k_from_scores(scores_for_elbow)
        # fallback rápido
        return _auto_k_by_quick_scores(X.values, y.values, task_type, prefer=prefer, k_max=len(X_cols))
    try:
        return max(1, min(int(top_k), len(X_cols)))
    except Exception:
        # fallback seguro
        return max(1, min(20, len(X_cols)))

# ========================== FUNÇÃO PRINCIPAL ========================== #

def apply_recommended_selection(
    df_in: pd.DataFrame,
    method_name: str,
    first_feature_col: str,
    last_feature_col: str,
    y_series: Optional[pd.Series],
    task_type: str,
    model_type: Optional[str] = None,
    top_k: Union[int, str] = 20,
    corr_threshold: float = 0.95,
    variance_threshold: float = 0.0,
    alpha: float = 1.0,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Executa o método de seleção de features conforme nome indicado em method_name.
    Retorna (df_reduzido, lista_colunas_selecionadas).
    """
    if df_in is None or df_in.empty:
        raise ValueError("DataFrame de entrada está vazio.")

    first_feature_col = _to_colname(df_in, first_feature_col)
    last_feature_col = _to_colname(df_in, last_feature_col)
    X_cols = _slice_columns(df_in, first_feature_col, last_feature_col)
    X = _ensure_numeric(df_in[X_cols])

    needs_y = method_name not in ["Variance Threshold", "Correlation Threshold"]
    if needs_y:
        if y_series is None or y_series.dropna().empty:
            raise ValueError("The selected method requires a label column (y).")
        y = pd.to_numeric(y_series, errors="coerce").fillna(0.0)
    else:
        y = None

    # ======================= MÉTODOS DE FILTRO ======================= #

    if method_name == "Variance Threshold":
        selector = VarianceThreshold(threshold=variance_threshold)
        mask = selector.fit(X).get_support()
        selected_cols = [c for c, keep in zip(X_cols, mask) if keep]

    elif method_name == "Correlation Threshold":
        selected_cols = _corr_filter(X, threshold=corr_threshold)

    elif method_name == "SelectKBest (ANOVA F-test)":
        k = _resolve_k(top_k, X_cols, y=y, X=X, task_type=task_type, prefer="anova")
        selector = SelectKBest(score_func=f_classif if task_type.startswith("class") else f_regression, k=k)
        mask = selector.fit(X, y).get_support()
        selected_cols = [c for c, keep in zip(X_cols, mask) if keep]

    elif method_name == "SelectKBest (Chi2)":
        Xp = X.copy()
        if (Xp.values < 0).any():
            Xp = pd.DataFrame(MinMaxScaler().fit_transform(X), columns=X.columns)
        k = _resolve_k(top_k, X_cols, y=y, X=Xp, task_type=task_type, prefer="anova")
        selector = SelectKBest(score_func=chi2, k=k)
        mask = selector.fit(Xp, y).get_support()
        selected_cols = [c for c, keep in zip(X_cols, mask) if keep]

    elif method_name == "SelectPercentile":
        # mantém sua semântica original: 20% das colunas
        k = max(1, int(len(X_cols) * 0.2))
        selector = SelectKBest(score_func=f_classif if task_type.startswith("class") else f_regression, k=k)
        mask = selector.fit(X, y).get_support()
        selected_cols = [c for c, keep in zip(X_cols, mask) if keep]

    elif method_name == "Mutual Information":
        scores = (mutual_info_classif(X, y, random_state=42) if task_type.startswith("class")
                  else mutual_info_regression(X, y, random_state=42))
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores, y=y, X=X, task_type=task_type, prefer="mi")
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    # ======================= MÉTODOS WRAPPER ======================= #

    elif method_name == "RFE":
        model = _get_default_model(task_type, model_type)
        k = _resolve_k(top_k, X_cols, y=y, X=X, task_type=task_type, prefer="rf")
        selector = RFE(model, n_features_to_select=k, step=1)
        mask = selector.fit(X, y).get_support()
        selected_cols = [c for c, keep in zip(X_cols, mask) if keep]

    elif method_name == "SFS (Forward)":
        model = _get_default_model(task_type, model_type)
        k = _resolve_k(top_k, X_cols, y=y, X=X, task_type=task_type, prefer="rf")
        selector = SequentialFeatureSelector(model, n_features_to_select=k, direction="forward", n_jobs=-1)
        selector.fit(X, y)
        selected_cols = [c for c, keep in zip(X_cols, selector.get_support()) if keep]

    elif method_name == "SFS (Backward)":
        model = _get_default_model(task_type, model_type)
        k = _resolve_k(top_k, X_cols, y=y, X=X, task_type=task_type, prefer="rf")
        selector = SequentialFeatureSelector(model, n_features_to_select=k, direction="backward", n_jobs=-1)
        selector.fit(X, y)
        selected_cols = [c for c, keep in zip(X_cols, selector.get_support()) if keep]

    # ======================= MÉTODOS EMBUTIDOS ======================= #

    elif method_name == "Lasso (L1)":
        model = Lasso(alpha=alpha, max_iter=10000, random_state=42)
        model.fit(X, y)
        scores = np.abs(model.coef_)
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores)
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    elif method_name == "Ridge (L2)":
        model = Ridge(alpha=alpha, random_state=42)
        model.fit(X, y)
        scores = np.abs(model.coef_)
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores)
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    elif method_name == "Elastic Net":
        model = ElasticNet(alpha=alpha, l1_ratio=0.5, random_state=42, max_iter=10000)
        model.fit(X, y)
        scores = np.abs(model.coef_)
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores)
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    elif method_name == "Tree-based Importance (RandomForest)":
        model = (RandomForestClassifier(n_estimators=600, random_state=42, n_jobs=-1)
                 if task_type.startswith("class")
                 else RandomForestRegressor(n_estimators=600, random_state=42, n_jobs=-1))
        model.fit(X, y)
        scores = model.feature_importances_
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores, y=y, X=X, task_type=task_type, prefer="rf")
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    elif method_name == "GB Importance":
        model = (GradientBoostingClassifier(random_state=42)
                 if task_type.startswith("class")
                 else GradientBoostingRegressor(random_state=42))
        model.fit(X, y)
        scores = model.feature_importances_
        k = _resolve_k(top_k, X_cols, scores_for_elbow=scores)
        order = np.argsort(scores)[::-1][:k]
        selected_cols = [X_cols[i] for i in order]

    # ======================= MODELOS ESTATÍSTICOS ======================= #

    elif method_name in ["Stepwise AIC", "Stepwise BIC"]:
        from statsmodels.api import OLS, add_constant, Logit
        Xc = add_constant(X)
        if task_type.startswith("class"):
            model = Logit(y, Xc).fit(disp=0)
        else:
            model = OLS(y, Xc).fit(disp=0)

        crit = "aic" if "AIC" in method_name else "bic"
        base_score = getattr(model, crit)
        selected_cols = list(X_cols)

        for col in X_cols:
            cols_try = [c for c in selected_cols if c != col]
            if len(cols_try) < 2:
                continue
            X_try = add_constant(X[cols_try])
            try:
                new_model = (Logit(y, X_try).fit(disp=0)
                             if task_type.startswith("class")
                             else OLS(y, X_try).fit(disp=0))
                new_score = getattr(new_model, crit)
                if new_score < base_score:
                    base_score = new_score
                    selected_cols = cols_try
            except Exception:
                continue

    else:
        raise ValueError(f"Método '{method_name}' não reconhecido.")

    df_out = df_in[selected_cols + [c for c in df_in.columns if c not in X_cols]]
    return df_out, selected_cols

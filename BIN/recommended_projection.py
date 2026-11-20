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
recommended_projection.py
Projeções/dimensionality reduction para CODRUG (compatível com pandas/scikit-learn).

API principal:
    apply_recommended_projection(
        df_in, method_name, first_feature_col, last_feature_col,
        y_series, task_type, model_type=None,
        n_components=2, random_state=42, extra_params=None
    ) -> (df_out, proj_columns, eval_info)
"""
from typing import List, Tuple, Optional, Dict, Any, Union
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib

from sklearn.decomposition import PCA, KernelPCA, TruncatedSVD, NMF
from sklearn.manifold import TSNE, Isomap, SpectralEmbedding
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler, FunctionTransformer

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import StratifiedKFold, KFold, cross_val_score


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

def _standardize(X: pd.DataFrame) -> np.ndarray:
    return StandardScaler().fit_transform(X.values)

def _get_default_model(task_type: str, model_type: Optional[str] = None):
    """Modelo simples para avaliação após projeção (quando aplicável)."""
    s = (model_type or "").lower()
    if task_type.startswith("class"):
        if "svm" in s:
            return SVC(kernel="rbf", probability=True, random_state=42)
        if "knn" in s:
            return KNeighborsClassifier(n_neighbors=7)
        return RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)
    else:
        if "svr" in s or "svm" in s:
            return SVR(kernel="rbf")
        if "knn" in s:
            return KNeighborsRegressor(n_neighbors=7)
        return RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)

def _cv_score(X, y, task_type: str, model_type: Optional[str] = None, cv=5, random_state=42):
    model = _get_default_model(task_type, model_type)
    if task_type.startswith("class"):
        cvobj = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
        scoring = "f1_macro"
    else:
        cvobj = KFold(n_splits=cv, shuffle=True, random_state=random_state)
        scoring = "r2"
    scores = cross_val_score(model, X, y, cv=cvobj, scoring=scoring, n_jobs=-1)
    return {"metric": scoring, "mean": float(np.mean(scores)), "std": float(np.std(scores))}


# ========================== FUNÇÃO PRINCIPAL ========================== #

def apply_recommended_projection(
    df_in: pd.DataFrame,
    method_name: str,
    first_feature_col: str,
    last_feature_col: str,
    y_series: Optional[pd.Series],
    task_type: str,
    model_type: Optional[str] = None,
    n_components: Optional[Union[int, float]] = None,
    random_state: int = None,
    var_thr: float = None,
    extra_params: Optional[Dict[str, Any]] = None,
    projection_artifact_path: Optional[str] = None,
    save_projection_artifact: bool = False,
    reuse_saved_projection: bool = False,
) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    """
    Executa a projeção/dimensionalidade pelo método indicado.
    Retorna (df_projetado_com_cols_restantes, lista_nomes_componentes, eval_info(opcional)).
    """
    if df_in is None or df_in.empty:
        raise ValueError("Internal DataFrame is empty.")

    extra_params = extra_params or {}

    # ==== Seleciona bloco X ====
    first_feature_col = _to_colname(df_in, first_feature_col)
    last_feature_col  = _to_colname(df_in, last_feature_col)
    X_cols = _slice_columns(df_in, first_feature_col, last_feature_col)
    X = _ensure_numeric(df_in[X_cols])

    if reuse_saved_projection:
        if not projection_artifact_path or not os.path.isfile(projection_artifact_path):
            raise ValueError("Projection artifact not found for transform on external data.")

        artifact = joblib.load(projection_artifact_path)
        saved_method = str(artifact.get("method_name", "")).strip().lower()
        if saved_method != str(method_name or "").strip().lower():
            raise ValueError(
                f"Saved projection method '{artifact.get('method_name')}' does not match requested method '{method_name}'."
            )

        saved_feature_cols = list(artifact.get("feature_columns") or [])
        if not saved_feature_cols:
            raise ValueError("Saved projection artifact does not contain feature columns.")

        missing_cols = [c for c in saved_feature_cols if c not in df_in.columns]
        if missing_cols:
            raise ValueError(
                "External dataset is missing feature columns required by the saved projection: "
                + ", ".join(map(str, missing_cols[:15]))
            )

        projector = artifact.get("projector")
        scaler = artifact.get("scaler")
        if projector is None or not hasattr(projector, "transform"):
            raise ValueError("Saved projection artifact cannot transform new data.")

        X_saved = _ensure_numeric(df_in[saved_feature_cols])
        X_input = scaler.transform(X_saved.values) if scaler is not None else X_saved.values
        n_negative = 0
        if saved_method == "nmf":
            # Artefatos de NMF gravados antes do corte de negativos ir para o artefato não têm scaler:
            # o corte (negativos -> 0) é feito aqui, igual ao do ajuste.
            n_negative = int((np.asarray(X_saved.values, dtype=float) < 0).sum())
            if scaler is None:
                X_input = np.clip(np.asarray(X_input, dtype=float), 0.0, None)
        Z = projector.transform(X_input)

        proj_cols = list(artifact.get("proj_cols") or [])
        if not proj_cols:
            proj_cols = [f"PRJ{i+1}" for i in range(Z.shape[1])]

        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        keep_others = [c for c in df_in.columns if c not in saved_feature_cols]
        df_out = pd.concat([proj, df_in[keep_others].reset_index(drop=True)], axis=1)
        eval_info = {
            "artifact_applied": True,
            "artifact_path": projection_artifact_path,
            "transform_feature_count": len(saved_feature_cols),
        }
        if saved_method == "nmf":
            eval_info["nmf_negative_values_clipped"] = n_negative
        return df_out, proj_cols, eval_info

    # ==== Trata y quando necessário ====
    y = None
    y_valid = None          # máscara das linhas com y válido (métodos supervisionados)
    method_lower = (method_name or "").lower()

    needs_y_supervised = any(k in method_lower for k in ["lda", "pls", "plsr", "pls-da"])
    if needs_y_supervised:
        if y_series is None or y_series.dropna().empty:
            raise ValueError("O método selecionado requer coluna de rótulos/valores (y).")
        ys = pd.Series(np.asarray(y_series))
        if len(ys) != len(X):
            raise ValueError("The label column (y) and the feature block have different numbers of rows.")
        if task_type.startswith("class"):
            # Rótulos de classe (texto ou número) viram códigos inteiros 0..k-1. Linhas sem rótulo
            # (NaN/vazio) NÃO viram uma classe "nan": ficam fora do ajuste e são projetadas depois,
            # com o modelo já ajustado.
            as_text = ys.astype(str).str.strip()
            y_valid = (ys.notna() & (as_text != "")).to_numpy()
            labels = ys[y_valid] if pd.api.types.is_numeric_dtype(ys) else as_text[y_valid]
            y = np.asarray(pd.Categorical(labels).codes, dtype=int)
        else:
            # Regressão: linhas sem valor de y (ou não numérico) ficam fora do ajuste do PLS. Antes elas
            # viravam y = 0.0, um valor falso que puxava os componentes.
            y_num = pd.to_numeric(ys, errors="coerce")
            y_valid = y_num.notna().to_numpy()
            y = y_num[y_valid].to_numpy(dtype=float)
        n_fit = int(y_valid.sum())
        if n_fit < 3:
            raise ValueError(f"Only {n_fit} row(s) have a valid label/value (y); the supervised projection "
                             "needs at least 3.")
        if task_type.startswith("class") and len(np.unique(y)) < 2:
            raise ValueError("The label column (y) has fewer than 2 classes - the supervised projection "
                             "needs at least 2 classes.")

    # ==== Executa método ====
    proj, proj_cols = None, []
    eval_info: Dict[str, Any] = {}
    artifact_scaler = None
    artifact_projector = None

    if method_lower in ("pca", "principal component analysis"):
        Xs = _standardize(X)

        # Se n_components for passado como None, 0 ou negativo, use var_thr
        if n_components is None:
            n_comp_pca = var_thr  # usa fração de variância acumulada
        elif isinstance(n_components, float) and 0 < n_components < 1:
            n_comp_pca = n_components  # usuário passou diretamente uma fração
        else:
            n_comp_pca = n_components

        pca = PCA(n_components=n_comp_pca, random_state=random_state)
        Z = pca.fit_transform(Xs)
        artifact_scaler = StandardScaler().fit(X.values)
        artifact_projector = PCA(n_components=n_comp_pca, random_state=random_state).fit(artifact_scaler.transform(X.values))

        proj_cols = [f"PC{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

        # Info adicional
        explained = pca.explained_variance_ratio_
        eval_info["explained_variance_ratio"] = explained.tolist()

        # NOVO: adicionar as 3 primeiras variâncias explicadas formatadas
        eval_info["top3_var_explained"] = [
            round(explained[i] * 100, 2)
            for i in range(min(3, len(explained)))
        ]

    elif "kernel pca" in method_lower or "kpca" in method_lower:
        kernel = extra_params.get("kernel", "rbf")
        gamma = extra_params.get("gamma", None)
        artifact_scaler = StandardScaler().fit(X.values)
        Xs = artifact_scaler.transform(X.values)
        kpca = KernelPCA(n_components=n_components, kernel=kernel, gamma=gamma, random_state=random_state)
        Z = kpca.fit_transform(Xs)
        artifact_projector = kpca
        proj_cols = [f"KPC{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

    elif "tsne" in method_lower or "t-sne" in method_lower:
        # t-SNE ignora n_components > 3 (prático até 3)
        perplexity = float(extra_params.get("perplexity", 30))
        learning_rate = float(extra_params.get("learning_rate", 200))
        n_iter = int(extra_params.get("n_iter", 1000))
        Xs = MinMaxScaler().fit_transform(X.values)  # ajuda estabilidade do TSNE
        ts = TSNE(n_components=min(n_components, 3), perplexity=perplexity,
                  learning_rate=learning_rate, n_iter=n_iter, init="pca", random_state=random_state)
        Z = ts.fit_transform(Xs)
        proj_cols = [f"TSNE{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

    elif "umap" in method_lower:
        try:
            import umap
        except Exception as e:
            raise RuntimeError("UMAP requer o pacote 'umap-learn'. Instale com: pip install umap-learn") from e
        n_neighbors = int(extra_params.get("n_neighbors", 15))
        min_dist    = float(extra_params.get("min_dist", 0.1))
        artifact_scaler = MinMaxScaler().fit(X.values)
        Xs = artifact_scaler.transform(X.values)
        um = umap.UMAP(n_components=n_components, n_neighbors=n_neighbors,
                       min_dist=min_dist, random_state=random_state)
        Z = um.fit_transform(Xs)
        artifact_projector = um
        proj_cols = [f"UMAP{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

    elif "svd" in method_lower or "truncatedsvd" in method_lower:
        svd = TruncatedSVD(n_components=n_components, random_state=random_state)
        Z = svd.fit_transform(X.values)
        artifact_projector = svd
        proj_cols = [f"SVD{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        eval_info["explained_variance_ratio"] = getattr(svd, "explained_variance_ratio_", np.array([])).tolist()

    elif method_lower == "nmf":
        # NMF exige dados não negativos: valores negativos são zerados. O mesmo corte vai para o artefato
        # (artifact_scaler), para que a projeção de dados externos faça igual - sem ele o transform()
        # do NMF dava erro com qualquer valor negativo no dataframe externo.
        artifact_scaler = FunctionTransformer(np.clip, kw_args={"a_min": 0.0, "a_max": None})
        n_negative = int((X.values < 0).sum())
        Xp = artifact_scaler.transform(X.values)
        nmf = NMF(n_components=n_components, init="nndsvd", random_state=random_state, max_iter=500)
        Z = nmf.fit_transform(Xp)
        artifact_projector = nmf
        proj_cols = [f"NMF{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        eval_info["nmf_negative_values_clipped"] = n_negative

    elif "isomap" in method_lower:
        # sklearn's Isomap has no "min_dist" parameter (that's a UMAP concept) - only
        # n_neighbors applies here.
        n_neighbors = int(extra_params.get("n_neighbors", 10))
        iso = Isomap(n_neighbors=n_neighbors, n_components=n_components)
        Z = iso.fit_transform(X.values)
        artifact_projector = iso
        proj_cols = [f"ISO{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

    elif "spectral" in method_lower:
        affinity = extra_params.get("affinity", "nearest_neighbors")
        se = SpectralEmbedding(n_components=n_components, affinity=affinity, random_state=random_state)
        Z = se.fit_transform(X.values)
        proj_cols = [f"SE{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)

    elif "lda" in method_lower:
        # Somente classificação; n_components <= n_classes-1
        if not str(task_type).lower().startswith("class"):
            raise ValueError("LDA requer tarefa de classificação.")
        classes = np.unique(y)
        max_comp = max(1, len(classes) - 1)
        n_comp_lda = min(n_components, max_comp)
        Xs = _standardize(X)
        lda = LDA(n_components=n_comp_lda)
        lda.fit(Xs[y_valid], y)
        Z = lda.transform(Xs)
        proj_cols = [f"LDA{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        # Avalia modelo default no espaço projetado (só as linhas com rótulo)
        eval_info = _cv_score(Z[y_valid], y, "classification", model_type)

    elif "pls-da" in method_lower or "pls da" in method_lower:
        if not str(task_type).lower().startswith("class"):
            raise ValueError("PLS-DA requer tarefa de classificação.")
        # PLS-DA = PLS ajustado a uma matriz de INDICADORES de classe (uma coluna 0/1 por classe), não
        # aos códigos inteiros das classes: com 3 ou mais classes, os códigos (0, 1, 2...) imporiam uma
        # ordem e distâncias que não existem entre as classes. Com 2 classes uma única coluna 0/1 já
        # basta (a segunda seria o complemento exato da primeira).
        n_classes = len(np.unique(y))
        indicator = (y == np.unique(y)[1]).astype(float) if n_classes == 2 else (
            (y[:, None] == np.unique(y)[None, :]).astype(float))
        Xs = _standardize(X)
        n_comp_plsda = int(max(1, min(n_components, Xs.shape[1], int(y_valid.sum()) - 1)))
        pls = PLSRegression(n_components=n_comp_plsda)
        pls.fit(Xs[y_valid], indicator)
        Z = pls.transform(Xs)
        proj_cols = [f"PLSDA{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        eval_info = _cv_score(Z[y_valid], y, "classification", model_type)

    elif "pls" in method_lower:  # PLS Regression
        if not str(task_type).lower().startswith("regress"):
            raise ValueError("PLS Regression requer tarefa de regressão.")
        Xs = _standardize(X)
        n_comp_pls = int(max(1, min(n_components, Xs.shape[1], int(y_valid.sum()) - 1)))
        pls = PLSRegression(n_components=n_comp_pls)
        pls.fit(Xs[y_valid], y)
        Z = pls.transform(Xs)
        proj_cols = [f"PLS{i+1}" for i in range(Z.shape[1])]
        proj = pd.DataFrame(Z, columns=proj_cols, index=df_in.index)
        eval_info = _cv_score(Z[y_valid], y, "regression", model_type)

    else:
        raise ValueError(f"Método de projeção '{method_name}' não reconhecido.")

    # Junta projeção com as colunas fora do bloco [first..last]
    keep_others = [c for c in df_in.columns if c not in X_cols]
    df_out = pd.concat([proj, df_in[keep_others].reset_index(drop=True)], axis=1)

    if save_projection_artifact and projection_artifact_path:
        if artifact_projector is not None and hasattr(artifact_projector, "transform"):
            os.makedirs(os.path.dirname(projection_artifact_path), exist_ok=True)
            joblib.dump(
                {
                    "method_name": method_name,
                    "feature_columns": X_cols,
                    "proj_cols": proj_cols,
                    "scaler": artifact_scaler,
                    "projector": artifact_projector,
                },
                projection_artifact_path,
            )
            eval_info["artifact_saved"] = True
            eval_info["artifact_path"] = projection_artifact_path
        else:
            eval_info["artifact_saved"] = False
            eval_info["artifact_reason"] = "Selected projection method does not support transform() for new data."

    return df_out, proj_cols, eval_info

"""Interpretability helpers for CODRUG (STEP 5 "Interpretability Tools").

Pure computation + figure builders, no Qt: SHAP explainer dispatch by model family, correlation
grouping of descriptors (hierarchical clustering on Spearman distance) and permutation importance
(individual or by whole correlated group) on the TEST set. SHAP is an optional dependency, imported
lazily; the library's own plotting functions are never used (they call plt.show()) - values are
extracted here and drawn on plain matplotlib Figures that the GUI embeds in its own canvases.
"""
from __future__ import annotations

import importlib.util
import os
import re
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

# LinearExplainer's correlation-dependent mode scales ~O(p^3) (measured: p=80 -> 2.6 s, p=160 -> 24 s,
# hours for p>=300 on binary fingerprints), so above this many descriptors it falls back to the
# interventional mode. Grouped importance is the recommended way to handle correlated descriptors there.
LINEAR_CORR_MAX_FEATURES = 100

_TREE_PREFIXES = (
    "RandomForest", "ExtraTrees", "GradientBoosting", "HistGradientBoosting",
    "XGB", "LGBM", "CatBoost", "DecisionTree",
)
_LINEAR_NAMES = {
    "Ridge", "RidgeClassifier", "Lasso", "ElasticNet", "LinearRegression", "HuberRegressor",
    "BayesianRidge", "LogisticRegression", "SGDRegressor", "SGDClassifier",
    "PassiveAggressiveRegressor", "PassiveAggressiveClassifier", "LinearDiscriminantAnalysis",
}
_PROJECTION_RE = re.compile(r"^(PRJ|PC|KPC|TSNE|UMAP|SVD|NMF|ISO|SE|LDA|PLSDA|PLS)\d+$")

_shap_module = None


def shap_installed() -> bool:
    """Cheap availability check (does not import shap, which pulls numba/llvmlite)."""
    return importlib.util.find_spec("shap") is not None


def import_shap():
    global _shap_module
    if _shap_module is None:
        import shap  # noqa: WPS433 - deliberately lazy (optional dependency)
        _shap_module = shap
    return _shap_module


# --------------------------------------------------------------------------------------------------
# model family / explainer dispatch
# --------------------------------------------------------------------------------------------------
def unwrap_model(model):
    """Returns the estimator that actually holds the learned parameters: unwraps CODRUG's
    label-encoding wrapper (XGBClassifier) and search objects (best_estimator_)."""
    seen = 0
    while seen < 4:
        seen += 1
        if type(model).__name__ == "_LabelEncodingClassifierWrapper" and "base_estimator_" in model.__dict__:
            model = model.__dict__["base_estimator_"]
        elif "best_estimator_" in getattr(model, "__dict__", {}):
            model = model.__dict__["best_estimator_"]
        else:
            break
    return model


def model_family(model) -> str:
    name = type(unwrap_model(model)).__name__
    if name in ("BaggingRegressor", "BaggingClassifier"):
        return "bagging"
    if name.startswith(_TREE_PREFIXES):
        return "tree"
    if name in _LINEAR_NAMES:
        return "linear"
    return "permutation"


def describe_explainer(model, n_features: int) -> dict:
    """What explainer will be used and whether its values are exact or approximate.
    `key` is translated by the GUI (i18n); `exact` drives the exact/approximate wording."""
    fam = model_family(model)
    if fam == "tree":
        return {"family": fam, "key": "tree", "exact": True}
    if fam == "bagging":
        return {"family": fam, "key": "bagging", "exact": True}
    if fam == "linear":
        if n_features <= LINEAR_CORR_MAX_FEATURES:
            return {"family": fam, "key": "linear_corr", "exact": True}
        return {"family": fam, "key": "linear_indep", "exact": True, "limit": LINEAR_CORR_MAX_FEATURES}
    return {"family": fam, "key": "permutation", "exact": False}


def looks_like_projection(columns, source_path: str = "", min_fraction: float = 0.8) -> bool:
    """True when the model's X columns are projection components (PCA/UMAP/t-SNE/...): SHAP and
    permutation would then refer to components, not descriptors, and the mechanistic reading is lost."""
    cols = [str(c) for c in columns]
    if source_path and "df3_projection" in os.path.basename(str(source_path)):
        return True
    if not cols:
        return False
    hits = sum(1 for c in cols if _PROJECTION_RE.match(c))
    return hits / len(cols) >= min_fraction


# --------------------------------------------------------------------------------------------------
# correlation grouping
# --------------------------------------------------------------------------------------------------
def correlation_groups(X: pd.DataFrame, threshold: float) -> np.ndarray:
    """Hierarchical clustering (average linkage) on the Spearman distance 1-|rho|, cut at
    1-threshold: descriptors whose cluster-average |rho| >= threshold end up in one group.
    Uses the TRAINING data only. Constant columns (undefined correlation) stay in their own group.
    Returns an integer label per column, numbered by order of first appearance."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    from scipy.stats import rankdata

    A = X.to_numpy(dtype=float)
    p = A.shape[1]
    if p == 1:
        return np.zeros(1, dtype=int)
    R = rankdata(A, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        rho = np.corrcoef(R, rowvar=False)
    rho = np.nan_to_num(rho, nan=0.0)
    np.fill_diagonal(rho, 1.0)
    dist = np.clip(1.0 - np.abs(rho), 0.0, 1.0)
    dist = (dist + dist.T) / 2.0
    np.fill_diagonal(dist, 0.0)
    Z = linkage(squareform(dist, checks=False), method="average")
    raw = fcluster(Z, t=max(1.0 - float(threshold), 1e-9), criterion="distance")
    order = {}
    labels = np.zeros(p, dtype=int)
    for i, g in enumerate(raw):
        if g not in order:
            order[g] = len(order)
        labels[i] = order[g]
    return labels


def build_groups(columns, labels) -> list:
    """[{id, name, idx, members}] ordered by group id."""
    columns = [str(c) for c in columns]
    groups = {}
    for i, g in enumerate(labels):
        groups.setdefault(int(g), []).append(i)
    out = []
    for g in sorted(groups):
        idx = groups[g]
        members = [columns[i] for i in idx]
        name = members[0] if len(idx) == 1 else f"G{g + 1:03d}"
        out.append({"id": g, "name": name, "idx": idx, "members": members})
    return out


def groups_table(groups) -> pd.DataFrame:
    rows = []
    for g in groups:
        for m in g["members"]:
            rows.append({"Feature": m, "Group": g["name"], "Group_size": len(g["members"])})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------
# permutation importance (test set, individual or by whole group)
# --------------------------------------------------------------------------------------------------
def resolve_scorer(scoring):
    from sklearn.metrics import get_scorer
    if scoring is None:
        return lambda model, X, y: float(model.score(X, y))
    if isinstance(scoring, str):
        return get_scorer(scoring)
    return scoring


def grouped_permutation_importance(model, X_test: pd.DataFrame, y_test, scoring, groups, n_repeats=5,
                                   seed=123, n_jobs=0, progress_cb=None):
    """Permutation importance on the TEST set. Each group's columns are permuted TOGETHER (the same
    row permutation for every column of the group), so correlated descriptors never form impossible
    molecules; with singleton groups this is the usual per-descriptor importance. The score is
    always in sklearn's 'greater is better' convention, so importance = baseline - permuted score
    (positive = the model got worse). Returns (mean, std, baseline, scorer_fell_back)."""
    import joblib

    cols = list(X_test.columns)
    A = X_test.to_numpy()
    n = A.shape[0]
    scorer = resolve_scorer(scoring)
    fell_back = False
    try:
        base = float(scorer(model, X_test, y_test))
    except Exception:
        scorer = resolve_scorer(None)
        base = float(scorer(model, X_test, y_test))
        fell_back = True

    rng = np.random.RandomState(seed)
    perms = [rng.permutation(n) for _ in range(int(n_repeats))]
    const = np.ptp(A.astype(float), axis=0) == 0

    def _task(gi):
        idx = groups[gi]["idx"]
        if all(const[j] for j in idx):
            return gi, np.zeros(len(perms))
        drops = []
        with joblib.parallel_backend("threading"):
            for perm in perms:
                Xp = A.copy()
                Xp[:, idx] = A[perm][:, idx]
                drops.append(base - float(scorer(model, pd.DataFrame(Xp, columns=cols), y_test)))
        return gi, np.asarray(drops)

    workers = int(n_jobs) if n_jobs and int(n_jobs) > 0 else (os.cpu_count() or 1)
    workers = max(1, min(workers, len(groups)))
    results = [None] * len(groups)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_task, gi) for gi in range(len(groups))]
        for fut in as_completed(futures):
            gi, drops = fut.result()
            results[gi] = drops
            done += 1
            if progress_cb and (done % max(1, len(groups) // 50) == 0 or done == len(groups)):
                progress_cb(done / len(groups), "")
    mean = np.array([r.mean() for r in results])
    std = np.array([r.std() for r in results])
    return mean, std, base, fell_back


# --------------------------------------------------------------------------------------------------
# SHAP
# --------------------------------------------------------------------------------------------------
def _to_k_n_f(sv, n, f):
    """Normalises any SHAP output (list of arrays, (n,f), (n,f,k) or (k,n,f)) to (k, n, f)."""
    arr = np.stack([np.asarray(a) for a in sv], 0) if isinstance(sv, list) else np.asarray(sv)
    if arr.ndim == 2:
        arr = arr[None]
    elif arr.ndim == 3 and arr.shape[0] == n and arr.shape[1] == f:
        arr = np.moveaxis(arr, 2, 0)
    return arr.astype(float)


def _tree_values(shap, inner, X_rows):
    expl = shap.TreeExplainer(inner)
    sv = expl.shap_values(X_rows, check_additivity=False)
    return _to_k_n_f(sv, *X_rows.shape)


def _bagging_values(shap, inner, X_rows):
    """Exact SHAP for a bagging ensemble of trees: the ensemble prediction is the mean of the base
    estimators' predictions and SHAP values are linear, so the mean of each tree's TreeExplainer
    values is exact (additivity verified to ~1e-15). Handles per-estimator feature subsets."""
    n, f = X_rows.shape
    acc = None
    for est, feats in zip(inner.estimators_, inner.estimators_features_):
        feats = np.asarray(feats)
        sub = X_rows.iloc[:, feats]
        sv = shap.TreeExplainer(est).shap_values(sub, check_additivity=False)
        sv = _to_k_n_f(sv, n, len(feats))
        full = np.zeros((sv.shape[0], n, f))
        full[:, :, feats] = sv
        acc = full if acc is None else acc + full
    return acc / len(inner.estimators_)


def _linear_values(shap, inner, X_train, X_rows):
    p = X_rows.shape[1]
    notes = []
    if p <= LINEAR_CORR_MAX_FEATURES:
        try:
            masker = shap.maskers.Impute(X_train.to_numpy(dtype=float), method="linear")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sv = shap.LinearExplainer(inner, masker).shap_values(X_rows.to_numpy(dtype=float))
            arr = _to_k_n_f(sv, *X_rows.shape)
            if np.all(np.isfinite(arr)):
                return arr, "linear_corr", notes
            notes.append("linear_corr_failed")
        except Exception:
            notes.append("linear_corr_failed")
    masker = shap.maskers.Independent(X_train.to_numpy(dtype=float), max_samples=100)
    sv = shap.LinearExplainer(inner, masker).shap_values(X_rows.to_numpy(dtype=float))
    return _to_k_n_f(sv, *X_rows.shape), "linear_indep", notes


def _prediction_fn(model, task, columns):
    def _df(A):
        return pd.DataFrame(np.asarray(A), columns=columns)

    if task == "classification":
        if hasattr(model, "predict_proba"):
            return lambda A: np.asarray(model.predict_proba(_df(A)), dtype=float)
        if hasattr(model, "decision_function"):
            return lambda A: np.asarray(model.decision_function(_df(A)), dtype=float)
        classes = list(getattr(model, "classes_", []))
        return lambda A: np.array([classes.index(c) for c in model.predict(_df(A))], dtype=float)
    return lambda A: np.asarray(model.predict(_df(A)), dtype=float)


def _permutation_values(shap, model, task, X_train, X_rows, seed, progress_cb=None, n_background=50):
    cols = list(X_rows.columns)
    p = len(cols)
    bg = X_train.sample(n=min(n_background, len(X_train)), random_state=seed) if len(X_train) > 1 else X_train
    masker = shap.maskers.Independent(bg.to_numpy(dtype=float), max_samples=len(bg))
    fn = _prediction_fn(model, task, cols)
    # max_evals must be >= 2p+1; a few permutation passes when cheap, the minimum when p is large.
    n_pass = int(np.clip(4000 // (2 * p + 1), 2, 10))
    expl = shap.PermutationExplainer(fn, masker, seed=seed)
    chunk = max(1, min(10, len(X_rows)))
    parts = []
    for start in range(0, len(X_rows), chunk):
        block = X_rows.iloc[start:start + chunk].to_numpy(dtype=float)
        ex = expl(block, max_evals=(2 * p + 1) * n_pass, silent=True)
        parts.append(_to_k_n_f(ex.values, block.shape[0], p))
        if progress_cb:
            progress_cb(min(1.0, (start + chunk) / len(X_rows)), "")
    return np.concatenate(parts, axis=1)


def compute_shap(model, task, X_train, X_test, max_rows=100, seed=123, progress_cb=None):
    """SHAP values on (a sample of) the TEST set, dispatched by model family. Returns dict with
    values (k, n, p), the rows explained, the explainer actually used (key/exact) and note codes."""
    shap = import_shap()
    if len(X_test) > max_rows:
        X_rows = X_test.sample(n=int(max_rows), random_state=seed).sort_index()
    else:
        X_rows = X_test
    inner = unwrap_model(model)
    info = describe_explainer(model, X_rows.shape[1])
    notes = []
    key, exact = info["key"], info["exact"]
    values = None
    if len(X_test) > max_rows:
        notes.append("shap_rows_sampled")
    try:
        if info["family"] == "tree":
            values = _tree_values(shap, inner, X_rows)
        elif info["family"] == "bagging":
            values = _bagging_values(shap, inner, X_rows)
        elif info["family"] == "linear":
            values, key, extra = _linear_values(shap, inner, X_train, X_rows)
            notes += extra
    except Exception:
        values = None
        if info["family"] != "permutation":
            notes.append("fallback_permutation")
    if values is None:
        values = _permutation_values(shap, model, task, X_train, X_rows, seed, progress_cb)
        key, exact = "permutation", False
    return {"values": values, "X_rows": X_rows, "explainer_key": key, "exact": exact, "notes": notes}


def shap_importance(values, columns, groups=None) -> np.ndarray:
    """Mean |SHAP|: per descriptor (groups=None) or per group (SHAP values of the members are summed
    per sample first - they are additive - then |.| and the mean over samples). Averaged over classes."""
    if groups is None:
        return np.abs(values).mean(axis=1).mean(axis=0)
    out = np.zeros(len(groups))
    for gi, g in enumerate(groups):
        out[gi] = np.abs(values[:, :, g["idx"]].sum(axis=2)).mean(axis=1).mean()
    return out


# --------------------------------------------------------------------------------------------------
# SHAP x structure: which substructures drive the prediction (bitInfo / DrawMorganBit)
# --------------------------------------------------------------------------------------------------
def structure_records(values, X_rows, rows_pos, columns, X_train, smiles_train, smiles_test, names_train,
                      names_test, preferred_bits=2048, preferred_chirality=True, n_show=12, max_candidates=80):
    """Pairs the most important descriptors (mean |SHAP|) with the substructure each fingerprint bit
    encodes. Circular fingerprints (ECFP4/FCFP6/counts): RDKit bitInfo, only after the fpSize/
    chirality were VERIFIED by recomputing the stored fingerprints; MACCS/PubChem keys: their
    reference SMARTS. The example molecule is the explained test compound where the descriptor
    contributes most (largest |SHAP| among those that have it), else a training compound.
    Returns (records, note_codes)."""
    try:
        from . import module_feature_structures as mfs
    except Exception:
        return [], ["structures_not_applicable"]
    if not getattr(mfs, "_RDKIT_AVAILABLE", False):
        return [], ["structures_not_applicable"]

    cols = [str(c) for c in columns]
    importance = shap_importance(values, cols)
    order = np.argsort(importance)[::-1]
    parsed = {}
    for j in order[: int(max_candidates) * 4]:
        info = mfs.parse_descriptor_column(cols[j])
        if info is not None:
            parsed[int(j)] = info
    if not parsed:
        return [], ["structures_not_applicable"]

    notes, configs = [], {}
    for family in {p["family"] for p in parsed.values() if p["family"] in mfs.MORGAN_FAMILIES}:
        configs[family] = mfs.verify_morgan_config(family, X_train, smiles_train, preferred_bits, preferred_chirality)
        if configs[family] is None:
            notes.append("structures_unverified")

    sv = values[-1]                                   # positive class for binary classifiers
    X_rows_v = X_rows.to_numpy(dtype=float)
    X_train_v = X_train.to_numpy(dtype=float)
    smiles_test = list(smiles_test); smiles_train = list(smiles_train)
    names_test = list(names_test); names_train = list(names_train)
    rows_pos = np.asarray(rows_pos)
    records = []

    for j in order:
        if len(records) >= int(n_show):
            break
        j = int(j)
        info = parsed.get(j)
        if info is None:
            continue
        family, bit = info["family"], int(info["index"])
        cfg = configs.get(family)
        if family in mfs.MORGAN_FAMILIES and cfg is None:
            continue
        smarts_ref, exact, note_ref = None, True, ""
        if family not in mfs.MORGAN_FAMILIES:
            ref = mfs.resolve_feature(cols[j])
            if ref is None or not ref.get("smarts"):
                continue
            smarts_ref, exact, note_ref = ref["smarts"], bool(ref.get("exact", False)), ref.get("note", "")

        def _has(smi):
            if family in mfs.MORGAN_FAMILIES:
                return mfs.morgan_bit_radius(smi, family, bit, cfg["fp_bits"], cfg["chirality"]) is not None
            return mfs.smarts_matches(smi, smarts_ref)

        present = np.where(X_rows_v[:, j] > 0)[0]
        present = present[np.argsort(-np.abs(sv[present, j]))] if len(present) else present
        example = None
        for r in present[:25]:
            smi = smiles_test[int(rows_pos[r])]
            if _has(smi):
                example = (names_test[int(rows_pos[r])], smi, "explained test compound")
                break
        if example is None:
            for r in np.where(X_train_v[:, j] > 0)[0][:60]:
                smi = smiles_train[int(r)]
                if _has(smi):
                    example = (names_train[int(r)], smi, "training compound")
                    break
        if example is None:
            continue

        mask = X_rows_v[:, j] > 0
        mean_present = float(sv[mask, j].mean()) if mask.any() else float("nan")
        if mask.any():
            direction = "raises prediction" if mean_present > 0 else ("lowers prediction" if mean_present < 0 else "neutral")
        else:
            direction = "n/a (absent in explained rows)"
        rec = {
            "rank": len(records) + 1, "descriptor": cols[j], "family": family, "bit_index": bit,
            "mean_abs_shap": float(importance[j]), "mean_shap_when_present": mean_present,
            "n_present_explained": int(mask.sum()), "direction": direction,
            "example_name": str(example[0]), "example_smiles": example[1], "example_source": example[2],
            "exact": exact,
        }
        if family in mfs.MORGAN_FAMILIES:
            rec.update(fp_bits=cfg["fp_bits"], chirality=cfg["chirality"],
                       radius=mfs.morgan_bit_radius(example[1], family, bit, cfg["fp_bits"], cfg["chirality"]),
                       smarts=mfs.morgan_bit_env_smarts(example[1], family, bit, cfg["fp_bits"], cfg["chirality"]) or "")
        else:
            rec.update(fp_bits=None, chirality=None, radius=None, smarts=smarts_ref)
        records.append(rec)
    if not records and not notes:
        notes.append("structures_none_resolved")
    return records, sorted(set(notes))


def substructure_figure(records, title, n_cols=4):
    """Grid with one panel per important descriptor: the substructure (Draw.DrawMorganBit for circular
    fingerprints: central atom blue, aromatic yellow, rest grey; SMARTS match highlighted for MACCS/
    PubChem) with its mean |SHAP| and whether it raises or lowers the prediction."""
    if not records:
        return None
    import io as _io
    from matplotlib.figure import Figure
    from PIL import Image
    from . import module_feature_structures as mfs

    panels = []
    for rec in records:
        if rec["family"] in mfs.MORGAN_FAMILIES:
            png = mfs.draw_morgan_bit_png(rec["example_smiles"], rec["family"], rec["bit_index"],
                                          rec["fp_bits"], rec["chirality"])
        else:
            png = mfs.draw_smarts_match_png(rec["example_smiles"], rec["smarts"])
        if png is not None:
            panels.append((rec, np.asarray(Image.open(_io.BytesIO(png)).convert("RGB"))))
    if not panels:
        return None
    n = len(panels)
    n_cols = min(n_cols, n)
    n_rows = int(np.ceil(n / n_cols))
    fig = Figure(figsize=(3.3 * n_cols, 3.45 * n_rows + 0.6))
    arrows = {"raises prediction": "\u2191 raises", "lowers prediction": "\u2193 lowers", "neutral": "\u2194 neutral"}
    for k, (rec, img) in enumerate(panels):
        ax = fig.add_subplot(n_rows, n_cols, k + 1)
        ax.imshow(img)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#C0392B" if rec["direction"].startswith("raises") else "#2E86C1" if rec["direction"].startswith("lowers") else "#999999")
            sp.set_linewidth(2.0)
        tag = arrows.get(rec["direction"], "?")
        approx = "" if rec["exact"] else " (approx.)"
        ax.set_title(f"{rec['descriptor']}{approx}\nmean|SHAP|={rec['mean_abs_shap']:.3g}  {tag}", fontsize=9)
        ax.set_xlabel(f"{_short(rec['example_name'], 28)} ({rec['example_source'].split()[0]})", fontsize=7)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return fig


# --------------------------------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------------------------------
def _rank_table(label_col, labels, value_col, mean, std=None, groups=None):
    df = pd.DataFrame({label_col: labels})
    if groups is not None:
        df["N_features"] = [len(g["idx"]) for g in groups]
    df[value_col + "_mean" if std is not None else value_col] = mean
    if std is not None:
        df[value_col + "_std"] = std
    if groups is not None:
        df["Members"] = [";".join(g["members"]) for g in groups]
    sort_col = value_col + "_mean" if std is not None else value_col
    df = df.sort_values(sort_col, ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", np.arange(1, len(df) + 1))
    return df


def run_analysis(model, task, X_train, X_test, y_test, scoring, methods, modalities, corr_threshold=0.8,
                 n_repeats=5, shap_max_rows=100, n_jobs=0, seed=123, progress_cb=None, structures=None):
    """methods: subset of {"shap", "permutation"}; modalities: subset of {"individual", "group"}.
    structures (optional dict: smiles_train, smiles_test, names_train, names_test, fp_bits,
    fp_chirality, n_show): when given together with SHAP, also pairs the top descriptors with the
    substructures they encode (res["structures"])."""
    def _p(frac, msg=""):
        if progress_cb:
            progress_cb(frac, msg)

    cols = [str(c) for c in X_test.columns]
    X_train = X_train.copy(); X_test = X_test.copy()
    X_train.columns = cols; X_test.columns = cols
    res = {"notes": [], "columns": cols}

    groups = None
    if "group" in modalities:
        _p(0.02, "groups")
        labels = correlation_groups(X_train, corr_threshold)
        groups = build_groups(cols, labels)
        res["groups"] = groups
        res["groups_table"] = groups_table(groups)
    singles = build_groups(cols, np.arange(len(cols)))

    want_shap = "shap" in methods
    want_perm = "permutation" in methods
    w_shap = 0.55 if (want_shap and want_perm) else (1.0 if want_shap else 0.0)
    w_perm = 1.0 - w_shap if want_perm else 0.0
    base_pct = 0.05
    span = 0.93

    if want_shap:
        sh = compute_shap(model, task, X_train, X_test, max_rows=shap_max_rows, seed=seed,
                          progress_cb=lambda f, m="": _p(base_pct + span * w_shap * f, "shap"))
        res["shap_values"] = sh["values"]
        res["shap_X"] = sh["X_rows"]
        res["explainer_key"] = sh["explainer_key"]
        res["explainer_exact"] = sh["exact"]
        res["notes"] += sh["notes"]
        if "individual" in modalities:
            imp = shap_importance(sh["values"], cols)
            res["shap_individual"] = _rank_table("Feature", cols, "Mean_abs_SHAP", imp)
        if groups is not None:
            imp = shap_importance(sh["values"], cols, groups)
            res["shap_group"] = _rank_table("Group", [g["name"] for g in groups], "Mean_abs_SHAP", imp, groups=groups)
        if structures:
            rows_pos = X_test.index.get_indexer(sh["X_rows"].index)
            recs, snotes = structure_records(
                sh["values"], sh["X_rows"], rows_pos, cols, X_train, structures["smiles_train"],
                structures["smiles_test"], structures["names_train"], structures["names_test"],
                structures.get("fp_bits", 2048), structures.get("fp_chirality", True), structures.get("n_show", 12))
            res["structures"] = recs
            res["notes"] += snotes
        _p(base_pct + span * w_shap, "shap")

    if want_perm:
        start = base_pct + span * w_shap
        both = ("individual" in modalities) and (groups is not None)

        def _perm(group_list, slot):
            lo, width = (0.0, 1.0) if not both else ((0.0, 0.5) if slot == 0 else (0.5, 0.5))
            return grouped_permutation_importance(
                model, X_test, y_test, scoring, group_list, n_repeats=n_repeats, seed=seed, n_jobs=n_jobs,
                progress_cb=lambda f, m="": _p(start + span * w_perm * (lo + width * f), "perm"))

        if "individual" in modalities:
            mean, std, base, fb = _perm(singles, 0)
            res["perm_baseline"] = base
            if fb:
                res["notes"].append("scorer_fallback")
            res["perm_individual"] = _rank_table("Feature", cols, "Importance", mean, std)
        if groups is not None:
            mean, std, base, fb = _perm(groups, 1)
            res["perm_baseline"] = base
            if fb and "scorer_fallback" not in res["notes"]:
                res["notes"].append("scorer_fallback")
            res["perm_group"] = _rank_table("Group", [g["name"] for g in groups], "Importance", mean, std, groups=groups)
    _p(1.0, "done")
    return res


# --------------------------------------------------------------------------------------------------
# figures (plain matplotlib Figures - the GUI embeds them in its own canvases)
# --------------------------------------------------------------------------------------------------
def _short(text, n=42):
    text = str(text)
    return text if len(text) <= n else text[: n - 1] + "…"


def _row_labels(df, label_col):
    labels = []
    for _, r in df.iterrows():
        if "Members" in df.columns and int(r.get("N_features", 1)) > 1:
            members = str(r["Members"]).split(";")
            labels.append(_short(f"{r[label_col]} ({len(members)}): {', '.join(members[:2])}…", 52))
        else:
            labels.append(_short(r[label_col], 52))
    return labels


def bar_figure(df, label_col, value_col, err_col, title, xlabel, top_n=20):
    from matplotlib.figure import Figure
    d = df.head(int(top_n)).iloc[::-1]
    fig = Figure(figsize=(9, max(3.5, 0.34 * len(d) + 1.6)))
    ax = fig.add_subplot(111)
    err = d[err_col].to_numpy() if err_col and err_col in d.columns else None
    ax.barh(_row_labels(d, label_col), d[value_col].to_numpy(), xerr=err, color="#4C78A8",
            ecolor="#333333", capsize=2)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.axvline(0, color="#888888", lw=0.8)
    fig.tight_layout()
    return fig


def beeswarm_figure(values, X_rows, columns, title, top_n=20):
    """Own SHAP summary (beeswarm) plot: one row per descriptor, x = SHAP value, colour = descriptor
    value. For binary classifiers the positive class (last) is shown; multiclass is not supported."""
    from matplotlib.figure import Figure
    k = values.shape[0]
    if k > 2:
        return None
    sv = values[-1]
    order = np.argsort(np.abs(sv).mean(axis=0))[::-1][: int(top_n)][::-1]
    fig = Figure(figsize=(9, max(3.8, 0.42 * len(order) + 1.8)))
    ax = fig.add_subplot(111)
    rng = np.random.RandomState(0)
    mappable = None
    for row, j in enumerate(order):
        x = sv[:, j]
        v = X_rows.iloc[:, j].to_numpy(dtype=float)
        lo, hi = np.nanpercentile(v, 5), np.nanpercentile(v, 95)
        if hi <= lo:   # sparse/binary descriptors (e.g. fingerprint bits): percentiles collapse to 0
            lo, hi = np.nanmin(v), np.nanmax(v)
        c = np.zeros_like(v) if hi <= lo else np.clip((v - lo) / (hi - lo), 0, 1)
        bins = np.digitize(x, np.linspace(x.min(), x.max() + 1e-12, 25))
        y = np.zeros_like(x)
        for b in np.unique(bins):
            sel = np.where(bins == b)[0]
            offs = (np.arange(len(sel)) - (len(sel) - 1) / 2.0) * min(0.09, 0.42 / max(1, len(sel)))
            y[sel] = offs[rng.permutation(len(sel))]
        mappable = ax.scatter(x, row + y, c=c, cmap="coolwarm", s=12, vmin=0, vmax=1, linewidths=0, alpha=0.9)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([_short(columns[j], 40) for j in order])
    ax.axvline(0, color="#888888", lw=0.8)
    ax.set_xlabel("SHAP value (impact on model output)")
    ax.set_title(title)
    if mappable is not None:
        cb = fig.colorbar(mappable, ax=ax, pad=0.02)
        cb.set_ticks([0, 1]); cb.set_ticklabels(["low", "high"]); cb.set_label("Descriptor value")
    fig.tight_layout()
    return fig

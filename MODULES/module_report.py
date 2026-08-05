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

"""Final report generator for CODRUG (STEP 7 "Generate Final Report", .docx).

Mirrors the structure of CODOC's MODULES/module_report.py: pulls its data from the unified
per-job JSON (job_dir/<job_name>.json, written incrementally as STEP 1-7 buttons run) plus the
result files each step already writes to disk (CSVs, USI session JSONs, plots). Kept free of
PyQt so it can be unit-tested and reused without a running GUI.

Each of the six report sections (STEP 1, STEP 2, STEP 4, STEP 5, STEP 6, STEP 7) is built
only from what the job's JSON actually recorded as executed - a step nobody ran is skipped
silently rather than shown as "not run", matching the source methodology template's own
instruction (METODOLOGIA_EXEMPLO.docx).
"""

from __future__ import annotations

import glob
import io
import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem.Draw import rdMolDraw2D
except Exception:
    Chem = None
    AllChem = None
    rdMolDraw2D = None

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
    _DOCX_AVAILABLE = True
except Exception:
    _DOCX_AVAILABLE = False

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except Exception:
    _PIL_AVAILABLE = False

COLOR_TITLE_BAR = "BDD6EE"
COLOR_SECTION_BAR = "DAE3F3"
COLOR_ACCENT_BAR = "E2EFDA"


def require_docx() -> None:
    if not _DOCX_AVAILABLE:
        raise RuntimeError("python-docx is not available in the current environment. Install python-docx to generate reports.")


def require_rdkit() -> None:
    if Chem is None or rdMolDraw2D is None:
        raise RuntimeError("RDKit is not available in the current environment. Install RDKit to generate reports.")


# --------------------------------------------------------------------------------------
# Job state loading
# --------------------------------------------------------------------------------------

def load_job_settings(job_dir: str) -> dict[str, Any]:
    """Read the unified per-job JSON (job_dir/<job_name>.json), falling back to the legacy
    STEP-1-only dataset_preparation.json for jobs created before it existed."""
    job_dir = str(job_dir)
    job_name = os.path.basename(os.path.normpath(job_dir))
    for path in (
        os.path.join(job_dir, f"{job_name}.json"),
        os.path.join(job_dir, "dataset_preparation.json"),
    ):
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def _latest_glob(pattern: str) -> Optional[str]:
    matches = glob.glob(pattern)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def _read_csv(path: Optional[str], **kwargs):
    if not path or not os.path.isfile(path):
        return None
    import pandas as pd
    try:
        return pd.read_csv(path, **kwargs)
    except Exception:
        return None


def _row_count(path: Optional[str]) -> Optional[int]:
    df = _read_csv(path)
    return None if df is None else len(df)


# --------------------------------------------------------------------------------------
# 2D structure rendering (ported from CODOC's module_report.molecule_image_bytes)
# --------------------------------------------------------------------------------------

def molecule_image_bytes(smiles: str, size: tuple[int, int] = (220, 160)) -> Optional[io.BytesIO]:
    if Chem is None or rdMolDraw2D is None or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        AllChem.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DCairo(*size)
        drawer.drawOptions().padding = 0.15
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        buffer = io.BytesIO(drawer.GetDrawingText())
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def _composite_2x2_image(paths: list[str], out_path: str) -> Optional[str]:
    """Merges up to 4 existing PNG files into a single 2x2 panel image (top-left, top-right,
    bottom-left, bottom-right), matching the "single figure with 4 components" instructions in
    the methodology template. Silently skipped (returns None) if Pillow is unavailable or fewer
    than 2 usable PNGs are found - SVG-only charts are not converted (no raster conversion
    dependency is assumed to be installed)."""
    if not _PIL_AVAILABLE:
        return None
    pngs = [p for p in paths if p and os.path.isfile(p) and p.lower().endswith(".png")]
    if len(pngs) < 2:
        return None
    try:
        images = [Image.open(p).convert("RGB") for p in pngs[:4]]
        cell_w = max(im.width for im in images)
        cell_h = max(im.height for im in images)
        cols = 2 if len(images) > 1 else 1
        rows = 2 if len(images) > 2 else 1
        canvas = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
        for idx, im in enumerate(images):
            x = (idx % cols) * cell_w
            y = (idx // cols) * cell_h
            canvas.paste(im, (x, y))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return out_path
    except Exception:
        return None


# --------------------------------------------------------------------------------------
# docx helpers (same pattern as CODOC's module_report.py)
# --------------------------------------------------------------------------------------

def _shade_cell(cell: Any, color_hex: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def _set_cell_width(cell: Any, width_cm: float) -> None:
    cell.width = Cm(width_cm)
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(9)


def _content_width_cm(document: Any) -> float:
    section = document.sections[0]
    return (section.page_width - section.left_margin - section.right_margin) / 360000


def _bar(document: Any, text: str, color_hex: str) -> None:
    width = _content_width_cm(document)
    table = document.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    _set_cell_width(cell, width)
    _shade_cell(cell, color_hex)
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = True
    document.add_paragraph().paragraph_format.space_after = Pt(2)


def _field_line(document: Any, label: str, value: Any) -> None:
    if value in (None, "", "None"):
        return
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(0)
    run_label = paragraph.add_run(f"{label}: ")
    run_label.bold = True
    paragraph.add_run(str(value))


def _para(document: Any) -> Any:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return paragraph


def _add(paragraph: Any, text: str, bold: bool = False) -> None:
    if not text:
        return
    run = paragraph.add_run(text)
    run.bold = bold


def _join_bold_list(add: Callable[[str, bool], None], items: list[str]) -> None:
    items = [str(i) for i in items if str(i).strip()]
    for index, item in enumerate(items):
        if index > 0:
            add(", " if index < len(items) - 1 else " and ", False)
        add(item, True)


def _fmt_num(value: Any) -> str:
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def _add_image(document: Any, path: Optional[str], width_cm: float = 14.0) -> bool:
    if not path or not os.path.isfile(path):
        return False
    try:
        document.add_picture(path, width=Cm(width_cm))
        document.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        return True
    except Exception:
        return False


def _add_dataframe_table(document: Any, df, max_rows: int = 15, max_cols: int = 8) -> None:
    if df is None or df.empty:
        return
    cols = list(df.columns)[:max_cols]
    rows = df[cols].head(max_rows)
    width = _content_width_cm(document)
    col_width = width / max(len(cols), 1)
    table = document.add_table(rows=1, cols=len(cols))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for col_idx, name in enumerate(cols):
        cell = table.cell(0, col_idx)
        _set_cell_width(cell, col_width)
        _shade_cell(cell, COLOR_ACCENT_BAR)
        cell.paragraphs[0].add_run(str(name)).bold = True
    for _, record in rows.iterrows():
        cells = table.add_row().cells
        for col_idx, name in enumerate(cols):
            _set_cell_width(cells[col_idx], col_width)
            value = record[name]
            text = f"{value:.4g}" if isinstance(value, float) else str(value)
            cells[col_idx].paragraphs[0].add_run(text)
    document.add_paragraph()


# --------------------------------------------------------------------------------------
# Section 1: STEP 1 - Dataset Preparation
# --------------------------------------------------------------------------------------

def _add_step1_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    step1 = state.get("step1")
    if not isinstance(step1, dict) or not step1:
        return False

    target_chembl_id = step1.get("target_chembl_id", "")
    organism = step1.get("organism_name", "")
    target_type = step1.get("target_type", "")
    assay_type = step1.get("assay_type", "")
    metrics = step1.get("assay_metric_selected", [])
    units = step1.get("assay_unit_selected", [])
    included = step1.get("assay_description_included", "")
    excluded = step1.get("assay_description_excluded", "")

    internal_dir = os.path.join(job_dir, "DATA_BASES", "INTERNAL_DATA")
    initial_path = _latest_glob(os.path.join(internal_dir, f"df1_by_activity_{target_chembl_id}_{organism}*.csv"))
    base_path = _latest_glob(os.path.join(internal_dir, f"df1_base_{target_chembl_id}_{organism}*.csv"))
    initial_count = _row_count(initial_path)
    base_count = _row_count(base_path)

    _bar(document, "STEP 1 - DATASET PREPARATION", COLOR_SECTION_BAR)
    p = _para(document)

    def add(text: str, bold: bool = False) -> None:
        _add(p, text, bold)

    add("The internal dataset used to screen the supervised machine learning models was built from the ", False)
    add("ChEMBL", True)
    add(" database via the chembl_webresource_client Python library. The Target Type selected was ", False)
    add(target_type or "n/a", True)
    add(" and, for Organism name, the term ", False)
    add(organism or "n/a", True)
    add(". Using Target ChEMBL ID ", False)
    add(target_chembl_id or "n/a", True)
    if initial_count is not None:
        add(", a dataframe was obtained containing ", False)
        add(f"{initial_count:,}", True)
        add(" compounds with experimental bioactivity data. ", False)
    else:
        add(". ", False)
    add("This initial dataframe was filtered by Assay Type ", False)
    add(assay_type or "n/a", True)
    if metrics:
        add(", Assay Metric ", False)
        _join_bold_list(add, metrics)
    if units:
        add(", Assay Unit ", False)
        _join_bold_list(add, units)
    add(". ", False)
    if included or excluded:
        add("Assay description was used for careful curation of the assay data, allowing the selection of the inclusion terms ", False)
        if included:
            add(included, True)
        if excluded:
            add(", and the exclusion terms ", False)
            add(excluded, True)
        add(". ", False)
    else:
        add(
            "No assay description filtering term (inclusion or exclusion) was applied, since it would imply a "
            "significant reduction in the data, which at this initial stage may already be considered scarce. ",
            False,
        )
    if base_count is not None:
        add("At the end of this stage the original dataframe was reduced to ", False)
        add(f"{base_count:,}", True)
        add(" compounds.", False)

    _field_line(document, "Cell line", step1.get("cell_name", ""))
    _field_line(document, "Cell ChEMBL ID", step1.get("cell_chembl_id", ""))
    document.add_paragraph()
    return True


# --------------------------------------------------------------------------------------
# Section 2: STEP 2 - Preprocessing and Exploratory Analysis (includes Generating
# Categories/Druggability Descriptors, moved here from the former STEP 3)
# --------------------------------------------------------------------------------------

def _add_step2_3_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    step2 = state.get("step2") if isinstance(state.get("step2"), dict) else {}
    if not step2:
        return False

    stats_dir = os.path.join(job_dir, "RESULTS", "STATISTICS")
    internal_dir = os.path.join(job_dir, "DATA_BASES", "INTERNAL_DATA")

    unit_col = step2.get("type_column") or step2.get("unit_column") or ""
    metric_col = step2.get("stat_column") or unit_col

    _bar(document, "STEP 2 - Preprocessing and Exploratory Analysis", COLOR_SECTION_BAR)
    p = _para(document)

    def add(text: str, bold: bool = False) -> None:
        _add(p, text, bold)

    unit_count = _row_count(_latest_glob(os.path.join(internal_dir, "df2_unit_*.csv")))
    rep_count = _row_count(_latest_glob(os.path.join(internal_dir, "df2_TratRepetitions_*.csv")))

    if unit_col:
        add("The bioactivity values were standardized to a common unit/type (", False)
        add(unit_col, True)
        add(")", False)
        if unit_count is not None:
            add(f", resulting in {unit_count:,} compounds", False)
        add(". ", False)
    rep_method = step2.get("rep_method", "")
    if rep_method:
        add("Duplicate compounds were consolidated using the ", False)
        add(rep_method, True)
        add(" method")
        if rep_count is not None:
            add(f", reducing the dataframe to {rep_count:,} unique compounds", False)
        add(". ", False)

    transforms = [
        label for key, label in (
            ("transform_log10", "-log10"),
            ("transform_ln", "ln"),
            ("transform_sqrt", "sqrt"),
            ("transform_cbrt", "cbrt"),
            ("transform_boxcox", "Box-Cox"),
            ("transform_yeojohnson", "Yeo-Johnson"),
        ) if step2.get(key)
    ]
    if transforms:
        add("The bioactivity value was transformed using ", False)
        _join_bold_list(add, transforms)
        add(". ", False)

    normal_tests = [
        label for key, label in (
            ("normal_test_shapiro", "Shapiro-Wilk"),
            ("normal_test_anderson", "Anderson-Darling"),
            ("normal_test_kolmogorov", "Kolmogorov-Smirnov"),
        ) if step2.get(key)
    ]
    if normal_tests:
        add("Normality was assessed with the ", False)
        _join_bold_list(add, normal_tests)
        add(" test(s). ", False)

    outlier_methods = [
        label for key, label in (
            ("outlier_zscore", "Z-Score"),
            ("outlier_iqr", "IQR"),
            ("outlier_sd", "Standard Deviation"),
        ) if step2.get(key)
    ]
    outlier_threshold = step2.get("outlier_threshold")
    if outlier_methods:
        add("Outlier detection was performed with the ", False)
        _join_bold_list(add, outlier_methods)
        add(" method(s)", False)
        if outlier_threshold:
            add(f", using a threshold of {outlier_threshold}", False)
        for method_key, csv_tag in (("outlier_zscore", "Z"), ("outlier_iqr", "IQR"), ("outlier_sd", "SD")):
            if step2.get(method_key):
                out_count = _row_count(_latest_glob(os.path.join(internal_dir, f"df2_TratOutliers_{csv_tag}_*.csv")))
                if out_count is not None:
                    add(f" ({csv_tag}: {out_count:,} compounds retained)", False)
        add(". ", False)

    class_value_col = step2.get("class_value_column") or metric_col or "value"
    class_rules = []
    class1_name, class1_op, class1_ref = step2.get("class1_name"), step2.get("class1_operator"), step2.get("class1_reference")
    if class1_name and class1_op and class1_ref:
        class_rules.append((class1_name, f"if {class_value_col} {class1_op} {class1_ref}"))
    class2_name, class2_min, class2_max = step2.get("class2_name"), step2.get("class2_min"), step2.get("class2_max")
    if class2_name and class2_min and class2_max:
        class_rules.append((class2_name, f"if {class_value_col} between {class2_min} and {class2_max}"))
    class3_name, class3_op, class3_ref = step2.get("class3_name"), step2.get("class3_operator"), step2.get("class3_reference")
    if class3_name and class3_op and class3_ref:
        class_rules.append((class3_name, f"if {class_value_col} {class3_op} {class3_ref}"))
    if class_rules:
        add("Compounds were categorized as ", False)
        _join_bold_list(add, [name for name, _ in class_rules])
        add(" (", False)
        for index, (name, rule) in enumerate(class_rules):
            if index > 0:
                add("; ", False)
            add(f"{name} {rule}", True)
        add("); compounds matching none of these rules were left unclassified. ", False)

    druggability_pairs = [
        ("druggability_mw", "MW", "druggability_mw_min", "druggability_mw_max"),
        ("druggability_logp", "LogP", "druggability_logp_min", "druggability_logp_max"),
        ("druggability_hdonor", "H-Donors", "druggability_hdonor_min", "druggability_hdonor_max"),
        ("druggability_haceptor", "H-Acceptors", "druggability_haceptor_min", "druggability_haceptor_max"),
        ("druggability_tpsa", "TPSA", "druggability_tpsa_min", "druggability_tpsa_max"),
        ("druggability_rbonds", "Rotatable Bonds", "druggability_rbonds_min", "druggability_rbonds_max"),
        ("druggability_ro5", "RO5 Violations", "druggability_ro5_min", "druggability_ro5_max"),
    ]
    active_ranges = [
        f"{label} ({step2.get(min_k)} to {step2.get(max_k)})"
        for flag_k, label, min_k, max_k in druggability_pairs
        if step2.get(flag_k)
    ]
    if active_ranges:
        add("Druggability descriptors were computed and filtered by ", False)
        add(", ".join(active_ranges), True)
        add(". ", False)

    document.add_paragraph()

    # Composite histogram/boxplot figure, if canonical PNGs are already on disk.
    candidates = []
    if metric_col:
        candidates += [
            os.path.join(stats_dir, f"histogram_{metric_col}.png"),
            os.path.join(stats_dir, "histogram_-log10.png"),
            os.path.join(stats_dir, f"boxplot_{metric_col}.png"),
            os.path.join(stats_dir, "boxplot_-log10.png"),
        ]
    composite_path = _composite_2x2_image(candidates, os.path.join(stats_dir, "_report_step2_distributions.png"))
    if composite_path:
        _add_image(document, composite_path)

    outlier_report = _latest_glob(os.path.join(stats_dir, "*_Outliers_Removal_Report.txt"))
    if outlier_report and os.path.isfile(outlier_report):
        try:
            text = Path(outlier_report).read_text(encoding="utf-8", errors="ignore")
            _field_line(document, "Outlier removal report", os.path.basename(outlier_report))
            for line in text.splitlines()[:12]:
                if line.strip():
                    document.add_paragraph(line, style=None)
        except OSError:
            pass

    document.add_paragraph()
    return True


# --------------------------------------------------------------------------------------
# Section 3: STEP 4 - Features Engineering
# --------------------------------------------------------------------------------------

def _add_step4_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    step4 = state.get("step4")
    if not isinstance(step4, dict) or not step4:
        return False

    scaling_method = step4.get("last_scaling_method")
    selection_method = step4.get("last_selection_method")
    projection_method = step4.get("last_projection_method")
    if not (scaling_method or selection_method or projection_method):
        return False

    _bar(document, "STEP 4 - Features Engineering", COLOR_SECTION_BAR)
    p = _para(document)

    def add(text: str, bold: bool = False) -> None:
        _add(p, text, bold)

    descriptors = step4.get("descriptors_selected")
    if isinstance(descriptors, dict) and descriptors.get("selected"):
        add("Molecular descriptors were generated using PaDELPy for ", False)
        _join_bold_list(add, descriptors["selected"])
        add(". ", False)

    if scaling_method:
        add("Feature scaling was performed using the ", False)
        add(scaling_method, True)
        add(" method. ", False)

    if selection_method:
        selection_count = _row_count(step4.get("last_selection_file"))
        add("Feature selection was performed using the ", False)
        add(selection_method, True)
        add(" method", False)
        if selection_count is not None:
            add(f", resulting in {selection_count:,} compounds with the selected feature set", False)
        add(". ", False)

    if projection_method:
        n_comp = step4.get("projection_n_components")
        add("Latent variable projection was performed using ", False)
        add(projection_method, True)
        if n_comp:
            add(f" with {n_comp} components", False)
        add(". ", False)

    # External dataset column-count note (paragraph 38 of the methodology template).
    ext_dir = os.path.join(job_dir, "DATA_BASES", "EXTERNAL_DATA")
    selection_path = step4.get("last_selection_file")
    if selection_path and os.path.isfile(selection_path):
        for ext_path in sorted(glob.glob(os.path.join(ext_dir, "df_external_descriptors_*.csv"))):
            ext_df = _read_csv(ext_path, nrows=1)
            sel_df = _read_csv(selection_path, nrows=1)
            if ext_df is None or sel_df is None:
                continue
            diff = len(set(ext_df.columns).symmetric_difference(set(sel_df.columns)))
            add(
                f" The external dataframe {os.path.basename(ext_path)} presented {diff} different "
                f"columns relative to the internal dataframe {os.path.basename(selection_path)}, as expected; "
                "these columns were ignored when applying the best models for bioactivity prediction.",
                False,
            )

    document.add_paragraph()
    return True


# --------------------------------------------------------------------------------------
# Section 4: STEP 5 - Machine Learning Models (Scikit-learn)
# --------------------------------------------------------------------------------------

def _add_step5_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    step6 = state.get("step6_sklearn") if isinstance(state.get("step6_sklearn"), dict) else {}
    if not step6:
        return False

    _bar(document, "STEP 5 - Machine Learning Models: Screening, Tuning, Validation and Application", COLOR_SECTION_BAR)

    added_any = False
    usi_root = os.path.join(job_dir, "RESULTS", "USI")

    skl_usi = step6.get("current_usi")
    if skl_usi:
        session_path = os.path.join(usi_root, skl_usi, "skl_session.json")
        session = {}
        if os.path.isfile(session_path):
            try:
                session = json.loads(Path(session_path).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                session = {}
        screening = session.get("screening_settings", {})
        models = session.get("models", [])
        best_model = session.get("best_model")
        p = _para(document)

        def add(text: str, bold: bool = False) -> None:
            _add(p, text, bold)

        add("Model screening (Scikit-learn) was performed with the following estimators: ", False)
        if models:
            _join_bold_list(add, models)
        add(". ", False)
        if screening.get("sort_metric"):
            add("Models were ranked by ", False)
            add(str(screening["sort_metric"]), True)
            add(". ", False)
        if screening.get("test_size"):
            test_size = float(screening["test_size"])
            add(f"The test set represented {test_size * 100:.0f}% and the training set {100 - test_size * 100:.0f}% of the data. ", False)
        if best_model:
            add("The best performing model was ", False)
            add(str(best_model), True)
            add(". ", False)

        screening_csv = _latest_glob(os.path.join(usi_root, skl_usi, "DATA", "skl_screening_*.csv"))
        _add_dataframe_table(document, _read_csv(screening_csv))

        tuning_settings = session.get("tuning_settings", {})
        if tuning_settings:
            tuned_models = ", ".join(tuning_settings.keys())
            document.add_paragraph().add_run(f"Hyperparameter tuning was applied to: {tuned_models}.").bold = False
            tune_csv = _latest_glob(os.path.join(usi_root, skl_usi, "DATA", "skl_tune_*.csv"))
            _add_dataframe_table(document, _read_csv(tune_csv))

        validation_settings = session.get("validation_settings", {})
        for model_name, settings in validation_settings.items():
            method = settings.get("method", "")
            folds = settings.get("folds", "")
            document.add_paragraph().add_run(
                f"Cross-validation of {model_name} was performed using {method} with {folds} folds."
            ).bold = False
            cv_csv = _latest_glob(os.path.join(usi_root, skl_usi, "DATA", f"skl_cv_{model_name}_*.csv"))
            _add_dataframe_table(document, _read_csv(cv_csv))
        added_any = True

    document.add_paragraph()
    return added_any


# --------------------------------------------------------------------------------------
# Section 5: STEP 6 - Applicability Domain and Similarity Analysis
# --------------------------------------------------------------------------------------

def _add_step7_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    step7 = state.get("step7_ad")
    if not isinstance(step7, dict) or not step7:
        return False

    _bar(document, "STEP 6 - Applicability Domain and Similarity Analysis", COLOR_SECTION_BAR)
    p = _para(document)

    def add(text: str, bold: bool = False) -> None:
        _add(p, text, bold)

    add(
        "The applicability domain (AD) was assessed using the Hat/leverage (Williams plot) technique, "
        "complemented by the Mahalanobis distance, a k-nearest-neighbors (KNN) distance check and Tanimoto "
        "structural similarity to the training set. ",
        False,
    )

    result_path = step7.get("result_csv")
    result_df = _read_csv(result_path)
    if result_df is not None and not result_df.empty:
        cutoff_cols = {
            "leverage_cut": "leverage (h*)",
            "mahal_cut": "Mahalanobis",
            "knn_cut": "KNN",
            "tanimoto_cut": "Tanimoto",
        }
        cutoffs = []
        for col, label in cutoff_cols.items():
            if col in result_df.columns:
                cutoffs.append(f"{label} (cut-off = {_fmt_num(result_df[col].iloc[0])})")
        if cutoffs:
            add("The analysis used the following cut-offs: ", False)
            add(", ".join(cutoffs), True)
            add(". ", False)

    verdict_counts = step7.get("verdict_counts", {})
    if verdict_counts:
        add("The applicability domain / similarity verdict distribution was: ", False)
        add(", ".join(f"{k}: {v}" for k, v in verdict_counts.items()), True)
        add(". Compounds verdicted Outside AD were removed from the external dataframe before the consensus analysis step.", False)

    document.add_paragraph()

    midia_dir = os.path.join(job_dir, "RESULTS", "MIDIA")
    ext_base = None
    if result_path:
        ext_base = os.path.basename(result_path)
    candidates = sorted(glob.glob(os.path.join(midia_dir, "Plot_williams_*.png"))) + \
        sorted(glob.glob(os.path.join(midia_dir, "Plot_mahalanobis_*.png"))) + \
        sorted(glob.glob(os.path.join(midia_dir, "Plot_pca_scatter_*.png"))) + \
        sorted(glob.glob(os.path.join(midia_dir, "Plot_tanimoto_*.png")))
    picks = []
    for prefix in ("Plot_williams_", "Plot_mahalanobis_", "Plot_pca_scatter_", "Plot_tanimoto_"):
        matches = sorted(glob.glob(os.path.join(midia_dir, f"{prefix}*.png")), key=os.path.getmtime, reverse=True)
        if matches:
            picks.append(matches[0])
    composite_path = _composite_2x2_image(picks, os.path.join(midia_dir, "_report_step7_ad.png"))
    if composite_path:
        _add_image(document, composite_path)

    document.add_paragraph()
    return True


# --------------------------------------------------------------------------------------
# Section 6: STEP 7 - Consensus Analysis
# --------------------------------------------------------------------------------------

def _find_smiles_lookup(job_dir: str, ids: set[str]) -> dict[str, str]:
    """Best-effort ID -> SMILES lookup, scanning prediction CSVs under RESULTS/USI/**/PREDICTIONS
    (which carry Name/SMILES columns) for the small set of IDs the consensus hits table needs."""
    lookup: dict[str, str] = {}
    if not ids:
        return lookup
    pattern = os.path.join(job_dir, "RESULTS", "USI", "*", "PREDICTIONS", "*.csv")
    for path in glob.glob(pattern):
        if len(lookup) >= len(ids):
            break
        df = _read_csv(path)
        if df is None:
            continue
        id_col = next((c for c in ("Name", "name", "molecule_chembl_id", "ID", "id") if c in df.columns), None)
        smiles_col = next((c for c in ("SMILES", "smiles", "canonical_smiles") if c in df.columns), None)
        if not id_col or not smiles_col:
            continue
        for _, row in df[[id_col, smiles_col]].iterrows():
            key = str(row[id_col])
            if key in ids and key not in lookup:
                lookup[key] = str(row[smiles_col])
    return lookup


def _add_step8_section(document: Any, job_dir: str, state: dict[str, Any]) -> bool:
    """Reads the "hits" CSV that STEP 7 itself already computed (df_consensus_hits_*.csv,
    referenced by step8_consensus.last_hits_file) rather than re-deriving the CV%/Hit% filter
    here - CODRUG.run_consensus_generate is the single source of truth for that logic, so the
    report can never drift out of sync with what the UI actually shows/saves."""
    step8 = state.get("step8_consensus")
    if not isinstance(step8, dict) or not step8:
        return False

    hits_path = step8.get("last_hits_file")
    if hits_path and os.path.isfile(hits_path):
        hits = _read_csv(hits_path)
    else:
        # Fall back to the full result only for older jobs saved before the hits CSV existed -
        # an existing hits file with 0 rows is a legitimate "no compound passed the filter"
        # outcome and must NOT fall back to the unfiltered table.
        hits = _read_csv(step8.get("last_result_file"))
    if hits is None or hits.empty:
        return False

    method = step8.get("consensus_method", "Z-Score (Mean/SD)")
    cv_max = step8.get("cv_max_percent")
    hit_percent = step8.get("hit_percent")

    _bar(document, "STEP 7 - Consensus Analysis", COLOR_SECTION_BAR)
    p = _para(document)

    def add(text: str, bold: bool = False) -> None:
        _add(p, text, bold)

    add(
        "The ranked list of the most promising compounds, in decreasing order of predicted bioactivity, was "
        "combined via consensus analysis using the ", False,
    )
    add(str(method), True)
    add(" method", False)
    if cv_max:
        add(", retaining only compounds with a coefficient of variation between models <= ", False)
        add(f"{cv_max}%", True)
    if hit_percent:
        add(f". This produced the top {hit_percent}% hits", False)
    add(f" ({len(hits)} compound(s)), listed below with their 2D structures.", False)
    document.add_paragraph()

    id_col = hits.columns[0]
    score_col = "consensus_score_mean" if "consensus_score_mean" in hits.columns else "zscore_consensus_mean"
    smiles_lookup = _find_smiles_lookup(job_dir, set(hits[id_col].astype(str)))

    width = _content_width_cm(document)
    col_widths = [width * 0.20, width * 0.30, width * 0.20, width * 0.15, width * 0.15]
    headers = ["Compound", "2D Structure", "Consensus Rank", "Consensus Score (mean)", "CV%"]
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for col, (header, col_w) in enumerate(zip(headers, col_widths)):
        cell = table.cell(0, col)
        _set_cell_width(cell, col_w)
        _shade_cell(cell, COLOR_ACCENT_BAR)
        cell.paragraphs[0].add_run(header).bold = True

    for _, record in hits.iterrows():
        compound_id = str(record[id_col])
        cells = table.add_row().cells
        _set_cell_width(cells[0], col_widths[0])
        cells[0].paragraphs[0].add_run(compound_id)
        _set_cell_width(cells[1], col_widths[1])
        smiles = smiles_lookup.get(compound_id, "")
        image = molecule_image_bytes(smiles) if smiles else None
        if image is not None:
            cells[1].paragraphs[0].add_run().add_picture(image, width=Cm(col_widths[1] - 0.6))
        else:
            cells[1].paragraphs[0].add_run("N/A")
        _set_cell_width(cells[2], col_widths[2])
        cells[2].paragraphs[0].add_run(_fmt_num(record.get("consensus_rank", "")))
        _set_cell_width(cells[3], col_widths[3])
        cells[3].paragraphs[0].add_run(_fmt_num(record.get(score_col, "")))
        _set_cell_width(cells[4], col_widths[4])
        cells[4].paragraphs[0].add_run(_fmt_num(record.get("bioactivity_cv_percent", "")))

    document.add_paragraph()
    return True


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------

def generate_final_report(
    job_dir: str,
    job_name: str,
    state: Optional[dict[str, Any]] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Build <job_dir>/RESULTS/<job_name>_REPORT.docx from the job's unified state JSON
    (job_dir/<job_name>.json) and the result files each STEP already writes to disk. Returns
    the output path. Raises RuntimeError if no section had any recorded state at all."""
    require_docx()

    def report(text: str) -> None:
        if progress_callback is not None:
            progress_callback(text)

    state = state if state is not None else load_job_settings(job_dir)
    if not isinstance(state, dict):
        state = {}

    document = Document()
    section = document.sections[0]
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)
    document.styles["Normal"].font.name = "Calibri"
    document.styles["Normal"].font.size = Pt(10)

    _bar(document, "CODRUG REPORT", COLOR_TITLE_BAR)
    _field_line(document, "Job Name", job_name)
    _field_line(document, "Task Type", state.get("task_type", ""))
    _field_line(document, "Generated", state.get("saved_at", ""))
    document.add_paragraph()

    report("Building STEP 1 - Dataset Preparation...")
    added_1 = _add_step1_section(document, job_dir, state)
    report("Building STEP 2 - Preprocessing and Exploratory Analysis...")
    added_23 = _add_step2_3_section(document, job_dir, state)
    report("Building STEP 4 - Features Engineering...")
    added_4 = _add_step4_section(document, job_dir, state)
    report("Building STEP 5 - Machine Learning Models...")
    added_5 = _add_step5_section(document, job_dir, state)
    report("Building STEP 6 - Applicability Domain and Similarity Analysis...")
    added_7 = _add_step7_section(document, job_dir, state)
    report("Building STEP 7 - Consensus Analysis...")
    added_8 = _add_step8_section(document, job_dir, state)

    if not any((added_1, added_23, added_4, added_5, added_7, added_8)):
        raise RuntimeError(
            "No recorded state was found for this job. Run at least one STEP (Generate Base "
            "Dataset, Outlier Elimination, Compute AD, Consensus Generate, etc.) before "
            "generating the final report."
        )

    results_dir = os.path.join(job_dir, "RESULTS")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, f"{job_name}_REPORT.docx")
    report(f"Saving {output_path} ...")
    document.save(output_path)
    return output_path

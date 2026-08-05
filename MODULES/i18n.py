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

"""Interface texts in English / Brazilian Portuguese for CODRUG.

Mirrors the pattern used by AgendaLab's i18n.py: a flat dict of {key: {"en": ..., "pt": ...}}
plus a single t(key, idioma, **kwargs) lookup. CODRUG's UI was originally written entirely in
English, so "en" values are always the original, unmodified text (switching to English can never
change existing behavior/wording) and "pt" values are the added translation.

t() falls back to returning the key itself when a key has no entry yet (or no entry for the
requested language) - this lets the interface be translated incrementally, tab by tab, without
ever crashing or showing a blank string for text that hasn't been ported to i18n.t(...) yet.
"""

IDIOMA_PADRAO = "en"

_TEXTOS = {
    # ---------------------------------------------------------------- Main window chrome
    "app_titulo": {
        "en": "CODRUG - An Open-Source Automated QSAR Analysis Tool",
        "pt": "CODRUG - Uma Ferramenta Automatizada e de Código Aberto para Análise QSAR",
    },
    "tooltip_bandeira_pt": {"en": "Português", "pt": "Português"},
    "tooltip_bandeira_en": {"en": "English", "pt": "English"},
    "btn_cpu_gpu_monitor": {"en": "CPU/GPU Monitor", "pt": "Monitor de CPU/GPU"},
    "tooltip_cpu_gpu_monitor": {
        "en": "Open a separate CPU/GPU monitor window that keeps updating even while the main "
              "window is busy running a heavy STEP 5 task.",
        "pt": "Abre uma janela separada de monitor de CPU/GPU que continua atualizando mesmo "
              "quando a janela principal estiver ocupada rodando uma tarefa pesada da STEP 5.",
    },

    # ---------------------------------------------------------------- Tab names
    "tab_home": {"en": "HOME", "pt": "INÍCIO"},
    "tab_config": {"en": "CONFIG", "pt": "CONFIG"},
    "tab_step1": {"en": "STEP 1", "pt": "ETAPA 1"},
    "tab_step2": {"en": "STEP 2", "pt": "ETAPA 2"},
    "tab_step4": {"en": "STEP 3", "pt": "ETAPA 3"},
    "tab_step5": {"en": "STEP 4", "pt": "ETAPA 4"},
    "tab_step6": {"en": "STEP 5", "pt": "ETAPA 5"},
    "tab_step7": {"en": "STEP 6", "pt": "ETAPA 6"},
    "tab_edit": {"en": "EDIT", "pt": "EDIT"},
    "tab_statistics": {"en": "STATS", "pt": "STATS"},

    # ---------------------------------------------------------------- HOME tab
    "home_tagline1": {
        "en": "Computational Drug Discovery Platform",
        "pt": "Plataforma Computacional de Descoberta de Fármacos",
    },
    "home_tagline2": {
        "en": "QSAR with Machine Learning Models",
        "pt": "QSAR com Modelos de Aprendizado de Máquina",
    },
    "home_grp_cpu": {"en": "Hardware Specs — CPU", "pt": "Especificações de Hardware — CPU"},
    "home_grp_gpu": {"en": "Hardware Specs — GPU", "pt": "Especificações de Hardware — GPU"},
    "home_grp_sw": {"en": "Software Specs", "pt": "Especificações de Software"},
    "home_grp_pipeline": {"en": "Pipeline — Steps", "pt": "Pipeline — Etapas"},
    "home_step0_name": {"en": "Configuration", "pt": "Configuração"},
    "home_step0_desc": {
        "en": "Project setup, environment and job folder preparation",
        "pt": "Configuração do projeto, ambiente e preparação da pasta do job",
    },
    "home_step1_name": {"en": "Step 1 — Dataset Preparation", "pt": "Etapa 1 — Preparação do Dataset"},
    "home_step1_desc": {
        "en": "Target, assay and bioactivity dataset construction from source data",
        "pt": "Construção do dataset de alvo, ensaio e bioatividade a partir dos dados de origem",
    },
    "home_step2_name": {"en": "Step 2 — Exploratory Analysis", "pt": "Etapa 2 — Análise Exploratória"},
    "home_step2_desc": {
        "en": "Cleaning, type conversion, visualization, distribution analysis, class categorization and druggability descriptor filtering",
        "pt": "Limpeza, conversão de tipos, visualização, análise de distribuição, categorização de classes e filtragem de descritores de drogabilidade",
    },
    "home_step3_name": {"en": "Step 3 — Feature Engineering", "pt": "Etapa 3 — Engenharia de Atributos"},
    "home_step3_desc": {
        "en": "Descriptor generation, structural processing and feature preparation",
        "pt": "Geração de descritores, processamento estrutural e preparação de atributos",
    },
    "home_step4_name": {"en": "Step 4 — Machine Learning", "pt": "Etapa 4 — Aprendizado de Máquina"},
    "home_step4_desc": {
        "en": "Scikit-learn setup, screening, tuning, saving and prediction workflows",
        "pt": "Fluxos de configuração, seleção, ajuste, salvamento e predição com Scikit-learn",
    },
    "home_step5_name": {"en": "Step 5 — Applicability Domain", "pt": "Etapa 5 — Domínio de Aplicabilidade"},
    "home_step5_desc": {
        "en": "Leverage, Mahalanobis distance and similarity-based domain assessment",
        "pt": "Avaliação de domínio por leverage, distância de Mahalanobis e similaridade",
    },
    "home_step6_name": {"en": "Step 6 — Consensus Analysis", "pt": "Etapa 6 — Análise de Consenso"},
    "home_step6_desc": {
        "en": "Consensus ranking with z-score integration, median-rank validation and Spearman concordance",
        "pt": "Ranqueamento por consenso com integração de z-score, validação por mediana de rank e concordância de Spearman",
    },
    "home_btn_start": {"en": "Start", "pt": "Iniciar"},
    "home_btn_install": {"en": "Install Requirements", "pt": "Instalar Dependências"},
    "msg_attention": {"en": "Attention", "pt": "Atenção"},
    "msg_home_build_error": {
        "en": "There was an error building the HOME TAB.\n\nDetails: {exc}",
        "pt": "Ocorreu um erro ao construir a aba HOME.\n\nDetalhes: {exc}",
    },

    # ---------------------------------------------------------------- Section titles (_mk_title)
    "title_project_settings": {"en": "Project Settings:", "pt": "Configurações do Projeto:"},
    "title_step1": {"en": "Dataset Preparation", "pt": "Preparação do Dataset"},
    "title_step2": {
        "en": "Data Preprocessing",
        "pt": "Pré-processamento dos Dados",
    },
    "title_step4": {"en": "Features Engineering", "pt": "Engenharia de Atributos"},
    "title_step5": {
        "en": "Machine Learning Models: Screening, Tuning, Validation and Application (Scikit-learn)",
        "pt": "Modelos de Aprendizado de Máquina: Seleção, Ajuste, Validação e Aplicação (Scikit-learn)",
    },
    "title_step6": {
        "en": "Applicability Domain and Similarity Analysis",
        "pt": "Domínio de Aplicabilidade e Análise de Similaridade",
    },
    "title_step7": {"en": "Consensus Analysis", "pt": "Análise de Consenso"},
    "title_edit": {"en": "Manipulate Dataframes", "pt": "Manipular Dataframes"},
    "title_statistics": {"en": "Statistical Tests", "pt": "Testes Estatísticos"},

    # ---------------------------------------------------------------- CONFIG tab
    "cfg_choose_task": {"en": "1. Choose the Task Type:", "pt": "1. Escolha o Tipo de Tarefa:"},
    "cfg_supervised": {"en": "Supervised:", "pt": "Supervisionado:"},
    "cfg_supervised_sub": {"en": "(with labels)", "pt": "(com rótulos)"},
    "cfg_unsupervised": {"en": "Unsupervised:", "pt": "Não Supervisionado:"},
    "cfg_unsupervised_sub": {"en": "(without labels)", "pt": "(sem rótulos)"},
    "cfg_logo_not_found": {"en": "Logo not found", "pt": "Logo não encontrado"},
    "cfg_task_desc_placeholder": {"en": " Concept ", "pt": " Conceito "},
    "cfg_task_desc_class": {
        "en": "Predicts categorical labels of instances based on their features.",
        "pt": "Prediz rótulos categóricos de instâncias com base em seus atributos.",
    },
    "cfg_task_desc_regress": {
        "en": "Predicts continuous labels of instances by quantifying their relationship to the features.",
        "pt": "Prediz rótulos contínuos de instâncias quantificando sua relação com os atributos.",
    },
    "cfg_task_desc_clust": {
        "en": "Automatically groups data without prior labels to uncover hidden patterns of similarity.",
        "pt": "Agrupa dados automaticamente, sem rótulos prévios, para revelar padrões ocultos de similaridade.",
    },
    "cfg_generate_project": {"en": "2. Generate Project:", "pt": "2. Gerar Projeto:"},
    "cfg_btn_new_project": {"en": "New Project", "pt": "Novo Projeto"},
    "cfg_label_date": {"en": "Date:", "pt": "Data:"},
    "cfg_label_job_name": {"en": "Job Name:", "pt": "Nome do Job:"},
    "cfg_placeholder_job_name": {
        "en": "Put here the new project name",
        "pt": "Coloque aqui o nome do novo projeto",
    },
    "cfg_btn_previous_project": {"en": "Previous Project", "pt": "Projeto Anterior"},
    "cfg_label_previous_run": {"en": "Select previous run:", "pt": "Selecione uma execução anterior:"},
    "cfg_placeholder_previous_run": {"en": "Select a previous run", "pt": "Selecione uma execução anterior"},
    "cfg_btn_set_run_folder": {"en": "Set run folder", "pt": "Definir pasta de execução"},
    "btn_back": {"en": " << BACK ", "pt": " << VOLTAR "},
    "btn_next": {"en": " NEXT >> ", "pt": " AVANÇAR >> "},
    "msg_cfg_build_error": {
        "en": "There was an error building the CONFIGURATION TAB",
        "pt": "Ocorreu um erro ao construir a aba de CONFIGURAÇÃO",
    },
    "cfg_no_folder_found": {"en": "No folder found", "pt": "Nenhuma pasta encontrada"},
    "msg_task_type_required_title": {"en": "Task Type Required", "pt": "Tipo de Tarefa Obrigatório"},
    "msg_task_type_required_body": {
        "en": "Please choose one of the Task Type options: Classification, Regression, or Clustering.",
        "pt": "Escolha uma das opções de Tipo de Tarefa: Classificação, Regressão ou Clusterização.",
    },
    "msg_job_load_error": {
        "en": "Could not load saved job settings from the selected job.\n\nDetails:\n{e}",
        "pt": "Não foi possível carregar as configurações salvas do job selecionado.\n\nDetalhes:\n{e}",
    },

    # ---------------------------------------------------------------- Shared / general dialogs
    "msg_wait": {"en": "Wait", "pt": "Aguarde"},
    "msg_processing": {
        "en": "It's being processed... Please wait for it to finish!",
        "pt": "Processando... Aguarde até que termine!",
    },
    "msg_checking_chembl": {
        "en": "Checking the status of the CHEMBL database!",
        "pt": "Verificando o status do banco de dados CHEMBL!",
    },
    "msg_chembl_unavailable_title": {"en": "ChEMBL Unavailable", "pt": "ChEMBL Indisponível"},
    "msg_chembl_unavailable_body": {
        "en": "The ChEMBL server (EBI) is currently unavailable.\n"
              "Check status at: https://chembl.github.io/status/\n"
              "Please try again in a few minutes.",
        "pt": "O servidor do ChEMBL (EBI) está indisponível no momento.\n"
              "Verifique o status em: https://chembl.github.io/status/\n"
              "Tente novamente em alguns minutos.",
    },

    # ---------------------------------------------------------------- STEP 1 (Dataset Preparation)
    "s1_btn_search_local": {"en": "Search Local Data", "pt": "Buscar Dados Locais"},
    "s1_btn_use_chembl": {"en": "Use ChEMBL Data", "pt": "Usar Dados do ChEMBL"},
    "s1_lbl_target_type": {"en": "Target Type:", "pt": "Tipo de Alvo:"},
    "s1_lbl_organism_name": {"en": "Organism Name:", "pt": "Nome do Organismo:"},
    "s1_lbl_pref_name": {"en": "Pref. Name:", "pt": "Nome Preferencial:"},
    "s1_lbl_target_chembl_id": {"en": "Target ChEMBL ID:", "pt": "Target ChEMBL ID:"},
    "s1_btn_explore_target": {"en": "Explore by target", "pt": "Explorar por alvo"},
    "s1_btn_generate_by_activity": {"en": "Generate Dataset by activity", "pt": "Gerar Dataset por atividade"},
    "s1_chk_web_scraping": {"en": "Web Scraping", "pt": "Web Scraping"},
    "s1_tooltip_web_scraping": {
        "en": "When checked, 'Generate Dataset by activity' downloads the data by scraping "
              "the ChEMBL explore website (same CSV export used by its 'CSV' button) instead "
              "of querying the chembl_webresource_client API.",
        "pt": "Quando marcado, 'Gerar Dataset por atividade' baixa os dados fazendo scraping "
              "do site de exploração do ChEMBL (mesmo CSV exportado pelo botão 'CSV' do site) "
              "em vez de consultar a API chembl_webresource_client.",
    },
    "s1_btn_explore_cell": {"en": "Explore by Cell-line", "pt": "Explorar por linhagem celular"},
    "s1_lbl_assay_type": {"en": "Assay Type:", "pt": "Tipo de Ensaio:"},
    "s1_lbl_assay_metric": {"en": "Assay Metric:", "pt": "Métrica do Ensaio:"},
    "s1_lbl_assay_unit": {"en": "Assay Unit:", "pt": "Unidade do Ensaio:"},
    "s1_lbl_assay_strain": {"en": "Assay Strain:", "pt": "Cepa do Ensaio:"},
    "s1_lbl_assay_chembl_id": {"en": "Assay ChEMBL ID:", "pt": "Assay ChEMBL ID:"},
    "s1_btn_assay_description_count": {"en": "Assay description count", "pt": "Contagem de descrições de ensaio"},
    "s1_btn_explore_assay": {"en": "Explore by assay", "pt": "Explorar por ensaio"},
    "s1_lbl_assay_included": {"en": "Assay Included Terms:", "pt": "Termos Incluídos do Ensaio:"},
    "s1_lbl_assay_excluded": {"en": "Assay Excluded Terms:", "pt": "Termos Excluídos do Ensaio:"},
    "s1_lbl_molecule_chembl_id": {"en": "Molecule ChEMBL ID:", "pt": "Molecule ChEMBL ID:"},
    "s1_lbl_molecule_name": {"en": "Molecule Name:", "pt": "Nome da Molécula:"},
    "s1_lbl_canonical_smiles": {"en": "Canonical SMILES:", "pt": "SMILES Canônico:"},
    "s1_lbl_activity_chembl_id": {"en": "Activity ChEMBL ID:", "pt": "Activity ChEMBL ID:"},
    "s1_btn_explore_molecule": {"en": "Explore \nby molecule", "pt": "Explorar \npor molécula"},
    "s1_btn_generate_base_dataset": {"en": "Generate \nBase Dataset", "pt": "Gerar \nDataset Base"},
    "s1_lbl_request_time": {"en": "Request time (s)", "pt": "Tempo de requisição (s)"},
    "s1_grp_view_frequency": {"en": "View frequency graphs", "pt": "Ver gráficos de frequência"},
    "s1_lbl_internal_dataset_list": {"en": "Internal Dataset list:", "pt": "Lista de Datasets Internos:"},
    "s1_lbl_columns": {"en": "Columns:", "pt": "Colunas:"},
    "btn_update": {"en": "Update", "pt": "Atualizar"},
    "s1_btn_view_graph": {"en": "View Graph", "pt": "Ver Gráfico"},
    "msg_step1_build_error_title": {"en": "STEP 1 build error", "pt": "Erro ao construir a ETAPA 1"},
    "msg_step1_build_error_body": {
        "en": "There was an error building the STEP 1 TAB",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 1",
    },
    "s1_dlg_select_csv_excel": {
        "en": "Select one or more CSV or Excel files",
        "pt": "Selecione um ou mais arquivos CSV ou Excel",
    },
    "btn_select_dataframe": {"en": "Select DataFrame", "pt": "Selecionar DataFrame"},

    # ---------------------------------------------------------------- Shared generic labels (reused across tabs)
    "lbl_select_column": {"en": "Select column:", "pt": "Selecione a coluna:"},
    "lbl_samples": {"en": "Samples:", "pt": "Amostras:"},
    "lbl_bins": {"en": "Bins:", "pt": "Classes:"},
    "lbl_threshold": {"en": "Threshold:", "pt": "Limiar:"},
    "lbl_column": {"en": "Column:", "pt": "Coluna:"},
    "lbl_value": {"en": "Value:", "pt": "Valor:"},
    "lbl_count": {"en": "Count:", "pt": "Contagem:"},
    "chk_legend": {"en": "Legend", "pt": "Legenda"},
    "chk_trend_line": {"en": "Trend Line", "pt": "Linha de Tendência"},

    # ---------------------------------------------------------------- STEP 2 (Preprocessing / Exploratory Analysis)
    "s2_grp_select_convert": {"en": "Select columns and convert units", "pt": "Selecionar colunas e converter unidades"},
    "s2_lbl_select_columns_interest": {"en": "1. Select columns \nof interest:", "pt": "1. Selecione as colunas \nde interesse:"},
    "s2_btn_count_filter_columns": {"en": "Count and Filter \nColumns of interest", "pt": "Contar e Filtrar \nColunas de interesse"},
    "s2_btn_count_del_null": {"en": "Count and delete \nnull or empty values", "pt": "Contar e excluir \nvalores nulos ou vazios"},
    "s2_lbl_select_standard_type": {"en": "2. Select \nstandard type:", "pt": "2. Selecione o \ntipo padrão:"},
    "s2_btn_convert_type": {"en": "Convert type", "pt": "Converter tipo"},
    "s2_lbl_select_standard_unit": {"en": "3. Select \nstandard unit:", "pt": "3. Selecione a \nunidade padrão:"},
    "s2_btn_convert_units": {"en": "Convert units", "pt": "Converter unidades"},
    "s2_grp_treat_repetitions": {"en": "Treat repetitions", "pt": "Tratar repetições"},
    "s2_lbl_select_column_1": {"en": "1. Select column:", "pt": "1. Selecione a coluna:"},
    "s2_btn_count_rep": {"en": "Count\n repetitions", "pt": "Contar\n repetições"},
    "s2_lbl_select_method_rep": {
        "en": "2. Select the methods \nfor treating repetitions:",
        "pt": "2. Selecione os métodos \npara tratar repetições:",
    },
    "s2_btn_run_method": {"en": "Run selected\n method", "pt": "Executar\n método selecionado"},
    "s2_lbl_select_molecule_id": {"en": "Select Molecule_ChEMBL_ID:", "pt": "Selecione o Molecule_ChEMBL_ID:"},
    "s2_btn_check_molecule": {"en": "Check Molecule", "pt": "Verificar Molécula"},
    "s2_grp_data_transformation": {"en": "Data transformation", "pt": "Transformação de dados"},
    "s2_lbl_select_transformations": {"en": "Select\nTransformation:", "pt": "Selecione\na Transformação:"},
    "s2_lbl_select_column_trans": {"en": "Select\ncolumn:", "pt": "Selecione\na coluna:"},
    "s2_btn_run_transformation": {"en": "Run \nTransformation", "pt": "Executar \nTransformação"},
    "s2_btn_eliminate_invalid": {
        "en": "Eliminating invalid, infinite \nor values that exceed the \nallowed range in float64",
        "pt": "Eliminar valores inválidos, infinitos \nou que excedam o intervalo \npermitido em float64",
    },
    "s2_grp_outlier_elimination": {"en": "Outlier Elimination", "pt": "Eliminação de Outliers"},
    "s2_btn_view_descriptive_stats": {"en": "View descritive \nStatistics", "pt": "Ver Estatística \nDescritiva"},
    "s2_lbl_select_chart": {"en": "Select chart:", "pt": "Selecione o gráfico:"},
    "s2_btn_view_dist_chart": {"en": "View distribution \nchart", "pt": "Ver gráfico de \ndistribuição"},
    "s2_lbl_label_mark": {"en": "Label Mark", "pt": "Marcadores"},
    "s2_lbl_normality_test": {"en": "Normality \nTest:", "pt": "Teste de \nNormalidade:"},
    "s2_lbl_outlier_detection": {"en": "Outlier \nDetection:", "pt": "Detecção de \nOutliers:"},
    "s2_btn_view_interpretation": {"en": "View \nInterpretation", "pt": "Ver \nInterpretação"},
    "s2_btn_outlier_elimination": {"en": "Outlier \nElimination", "pt": "Eliminação de \nOutliers"},
    "msg_step2_build_error_title": {"en": "STEP 2 build error", "pt": "Erro ao construir a ETAPA 2"},
    "msg_step2_build_error": {
        "en": "There was an error building the STEP 2 TAB",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 2",
    },

    # ---------------------------------------------------------------- STEP 3 (Statistical Analysis)
    "s3_grp_generating_categories": {"en": "Generating Categories", "pt": "Geração de Categorias"},
    "s3_lbl_select_value_column": {"en": "Select value column:", "pt": "Selecione a coluna de valor:"},
    "s3_chk_inverse_scale": {"en": "Inverse scale", "pt": "Escala inversa"},
    "s3_tooltip_inverse_scale": {
        "en": "Lower value = more active (e.g. IC50, MIC).",
        "pt": "Valor menor = mais ativo (ex.: IC50, MIC).",
    },
    "s3_chk_direct_scale": {"en": "Direct scale", "pt": "Escala direta"},
    "s3_tooltip_direct_scale": {
        "en": "Higher value = more active (e.g. pIC50, pMIC).",
        "pt": "Valor maior = mais ativo (ex.: pIC50, pMIC).",
    },
    "s3_lbl_class1": {"en": "Class 1:", "pt": "Classe 1:"},
    "s3_lbl_class2": {"en": "Class 2:", "pt": "Classe 2:"},
    "s3_lbl_class3": {"en": "Class 3:", "pt": "Classe 3:"},
    "s3_lbl_reference_value": {"en": "Reference value:", "pt": "Valor de referência:"},
    "s3_lbl_range_value": {"en": "Range value:", "pt": "Valor do intervalo:"},
    "lbl_to": {"en": "to", "pt": "até"},
    "s3_btn_set_classes": {"en": "Set Classes", "pt": "Definir Classes"},
    "s3_lbl_view_molecule_class": {"en": "View Molecule Class:", "pt": "Ver Classe da Molécula:"},
    "s3_lbl_molecule_chembl_id": {"en": "Molecule_ChEMBL_ID:", "pt": "Molecule_ChEMBL_ID:"},
    "lbl_class": {"en": "Class:", "pt": "Classe:"},
    "s3_btn_view_class": {"en": "View Class", "pt": "Ver Classe"},
    "s3_lbl_select_class_column": {"en": "Select Class column:", "pt": "Selecione a coluna de Classe:"},
    "s3_btn_view_frequency": {"en": "View Frequency", "pt": "Ver Frequência"},
    "s3_grp_druggability": {"en": "Generating Druggability Descriptors", "pt": "Geração de Descritores de Drogabilidade"},
    "s3_lbl_select_properties": {"en": "Select Properties:", "pt": "Selecione as Propriedades:"},
    "s3_chk_molecular_weight": {"en": "Molecular Weight", "pt": "Massa Molecular"},
    "s3_chk_hdonor": {"en": "H-Donor", "pt": "Doador de H"},
    "s3_chk_haceptor": {"en": "H-Aceptor", "pt": "Aceptor de H"},
    "s3_chk_rotatable_bonds": {"en": "Rotatable Bonds", "pt": "Ligações Rotacionáveis"},
    "s3_chk_violations": {"en": "Nº Violations", "pt": "Nº de Violações"},
    "s3_lbl_select_range": {"en": "Select Range:", "pt": "Selecione o Intervalo:"},
    "s3_btn_set_druggability": {"en": "Set Druggability\n Descriptors", "pt": "Definir Descritores\n de Drogabilidade"},
    "s3_btn_filter_druggability": {"en": "Filter by\n Druggability Rule", "pt": "Filtrar pela\n Regra de Drogabilidade"},

    # ---------------------------------------------------------------- STATISTICS tab
    "stats_grp_descriptive_distribution": {
        "en": "Descriptive Statistics / Distribution",
        "pt": "Estatística Descritiva / Distribuição",
    },
    "menu_statistics": {"en": "Statistics", "pt": "Estatística"},
    "msg_statistics_build_error_title": {"en": "STATISTICS build error", "pt": "Erro ao construir a aba ESTATÍSTICA"},
    "msg_statistics_build_error": {
        "en": "There was an error building the STATISTICS TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba ESTATÍSTICA:\n{e}",
    },
    "stats_grp_sample_power": {
        "en": "Sample Size and Statistical Power",
        "pt": "Cálculo Amostral e Poder Estatístico",
    },
    "stats_lbl_confidence": {"en": "Confidence Level (%):", "pt": "Nível de Confiança (%):"},
    "stats_lbl_confidence_z": {"en": "Confidence Level (Z):", "pt": "Nível de Confiança (Z):"},
    "stats_lbl_alpha": {"en": "Type I Error (α):", "pt": "Erro Tipo I (α):"},
    "stats_lbl_power": {"en": "Statistical Power:", "pt": "Poder Estatístico:"},
    "stats_lbl_beta": {"en": "Type II Error (β):", "pt": "Erro Tipo II (β):"},
    "stats_lbl_p1": {"en": "Group 1 proportion (p1):", "pt": "Proporção do Grupo 1 (p1):"},
    "stats_lbl_p2": {"en": "Group 2 proportion (p2):", "pt": "Proporção do Grupo 2 (p2):"},
    "stats_lbl_p2_hint": {
        "en": "(p2 optional - fill it in to compare 2 groups instead of estimating a single proportion)",
        "pt": "(p2 opcional - preencha para comparar 2 grupos, em vez de estimar uma única proporção)",
    },
    "stats_lbl_margin_error": {"en": "Margin of Error (%):", "pt": "Margem de Erro (%):"},
    "stats_lbl_population_size": {"en": "Population Size (N):", "pt": "Tamanho da População (N):"},
    "stats_btn_sample_size": {"en": "Calculate\nSample Size", "pt": "Calcular\nTamanho Amostral"},
    "stats_btn_power": {"en": "Calculate\nStatistical Power", "pt": "Calcular\nPoder Estatístico"},

    "s3_grp_compare_classes": {"en": "Compare Classes", "pt": "Comparar Classes"},
    "s3_lbl_select_variable": {"en": "Select Variable:", "pt": "Selecione a Variável:"},
    "s3_btn_verify_assumptions": {"en": "Verify \nAssumptions", "pt": "Verificar \nPressupostos"},
    "s3_chk_normality_test": {"en": "Normality Test", "pt": "Teste de Normalidade"},
    "s3_chk_homogeneity_test": {"en": "Homoscedasticity Test", "pt": "Teste de Homocedasticidade"},
    "s3_lbl_select_groups": {"en": "Select groups:", "pt": "Selecione os grupos:"},
    "s3_lbl_parametric_tests": {"en": "Parametric Tests:", "pt": "Testes Paramétricos:"},
    "s3_lbl_non_parametric_tests": {"en": "Non-Parametric Tests:", "pt": "Testes Não Paramétricos:"},
    "s3_lbl_post_hoc": {"en": "Post-Hoc Test:", "pt": "Teste Post-Hoc:"},
    "s3_grp_correlate_variables": {"en": "Correlate variables", "pt": "Correlacionar variáveis"},
    "s3_lbl_select_variable1": {"en": "Select Variable 1:", "pt": "Selecione a Variável 1:"},
    "s3_lbl_select_variable2": {"en": "Select Variable 2:", "pt": "Selecione a Variável 2:"},
    "s3_lbl_select_variable3": {"en": "Select Variable 3:", "pt": "Selecione a Variável 3:"},
    "s3_lbl_num_samples": {"en": "Samples Number:", "pt": "Número de Amostras:"},
    "s3_lbl_confidence_interval": {"en": "Confidence Interval:", "pt": "Intervalo de Confiança:"},
    "s3_chk_2d_plot": {"en": "2D Plot", "pt": "Gráfico 2D"},
    "s3_chk_3d_plot": {"en": "3D Plot", "pt": "Gráfico 3D"},
    "s3_chk_plot_equation": {"en": "Plot Equation", "pt": "Exibir Equação"},
    "s3_lbl_correlation_tests": {"en": "Correlation Tests:", "pt": "Testes de Correlação:"},
    "lbl_to_short": {"en": "To", "pt": "Até"},

    # ---------------------------------------------------------------- STEP 4 (Feature Engineering)
    "s4_lbl_random_state": {"en": "Random State:", "pt": "Estado Aleatório:"},
    "s4_tooltip_session_id": {"en": "Session Id", "pt": "ID da Sessão"},
    "s4_grp_descriptors_builder": {"en": "Descriptors Builder", "pt": "Construtor de Descritores"},
    "s4_lbl_select_descriptors": {"en": "Select Descriptors:", "pt": "Selecione os Descritores:"},
    "s4_lbl_select_structure_column": {"en": "Structure \nColumn:", "pt": "Coluna \nde Estrutura:"},
    "s4_btn_select_structures_file": {"en": "Or Select \nStructures File", "pt": "Ou Selecione o \nArquivo de Estruturas"},
    "s4_lbl_select_bioactivity_column": {"en": "Bioactivity \nColumn:", "pt": "Coluna \nde Bioatividade:"},
    "s4_lbl_select_name_column": {"en": "Name \nColumn:", "pt": "Coluna \nde Nome:"},
    "s4_chk_remove_salt": {"en": "Remove salt", "pt": "Remover sal"},
    "s4_chk_detect_aromaticity": {"en": "Detect Aromaticity", "pt": "Detectar Aromaticidade"},
    "s4_chk_standardize_tautomers": {"en": "Standardize Tautomers", "pt": "Padronizar Tautômeros"},
    "s4_chk_standardize_nitro": {"en": "Standardize Nitro Groups", "pt": "Padronizar Grupos Nitro"},
    "s4_chk_retain_3d": {"en": "Retain 3D coordinates", "pt": "Manter coordenadas 3D"},
    "s4_chk_convert_3d": {"en": "Convert to 3D", "pt": "Converter para 3D"},
    "s4_btn_generate_descriptors": {"en": "Generate \nDescriptors", "pt": "Gerar \nDescritores"},
    "s4_grp_dimensionality_reduction": {"en": "Dimensionality Reduction", "pt": "Redução de Dimensionalidade"},
    "s4_lbl_feature_columns_range": {"en": "Feature Columns Range:", "pt": "Intervalo de Colunas de Atributos:"},
    "s4_lbl_label_column": {"en": "Label Column:", "pt": "Coluna de Rótulo:"},
    "s4_lbl_class_column": {"en": "Class Column:", "pt": "Coluna de Classe:"},
    "s4_lbl_features_types": {"en": "Features Types:", "pt": "Tipos de Atributos:"},
    "s4_lbl_attribute_options": {"en": "Attribute Options:", "pt": "Opções de Atributo:"},
    "s4_lbl_model_type": {"en": "Model Type:", "pt": "Tipo de Modelo:"},
    "s4_lbl_recommended_scaling": {"en": "Recommended Scaling:", "pt": "Escalonamento Recomendado:"},
    "s4_btn_run_scaling": {"en": "Run Scaling", "pt": "Executar Escalonamento"},
    "s4_lbl_recommended_selection": {"en": "Recommended Selection:", "pt": "Seleção Recomendada:"},
    "s4_btn_run_selection": {"en": "Run Selection", "pt": "Executar Seleção"},
    "s4_lbl_recommended_projection": {"en": "Recommended Projection:", "pt": "Projeção Recomendada:"},
    "s4_btn_run_projection": {"en": "Run Projection", "pt": "Executar Projeção"},
    "s4_lbl_parameters": {"en": "Parameters:", "pt": "Parâmetros:"},
    "btn_reset": {"en": "Reset", "pt": "Redefinir"},
    "s4_tooltip_reset_params": {
        "en": "Restores every row in this table to its predefined value and restores the "
              "full, unfiltered method list in Recommended Scaling/Selection/Projection "
              "(undoing any narrowing from Features Types/Attribute Options/Model Type).",
        "pt": "Restaura todas as linhas desta tabela para o valor predefinido e restaura a "
              "lista completa, sem filtro, de métodos em Escalonamento/Seleção/Projeção "
              "Recomendados (desfazendo qualquer restrição de Tipos de Atributos/Opções de "
              "Atributo/Tipo de Modelo).",
    },
    "s4_col_parameter": {"en": "Parameter", "pt": "Parâmetro"},
    "lbl_value_col": {"en": "Value", "pt": "Valor"},
    "msg_step4_build_error_title": {"en": "STEP 4 build error", "pt": "Erro ao construir a ETAPA 4"},
    "msg_step4_build_error": {
        "en": "There was an error building the STEP 4 TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 4:\n{e}",
    },

    # ---------------------------------------------------------------- STEP 5 (scikit-learn)
    "btn_select_internal_df": {"en": "Select Internal DataFrame", "pt": "Selecionar DataFrame Interno"},
    "btn_select_external_df": {"en": "Select External DataFrame", "pt": "Selecionar DataFrame Externo"},
    "s5_lbl_usi": {"en": "USI:", "pt": "USI:"},
    "s5_subtab_predict": {"en": "Predict", "pt": "Predizer"},
    "lbl_descriptors_columns_range": {"en": "Descriptors Columns Range:", "pt": "Intervalo de Colunas de Descritores:"},
    "btn_plot_model": {"en": "Plot Model", "pt": "Plotar Modelo"},
    "msg_step5_build_error_title": {"en": "STEP 5 build error", "pt": "Erro ao construir a ETAPA 5"},
    "msg_step5_build_error": {
        "en": "There was an error building the STEP 5 TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 5:\n{e}",
    },

    # ---------------------------------------------------------------- STEP 5 (scikit-learn), continued
    "s6_tooltip_random_state": {"en": "Random State", "pt": "Estado Aleatório"},
    "s6_tooltip_usi": {
        "en": "Use Sample Index — type a new code (used by Run Screening) or pick an existing "
              "one from the list to reload that run's models, train/test data and Hyperparameter "
              "Tuning grids.",
        "pt": "Índice de Amostra Utilizado — digite um novo código (usado pelo Run Screening) ou "
              "escolha um existente na lista para recarregar os modelos, dados de treino/teste e "
              "grades de Hyperparameter Tuning dessa execução.",
    },
    "s6_grp_model_screening": {"en": "Model Screening", "pt": "Seleção de Modelos"},
    "lbl_models": {"en": "Models:", "pt": "Modelos:"},
    "s6_lbl_sort_metric": {"en": "Sort metric:", "pt": "Métrica de ordenação:"},
    "s6_lbl_select_x_range": {"en": "Select X range (internal df):", "pt": "Selecione o intervalo X (df interno):"},
    "s6_lbl_select_y_column_internal": {"en": "Select Y column (internal df):", "pt": "Selecione a coluna Y (df interno):"},
    "s6_lbl_select_test_size": {"en": "Select Test Size:", "pt": "Selecione o Tamanho do Teste:"},
    "lbl_status": {"en": "Status:", "pt": "Status:"},
    "s6_fmt_screening_progress": {"en": "Screening: %p%", "pt": "Seleção: %p%"},
    "btn_select_all": {"en": "Select All", "pt": "Selecionar Tudo"},
    "s6_btn_run_screening": {"en": "Run Screening", "pt": "Executar Seleção"},
    "s6_grp_hyperparameter_tuning": {"en": "Hyperparameter Tuning", "pt": "Ajuste de Hiperparâmetros"},
    "lbl_model": {"en": "Model:", "pt": "Modelo:"},
    "lbl_method": {"en": "Method:", "pt": "Método:"},
    "s6_lbl_cv_folds": {"en": "CV folds:", "pt": "Folds de CV:"},
    "s6_lbl_n_iter": {"en": "n_iter (Randomized/Bayesian):", "pt": "n_iter (Randomized/Bayesian):"},
    "s6_col_hyperparameter": {"en": "Hyperparameter", "pt": "Hiperparâmetro"},
    "s6_col_values_to_test": {"en": "Values to test (comma-separated)", "pt": "Valores a testar (separados por vírgula)"},
    "s6_btn_run_tuning": {"en": "Run Tuning", "pt": "Executar Ajuste"},
    "lbl_parameter": {"en": "Parameter:", "pt": "Parâmetro:"},
    "btn_plot": {"en": "Plot", "pt": "Plotar"},
    "s6_grp_validation": {"en": "Validation", "pt": "Validação"},
    "s6_lbl_folds": {"en": "Folds:", "pt": "Folds:"},
    "s6_lbl_p_leave_p_out": {"en": "p (Leave-P-Out):", "pt": "p (Leave-P-Out):"},
    "s6_btn_run_cross_validation": {"en": "Run Cross-Validation", "pt": "Executar Validação Cruzada"},
    "s6_grp_remove_model_predict": {"en": "Remove Model and Predict", "pt": "Remover Modelo e Predizer"},
    "s6_chk_remove_descriptors": {"en": "Remove Descriptors", "pt": "Remover Descritores"},
    "s6_btn_remove_model": {"en": "Remove Model", "pt": "Remover Modelo"},
    "s6_grp_performance_charts": {"en": "Performance Charts", "pt": "Gráficos de Desempenho"},
    "s6_chk_metric_legend": {"en": "Metric Legend", "pt": "Legenda de Métricas"},
    "s6_tooltip_metric_legend": {
        "en": "Add R2, MAE, RMSE and MSE to the chart legend (regression charts only).",
        "pt": "Adiciona R2, MAE, RMSE e MSE à legenda do gráfico (somente gráficos de regressão).",
    },
    "msg_step6_build_error_title": {"en": "STEP 6 build error", "pt": "Erro ao construir a ETAPA 6"},
    "msg_step6_build_error": {
        "en": "There was an error building the STEP 6 TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 6:\n{e}",
    },

    # ---------------------------------------------------------------- STEP 6 (Applicability Domain)
    "s7_grp_set_ad_params": {"en": "Set AD Parameters", "pt": "Definir Parâmetros de DA"},
    "s7_chk_project_pca": {"en": "Project PCA for plots", "pt": "Projetar PCA para os gráficos"},
    "s7_lbl_k_knn": {"en": "k (kNN):", "pt": "k (kNN):"},
    "s7_lbl_alpha_chi2": {"en": "α for χ² cut (MD):", "pt": "α para corte χ² (MD):"},
    "s7_lbl_fingerprint": {"en": "Fingerprint:", "pt": "Fingerprint:"},
    "s7_btn_compute_ad": {"en": "Compute AD", "pt": "Calcular DA"},
    "s7_btn_plot_williams": {"en": "Plot Williams", "pt": "Plotar Williams"},
    "s7_btn_hist_mahalanobis": {"en": "Hist Mahalanobis", "pt": "Hist Mahalanobis"},
    "s7_btn_pca_scatter_ad": {"en": "PCA Scatter (AD)", "pt": "Dispersão PCA (DA)"},
    "s7_btn_similarity_dist": {"en": "Similarity Dist", "pt": "Dist. Similaridade"},
    "s7_fmt_ad_progress": {"en": "AD: %p%", "pt": "DA: %p%"},
    "msg_step7_build_error_title": {"en": "STEP 7 build error", "pt": "Erro ao construir a ETAPA 7"},
    "msg_step7_build_error": {
        "en": "There was an error building the STEP 7 TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 7:\n{e}",
    },

    # ---------------------------------------------------------------- STEP 7 (Consensus Analysis)
    "s8_btn_select_dataframe_n": {"en": "Dataframe\n {slot}", "pt": "Dataframe\n {slot}"},
    "s8_placeholder_dataframe_n": {"en": "DataFrame {slot}", "pt": "DataFrame {slot}"},
    "s8_lbl_id_column": {"en": "ID Column:", "pt": "Coluna de ID:"},
    "s8_lbl_value_column": {"en": "Value Column:", "pt": "Coluna de Valor:"},
    "s8_placeholder_weight": {"en": "Weight", "pt": "Peso"},
    "s8_tooltip_weight": {
        "en": "Only used by the 'Weighted Consensus' method. Auto-suggested from the "
              "model's R2 Test (regression) / F1 (classification) when the dataframe "
              "comes from a known USI - editable.",
        "pt": "Usado apenas pelo método 'Weighted Consensus'. Sugerido automaticamente a partir "
              "do R2 Test (regressão) / F1 (classificação) do modelo quando o dataframe vem de "
              "uma USI conhecida - editável.",
    },
    "s8_lbl_ranking_direction": {"en": "Ranking direction:", "pt": "Direção do ranking:"},
    "s8_chk_increase": {"en": "Increase", "pt": "Crescente"},
    "s8_chk_decrease": {"en": "Decrease", "pt": "Decrescente"},
    "s8_lbl_consensus_method": {"en": "Consensus Method:", "pt": "Método de Consenso:"},
    "s8_tooltip_consensus_method": {
        "en": "Z-Score (Mean/SD): classic standardized consensus.\n"
              "Z-Score (Median/MAD): robust to outlier compounds.\n"
              "Rank Sum / Borda count: non-parametric, uses list positions only.\n"
              "Reciprocal Rank Fusion (RRF): robust ensemble-fusion score, no normalization needed.\n"
              "Weighted Consensus: Z-Score weighted per list by the 'Weight' field (manual, "
              "or auto-suggested from R2 Test/F1 when the list traces back to a known USI).",
        "pt": "Z-Score (Mean/SD): consenso padronizado clássico.\n"
              "Z-Score (Median/MAD): robusto a compostos discrepantes (outliers).\n"
              "Rank Sum / Borda count: não paramétrico, usa apenas as posições nas listas.\n"
              "Reciprocal Rank Fusion (RRF): score de fusão robusto, sem necessidade de normalização.\n"
              "Weighted Consensus: Z-Score ponderado por lista pelo campo 'Weight' (manual, "
              "ou sugerido automaticamente a partir de R2 Test/F1 quando a lista vem de uma USI conhecida).",
    },
    "s8_lbl_max_cv": {"en": "Max CV% (optional):", "pt": "CV% Máximo (opcional):"},
    "s8_tooltip_max_cv": {
        "en": "Keeps only compounds whose coefficient of variation between the selected lists "
              "is <= this value. Leave blank to skip this filter.",
        "pt": "Mantém apenas compostos cujo coeficiente de variação entre as listas selecionadas "
              "seja <= este valor. Deixe em branco para não aplicar este filtro.",
    },
    "s8_lbl_top_hits": {"en": "Top Hits % (optional):", "pt": "Top Hits % (opcional):"},
    "s8_tooltip_top_hits": {
        "en": "Keeps only the top X% best-ranked compounds (of the shared/merged total, after "
              "the CV% filter). E.g. 1000 shared compounds + Hits 2% -> top 20. Leave blank to "
              "keep every compound that passes the CV% filter.",
        "pt": "Mantém apenas os X% melhores compostos ranqueados (do total compartilhado/combinado, "
              "após o filtro de CV%). Ex.: 1000 compostos compartilhados + Hits 2% -> top 20. Deixe "
              "em branco para manter todos os compostos que passarem no filtro de CV%.",
    },
    "s8_btn_consensus_generate": {"en": "Consensus Generate", "pt": "Gerar Consenso"},
    "btn_clear": {"en": "Clear", "pt": "Limpar"},
    "s8_btn_generate_final_report": {"en": "Generate Final Report", "pt": "Gerar Relatório Final"},

    # ---------------------------------------------------------------- EDIT tab
    "edit_grp_merge_remove_compare": {"en": "Merge, Remove or Compare", "pt": "Combinar, Remover ou Comparar"},
    "edit_lbl_select_df1": {"en": "Select DataFrame 1:", "pt": "Selecione o DataFrame 1:"},
    "edit_lbl_select_index1": {"en": "Select Index 1:", "pt": "Selecione o Índice 1:"},
    "edit_placeholder_select_df1": {"en": "Select DataFrame 1", "pt": "Selecione o DataFrame 1"},
    "btn_search": {"en": "Search", "pt": "Buscar"},
    "edit_lbl_select_df2": {"en": "Select DataFrame 2:", "pt": "Selecione o DataFrame 2:"},
    "edit_lbl_select_index2": {"en": "Select Index 2:", "pt": "Selecione o Índice 2:"},
    "edit_placeholder_select_df2": {"en": "Select DataFrame 2", "pt": "Selecione o DataFrame 2"},
    "edit_chk_by_rows": {"en": "By Rows", "pt": "Por Linhas"},
    "edit_chk_by_columns": {"en": "By Columns", "pt": "Por Colunas"},
    "edit_btn_merge_dataframes": {"en": "Merge from\n Dataframes", "pt": "Combinar a partir\n de Dataframes"},
    "edit_btn_remove_from_dataframes": {"en": "Remove from\n Dataframes", "pt": "Remover a partir\n de Dataframes"},
    "edit_btn_delete_dataframes": {"en": "Delete \n Dataframes", "pt": "Excluir \n Dataframes"},
    "edit_btn_compare_files": {"en": "Compare\nFiles", "pt": "Comparar\nArquivos"},
    "edit_grp_filter_by_value": {"en": "Filter by Value", "pt": "Filtrar por Valor"},
    "edit_lbl_dataframe1": {"en": "Dataframe 1:", "pt": "Dataframe 1:"},
    "edit_btn_select_predictions_df": {"en": "Filtered\n Dataframe", "pt": "Dataframe\n Filtrado"},
    "edit_placeholder_select_predictions_df": {"en": "Select Predictions Dataframe", "pt": "Selecione o Dataframe de Predições"},
    "edit_lbl_select_id_column": {"en": "ID column:", "pt": "Coluna de ID:"},
    "edit_lbl_select_predictions_column": {"en": "Filtered column:", "pt": "Coluna Filtrada:"},
    "edit_lbl_dataframe2": {"en": "Dataframe 2:", "pt": "Dataframe 2:"},
    "edit_btn_select_ad_df": {"en": "Filter\n Dataframe", "pt": "Dataframe\n Filtrante"},
    "edit_placeholder_select_ad_df": {"en": "Select AD Dataframe", "pt": "Selecione o Dataframe de DA"},
    "edit_lbl_select_value_column": {"en": "Filter column:", "pt": "Coluna Filtrante:"},
    "edit_lbl_select_values": {"en": "Select values:", "pt": "Selecione os valores:"},
    "edit_chk_interval_value": {"en": "Interval value", "pt": "Valor de intervalo"},
    "edit_placeholder_minimum": {"en": "Minimum", "pt": "Mínimo"},
    "edit_placeholder_maximum": {"en": "Maximum", "pt": "Máximo"},
    "edit_btn_generate_filtered_df": {"en": "Generate Filtered Dataframe", "pt": "Gerar Dataframe Filtrado"},
    "edit_grp_transform_by_value": {"en": "Transform by Value", "pt": "Transformar por Valor"},
    "edit_lbl_dataframe": {"en": "Dataframe:", "pt": "Dataframe:"},
    "edit_lbl_select_column1": {"en": "Column: 1", "pt": "Coluna: 1"},
    "edit_lbl_select_column2": {"en": "Column 2", "pt": "Coluna 2"},
    "edit_lbl_math_function": {"en": "Mathematical function", "pt": "Função matemática"},
    "edit_lbl_new_column_name": {"en": "New column name", "pt": "Nome da nova coluna"},
    "edit_placeholder_new_column": {"en": "Ex.: transformed_value", "pt": "Ex.: valor_transformado"},
    "edit_btn_transform": {"en": "Transform", "pt": "Transformar"},
    "msg_edit_build_error_title": {"en": "EDIT build error", "pt": "Erro ao construir a aba EDITAR"},
    "msg_edit_build_error": {
        "en": "There was an error building the EDIT TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba EDITAR:\n{e}",
    },

    # ---------------------------------------------------------------- Common QMessageBox titles (app-wide)
    # These are the most frequently reused literal titles passed to QMessageBox.warning/information/
    # critical/question(self, "<title>", ...) across the whole file - translating them covers the
    # large majority of the ~445 message-box call sites even though most message BODIES (the
    # second argument, almost always unique per call site) are still English-only.
    "msg_title_attention": {"en": "Attention", "pt": "Atenção"},
    "msg_title_attention_bang": {"en": "Attention!", "pt": "Atenção!"},
    "msg_title_error": {"en": "Error", "pt": "Erro"},
    "msg_title_warning": {"en": "Warning", "pt": "Aviso"},
    "msg_title_info": {"en": "Info", "pt": "Informação"},
    "msg_title_result": {"en": "Result", "pt": "Resultado"},
    "msg_title_success": {"en": "Success", "pt": "Sucesso"},
    "msg_title_done": {"en": "Done", "pt": "Concluído"},
    "msg_title_ad": {"en": "AD", "pt": "DA"},
    "msg_title_plot": {"en": "Plot", "pt": "Gráfico"},
    "msg_title_plot_error": {"en": "Plot error", "pt": "Erro no gráfico"},
    "msg_title_predict": {"en": "Predict", "pt": "Predizer"},
    "msg_title_tuning": {"en": "Tuning", "pt": "Ajuste"},
    "msg_title_tuning_error": {"en": "Tuning error", "pt": "Erro no ajuste"},
    "msg_title_evaluate": {"en": "Evaluate", "pt": "Avaliar"},
    "msg_title_evaluate_error": {"en": "Evaluate error", "pt": "Erro na avaliação"},
    "msg_title_screening": {"en": "Screening", "pt": "Seleção"},
    "msg_title_screening_error": {"en": "Screening error", "pt": "Erro na seleção"},
    "msg_title_usi": {"en": "USI", "pt": "USI"},
    "msg_title_remove_model": {"en": "Remove Model", "pt": "Remover Modelo"},
    "msg_title_error_list_columns_csv": {"en": "Error on list columns CSV", "pt": "Erro ao listar colunas do CSV"},
    "msg_title_error_list_units_csv": {"en": "Error on list units CSV", "pt": "Erro ao listar unidades do CSV"},
    "msg_title_error_list_types_csv": {"en": "Error on list types CSV", "pt": "Erro ao listar tipos do CSV"},
    "msg_title_error_opening_file": {"en": "Error opening file.", "pt": "Erro ao abrir arquivo."},
    "msg_title_error_opening_csv": {"en": "Error opening CSV", "pt": "Erro ao abrir CSV"},
    "msg_title_error_reading_csv": {"en": "Error reading CSV", "pt": "Erro ao ler CSV"},
    "msg_title_error_generating_chart": {"en": "Error generating chart", "pt": "Erro ao gerar gráfico"},
    "msg_title_generate_final_report": {"en": "Generate Final Report", "pt": "Gerar Relatório Final"},
    "msg_title_compare_files": {"en": "Compare Files", "pt": "Comparar Arquivos"},
    "msg_title_download_stopped": {"en": "Download Stopped", "pt": "Download Interrompido"},
    "msg_title_monitor": {"en": "Monitor", "pt": "Monitor"},
    "msg_title_monitor_error": {"en": "Monitor error", "pt": "Erro no monitor"},
    "msg_title_units_incompatible_source": {"en": "Units: incompatible source", "pt": "Unidades: origem incompatível"},
    "msg_title_error_during_unit_conversion": {"en": "Error during unit conversion", "pt": "Erro durante a conversão de unidade"},
    "msg_title_confirm_deletion": {"en": "Confirm deletion", "pt": "Confirmar exclusão"},
    "msg_title_finished": {"en": "Finished", "pt": "Concluído"},
    "msg_title_current_job": {"en": "Current Job", "pt": "Job Atual"},
    "msg_title_save": {"en": "Save", "pt": "Salvar"},
    "msg_title_preview": {"en": "Preview", "pt": "Pré-visualização"},
    "msg_title_remove_rows_columns": {"en": "Remove Rows/Columns", "pt": "Remover Linhas/Colunas"},
    "msg_title_predict_error": {"en": "Predict error", "pt": "Erro na predição"},
    "msg_title_remove_model_error": {"en": "Remove Model error", "pt": "Erro ao remover modelo"},
    "msg_title_tuning_complete": {"en": "Tuning complete", "pt": "Ajuste concluído"},

    # ---------------------------------------------------------------- Menu bar (Menu / Help)
    # "Menu" (top-level menu title) stays literal in both languages - explicit user request.
    "menu_help": {"en": "Help", "pt": "Ajuda"},
    "menu_configure_new_run": {"en": "Configure New Run", "pt": "Configurar Nova Execução"},
    "menu_step1": {"en": "Step 1 - Dataset Preparation", "pt": "Etapa 1 - Preparação do Dataset"},
    "menu_step2": {
        "en": "Step 2 - Data Preprocessing",
        "pt": "Etapa 2 - Pré-processamento dos Dados",
    },
    "menu_step4": {"en": "Step 3 - Features Engineering", "pt": "Etapa 3 - Engenharia de Atributos"},
    "menu_step5": {
        "en": "Step 4 - Machine Learning Models Screening (Scikit-learn)",
        "pt": "Etapa 4 - Seleção de Modelos de Aprendizado de Máquina (Scikit-learn)",
    },
    "menu_step6": {
        "en": "Step 5 - Applicability Domain and Similarity Analysis",
        "pt": "Etapa 5 - Domínio de Aplicabilidade e Análise de Similaridade",
    },
    "menu_step7": {"en": "Step 6 - Consensus Analysis", "pt": "Etapa 6 - Análise de Consenso"},
    "menu_edit": {"en": "Edit - DataFrame Manipulate", "pt": "Editar - Manipulação do DataFrame"},
    "menu_exit": {"en": "Exit", "pt": "Sair"},
    "menu_install_requirements": {"en": "Install Requirements", "pt": "Instalar Dependências"},
    "menu_code_and_tutorials": {"en": "Code and Tutorials (Github)", "pt": "Código e Tutoriais (Github)"},
    "menu_about": {"en": "About", "pt": "Sobre"},

    # ---------------------------------------------------------------- About dialog
    "about_title": {"en": "ABOUT", "pt": "SOBRE"},
    "about_subtitle": {"en": "An Open-Source Automated QSAR Analysis Tool", "pt": "Uma Ferramenta Automatizada e de Código Aberto para Análise QSAR"},
    "about_developed_by": {"en": "Developed by:", "pt": "Desenvolvido por:"},
    "about_brazil": {"en": "Brazil", "pt": "Brasil"},
    "about_contact": {"en": "Contact:", "pt": "Contato:"},
    "about_version": {"en": "Version 1.0 (beta)   © October 2025", "pt": "Versão 1.0 (beta)   © Outubro de 2025"},

    # ---------------------------------------------------------------- RequirementsInstaller window
    # (MODULES/module_requirements.py) — standalone window opened from Help > Install Requirements
    # and from the HOME tab's "Install Requirements" button. Translated once at construction time
    # from the idioma passed in by the caller (no live language switcher inside this sub-window).
    "req_window_title": {"en": "Install Requirements (Python venv + pip)", "pt": "Instalar Dependências (venv Python + pip)"},
    "req_env_info": {
        "en": "Selected packages will be installed into the CODRUG Python virtual environment "
              "(~/.venv/CODRUG).<br>"
              "Active Python: <b>{python_exe}</b> ({python_ver})",
        "pt": "Os pacotes selecionados serão instalados no ambiente virtual Python do CODRUG "
              "(~/.venv/CODRUG).<br>"
              "Python ativo: <b>{python_exe}</b> ({python_ver})",
    },
    "req_opt_latest": {"en": "Latest", "pt": "Mais recente"},
    "req_opt_tested": {"en": "Version:", "pt": "Versão:"},
    "req_chk_venv": {"en": "Create/repair CODRUG Python environment (venv)", "pt": "Criar/reparar o ambiente Python do CODRUG (venv)"},
    "req_tooltip_venv": {
        "en": "Using the current Python to create the venv. Field is informative.",
        "pt": "Usa o Python atual para criar o venv. Campo apenas informativo.",
    },
    "req_chk_java": {"en": "Install Java (JRE, required by PaDEL-Descriptor)", "pt": "Instalar Java (JRE, necessário para o PaDEL-Descriptor)"},
    "req_java_default_label": {"en": "Default (default-jre)", "pt": "Padrão (default-jre)"},
    "req_java_version_label": {"en": "Version:", "pt": "Versão:"},
    "req_tooltip_java_version": {
        "en": "openjdk-<version>-jre will be installed via apt, e.g. 'openjdk-11-jre'.",
        "pt": "openjdk-<versão>-jre será instalado via apt, ex.: 'openjdk-11-jre'.",
    },
    "req_chk_scikitlearn": {"en": "Install scikit-learn", "pt": "Instalar scikit-learn"},
    "req_chk_cuml": {
        "en": "Install cuML (RAPIDS, optional GPU backend for Scikit-learn)",
        "pt": "Instalar cuML (RAPIDS, backend de GPU opcional para o Scikit-learn)",
    },
    "req_tooltip_cuml_unavailable": {
        "en": "Unavailable: {reason} cuML pip wheels only support Linux with an NVIDIA GPU "
              "(CUDA 11.4+/12.x). Scikit-learn works fine without it; the 'soft dependency' warning "
              "is harmless CPU-only fallback.",
        "pt": "Indisponível: {reason} Os pacotes pip do cuML só funcionam em Linux com GPU NVIDIA "
              "(CUDA 11.4+/12.x). O Scikit-learn funciona normalmente sem ele; o aviso de "
              "'soft dependency' é inofensivo (fallback para CPU).",
    },
    "req_chk_chembl": {"en": "Install chembl_webresource_client", "pt": "Instalar chembl_webresource_client"},
    "req_chk_padelpy": {"en": "Install padelpy (PaDEL-Descriptor launcher)", "pt": "Instalar padelpy (executor do PaDEL-Descriptor)"},
    "req_chk_rdkit": {"en": "Install RDKit (rdkit-pypi)", "pt": "Instalar RDKit (rdkit-pypi)"},
    "req_chk_matplotlib": {"en": "Install Matplotlib", "pt": "Instalar Matplotlib"},
    "req_chk_seaborn": {"en": "Install Seaborn", "pt": "Instalar Seaborn"},
    "req_chk_joblib": {"en": "Install joblib", "pt": "Instalar joblib"},
    "req_chk_pandas": {"en": "Install pandas", "pt": "Instalar pandas"},
    "req_chk_numpy": {"en": "Install numpy", "pt": "Instalar numpy"},
    "req_chk_pytorch": {
        "en": "Install PyTorch (variant auto-selected from detected hardware)",
        "pt": "Instalar PyTorch (variante selecionada automaticamente conforme o hardware detectado)",
    },
    "req_chk_tensorflow": {"en": "Install TensorFlow (pip wheels)", "pt": "Instalar TensorFlow (pacotes pip)"},
    "req_chk_libs": {"en": "Install another libs (default set)", "pt": "Instalar outras bibliotecas (conjunto padrão)"},
    "req_placeholder_cuml_version": {"en": "{pkg} version (blank = latest)", "pt": "versão do {pkg} (em branco = mais recente)"},
    "req_placeholder_libs_version": {"en": "(not used, default curated set)", "pt": "(não usado, conjunto padrão pré-definido)"},
    "req_btn_select_all": {"en": "Select All", "pt": "Selecionar Tudo"},
    "req_btn_install_selected": {"en": "Install Selected", "pt": "Instalar Selecionados"},
    "req_btn_close": {"en": "Close", "pt": "Fechar"},
    "req_msg_no_selection_title": {"en": "No Selection", "pt": "Nada Selecionado"},
    "req_msg_no_selection_body": {"en": "Please select at least one requirement.", "pt": "Selecione ao menos uma dependência."},
    "req_log_ensuring_venv": {"en": "Ensuring Python venv at ~/CODRUG/.venv ...\n", "pt": "Garantindo o venv Python em ~/CODRUG/.venv ...\n"},
    "req_log_using_python": {"en": "Using Python: {python}\n", "pt": "Usando Python: {python}\n"},
    "req_log_installing": {"en": "Installing {name} ...\n", "pt": "Instalando {name} ...\n"},
    "req_log_installing_default_libs": {"en": "Installing libraries (default set) ...\n", "pt": "Instalando bibliotecas (conjunto padrão) ...\n"},
    "req_log_all_installed": {
        "en": "\nAll selected requirements installed into the CODRUG venv!\n",
        "pt": "\nTodas as dependências selecionadas foram instaladas no venv do CODRUG!\n",
    },
    "req_log_aborted": {"en": "Aborted on {name} install failure.\n", "pt": "Interrompido: falha ao instalar {name}.\n"},
    "req_log_pkg_installed": {"en": "{spec} installed.\n", "pt": "{spec} instalado.\n"},
    "req_log_pkg_install_warn": {"en": "[WARN] Could not install {target}:\n{output}\n", "pt": "[AVISO] Não foi possível instalar {target}:\n{output}\n"},
    "req_log_invalid_pytorch_variant": {
        "en": "Invalid PyTorch variant '{variant}'. Use 'cu128', 'cu121', 'cu118' or 'cpu'.\n",
        "pt": "Variante de PyTorch inválida '{variant}'. Use 'cu128', 'cu121', 'cu118' ou 'cpu'.\n",
    },
    "req_log_pytorch_installed": {"en": "PyTorch installed ({variant}{version}).\n", "pt": "PyTorch instalado ({variant}{version}).\n"},
    "req_log_cuml_skip": {
        "en": "[WARN] Skipping cuML: pip wheels require Linux + NVIDIA GPU with CUDA 11.4+/12.x "
              "({reason}). Scikit-learn keeps working on CPU-only estimators; the 'soft dependency' "
              "warning in the logs is harmless.\n",
        "pt": "[AVISO] Pulando cuML: os pacotes pip exigem Linux + GPU NVIDIA com CUDA 11.4+/12.x "
              "({reason}). O Scikit-learn continua funcionando com estimadores somente-CPU; o aviso de "
              "'soft dependency' nos logs é inofensivo.\n",
    },
    "req_log_cuml_installed": {"en": "cuML installed ({spec}).\n", "pt": "cuML instalado ({spec}).\n"},
    "req_log_tensorflow_installed": {"en": "TensorFlow installed (version={ver}).\n", "pt": "TensorFlow instalado (versão={ver}).\n"},
    "req_log_java_skip": {
        "en": "[WARN] Skipping Java: apt bootstrap is only supported on Ubuntu/Debian-based Linux "
              "with 'sudo'. Install manually, e.g. 'sudo apt install openjdk-11-jre'.\n",
        "pt": "[AVISO] Pulando Java: o bootstrap via apt só é suportado em Linux baseado em "
              "Ubuntu/Debian com 'sudo'. Instale manualmente, ex.: 'sudo apt install openjdk-11-jre'.\n",
    },
    "req_log_java_apt_update_failed": {"en": "Failed to run 'sudo apt update'.\n", "pt": "Falha ao executar 'sudo apt update'.\n"},
    "req_log_java_apt_install_failed": {"en": "Failed to install {pkg} via apt.\n", "pt": "Falha ao instalar {pkg} via apt.\n"},
}


def t(chave, idioma, **kwargs):
    valor = _TEXTOS.get(chave, {}).get(idioma)
    if valor is None:
        valor = _TEXTOS.get(chave, {}).get(IDIOMA_PADRAO, chave)
    return valor.format(**kwargs) if kwargs else valor

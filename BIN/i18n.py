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
        "en": "Project setup, environment and project folder preparation",
        "pt": "Configuração do projeto, ambiente e preparação da pasta do projeto",
    },
    "home_step1_name": {"en": "Step 1 — Dataset Preparation", "pt": "Etapa 1 — Preparação do Dataset"},
    "home_step1_desc": {
        "en": "Target, assay and bioactivity dataset construction from source data",
        "pt": "Construção do dataset de alvo, ensaio e bioatividade a partir dos dados de origem",
    },
    "home_step2_name": {"en": "Step 2 — Data Preprocessing", "pt": "Etapa 2 — Pré-Processamento de dados"},
    "home_step2_desc": {
        "en": "Cleaning, conversion, replicates, outliers and categorization.",
        "pt": "Limpeza, conversão, repetições, outliers e categorização.",
    },
    "home_step3_name": {"en": "Step 3 — Feature Engineering", "pt": "Etapa 3 — Engenharia de Atributos"},
    "home_step3_desc": {
        "en": "Descriptor generation, druggability descriptors, structural processing and feature preparation",
        "pt": "Geração de descritores, descritores de drogabilidade, processamento estrutural e preparação de atributos",
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
        "en": "Consensus ranking with z-score integration and Spearman concordance",
        "pt": "Ranqueamento por consenso com integração de z-score e concordância de Spearman",
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
        "en": "Applicability Domain, Similarity Analysis and Interpretability",
        "pt": "Domínio de Aplicabilidade, Análise de Similaridade e Interpretabilidade",
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
    "cfg_label_project_name": {"en": "Project Name:", "pt": "Nome do Projeto:"},
    "cfg_placeholder_project_name": {
        "en": "Put here the new project name",
        "pt": "Coloque aqui o nome do novo projeto",
    },
    "cfg_btn_previous_project": {"en": "Previous Project", "pt": "Projeto Anterior"},
    "cfg_label_previous_run": {"en": "Select:", "pt": "Selecione:"},
    "cfg_placeholder_previous_run": {"en": "Select a previous project", "pt": "Selecione um projeto anterior"},
    "cfg_btn_set_run_folder": {"en": "Set project folder", "pt": "Definir pasta do projeto"},
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
    "msg_project_required_title": {"en": "Project Required", "pt": "Projeto Necessário"},
    "msg_project_required_body": {
        "en": "You need to create a New Project (enter a project name) or select a Previous Project before setting the project folder.",
        "pt": "Você precisa criar um Novo Projeto (definir um nome de projeto) ou selecionar um Projeto Anterior antes de definir a pasta do projeto.",
    },
    "msg_projects_migration_title": {"en": "Projects folder", "pt": "Pasta de projetos"},
    "msg_projects_migration_partial": {
        "en": "The projects folder is now called PROJECTS (formerly JOBS). Some projects could not be moved and remain in the JOBS folder - they are still listed and can be opened normally.",
        "pt": "A pasta de projetos agora se chama PROJECTS (antes JOBS). Alguns projetos não puderam ser movidos e continuam na pasta JOBS - eles continuam listados e podem ser abertos normalmente.",
    },
    "msg_data_folder_migration_partial": {
        "en": "The data subfolder of each project is now called DATA (formerly DATA_BASES). Some items could not be moved and remain in DATA_BASES (nothing was overwritten): {items}",
        "pt": "A subpasta de dados de cada projeto agora se chama DATA (antes DATA_BASES). Alguns itens não puderam ser movidos e continuam em DATA_BASES (nada foi sobrescrito): {items}",
    },
    "msg_projects_migration_conflicts": {
        "en": "Already present in PROJECTS (not overwritten): {names}",
        "pt": "Já existentes em PROJECTS (não sobrescritos): {names}",
    },
    "msg_projects_migration_errors": {"en": "Errors: {errors}", "pt": "Erros: {errors}"},
    "msg_project_load_error": {
        "en": "Could not load saved project settings from the selected project.\n\nDetails:\n{e}",
        "pt": "Não foi possível carregar as configurações salvas do projeto selecionado.\n\nDetalhes:\n{e}",
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
    "s1_grp_target_filter": {"en": "Target Filter", "pt": "Filtro de Alvo"},
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
    "s1_grp_cell_filter": {"en": "Cell line Filter", "pt": "Filtro de Linhagem Celular"},
    "s1_btn_explore_cell": {"en": "Explore by Cell-line", "pt": "Explorar por linhagem celular"},
    "s1_grp_assay_filter": {"en": "Assay/Activity Filter", "pt": "Filtro de Ensaio/Atividade"},
    "s1_lbl_assay_type": {"en": "Assay Type:", "pt": "Tipo de Ensaio:"},
    "s1_lbl_assay_metric": {"en": "Activity Type:", "pt": "Tipo de Atividade:"},
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
    "s1_grp_validity_filter": {"en": "Validity Filter", "pt": "Filtro de Validade"},
    "s1_chk_validity_comment": {"en": "Validity Comment", "pt": "Comentário de Validade"},
    "s1_chk_validity_description": {"en": "Validity Description", "pt": "Descrição de Validade"},
    "s1_tooltip_validity_comment": {
        "en": "Select data_validity_comment value(s) that flag a problem with the data. Compounds whose data_validity_comment matches one of the selected values are REMOVED from the dataset when 'Generate Base Dataset' runs - everything else (including empty/blank) is kept.",
        "pt": "Selecione o(s) valor(es) de data_validity_comment que sinalizam problema no dado. Os compostos cujo data_validity_comment corresponder a um dos valores selecionados são REMOVIDOS do dataset ao rodar 'Generate Base Dataset' - todo o resto (inclusive vazio) é mantido.",
    },
    "s1_tooltip_validity_description": {
        "en": "Select data_validity_description value(s) that flag a problem with the data. Compounds whose data_validity_description matches one of the selected values are REMOVED from the dataset when 'Generate Base Dataset' runs - everything else (including empty/blank) is kept.",
        "pt": "Selecione o(s) valor(es) de data_validity_description que sinalizam problema no dado. Os compostos cujo data_validity_description corresponder a um dos valores selecionados são REMOVIDOS do dataset ao rodar 'Generate Base Dataset' - todo o resto (inclusive vazio) é mantido.",
    },
    "s1_grp_explore_molecules": {"en": "Explore Molecules", "pt": "Explorar Moléculas"},
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
    "s2_chk_use_standard_values": {"en": "Use Standard values", "pt": "Usar valores padronizados"},
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
    "s2_lbl_select_relation_column_rep": {"en": "3. Select the \nrelation column:", "pt": "3. Selecione a \ncoluna de relação:"},
    "s2_tooltip_relation_values_rep": {
        "en": "Values found in the selected relation column (e.g. '=', '>', '>=', '<', '<='). Select the ones you want REMOVED - typically the censored ones (>, >=, <, <=), which mean the assay only bounds the true value (e.g. 'IC50 > 10000 nM' = inactive up to the highest dose tested, not an exact 10000 nM measurement).",
        "pt": "Valores encontrados na coluna de relação selecionada (ex.: '=', '>', '>=', '<', '<='). Selecione os que você quer REMOVER - tipicamente os censurados (>, >=, <, <=), que significam que o ensaio só limita o valor real (ex.: 'IC50 > 10000 nM' = inativo até a dose máxima testada, não uma medida exata de 10000 nM).",
    },
    "s2_btn_remove_value_rep": {"en": "Remove by \nrelation", "pt": "Remover por \nrelação"},
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
    "stats_tooltip_margin_error": {
        "en": "Half-width of the confidence interval for a single proportion (precision wanted, e.g. +/-5 points). It is NOT the same as the Type I error: the confidence level (and alpha) sets how sure you want to be, the margin of error sets how precise. Used only by the single-proportion sample size.",
        "pt": "Meia-largura do intervalo de confiança de uma única proporção (precisão desejada, ex.: +/-5 pontos). NÃO é o mesmo que o erro Tipo I: o nível de confiança (e o α) define o quão seguro você quer estar, a margem de erro define o quão preciso. Usada só no tamanho amostral de uma única proporção.",
    },
    "stats_lbl_population_size": {"en": "Population Size (N):", "pt": "Tamanho da População (N):"},
    "stats_lbl_n1": {"en": "Sample size Group 1 (n1):", "pt": "Tamanho amostral Grupo 1 (n1):"},
    "stats_lbl_n2": {"en": "Sample size Group 2 (n2):", "pt": "Tamanho amostral Grupo 2 (n2):"},
    "stats_lbl_n1n2_hint": {
        "en": "(used only by 'Calculate Statistical Power' - the actual number of observations in each of the 2 compared groups, not the total dataset size)",
        "pt": "(usado só em 'Calcular Poder Estatístico' - o número real de observações em cada um dos 2 grupos comparados, não o tamanho do dataset inteiro)",
    },
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
    "s4_lbl_bits_number": {"en": "Bits number:", "pt": "Número de bits:"},
    "s4_tooltip_bits_number": {
        "en": "Fingerprint size (number of bits), only adjustable for descriptors computed "
              "directly by RDKit: ECFP4, FCFP6, ECFP4 counting, Avalon FP, Topological Torsion, "
              "Pattern FP and Atom Pair. Disabled for PaDEL's own fingerprints (MACCS, Pubchem, "
              "Fingerprinter, KlekotaRoth, etc.) and for 1D/2D or 3D descriptors, which have a "
              "fixed size not configurable through PaDEL. Select at least one of those RDKit "
              "descriptors above to enable this field.",
        "pt": "Tamanho do fingerprint (número de bits), ajustável apenas para descritores "
              "calculados diretamente pelo RDKit: ECFP4, FCFP6, ECFP4 counting, Avalon FP, "
              "Topological Torsion, Pattern FP e Atom Pair. Fica desabilitado para os "
              "fingerprints do próprio PaDEL (MACCS, Pubchem, Fingerprinter, KlekotaRoth etc.) e "
              "para descritores 1D/2D ou 3D, que têm tamanho fixo, não configurável pelo PaDEL. "
              "Selecione ao menos um desses descritores RDKit acima para habilitar este campo.",
    },
    "s4_chk_fp_chirality": {"en": "Chirality", "pt": "Quiralidade"},
    "s4_tooltip_fp_chirality": {
        "en": "Include chirality (stereochemistry) as an atom invariant when computing the "
              "fingerprint - only applies to the same RDKit-computed descriptors as 'Bits "
              "number' (ECFP4, FCFP6, ECFP4 counting, Topological Torsion, Atom Pair; ignored by "
              "Avalon FP and Pattern FP). Checked (default) distinguishes stereoisomers that "
              "would otherwise map to the same bits; uncheck to match RDKit's own default "
              "(achiral) behavior.",
        "pt": "Inclui a quiralidade (estereoquímica) como invariante de átomo ao calcular o "
              "fingerprint - só se aplica aos mesmos descritores calculados pelo RDKit que "
              "'Bits number' (ECFP4, FCFP6, ECFP4 counting, Topological Torsion, Atom Pair; "
              "ignorado por Avalon FP e Pattern FP). Marcado (padrão) distingue estereoisômeros "
              "que de outra forma cairiam nos mesmos bits; desmarque para o comportamento padrão "
              "do próprio RDKit (aquiral).",
    },
    "s4_lbl_select_structure_column": {"en": "Structure \nColumn:", "pt": "Coluna \nde Estrutura:"},
    "s4_btn_select_structures_file": {"en": "Or Select \nStructures File", "pt": "Ou Selecione o \nArquivo de Estruturas"},
    "s4_tooltip_select_structures_file": {
        "en": "Select a folder with structure files: .smi, .sdf and .mol are read natively; .mol2, .pdb, .pdbqt and .xyz require OpenBabel (install it in HOME > Installation Requirements). Builds a [name, canonical_smiles] table - the original 3D geometry (when the file has one) is kept aside for 'Retain 3D coordinates' in Generate Descriptors.",
        "pt": "Selecione uma pasta com arquivos de estrutura: .smi, .sdf e .mol são lidos nativamente; .mol2, .pdb, .pdbqt e .xyz precisam do OpenBabel (instale em HOME > Installation Requirements). Monta uma tabela [nome, canonical_smiles] - a geometria 3D original (quando o arquivo tiver uma) é guardada à parte para o 'Retain 3D coordinates' do Generate Descriptors.",
    },
    "s4_lbl_select_bioactivity_column": {"en": "Bioactivity \nColumn:", "pt": "Coluna \nde Bioatividade:"},
    "s4_lbl_select_name_column": {"en": "Name \nColumn:", "pt": "Coluna \nde Nome:"},
    "s4_chk_remove_salt": {"en": "Remove salt", "pt": "Remover sal"},
    "s4_chk_detect_aromaticity": {"en": "Detect Aromaticity", "pt": "Detectar Aromaticidade"},
    "s4_chk_standardize_tautomers": {"en": "Standardize Tautomers", "pt": "Padronizar Tautômeros"},
    "s4_chk_standardize_nitro": {"en": "Standardize Nitro Groups", "pt": "Padronizar Grupos Nitro"},
    "s4_chk_retain_3d": {"en": "Retain 3D coordinates", "pt": "Manter coordenadas 3D"},
    "s4_tooltip_retain_3d": {
        "en": "Only affects the '3D' descriptor group. When EITHER this or 'Convert to 3D' is "
              "checked: compounds loaded via 'Or Select Structures File' from a real 3D source "
              "(.sdf/.mol2/.pdb/.pdbqt/.xyz with actual 3D coordinates) use that ORIGINAL "
              "geometry; compounds without native 3D instead get a small conformational ensemble "
              "(ETKDGv3 + MMFF/UFF optimization + RMSD-based pruning of near-duplicates), and the "
              "3D descriptors are computed as a Boltzmann-weighted average over that ensemble - "
              "not a single arbitrary conformer. When BOTH are unchecked (default): PaDEL "
              "generates a single 3D conformer internally, like before.",
        "pt": "Só afeta o grupo de descritores '3D'. Quando ESTE ou 'Convert to 3D' estiver "
              "marcado: compostos carregados via 'Or Select Structures File' a partir de uma "
              "fonte 3D real (.sdf/.mol2/.pdb/.pdbqt/.xyz com coordenadas 3D de fato) usam essa "
              "geometria ORIGINAL; compostos sem 3D nativo recebem em vez disso um pequeno "
              "ensemble conformacional (ETKDGv3 + otimização MMFF/UFF + pruning de "
              "quase-duplicatas por RMSD), e os descritores 3D são calculados como uma média "
              "ponderada por Boltzmann sobre esse ensemble - não uma única conformação "
              "arbitrária. Quando AMBOS estiverem desmarcados (padrão): o PaDEL gera uma única "
              "conformação 3D internamente, como antes.",
    },
    "s4_chk_convert_3d": {"en": "Convert to 3D", "pt": "Converter para 3D"},
    "s4_tooltip_convert_3d": {
        "en": "Only affects the '3D' descriptor group. Has the same effect as 'Retain 3D "
              "coordinates' above (checking either one is enough) - see its tooltip for details "
              "on the native-geometry/conformational-ensemble behavior this triggers.",
        "pt": "Só afeta o grupo de descritores '3D'. Tem o mesmo efeito de 'Manter coordenadas 3D' "
              "acima (marcar qualquer um dos dois já basta) - veja o tooltip dele para os "
              "detalhes do comportamento de geometria nativa/ensemble conformacional que isso "
              "aciona.",
    },
    "s4_btn_split_external": {"en": "Split External\nDataFrame", "pt": "Separar\nDataFrame Externo"},
    "s4_lbl_external_size": {"en": "External Size:", "pt": "Tamanho Externo:"},
    "s4_lbl_split_method": {"en": "Split Method:", "pt": "Método:"},
    "msg_title_split_external": {"en": "Split External DataFrame", "pt": "Separar DataFrame Externo"},
    "s4_tooltip_external_size": {
        "en": "Fraction of the current dataframe (Select DataFrame) set aside as the EXTERNAL validation set.",
        "pt": "Fração do dataframe atual (Select DataFrame) separada como conjunto de validação EXTERNA.",
    },
    "s4_tooltip_ext_split_method": {
        "en": "Random: random split, reproducible with this step's Random State.\n"
              "Kennard-Stone / Sphere Exclusion: rational splits on the descriptor columns of 'Feature Columns Range' "
              "(the external set lies inside the chemical space of the internal one) - same methods as the 'Split:' of STEP 4.",
        "pt": "Random: divisão aleatória, reprodutível pelo Random State desta etapa.\n"
              "Kennard-Stone / Sphere Exclusion: divisões racionais sobre as colunas de descritores de 'Feature Columns Range' "
              "(o conjunto externo fica dentro do espaço químico do interno) - os mesmos métodos do 'Split:' da ETAPA 4.",
    },
    "s4_tooltip_split_external": {
        "en": "Splits the current dataframe into an INTERNAL and an EXTERNAL set (the original file is kept). Do it BEFORE "
              "scaling, selection and projection, so the external set does not influence any modelling decision (OECD Principle 4). "
              "Both files are saved in DATA/INTERNAL_DATA: <name>_<pct>_Internal.csv becomes the current dataframe and "
              "<name>_<pct>_External.csv is the one to choose in 'Select External DataFrame' (STEP 4 and 5).",
        "pt": "Divide o dataframe atual em um conjunto INTERNO e um EXTERNO (o arquivo original é mantido). Faça isso ANTES do "
              "escalonamento, da seleção e da projeção, para o conjunto externo não influenciar nenhuma decisão de modelagem "
              "(Princípio 4 da OECD). Os dois arquivos ficam em DATA/INTERNAL_DATA: <nome>_<pct>_Internal.csv passa a ser o dataframe atual e "
              "<nome>_<pct>_External.csv é o que deve ser escolhido no 'Select External DataFrame' (ETAPAS 4 e 5).",
    },
    "s4_msg_split_no_df": {
        "en": "Select the dataframe to split first (Select DataFrame, at the top of this step).",
        "pt": "Selecione antes o dataframe a ser dividido (Select DataFrame, no topo desta etapa).",
    },
    "s4_msg_split_too_small": {
        "en": "The dataframe has only {n} rows - too few to split with this External Size.",
        "pt": "O dataframe tem apenas {n} linhas - poucas para dividir com este Tamanho Externo.",
    },
    "s4_msg_split_no_features": {
        "en": "Kennard-Stone and Sphere Exclusion need the descriptor columns: set a valid 'Feature Columns Range' (Dimensionality Reduction group) or use the Random method.",
        "pt": "Kennard-Stone e Sphere Exclusion precisam das colunas de descritores: defina um 'Feature Columns Range' válido (grupo Dimensionality Reduction) ou use o método Random.",
    },
    "s4_msg_split_overwrite": {
        "en": "These files already exist and will be overwritten:\n{files}\n\nContinue?",
        "pt": "Estes arquivos já existem e serão sobrescritos:\n{files}\n\nContinuar?",
    },
    "s4_msg_split_done": {
        "en": "Split done ({method}): {n_int} internal and {n_ext} external compounds.\n\nInternal (now the current dataframe):\n{int_path}\n\nExternal:\n{ext_path}",
        "pt": "Divisão concluída ({method}): {n_int} compostos internos e {n_ext} externos.\n\nInterno (agora o dataframe atual):\n{int_path}\n\nExterno:\n{ext_path}",
    },
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
    "btn_select_ad_df": {"en": "Select AD DataFrame", "pt": "Selecionar DataFrame de DA"},
    "s5_lbl_usi": {"en": "USI:", "pt": "USI:"},
    "s5_subtab_predict": {"en": "Predict", "pt": "Predizer"},
    "lbl_descriptors_columns_range": {"en": "Descriptors Columns:", "pt": "Colunas de Descritores:"},
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
    "s6_chk_with_y": {"en": "With Y", "pt": "Com Y"},
    "s6_tooltip_with_y": {
        "en": "Checked automatically when the External DataFrame has the same Y column used to train "
              "the models. When checked, Predict also computes the external predictivity metrics "
              "(RMSEP, Q2F1-F3, CCC, Golbraikh-Tropsha, rm2) on the rows that have an observed Y.",
        "pt": "Marcado automaticamente quando o External DataFrame tem a mesma coluna Y usada no treino "
              "dos modelos. Quando marcado, o Predict também calcula as métricas de predictivity externas "
              "(RMSEP, Q2F1-F3, CCC, Golbraikh-Tropsha, rm2) nas linhas que têm Y observado.",
    },
    "s6_msg_with_y_not_found": {
        "en": "The Y column used for training ('{y}') was not found in the External DataFrame (or it has "
              "no usable values). 'With Y' was unchecked.",
        "pt": "A coluna Y usada no treino ('{y}') não foi encontrada no External DataFrame (ou não tem "
              "valores utilizáveis). 'Com Y' foi desmarcado.",
    },
    "s6_msg_with_y_too_few": {
        "en": "Only {n} row(s) of the External DataFrame have an observed Y - at least 3 are needed to "
              "compute the external metrics. The predictions were saved normally.",
        "pt": "Apenas {n} linha(s) do External DataFrame têm Y observado - são necessárias ao menos 3 "
              "para calcular as métricas externas. As predições foram salvas normalmente.",
    },
    "s6_btn_evaluate_test": {"en": "Evaluate Test", "pt": "Avaliar Teste"},
    "s6_tooltip_evaluate_test": {
        "en": "Final predictivity evaluation (OECD Principle 4) of the selected model(s) on the test set "
              "held out in Screening. Do it once, with the final (tuned and validated) model.",
        "pt": "Avaliação final de predictivity (Princípio 4 da OECD) do(s) modelo(s) selecionado(s) no "
              "conjunto teste separado no Screening. Faça uma única vez, com o modelo final (tunado e validado).",
    },
    "s6_msg_evaluate_test_confirm": {
        "en": "The test set ({n} compounds) took no part in Screening, Tuning or Validation. It should "
              "be used only once, to report the predictivity of the final model - using it to go back "
              "and change the model would turn it into training data.\n\nEvaluate the selected model(s) now?",
        "pt": "O conjunto teste ({n} compostos) não participou do Screening, do Tuning nem da Validation. "
              "Ele deve ser usado uma única vez, para reportar a predictivity do modelo final - usá-lo para "
              "voltar e alterar o modelo o transformaria em dado de treino.\n\nAvaliar o(s) modelo(s) "
              "selecionado(s) agora?",
    },
    "s6_tooltip_test_size": {
        "en": "Fraction of the Internal DataFrame held out as the test set (final predictivity evaluation). "
              "0 = no test set: the whole Internal DataFrame is used for Screening, Tuning and Validation, "
              "and external validation is done with the External DataFrame (Predict with 'With Y').",
        "pt": "Fração do Internal DataFrame separada como conjunto teste (avaliação final de predictivity). "
              "0 = sem conjunto teste: todo o Internal DataFrame é usado no Screening, Tuning e Validation, "
              "e a validação externa é feita com o External DataFrame (Predict com 'Com Y').",
    },
    "s6_msg_no_test_set": {
        "en": "This USI has no test set (Test Size = 0): the whole Internal DataFrame was used for training. "
              "For external validation, select the External DataFrame and run Predict with 'With Y' checked.",
        "pt": "Esta USI não tem conjunto teste (Tamanho do Teste = 0): todo o Internal DataFrame foi usado no treino. "
              "Para a validação externa, selecione o External DataFrame e rode o Predict com 'Com Y' marcado.",
    },
    "s6_msg_chart_no_test_set": {
        "en": "The chart '{chart}' evaluates the model on the test set, and this USI has no test set (Test Size = 0). "
              "Use 'Plot CV Predictions' (Validation and Model Robustness) to inspect the model on the training set.",
        "pt": "O gráfico '{chart}' avalia o modelo no conjunto teste, e esta USI não tem conjunto teste (Tamanho do "
              "Teste = 0). Use 'Gráfico da CV' (Validação e Robustez do Modelo) para inspecionar o modelo no treino.",
    },
    "s6_btn_cv_plot": {"en": "Plot CV Predictions", "pt": "Gráfico da CV"},
    "s6_tooltip_cv_plot": {
        "en": "Predicted vs Experimental (regression) or Confusion Matrix (classification) with the out-of-fold "
              "predictions of the last cross-validation of the selected model - training set only, the test set is not used.",
        "pt": "Predito vs Experimental (regressão) ou Matriz de Confusão (classificação) com as predições out-of-fold "
              "da última validação cruzada do modelo selecionado - só o conjunto de treino, o teste não é usado.",
    },
    "s6_msg_cv_plot_run_first": {
        "en": "Run Cross-Validation for the model '{model}' first (KFold, StratifiedKFold, LOOCV, Time Series or Nested CV).",
        "pt": "Rode primeiro a validação cruzada do modelo '{model}' (KFold, StratifiedKFold, LOOCV, Time Series ou Nested CV).",
    },
    "s6_msg_cv_plot_unavailable": {
        "en": "The method '{method}' predicts the same compound more than once (Leave-P-Out with p > 1, Bootstrap), so "
              "there is no single out-of-fold prediction per compound to plot. Use KFold, StratifiedKFold, LOOCV or Nested CV.",
        "pt": "O método '{method}' prevê o mesmo composto mais de uma vez (Leave-P-Out com p > 1, Bootstrap), então "
              "não há uma predição out-of-fold única por composto. Use KFold, StratifiedKFold, LOOCV ou Nested CV.",
    },
    "s6_lbl_split_method": {"en": "Split:", "pt": "Divisão:"},
    "s6_tooltip_split_method": {
        "en": "How the Internal DataFrame is divided into training and test sets.\n"
              "Random: random split, reproducible with the Random State (default).\n"
              "Kennard-Stone: picks the training set to cover the descriptor space (max-min distance); "
              "the test set lies inside the training space. Exact test size.\n"
              "Sphere Exclusion (Golbraikh & Tropsha): sphere centres go to training and the compounds "
              "inside each sphere go to test; the radius is tuned to approach the chosen test size.\n"
              "Rational methods use Euclidean distances on autoscaled descriptors (first principal "
              "components, up to 50, when there are more columns) and are applied per class in classification.",
        "pt": "Como o Internal DataFrame é dividido em conjuntos de treino e teste.\n"
              "Random: divisão aleatória, reprodutível pelo Random State (padrão).\n"
              "Kennard-Stone: escolhe o treino para cobrir o espaço dos descritores (distância max-min); "
              "o teste fica dentro do espaço do treino. Tamanho do teste exato.\n"
              "Sphere Exclusion (Golbraikh & Tropsha): os centros das esferas vão para o treino e os "
              "compostos dentro de cada esfera vão para o teste; o raio é ajustado para se aproximar do "
              "tamanho de teste escolhido.\n"
              "Os métodos racionais usam distâncias euclidianas nos descritores autoescalados (primeiras "
              "componentes principais, até 50, quando há mais colunas) e são aplicados por classe na classificação.",
    },
    "msg_title_refit": {"en": "Refit", "pt": "Refit"},
    "s6_btn_refit": {"en": "Refit", "pt": "Refit"},
    "s6_tooltip_refit": {
        "en": "Retrains the selected model(s) with the SAME hyperparameters on training + test sets (100% of the "
              "Internal DataFrame) and saves each one as '<name>_refit'. Use it after Evaluate Test, to get a final "
              "model with all data: the test metrics remain those of the source model (a conservative estimate for "
              "the _refit model), whose external validation is done with Predict + 'With Y'.",
        "pt": "Retreina o(s) modelo(s) selecionado(s) com os MESMOS hiperparâmetros em treino + teste (100% do "
              "Internal DataFrame) e salva cada um como '<nome>_refit'. Use depois do Evaluate Test, para ter um "
              "modelo final com todos os dados: as métricas de teste continuam sendo as do modelo de origem (uma "
              "estimativa conservadora para o _refit), cuja validação externa é feita com Predict + 'Com Y'.",
    },
    "s6_msg_refit_no_test": {
        "en": "This USI has no test set (Test Size = 0): its models were already trained on 100% of the Internal "
              "DataFrame, so there is nothing to refit.",
        "pt": "Esta USI não tem conjunto teste (Tamanho do Teste = 0): seus modelos já foram treinados com 100% do "
              "Internal DataFrame, então não há o que retreinar.",
    },
    "s6_msg_refit_already": {
        "en": "These models are already refit models (trained on training + test): {models}.",
        "pt": "Estes modelos já são modelos refit (treinados em treino + teste): {models}.",
    },
    "s6_msg_refit_confirm": {
        "en": "Refit {models} with the same hyperparameters on training ({n_train}) + test ({n_test}) = {n_total} "
              "compounds?\n\nEach one is saved as '<name>_refit' (the source model is kept). The test set then "
              "becomes training data of the _refit model: Evaluate Test, the test-based Performance Charts and the "
              "Interpretability Tools are not available for it - its external validation is done with Predict + "
              "'With Y' on the External DataFrame. Run Evaluate Test on the source model first, if you have not yet.",
        "pt": "Retreinar {models} com os mesmos hiperparâmetros em treino ({n_train}) + teste ({n_test}) = {n_total} "
              "compostos?\n\nCada um é salvo como '<nome>_refit' (o modelo de origem é mantido). O conjunto teste "
              "passa a ser dado de treino do modelo _refit: Evaluate Test, os gráficos de Performance Charts "
              "baseados no teste e as Interpretability Tools não ficam disponíveis para ele - sua validação externa é "
              "feita com Predict + 'Com Y' no External DataFrame. Rode antes o Evaluate Test no modelo de origem, se "
              "ainda não rodou.",
    },
    "s6_msg_refit_done": {
        "en": "Refit done ({n_total} compounds): {models}.",
        "pt": "Refit concluído ({n_total} compostos): {models}.",
    },
    "s6_msg_refit_no_test_eval": {
        "en": "Refit models were trained WITH the test set, so they cannot be evaluated on it: {models}. Their test "
              "metrics are those of the source models; use Predict + 'With Y' on the External DataFrame for their "
              "external validation.",
        "pt": "Modelos refit foram treinados COM o conjunto teste e por isso não podem ser avaliados nele: {models}. "
              "Suas métricas de teste são as dos modelos de origem; use Predict + 'Com Y' no External DataFrame para "
              "a validação externa deles.",
    },
    "s6_msg_refit_no_test_chart": {
        "en": "The chart '{chart}' evaluates the model on the test set, which is part of the training data of the "
              "refit model '{model}' - it would show fit, not prediction. Plot it for the source model instead.",
        "pt": "O gráfico '{chart}' avalia o modelo no conjunto teste, que faz parte do treino do modelo refit "
              "'{model}' - mostraria ajuste, não predição. Gere-o para o modelo de origem.",
    },
    "s6_msg_refit_no_tuning": {
        "en": "'{model}' is a refit (final) model. To tune, select its source model '{source}' and refit again afterwards.",
        "pt": "'{model}' é um modelo refit (final). Para tunar, selecione o modelo de origem '{source}' e faça o refit de novo depois.",
    },
    "s6_lbl_screening_cv_folds": {"en": "CV Folds (train):", "pt": "Folds da CV (treino):"},
    "s6_tooltip_screening_cv_folds": {
        "en": "Number of k-fold cross-validation folds used to rank the models. The cross-validation "
              "runs on the training set only; the test set is kept aside for the final evaluation.",
        "pt": "Número de folds da validação cruzada k-fold usada para ranquear os modelos. A validação "
              "cruzada roda somente no conjunto de treino; o conjunto de teste fica reservado para a "
              "avaliação final.",
    },
    "lbl_status": {"en": "Status:", "pt": "Status:"},
    "s6_fmt_screening_progress": {"en": "Screening: %p%", "pt": "Seleção: %p%"},
    "btn_select_all": {"en": "Select All", "pt": "Selecionar Tudo"},
    "s6_btn_view_train_test_freq": {"en": "View Frequency", "pt": "Ver Frequência"},
    "s6_btn_run_screening": {"en": "Run Screening", "pt": "Executar Seleção"},
    "s6_grp_hyperparameter_tuning": {"en": "Hyperparameter Tuning", "pt": "Ajuste de Hiperparâmetros"},
    "lbl_model": {"en": "Model:", "pt": "Modelo:"},
    "lbl_method": {"en": "Method:", "pt": "Método:"},
    "s6_lbl_cv_folds": {"en": "CV folds:", "pt": "Folds de CV:"},
    "s6_lbl_n_iter": {"en": "n_iter (Randomized/Bayesian):", "pt": "n_iter (Randomized/Bayesian):"},
    "s6_col_hyperparameter": {"en": "Hyperparameter", "pt": "Hiperparâmetro"},
    "s6_col_values_to_test": {"en": "Values to test (comma-separated)", "pt": "Valores a testar (separados por vírgula)"},
    "s6_btn_run_tuning": {"en": "Run Tuning", "pt": "Executar Ajuste"},
    "s6_btn_add_hyperparam_row": {"en": "+ Add row", "pt": "+ Adicionar linha"},
    "s6_btn_remove_hyperparam_row": {"en": "− Remove row", "pt": "− Remover linha"},
    "lbl_parameter": {"en": "Parameter:", "pt": "Parâmetro:"},
    "btn_plot": {"en": "Plot", "pt": "Plotar"},
    "s6_grp_validation": {"en": "Validation and Model Robustness", "pt": "Validação e Robustez do Modelo"},
    "s6_lbl_folds": {"en": "Folds:", "pt": "Folds:"},
    "s6_lbl_p_leave_p_out": {"en": "p (Leave-P-Out):", "pt": "p (Leave-P-Out):"},
    "s6_btn_run_cross_validation": {"en": "Run Cross-Validation", "pt": "Executar Validação Cruzada"},
    "s6_grp_remove_model_predict": {"en": "Refit, Evaluate, Predict and Remove", "pt": "Retreinar, Avaliar, Predizer e Remover"},
    "s6_chk_remove_descriptors": {"en": "Remove Descriptors", "pt": "Remover Descritores"},
    "s6_btn_remove_model": {"en": "Remove Model", "pt": "Remover Modelo"},
    "s6_grp_performance_charts": {"en": "Performance Charts", "pt": "Gráficos de Desempenho"},
    "s6_chk_metric_legend": {"en": "Metric Legend", "pt": "Legenda de Métricas"},
    "s6_tooltip_metric_legend": {
        "en": "Add R2, MAE, RMSE and MSE to the chart legend (regression charts only).",
        "pt": "Adiciona R2, MAE, RMSE e MSE à legenda do gráfico (somente gráficos de regressão).",
    },
    "s6_lbl_yrand_n": {"en": "Permutations (n):", "pt": "Permutações (n):"},
    "s6_tooltip_yrand_n": {
        "en": "Number of Y-scrambling runs. Each run shuffles the response column, retrains the "
              "selected model with the same cross-validation scheme (same 'Folds' as "
              "Cross-Validation, above), and records its score. 100 is the standard literature "
              "default.",
        "pt": "Número de execuções da Y-scrambling. Cada execução embaralha a coluna resposta, "
              "retreina o modelo selecionado com o mesmo esquema de validação cruzada (mesmo "
              "'Folds' do Cross-Validation, acima), e registra sua métrica. 100 é o padrão usual "
              "na literatura.",
    },
    "s6_btn_yrand_run": {"en": "Run Y-Scrambling", "pt": "Executar Y-Scrambling"},
    "s6_tooltip_yrand_run": {
        "en": "OECD-recommended robustness check: retrains the model selected in Hyperparameter "
              "Tuning's 'Model' combobox n times with the response column shuffled (same X, same "
              "number of Folds as Cross-Validation above, same 'Sort metric'), and compares the "
              "resulting metric distribution against the real (unshuffled) model - a clear gap is "
              "evidence the real model isn't just chance correlation. Requires Run Screening to "
              "have been run first (uses the same X/y). Runs the n permutations in parallel "
              "across CPU cores.",
        "pt": "Verificação de robustez recomendada pela OECD: retreina o modelo selecionado na caixa "
              "'Model' do Hyperparameter Tuning n vezes com a coluna resposta embaralhada (mesmo X, "
              "mesmo número de Folds do Cross-Validation acima, mesma 'Sort metric'), e compara a "
              "distribuição de métricas resultante contra o modelo real (não embaralhado) - uma "
              "diferença clara é evidência de que o modelo real não é fruto de correlação ao "
              "acaso. Requer ter rodado Run Screening antes (usa o mesmo X/y). Executa as n "
              "permutações em paralelo entre os núcleos da CPU.",
    },
    "msg_step6_build_error_title": {"en": "STEP 6 build error", "pt": "Erro ao construir a ETAPA 6"},
    "msg_step6_build_error": {
        "en": "There was an error building the STEP 6 TAB:\n{e}",
        "pt": "Ocorreu um erro ao construir a aba da ETAPA 6:\n{e}",
    },

    # ---------------------------------------------------------------- STEP 6 (Applicability Domain)
    "s7_grp_set_ad_params": {"en": "Set AD Parameters", "pt": "Definir Parâmetros de DA"},
    "s7_lbl_k_knn": {"en": "k (kNN):", "pt": "k (kNN):"},
    "s7_lbl_alpha_chi2": {"en": "Mahalanobis α (coverage):", "pt": "α da Mahalanobis (cobertura):"},
    "s7_tooltip_ad_alpha": {
        "en": "Confidence level for the Mahalanobis criterion, used by BOTH cutoff modes: with 'Empirical percentile' it is literally the fraction of training compounds kept inside the cutoff; with 'Theoretical chi2' it is the alpha of sqrt(chi2_p(alpha)).",
        "pt": "Nível de confiança do critério Mahalanobis, usado pelos DOIS modos de corte: com 'Empirical percentile' é, literalmente, a fração de compostos de treino mantida dentro do corte; com 'Theoretical chi2' é o alpha de sqrt(chi2_p(alpha)).",
    },
    "s7_lbl_ad_workers": {"en": "Workers (0 = auto):", "pt": "Núcleos (0 = auto):"},
    "s7_tooltip_ad_workers": {
        "en": "Threads for the Compute AD workload (kNN, Tanimoto, RDKit). 0 = all available cores.",
        "pt": "Threads para o cálculo do Compute AD (kNN, Tanimoto, RDKit). 0 = todos os núcleos disponíveis.",
    },
    "s7_lbl_ad_knn_agg": {"en": "kNN aggregation:", "pt": "Agregação kNN:"},
    "s7_tooltip_ad_knn_agg": {
        "en": "How the k neighbour distances are reduced to one number, applied to BOTH the training cutoff and the external value. 'Mean of k' = average of the k nearest; 'k-th neighbour' = distance to the farthest of the k.",
        "pt": "Como as distâncias dos k vizinhos viram um único número, aplicado TANTO ao corte do treino QUANTO ao valor externo. 'Média dos k' = média dos k mais próximos; 'k-ésimo vizinho' = distância ao mais distante dos k.",
    },
    "s7_lbl_ad_percentile": {"en": "kNN percentile:", "pt": "Percentil kNN:"},
    "s7_tooltip_ad_percentile": {
        "en": "Percentile of the training kNN-distance distribution used as the in-domain cutoff (default 95).",
        "pt": "Percentil da distribuição de distâncias kNN do treino usado como corte do domínio (padrão 95).",
    },
    "s7_lbl_ad_lev_cutoff": {"en": "Leverage cutoff:", "pt": "Corte do leverage:"},
    "s7_tooltip_ad_lev_cutoff": {
        "en": "'Theoretical' = multiplier*(p+1)/n (Williams-plot convention). 'Empirical percentile' = percentile (100*alpha) of the real h_train distribution; note leverage is an affine function of the squared Mahalanobis distance, so in empirical mode this criterion becomes nearly redundant with the Mahalanobis one.",
        "pt": "'Theoretical' = multiplicador*(p+1)/n (convenção do Williams plot). 'Empirical percentile' = percentil (100*alpha) da distribuição real de h_train; lembre que o leverage é função afim da distância de Mahalanobis ao quadrado, então no modo empírico este critério fica quase redundante com o de Mahalanobis.",
    },
    "s7_tooltip_ad_lev_mult": {
        "en": "Multiplier for the theoretical leverage cutoff multiplier*(p+1)/n: 2, 2.5 or 3 (2 stricter, 3 = classic Williams-plot value). Ignored in 'Empirical percentile' mode.",
        "pt": "Multiplicador do corte teórico de leverage multiplicador*(p+1)/n: 2, 2,5 ou 3 (2 mais estrito, 3 = valor clássico do Williams plot). Ignorado no modo 'Empirical percentile'.",
    },
    "s7_lbl_ad_tani_cutoff": {"en": "Tanimoto cutoff:", "pt": "Corte do Tanimoto:"},
    "s7_tooltip_ad_tani_cutoff": {
        "en": "'Fixed threshold' = the value in the box beside it (a compound is in-domain if its max Tanimoto to training >= threshold). 'Empirical percentile' = the (100*(1-alpha)) percentile of each training compound's max Tanimoto to the rest of training (self-calibrating, but sensitive to near-duplicates in the training set and needs the train x train Tanimoto).",
        "pt": "'Fixed threshold' = o valor na caixa ao lado (o composto está no domínio se seu Tanimoto máximo ao treino >= limiar). 'Empirical percentile' = o percentil (100*(1-alpha)) do Tanimoto máximo de cada composto de treino aos demais do treino (auto-calibra, mas é sensível a quase-duplicados no treino e exige o Tanimoto treino x treino).",
    },
    "s7_tooltip_ad_tani_thr": {
        "en": "Fixed Tanimoto threshold (default 0.5; ~0.6 is common for MACCS keys). Used only in 'Fixed threshold' mode.",
        "pt": "Limiar fixo de Tanimoto (padrão 0,5; ~0,6 é comum para chaves MACCS). Usado apenas no modo 'Fixed threshold'.",
    },
    "s7_lbl_ad_mahal_cutoff": {"en": "Mahalanobis cutoff:", "pt": "Corte da Mahalanobis:"},
    "s7_tooltip_ad_mahal_cutoff": {
        "en": "'Empirical percentile' = cutoff at percentile (100*alpha) of the real training Mahalanobis-distance distribution (alpha then literally = fraction of training inside). 'Theoretical chi2' = sqrt(chi2_p(alpha)), assumes multivariate normality and barely moves with alpha when p is large.",
        "pt": "'Empirical percentile' = corte no percentil (100*alpha) da distribuição real de distâncias de Mahalanobis do treino (alpha passa a ser, literalmente, a fração do treino contida). 'Theoretical chi2' = sqrt(chi2_p(alpha)), pressupõe normalidade multivariada e quase não muda com alpha quando p é grande.",
    },
    "s7_btn_compute_ad": {"en": "Compute AD", "pt": "Calcular DA"},
    "s7_fmt_ad_progress": {"en": "AD: %p%", "pt": "DA: %p%"},
    "s7_grp_ad_exploration": {"en": "AD Exploration", "pt": "Exploração de DA"},
    "s7_lbl_ad_expl_x": {"en": "X axis:", "pt": "Eixo X:"},
    "s7_lbl_ad_expl_y": {"en": "Y axis:", "pt": "Eixo Y:"},
    "s7_lbl_ad_expl_z": {"en": "Z axis (3D):", "pt": "Eixo Z (3D):"},
    "s7_lbl_ad_expl_compound": {"en": "Highlight compound(s):", "pt": "Destacar composto(s):"},
    "s7_lbl_ad_expl_desc": {"en": "Highlight descriptor(s):", "pt": "Destacar descritor(es):"},
    "s7_ph_ad_expl_filter": {"en": "Type to filter...", "pt": "Digite para filtrar..."},
    "s7_tooltip_ad_expl_compound": {
        "en": "Select one or more External compounds to highlight in the plot (click to toggle; type above to filter the list).",
        "pt": "Selecione um ou mais compostos do Externo para destacar no gráfico (clique para marcar/desmarcar; digite acima para filtrar a lista).",
    },
    "s7_tooltip_ad_expl_desc": {
        "en": "Select one or more binary fingerprint columns (present in both Internal and External). Compounds where the selected descriptor(s) = 1 are highlighted with a ring marker in the plot.",
        "pt": "Selecione uma ou mais colunas de fingerprint binário (presentes no Interno e no Externo). Os compostos onde o(s) descritor(es) selecionado(s) = 1 são destacados no gráfico com um marcador em anel.",
    },
    "s7_chk_ad_expl_hide_others": {"en": "Hide non-highlighted", "pt": "Ocultar não destacados"},
    "s7_tooltip_ad_expl_hide_others": {
        "en": "Show only compounds that are highlighted (selected in 'Highlight compound(s)') or match the selected descriptor(s) - everything else is hidden from the External layer. Ignored if nothing is selected.",
        "pt": "Mostra só os compostos destacados (marcados em 'Highlight compound(s)') ou que casam com o(s) descritor(es) selecionado(s) - o restante é ocultado da camada Externa. Ignorado se nada estiver selecionado.",
    },
    "s7_tooltip_ad_expl_desc_match": {
        "en": "'Any selected' = highlight compounds with at least one of the selected descriptors = 1 (OR). 'All selected' = only compounds with every selected descriptor = 1 (AND).",
        "pt": "'Any selected' = destaca compostos com pelo menos um dos descritores selecionados = 1 (OU). 'All selected' = só compostos com todos os descritores selecionados = 1 (E).",
    },
    "s7_lbl_ad_expl_plot_type": {"en": "Plot Type:", "pt": "Tipo de gráfico:"},
    "s7_tooltip_ad_expl_plot_type": {
        "en": "Select any combination: '3D scatter' (else 2D), 'Train as KDE density' (else scattered points), 'Marginal histograms (2D)' (ignored in 3D). 'Frequency' ignores X/Y/Z and Compute AD - it plots class counts from 'Select AD DataFrame' / 'Select Column:' instead.",
        "pt": "Selecione qualquer combinação: '3D scatter' (senão 2D), 'Train as KDE density' (senão pontos dispersos), 'Marginal histograms (2D)' (ignorado em 3D). 'Frequency' ignora X/Y/Z e o Compute AD - plota a contagem de classes de 'Select AD DataFrame' / 'Select Column:'.",
    },
    "s7_chk_ad_expl_thresholds": {"en": "Show cutoff lines", "pt": "Mostrar linhas de corte"},
    "s7_chk_ad_expl_show_ext": {"en": "Show external points", "pt": "Mostrar pontos externos"},
    "s7_chk_ad_expl_profile": {"en": "AD profile panel", "pt": "Painel de perfil de DA"},
    "s7_btn_ad_expl_pred": {"en": "Select Predictions CSV", "pt": "Selecionar CSV de Previsões"},
    "s7_lbl_ad_expl_pred_col": {"en": "Predicted column:", "pt": "Coluna prevista:"},
    "s7_btn_ad_expl_load": {"en": "LOAD", "pt": "LOAD"},
    "s7_tooltip_ad_expl_load": {
        "en": "Loads/refreshes the 'Highlight compound(s)' and 'Highlight descriptor(s)' lists from the current Compute AD result. Not automatic - click after a new Compute AD, since populating thousands of items has a cost.",
        "pt": "Carrega/atualiza as listas 'Highlight compound(s)' e 'Highlight descriptor(s)' a partir do resultado atual do Compute AD. Não é automático - clique após um novo Compute AD, já que popular milhares de itens tem custo.",
    },
    "s7_btn_ad_expl_plot": {"en": "Plot AD Exploration", "pt": "Plotar Exploração de DA"},
    "s7_msg_ad_reference_train": {
        "en": "Applicability domain defined on the TRAINING set only ({n} compounds of USI {usi}); the test set is not part of the domain.",
        "pt": "Domínio de aplicabilidade definido apenas sobre o conjunto de TREINO ({n} compostos da USI {usi}); o conjunto de teste não faz parte do domínio.",
    },
    "s7_msg_ad_reference_no_test": {
        "en": "Applicability domain defined on the WHOLE Internal DataFrame ({n} compounds): USI {usi} has no test set (Test Size = 0), so all compounds were used to build the model.",
        "pt": "Domínio de aplicabilidade definido sobre o Internal DataFrame INTEIRO ({n} compostos): a USI {usi} não tem conjunto teste (Tamanho do Teste = 0), então todos os compostos foram usados para gerar o modelo.",
    },
    "s7_msg_ad_reference_refit": {
        "en": "Applicability domain defined on the WHOLE Internal DataFrame ({n} compounds): USI {usi} has refit model(s) trained on training + test ({models}).",
        "pt": "Domínio de aplicabilidade definido sobre o Internal DataFrame INTEIRO ({n} compostos): a USI {usi} tem modelo(s) refit treinado(s) em treino + teste ({models}).",
    },
    "s7_msg_ad_reference_full": {
        "en": "No train/test split of the current USI was found for this Internal DataFrame, so the domain was defined on the ENTIRE internal DataFrame ({n} compounds). Run Screening in STEP 4 (or load a USI) with this DataFrame to restrict it to the training set.",
        "pt": "Nenhum split de treino/teste da USI atual foi encontrado para este Internal DataFrame, então o domínio foi definido sobre o Internal DataFrame INTEIRO ({n} compostos). Rode o Screening na ETAPA 4 (ou carregue uma USI) com este DataFrame para restringi-lo ao conjunto de treino.",
    },

    # ---------------------------------------------------------------- STEP 5: Interpretability Tools
    "msg_title_interp": {"en": "Interpretability", "pt": "Interpretabilidade"},
    "s7i_grp_title": {"en": "Interpretability Tools", "pt": "Ferramentas de Interpretabilidade"},
    "s7i_lbl_model": {"en": "Model:", "pt": "Modelo:"},
    "s7i_tooltip_model": {
        "en": "Trained models of the current USI (STEP 4), in ranking order. The analysis uses the set chosen in 'Data:' (test set of the USI or External DataFrame).",
        "pt": "Modelos treinados da USI atual (ETAPA 4), na ordem do ranking. A análise usa o conjunto escolhido em 'Dados:' (conjunto teste da USI ou External DataFrame).",
    },
    "s7i_tooltip_explainer": {
        "en": "SHAP explainer chosen automatically for this model family: trees and boosting -> TreeExplainer (exact); linear/regularised models -> LinearExplainer (exact); SVM/KNN/MLP and the rest -> PermutationExplainer (approximate, linear cost in the number of descriptors).",
        "pt": "Explicador SHAP escolhido automaticamente para a família do modelo: árvores e boosting -> TreeExplainer (exato); modelos lineares/regularizados -> LinearExplainer (exato); SVM/KNN/MLP e demais -> PermutationExplainer (aproximado, custo linear no número de descritores).",
    },
    "s7i_explainer_line": {"en": "Explainer: {desc} - {kind}", "pt": "Explicador: {desc} - {kind}"},
    "s7i_kind_exact": {"en": "exact values", "pt": "valores exatos"},
    "s7i_kind_approx": {"en": "approximate values", "pt": "valores aproximados"},
    "s7i_exp_tree": {"en": "TreeExplainer (polynomial time)", "pt": "TreeExplainer (tempo polinomial)"},
    "s7i_exp_bagging": {"en": "TreeExplainer averaged over the base trees", "pt": "TreeExplainer médio sobre as árvores-base"},
    "s7i_exp_linear_corr": {"en": "LinearExplainer with feature correlation", "pt": "LinearExplainer com correlação entre atributos"},
    "s7i_exp_linear_indep": {
        "en": "LinearExplainer, interventional mode (the correlation-dependent mode is only used up to {limit} descriptors)",
        "pt": "LinearExplainer, modo intervencional (o modo com correlação só é usado até {limit} descritores)",
    },
    "s7i_exp_permutation": {
        "en": "PermutationExplainer (model-agnostic: SVM, KNN, neural networks and other models)",
        "pt": "PermutationExplainer (agnóstico ao modelo: SVM, KNN, redes neurais e demais modelos)",
    },
    "s7i_lbl_methods": {"en": "Methods:", "pt": "Métodos:"},
    "s7i_lbl_modality": {"en": "Modality:", "pt": "Modalidade:"},
    "s7i_chk_shap": {"en": "SHAP", "pt": "SHAP"},
    "s7i_tooltip_shap": {
        "en": "SHAP values on (a sample of) the set chosen in 'Data:' - the External DataFrame does not need the Y column. Optional dependency: install it with 'pip install shap'.",
        "pt": "Valores SHAP sobre (uma amostra do) conjunto escolhido em 'Dados:' - o External DataFrame não precisa da coluna Y. Dependência opcional: instale com 'pip install shap'.",
    },
    "s7i_chk_perm": {"en": "Permutation importance", "pt": "Importância por permutação"},
    "s7i_tooltip_perm": {
        "en": "Drop in the score when a descriptor (or a whole group) is shuffled, scored with the same metric as the Screening 'Sort metric'. Computed only on compounds the model did not see - the test set or the External DataFrame (rows with an observed Y) - since on the training set it would measure memorisation, not predictive ability.",
        "pt": "Queda do escore ao embaralhar um descritor (ou um grupo inteiro), com a mesma métrica do 'Sort metric' do Screening. Calculada só em compostos que o modelo não viu - o conjunto teste ou o External DataFrame (linhas com Y observado) - pois no treino mediria memorização, não capacidade preditiva.",
    },
    "s7i_chk_individual": {"en": "Individual", "pt": "Individual"},
    "s7i_tooltip_individual": {
        "en": "One result per descriptor. With strongly collinear descriptors, permutation importance splits the importance among the correlated ones and underestimates all of them.",
        "pt": "Um resultado por descritor. Com descritores muito colineares, a importância por permutação divide o valor entre os correlacionados e subestima todos eles.",
    },
    "s7i_chk_group": {"en": "By group (correlated)", "pt": "Por grupo (correlacionados)"},
    "s7i_tooltip_group": {
        "en": "Clusters the descriptors by correlation (hierarchical clustering on the Spearman distance, training set) and permutes each WHOLE group together, so no impossible molecules are created. For SHAP, the values of a group's members are summed per compound.",
        "pt": "Agrupa os descritores por correlação (clusterização hierárquica sobre a distância de Spearman, conjunto de treino) e permuta cada grupo INTEIRO junto, sem criar moléculas impossíveis. No SHAP, os valores dos membros do grupo são somados por composto.",
    },
    "s7i_lbl_corr": {"en": "Group |ρ| ≥", "pt": "Grupo |ρ| ≥"},
    "s7i_tooltip_corr": {
        "en": "Descriptors whose cluster-average absolute Spearman correlation is at least this value are placed in the same group.",
        "pt": "Descritores cuja correlação de Spearman absoluta média no cluster seja pelo menos este valor ficam no mesmo grupo.",
    },
    "s7i_lbl_repeats": {"en": "Repeats:", "pt": "Repetições:"},
    "s7i_tooltip_repeats": {
        "en": "Permutation repeats: how many times each descriptor/group is shuffled; the mean and standard deviation over the repeats are reported.",
        "pt": "Repetições da permutação: quantas vezes cada descritor/grupo é embaralhado; são reportadas a média e o desvio padrão das repetições.",
    },
    "s7i_lbl_shap_rows": {"en": "SHAP rows:", "pt": "Linhas do SHAP:"},
    "s7i_tooltip_shap_rows": {
        "en": 'Maximum number of compounds (test set or External DataFrame) explained by SHAP (random sample when the set is larger). Mainly bounds the cost of the PermutationExplainer.',
        "pt": 'Número máximo de compostos (conjunto teste ou External DataFrame) explicados pelo SHAP (amostra aleatória quando o conjunto é maior). Limita principalmente o custo do PermutationExplainer.',
    },
    "s7i_lbl_top_n": {"en": "Top N:", "pt": "Top N:"},
    "s7i_lbl_workers": {"en": "Workers:", "pt": "Núcleos:"},
    "s7i_tooltip_top_n": {
        "en": "Number of descriptors/groups shown in each chart (the CSV files always contain all of them).",
        "pt": "Número de descritores/grupos mostrados em cada gráfico (os arquivos CSV sempre trazem todos).",
    },
    "s7i_tooltip_workers": {
        "en": "Threads for permutation importance (0 = all available cores).",
        "pt": "Threads para a importância por permutação (0 = todos os núcleos disponíveis).",
    },
    "s7i_fmt_progress": {"en": "Interpretability: %p%", "pt": "Interpretabilidade: %p%"},
    "s7i_btn_run": {"en": "Run Interpretability", "pt": "Executar Interpretabilidade"},
    "s7i_warn_module_missing": {
        "en": "The interpretability module could not be loaded (see the console for details).",
        "pt": "O módulo de interpretabilidade não pôde ser carregado (veja o console para detalhes).",
    },
    "s7i_warn_clustering": {
        "en": "Interpretability applies to regression/classification models only (clustering has no test set or response).",
        "pt": "A interpretabilidade se aplica apenas a modelos de regressão/classificação (clusterização não tem conjunto de teste nem resposta).",
    },
    "s7i_warn_refit": {
        "en": "The selected model is a refit model (trained on training + test), so its test set is training data. Choose 'External DataFrame' in 'Data:' (or select the source model).",
        "pt": "O modelo selecionado é um modelo refit (treinado em treino + teste), então o seu conjunto teste é dado de treino. Escolha 'External DataFrame' em 'Dados:' (ou selecione o modelo de origem).",
    },
    "s7i_lbl_data": {"en": "Data:", "pt": "Dados:"},
    "s7i_data_test": {"en": "Test set", "pt": "Conjunto teste"},
    "s7i_data_external": {"en": "External DataFrame", "pt": "External DataFrame"},
    "s7i_tooltip_data": {
        "en": "Set on which the tools measure the model. Test set: the test set of the USI (not available with Test Size = 0 or for refit models - then 'External DataFrame' is selected automatically). External DataFrame: the selected external set, with the same descriptor columns as the model; SHAP does not need Y, permutation importance uses only the rows with an observed Y.",
        "pt": "Conjunto em que as ferramentas medem o modelo. Conjunto teste: o teste da USI (indisponível com Tamanho do Teste = 0 ou para modelos refit - nesses casos 'External DataFrame' é escolhido automaticamente). External DataFrame: o conjunto externo selecionado, com as mesmas colunas de descritores do modelo; o SHAP não precisa de Y, e a importância por permutação usa só as linhas com Y observado.",
    },
    "s7i_warn_ext_missing": {
        "en": "Select the External DataFrame (STEP 4 or STEP 5) to run the interpretability tools on it.",
        "pt": "Selecione o External DataFrame (ETAPA 4 ou ETAPA 5) para rodar as ferramentas de interpretabilidade sobre ele.",
    },
    "s7i_warn_ext_columns": {
        "en": "The External DataFrame lacks {n} of the model's {total} descriptor columns (or has no row with all of them numeric). It must contain the same descriptors used to train the model.",
        "pt": "O External DataFrame não tem {n} das {total} colunas de descritores do modelo (ou nenhuma linha com todas numéricas). Ele precisa conter os mesmos descritores usados no treino do modelo.",
    },
    "s7i_warn_ext_no_y": {
        "en": "The External DataFrame has no Y column ('{y}'): only SHAP is available - permutation importance needs the observed values.",
        "pt": "O External DataFrame não tem a coluna Y ('{y}'): só o SHAP está disponível - a importância por permutação precisa dos valores observados.",
    },
    "s7i_msg_ext_too_few": {
        "en": "Only {n} compound(s) of the External DataFrame have a usable observed Y - at least 3 are needed for permutation importance.",
        "pt": "Apenas {n} composto(s) do External DataFrame têm Y observado utilizável - são necessários ao menos 3 para a importância por permutação.",
    },
    "s7i_warn_no_test_set": {
        "en": "This USI has no test set (Test Size = 0 in STEP 4). Choose 'External DataFrame' in 'Data:' to run the interpretability tools on the external set.",
        "pt": "Esta USI não tem conjunto teste (Tamanho do Teste = 0 na ETAPA 4). Escolha 'External DataFrame' em 'Dados:' para rodar as ferramentas de interpretabilidade no conjunto externo.",
    },
    "s7i_warn_no_model": {
        "en": 'Run Screening in STEP 4 (or load a USI) to enable this group: it needs a trained model of that USI.',
        "pt": 'Rode o Screening na ETAPA 4 (ou carregue uma USI) para habilitar este grupo: ele precisa de um modelo treinado dessa USI.',
    },
    "s7i_warn_projection": {
        "en": "Disabled: this model was trained on projected components (PCA/UMAP/t-SNE/...), so SHAP and permutation would refer to components, not descriptors, and the mechanistic reading is lost.",
        "pt": "Desabilitado: este modelo foi treinado em componentes projetados (PCA/UMAP/t-SNE/...), então SHAP e permutação se refeririam a componentes, não a descritores, e a leitura mecanística se perde.",
    },
    "s7i_warn_shap_missing": {
        "en": "SHAP is not installed (optional dependency) - only permutation importance is available. Install it with 'pip install shap'.",
        "pt": "SHAP não está instalado (dependência opcional) - apenas a importância por permutação está disponível. Instale com 'pip install shap'.",
    },
    "s7i_msg_select_method": {"en": "Select at least one method (SHAP and/or permutation importance).", "pt": "Selecione pelo menos um método (SHAP e/ou importância por permutação)."},
    "s7i_msg_select_modality": {"en": "Select at least one modality (individual and/or by group).", "pt": "Selecione pelo menos uma modalidade (individual e/ou por grupo)."},
    "s7i_msg_shap_import_failed": {"en": "SHAP could not be imported:\n{e}", "pt": "Não foi possível importar o SHAP:\n{e}"},
    "s7i_msg_saved_to": {"en": "{n} file(s) (CSV tables and PNG charts) saved under the USI folder (data: {folder}).", "pt": "{n} arquivo(s) (tabelas CSV e gráficos PNG) salvos na pasta da USI (dados: {folder})."},
    "s7i_msg_chart_saved": {"en": "Chart saved to:\n{path}", "pt": "Gráfico salvo em:\n{path}"},
    "s7i_note_shap_rows_sampled": {
        "en": "SHAP was computed on a random sample of {rows} test compounds (see 'SHAP rows'); permutation importance used the whole test set.",
        "pt": "O SHAP foi calculado em uma amostra aleatória de {rows} compostos de teste (veja 'Linhas do SHAP'); a importância por permutação usou todo o teste.",
    },
    "s7i_note_fallback_permutation": {
        "en": "The specific explainer failed for this model, so the PermutationExplainer (approximate) was used instead.",
        "pt": "O explicador específico falhou para este modelo, então foi usado o PermutationExplainer (aproximado).",
    },
    "s7i_note_linear_corr_failed": {
        "en": "The correlation-dependent LinearExplainer could not be used (singular covariance); the interventional mode was used instead.",
        "pt": "O LinearExplainer com correlação não pôde ser usado (covariância singular); foi usado o modo intervencional.",
    },
    "s7i_note_scorer_fallback": {
        "en": "The 'Sort metric' scorer is not available for this model; the model's default score was used for permutation importance.",
        "pt": "O escore do 'Sort metric' não está disponível para este modelo; foi usado o escore padrão do modelo na importância por permutação.",
    },
    "s7i_dlg_title": {"en": "Interpretability - {model}", "pt": "Interpretabilidade - {model}"},
    "s7i_btn_save_chart": {"en": "Save Chart", "pt": "Salvar Gráfico"},
    "s7i_btn_close": {"en": "Close", "pt": "Fechar"},
    "s7i_tab_perm_individual": {"en": "Permutation - individual", "pt": "Permutação - individual"},
    "s7i_tab_perm_group": {"en": "Permutation - by group", "pt": "Permutação - por grupo"},
    "s7i_tab_shap_individual": {"en": "SHAP - individual", "pt": "SHAP - individual"},
    "s7i_tab_shap_beeswarm": {"en": "SHAP - summary", "pt": "SHAP - resumo"},
    "s7i_tab_shap_group": {"en": "SHAP - by group", "pt": "SHAP - por grupo"},
    "s7i_tab_shap_structures": {"en": "SHAP - substructures", "pt": "SHAP - subestruturas"},
    "s7i_note_structures_unverified": {
        "en": "Substructures were NOT drawn for some circular-fingerprint descriptors: the fingerprint settings (size/chirality) could not be verified against the descriptor table, and a wrong setting would draw the wrong substructure.",
        "pt": "As subestruturas NÃO foram desenhadas para alguns descritores de fingerprint circular: as configurações do fingerprint (tamanho/quiralidade) não puderam ser verificadas contra a tabela de descritores, e uma configuração errada desenharia a subestrutura errada.",
    },
    "s7i_note_structures_not_applicable": {
        "en": "No substructure chart: none of the most important descriptors is a fingerprint bit/key with a known structural definition (ECFP/FCFP, MACCS, PubChem).",
        "pt": "Sem gráfico de subestruturas: nenhum dos descritores mais importantes é um bit/chave de fingerprint com definição estrutural conhecida (ECFP/FCFP, MACCS, PubChem).",
    },
    "s7i_note_structures_none_resolved": {
        "en": "No substructure chart: no important fingerprint descriptor could be paired with an example compound that has it.",
        "pt": "Sem gráfico de subestruturas: nenhum descritor de fingerprint importante pôde ser associado a um composto de exemplo que o possua.",
    },
    "s7i_tab_data_suffix": {"en": "[data]", "pt": "[dados]"},
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
              "model's screening Q2 CV (regression) / F1 CV (classification) when the dataframe "
              "comes from a known USI - editable.",
        "pt": "Usado apenas pelo método 'Weighted Consensus'. Sugerido automaticamente a partir "
              "do Q2 CV (regressão) / F1 CV (classificação) do Screening do modelo quando o dataframe vem de "
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
              "or auto-suggested from the screening Q2 CV/F1 CV when the list traces back to a known USI).",
        "pt": "Z-Score (Mean/SD): consenso padronizado clássico.\n"
              "Z-Score (Median/MAD): robusto a compostos discrepantes (outliers).\n"
              "Rank Sum / Borda count: não paramétrico, usa apenas as posições nas listas.\n"
              "Reciprocal Rank Fusion (RRF): score de fusão robusto, sem necessidade de normalização.\n"
              "Weighted Consensus: Z-Score ponderado por lista pelo campo 'Weight' (manual, "
              "ou sugerido automaticamente a partir do Q2 CV/F1 CV do Screening quando a lista vem de uma USI conhecida).",
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
    "s8_grp_consensus_options": {"en": "Consensus Options", "pt": "Opções de Consenso"},
    "s8_btn_consensus_generate": {"en": "Consensus Generate", "pt": "Gerar Consenso"},
    "btn_clear": {"en": "Clear", "pt": "Limpar"},
    "s8_btn_generate_final_report": {"en": "Generate Final Report", "pt": "Gerar Relatório Final"},
    "s8_grp_codoc_integration": {"en": "CODOC Integration", "pt": "Integração com o CODOC"},
    "s8_lbl_structures_scope": {"en": "Select Consensus Data:", "pt": "Selecionar Dados do Consenso:"},
    "s8_tooltip_structures_scope": {
        "en": "'All': every compound that took part in the consensus (the full merged result). "
              "'Hits': only the compounds in the filtered Hits table (after the CV%/Top Hits% filters).",
        "pt": "'All': todos os compostos que participaram do consenso (resultado completo combinado). "
              "'Hits': apenas os compostos da tabela de Hits filtrada (após os filtros de CV%/Top Hits%).",
    },
    "s8_chk_structures_sdf2d": {"en": "SDF 2D", "pt": "SDF 2D"},
    "s8_tooltip_structures_sdf2d": {
        "en": "Writes a single combined .sdf file (2D coordinates) with the selected compounds' structures.",
        "pt": "Grava um único arquivo .sdf combinado (coordenadas 2D) com as estruturas dos compostos selecionados.",
    },
    "s8_chk_structures_smiles": {"en": "Smiles", "pt": "Smiles"},
    "s8_tooltip_structures_smiles": {
        "en": "Writes a single .smi file (SMILES + Name, one per line) with the selected compounds.",
        "pt": "Grava um único arquivo .smi (SMILES + Nome, um por linha) com os compostos selecionados.",
    },
    "s8_btn_generate_structures": {"en": "Generate Structure", "pt": "Gerar Estrutura"},
    "s8_tooltip_generate_structures": {
        "en": "Writes .sdf and/or .smi files (per the checkboxes) with ALL AND ONLY the compounds "
              "from 'Select Consensus Data' (All or Hits), saved under RESULTS/STRUCTURES - for use "
              "by CODOC. Run 'Consensus Generate' first.",
        "pt": "Grava arquivos .sdf e/ou .smi (conforme os checkboxes) com TODOS E APENAS os compostos "
              "de 'Select Consensus Data' (All ou Hits), salvos em RESULTS/STRUCTURES - para uso pelo "
              "CODOC. Execute 'Consensus Generate' antes.",
    },

    # ---------------------------------------------------------------- EDIT tab
    "edit_grp_merge_remove_compare": {"en": "Merge, Remove or Compare", "pt": "Combinar, Remover ou Comparar"},
    "edit_lbl_select_df1": {"en": "Select DataFrame 1:", "pt": "Selecione o DataFrame 1:"},
    "edit_lbl_select_index1": {"en": "Select Index(es) 1:", "pt": "Selecione o(s) Índice(s) 1:"},
    "edit_placeholder_select_df1": {"en": "Select DataFrame 1", "pt": "Selecione o DataFrame 1"},
    "btn_search": {"en": "Search", "pt": "Buscar"},
    "edit_lbl_select_df2": {"en": "Select DataFrame 2:", "pt": "Selecione o DataFrame 2:"},
    "edit_lbl_select_index2": {"en": "Select Index(es) 2:", "pt": "Selecione o(s) Índice(s) 2:"},
    "edit_placeholder_select_df2": {"en": "Select DataFrame 2", "pt": "Selecione o DataFrame 2"},
    "edit_placeholder_select_indices": {"en": "e.g. 0,1,3-7,10", "pt": "ex.: 0,1,3-7,10"},
    "edit_tooltip_select_indices": {
        "en": "Single indices and/or ranges, comma-separated (e.g. 0,1,3-7,10 selects/removes "
              "positions 0, 1, 3 through 7, and 10).",
        "pt": "Índices únicos e/ou intervalos, separados por vírgula (ex.: 0,1,3-7,10 seleciona/"
              "remove as posições 0, 1, 3 até 7 e 10).",
    },
    "edit_chk_by_rows": {"en": "By Rows", "pt": "Por Linhas"},
    "edit_chk_by_columns": {"en": "By Columns", "pt": "Por Colunas"},
    "edit_btn_merge_dataframes": {"en": "Merge from\n Dataframes", "pt": "Combinar a partir\n de Dataframes"},
    "edit_btn_remove_from_dataframes": {"en": "Remove from\n Dataframes", "pt": "Remover a partir\n de Dataframes"},
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
    "msg_title_finished": {"en": "Finished", "pt": "Concluído"},
    "msg_title_current_project": {"en": "Current Project", "pt": "Projeto Atual"},
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
        "en": "Step 5 - Applicability Domain, Similarity Analysis and Interpretability",
        "pt": "Etapa 5 - Domínio de Aplicabilidade, Análise de Similaridade e Interpretabilidade",
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
    # (BIN/module_requirements.py) — standalone window opened from Help > Install Requirements
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
    "req_chk_openbabel": {"en": "Install OpenBabel (openbabel-wheel)", "pt": "Instalar OpenBabel (openbabel-wheel)"},
    "req_tooltip_openbabel": {
        "en": "Optional. Used by STEP 3 'Or Select Structures File' to read .mol2/.pdb/.pdbqt (and similar) structure files, preserving their original 3D coordinates for 3D descriptors. Not required for .smi/.sdf, which RDKit already reads.",
        "pt": "Opcional. Usado pela STEP 3 'Or Select Structures File' para ler arquivos de estrutura .mol2/.pdb/.pdbqt (e similares), preservando as coordenadas 3D originais para os descritores 3D. Não é necessário para .smi/.sdf, que já são lidos pelo RDKit.",
    },
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

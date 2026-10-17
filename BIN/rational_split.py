"""Divisão treino/teste RACIONAL para a STEP 4 (Model Screening) do CODRUG.

Além do split aleatório (sklearn.train_test_split), oferece dois métodos clássicos de QSAR que
escolhem o conjunto de TREINO de modo a cobrir o espaço químico, deixando o TESTE dentro desse
espaço (interpolação):

- Kennard-Stone (Kennard & Stone, 1969): começa pelo par de compostos mais distante entre si e,
  a cada passo, inclui no treino o composto cuja menor distância aos já escolhidos é a maior
  (max-min), até completar o tamanho do treino. Os compostos restantes - os mais "internos" - formam
  o teste. Determinístico; o tamanho do teste é exatamente o pedido.
- Sphere exclusion (Golbraikh & Tropsha, 2002; Golbraikh et al., 2003): o primeiro centro é o
  composto de maior atividade (regressão) ou o mais próximo do centróide (classificação); o centro
  vai para o treino e os compostos dentro da esfera de raio R em torno dele vão para o teste; os
  próximos centros são escolhidos pelo critério max-min entre os compostos ainda não atribuídos. O
  raio R é ajustado por busca binária para a fração de teste ficar o mais próxima possível da pedida
  (o tamanho final pode diferir ligeiramente). Determinístico.

- Scaffold (Bemis & Murcko, 1996), versão "balanced" (Yang et al., 2019 - Chemprop): agrupa os
  compostos pelo esqueleto de Bemis-Murcko do SMILES e reparte GRUPOS inteiros - nenhum scaffold
  aparece nos dois conjuntos. Grupos maiores que metade do teste vão para o treino; os demais são
  sorteados (Random State) e entram no teste enquanto couberem. Mede a previsão de famílias químicas
  NOVAS (extrapolação) - o oposto de Kennard-Stone/Sphere Exclusion. Precisa da coluna de SMILES; o
  tamanho final do teste pode diferir um pouco do pedido (grupos não são partidos) e não há
  estratificação por classe (um scaffold pode ter compostos de classes diferentes).

Espaço usado por Kennard-Stone e Sphere Exclusion: descritores autoescalados (z-score; colunas constantes são
ignoradas) e, se houver mais de MAX_COMPONENTS colunas, projetados nas primeiras componentes
principais (até MAX_COMPONENTS) - distâncias euclidianas nesse espaço. Em classificação, os métodos
são aplicados dentro de cada classe (split estratificado), preservando as proporções de classe.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

RANDOM = "Random"
STRATIFIED = "Stratified Random"
KENNARD_STONE = "Kennard-Stone"
SPHERE_EXCLUSION = "Sphere Exclusion"
SCAFFOLD = "Scaffold"
METHODS = (RANDOM, STRATIFIED, KENNARD_STONE, SPHERE_EXCLUSION, SCAFFOLD)
# Nº de faixas (quantis de Y) usadas para estratificar a divisão aleatória em regressão.
STRATIFY_BINS = 5

MAX_COMPONENTS = 50


def descriptor_space(x: pd.DataFrame) -> np.ndarray:
    """Matriz (n x k) em que as distâncias são calculadas: autoescalada e, se necessário, reduzida
    por PCA às primeiras MAX_COMPONENTS componentes."""
    a = np.asarray(x, dtype=float)
    a = np.where(np.isfinite(a), a, np.nan)
    col_mean = np.nanmean(a, axis=0)
    a = np.where(np.isnan(a), col_mean, a)  # valores ausentes -> média da coluna
    std = a.std(axis=0)
    keep = std > 0
    if not keep.any():
        return np.zeros((a.shape[0], 1))
    z = (a[:, keep] - a[:, keep].mean(axis=0)) / std[keep]
    if z.shape[1] > MAX_COMPONENTS:
        from sklearn.decomposition import PCA
        n_comp = min(MAX_COMPONENTS, z.shape[0] - 1)
        z = PCA(n_components=n_comp, svd_solver="randomized", random_state=0).fit_transform(z)
    return z


def _farthest_pair(z: np.ndarray, chunk: int = 2048) -> tuple[int, int]:
    """Índices do par de pontos mais distante (distâncias calculadas em blocos)."""
    sq = (z ** 2).sum(axis=1)
    best, pair = -1.0, (0, 0)
    for start in range(0, len(z), chunk):
        block = z[start:start + chunk]
        d2 = sq[start:start + chunk, None] + sq[None, :] - 2.0 * block @ z.T
        i, j = np.unravel_index(int(np.argmax(d2)), d2.shape)
        if d2[i, j] > best:
            best, pair = float(d2[i, j]), (start + int(i), int(j))
    return pair


def _dist_to(z: np.ndarray, idx: int) -> np.ndarray:
    return np.sqrt(((z - z[idx]) ** 2).sum(axis=1))


def kennard_stone(z: np.ndarray, n_train: int) -> np.ndarray:
    """Índices (posições) escolhidos para o treino pelo algoritmo de Kennard-Stone."""
    n = len(z)
    n_train = max(0, min(n, int(n_train)))
    if n_train == 0:
        return np.array([], dtype=int)
    if n_train >= n:
        return np.arange(n)
    if n == 1 or n_train == 1:
        centroid = z.mean(axis=0)
        return np.array([int(np.argmax(((z - centroid) ** 2).sum(axis=1)))])
    i, j = _farthest_pair(z)
    selected = [i] if i == j else [i, j]
    min_d = np.minimum(_dist_to(z, i), _dist_to(z, j))
    min_d[selected] = -1.0
    while len(selected) < n_train:
        nxt = int(np.argmax(min_d))
        selected.append(nxt)
        min_d = np.minimum(min_d, _dist_to(z, nxt))
        min_d[selected] = -1.0
    return np.array(selected, dtype=int)


def _sphere_exclusion_once(z: np.ndarray, radius: float, first: int) -> tuple[np.ndarray, np.ndarray]:
    """Uma passada de sphere exclusion com raio fixo: (índices do treino, índices do teste)."""
    n = len(z)
    state = np.zeros(n, dtype=np.int8)  # 0 = livre, 1 = treino, 2 = teste
    min_d_centers = np.full(n, np.inf)
    center = first
    while True:
        state[center] = 1
        d = _dist_to(z, center)
        inside = (d <= radius) & (state == 0)
        state[inside] = 2
        min_d_centers = np.minimum(min_d_centers, d)
        free = np.flatnonzero(state == 0)
        if free.size == 0:
            break
        center = int(free[np.argmax(min_d_centers[free])])  # max-min entre os livres
    return np.flatnonzero(state == 1), np.flatnonzero(state == 2)


def sphere_exclusion(z: np.ndarray, test_fraction: float, first: int, iterations: int = 40) -> np.ndarray:
    """Índices do treino por sphere exclusion, com o raio ajustado por busca binária para a fração
    de teste ficar o mais próxima possível de test_fraction."""
    n = len(z)
    if n <= 1 or test_fraction <= 0:
        return np.arange(n)
    target = test_fraction * n
    lo = 0.0
    hi = float(np.sqrt(((z - z.mean(axis=0)) ** 2).sum(axis=1)).max() * 2.0) or 1.0
    best_train, best_err = np.arange(n), abs(target)
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        train, test = _sphere_exclusion_once(z, mid, first)
        err = abs(len(test) - target)
        if err < best_err:
            best_train, best_err = train, err
        if err < 0.5:
            break
        if len(test) < target:
            lo = mid
        else:
            hi = mid
    return best_train


def murcko_scaffold(smiles) -> str:
    """SMILES canônico do esqueleto de Bemis-Murcko (anéis + ligantes entre eles); "" para moléculas
    acíclicas e None para SMILES inválido/vazio."""
    if smiles is None or (isinstance(smiles, float) and math.isnan(smiles)) or not str(smiles).strip():
        return None
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None:
        return None
    try:
        return MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
    except Exception:
        return None


def scaffold_split_positions(smiles, test_size: float, random_state=None) -> np.ndarray:
    """Posições (0..n-1) do conjunto de TREINO na divisão por scaffold "balanced". SMILES inválidos
    formam cada um o seu próprio grupo."""
    smiles = list(smiles)
    n = len(smiles)
    n_test = int(math.ceil(test_size * n))
    groups = {}
    for i, smi in enumerate(smiles):
        key = murcko_scaffold(smi)
        groups.setdefault(key if key is not None else f"__invalid_{i}", []).append(i)
    sets = list(groups.values())
    big = [g for g in sets if len(g) > n_test / 2]
    small = [g for g in sets if len(g) <= n_test / 2]
    rng = np.random.RandomState(random_state if random_state is not None else 0)
    rng.shuffle(small)
    train, test = [], []
    for g in big:
        train.extend(g)
    for g in small:
        if len(test) + len(g) <= n_test:
            test.extend(g)
        else:
            train.extend(g)
    if not test and small:  # teste vazio (grupos grandes demais): usa o menor grupo
        smallest = min(small, key=len)
        test.extend(smallest)
        train = [i for i in train if i not in set(smallest)]
    return np.array(sorted(train), dtype=int)


def stratify_labels(y, task: str, n_bins: int = STRATIFY_BINS):
    """Rótulos para estratificar a divisão aleatória: em classificação, a própria classe; em
    regressão, a faixa de Y (quantis - até n_bins faixas com o mesmo nº de compostos, menos se
    houver valores repetidos). Y ausente (NaN) vira uma faixa própria."""
    y_series = pd.Series(np.asarray(y))
    if task == "classification":
        return y_series.astype(str).to_numpy()
    values = pd.to_numeric(y_series, errors="coerce")
    labels = pd.Series("nan", index=values.index, dtype=object)
    ok = values.notna()
    if ok.sum() > 0:
        n = max(1, min(int(n_bins), int(ok.sum())))
        bins = pd.qcut(values[ok], q=n, labels=False, duplicates="drop")
        labels[ok] = bins.astype(int).astype(str)
    return labels.to_numpy()


def split(x: pd.DataFrame, y, test_size: float, method: str, task: str,
          random_state=None, smiles=None):
    """Mesmo contrato de sklearn.train_test_split: devolve (x_train, x_test, y_train, y_test),
    preservando os índices originais. method: RANDOM, STRATIFIED, KENNARD_STONE, SPHERE_EXCLUSION ou
    SCAFFOLD (este exige 'smiles', alinhado linha a linha com x). y pode ser None (divisão só por X;
    y_train/y_test devolvidos como None) - exceto no STRATIFIED, que precisa de Y.
    STRATIFIED: divisão aleatória (train_test_split, mesmo Random State) estratificada - mesma
    proporção de cada classe (classificação) ou de cada faixa de Y (regressão, ver stratify_labels)
    no treino e no teste."""
    if method == STRATIFIED:
        if y is None:
            raise ValueError("The Stratified Random split needs the response column (Y).")
        from sklearn.model_selection import train_test_split
        strata = stratify_labels(y, task)
        counts = pd.Series(strata).value_counts()
        if counts.min() < 2:
            raise ValueError(
                f"Stratified Random split: the group '{counts.idxmin()}' has only {int(counts.min())} "
                "compound(s) - each class (or Y range) needs at least 2. Use the Random split.")
        return train_test_split(x, y, test_size=test_size, random_state=random_state, stratify=strata)
    if method == SCAFFOLD:
        if smiles is None:
            raise ValueError("The Scaffold split needs a SMILES column.")
        smiles = list(smiles)
        if len(smiles) != len(x):
            raise ValueError("The SMILES column must have one value per row of X.")
        train_mask = np.zeros(len(x), dtype=bool)
        train_mask[scaffold_split_positions(smiles, test_size, random_state)] = True
        x_train, x_test = x.iloc[train_mask], x.iloc[~train_mask]
        if y is None:
            return x_train, x_test, None, None
        y_arr = y if isinstance(y, pd.Series) else pd.Series(np.asarray(y), index=x.index)
        return x_train, x_test, y_arr.iloc[train_mask], y_arr.iloc[~train_mask]

    if y is None:
        # Sem variável resposta (ex.: separação do conjunto externo na Etapa 3 sem coluna Y definida):
        # divide só por X; no Sphere Exclusion o primeiro centro passa a ser o mais próximo do centróide.
        y_dummy = pd.Series(np.zeros(len(x)), index=x.index)
        x_tr, x_te, _yt, _ye = split(x, y_dummy, test_size, method, "none", random_state=random_state)
        return x_tr, x_te, None, None

    if method == RANDOM or method not in METHODS:
        from sklearn.model_selection import train_test_split
        return train_test_split(x, y, test_size=test_size, random_state=random_state)

    y_series = pd.Series(np.asarray(y), index=x.index)
    if task == "classification":
        groups = [np.flatnonzero((y_series == cls).to_numpy()) for cls in pd.unique(y_series)]
    else:
        groups = [np.arange(len(x))]

    z_all = descriptor_space(x)
    train_pos = []
    for pos in groups:
        if len(pos) == 0:
            continue
        z = z_all[pos]
        n_test = int(math.ceil(test_size * len(pos)))  # mesma conta do train_test_split
        if len(pos) < 2:
            sel = np.arange(len(pos))
        elif method == KENNARD_STONE:
            sel = kennard_stone(z, len(pos) - n_test)
        else:
            y_num = pd.to_numeric(y_series.iloc[pos], errors="coerce").to_numpy()
            if task == "regression" and np.isfinite(y_num).any():
                first = int(np.nanargmax(y_num))
            else:
                first = int(np.argmin(((z - z.mean(axis=0)) ** 2).sum(axis=1)))
            sel = sphere_exclusion(z, test_size, first)
        train_pos.extend(pos[sel].tolist())

    train_mask = np.zeros(len(x), dtype=bool)
    train_mask[train_pos] = True
    x_train, x_test = x.iloc[train_mask], x.iloc[~train_mask]
    y_arr = y if isinstance(y, pd.Series) else y_series
    y_train, y_test = y_arr.iloc[train_mask], y_arr.iloc[~train_mask]
    return x_train, x_test, y_train, y_test

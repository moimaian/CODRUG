# Versionamento do CODRUG

A partir da `1.0.0-1` (primeira versão estável, fim do beta), a versão segue
**MAJOR.MINOR.PATCH** (SemVer) para o número que importa (o que aparece antes
do traço); o `-N` depois do traço é a *revisão de empacotamento*, no sentido
estrito do Debian — só sobe quando `packaging/` muda (control.in, postinst,
postrm, codrug-launcher, .desktop...) sem nenhuma mudança de código do
programa. Toda mudança de código reseta o `-N` para `-1`.

**Fonte única do número: [`BIN/versao.py`](../BIN/versao.py)** (`VERSAO =
"..."`). É o mesmo valor que:
- aparece no rodapé de todas as abas, centralizado entre BACK e NEXT (na
  HOME, na linha de rodapé abaixo dos botões);
- aparece em Help > About;
- `packaging/deb/build.sh` usa como padrão ao gerar o `.deb`.

`packaging/deb/build.sh` recusa rodar se `BIN/versao.py` e a primeira linha
de `packaging/deb/changelog` não tiverem o mesmo número — os dois precisam
ser atualizados juntos (ver "Ao gerar um novo .deb" abaixo).

```
1.0.0    -1
└─┬─┘    └┬┘
  │       └─ revisão de empacotamento (só packaging/ mudou)
  └─ versão do programa (MAJOR.MINOR.PATCH)
```

### Época `1:` no `.deb`

Antes da `1.0.0-1` os `.deb` eram numerados por data (`2026.08.06`,
`2026.09.13`, `2026.10.08`). Para o dpkg, `2026.10.08` é *maior* que
`1.0.0-1`, então quem tivesse um desses instalado nunca receberia a versão
nova pelo apt. Por isso o campo `Version:` do pacote leva a época `1:`
(`1:1.0.0-1`), que tem prioridade sobre o resto da comparação. O
`build.sh` acrescenta a época sozinho — **não** a coloque em
`BIN/versao.py` nem no changelog. Uma época nunca pode ser removida depois
de publicada (voltaria a perder para os pacotes por data); se um dia
precisar mudar o esquema de novo, sobe para `2:`.

## Como decidir qual número sobe

A pergunta não é "quanto código mudou" — é **"alguém que já usa o CODRUG
hoje vai precisar fazer algo diferente, ou vai ter algo que parou de
funcionar, por causa desta mudança?"**

- **PATCH** (`1.0.0` → `1.0.1`): corrige um bug, sem mudar nenhum
  comportamento que já era esperado. Ex.: a correção do erro `'type'` /
  `search_value` ao carregar um dataframe na STEP 2.

- **MINOR** (`1.0.0` → `1.1.0`, zera o patch): funcionalidade nova,
  adicionada sem quebrar nada do que já existia — a pessoa ganha algo, não
  perde nada. Ex.: o botão "Split External DataFrame" da STEP 3, um novo
  modelo na lista da STEP 4, uma nova métrica, SHAP/permutation no External
  DataFrame.

- **MAJOR** (`1.0.0` → `2.0.0`, zera minor e patch): muda ou remove algo
  que já existia, de um jeito que quem já usa precisa se adaptar. Ex.:
  - remover/renumerar uma STEP ou um botão do fluxo;
  - mudar o formato do JSON de estado do projeto (`PROJECTS/<projeto>/
    <projeto>.json`) ou do `skl_session.json` de um USI de um jeito que
    projetos salvos por versões antigas parem de abrir;
  - renomear pastas do layout (`PROJECTS`, `DATA`, `BASE`, `BIN`...) sem
    migração automática;
  - mudar a versão de Python exigida pelo venv (hoje 3.10);
  - mudar `/opt/codrug` para outro caminho no `.deb`.

  Renomeações que vêm **com migração automática e transparente** (como
  JOBS → PROJECTS e DATA_BASES → DATA) não obrigam MAJOR — contam como
  MINOR, já que o usuário não precisa fazer nada.

## Ao gerar um novo `.deb`

1. Decida o próximo `MAJOR.MINOR.PATCH` pelas regras acima.
2. Atualize `VERSAO` em `BIN/versao.py` para o novo número.
3. Adicione uma entrada no topo de `packaging/deb/changelog` (formato
   Debian padrão: `codrug (X.Y.Z-1) unstable; urgency=low`, lista do que
   mudou, linha `-- Nome <email>  data`) com o **mesmo** número do passo 2.
4. `packaging/deb/build.sh` (sem argumento já usa o número de
   `BIN/versao.py`). O pacote sai como `packaging/dist/codrug_X.Y.Z-1_all.deb`.

Se a mudança for só de empacotamento (ex.: ajustar o `postinst`, sem tocar
em `CODRUG.py`/`BIN/`), mantenha o `X.Y.Z` e suba só o `-N` (`1.0.0-1` →
`1.0.0-2`) — também em `BIN/versao.py`, para o app e o pacote mostrarem o
mesmo número.

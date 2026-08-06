# Empacotamento .deb do CODRUG

## Build

```bash
packaging/deb/build.sh              # versão = data de hoje (AAAA.MM.DD)
packaging/deb/build.sh 2026.08.06   # versão explícita
```

Gera `packaging/dist/codrug_<versão>_all.deb`.

Dependências para *buildar* (não para instalar/usar): `dpkg-deb`, `rsync`
(já vêm em qualquer Debian/Ubuntu/Mint). `lintian` é opcional.

## Instalar

```bash
sudo apt install ./packaging/dist/codrug_<versão>_all.deb
```

Isso cria:
- `/opt/codrug` — código-fonte da aplicação (arquivo do pacote, gerenciado pelo dpkg);
- `/usr/bin/codrug` — launcher;
- `/usr/share/applications/codrug.desktop` — entrada no menu.

## O que acontece no primeiro clique em "CODRUG" no menu

1. `/usr/bin/codrug` sincroniza `/opt/codrug` → `$HOME/CODRUG` (sem tocar em
   `$HOME/CODRUG/JOBS`, que guarda os resultados do usuário) e chama
   `python3 $HOME/CODRUG/CODRUG.py`.
2. `CODRUG.py` (código já existente, inalterado por este empacotamento)
   detecta que ainda não está rodando no venv-alvo e chama
   `bootstrap_pyqt5(interactive=True, reexec=True)` em
   `MODULES/module_requirements.py`, que:
   - cria `$HOME/.venv/CODRUG` com Python 3.10;
   - instala PyQt5 e, em seguida, o restante das dependências científicas
     (RDKit, scikit-learn, PyCaret, etc.) — pelo botão "Instalação de
     Requisitos" na aba HOME ou pela splash screen;
   - se reinicia (`os.execve`) já dentro do venv.
3. A splash screen (`MODULES/splash_screen.py`) recria/atualiza também o
   `.desktop` em `~/.local/share/applications/CODRUG.desktop` e a estrutura
   de subpastas dentro de `$HOME/CODRUG`.

Por isso `Terminal=true` no `.desktop`: o passo 2 usa `input()` para
confirmar a criação do ambiente (mesmo comportamento que já existia rodando
`python3 CODRUG.py` manualmente pelo terminal).

## Por que o pacote não cria o venv/instala as dependências no `postinst`

`postinst`/`postrm` rodam como **root**, durante `apt install`/`dpkg -i`.
Nesse momento:

- `$HOME` não é o home do usuário final (é `/root` ou indefinido) — não dá
  para localizar `$HOME/CODRUG` de forma confiável, e em máquina
  multiusuário a pergunta "de qual usuário?" nem faz sentido para um
  pacote de sistema;
- instalar via pip pacotes pesados (RDKit, TensorFlow, PyTorch, PyCaret)
  depende de rede, demora minutos, e se falhar no meio deixa o `dpkg` em
  estado `half-configured`, travando qualquer `apt` seguinte até conserto
  manual — contra as boas práticas de empacotamento Debian.

Por isso o pacote fica deliberadamente fino: só coloca arquivos em
`/opt/codrug`, registra o menu, e deixa o bootstrap por-usuário para o
próprio `CODRUG.py`, que já existia antes deste empacotamento.

## Atualizações

`apt upgrade` atualiza `/opt/codrug`. Na próxima vez que o usuário abrir o
CODRUG pelo menu, o launcher sincroniza a versão nova para `$HOME/CODRUG`
(de novo, preservando `JOBS/`). O venv em `~/.venv/CODRUG` não é recriado
automaticamente por uma atualização do pacote — `ensure_venv()` só recria o
venv se a versão do Python dentro dele mudar; para forçar reinstalação de
dependências científicas, use o botão "Instalação de Requisitos" na aba
HOME do próprio app.

## Desinstalar

```bash
sudo apt remove codrug     # mantém ~/CODRUG e ~/.venv/CODRUG
sudo apt purge codrug      # idem — avisa no terminal, mas não apaga nada em $HOME
```

Dados por-usuário (`~/CODRUG`, incluindo `~/CODRUG/JOBS`, e
`~/.venv/CODRUG`) nunca são apagados automaticamente pelo pacote — remova
manualmente se quiser liberar espaço.

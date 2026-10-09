# Empacotamento .deb do CODRUG

## Build

```bash
packaging/deb/build.sh              # versão = BIN/versao.py (ex.: 1.0.0-1)
packaging/deb/build.sh 1.0.0-2      # versão explícita
```

Gera `packaging/dist/codrug_<versão>_all.deb`. Antes de gerar um novo pacote,
atualize `BIN/versao.py` e o topo de `packaging/deb/changelog` com o mesmo
número — o script recusa rodar se os dois divergirem. Regras para escolher o
número (MAJOR/MINOR/PATCH-N) e o motivo da época `1:` no campo `Version` em
[`packaging/VERSIONING.md`](../VERSIONING.md).

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
   `$HOME/CODRUG/PROJECTS`, que guarda os resultados do usuário) e chama
   `python3 $HOME/CODRUG/CODRUG.py`.
2. `CODRUG.py` (código já existente, inalterado por este empacotamento)
   detecta que ainda não está rodando no venv-alvo e chama
   `bootstrap_pyqt5(interactive=True, reexec=True)` em
   `BIN/module_requirements.py`, que:
   - cria `$HOME/.venv/CODRUG` com Python 3.10;
   - instala PyQt5 e, em seguida, o restante das dependências científicas
     (RDKit, scikit-learn, etc.) — pelo botão "Instalação de
     Requisitos" na aba HOME ou pela splash screen;
   - se reinicia (`os.execve`) já dentro do venv.
3. A splash screen (`BIN/splash_screen.py`) recria/atualiza também o
   `.desktop` em `~/.local/share/applications/CODRUG.desktop` e a estrutura
   de subpastas dentro de `$HOME/CODRUG`.

O `.desktop` usa `Terminal=false`: o CODRUG abre sem terminal, e a saída do
programa (prints, erros, saída de subprocessos) é gravada em
`~/.cache/codrug/terminal_<PID>.log`, que pode ser acompanhada ao vivo por
**Help > Terminal**. A exceção é a primeira execução: sem o venv ainda
criado, o passo 2 usa `input()` para confirmar a criação do ambiente, então
`/usr/bin/codrug` se reabre sozinho dentro de um emulador de terminal
(gnome-terminal, x-terminal-emulator ou xterm) só nessa vez. Instalações de
pacotes do sistema pedidas pela interface (ex.: Java via apt) usam `pkexec`
— senha numa janela gráfica — quando não há terminal.

## Por que o pacote não cria o venv/instala as dependências no `postinst`

`postinst`/`postrm` rodam como **root**, durante `apt install`/`dpkg -i`.
Nesse momento:

- `$HOME` não é o home do usuário final (é `/root` ou indefinido) — não dá
  para localizar `$HOME/CODRUG` de forma confiável, e em máquina
  multiusuário a pergunta "de qual usuário?" nem faz sentido para um
  pacote de sistema;
- instalar via pip pacotes pesados (RDKit, TensorFlow, PyTorch)
  depende de rede, demora minutos, e se falhar no meio deixa o `dpkg` em
  estado `half-configured`, travando qualquer `apt` seguinte até conserto
  manual — contra as boas práticas de empacotamento Debian.

Por isso o pacote fica deliberadamente fino: só coloca arquivos em
`/opt/codrug`, registra o menu, e deixa o bootstrap por-usuário para o
próprio `CODRUG.py`, que já existia antes deste empacotamento.

## Atualizações

`apt upgrade` atualiza `/opt/codrug`. Na próxima vez que o usuário abrir o
CODRUG pelo menu, o launcher sincroniza a versão nova para `$HOME/CODRUG`
(de novo, preservando `PROJECTS/`). O venv em `~/.venv/CODRUG` não é recriado
automaticamente por uma atualização do pacote — `ensure_venv()` só recria o
venv se a versão do Python dentro dele mudar; para forçar reinstalação de
dependências científicas, use o botão "Instalação de Requisitos" na aba
HOME do próprio app.

## Desinstalar

```bash
sudo apt remove codrug     # mantém ~/CODRUG e ~/.venv/CODRUG
sudo apt purge codrug      # idem — avisa no terminal, mas não apaga nada em $HOME
```

Dados por-usuário (`~/CODRUG`, incluindo `~/CODRUG/PROJECTS`, e
`~/.venv/CODRUG`) nunca são apagados automaticamente pelo pacote — remova
manualmente se quiser liberar espaço.

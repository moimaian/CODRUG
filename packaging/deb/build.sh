#!/bin/bash
# Monta o pacote codrug_<versão>_all.deb a partir do estado atual do repo.
#
# Uso:
#   packaging/deb/build.sh [versão]
#
# A versão segue MAJOR.MINOR.PATCH-N (ver packaging/VERSIONING.md antes de
# escolher o próximo número: PATCH para bug fix, MINOR para funcionalidade
# nova sem quebrar nada, MAJOR para mudança incompatível; N é a revisão de
# empacotamento, só sobe sozinha se for uma mudança que não toca em
# CODRUG.py nem BIN/). Sem argumento, usa BIN/versao.py (fonte única — é o
# mesmo valor mostrado no rodapé das abas e em Help > About). Lembre de:
# 1) atualizar BIN/versao.py, 2) adicionar a entrada correspondente no topo
# de packaging/deb/changelog, antes de rodar este script.
#
# O campo Version do DEBIAN/control leva a época "1:" (ver VERSIONING.md):
# os .deb antigos eram numerados por data (2026.10.08 > 1.0.0 para o dpkg).
#
# O .deb resultante é gravado em packaging/dist/.

set -euo pipefail
umask 022   # garante dirs 755 / arquivos 644 no staging, independente do umask local

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/packaging/dist"
VERSAO_CODIGO="$(sed -n 's/^VERSAO = "\(.*\)"$/\1/p' "$PROJECT_ROOT/BIN/versao.py")"
VERSAO_CHANGELOG="$(sed -n '1s/^codrug (\(.*\)).*/\1/p' "$SCRIPT_DIR/changelog")"
if [ -z "$VERSAO_CODIGO" ] || [ "$VERSAO_CODIGO" != "$VERSAO_CHANGELOG" ]; then
    echo "build.sh: BIN/versao.py ($VERSAO_CODIGO) e o topo de packaging/deb/changelog" >&2
    echo "          ($VERSAO_CHANGELOG) estão em versões diferentes — atualize os dois" >&2
    echo "          antes de empacotar (ver packaging/VERSIONING.md)." >&2
    exit 1
fi
VERSION="${1:-$VERSAO_CODIGO}"
DEB_EPOCH="1"

for tool in dpkg-deb rsync gzip; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "build.sh: dependência ausente: $tool" >&2
        exit 1
    fi
done

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

echo "==> Preparando staging em $STAGE"
mkdir -p \
    "$STAGE/DEBIAN" \
    "$STAGE/opt/codrug" \
    "$STAGE/usr/bin" \
    "$STAGE/usr/share/applications" \
    "$STAGE/usr/share/doc/codrug"

echo "==> Copiando arquivos da aplicação para /opt/codrug"
rsync -a \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    "$PROJECT_ROOT/CODRUG.py" \
    "$PROJECT_ROOT/BIN" \
    "$PROJECT_ROOT/MIDIA" \
    "$PROJECT_ROOT/BASE" \
    "$PROJECT_ROOT/TEST" \
    "$PROJECT_ROOT/TUTORIALS" \
    "$PROJECT_ROOT/LICENSE.txt" \
    "$PROJECT_ROOT/README.md" \
    "$STAGE/opt/codrug/"

# Normaliza permissões: o diretório de trabalho local pode ter modos
# incomuns (ex.: BIN/ ficou 700 na máquina de desenvolvimento); o
# pacote precisa ser legível/executável por qualquer usuário do sistema.
find "$STAGE/opt/codrug" -type d -exec chmod 755 {} +
find "$STAGE/opt/codrug" -type f -exec chmod 644 {} +
chmod 755 "$STAGE/opt/codrug/CODRUG.py"

echo "==> Instalando launcher e menu"
install -m 755 "$SCRIPT_DIR/codrug-launcher" "$STAGE/usr/bin/codrug"
install -m 644 "$SCRIPT_DIR/codrug.desktop" "$STAGE/usr/share/applications/codrug.desktop"
install -m 644 "$PROJECT_ROOT/LICENSE.txt" "$STAGE/usr/share/doc/codrug/copyright"
install -m 644 "$PROJECT_ROOT/README.md" "$STAGE/usr/share/doc/codrug/README.md"
gzip -9nc "$SCRIPT_DIR/changelog" > "$STAGE/usr/share/doc/codrug/changelog.Debian.gz"
chmod 644 "$STAGE/usr/share/doc/codrug/changelog.Debian.gz"

echo "==> Gerando DEBIAN/control (versão $DEB_EPOCH:$VERSION)"
INSTALLED_SIZE="$(du -sk "$STAGE/opt/codrug" | cut -f1)"
sed \
    -e "s/@VERSION@/$DEB_EPOCH:$VERSION/" \
    -e "s/@INSTALLED_SIZE@/$INSTALLED_SIZE/" \
    "$SCRIPT_DIR/control.in" > "$STAGE/DEBIAN/control"

install -m 755 "$SCRIPT_DIR/postinst" "$STAGE/DEBIAN/postinst"
install -m 755 "$SCRIPT_DIR/postrm" "$STAGE/DEBIAN/postrm"

mkdir -p "$DIST_DIR"
OUT_DEB="$DIST_DIR/codrug_${VERSION}_all.deb"

echo "==> Empacotando $OUT_DEB"
dpkg-deb --root-owner-group --build "$STAGE" "$OUT_DEB"

if command -v lintian >/dev/null 2>&1; then
    echo "==> lintian (informativo, não interrompe o build)"
    lintian "$OUT_DEB" || true
fi

echo "==> Pronto: $OUT_DEB"

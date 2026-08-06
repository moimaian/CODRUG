#!/bin/bash
# Monta o pacote codrug_<versão>_all.deb a partir do estado atual do repo.
#
# Uso:
#   packaging/deb/build.sh [versão]
#
# Sem argumento, a versão é a data de hoje (AAAA.MM.DD). Passe uma versão
# explícita para releases nomeadas, ex.: packaging/deb/build.sh 2026.08.06
#
# O .deb resultante é gravado em packaging/dist/.

set -euo pipefail
umask 022   # garante dirs 755 / arquivos 644 no staging, independente do umask local

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/packaging/dist"
VERSION="${1:-$(date +%Y.%m.%d)}"

for tool in dpkg-deb rsync; do
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
    "$PROJECT_ROOT/MODULES" \
    "$PROJECT_ROOT/ICONS" \
    "$PROJECT_ROOT/BASE" \
    "$PROJECT_ROOT/TEST" \
    "$PROJECT_ROOT/TUTORIALS" \
    "$PROJECT_ROOT/LICENSE.txt" \
    "$PROJECT_ROOT/README.md" \
    "$STAGE/opt/codrug/"

# Normaliza permissões: o diretório de trabalho local pode ter modos
# incomuns (ex.: MODULES/ ficou 700 na máquina de desenvolvimento); o
# pacote precisa ser legível/executável por qualquer usuário do sistema.
find "$STAGE/opt/codrug" -type d -exec chmod 755 {} +
find "$STAGE/opt/codrug" -type f -exec chmod 644 {} +
chmod 755 "$STAGE/opt/codrug/CODRUG.py"

echo "==> Instalando launcher e menu"
install -m 755 "$SCRIPT_DIR/codrug-launcher" "$STAGE/usr/bin/codrug"
install -m 644 "$SCRIPT_DIR/codrug.desktop" "$STAGE/usr/share/applications/codrug.desktop"
install -m 644 "$PROJECT_ROOT/LICENSE.txt" "$STAGE/usr/share/doc/codrug/copyright"
install -m 644 "$PROJECT_ROOT/README.md" "$STAGE/usr/share/doc/codrug/README.md"

echo "==> Gerando DEBIAN/control (versão $VERSION)"
INSTALLED_SIZE="$(du -sk "$STAGE/opt/codrug" | cut -f1)"
sed \
    -e "s/@VERSION@/$VERSION/" \
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

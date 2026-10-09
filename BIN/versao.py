"""Versão do CODRUG — única fonte de verdade, importada tanto pela própria
interface (rodapé de todas as abas, entre BACK e NEXT, e diálogo Help > About)
quanto por packaging/deb/build.sh (que a usa como padrão ao gerar o .deb).

Ver packaging/VERSIONING.md para as regras de quando subir MAJOR, MINOR ou
PATCH. A cada mudança que altere a versão, atualize o valor abaixo e
adicione a entrada correspondente no topo de packaging/deb/changelog (mesmo
número, os dois têm que bater)."""

VERSAO = "1.0.0-1"

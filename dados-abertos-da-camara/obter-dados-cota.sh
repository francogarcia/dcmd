#!/usr/bin/env bash

set -Eeuo pipefail

INPUT_URL_2025="https://www.camara.leg.br/cotas/Ano-2025.json.zip"
INPUT_DADOS_DEPUTADOS_2025="https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura=57&ordem=ASC&ordenarPor=nome"
DIRETORIO_DATASETS="$(pwd)/input/datasets/"

INPUT_DIRETORIO_TEMPORARIO_DOWNLOAD="/tmp/download/"

mkdir -p "${DIRETORIO_DATASETS}"

mkdir -p "${INPUT_DIRETORIO_TEMPORARIO_DOWNLOAD}"
pushd "${INPUT_DIRETORIO_TEMPORARIO_DOWNLOAD}"

# ISO string (use -Ns for nanoseconds).
timestamp=$(date -Is)

wget ${INPUT_URL_2025}
unzip *.zip
checksum_cota_2025=$(sha256sum *.zip | jq -Rs .)

curl -X 'GET' \
     "${INPUT_DADOS_DEPUTADOS_2025}" \
     -H 'accept: application/json' \
     > "lista-deputados.json"
checksum_dados_deputados_2025=$(sha256sum lista-deputados.json | jq -Rs .)

cp *.json "${DIRETORIO_DATASETS}"

echo "{
  \"timestamp\": \"${timestamp}\",
  \"files\": [
    \"${INPUT_URL_2025}\",
    \"${INPUT_DADOS_DEPUTADOS_2025}\"
  ],
  \"checksums-sha256\": [
     ${checksum_cota_2025},
     ${checksum_dados_deputados_2025}
  ]
}" \
     > "${DIRETORIO_DATASETS}/dados-metadados-entrada.json"

cat "${DIRETORIO_DATASETS}/dados-metadados-entrada.json"

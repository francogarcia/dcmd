#!/usr/bin/env bash

echo "Removendo arquivos gerados anteriormente..."
rm -r ./output

set -Eeuo pipefail

echo "Obtendo dependências e criando diretórios..."
./dependencias.sh

source virtual_environment/bin/activate

echo "Baixando os dados da cota..."
./obter-dados-cota.sh
echo "Baixando os dados de contato..."
python dados-deputados.py
python historicos-deputados.py

echo "Processando os dados..."
python processamento-historico-deputados.py
python gastos-deputados.py

echo "---"
echo "Pronto!"

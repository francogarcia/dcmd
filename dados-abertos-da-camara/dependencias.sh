#!/usr/bin/env bash

python -m venv virtual_environment

source virtual_environment/bin/activate

pip install jsonpickle

pip install matplotlib
pip install numpy
pip install pandas

pip install odfpy
pip install openpyxl

pip install jinja2

pip install svg-python

pip install httpx

mkdir -p ./input/api/
mkdir -p ./input/datasets/
mkdir -p ./input/datasets/testes/
mkdir -p ./input/deputados/2025/

mkdir -p ./output/
mkdir -p ./output/api/votacoes
mkdir -p ./output/datasets/gastos/2025/
mkdir -p ./output/datasets/gastos/2025/por-deputado/2025/
mkdir -p ./output/datasets/gastos/2025/por-partido/2025/

import datetime
from dateutil.relativedelta import relativedelta
import json
import math
import os
import time


LISTA_DADOS_DEPUTADOS_ENTRADA = "./input/datasets/lista-deputados.json"
DADOS_DEPUTADOS_ENTRADA = "./input/deputados/2025/"
HISTORICOS_DEPUTADOS_ENTRADA = "./input/deputados/2025-historicos/"
HISTORICOS_DEPUTADOS_SAIDA = "./input/deputados/historico-deputados-2025.json"


SALARIO_2025_JANEIRO = 44_008.52
SALARIO_2025 = 46_366.19
ID_LEGISLATURA = 57

# curl -X 'GET' \
    #  'https://dadosabertos.camara.leg.br/api/v2/referencias/situacoesDeputado' \
    #  -H 'accept: application/json'

SITUACOES_POSSIVEIS = {
    "Afastado": {
        "sigla": "A",
        "nome": "Afastado",
    },
    "Convocado": {
        "sigla": "C",
        "nome": "Convocado",
    },
    "Exercício": {
        "sigla": "E",
        "nome": "Exercício",
    },
    "Fim de Mandato": {
        "sigla": "F",
        "nome": "Fim de Mandato",
    },
    "Licença": {
        "sigla": "L",
        "nome": "Licença",
    },
    "Suplência": {
        "sigla": "S",
        "nome": "Suplência",
    },
    "Suspenso": {
        "sigla": "U",
        "nome": "Suspenso",
    },
    "Vacância": {
        "sigla": "V",
        "nome": "Vacância",
    }
}

SITUACOES_SALARIO = [
    SITUACOES_POSSIVEIS["Exercício"]["nome"],
]

# SITUACOES_INICIO_SALARIO = [
#     SITUACOES_POSSIVEIS["Exercício"]["nome"],
# ]

# SITUACOES_FIM_SALARIO = [
#     SITUACOES_POSSIVEIS["Afastado"]["nome"],
#     SITUACOES_POSSIVEIS["Convocado"]["nome"],
#     SITUACOES_POSSIVEIS["Fim de Mandato"]["nome"],
#     SITUACOES_POSSIVEIS["Licença"]["nome"],
#     SITUACOES_POSSIVEIS["Suplência"]["nome"],
#     SITUACOES_POSSIVEIS["Suspenso"]["nome"],
#     SITUACOES_POSSIVEIS["Vacância"]["nome"],
# ]


def processe_historicos_deputados():
    # TODO timestamp = datetime.datetime.fromisoformat(timestamp_dados)
    timestamp_analise_dados = datetime.datetime.now()
    mes_analise_dados = timestamp_analise_dados.month
    # TODO Usar este valor para ano ao invés de 2025.
    ano_analise_dados = timestamp_analise_dados.year

    with open(LISTA_DADOS_DEPUTADOS_ENTRADA) as arquivo:
        conteudo = json.load(arquivo)
        dados_deputados_entrada = conteudo["dados"]

    historicos_deputados = {}

    numero_deputados = len(dados_deputados_entrada)
    print(f"Número de deputados (pode conter duplicatas com mudanças de partidos): {numero_deputados}")

    for indice_deputado, dados_deputado in enumerate(dados_deputados_entrada):
        idDeputado = dados_deputado["id"]
        idLegislatura = dados_deputado["idLegislatura"]
        nome = dados_deputado["nome"]
        siglaPartido = dados_deputado["siglaPartido"]
        siglaUF = dados_deputado["siglaUf"]

        caminho_arquivo = os.path.join(HISTORICOS_DEPUTADOS_ENTRADA, f"historico-deputado-{idDeputado}.json")
        if (not os.path.exists(caminho_arquivo)):
            print(f"Deputado: {idDeputado} - {nome} ({siglaPartido} / {siglaUF})")
            print(f"[ERROR] Arquivo não encontrado: {caminho_arquivo}")
            sys.exit(1)
            continue

        ultima_situacao_antes_2025 = ""
        situacoes_2025 = []

        with open(caminho_arquivo, "r") as file:
            dados_json = json.loads(file.read().encode("utf-8"))
            dados = dados_json["dados"]
            dados = sorted(dados, key=lambda item: item["dataHora"])

            for item_historico in dados:
                historico_id_deputado = item_historico["id"]
                historico_data_hora = datetime.datetime.fromisoformat(item_historico["dataHora"])
                historico_situacao = item_historico["situacao"]
                historico_condicao_eleitoral = item_historico["condicaoEleitoral"]
                historico_descricao_status = item_historico["descricaoStatus"]
                historico_legislatura = item_historico["idLegislatura"]

                if (historico_legislatura != ID_LEGISLATURA):
                    continue

                # print(historico_data_hora)
                if (historico_data_hora.year < 2025):
                    ultima_situacao_antes_2025 = historico_situacao
                    continue

                situacoes_2025.append({
                    "situacao": historico_situacao,
                    "data_hora": historico_data_hora,
                    "descricao_status": historico_descricao_status,
                    "condicao_eleitoral": historico_condicao_eleitoral,
                })

        # if (len(situacoes_2025) <= 0):
        #     continue

        # print(caminho_arquivo)
        print(idDeputado, idLegislatura, f"{nome} ({siglaPartido} / {siglaUF})")
        print("Situações antes de 2025:", ultima_situacao_antes_2025)
        meses_salario_2025 = 0
        dias_em_exercicio_2025 = -1
        salario_estimado_2025 = 0
        if (len(situacoes_2025) > 0):
            print("Situações em 2025:", situacoes_2025)

            # duracao_em_exercicio = datetime.timedelta()
            duracao_em_exercicio = relativedelta()
            ultima_situacao = ultima_situacao_antes_2025
            data_hora_ultima_situacao = datetime.datetime.fromisoformat("2024-12-31T23:59")
            incluir_salario_janeiro = False
            for item_situacao in situacoes_2025:
                nova_situacao = item_situacao["situacao"]
                nova_data_hora = item_situacao["data_hora"]
                nova_descricao_status = item_situacao["descricao_status"]
                nova_condicao_eleitoral = item_situacao["condicao_eleitoral"]
                print(f"| {nova_data_hora} | Situação: {nova_situacao} | Condição: {nova_condicao_eleitoral} | Descrição: {nova_descricao_status}")

                # recebeu_salario = (ultima_situacao in SITUACOES_SALARIO) or (nova_situacao in SITUACOES_SALARIO)
                recebeu_salario = (ultima_situacao in SITUACOES_SALARIO)
                if (recebeu_salario):
                    if ((data_hora_ultima_situacao >= datetime.datetime(2024, 12, 31, 0, 0, 0)) and (data_hora_ultima_situacao <= datetime.datetime(2025, 1, 31, 23, 59, 59))):
                        print("month", data_hora_ultima_situacao.month)
                        incluir_salario_janeiro = True

                    delta = nova_data_hora - data_hora_ultima_situacao
                    print("delta", delta)
                    duracao_em_exercicio += delta

                ultima_situacao = nova_situacao
                data_hora_ultima_situacao = nova_data_hora

            if (ultima_situacao in SITUACOES_SALARIO):
                duracao_em_exercicio += timestamp_analise_dados - data_hora_ultima_situacao

            # print("em exercício:", duracao_em_exercicio)
            print("Dias em exercício:", duracao_em_exercicio.days)
            if (duracao_em_exercicio.days > 0):
                dias_em_exercicio_2025 = duracao_em_exercicio.days
                meses_salario_2025 = duracao_em_exercicio.days / 30.0

            print("Meses em exercício 2025:", meses_salario_2025)
            meses_salario_2025 = math.floor(meses_salario_2025)

            assert (meses_salario_2025 <= mes_analise_dados)
            salario_estimado_2025 = max(0.0, SALARIO_2025_JANEIRO + (meses_salario_2025 - 1) * SALARIO_2025)
        else:
            if (ultima_situacao_antes_2025 in SITUACOES_SALARIO):
                meses_salario_2025 = mes_analise_dados
                salario_estimado_2025 = max(0.0, SALARIO_2025_JANEIRO + (meses_salario_2025 - 1) * SALARIO_2025)


        print("Meses de salário em 2025:", meses_salario_2025)
        print(f"Salário estimado até {mes_analise_dados}/2025: {salario_estimado_2025}")
        print()
        # if (indice_deputado > 30):
        #     return

        historicos_deputados[idDeputado] = {
            "id_deputado": idDeputado,
            "id_legislatura": idLegislatura,
            "2025": {
                "ano_analise": ano_analise_dados,
                "dias_em_exercicio": dias_em_exercicio_2025,
                "meses_salario": meses_salario_2025,
                "salario": salario_estimado_2025,
            },
        }

    return historicos_deputados


def main():
    historicos_deputados = processe_historicos_deputados()
    print("Número de históricos analisados:", len(historicos_deputados))
    with open(HISTORICOS_DEPUTADOS_SAIDA, "w") as file:
        json.dump(historicos_deputados, file)


if __name__ == "__main__":
    main()

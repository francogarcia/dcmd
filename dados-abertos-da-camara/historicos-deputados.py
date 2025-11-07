import datetime
import httpx
import json
import os
import time


IGNORAR_DEPUTADO_SE_JA_EXISTIR_ARQUIVO = True
LISTA_DADOS_DEPUTADOS_ENTRADA = "./input/datasets/lista-deputados.json"
DADOS_DEPUTADOS_ENTRADA = "./input/deputados/2025/"
HISTORICOS_DEPUTADOS_SAIDA = "./input/deputados/2025-historicos/"
TEMPO_ENTRE_REQUISICOES_MS = 1000
# None para infinito
TIMEOUT_REQUISICAO_MS = 300.0 * 1000
URL_BASE_API_HISTORICOS_DEPUTADOS = f"https://dadosabertos.camara.leg.br/api/v2/deputados"
URL_SUFIXO_API_HISTORICOS_DEPUTADOS = f"historico"


def baixe_historicos_deputados():
    with open(LISTA_DADOS_DEPUTADOS_ENTRADA) as arquivo:
        conteudo = json.load(arquivo)
        dados_deputados_entrada = conteudo["dados"]

    numero_deputados = len(dados_deputados_entrada)
    print(f"Número de deputados (pode conter duplicatas com mudanças de partidos): {numero_deputados}")

    for indice_deputado, dados_deputado in enumerate(dados_deputados_entrada):
        idDeputado = dados_deputado["id"]
        idLegislatura = dados_deputado["idLegislatura"]
        nome = dados_deputado["nome"]
        siglaPartido = dados_deputado["siglaPartido"]
        siglaUF = dados_deputado["siglaUf"]

        caminho_arquivo = os.path.join(HISTORICOS_DEPUTADOS_SAIDA, f"historico-deputado-{idDeputado}.json")
        if (IGNORAR_DEPUTADO_SE_JA_EXISTIR_ARQUIVO):
            if (os.path.exists(caminho_arquivo)):
                print("[Já existe]", idDeputado, idLegislatura, f"{nome} ({siglaPartido} / {siglaUF})")
                continue
            else:
                print("[Necessário]", idDeputado, idLegislatura, f"{nome} ({siglaPartido} / {siglaUF})")

        try:
            headers = {
                "accept": "application/json",
            }
            resposta = httpx.get(f"{URL_BASE_API_HISTORICOS_DEPUTADOS}/{idDeputado}/{URL_SUFIXO_API_HISTORICOS_DEPUTADOS}",
                                 headers=headers,
                                 timeout=TIMEOUT_REQUISICAO_MS / 1000.0,
                                 )
            if (resposta.status_code == httpx.codes.OK):
                dados_json = resposta.json()
                with open(caminho_arquivo, "w") as file:
                    json.dump(dados_json, file)
            else:
                # TODO Tentar novamente.
                resposta.raise_for_status()
        except httpx.HTTPError as exc:
            # TODO Tentar novamente.
            print(f"HTTP Exception for {exc.request.url} - {exc}")

        time.sleep(TEMPO_ENTRE_REQUISICOES_MS / 1000.0)

        print(idDeputado, idLegislatura, f"{nome} ({siglaPartido} / {siglaUF})")


def main():
    baixe_historicos_deputados()


if __name__ == "__main__":
    main()

import httpx
import json
import os
import time


LISTA_DADOS_DEPUTADOS_ENTRADA = "./input/datasets/lista-deputados.json"
DADOS_DEPUTADOS_SAIDA = "./input/deputados/2025/"
TEMPO_ENTRE_REQUISICOES_MS = 1000
URL_BASE_API_DADOS_DEPUTADOS = f"https://dadosabertos.camara.leg.br/api/v2/deputados"


def main():
    with open(LISTA_DADOS_DEPUTADOS_ENTRADA) as arquivo:
        conteudo = json.load(arquivo)
        dados_deputados_entrada = conteudo["dados"]

    numero_deputados = len(dados_deputados_entrada)
    print(f"Número de deputados: {numero_deputados}")

    for indice_deputado, dados_deputado in enumerate(dados_deputados_entrada):
        idDeputado = dados_deputado["id"]
        idLegislatura = dados_deputado["idLegislatura"]
        nome = dados_deputado["nome"]
        siglaPartido = dados_deputado["siglaPartido"]
        siglaUF = dados_deputado["siglaUf"]
        urlFoto = dados_deputado["urlFoto"]

        print(f"{indice_deputado + 1} / {numero_deputados}")
        print(idDeputado, idLegislatura, f"{nome} ({siglaPartido} / {siglaUF})", f"<{urlFoto}>")

        try:
            headers = {
                "accept": "application/json",
            }
            resposta = httpx.get(f"{URL_BASE_API_DADOS_DEPUTADOS}/{idDeputado}",
                                 headers=headers,
                                 )
            if (resposta.status_code == httpx.codes.OK):
                dados_json = resposta.json()
                # print(dados_json)
                # TODO FIXME Alguns deputados mudaram de partido e possuem mais de uma entrada.
                with open(os.path.join(DADOS_DEPUTADOS_SAIDA, f"dados-deputado-{idDeputado}.json"), "w") as file:
                    json.dump(dados_json, file)
            else:
                # TODO Tentar novamente.
                resposta.raise_for_status()
        except httpx.HTTPError as exc:
            # TODO Tentar novamente.
            print(f"HTTP Exception for {exc.request.url} - {exc}")

        time.sleep(TEMPO_ENTRE_REQUISICOES_MS / 1000.0)


if __name__ == "__main__":
    main()

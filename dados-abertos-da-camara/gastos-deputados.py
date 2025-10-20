# import glob
import json
import numpy as np
import os
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import re

import locale
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


INPUT_YEAR = 2025
INPUT_FILE = f"./input/datasets/Ano-{INPUT_YEAR}.json"
INPUT_OUTPUT_DIR = os.path.join("./output/datasets/gastos/", f"{INPUT_YEAR}")
INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR = os.path.join("por-deputado/", f"{INPUT_YEAR}")
INPUT_OUTPUT_POR_PARTIDOS_SUBDIR = os.path.join("por-partido/", f"{INPUT_YEAR}")

INPUT_DROP_NA_ROWS = False
INPUT_DROP_ROWS_BEFORE_INPUT_YEAR = True

# If > 0, the chosen number of rows from the dataframe.
INPUT_USE_DATASET_SAMPLE = -1
# INPUT_USE_DATASET_SAMPLE = 100

# True: Ignora as chamadas para processamento de dados e geração de respostas.
INPUT_DEV_MODE = False
INPUT_DEV_MODE_FORCE_RUN = True
INPUT_USE_TEST_DATASET = False
if (INPUT_USE_TEST_DATASET):
    INPUT_FILE = "./input/datasets/testes/Ano-2025-test.json"


NOME_PARLAMENTAR = "nomeParlamentar"
CPF = "cpf"
ID_DEPUTADO = "idDeputado"
NUMERO_CARTEIRA_PARLAMENTAR = "numeroCarteiraParlamentar"
LEGISLATURA = "legislatura"
SIGLA_UF = "siglaUF"
SIGLA_PARTIDO = "siglaPartido"
CODIGO_LEGISLATURA = "codigoLegislatura"
NUMERO_SUB_COTA = "numeroSubCota"
DESCRICAO = "descricao"
NUMERO_ESPECIFICACAO_SUB_COTA = "numeroEspecificacaoSubCota"
DESCRICAO_ESPECIFICACAO = "descricaoEspecificacao"
FORNECEDOR = "fornecedor"
CNPJ_CPF = "cnpjCPF"
NUMERO = "numero"
TIPO_DOCUMENTO = "tipoDocumento"
DATA_EMISSAO = "dataEmissao"
VALOR_DOCUMENTO = "valorDocumento"
VALOR_GLOSA = "valorGlosa"
VALOR_LIQUIDO = "valorLiquido"
MES = "mes"
ANO = "ano"
PARCELA = "parcela"
PASSAGEIRO = "passageiro"
TRECHO = "trecho"
LOTE = "lote"
RESSARCIMENTO = "ressarcimento"
DAT_PAGAMENTO_RESTITUICAO = "datPagamentoRestituicao"
RESTITUICAO = "restituicao"
NUMERO_DEPUTADO_ID = "numeroDeputadoID"
ID_DOCUMENTO = "idDocumento"
URL_DOCUMENTO = "urlDocumento"

NUMERO_DEPUTADOS_PARTIDO = "numeroDeputadosPartido"
QUANTIA_MAXIMA_ANTES_NOTACAO_CIENTIFICA = 30_000_000.00

# df = pd.read_json("./input/datasets/testes/Ano-2025-min.json")
#
# input_files = glob.glob(os.path.join("./input/datasets/testes/", "*.json"))
# individual_dfs = (pd.read_json(f) for f in input_files)
# df = pd.concat(individual_dfs, ignore_index=True)

with open(INPUT_FILE) as file:
    # dados = json.load(file)
    dados = json.loads(file.read().encode("utf-8"))
    dados = dados["dados"]
    df = pd.DataFrame.from_dict(dados)
    # print(df.to_string())

if (INPUT_USE_DATASET_SAMPLE > 0):
    df = df.sample(INPUT_USE_DATASET_SAMPLE)

# Ajustes em colunas.
# df = df.astype(str)
df[ID_DEPUTADO] = df[ID_DEPUTADO].astype("Int64") # int does not suport NA values; it is also Int64, not int64.
df[SIGLA_PARTIDO] = df[SIGLA_PARTIDO].astype("string")
df[DESCRICAO] = df[DESCRICAO].astype("string")
df[VALOR_LIQUIDO] = df[VALOR_LIQUIDO].astype(float)
# Ajustar para tempo.
# df[DATA_EMISSAO] = df.drop(df[[DATA_EMISSAO < "2025-01-01"]].index)
df[DATA_EMISSAO] = pd.to_datetime(df[DATA_EMISSAO])
if (INPUT_DROP_ROWS_BEFORE_INPUT_YEAR):
    df = df[(df[DATA_EMISSAO].dt.year == INPUT_YEAR)]


# <https://matplotlib.org/stable/users/explain/colors/colormaps.html>
# COLOR_MAP = plt.get_cmap("gist_rainbow")
# COLOR_MAP = plt.get_cmap("gist_stern")
COLOR_MAP = plt.get_cmap("gist_ncar")


def escreva_secao(titulo, df):
    print(titulo)
    print(len(titulo) * "=")
    print(df.to_string())
    print(200 * "-")
    print("\n")



def gere_caminho_arquivo(titulo, subdiretorio = ""):
    if (not subdiretorio):
        caminho_arquivo = os.path.join(INPUT_OUTPUT_DIR, titulo)
    else:
        caminho_arquivo = os.path.join(INPUT_OUTPUT_DIR, subdiretorio, titulo)
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

    return caminho_arquivo


def gere_dataset(titulo, df, subdiretorio = ""):
    caminho_arquivo = gere_caminho_arquivo(titulo, subdiretorio)

    export_csv = True
    if (export_csv):
        # df.to_csv(caminho_arquivo + ".csv", index=False)
        df.to_csv(caminho_arquivo + ".csv")

    export_html = False
    if (export_html):
        if (isinstance(df, pd.DataFrame)):
            df.to_html(caminho_arquivo + ".html")

    export_xlsx = False
    if (export_xlsx):
        # df.to_excel(caminho_arquivo + ".xlsx", index=False, sheet_name=titulo)
        df.to_excel(caminho_arquivo + ".xlsx", sheet_name=titulo)

    export_ods = False
    if (export_ods):
        writer = pd.ExcelWriter(caminho_arquivo + ".ods")
        # df.to_excel(writer, index=False, sheet_name=titulo)
        df.to_excel(writer, sheet_name=titulo)
        writer.close()

    export_json = False
    if (export_json):
        # json_contents = df.to_json(
        #     force_ascii=False,
        #     double_precision=10,
        #     date_unit="ms",
        #     indent=4,
        # )
        # with open(caminho_arquivo + ".json", "w") as file:
        #     json.dump(json_contents, file)
        # TODO FIXME Do not reset index, as this removes the groups. Try to use the index as a key.
        df.reset_index().to_json(
            caminho_arquivo + ".json",
            orient="records",
            force_ascii=False,
            double_precision=10,
            date_format="iso", # "epoch"
            date_unit="ms",
            indent=4,
        )


def escreva_secao_e_gere_dataset(titulo, df):
    escreva_secao(titulo, df)
    gere_dataset(titulo, df)


SOMATORIO_VALOR_LIQUIDO = (VALOR_LIQUIDO, "sum")
SOMATORIO_DESCRICAO_VALOR_LIQUIDO = (VALOR_LIQUIDO, "sum", VALOR_LIQUIDO)
def ordene_por_valor_liquido(df, colunas=[SOMATORIO_DESCRICAO_VALOR_LIQUIDO]):
    resultado = df.sort_values(by=colunas, ascending=False)
    return resultado


# NOTE                                                                                    Opcional: Dados parecem vim com " -".
CPF_PADRAO = r"^([0-9]|[0-9]{2}|[0-9]{3})[\.]?([0-9]{3})[\.]?([0-9]{3})[\.\-\/]?([0-9]{2})[\ \-]*?$"
CPF_REGEX = re.compile(CPF_PADRAO)
def e_cpf(texto):
    return CPF_REGEX.match(texto)


def esconder_cpf(linha):
    cnpjCPF = linha[CNPJ_CPF]
    if (e_cpf(cnpjCPF)):
        return "[CPF REMOVIDO]"

    return cnpjCPF

# Colunas:
# colunas = df.columns.values.tolist()
# print("Lista", colunas)
# print("List", [*df])
# print("Set", {*df})
# print("Tuple", *df)
# *colunas, = df
# print("Lista", colunas)

if (not INPUT_DEV_MODE):
    escreva_secao_e_gere_dataset("Descrição - Dados", df.describe(include="all"))
    # escreva_secao_e_gere_dataset("Descrição - Dados Categóricos", df.describe(exclude="number"))
    # escreva_secao_e_gere_dataset("Descrição - Dados Numéricos", df.describe(exclude="category"))

    # for coluna in df.columns.values.tolist():
    #     titulo = f"Descrição - {coluna}"
    #     escreva_secao_e_gere_dataset(titulo, df[coluna].describe())

# Número de valores únicos por coluna.
# print(df.nunique())
# Partidos.
# print(df[SIGLA_PARTIDO].unique())

def numero_deputados_por_partido():
    agrupamento = df[[
        SIGLA_PARTIDO,
        SIGLA_UF,
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        CPF,
    ]].groupby([
        SIGLA_PARTIDO,
    ])
    resultado = agrupamento[NUMERO_DEPUTADO_ID].nunique()
    return resultado

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Número de Deputados por Partido"
    resultado = numero_deputados_por_partido()
    escreva_secao_e_gere_dataset(titulo, resultado)

def informacaoes_deputado_por_partido():
    deputados_por_partido = numero_deputados_por_partido().to_dict()

    resultado = df[[
        SIGLA_PARTIDO,
        SIGLA_UF,
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        CPF,
    ]]
    resultado = resultado.set_index(SIGLA_PARTIDO).drop_duplicates().reset_index()
    resultado[NUMERO_DEPUTADOS_PARTIDO] = resultado.apply(lambda row: deputados_por_partido[row[SIGLA_PARTIDO]], axis=1)
    resultado = resultado.set_index(SIGLA_PARTIDO)
    resultado = resultado.sort_values(by=[SIGLA_PARTIDO])
    return resultado

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Informações de Deputados por Partido"
    resultado = informacaoes_deputado_por_partido()
    escreva_secao_e_gere_dataset(titulo, resultado)

def gastos_liquidos_por_partido():
    deputados_por_partido = numero_deputados_por_partido().to_dict()

    resultado = df[[
        SIGLA_PARTIDO,
        # SIGLA_UF,
        VALOR_LIQUIDO,
    ]]
    resultado[NUMERO_DEPUTADOS_PARTIDO] = resultado.reset_index().apply(lambda row: deputados_por_partido[row[SIGLA_PARTIDO]], axis=1)
    resultado.set_index(SIGLA_PARTIDO)

    resultado = resultado[[
        SIGLA_PARTIDO,
        # SIGLA_UF,
        VALOR_LIQUIDO,
        NUMERO_DEPUTADOS_PARTIDO,
    ]].groupby([
        SIGLA_PARTIDO,
        # SIGLA_UF,
    ]) \
    .apply( # .agg({VALOR_LIQUIDO: ["describe", "sum"], # ["count", "sum", "mean", "median", "min", "max", "std"], # np.sum, np.mean}) \
        # TODO agg -> describe
        lambda d: pd.Series({
            # VALOR_LIQUIDO:
            # VALOR_LIQUIDO: [d[VALOR_LIQUIDO].describe()],
            (VALOR_LIQUIDO, "count"): d[VALOR_LIQUIDO].count(),
            (VALOR_LIQUIDO, "mean"): d[VALOR_LIQUIDO].mean(),
            (VALOR_LIQUIDO, "std"): d[VALOR_LIQUIDO].std(),
            (VALOR_LIQUIDO, "min"): d[VALOR_LIQUIDO].min(),
            (VALOR_LIQUIDO, "25"): d[VALOR_LIQUIDO].quantile(0.25),
            (VALOR_LIQUIDO, "50%"): d[VALOR_LIQUIDO].median(),
            (VALOR_LIQUIDO, "75"): d[VALOR_LIQUIDO].quantile(0.75),
            (VALOR_LIQUIDO, "max"): d[VALOR_LIQUIDO].max(),
            # (VALOR_LIQUIDO, "sum")
            SOMATORIO_VALOR_LIQUIDO: d[VALOR_LIQUIDO].sum(),
            # Dados derivados:
            (VALOR_LIQUIDO, "mediaPorDeputado"): d[VALOR_LIQUIDO].sum() / d[NUMERO_DEPUTADOS_PARTIDO].min(),
            (VALOR_LIQUIDO, "medianaPorDeputado"): d[VALOR_LIQUIDO].median() / d[NUMERO_DEPUTADOS_PARTIDO].min(),
        }),
    )

    return resultado

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Gastos Líquidos por Partido"
    resultado = gastos_liquidos_por_partido()
    escreva_secao_e_gere_dataset(titulo, resultado)

titulo = "Gastos Líquidos por Deputado"
def gastos_liquidos_por_deputado():
    agrupamento = df[[
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
    ]].groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
    ])
    # for label, group_df in agrupamento:
    #     # print(label, group_df)
    #     nome_arquivo = f"{titulo} - {label[0]}-{label[1].replace(" ", "_")}-{label[2]}-{label[3]}"
    #     gere_dataset(nome_arquivo, group_df, os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(label[0])))

    resultado = agrupamento.agg({
        VALOR_LIQUIDO: ["describe", "sum"], # ["count", "sum", "mean", "median", "min", "max", "std"], # np.sum, np.mean
    })
    return resultado

if (not INPUT_DEV_MODE):
    resultado = gastos_liquidos_por_deputado()
    escreva_secao_e_gere_dataset(titulo, resultado)

def gastos_liquidos_por_deputado_individual():
    agrupamento = df[[
        NUMERO_DEPUTADO_ID,
        ID_DEPUTADO,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
    ]].groupby([
        NUMERO_DEPUTADO_ID,
        # ID_DEPUTADO,
    ])
    return agrupamento

if (not INPUT_DEV_MODE):
    titulo = "Gastos Líquidos por Deputado"
    resultado = gastos_liquidos_por_deputado_individual()
    for label, group_df in resultado:
        nome_arquivo = f"{titulo} - {label[0]}"
        resultado = gere_dataset(
            nome_arquivo,
            # group_df,
            group_df.reset_index().groupby([
                NUMERO_DEPUTADO_ID,
                # ID_DEPUTADO,
            ]).agg({
                VALOR_LIQUIDO: ["sum", "describe"], # ["count", "sum", "mean", "median", "min", "max", "std"], # np.sum, np.mean
            }),
            os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(label[0])),
        )

def gastos_liquidos_por_categoria_por_deputado_individual():
    agrupamento = df[[
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
        DESCRICAO,
        # FORNECEDOR,
    ]].groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
    ])
    return agrupamento

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Gastos Líquidos por Deputado por Categoria"
    resultado = gastos_liquidos_por_categoria_por_deputado_individual()
    for label, group_df in resultado:
        nome_arquivo = f"{titulo} - {label[0]}"
        df_exportacao = group_df.reset_index().groupby([
            # NUMERO_DEPUTADO_ID,
            DESCRICAO,
        ]).agg({
            VALOR_LIQUIDO: ["sum", "describe"], # ["count", "sum", "mean", "median", "min", "max", "std"], # np.sum, np.mean
        }).sort_values(
            by=[SOMATORIO_DESCRICAO_VALOR_LIQUIDO],
            ascending=False,
        )

        remover_colunas_hierarquicas = True
        if (remover_colunas_hierarquicas):
            df_exportacao = df_exportacao.reset_index()
            # df_exportacao.columns = df_exportacao.columns.get_level_values(0)
            df_exportacao.columns = ["_".join(coluna).strip().rstrip("_") for coluna in df_exportacao.columns.values]
            df_exportacao["valorLiquido_describe_count"] = df_exportacao["valorLiquido_describe_count"].astype(int)
            nomes_colunas = {
                "descricao": "Descrição",
                "valorLiquido_sum_valorLiquido": "Total (R$)",
                "valorLiquido_describe_count": "Quantidade",
                "valorLiquido_describe_mean": "Média (R$)",
                "valorLiquido_describe_std": "Desvio Padrão (R$)",
                "valorLiquido_describe_min": "Mínimo (R$)",
                "valorLiquido_describe_25%": "25º Percentil (R$)",
                "valorLiquido_describe_50%": "50º Percentil (R$)",
                "valorLiquido_describe_75%": "75º Percentil (R$)",
                "valorLiquido_describe_max": "Máximo (R$)",
            }
            df_exportacao = df_exportacao.rename(columns=nomes_colunas)
            df_exportacao = df_exportacao.set_index("Descrição")

        resultado = gere_dataset(
            nome_arquivo,
            df_exportacao,
            os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(label[0])),
        )

def gastos_liquidos_por_fornecedor_por_deputado_individual():
    agrupamento = df[[
        ID_DOCUMENTO,
        DESCRICAO,
        VALOR_DOCUMENTO,
        VALOR_GLOSA,
        VALOR_LIQUIDO,
        FORNECEDOR,
        CNPJ_CPF,
        NUMERO,
        DATA_EMISSAO,
        MES,
        ANO,
        URL_DOCUMENTO,
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        LEGISLATURA,
        SIGLA_PARTIDO,
        SIGLA_UF,
    ]].sort_values(
        by=[FORNECEDOR, DATA_EMISSAO]
    ).groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
    ])

    return agrupamento


if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Gastos Líquidos de Cada Deputado por Fornecedor"
    resultado = gastos_liquidos_por_fornecedor_por_deputado_individual()
    for label, group_df in resultado:
        nome_arquivo = f"{titulo} - {label[0]}"
        df_exportacao = group_df
        df_exportacao = df_exportacao.set_index("idDocumento")
        df_exportacao[CNPJ_CPF] = df_exportacao.apply(lambda linha: esconder_cpf(linha), axis=1)

        gere_dataset(nome_arquivo, df_exportacao, os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(label[0])))

def gastos_liquidos_por_partido():
    deputados_por_partido = numero_deputados_por_partido().to_dict()

    resultado = df[[
        SIGLA_PARTIDO,
        # SIGLA_UF,
        VALOR_LIQUIDO,
    ]]
    resultado[NUMERO_DEPUTADOS_PARTIDO] = resultado.reset_index().apply(lambda row: deputados_por_partido[row[SIGLA_PARTIDO]], axis=1)
    resultado.set_index(SIGLA_PARTIDO)

    resultado = resultado[[
        SIGLA_PARTIDO,
        # SIGLA_UF,
        VALOR_LIQUIDO,
        NUMERO_DEPUTADOS_PARTIDO,
    ]].groupby([
        SIGLA_PARTIDO,
        # SIGLA_UF,
    ]) \
    .apply( # .agg({VALOR_LIQUIDO: ["describe", "sum"], # ["count", "sum", "mean", "median", "min", "max", "std"], # np.sum, np.mean}) \
        # TODO agg -> describe
        lambda d: pd.Series({
            # VALOR_LIQUIDO:
            # VALOR_LIQUIDO: [d[VALOR_LIQUIDO].describe()],
            (VALOR_LIQUIDO, "count"): d[VALOR_LIQUIDO].count(),
            (VALOR_LIQUIDO, "mean"): d[VALOR_LIQUIDO].mean(),
            (VALOR_LIQUIDO, "std"): d[VALOR_LIQUIDO].std(),
            (VALOR_LIQUIDO, "min"): d[VALOR_LIQUIDO].min(),
            (VALOR_LIQUIDO, "25"): d[VALOR_LIQUIDO].quantile(0.25),
            (VALOR_LIQUIDO, "50%"): d[VALOR_LIQUIDO].median(),
            (VALOR_LIQUIDO, "75"): d[VALOR_LIQUIDO].quantile(0.75),
            (VALOR_LIQUIDO, "max"): d[VALOR_LIQUIDO].max(),
            # (VALOR_LIQUIDO, "sum")
            SOMATORIO_VALOR_LIQUIDO: d[VALOR_LIQUIDO].sum(),
            # Dados derivados:
            (VALOR_LIQUIDO, "mediaPorDeputado"): d[VALOR_LIQUIDO].sum() / d[NUMERO_DEPUTADOS_PARTIDO].min(),
            (VALOR_LIQUIDO, "medianaPorDeputado"): d[VALOR_LIQUIDO].median() / d[NUMERO_DEPUTADOS_PARTIDO].min(),
        }),
    )

    return resultado

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Gastos Líquidos por Partido"
    resultado = gastos_liquidos_por_partido()
    escreva_secao_e_gere_dataset(titulo, resultado)

if (not INPUT_DEV_MODE or INPUT_DEV_MODE_FORCE_RUN):
    titulo = "Gastos Líquidos por Partido (ordem decrescente)"
    resultado_ordenado = ordene_por_valor_liquido(resultado, [SOMATORIO_VALOR_LIQUIDO])
    escreva_secao_e_gere_dataset(titulo, resultado_ordenado)

if (not INPUT_DEV_MODE):
    titulo = "Gastos Líquidos Por Deputado por Data"
    agrupamento = df[[
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
        DATA_EMISSAO,
    ]].sort_values(
        by=[DATA_EMISSAO]
    ).groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
    ])
    for numero_deputado_id, group_df in agrupamento:
        numero_deputado_id, = numero_deputado_id
        nome_parlamentar = group_df[[NOME_PARLAMENTAR]].mode()[NOME_PARLAMENTAR][0]
        partido_parlamentar = group_df[[SIGLA_PARTIDO]].mode()[SIGLA_PARTIDO][0]
        uf_parlamentar = group_df[[SIGLA_UF]].mode()[SIGLA_UF][0]
        label = f"{numero_deputado_id}: {nome_parlamentar} ({partido_parlamentar} / {uf_parlamentar})"

        figure, ax = plt.subplots(
            figsize=(12, 5),
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        plt.gcf().axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, pos: locale.currency(x, grouping=True)))

        color = "blue"
        point_radius = 2
        radius_area = point_radius * point_radius
        group_df.plot(
            kind="scatter",
            # or:
            # marker=".",
            # linestyle="none",
            ax=ax,
            label=label,
            x=DATA_EMISSAO,
            y=VALOR_LIQUIDO,
            xlabel="Data de emissão",
            ylabel="Gasto (R$)",
            grid = True,
            c=color,
            s=radius_area,
            # drawstyle="steps",
        )

        last_entry = ax.get_children()[-1]
        _, y = last_entry.xy
        # label = f"{label}: {locale.currency(y, grouping=True)}"
        ax.annotate(label, xy=(1,y), xytext=(6,0), color=color,
                    xycoords = ax.get_yaxis_transform(), textcoords="offset points",
                    size=14, va="center")

        plt.legend()
        caminho_arquivo = gere_caminho_arquivo(os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(numero_deputado_id), f"{titulo} - {numero_deputado_id}.png"))
        print(caminho_arquivo)
        figure.savefig(caminho_arquivo, bbox_inches='tight')
        matplotlib.pyplot.close()

if (not INPUT_DEV_MODE):
    titulo = "Gastos Líquidos Por Deputado por Data (barras)"
    agrupamento = df[[
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
        DATA_EMISSAO,
    ]].sort_values(
        by=[DATA_EMISSAO]
    ).groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
    ])
    for numero_deputado_id, group_df in agrupamento:
        numero_deputado_id, = numero_deputado_id
        nome_parlamentar = group_df[[NOME_PARLAMENTAR]].mode()[NOME_PARLAMENTAR][0]
        partido_parlamentar = group_df[[SIGLA_PARTIDO]].mode()[SIGLA_PARTIDO][0]
        uf_parlamentar = group_df[[SIGLA_UF]].mode()[SIGLA_UF][0]
        label = f"{numero_deputado_id}: {nome_parlamentar} ({partido_parlamentar} / {uf_parlamentar})"

        figure, ax = plt.subplots(
            figsize=(12, 5),
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        plt.gcf().axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, pos: locale.currency(x, grouping=True)))

        plot = group_df.groupby([
            pd.Grouper(key=DATA_EMISSAO, freq="1ME"),
        ]).agg({
            VALOR_LIQUIDO: "sum",
        }).reset_index().plot(
            kind="bar",
            ax=ax,
            label=label,
            x=DATA_EMISSAO,
            y=VALOR_LIQUIDO,
            xlabel="Data de emissão",
            ylabel="Gasto (R$)",
            grid = True,
        )
        plot.bar_label(
            plot.containers[0],
            label_type="edge",
            padding=3,
            fmt=lambda x: locale.currency(x, grouping=True),
        )

        plt.legend()
        caminho_arquivo = gere_caminho_arquivo(os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(numero_deputado_id), f"{titulo} - {numero_deputado_id}.png"))
        print(caminho_arquivo)
        figure.savefig(caminho_arquivo, bbox_inches='tight')
        matplotlib.pyplot.close()

if (not INPUT_DEV_MODE):
    titulo = "Gastos Líquidos (Cumulativos) Por Deputado por Data"
    agrupamento = df[[
        ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
        NOME_PARLAMENTAR,
        SIGLA_PARTIDO,
        SIGLA_UF,
        VALOR_LIQUIDO,
        DATA_EMISSAO,
    ]].sort_values(
        by=[DATA_EMISSAO]
    ).groupby([
        # ID_DEPUTADO,
        NUMERO_DEPUTADO_ID,
    ])
    for numero_deputado_id, group_df in agrupamento:
        numero_deputado_id, = numero_deputado_id
        nome_parlamentar = group_df[[NOME_PARLAMENTAR]].mode()[NOME_PARLAMENTAR][0]
        partido_parlamentar = group_df[[SIGLA_PARTIDO]].mode()[SIGLA_PARTIDO][0]
        uf_parlamentar = group_df[[SIGLA_UF]].mode()[SIGLA_UF][0]
        label = f"{numero_deputado_id}: {nome_parlamentar} ({partido_parlamentar} / {uf_parlamentar})"
        group_df["cumsum"] = group_df[VALOR_LIQUIDO].cumsum()

        figure, ax = plt.subplots(
            figsize=(12, 5),
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        plt.gcf().axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, pos: locale.currency(x, grouping=True)))

        group_df.plot(
            kind="line",
            ax=ax,
            label=label,
            x=DATA_EMISSAO,
            y="cumsum",
            xlabel="Data de emissão",
            ylabel="Gasto (R$)",
            grid = True,
            drawstyle="steps",
        )

        line = ax.lines[-1]
        y = line.get_ydata()[-1]
        label = f"{label}: {locale.currency(y, grouping=True)}"
        ax.annotate(label, xy=(1,y), xytext=(6,0), color=line.get_color(),
                    xycoords = ax.get_yaxis_transform(), textcoords="offset points",
                    size=14, va="center")

        plt.legend()
        caminho_arquivo = gere_caminho_arquivo(os.path.join(INPUT_OUTPUT_POR_DEPUTADOS_SUBDIR, str(numero_deputado_id), f"{titulo} - {numero_deputado_id}.png"))
        print(caminho_arquivo)
        figure.savefig(caminho_arquivo, bbox_inches='tight')
        matplotlib.pyplot.close()

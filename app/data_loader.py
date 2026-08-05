import re
from datetime import date

import pandas as pd

def _limpar_texto(serie):
    """Remove espaços comuns e o espaço invisível usado em algumas células."""
    return (
        serie.astype("string")
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
    )

def _voltar_ao_inicio(arquivo):
    """Permite reutilizar o UploadedFile do Streamlit em várias leituras."""
    if hasattr(arquivo, "seek"):
        arquivo.seek(0)


def _infer_report_month(arquivo):
    nome = getattr(arquivo, "name", "") or ""
    padroes = [
        r"(?P<ano>20\d{2})[-_/](?P<mes>0?[1-9]|1[0-2])",
        r"(?P<mes>0?[1-9]|1[0-2])[-_/](?P<ano>20\d{2})",
    ]

    for padrao in padroes:
        match = re.search(padrao, nome)
        if match:
            return date(int(match.group("ano")), int(match.group("mes")), 1)

    return date.today().replace(day=1)


def load_data_resultados(arquivo):
    _voltar_ao_inicio(arquivo)

    df_1 = pd.read_excel(arquivo, sheet_name="RESULTADOS", header=1)
    df_1.columns = df_1.columns.str.strip()

    df_1 = df_1.rename(
        columns={
            "Rótulos de Linha": "Campanha",
            "Soma de QTD_VENDA": "Qtd Venda",
            "Soma de DISPARADOS": "Disparados",
            "Soma de ENTREGUES": "Entregues",
            "Média de TAXA_ENTREGA": "Taxa de Entrega",
            "Soma de ABERTURAS": "Aberturas",
            "Soma de CLIQUES": "Cliques",
            "Soma de QTDE_CLIENTE": "Clientes",
            "VALOR_VENDA": "Receita",
            "VALOR_DESCONTO": "Desconto",
        }
    )
    df_1 = df_1.dropna(subset=["Campanha"])
    df_1 = df_1[df_1["Campanha"] != "Total Geral"]

    for coluna in [
        "Qtd Venda",
        "Disparados",
        "Entregues",
        "Aberturas",
        "Cliques",
        "Clientes",
        "Receita",
        "Desconto",
        "Taxa de Entrega",
    ]:
        if coluna in df_1.columns:
            df_1[coluna] = pd.to_numeric(df_1[coluna], errors="coerce").fillna(0)

    return df_1

def load_data_recomposicao(arquivo):
    """
    Lê os blocos da aba RECOMPOSIÇÃO e entrega uma tabela normalizada:
    Categoria, Comprador, Contato, Receita, Desconto, Taxa de Desconto
    e Participação na Receita.

    A localização dos blocos é feita pelos títulos, sem depender de números
    fixos de linha.
    """
    _voltar_ao_inicio(arquivo)
    df_bruto = pd.read_excel(
        arquivo,
        sheet_name="RECOMPOSIÇÃO",
        header=None,
    )

    if df_bruto.shape[1] < 7:
        raise ValueError(
            "A aba RECOMPOSIÇÃO não possui a estrutura esperada de 7 colunas."
        )

    primeira_coluna = _limpar_texto(df_bruto.iloc[:, 0])
    linhas_cabecalho = df_bruto.index[
        primeira_coluna.eq("Rótulos de Linha")
    ].tolist()

    if len(linhas_cabecalho) < 2:
        raise ValueError(
            "Não foi possível localizar o bloco de categorias na aba RECOMPOSIÇÃO."
        )

    # O segundo bloco da aba contém a composição por categoria.
    linha_inicio_categorias = linhas_cabecalho[1]
    linhas_total = df_bruto.index[
        (df_bruto.index > linha_inicio_categorias)
        & primeira_coluna.eq("Total Geral")
    ].tolist()

    if not linhas_total:
        raise ValueError(
            "Não foi possível localizar o Total Geral do bloco de categorias."
        )

    linha_fim_categorias = linhas_total[0]

    df_categorias = df_bruto.loc[
        linha_inicio_categorias + 1 : linha_fim_categorias - 1,
        [0, 1, 2],
    ].copy()
    df_categorias.columns = ["Categoria", "Receita", "Desconto"]
    df_categorias = df_categorias.dropna(subset=["Categoria"])
    df_categorias["Categoria"] = _limpar_texto(df_categorias["Categoria"])

    # A tabela à direita relaciona categoria, comprador e contato.
    quinta_coluna = _limpar_texto(df_bruto.iloc[:, 4])
    linhas_mapa = df_bruto.index[quinta_coluna.eq("CATEGORIAS")].tolist()

    if not linhas_mapa:
        raise ValueError(
            "Não foi possível localizar o mapa de categorias e compradores."
        )

    linha_inicio_mapa = linhas_mapa[0]

    df_mapa = df_bruto.loc[
        linha_inicio_mapa + 1 :,
        [4, 5, 6],
    ].copy()
    df_mapa.columns = ["Categoria", "Comprador", "Contato"]
    df_mapa = df_mapa.dropna(subset=["Categoria"])

    for coluna in ["Categoria", "Comprador", "Contato"]:
        df_mapa[coluna] = _limpar_texto(df_mapa[coluna])

    for coluna in ["Receita", "Desconto"]:
        df_categorias[coluna] = pd.to_numeric(
            df_categorias[coluna],
            errors="coerce",
        ).fillna(0.0)

    df_recomposicao = df_categorias.merge(
        df_mapa,
        on="Categoria",
        how="left",
        validate="many_to_one",
    )

    df_recomposicao["Comprador"] = (
        df_recomposicao["Comprador"].fillna("Não informado")
    )
    df_recomposicao["Contato"] = (
        df_recomposicao["Contato"].fillna("Não informado")
    )

    receita_sem_zero = df_recomposicao["Receita"].replace(0, pd.NA)
    receita_total = df_recomposicao["Receita"].sum()

    df_recomposicao["Taxa de Desconto"] = (
        df_recomposicao["Desconto"]
        .div(receita_sem_zero)
        .fillna(0.0)
        .astype(float)
    )

    if receita_total:
        df_recomposicao["Participação na Receita"] = (
            df_recomposicao["Receita"] / receita_total
        )
    else:
        df_recomposicao["Participação na Receita"] = 0.0

    return (
        df_recomposicao[
            [
                "Categoria",
                "Comprador",
                "Contato",
                "Receita",
                "Desconto",
                "Taxa de Desconto",
                "Participação na Receita",
            ]
        ]
        .sort_values("Receita", ascending=False)
        .reset_index(drop=True)
    )


def load_workbook_bundle(arquivo):
    report_month = _infer_report_month(arquivo)
    df_resultados = load_data_resultados(arquivo)
    df_recomposicao = load_data_recomposicao(arquivo)

    return {
        "report_month": report_month,
        "df_resultados": df_resultados,
        "df_recomposicao": df_recomposicao,
    }

def load_data_campanhas(arquivo):
        df_2 = pd.read_excel(arquivo, sheet_name = "CAMPANHAS", header = 1)
        df_2 = df_2.columns.str.strip()

        df_2 = df_2.rename(columns = [
                
        ])

def formata_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formata_int(valor):
    return f"{valor:,.0f}".replace(",", ".")
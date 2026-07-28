import time
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_loader import (
    formata_brl,
    formata_int,
    load_data_recomposicao,
    load_data_resultados,
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
logo_path = PROJECT_ROOT / "assets" / "LINKEDIN - CAPA.png"


def initialize_session():
    if "brands" not in st.session_state:
        st.session_state.brands = ["Unilever"]

    if "selected_brand" not in st.session_state:
        st.session_state.selected_brand = st.session_state.brands[0]


@st.dialog("Nova Marca")
def add_brand():
    brand_name = st.text_input("Nome da marca")

    if st.button("Salvar"):
        if brand_name.strip():
            st.session_state.brands.append(brand_name)
            st.session_state.selected_brand = brand_name
            st.rerun()


@st.dialog("Excluir")
def delete_brand():
    st.write(
        f"Deseja realmente excluir a marca **{st.session_state.selected_brand}**?"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancelar"):
            st.rerun()

    with col2:
        if st.button("Excluir"):
            st.session_state.brands.remove(st.session_state.selected_brand)

            if st.session_state.brands:
                st.session_state.selected_brand = st.session_state.brands[0]
            else:
                st.session_state.brands = ["Unilever"]
                st.session_state.selected_brand = "Unilever"

            st.rerun()


@st.dialog("Log out")
def logout():
    st.write("Tem certeza que deseja sair da aplicação?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Sair", use_container_width=True):
            st.logout()


def login_screen():
    st.image(str(logo_path), use_container_width=True)
    st.header("Olá, tudo bem?")
    st.subheader("Por favor, faça seu login para acessar a dashboard.")
    st.button("Login", on_click=st.login)


def dashboard():

    initialize_session()

    with st.sidebar:

        st.caption("Veja os números do universo Tenda com as marcas!")

        st.button("Universo")
        st.divider()

        st.title("Selecione a marca")

        st.selectbox(
            "Marca",
            st.session_state.brands,
            key="selected_brand"
        )

        if st.button("Adicionar"):
            add_brand()

        if st.button("Excluir"):
            delete_brand()

        st.divider()

        if st.button("Log out"):
            logout()

    st.image(str(logo_path), use_container_width=True)
    st.title("TENDA - MENSURAÇÃO DE CAMPANHAS")
    st.subheader(f"Bem vindo(a), {st.user.name}!")

    upload = st.file_uploader(
        "Faça o upload de arquivo",
        type=["xlsx"]
    )

    if upload is not None:
        with st.spinner("Loading..."):
            time.sleep(2)

        st.success("Dados obtidos com sucesso!")

        df_1 = load_data_resultados(upload)
        df_recomposicao = load_data_recomposicao(upload)

        st.dataframe(
            df_1,
            use_container_width=True,
            hide_index=True
        )

        tab1, tab2, tab3 = st.tabs(
            ["Visão Geral", "Séries Históricas", "Composições"]
        )

        with tab1:
            st.header("Valores Agregados")

            total_receita = df_1["Receita"].sum()
            total_clientes = df_1["Clientes"].sum()
            total_disparos = df_1["Disparados"].sum()
            taxa_abertura = (df_1["Aberturas"].sum()*10)
            taxa_clique = (df_1["Cliques"].sum() / (df_1["Aberturas"].sum()*df_1["Disparados"].sum()))

            col1, col2  = st.columns(2)
            col4, col5, col3 = st.columns(3)
            col1.metric("Receita Total", formata_brl(total_receita), border=True)
            col2.metric("Clientes que Compraram", formata_int(total_clientes), border=True)
            col3.metric("Total de Disparos", formata_int(total_disparos), border=True)
            col4.metric("Taxa de Abertura Média", f"{taxa_abertura:.3f}%".replace(".", ","), border=True)
            col5.metric("Taxa de Clique Média", f"{taxa_clique*100:.3f}%".replace(".", ","), border=True)

            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.subheader("Top 10 Campanhas por Receita")
                top10_receita = df_1.nlargest(10, 'Receita')
                fig_receita = px.bar(top10_receita, x="Receita", y="Campanha", orientation="h",
                                     color="Receita", color_continuous_scale=["#EAF0FF", "#183D7A"])
                # Ordena para a maior barra ficar no topo
                fig_receita.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False,
                                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_receita, use_container_width=True)
            

            with col_graf2:
                st.subheader("Funil de Campanhas")
                funnel_data = dict(
                    Etapas=["Disparados", "Entregues", "Aberturas","Cliques"],
                    Valores=[
                        df_1["Disparados"].sum(),
                        df_1["Entregues"].sum(),
                        (df_1["Aberturas"].sum()/10)*df_1["Entregues"].sum(),
                        df_1["Cliques"].sum()
                    ]
                )
                fig_funil = go.Figure(go.Funnel(
                    y=funnel_data["Etapas"],
                    x=funnel_data["Valores"],
                    textinfo="value+percent initial"
                ))
                fig_funil.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color="#122033"))
                st.plotly_chart(fig_funil, use_container_width=True)

        with tab2:
            st.header("Acompanhe as métricas por tempo!")
        
        with tab3:

            st.header("Entenda a composição!")
            st.caption(
                "Analise como receita e desconto se distribuem entre "
                "categorias e compradores."
            )

            categorias = df_recomposicao["Categoria"].tolist()
            categorias_selecionadas = st.multiselect(
                "Filtre as categorias",
                options=categorias,
                default=categorias,
                key="categorias_recomposicao",
            )

            if not categorias_selecionadas:
                st.info("Selecione ao menos uma categoria para visualizar os dados.")
            else:
                df_comp = df_recomposicao[
                    df_recomposicao["Categoria"].isin(
                        categorias_selecionadas
                    )
                ].copy()

                receita_total_comp = df_comp["Receita"].sum()
                desconto_total_comp = df_comp["Desconto"].sum()
                taxa_desconto_ponderada = (
                    desconto_total_comp / receita_total_comp
                    if receita_total_comp
                    else 0
                )

                indice_lider = df_comp["Receita"].idxmax()
                categoria_lider = df_comp.loc[indice_lider, "Categoria"]
                receita_lider = df_comp.loc[indice_lider, "Receita"]

                kpi1, kpi2 = st.columns(2)
                kpi1.metric(
                    "Receita",
                    formata_brl(receita_total_comp),
                    border=True,
                )
                kpi2.metric(
                    "Desconto",
                    formata_brl(desconto_total_comp),
                    border=True
                )

                kpi3, kpi4 = st.columns(2)
                kpi3.metric(
                    "Taxa de desconto",
                    (
                        f"{taxa_desconto_ponderada * 100:.2f}%"
                        .replace(".", ",")
                    ),
                    border=True
                )
                kpi4.metric(
                    "Categoria líder",
                    categoria_lider,
                    formata_brl(receita_lider),
                    delta_color="green",
                )
            st.divider()

            st.header("Composição da receita")

            # O treemap ocupa toda a largura da página. O comprador
            # continua disponível no hover, enquanto cada categoria
            # recebe o máximo de área possível para exibir seu valor.
            df_treemap = df_comp.copy()
            df_treemap["Receita formatada"] = (
                df_treemap["Receita"].apply(formata_brl)
            )
            df_treemap["Desconto formatado"] = (
                df_treemap["Desconto"].apply(formata_brl)
            )
            df_treemap["Taxa formatada"] = (
                df_treemap["Taxa de Desconto"]
                .mul(100)
                .map(lambda valor: f"{valor:.2f}%".replace(".", ","))
            )
            df_treemap["Participação formatada"] = (
                df_treemap["Participação na Receita"]
                .mul(100)
                .map(lambda valor: f"{valor:.2f}%".replace(".", ","))
            )

            fig_composicao = px.treemap(
                df_treemap,
                path=["Categoria"],
                values="Receita",
                color="Receita",
                color_continuous_scale=[
                    "#EAF0FF",
                    "#6D8EC5",
                    "#183D7A",
                ],
                custom_data=[
                    "Comprador",
                    "Receita formatada",
                    "Desconto formatado",
                    "Taxa formatada",
                    "Participação formatada",
                ],
            )
            fig_composicao.update_traces(
                texttemplate=(
                    "<b>%{label}</b><br>"
                    "%{customdata[1]}"
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Comprador: %{customdata[0]}<br>"
                    "Receita: %{customdata[1]}<br>"
                    "Desconto: %{customdata[2]}<br>"
                    "Taxa de desconto: %{customdata[3]}<br>"
                    "Participação: %{customdata[4]}"
                    "<extra></extra>"
                ),
                marker={
                    "line": {
                        "width": 3,
                        "color": "white",
                    }
                },
                tiling={"pad": 3},
            )
            fig_composicao.update_layout(
                height=675,
                margin={"t": 10, "l": 10, "r": 10, "b": 10},
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                uniformtext_minsize=10,
                uniformtext_mode="show",
            )
            st.plotly_chart(
                fig_composicao,
                use_container_width=True,
            )

            st.divider() ###############################################################################################

            st.subheader("Taxa de desconto por categoria")

            df_taxa = df_comp.sort_values(
                "Taxa de Desconto",
                ascending=True,
            )
            fig_taxa = px.bar(
                df_taxa,
                x="Taxa de Desconto",
                y="Categoria",
                orientation="h",
                color="Taxa de Desconto",
                color_continuous_scale=[
                    "#EAF0FF",
                    "#183D7A",
                ],
            )
            fig_taxa.update_traces(
                texttemplate="%{x:.2%}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Taxa de desconto: %{x:.2%}"
                    "<extra></extra>"
                ),
            )
            fig_taxa.update_xaxes(
                tickformat=".1%",
                title=None,
            )
            fig_taxa.update_yaxes(title=None)
            fig_taxa.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin={"t": 10, "l": 10, "r": 45, "b": 10},
            )
            st.plotly_chart(
                fig_taxa,
                use_container_width=True,
            )

            st.subheader("Detalhamento da recomposição")

            tabela_composicao = df_comp[
                [
                    "Categoria",
                    "Comprador",
                    "Contato",
                    "Receita",
                    "Desconto",
                    "Taxa de Desconto",
                    "Participação na Receita",
                ]
            ].copy()

            st.dataframe(
                tabela_composicao,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Receita": st.column_config.NumberColumn(
                        "Receita",
                        format="R$ %.2f",
                    ),
                    "Desconto": st.column_config.NumberColumn(
                        "Desconto",
                        format="R$ %.2f",
                    ),
                    "Taxa de Desconto": st.column_config.NumberColumn(
                        "Taxa de desconto",
                        format="percent",
                    ),
                    "Participação na Receita": (
                        st.column_config.NumberColumn(
                            "Participação na receita",
                            format="percent",
                        )
                    ),
                },
            )
import time
from pathlib import Path

import streamlit as st

from data_loader import load_data

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

        df = load_data(upload)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        tab1, tab2 = st.tabs(
            ["Visão Geral", "Séries Históricas"]
        )

        with tab1:
            st.header("Valores Agregados")

        with tab2:
            st.header("Acompanhe as métricas por tempo!")
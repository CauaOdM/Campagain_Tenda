import re
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import openpyxl
import time

from data_loader import load_data

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
logo_path = PROJECT_ROOT / "assets" / "LINKEDIN - CAPA.png"

def login_screen():
    st.image(str(logo_path), use_container_width=True)
    st.header("Olá, tudo bem?")
    st.subheader("Por favor, faça seu login para acessar a dashboard.")
    st.button("Login", on_click=st.login)

is_logged_in = getattr(st.user, "is_logged_in", False)

if not is_logged_in:
    login_screen()
else:
    st.image(str(logo_path), use_container_width=True)
    st.title('TENDA - MENSURAÇÃO DE CAMPANHAS')
    st.subheader(f"Bem vindo(a), {st.user.name}!")
    #input de arquivo que vai para o banco de dados
    upload = st.file_uploader("Faça o upload de arquivo", type=["xlsx"])
    if upload is not None:
        data_load_state = st.text('Loading data...')
        time.sleep(1.75)
        st.success('Dados obtidos com sucesso!')
        df = load_data(upload)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.button("Log out", on_click=st.logout)
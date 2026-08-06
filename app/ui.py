from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import formata_brl, formata_int
from repository import (
    create_brand,
    delete_brand as delete_brand_record,
    list_brand_months,
    list_brands,
    load_dashboard_data,
    sync_workbook,
)


st.set_page_config(
    page_title="Tenda CRM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

TENDA_COLORS = {
    "azul": "#1c3c6c",
    "vermelho": "#ec2c24",
    "cinza_claro": "#d1c4cc",
    "azul_cinza": "#7c84a4",
    "cinza_azulado": "#8c8cac",
}

st.markdown(
    f"""
    <style>
        :root {{
            --tenda-blue: {TENDA_COLORS["azul"]};
            --tenda-red: {TENDA_COLORS["vermelho"]};
            --tenda-light-gray: {TENDA_COLORS["cinza_claro"]};
            --tenda-blue-gray: {TENDA_COLORS["azul_cinza"]};
            --tenda-gray-blue: {TENDA_COLORS["cinza_azulado"]};

            --surface: #ffffff;
            --surface-soft: #f8f9fb;
            --page: #f2f4f7;
            --text: #24324a;
            --text-muted: #667085;
            --border: rgba(28, 60, 108, 0.14);
            --shadow: 0 6px 20px rgba(28, 60, 108, 0.07);
            --shadow-hover: 0 10px 28px rgba(28, 60, 108, 0.11);
            --radius: 14px;
        }}

        /* Estrutura geral */
        html,
        body,
        [class*="css"] {{
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(
                    180deg,
                    rgba(28, 60, 108, 0.035) 0,
                    transparent 240px
                ),
                var(--page);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: rgba(242, 244, 247, 0.94);
            border-bottom: 1px solid rgba(28, 60, 108, 0.08);
            backdrop-filter: blur(10px);
        }}

        [data-testid="stMainBlockContainer"] {{
            width: 100%;
            max-width: 1480px;
            padding-top: 1.75rem;
            padding-right: clamp(1rem, 2.4vw, 2.5rem);
            padding-bottom: 4rem;
            padding-left: clamp(1rem, 2.4vw, 2.5rem);
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                var(--tenda-blue) 0%,
                #162f56 100%
            );
            border-right: 3px solid var(--tenda-red);
            box-shadow: 6px 0 24px rgba(28, 60, 108, 0.10);
        }}

        [data-testid="stSidebar"] > div {{
            padding-top: 1.25rem;
            padding-right: 1rem;
            padding-left: 1rem;
        }}

        [data-testid="stSidebar"] * {{
            color: #ffffff;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: #ffffff;
            letter-spacing: -0.01em;
        }}

        [data-testid="stSidebar"] h1 {{
            margin-bottom: 0.85rem;
            padding-bottom: 0;
            border-bottom: 0;
            font-size: 1.35rem;
        }}

        [data-testid="stSidebar"] h1::after {{
            display: none;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255, 255, 255, 0.18);
            margin: 1.25rem 0;
        }}

        [data-testid="stSidebar"] label {{
            font-size: 0.82rem;
            font-weight: 650;
            letter-spacing: 0.01em;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 8px;
            box-shadow: none;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
        [data-testid="stSidebar"] [data-baseweb="input"] > div:hover {{
            border-color: rgba(255, 255, 255, 0.55);
        }}

        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] [data-testid="stButton"] > button,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
        [data-testid="stSidebar"] button[data-testid="stBaseButton-tertiary"] {{
            width: 100%;
            min-height: 42px;
            background: rgba(255, 255, 255, 0.09) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.32) !important;
            border-radius: 8px;
            font-weight: 650;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] [data-testid="stButton"] > button p,
        [data-testid="stSidebar"] [data-testid="stButton"] > button span,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] p,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] span,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] span,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-tertiary"] p,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-tertiary"] span {{
            color: #ffffff !important;
        }}

        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] [data-testid="stButton"] > button:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-tertiary"]:hover {{
            background: var(--tenda-red) !important;
            border-color: var(--tenda-red) !important;
            color: #ffffff !important;
        }}

        [data-testid="stSidebar"] .stButton > button:focus-visible,
        [data-testid="stSidebar"] [data-testid="stButton"] > button:focus-visible,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:focus-visible,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:focus-visible,
        [data-testid="stSidebar"] button[data-testid="stBaseButton-tertiary"]:focus-visible {{
            outline: 3px solid rgba(255, 255, 255, 0.34);
            outline-offset: 2px;
        }}

        /* Hierarquia tipográfica */
        h1,
        h2,
        h3,
        h4 {{
            color: var(--tenda-blue);
            letter-spacing: -0.025em;
        }}

        h1 {{
            position: relative;
            margin-bottom: 1.35rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid rgba(28, 60, 108, 0.14);
            font-size: clamp(1.85rem, 3vw, 2.75rem);
            font-weight: 750;
            line-height: 1.12;
        }}

        h1::after {{
            content: "";
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 76px;
            height: 4px;
            background: var(--tenda-red);
            border-radius: 2px;
        }}

        h2 {{
            margin-top: 1.5rem;
            font-size: clamp(1.3rem, 2vw, 1.65rem);
            font-weight: 720;
        }}

        h3 {{
            font-size: 1.12rem;
            font-weight: 700;
        }}

        p {{
            color: var(--text);
            line-height: 1.6;
        }}

        /* Cards de métricas */
        [data-testid="stMetric"] {{
            position: relative;
            min-height: 142px;
            padding: 1.2rem 1.25rem 1rem;
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            transition:
                transform 160ms ease,
                box-shadow 160ms ease,
                border-color 160ms ease;
        }}

        [data-testid="stMetric"]::before {{
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(
                90deg,
                var(--tenda-blue) 0%,
                var(--tenda-blue) 78%,
                var(--tenda-red) 78%,
                var(--tenda-red) 100%
            );
        }}

        [data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            border-color: rgba(28, 60, 108, 0.24);
            box-shadow: var(--shadow-hover);
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--text-muted);
            font-size: clamp(0.72rem, 0.85vw, 0.8rem);
            font-weight: 700;
            letter-spacing: 0.045em;
            line-height: 1.35;
            text-transform: uppercase;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--tenda-blue);
            font-size: clamp(1.45rem, 2.15vw, 1.95rem);
            font-weight: 750;
            letter-spacing: -0.035em;
            line-height: 1.1;
            white-space: nowrap;
        }}

        [data-testid="stMetricDelta"] {{
            color: var(--tenda-gray-blue);
            font-size: 0.78rem;
            font-weight: 600;
        }}

        /* Grade principal de KPIs: mantém proporções e alinhamento em qualquer tela. */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1.15rem 0 1.9rem;
        }}

        .kpi-card {{
            position: relative;
            display: flex;
            min-width: 0;
            min-height: 154px;
            flex-direction: column;
            padding: 1.2rem 1.15rem 1rem;
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }}

        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--tenda-blue) 0 78%, var(--tenda-red) 78% 100%);
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(28, 60, 108, 0.24);
            box-shadow: var(--shadow-hover);
        }}

        .kpi-label {{
            min-height: 2.55em;
            color: var(--text-muted);
            font-size: clamp(0.69rem, 0.82vw, 0.78rem);
            font-weight: 750;
            letter-spacing: 0.04em;
            line-height: 1.3;
            text-transform: uppercase;
        }}

        .kpi-value {{
            margin-top: 0.45rem;
            overflow: hidden;
            color: var(--tenda-blue);
            font-size: clamp(1.25rem, 1.65vw, 1.75rem);
            font-weight: 780;
            letter-spacing: -0.04em;
            line-height: 1.1;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .kpi-detail {{
            align-self: flex-start;
            margin-top: auto;
            padding-top: 0.75rem;
            color: var(--text-muted);
            font-size: 0.76rem;
            font-weight: 650;
            line-height: 1.25;
        }}

        .kpi-detail.positive,
        .kpi-detail.warning {{
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
        }}

        .kpi-detail.positive {{
            background: #e7f6ec;
            color: #187b43;
        }}

        .kpi-detail.warning {{
            background: #fff3df;
            color: #9a5b00;
        }}

        /* Cabeçalho compacto do dashboard. */
        .dashboard-intro {{
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1.5rem;
            margin: 0.65rem 0 0;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }}

        .dashboard-intro h1 {{
            margin: 0.22rem 0 0.35rem;
            padding: 0;
            border: 0;
            font-size: clamp(1.8rem, 3vw, 2.7rem);
        }}

        .dashboard-intro h1::after {{
            display: none;
        }}

        .dashboard-intro p {{
            margin: 0;
            color: var(--text-muted);
            font-size: 0.94rem;
            line-height: 1.45;
        }}

        .dashboard-eyebrow {{
            color: var(--tenda-red);
            font-size: 0.73rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }}

        .period-chip {{
            display: flex;
            min-width: 175px;
            flex-direction: column;
            flex: 0 0 auto;
            padding: 0.7rem 0.9rem;
            background: rgba(28, 60, 108, 0.06);
            border: 1px solid rgba(28, 60, 108, 0.11);
            border-radius: 10px;
            text-align: right;
        }}

        .period-chip span {{
            color: var(--text-muted);
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .period-chip strong {{
            margin-top: 0.12rem;
            color: var(--tenda-blue);
            font-size: 0.96rem;
        }}

        /* Containers e cards de conteúdo */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--surface);
            border: 1px solid var(--border) !important;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }}

        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding: 0.9rem 1rem 0.75rem;
        }}

        /* Gráficos */
        [data-testid="stPlotlyChart"],
        [data-testid="stVegaLiteChart"] {{
            overflow: hidden;
            background: var(--surface);
            border: 0;
            border-radius: 8px;
            box-shadow: none;
        }}

        /* Tabelas */
        [data-testid="stDataFrame"] {{
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }}

        [data-testid="stDataFrame"] [role="columnheader"] {{
            background: rgba(28, 60, 108, 0.07);
            color: var(--tenda-blue);
            font-weight: 700;
        }}

        /* Abas */
        [data-baseweb="tab-list"] {{
            gap: 0.35rem;
            border-bottom: 1px solid var(--border);
        }}

        [data-baseweb="tab"] {{
            min-height: 44px;
            padding-right: 1rem;
            padding-left: 1rem;
            color: var(--text-muted);
            font-weight: 650;
        }}

        [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--tenda-blue);
        }}

        [data-baseweb="tab-highlight"] {{
            height: 3px;
            background-color: var(--tenda-red);
        }}

        /* Expanders */
        [data-testid="stExpander"] {{
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 9px;
            box-shadow: 0 2px 10px rgba(28, 60, 108, 0.05);
        }}

        [data-testid="stExpander"] summary {{
            color: var(--tenda-blue);
            font-weight: 700;
        }}

        /* Botões */
        .stButton > button,
        .stDownloadButton > button {{
            min-height: 40px;
            padding: 0.45rem 1.05rem;
            border: 1px solid var(--tenda-blue);
            border-radius: 8px;
            background: #ffffff;
            color: var(--tenda-blue);
            font-weight: 700;
            transition:
                background 150ms ease,
                color 150ms ease,
                border-color 150ms ease,
                box-shadow 150ms ease;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            background: var(--tenda-blue);
            border-color: var(--tenda-blue);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(28, 60, 108, 0.16);
        }}

        .stButton > button[kind="primary"] {{
            background: var(--tenda-blue);
            color: #ffffff;
        }}

        .stButton > button[kind="primary"]:hover {{
            background: var(--tenda-red);
            border-color: var(--tenda-red);
        }}

        /* Campos de formulário */
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-baseweb="textarea"] {{
            border-color: var(--border);
            border-radius: 8px;
            background: var(--surface);
        }}

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="select"] > div:focus-within,
        [data-baseweb="textarea"]:focus-within {{
            border-color: var(--tenda-blue);
            box-shadow: 0 0 0 2px rgba(28, 60, 108, 0.10);
        }}

        /* Mensagens e avisos */
        [data-testid="stAlert"] {{
            border: 1px solid rgba(28, 60, 108, 0.14);
            border-left: 4px solid var(--tenda-blue);
            border-radius: 8px;
            box-shadow: none;
        }}

        /* Textos auxiliares */
        [data-testid="stCaptionContainer"],
        .stCaption {{
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        hr {{
            border: 0;
            border-top: 1px solid rgba(28, 60, 108, 0.12);
            margin: 1.8rem 0;
        }}

        div[data-testid="stImage"] img {{
            width: 100%;
            max-height: 176px;
            border: 1px solid rgba(28, 60, 108, 0.10);
            border-radius: var(--radius);
            object-fit: cover;
            object-position: center;
        }}

        /* Responsividade */
        @media (max-width: 1500px) {{
            .kpi-grid {{
                grid-template-columns: repeat(6, minmax(0, 1fr));
            }}

            .kpi-card {{
                grid-column: span 2;
            }}

            .kpi-card:nth-child(4) {{
                grid-column: 2 / span 2;
            }}
        }}

        @media (max-width: 900px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-top: 1.25rem;
                padding-right: 1rem;
                padding-left: 1rem;
            }}

            [data-testid="stMetric"] {{
                min-height: 116px;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 1.55rem;
            }}

            .dashboard-intro {{
                align-items: flex-start;
                flex-direction: column;
                gap: 0.8rem;
            }}

            .period-chip {{
                min-width: 0;
                width: 100%;
                text-align: left;
            }}

            .kpi-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .kpi-card,
            .kpi-card:nth-child(4) {{
                grid-column: auto;
            }}
        }}

        @media (max-width: 560px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}

            .kpi-card {{
                min-height: 132px;
            }}

            .kpi-label {{
                min-height: auto;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
logo_path = PROJECT_ROOT / "assets" / "LINKEDIN - CAPA.png"


def _style_figure(fig, height):
    fig.update_layout(
        height=height,
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font={"color": TENDA_COLORS["azul"], "family": "Inter, Segoe UI, Arial, sans-serif", "size": 12},
        legend_title_text="",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.04, "xanchor": "right", "x": 1},
        margin={"t": 40, "l": 32, "r": 24, "b": 44},
        hoverlabel={"bgcolor": "#ffffff", "font_color": TENDA_COLORS["azul"]},
    )
    fig.update_xaxes(
        automargin=True,
        showgrid=False,
        linecolor=TENDA_COLORS["cinza_claro"],
        tickfont={"color": TENDA_COLORS["azul_cinza"]},
    )
    fig.update_yaxes(
        automargin=True,
        gridcolor="rgba(209, 196, 204, 0.42)",
        zeroline=False,
        tickfont={"color": TENDA_COLORS["azul_cinza"]},
    )
    return fig


def initialize_session():
    if "brands" not in st.session_state:
        st.session_state.brands = list_brands()

    if "selected_brand" not in st.session_state:
        st.session_state.selected_brand = st.session_state.brands[0]

    if "selected_safra_end" not in st.session_state:
        st.session_state.selected_safra_end = None


@st.dialog("Nova Marca")
def add_brand():
    brand_name = st.text_input("Nome da marca")

    if st.button("Salvar"):
        if brand_name.strip() and create_brand(brand_name):
            st.session_state.brands = list_brands()
            st.session_state.selected_brand = brand_name.strip()
            st.session_state.selected_safra_end = None
            st.rerun()


@st.dialog("Excluir")
def delete_brand():
    st.write(f"Deseja realmente excluir a marca **{st.session_state.selected_brand}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancelar"):
            st.rerun()

    with col2:
        if st.button("Excluir"):
            delete_brand_record(st.session_state.selected_brand)
            st.session_state.brands = list_brands()
            st.session_state.selected_brand = st.session_state.brands[0]
            st.session_state.selected_safra_end = None
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


def _comparison_delta(value, reference):
    if reference in (0, 0.0):
        return None
    return (value / reference) - 1


def _status_label(roi):
    if roi >= 8:
        return "Superada"
    if roi >= 4:
        return "No Alvo"
    return "Atenção"


def _status_tone(roi):
    if roi >= 8:
        return "positive"
    if roi < 4:
        return "warning"
    return "neutral"


def _metric_card(label, value, detail=None, tone="neutral"):
    detail_html = ""
    if detail:
        detail_html = f'<div class="kpi-detail {escape(tone)}">{escape(detail)}</div>'

    return (
        '<article class="kpi-card">'
        f'<div class="kpi-label">{escape(label)}</div>'
        f'<div class="kpi-value" title="{escape(value)}">{escape(value)}</div>'
        f'{detail_html}'
        '</article>'
    )


def _render_metric_grid(cards):
    cards_html = "".join(_metric_card(**card) for card in cards)
    st.html(f'<section class="kpi-grid">{cards_html}</section>')


def _safe_month_options(brand_name):
    month_options = [month.strftime("%m/%Y") for month in list_brand_months(brand_name)]
    if not month_options:
        month_options = [pd.Timestamp.today().strftime("%m/%Y")]
    if st.session_state.selected_safra_end not in month_options:
        st.session_state.selected_safra_end = month_options[0]
    return month_options


def dashboard():
    initialize_session()

    with st.sidebar:
        st.caption("Veja os números do universo Tenda com as marcas!")
        st.button("Visão Geral", use_container_width=True)
        st.divider()

        st.title("Selecione a marca")
        st.selectbox("Marca", st.session_state.brands, key="selected_brand")

        month_options = _safe_month_options(st.session_state.selected_brand)
        st.selectbox("Safra (mês final dos últimos 12 meses)", month_options, key="selected_safra_end")

        upload = st.file_uploader("Faça o upload de arquivo", type=["xlsx"], key="upload_xlsx")
        if st.button("Atualizar banco com este arquivo", use_container_width=True):
            if upload is None:
                st.warning("Selecione um arquivo XLSX antes de sincronizar.")
            else:
                with st.spinner("Gravando dados no banco..."):
                    sync_workbook(upload, st.session_state.selected_brand)
                st.success("Upload sincronizado com o banco.")
                st.rerun()

        st.divider()

        if st.button("Adicionar", use_container_width=True):
            add_brand()

        if st.button("Excluir", use_container_width=True):
            delete_brand()

        if st.button("Log out", use_container_width=True):
            logout()

    selected_safra_end = pd.to_datetime(st.session_state.selected_safra_end, format="%m/%Y").date().replace(day=1)

    payload = load_dashboard_data(
        brand_name=st.session_state.selected_brand,
        safra_end_month=selected_safra_end,
    )
    brand_df = payload["df_resultados"]
    brand_comp = payload["df_composicao"]
    geral_df = payload["df_resultados_geral"]
    geral_comp = payload["df_composicao_geral"]
    serie_brand = payload["serie_mensal"]
    serie_geral = payload["serie_mensal_geral"]
    safra_start = payload["safra_start"]
    safra_end = payload["safra_end"]
    metrics = payload["metrics"]

    if safra_start and safra_end:
        caption_period = f"{pd.Timestamp(safra_start).strftime('%m/%Y')} - {pd.Timestamp(safra_end).strftime('%m/%Y')}"
    else:
        caption_period = "Sem período disponível"

    display_name = str(getattr(st.user, "name", None) or "usuário")
    brand_name = st.session_state.selected_brand.upper()

    st.image(str(logo_path), use_container_width=True)
    st.html(
        f"""
        <section class="dashboard-intro">
            <div>
                <span class="dashboard-eyebrow">Painel de CRM · Visão executiva</span>
                <h1>TENDA — {escape(brand_name)}</h1>
                <p>Bem-vindo(a), {escape(display_name)}. Acompanhe o desempenho consolidado das campanhas.</p>
            </div>
            <div class="period-chip">
                <span>Safra 12 meses</span>
                <strong>{escape(caption_period)}</strong>
            </div>
        </section>
        """,
    )

    if brand_df.empty:
        st.info("Nenhum dado encontrado ainda. Faça upload de um XLSX para popular esta marca.")
        return

    geral_receita = float(geral_df["Receita"].sum()) if not geral_df.empty else 0.0
    geral_desconto = float(geral_df["Desconto"].sum()) if not geral_df.empty else 0.0
    geral_clientes = int(geral_df["Clientes"].sum()) if not geral_df.empty else 0
    geral_disparados = int(geral_df["Disparados"].sum()) if not geral_df.empty else 0

    _render_metric_grid(
        [
            {
                "label": "Receita Total CRM",
                "value": formata_brl(metrics["receita_total"]),
                "detail": None
                if not geral_receita
                else f"vs. geral {_comparison_delta(metrics['receita_total'], geral_receita):+.1%}",
            },
            {
                "label": "ROI Global do Desconto",
                "value": f"{metrics['roi']:.2f}x",
                "detail": _status_label(metrics["roi"]),
                "tone": _status_tone(metrics["roi"]),
            },
            {
                "label": "Share Médio no Faturamento",
                "value": f"{metrics['share_faturamento'] * 100:.2f}%".replace(".", ","),
                "detail": None if not geral_receita else f"Geral {formata_brl(geral_receita)}",
            },
            {
                "label": "Investimento Concedido",
                "value": formata_brl(metrics["desconto_total"]),
                "detail": None
                if not geral_desconto
                else f"vs. geral {_comparison_delta(metrics['desconto_total'], geral_desconto):+.1%}",
            },
            {
                "label": "Base Única Impactada",
                "value": formata_int(metrics["base_unica"]),
                "detail": None
                if not geral_clientes
                else f"vs. geral {_comparison_delta(metrics['base_unica'], geral_clientes):+.1%}",
            },
        ]
    )

    col_graf1, col_graf2 = st.columns(2, gap="large")
    with col_graf1:
        with st.container(border=True):
            st.subheader("Evolução Mensal da Marca")
            if serie_brand.empty:
                st.info("Sem série histórica para esta marca e safra.")
            else:
                serie_plot = serie_brand.copy()
                serie_plot["report_month"] = pd.to_datetime(serie_plot["report_month"])
                fig_series = px.line(
                    serie_plot,
                    x="report_month",
                    y=["Receita", "Desconto"],
                    markers=True,
                    color_discrete_sequence=[TENDA_COLORS["azul"], TENDA_COLORS["vermelho"]],
                )
                st.plotly_chart(_style_figure(fig_series, 340), use_container_width=True)

    with col_graf2:
        with st.container(border=True):
            st.subheader("Comparação com o Geral Tenda")
            comparativo = pd.DataFrame(
                {
                    "Escopo": ["Marca", "Geral"],
                    "Receita": [metrics["receita_total"], geral_receita],
                    "Desconto": [metrics["desconto_total"], geral_desconto],
                }
            )
            fig_comp = px.bar(
                comparativo,
                x="Escopo",
                y=["Receita", "Desconto"],
                barmode="group",
                color_discrete_sequence=[TENDA_COLORS["azul"], TENDA_COLORS["vermelho"]],
            )
            st.plotly_chart(_style_figure(fig_comp, 340), use_container_width=True)

    col_graf3, col_graf4 = st.columns(2, gap="large")
    with col_graf3:
        with st.container(border=True):
            st.subheader("Receita e Verba por Campanha")
            df_plot = brand_df.nlargest(min(10, len(brand_df)), "Receita").copy()
            fig_receita = px.bar(
                df_plot,
                x="Campanha",
                y=["Receita", "Desconto"],
                barmode="group",
                color_discrete_sequence=[TENDA_COLORS["azul"], TENDA_COLORS["vermelho"]],
            )
            fig_receita.update_xaxes(tickangle=-24)
            st.plotly_chart(_style_figure(fig_receita, 340), use_container_width=True)

    with col_graf4:
        with st.container(border=True):
            st.subheader("Funil Operacional")
            funnel_data = {
                "Etapas": ["Disparados", "Entregues", "Aberturas", "Cliques"],
                "Valores": [
                    metrics["disparados"],
                    metrics["entregues"],
                    int(metrics["entregues"] * metrics["taxa_abertura"]),
                    int(metrics["disparados"] * metrics["taxa_clique"]),
                ],
            }
            fig_funil = go.Figure(
                go.Funnel(
                    y=funnel_data["Etapas"],
                    x=funnel_data["Valores"],
                    textinfo="value+percent initial",
                    marker={
                        "color": [
                            TENDA_COLORS["azul"],
                            TENDA_COLORS["azul_cinza"],
                            TENDA_COLORS["cinza_azulado"],
                            TENDA_COLORS["vermelho"],
                        ],
                        "line": {"color": "#ffffff", "width": 2},
                    },
                    connector={"line": {"color": TENDA_COLORS["cinza_claro"], "width": 1}},
                )
            )
            styled_funil = _style_figure(fig_funil, 340)
            styled_funil.update_layout(showlegend=False)
            st.plotly_chart(styled_funil, use_container_width=True)

    st.subheader("Performance por Campanha")
    tabela = brand_df.copy()
    tabela["ROI"] = tabela.apply(lambda row: (row["Receita"] / row["Desconto"]) if row["Desconto"] else 0, axis=1)
    tabela["Share"] = tabela["Receita"].div(max(tabela["Receita"].sum(), 1))
    st.dataframe(
        tabela[["Campanha", "Qtd Venda", "Clientes", "Receita", "Desconto", "ROI", "Share"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
            "Desconto": st.column_config.NumberColumn("Desconto", format="R$ %.2f"),
            "ROI": st.column_config.NumberColumn("ROI", format="%.2f x"),
            "Share": st.column_config.NumberColumn("Share", format="percent"),
        },
    )

    if not brand_comp.empty:
        st.divider()
        st.subheader("Recomposição por Categoria")
        categorias = brand_comp["Categoria"].tolist()
        categorias_selecionadas = st.multiselect(
            "Filtre as categorias",
            options=categorias,
            default=categorias[: min(5, len(categorias))],
            key="categorias_recomposicao",
        )

        df_comp = brand_comp[brand_comp["Categoria"].isin(categorias_selecionadas)].copy()
        if not df_comp.empty:
            receita_total_comp = df_comp["Receita"].sum()
            desconto_total_comp = df_comp["Desconto"].sum()
            taxa_desconto_ponderada = desconto_total_comp / receita_total_comp if receita_total_comp else 0
            categoria_lider = df_comp.loc[df_comp["Receita"].idxmax(), "Categoria"]

            col_a, col_b, col_c, col_d = st.columns(4, gap="medium")
            col_a.metric("Receita", formata_brl(receita_total_comp))
            col_b.metric("Desconto", formata_brl(desconto_total_comp))
            col_c.metric("Taxa de desconto", f"{taxa_desconto_ponderada * 100:.2f}%".replace(".", ","))
            col_d.metric("Categoria líder", categoria_lider)

            col_left, col_right = st.columns(2, gap="large")
            with col_left:
                with st.container(border=True):
                    fig_composicao = px.treemap(
                        df_comp,
                        path=["Categoria"],
                        values="Receita",
                        color="Receita",
                        color_continuous_scale=[
                            TENDA_COLORS["cinza_claro"],
                            TENDA_COLORS["azul_cinza"],
                            TENDA_COLORS["azul"],
                        ],
                    )
                    styled_composicao = _style_figure(fig_composicao, 420)
                    styled_composicao.update_layout(margin={"t": 20, "l": 10, "r": 10, "b": 10})
                    st.plotly_chart(styled_composicao, use_container_width=True)

            with col_right:
                with st.container(border=True):
                    df_taxa = df_comp.sort_values("Taxa de Desconto", ascending=True)
                    fig_taxa = px.bar(
                        df_taxa,
                        x="Taxa de Desconto",
                        y="Categoria",
                        orientation="h",
                        color="Taxa de Desconto",
                        color_continuous_scale=[
                            TENDA_COLORS["cinza_claro"],
                            TENDA_COLORS["azul_cinza"],
                            TENDA_COLORS["vermelho"],
                        ],
                    )
                    styled_taxa = _style_figure(fig_taxa, 420)
                    styled_taxa.update_layout(showlegend=False, margin={"t": 20, "l": 10, "r": 45, "b": 20})
                    st.plotly_chart(styled_taxa, use_container_width=True)

            st.dataframe(
                df_comp[["Categoria", "Comprador", "Contato", "Receita", "Desconto", "Taxa de Desconto", "Participação na Receita"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
                    "Desconto": st.column_config.NumberColumn("Desconto", format="R$ %.2f"),
                    "Taxa de Desconto": st.column_config.NumberColumn("Taxa de desconto", format="percent"),
                    "Participação na Receita": st.column_config.NumberColumn("Participação na receita", format="percent"),
                },
            )
import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO

# =================== CORES ===================
SPACE_CADET = "#272846"
HARVEST_GOLD = "#e5a125"
HONEYDEW = "#f0f8ea"
SLATE_GRAY = "#717c89"

# ========== CSS VISUAL PREMIUM ==========
st.markdown(f"""
<style>
    html, body, .stApp, .block-container {{
        background-color: {SPACE_CADET} !important;
    }}
    header, .css-18e3th9, .e1fb0mya2 {{
        background: {SPACE_CADET}!important;
        min-height:0px!important;
        border-bottom: none!important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {SPACE_CADET} !important;
        border-right: 2px solid {HARVEST_GOLD}22 !important;
    }}
    .titulo-header {{
        color: {HONEYDEW};
        font-size: 2.1rem;
        font-weight: 900;
        letter-spacing:0.03em;
        display:flex;
        align-items:center;
        gap:20px;
        border-bottom:2px solid {HARVEST_GOLD}33;
        padding-bottom:0.3rem;
        margin-bottom:23px;
        margin-top:10px;
    }}
    h3, .headline-section {{
        color: {HARVEST_GOLD}!important;
        margin-bottom: 0.39em!important;
        font-size: 1.24rem!important;
    }}
    .table-title {{
        color: {HARVEST_GOLD}; font-size:1.1rem; font-weight:700;
    }}
    .stDataFrame thead tr th {{
        background: {HARVEST_GOLD} !important;
        color: {SPACE_CADET} !important;
        font-weight:800 !important;
        border-bottom:2px solid {HONEYDEW}25 !important;
        font-size:1.09em !important;
    }}
    .stDataFrame tbody tr td {{
        background: {SPACE_CADET} !important;
        color: {HONEYDEW} !important;
        font-size:1em !important;
        border-color: {SLATE_GRAY}30 !important;
    }}
    .stDataFrame {{border:1.5px solid {SLATE_GRAY}!important; border-radius:8px!important;}}
    .captionTABLE {{
        color: {SLATE_GRAY};
        font-size: 0.94em;
        text-align:right;
        margin-top:-0.7em;
        padding-bottom:0.12em;
    }}
    .element-container:has(.stLineChart)>div{{
        max-width: 600px!important;
        margin:1em auto 0 auto!important;
    }}
    .main .block-container {{
        max-width: 100vw!important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== SENHA ==========
def autentica_usuario():
    st.markdown(
        "<h3 style='color:#e5a125;text-align:center'>🔒 Acesso restrito</h3>",
        unsafe_allow_html=True
    )
    senha = st.text_input("Para acessar as posições, digite a senha:", type="password")
    if senha == "jmjp#agi@fu$obeglgct22":
        st.success("Senha correta! Bem-vindo ao painel.")
        return True
    elif senha and senha != "jmjp#agi@fu$obeglgct22":
        st.error("Senha incorreta.")
        st.warning("Se você não tem a senha, contacte o responsável pelo time LIBRA CAPITAL.")
        return False
    else:
        st.info("Digite a senha para acessar o painel.")
        return False

if not autentica_usuario():
    st.stop()

# ========== HEADER: LOGO + TÍTULO ==========
with st.container():
    cols = st.columns([0.095, 0.905])
    with cols[0]:
        st.image("imagens/Capital-branca.png", width=55)
    with cols[1]:
        st.markdown(
            f"""
            <span style='
                color: #f0f8ea;
                font-size: 2.1rem;
                font-weight:900;
                letter-spacing:0.03em;
                border-bottom: 2px solid #e5a12566;
                padding-bottom: 0.12em;
                line-height: 1.14;
                '>
                LIBRA CAPITAL
                <span style='font-weight:400;color:#e5a125;'>| Posição Diária</span>
            </span>
            """,
            unsafe_allow_html=True
        )

st.markdown('<br/>', unsafe_allow_html=True)

# =========== SIDEBAR - FILTROS ============
st.sidebar.title("FILTRAR VISUALIZAÇÃO")
st.sidebar.markdown(f'<hr style="border-color:{HARVEST_GOLD}22;">', unsafe_allow_html=True)

# === Leitura dos dados do Google Sheets ===
GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
url_caixa = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Caixa"
url_cotas = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Cotas"

r_caixa = requests.get(url_caixa)
r_caixa.raise_for_status()
df_caixa = pd.read_csv(StringIO(r_caixa.text))

r_cotas = requests.get(url_cotas)
r_cotas.raise_for_status()
df_cotas = pd.read_csv(StringIO(r_cotas.text))

# ========== DEBUG: VAMOS VER OS DADOS BRUTOS ==========
st.markdown("### 🔍 DEBUG - Dados do Caixa")
st.write("**Colunas disponíveis:**", list(df_caixa.columns))
st.write("**Shape do DataFrame:**", df_caixa.shape)
st.write("**Primeiras 3 linhas:**")
st.dataframe(df_caixa.head(3))

st.markdown("### 🔍 DEBUG - Dados das Cotas")
st.write("**Colunas disponíveis:**", list(df_cotas.columns))
st.write("**Shape do DataFrame:**", df_cotas.shape)
st.write("**Primeiras 3 linhas:**")
st.dataframe(df_cotas.head(3))

df_caixa["Data"] = pd.to_datetime(df_caixa["Data"], dayfirst=True, errors="coerce")
df_cotas["Data"] = pd.to_datetime(df_cotas["Data"], dayfirst=True, errors="coerce")

def date_br(dt):
    if isinstance(dt, (datetime.date, pd.Timestamp)):
        return dt.strftime("%d/%m/%Y")
    return str(dt)

# === DATA DO CAIXA ===
datas_caixa = sorted(df_caixa["Data"].dropna().unique())
default_caixa = max(datas_caixa)
data_caixa_sel = st.sidebar.date_input(
    "Data do Caixa",
    value=default_caixa,
    min_value=min(datas_caixa),
    max_value=default_caixa,
    key="data_caixa",
    format="DD/MM/YYYY"
)

# === DATA DAS COTAS ===
datas_cotas = sorted(df_cotas["Data"].dropna().unique())
default_cotas = max(datas_cotas)
data_cota_sel = st.sidebar.date_input(
    "Data das Cotas",
    value=default_cotas,
    min_value=min(datas_cotas),
    max_value=default_cotas,
    key="data_cotas",
    format="DD/MM/YYYY"
)

# === PERÍODO DO GRÁFICO ===
min_graf, max_graf = min(df_cotas["Data"]), max(df_cotas["Data"])
periodo_graf = st.sidebar.date_input(
    "Período do gráfico das cotas",
    [min_graf, max_graf],
    key="periodo_graf",
    format="DD/MM/YYYY"
)

if not isinstance(periodo_graf, (list, tuple)):
    periodo_graf = [periodo_graf, periodo_graf]

# Converte para datetime se necessário
if hasattr(data_caixa_sel, "to_pydatetime"):
    data_caixa_sel = data_caixa_sel.to_pydatetime()
if hasattr(data_cota_sel, "to_pydatetime"):
    data_cota_sel = data_cota_sel.to_pydatetime()

data_caixa_br = date_br(data_caixa_sel)
data_cota_br = date_br(data_cota_sel)

df_caixa_dia = df_caixa[df_caixa["Data"] == pd.to_datetime(data_caixa_sel)]
df_cotas_dia = df_cotas[df_cotas["Data"] == pd.to_datetime(data_cota_sel)]

st.markdown("### 🔍 DEBUG - Dados Filtrados por Data")
st.write(f"**Data selecionada:** {data_caixa_br}")
st.write(f"**Linhas encontradas para o caixa:** {len(df_caixa_dia)}")
if not df_caixa_dia.empty:
    st.write("**Dados do caixa para a data:**")
    st.dataframe(df_caixa_dia)

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {SLATE_GRAY}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

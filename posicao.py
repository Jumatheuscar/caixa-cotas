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
periodo_graf_br = [date_br(periodo_graf[0]), date_br(periodo_graf[1])]

df_caixa_dia = df_caixa[df_caixa["Data"] == pd.to_datetime(data_caixa_sel)]
df_cotas_dia = df_cotas[df_cotas["Data"] == pd.to_datetime(data_cota_sel)]

# ========== SEÇÃO CAIXA - VOLTANDO À LÓGICA ORIGINAL ==========
st.markdown("<h3>Caixa</h3>", unsafe_allow_html=True)
st.markdown(f"<span class='table-title'>POSIÇÃO DIÁRIA - {data_caixa_br}</span>", unsafe_allow_html=True)

# LISTAS ORIGINAIS
empresas = ["Apuama", "Bristol", "Consignado", "libra sec 40", "libra sec 60", "Tractor"]
contas = [
    "Conta recebimento",
    "Conta de conciliação", 
    "Reserva de caixa",
    "Conta pgto",
    "Disponível para operação"
]

# MATRIZ ORIGINAL
matriz = pd.DataFrame(index=contas, columns=empresas, dtype=float)

# PREENCHIMENTO SIMPLES DA MATRIZ - SEM FILTROS COMPLEXOS
for linha in df_caixa_dia.itertuples():
    empresa = linha.Empresa
    
    # Se a empresa está na nossa lista, preenche os dados
    if empresa in empresas:
        try:
            # Pega os valores DIRETAMENTE da linha (assumindo que as colunas existem)
            # Vou usar os índices das colunas em vez dos nomes
            receb = getattr(linha, '_3', 0) if hasattr(linha, '_3') else 0  # Coluna 3
            conc = getattr(linha, '_4', 0) if hasattr(linha, '_4') else 0   # Coluna 4  
            reserva = getattr(linha, '_5', 0) if hasattr(linha, '_5') else 0 # Coluna 5
            pgto = getattr(linha, '_6', 0) if hasattr(linha, '_6') else 0   # Coluna 6
            
            # Conversão para float
            receb = float(receb) if pd.notna(receb) else 0
            conc = float(conc) if pd.notna(conc) else 0  
            reserva = float(reserva) if pd.notna(reserva) else 0
            pgto = float(pgto) if pd.notna(pgto) else 0
            
            # Cálculo do disponível
            disponivel = pgto - reserva
            
            # Preenche a matriz
            matriz.at["Conta recebimento", empresa] = receb
            matriz.at["Conta de conciliação", empresa] = conc
            matriz.at["Reserva de caixa", empresa] = reserva
            matriz.at["Conta pgto", empresa] = pgto
            matriz.at["Disponível para operação", empresa] = disponivel
            
        except Exception as e:
            # Se der erro, preenche com zero
            matriz.at["Conta recebimento", empresa] = 0
            matriz.at["Conta de conciliação", empresa] = 0
            matriz.at["Reserva de caixa", empresa] = 0
            matriz.at["Conta pgto", empresa] = 0
            matriz.at["Disponível para operação", empresa] = 0

# Preenche com zero onde não tem dados
matriz = matriz.fillna(0)

def brl(x):
    try:
        x_float = float(x)
        return f"R$ {x_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

st.dataframe(
    matriz.applymap(brl),
    use_container_width=False,
    width=940,
    height=210,
)

# ========== SEÇÃO COTAS ==========
st.markdown("<h3>Cotas</h3>", unsafe_allow_html=True)
st.markdown(f"<span class='table-title'>Cotas {data_cota_br}</span>", unsafe_allow_html=True)

def percent_br(x):
    try:
        if pd.isna(x) or x == "" or x is None:
            return ""
        x_float = float(x)
        return f"{x_float:.2%}".replace(".", ",")
    except Exception:
        return ""

tabela_cotas = df_cotas_dia[["Fundo", "Cota mensal", "Cota anual"]].copy()
tabela_cotas = tabela_cotas.dropna(how="all")

tabela_cotas["Cota mensal"] = tabela_cotas["Cota mensal"].apply(percent_br)
tabela_cotas["Cota anual"] = tabela_cotas["Cota anual"].apply(percent_br)

altura_cotas = 62 + max(44, 40*len(tabela_cotas))

st.dataframe(
    tabela_cotas.reset_index(drop=True),
    use_container_width=False,
    width=465,
    height=altura_cotas,
)

st.markdown(f'<div class="captionTABLE">Variação mensal e anual dos fundos - dados oficiais Libra Capital</div>', unsafe_allow_html=True)

# ========== GRÁFICO DA EVOLUÇÃO ==========
st.markdown('<hr style="margin-top:1.2em;margin-bottom:0.2em;">', unsafe_allow_html=True)
st.markdown('<h3>Evolução das cotas mensais dos fundos</h3>', unsafe_allow_html=True)

cols_graph_center, col_graph, cols_graph_right = st.columns([2,4,2])

with col_graph:
    try:
        df_cotas_graf = df_cotas[
            (df_cotas["Data"] >= pd.to_datetime(periodo_graf[0]))
            & (df_cotas["Data"] <= pd.to_datetime(periodo_graf[1]))
        ]
    except Exception as e:
        st.error(f"Erro no período do gráfico ({e})")
        df_cotas_graf = pd.DataFrame()
    
    if not df_cotas_graf.empty:
        graf = df_cotas_graf.pivot(
            index="Data",
            columns="Fundo",
            values="Cota mensal"
        )
        st.line_chart(graf, use_container_width=True, height=255)
    else:
        st.info("Selecione um período válido para exibir o gráfico.")

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {SLATE_GRAY}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

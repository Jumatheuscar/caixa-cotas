import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO

# =================== CORES ===================
SPACE_CADET = "#042F3C"
HARVEST_GOLD = "#C66300"
HONEYDEW = "#FFF4E3"
SLATE_GRAY = "#717c89"

# ========== CSS VISUAL ==========
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
    border-right: 2px solid {HARVEST_GOLD}55 !important;
    color: {HARVEST_GOLD} !important;
}}
[data-testid="stSidebar"] * {{
    color: {HARVEST_GOLD} !important;
}}
    h3 {{
        color: {HARVEST_GOLD}!important;
        font-size: 1.3rem!important;
    }}
    .table-title {{
        color: {HARVEST_GOLD}; font-size:1.2rem; font-weight:700;
    }}
    .stDataFrame thead tr th {{
        background: {HARVEST_GOLD} !important;
        color: {SPACE_CADET} !important;
        font-weight:800 !important;
        font-size:1.1em !important;
    }}
    .stDataFrame tbody tr td {{
        background: {SPACE_CADET} !important;
        color: {HONEYDEW} !important;
        font-size:1em !important;
        border-color: {SLATE_GRAY}30 !important;
    }}
    .stDataFrame {{border:2px solid {SLATE_GRAY}!important; border-radius:10px!important;}}
    .main .block-container {{
        max-width: 100vw!important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÃO PARA CONVERTER VALORES BRASILEIROS ==========
def converter_valor_br(valor):
    if pd.isna(valor) or valor == "" or valor is None:
        return 0.0
    valor_str = str(valor).replace("R$", "").replace(" ", "").strip()
    if valor_str.count('.') == 1 and valor_str.count(',') == 0:
        try:
            return float(valor_str)
        except:
            return 0.0
    if ',' in valor_str:
        partes = valor_str.split(',')
        parte_inteira = partes[0].replace('.', '')
        parte_decimal = partes[1] if len(partes) > 1 else '00'
        valor_str = f"{parte_inteira}.{parte_decimal}"
    else:
        valor_str = valor_str.replace('.', '')
    try:
        return float(valor_str)
    except:
        return 0.0

# ========== SENHA ==========
def autentica_usuario():
    if "senha_ok" not in st.session_state:
        st.session_state["senha_ok"] = False

    if not st.session_state["senha_ok"]:
        st.markdown(
            f"<h3 style='color:{HARVEST_GOLD};text-align:center'>🔒 Acesso restrito</h3>",
            unsafe_allow_html=True
        )
        senha_input = st.text_input("Digite a senha:", type="password")
        if senha_input == "mesaLibra":
            st.session_state["senha_ok"] = True
            st.success("Senha correta! Bem-vindo ao painel.")
            st.rerun()
        elif senha_input:
            st.error("Senha incorreta.")
        st.stop()
    else:
        st.success("Seja bem-vindo ao painel.")

autentica_usuario()

# ========== HEADER ==========
with st.container():
    cols = st.columns([0.095, 0.905])
    with cols[0]:
        # Logo maior
        st.image("imagens/Capital-branca.png", width=220, output_format="PNG")
    with cols[1]:
        st.markdown(
            f"""
            <span style='
                color: {HONEYDEW};
                font-size: 2.4rem;
                font-weight:900;
                border-bottom: 2px solid {HARVEST_GOLD}99;
                padding-bottom: 0.12em;'>
                LIBRA CAPITAL
                <span style='font-weight:400;color:{HARVEST_GOLD};'>| Painel</span>
            </span>
            """,
            unsafe_allow_html=True
        )

st.markdown('<br/>', unsafe_allow_html=True)

# =========== SIDEBAR ============
st.sidebar.title("FILTRAR VISUALIZAÇÃO")
st.sidebar.markdown(f'<hr style="border-color:{HARVEST_GOLD}55;">', unsafe_allow_html=True)

# === Leitura dos dados do Google Sheets ===
GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
url_caixa = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Caixa"
url_apuama = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Dre_Apuama"

r_caixa = requests.get(url_caixa)
r_caixa.raise_for_status()
df_caixa = pd.read_csv(StringIO(r_caixa.text))

r_apuama = requests.get(url_apuama)
r_apuama.raise_for_status()
df_apuama = pd.read_csv(StringIO(r_apuama.text))

df_caixa["Data"] = pd.to_datetime(df_caixa["Data"], dayfirst=True, errors="coerce")

# Tabs principais
aba = st.tabs(["📊 Caixa", "📈 Enquadramento"])

# ========== SEÇÃO CAIXA ==========
with aba[0]:
    # === DATA DO CAIXA ===
    datas_caixa = sorted(df_caixa["Data"].dropna().unique())
    default_caixa = max(datas_caixa)
    data_caixa_sel = st.sidebar.date_input(
        "Data do Caixa",
        value=default_caixa,
        min_value=min(datas_caixa),
        max_value=default_caixa,
        format="DD/MM/YYYY"
    )

    if hasattr(data_caixa_sel, "to_pydatetime"):
        data_caixa_sel = data_caixa_sel.to_pydatetime()

    data_caixa_br = data_caixa_sel.strftime("%d/%m/%Y")
    df_caixa_dia = df_caixa[df_caixa["Data"] == pd.to_datetime(data_caixa_sel)]

    st.markdown("<h3>Caixa</h3>", unsafe_allow_html=True)
    st.markdown(f"<span class='table-title'>POSIÇÃO DIÁRIA - {data_caixa_br}</span>", unsafe_allow_html=True)

    # Empresas sem "libra sec 40" e "libra sec 60"
    empresas = ["Apuama", "Bristol", "Consignado", "Tractor"]
    contas = [
        "Conta recebimento",
        "Conta de conciliação", 
        "Reserva de caixa",
        "Conta pgto",
        "Disponível para operação"
    ]

    matriz = pd.DataFrame(index=contas, columns=empresas, dtype=float)

    for _, linha in df_caixa_dia.iterrows():
        empresa = linha["Empresa"]
        if empresa in empresas:
            conta_receb = converter_valor_br(linha["Conta recebimento"])
            conta_conc = converter_valor_br(linha["Conta de conciliação"])
            reserva = converter_valor_br(linha["Reserva"])
            conta_pgto = converter_valor_br(linha["Conta pgto"])
            disponivel = conta_pgto - reserva

            matriz.at["Conta recebimento", empresa] = conta_receb
            matriz.at["Conta de conciliação", empresa] = conta_conc
            matriz.at["Reserva de caixa", empresa] = reserva
            matriz.at["Conta pgto", empresa] = conta_pgto
            matriz.at["Disponível para operação", empresa] = disponivel

    def brl(x):
        try:
            return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "R$ 0,00"

    # formata valores
    matriz_fmt = matriz.applymap(brl)

    # remove linhas completamente vazias
    matriz_fmt = matriz_fmt.dropna(how="all")

    # coloca a última linha em negrito
    def highlight_last_row(row):
        if row.name == "Disponível para operação":
            return ["font-weight: bold" for _ in row]
        return ["" for _ in row]

    styled = matriz_fmt.style.apply(highlight_last_row, axis=1)

    st.dataframe(
        styled,
        use_container_width=True,
        height=(40 * len(matriz_fmt) + 60)
    )

# ========== SEÇÃO ENQUADRAMENTO ==========
with aba[1]:
    st.markdown("### 📊 Enquadramento Cedentes e Sacados")

    # Corrigir PL TOTAL para número
    df_apuama["PL TOTAL"] = (
        df_apuama["PL TOTAL"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Último PL válido
    pl_valor = df_apuama.dropna(subset=["PL TOTAL"]).iloc[-1]["PL TOTAL"]
    data_pl = df_apuama.dropna(subset=["PL TOTAL"]).iloc[-1]["Data"]

    def brl(x):
        try:
            return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "R$ 0,00"

    st.markdown(f"**PL usado (Apuama - {pd.to_datetime(data_pl).strftime('%d/%m/%Y')}):** {brl(pl_valor)}")

    uploaded_file = st.file_uploader("📂 Enviar planilha de estoque (Excel D-1)", type=["xlsx"])

    if uploaded_file:
        df_estoque = pd.read_excel(uploaded_file)

        # Cedentes
        df_cedentes = (
            df_estoque.groupby(["NOME_CEDENTE", "DOC_CEDENTE"])["VALOR_NOMINAL"]
            .sum()
            .reset_index()
        )
        df_cedentes = df_cedentes.rename(columns={
            "NOME_CEDENTE": "Nome",
            "DOC_CEDENTE": "Documento",
            "VALOR_NOMINAL": "Valor Total"
        })
        df_cedentes["%PL"] = df_cedentes["Valor Total"] / pl_valor * 100
        df_cedentes["Enquadrado"] = df_cedentes["%PL"] <= 10

        df_cedentes["Valor Total"] = df_cedentes["Valor Total"].apply(brl)
        df_cedentes["%PL"] = df_cedentes["%PL"].map(lambda x: f"{x:.2f}%")
        df_cedentes["Enquadrado"] = df_cedentes["Enquadrado"].map(lambda x: "✅ Enquadrado" if x else "❌ Fora")

        st.markdown("#### Cedentes")
        st.dataframe(df_cedentes, use_container_width=True, height=400)

        # Sacados
        df_sacados = (
            df_estoque.groupby(["NOME_SACADO", "DOC_SACADO"])["VALOR_NOMINAL"]
            .sum()
            .reset_index()
        )
        df_sacados = df_sacados.rename(columns={
            "NOME_SACADO": "Nome",
            "DOC_SACADO": "Documento",
            "VALOR_NOMINAL": "Valor Total"
        })
        df_sacados["%PL"] = df_sacados["Valor Total"] / pl_valor * 100
        df_sacados["Enquadrado"] = df_sacados["%PL"] <= 10

        df_sacados["Valor Total"] = df_sacados["Valor Total"].apply(brl)
        df_sacados["%PL"] = df_sacados["%PL"].map(lambda x: f"{x:.2f}%")
        df_sacados["Enquadrado"] = df_sacados["Enquadrado"].map(lambda x: "✅ Enquadrado" if x else "❌ Fora")

        st.markdown("#### Sacados")
        st.dataframe(df_sacados, use_container_width=True, height=400)

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {HONEYDEW}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

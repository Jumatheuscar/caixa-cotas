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

# Função para formatar em BRL
def brl(x):
    try:
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

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
df_caixa = pd.read_csv(StringIO(r_caixa.text))
df_caixa["Data"] = pd.to_datetime(df_caixa["Data"], dayfirst=True, errors="coerce")

r_apuama = requests.get(url_apuama)
df_apuama = pd.read_csv(StringIO(r_apuama.text))
df_apuama["Data"] = pd.to_datetime(df_apuama["Data"], dayfirst=True, errors="coerce")

# ========== TABS ==========
tab1, tab2 = st.tabs(["💰 Caixa", "📊 Enquadramento"])

# --------- TAB 1: CAIXA ---------
with tab1:
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

    empresas = ["Apuama", "Bristol", "Consignado", "Tractor"]
    contas = ["Conta recebimento","Conta de conciliação","Reserva de caixa","Conta pgto","Disponível para operação"]

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

    matriz_fmt = matriz.applymap(brl).dropna(how="all")

    def highlight_last_row(row):
        if row.name == "Disponível para operação":
            return ["font-weight: bold" for _ in row]
        return ["" for _ in row]

    styled = matriz_fmt.style.apply(highlight_last_row, axis=1)

    st.dataframe(styled, use_container_width=True, height=(40 * len(matriz_fmt) + 60))

# --------- TAB 2: ENQUADRAMENTO ---------
with tab2:
    st.markdown("<h3>📊 Enquadramento Cedentes e Sacados</h3>", unsafe_allow_html=True)

    pl_valor = df_apuama.dropna(subset=["PL TOTAL"]).iloc[-1]["PL TOTAL"]
    st.markdown(f"**PL usado (Apuama - {df_apuama.iloc[-1]['Data'].strftime('%d/%m/%Y')}):** {brl(pl_valor)}")

    uploaded_file = st.file_uploader("📂 Enviar planilha de estoque (Excel D-1)", type=["xlsx"])

    if uploaded_file is not None:
        df_estoque = pd.read_excel(uploaded_file, engine="openpyxl")

        # Cedentes
        cedentes = df_estoque.groupby(["NOME_CEDENTE", "DOC_CEDENTE"], as_index=False)["VALOR_NOMINAL"].sum()
        cedentes["%PL"] = (cedentes["VALOR_NOMINAL"] / float(pl_valor)) * 100
        cedentes["Enquadramento"] = cedentes["%PL"].apply(lambda x: "Excedido" if x > 10 else "Enquadrado")

        df_cedentes_fmt = cedentes.rename(columns={
            "NOME_CEDENTE": "Nome","DOC_CEDENTE": "Documento","VALOR_NOMINAL": "Valor Total"})
        df_cedentes_fmt["Valor Total"] = df_cedentes_fmt["Valor Total"].apply(brl)
        df_cedentes_fmt["%PL"] = df_cedentes_fmt["%PL"].apply(lambda x: f"{x:.2f}%")

        # Sacados
        sacados = df_estoque.groupby(["NOME_SACADO", "DOC_SACADO"], as_index=False)["VALOR_NOMINAL"].sum()
        sacados["%PL"] = (sacados["VALOR_NOMINAL"] / float(pl_valor)) * 100
        sacados["Enquadramento"] = sacados["%PL"].apply(lambda x: "Excedido" if x > 10 else "Enquadrado")

        df_sacados_fmt = sacados.rename(columns={
            "NOME_SACADO": "Nome","DOC_SACADO": "Documento","VALOR_NOMINAL": "Valor Total"})
        df_sacados_fmt["Valor Total"] = df_sacados_fmt["Valor Total"].apply(brl)
        df_sacados_fmt["%PL"] = df_sacados_fmt["%PL"].apply(lambda x: f"{x:.2f}%")

        st.markdown("**Cedentes**")
        st.dataframe(df_cedentes_fmt.sort_values("%PL", ascending=False), use_container_width=True, height=(40 * len(df_cedentes_fmt) + 80))

        st.markdown("**Sacados**")
        st.dataframe(df_sacados_fmt.sort_values("%PL", ascending=False), use_container_width=True, height=(40 * len(df_sacados_fmt) + 80))

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {HONEYDEW}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

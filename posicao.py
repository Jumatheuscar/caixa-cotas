import streamlit as st
import pandas as pd
import requests
from io import StringIO

# =================== CORES ===================
SPACE_CADET = "#042F3C"
HARVEST_GOLD = "#C66300"
HONEYDEW = "#FFF4E3"
SLATE_GRAY = "#717c89"
VERDE = "#2ecc71"
VERMELHO = "#e74c3c"

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
    /* Tabs com underline */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 36px;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600;
        padding: 12px 24px;
        border-bottom: 3px solid transparent;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        border-bottom: 3px solid {HARVEST_GOLD};
        color: {HARVEST_GOLD};
    }}
    /* Indicadores */
    .indicador {{
        padding: 12px;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: bold;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÃO BRL ==========
def brl(x):
    try:
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

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
                <span style='font-weight:400;color:{HARVEST_GOLD};'>| Posição Diária</span>
            </span>
            """,
            unsafe_allow_html=True
        )

# ========== ABAS ==========
aba = st.tabs(["💰 Caixa", "📊 Enquadramento"])

# ================= CAIXA =================
with aba[0]:
    st.markdown("<h3>Caixa</h3>", unsafe_allow_html=True)
    # aqui mantém seu código do caixa igualzinho...

# ================= ENQUADRAMENTO =================
with aba[1]:
    st.markdown("<h3>📊 Enquadramento - Cedentes e Sacados (Apuama)</h3>", unsafe_allow_html=True)

    GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
    url_dre_apuama = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Dre_Apuama"
    r_dre = requests.get(url_dre_apuama)
    r_dre.raise_for_status()
    df_dre = pd.read_csv(StringIO(r_dre.text))

    df_dre["Data"] = pd.to_datetime(df_dre["Data"], dayfirst=True, errors="coerce")
    df_dre = df_dre.dropna(subset=["PL TOTAL"])
    pl_apuama = float(str(df_dre.iloc[-1]["PL TOTAL"]).replace(".", "").replace(",", "."))
    
    st.markdown(f"<b>PL usado (Apuama - {df_dre.iloc[-1]['Data'].strftime('%d/%m/%Y')}):</b> {brl(pl_apuama)}", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Envie o arquivo de estoque (Excel)", type=["xlsx"])
    if uploaded_file:
        df_estoque = pd.read_excel(uploaded_file)

        # Substituição condicional
        condicoes = [
            "UY3 SOCIEDADE DE CREDITO DIRETO S/ A",
            "MONEY PLUS SOCIEDADE DE CREDITO AO MICROEMPREENDED",
            "MONEY PLUS SOCIEDADE DE CREDITO AO MICRO"
        ]
        df_estoque["NOME_CEDENTE"] = df_estoque.apply(
            lambda x: x["NOME_SACADO"] if x["NOME_CEDENTE"] in condicoes else x["NOME_CEDENTE"],
            axis=1
        )

        # Cedentes
        df_cedentes = df_estoque.groupby(["NOME_CEDENTE", "DOC_CEDENTE"], as_index=False)["VALOR_NOMINAL"].sum()
        df_cedentes.rename(columns={"NOME_CEDENTE": "Cedente", "DOC_CEDENTE": "CNPJ", "VALOR_NOMINAL": "Valor Total"}, inplace=True)
        df_cedentes["%PL"] = df_cedentes["Valor Total"].astype(float) / pl_apuama * 100
        df_cedentes["Enq."] = df_cedentes["%PL"].apply(lambda x: "✅ Enq." if x <= 10 else "❌ Fora")
        df_cedentes = df_cedentes.sort_values(by="Valor Total", ascending=False)

        # Sacados
        df_sacados = df_estoque.groupby(["NOME_SACADO", "DOC_SACADO"], as_index=False)["VALOR_NOMINAL"].sum()
        df_sacados.rename(columns={"NOME_SACADO": "Sacado", "DOC_SACADO": "CNPJ", "VALOR_NOMINAL": "Valor Total"}, inplace=True)
        df_sacados["%PL"] = df_sacados["Valor Total"].astype(float) / pl_apuama * 100
        df_sacados["Enq."] = df_sacados["%PL"].apply(lambda x: "✅ Enq." if x <= 10 else "❌ Fora")
        df_sacados = df_sacados.sort_values(by="Valor Total", ascending=False)

        # Indicadores
        maior_ced = df_cedentes["%PL"].max()
        top5_ced = df_cedentes["%PL"].nlargest(5).sum()
        maior_sac = df_sacados["%PL"].max()
        top5_sac = df_sacados["%PL"].nlargest(5).sum()

        st.markdown("### 🔎 Indicadores")
        col1, col2, col3, col4 = st.columns(4)

        def indicador_html(label, valor, limite):
            cor = VERDE if valor <= limite else VERMELHO
            return f"<div class='indicador' style='background:{cor}33; color:{cor}'>{label}<br>{valor:.2f}%</div>"

        col1.markdown(indicador_html("Maior Cedente", maior_ced, 10), unsafe_allow_html=True)
        col2.markdown(indicador_html("Top 5 Cedentes", top5_ced, 40), unsafe_allow_html=True)
        col3.markdown(indicador_html("Maior Sacado", maior_sac, 10), unsafe_allow_html=True)
        col4.markdown(indicador_html("Top 5 Sacados", top5_sac, 40), unsafe_allow_html=True)

        # Mostrar tabelas
        st.markdown("### Cedentes")
        st.dataframe(df_cedentes.style.format({"Valor Total": brl, "%PL": "{:.2f}%"}), use_container_width=True)

        st.markdown("### Sacados")
        st.dataframe(df_sacados.style.format({"Valor Total": brl, "%PL": "{:.2f}%"}), use_container_width=True)

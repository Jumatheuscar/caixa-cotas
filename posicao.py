import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO
import os

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
    /* Tabs */
    div[data-baseweb="tab-list"] > div[role="tab"] {{
        border-bottom: 3px solid transparent;
        padding-bottom: 8px;
        font-weight: 600;
    }}
    div[data-baseweb="tab-list"] > div[role="tab"][aria-selected="true"] {{
        border-bottom: 3px solid {HARVEST_GOLD};
        color: {HARVEST_GOLD};
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

st.markdown('<br/>', unsafe_allow_html=True)

# ========== ABAS ==========
aba = st.tabs(["🍯 Caixa", "📊 Enquadramento"])

# ========== ABA CAIXA ==========
with aba[0]:
    st.markdown("<h3>Caixa</h3>", unsafe_allow_html=True)

    GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
    url_caixa = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Caixa"

    r_caixa = requests.get(url_caixa)
    r_caixa.raise_for_status()
    df_caixa = pd.read_csv(StringIO(r_caixa.text))

    df_caixa["Data"] = pd.to_datetime(df_caixa["Data"], dayfirst=True, errors="coerce")

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

    st.markdown(f"<span class='table-title'>POSIÇÃO DIÁRIA - {data_caixa_br}</span>", unsafe_allow_html=True)

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

    matriz_fmt = matriz.applymap(brl)
    matriz_fmt = matriz_fmt.dropna(how="all")

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

# ========== ABA ENQUADRAMENTO ==========
with aba[1]:
    st.markdown("### 📊 Enquadramento - Cedentes e Sacados")

    fundo_sel = st.radio("Selecione o Fundo", ["Apuama", "Bristol"], horizontal=True)

    GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
    sheet_map = {
        "Apuama": "Dre_Apuama",
        "Bristol": "Dre_Bristol"
    }

    # === Persistência do arquivo ===
    hoje = datetime.date.today().strftime("%Y%m%d")
    file_path = f"/tmp/estoque_{fundo_sel}_{hoje}.xlsx"

    if os.path.exists(file_path):
        df_estoque = pd.read_excel(file_path)
        st.info(f"Usando arquivo de estoque já carregado hoje para {fundo_sel}.")
    else:
        uploaded_file = st.file_uploader(f"Envie o arquivo de estoque do {fundo_sel}", type=["xlsx"], key=f"upload_{fundo_sel}")
        if uploaded_file:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            df_estoque = pd.read_excel(file_path)
            st.success(f"Arquivo de estoque salvo e carregado para {fundo_sel}.")
        else:
            st.warning(f"Nenhum arquivo carregado ainda para {fundo_sel}.")
            df_estoque = None

    if df_estoque is not None:
        # Renomear colunas
        df_estoque = df_estoque.rename(columns={
            "NOME_CEDENTE": "Cedente",
            "DOC_CEDENTE": "CNPJ_Cedente",
            "NOME_SACADO": "Sacado",
            "DOC_SACADO": "CNPJ_Sacado",
            "VALOR_NOMINAL": "Valor"
        })

        # Buscar PL do fundo
        url_pl = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_map[fundo_sel]}"
        r_pl = requests.get(url_pl)
        r_pl.raise_for_status()
        df_pl = pd.read_csv(StringIO(r_pl.text))
        df_pl["Data"] = pd.to_datetime(df_pl["Data"], dayfirst=True, errors="coerce")

        data_pl = df_pl["Data"].max()
        pl_valor = converter_valor_br(df_pl.loc[df_pl["Data"] == data_pl, "PL TOTAL"].values[0])

        st.markdown(f"**PL usado ({fundo_sel} - {data_pl.strftime('%d/%m/%Y')}):** R$ {pl_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Cedentes
        df_cedentes = df_estoque.groupby(["Cedente", "CNPJ_Cedente"], as_index=False)["Valor"].sum()
        df_cedentes["%PL"] = df_cedentes["Valor"].astype(float) / float(pl_valor) * 100
        df_cedentes["Enquadrado"] = df_cedentes["%PL"].apply(lambda x: "✅" if x <= 10 else "❌")
        df_cedentes = df_cedentes.sort_values("%PL", ascending=False)

        maior_cedente = df_cedentes.iloc[0]
        top5_cedentes = df_cedentes.head(5)["%PL"].sum()

        st.metric("Maior Cedente", f"{maior_cedente['Cedente']} ({maior_cedente['%PL']:.2f}%)")
        st.metric("Top 5 Cedentes", f"{top5_cedentes:.2f}%")

        df_cedentes["Valor"] = df_cedentes["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df_cedentes["%PL"] = df_cedentes["%PL"].apply(lambda x: f"{x:.2f}%")

        st.markdown("#### Cedentes")
        st.dataframe(df_cedentes, use_container_width=True, height=400)

        # Sacados
        df_sacados = df_estoque.groupby(["Sacado", "CNPJ_Sacado"], as_index=False)["Valor"].sum()
        df_sacados["%PL"] = df_sacados["Valor"].astype(float) / float(pl_valor) * 100
        df_sacados["Enquadrado"] = df_sacados["%PL"].apply(lambda x: "✅" if x <= 10 else "❌")
        df_sacados = df_sacados.sort_values("%PL", ascending=False)

        maior_sacado = df_sacados.iloc[0]
        top5_sacados = df_sacados.head(5)["%PL"].sum()

        st.metric("Maior Sacado", f"{maior_sacado['Sacado']} ({maior_sacado['%PL']:.2f}%)")
        st.metric("Top 5 Sacados", f"{top5_sacados:.2f}%")

        df_sacados["Valor"] = df_sacados["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df_sacados["%PL"] = df_sacados["%PL"].apply(lambda x: f"{x:.2f}%")

        st.markdown("#### Sacados")
        st.dataframe(df_sacados, use_container_width=True, height=400)

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {HONEYDEW}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

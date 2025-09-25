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

# ========== LIMITES DE ENQUADRAMENTO ==========
LIMITES = {
    "Apuama": {
        "maior_cedente": 10,
        "top_cedentes": 40,
        "maior_sacado": 10,
        "top_sacados": 35
    },
    "Bristol": {
        "maior_cedente": 7,
        "top_cedentes": 40,
        "maior_sacado": 10,
        "top_sacados": 25
    }
}

# Cedentes que devem virar sacados
CEDENTES_SUBSTITUIR = [
    "UY3 SOCIEDADE DE CREDITO DIRETO S/ A",
    "MONEY PLUS SOCIEDADE DE CREDITO AO MICROEMPREENDED",
    "MONEY PLUS SOCIEDADE DE CREDITO AO MICRO",
    "BMP MONEY PLUS SOCIEDADE DE CRÉDITO DIRETO SA"
]

# ========== ABA ENQUADRAMENTO ==========
with aba[1]:
    st.markdown("### 📊 Enquadramento - Cedentes e Sacados")

    fundo_sel = st.selectbox("Selecione o fundo", ["Apuama", "Bristol"])
    limites = LIMITES[fundo_sel]

    # caminho salvo em /tmp
    tmp_path = f"/tmp/{fundo_sel}.xlsx"

    uploaded_file = st.file_uploader(f"Envie o arquivo de estoque ({fundo_sel})", type=["xlsx"], key=f"upload_{fundo_sel}")
    if uploaded_file is not None:
        # salva o arquivo em /tmp
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        df_estoque = pd.read_excel(uploaded_file)
    elif os.path.exists(tmp_path):
        df_estoque = pd.read_excel(tmp_path)
        st.info(f"Usando arquivo salvo anteriormente para {fundo_sel}.")
    else:
        st.warning("Nenhum arquivo enviado ainda.")
        df_estoque = None

    if df_estoque is not None:
        df_estoque = df_estoque.rename(columns={{
            "NOME_CEDENTE": "Cedente",
            "DOC_CEDENTE": "CNPJ_Cedente",
            "NOME_SACADO": "Sacado",
            "DOC_SACADO": "CNPJ_Sacado",
            "VALOR_NOMINAL": "Valor"
        }})

        # substitui cedente -> sacado
        mask = df_estoque["Cedente"].isin(CEDENTES_SUBSTITUIR)
        df_estoque.loc[mask, "Cedente"] = df_estoque.loc[mask, "Sacado"]
        df_estoque.loc[mask, "CNPJ_Cedente"] = df_estoque.loc[mask, "CNPJ_Sacado"]

        # consolida
        df_estoque = df_estoque.groupby(["Cedente", "CNPJ_Cedente", "Sacado", "CNPJ_Sacado"], as_index=False)["Valor"].sum()

        # PL
        GOOGLE_SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"
        aba_pl = "Dre_Apuama" if fundo_sel == "Apuama" else "Dre_Bristol"
        url_pl = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={aba_pl}"
        r_pl = requests.get(url_pl)
        r_pl.raise_for_status()
        df_pl = pd.read_csv(StringIO(r_pl.text))
        df_pl["Data"] = pd.to_datetime(df_pl["Data"], dayfirst=True, errors="coerce")

        data_pl = df_pl["Data"].max()
        pl_fundo = converter_valor_br(df_pl.loc[df_pl["Data"] == data_pl, "PL TOTAL"].values[0])

        st.markdown(f"**PL usado ({fundo_sel} - {data_pl.strftime('%d/%m/%Y')}):** R$ {pl_fundo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Cedentes
        df_cedentes = df_estoque.groupby(["Cedente", "CNPJ_Cedente"], as_index=False)["Valor"].sum()
        df_cedentes["%PL"] = df_cedentes["Valor"].astype(float) / float(pl_fundo) * 100
        df_cedentes = df_cedentes.sort_values("%PL", ascending=False)

        maior_cedente = df_cedentes.iloc[0]
        top5_cedentes = df_cedentes.head(5)["%PL"].sum()

        st.metric(
            "Maior Cedente",
            f"{maior_cedente['Cedente']} - {maior_cedente['%PL']:.2f}%",
            delta="✅ Enquadrado" if maior_cedente['%PL'] <= limites["maior_cedente"] else "❌ Fora do Limite"
        )
        st.metric(
            "Top 5 Cedentes",
            f"{top5_cedentes:.2f}%",
            delta="✅ Enquadrado" if top5_cedentes <= limites["top_cedentes"] else "❌ Fora do Limite"
        )

        df_cedentes["Valor"] = df_cedentes["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df_cedentes["%PL"] = df_cedentes["%PL"].apply(lambda x: f"{x:.2f}%")

        st.markdown("#### Cedentes")
        st.dataframe(df_cedentes, use_container_width=True, height=400)

        # Sacados
        df_sacados = df_estoque.groupby(["Sacado", "CNPJ_Sacado"], as_index=False)["Valor"].sum()
        df_sacados["%PL"] = df_sacados["Valor"].astype(float) / float(pl_fundo) * 100
        df_sacados = df_sacados.sort_values("%PL", ascending=False)

        maior_sacado = df_sacados.iloc[0]
        topN = 10 if fundo_sel == "Apuama" else 5
        topN_sacados = df_sacados.head(topN)["%PL"].sum()

        st.metric(
            "Maior Sacado",
            f"{maior_sacado['Sacado']} - {maior_sacado['%PL']:.2f}%",
            delta="✅ Enquadrado" if maior_sacado['%PL'] <= limites["maior_sacado"] else "❌ Fora do Limite"
        )
        st.metric(
            f"Top {topN} Sacados",
            f"{topN_sacados:.2f}%",
            delta="✅ Enquadrado" if topN_sacados <= limites["top_sacados"] else "❌ Fora do Limite"
        )

        df_sacados["Valor"] = df_sacados["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df_sacados["%PL"] = df_sacados["%PL"].apply(lambda x: f"{x:.2f}%")

        st.markdown("#### Sacados")
        st.dataframe(df_sacados, use_container_width=True, height=400)

        # ========== SIMULADOR DE OPERAÇÃO ==========
        st.markdown("### 🧮 Simulador de Operação")

        aba_sim = st.tabs(["Cedente", "Sacado"])

        # --- Simulador Cedente ---
        with aba_sim[0]:
            cedente_sim = st.selectbox("Selecione o Cedente para simular", df_cedentes["Cedente"].unique())
            valor_simulado_ced = st.number_input("Digite o valor da operação simulada (R$)", min_value=0.0, step=1000.0, key="cedente_sim")

            if valor_simulado_ced > 0:
                linha_ced = df_cedentes[df_cedentes["Cedente"] == cedente_sim].copy()
                valor_atual = converter_valor_br(linha_ced["Valor"].values[0])
                novo_total = valor_atual + valor_simulado_ced
                perc_total = novo_total / pl_fundo * 100

                df_cedentes_sim = df_cedentes.copy()
                df_cedentes_sim.loc[df_cedentes_sim["Cedente"] == cedente_sim, "%PL"] = f"{perc_total:.2f}%"
                top5_cedentes_sim = df_cedentes_sim.head(5)["%PL"].str.replace("%", "").str.replace(",", ".").astype(float).sum()

                st.markdown(f"**Valor atual:** R$ {valor_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"**Valor simulado:** R$ {valor_simulado_ced:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"**Novo total:** R$ {novo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                st.metric(
                    "Novo %PL do Cedente",
                    f"{perc_total:.2f}%",
                    delta="✅ Enquadrado" if perc_total <= limites["maior_cedente"] else "❌ Fora do Limite"
                )
                st.metric(
                    "Novo Top 5 Cedentes",
                    f"{top5_cedentes_sim:.2f}%",
                    delta="✅ Enquadrado" if top5_cedentes_sim <= limites["top_cedentes"] else "❌ Fora do Limite"
                )

        # --- Simulador Sacado ---
        with aba_sim[1]:
            sacado_sim = st.selectbox("Selecione o Sacado para simular", df_sacados["Sacado"].unique())
            valor_simulado_sac = st.number_input("Digite o valor da operação simulada (R$)", min_value=0.0, step=1000.0, key="sacado_sim")

            if valor_simulado_sac > 0:
                linha_sac = df_sacados[df_sacados["Sacado"] == sacado_sim].copy()
                valor_atual_sac = converter_valor_br(linha_sac["Valor"].values[0])
                novo_total_sac = valor_atual_sac + valor_simulado_sac
                perc_total_sac = novo_total_sac / pl_fundo * 100

                df_sacados_sim = df_sacados.copy()
                df_sacados_sim.loc[df_sacados_sim["Sacado"] == sacado_sim, "%PL"] = f"{perc_total_sac:.2f}%"
                topN_sacados_sim = df_sacados_sim.head(topN)["%PL"].str.replace("%", "").str.replace(",", ".").astype(float).sum()

                st.markdown(f"**Valor atual:** R$ {valor_atual_sac:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"**Valor simulado:** R$ {valor_simulado_sac:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"**Novo total:** R$ {novo_total_sac:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                st.metric(
                    "Novo %PL do Sacado",
                    f"{perc_total_sac:.2f}%",
                    delta="✅ Enquadrado" if perc_total_sac <= limites["maior_sacado"] else "❌ Fora do Limite"
                )
                st.metric(
                    f"Novo Top {topN} Sacados",
                    f"{topN_sacados_sim:.2f}%",
                    delta="✅ Enquadrado" if topN_sacados_sim <= limites["top_sacados"] else "❌ Fora do Limite"
                )

# ========== RODAPÉ ==========
st.markdown(
    f"""<p style="text-align: right; color: {HONEYDEW}; font-size: 1em;">
        Powered by Juan & Streamlit | <b style="color:{HARVEST_GOLD}">LIBRA CAPITAL</b> 🦁
    </p>""",
    unsafe_allow_html=True,
)

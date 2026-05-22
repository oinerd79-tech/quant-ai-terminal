import finnhub
from twelvedata import TDClient
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px

def gerar_analise(

    retorno,
    momentum,
    volatilidade,
    sharpe

):

    tendencia = "neutra"

    if momentum > 20:
        tendencia = "forte alta"

    elif momentum < -10:
        tendencia = "forte baixa"

    risco = "moderado"

    if volatilidade > 50:
        risco = "alto"

    elif volatilidade < 25:
        risco = "baixo"

    qualidade = "mediana"

    if sharpe > 1.5:
        qualidade = "excelente"

    elif sharpe > 1:
        qualidade = "boa"

    texto = f"""

    O ativo apresenta tendência de {tendencia},
    retorno anual de {retorno:.2f}%,
    momentum de {momentum:.2f}%,
    volatilidade {risco}
    e relação risco/retorno {qualidade}.

    """

    return texto

finnhub_client = finnhub.Client(

    api_key=st.secrets["FINNHUB_API"]

)

td = TDClient(

    apikey=st.secrets["TWELVE_API"]

)

# =========================================
# CONFIG
# =========================================

st.set_page_config(

    page_title="Quant AI Terminal",

    layout="wide"

)

st.title("📈 Quant AI Terminal")

st.sidebar.header("⚙️ Configurações")

quantidade_ativos = st.sidebar.slider(

    "Quantidade de ativos",

    3,

    20,

    7

)

lista_base = [

    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "AMZN",
    "GOOGL",
    "TSLA",
    "AMD",
    "NFLX",
    "AVGO",
    "PLTR",
    "INTC",
    "CRM",
    "ADBE",
    "ORCL",
    "QCOM",
    "MU",
    "SHOP",
    "SNOW",
    "UBER"

]

acoes = lista_base[:quantidade_ativos]

st.markdown(
    "Engine quantitativa baseada em momentum, volatilidade e Sharpe Ratio."
)

# =========================================
# LISTA DE AÇÕES
# =========================================

acoes = [

    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "AMZN",
    "GOOGL",
    "TSLA"

]

# =========================================
# COLETA
# =========================================
spy = yf.download(

    "SPY",

    period="1y",

    progress=False,

    auto_adjust=True

)

spy_retorno = (

    (
        spy["Close"].iloc[-1]
        /
        spy["Close"].iloc[0]
    ) - 1

) * 100

dados = []

for ticker in acoes:

    st.write(f"Processando: {ticker}")

    try:

        df_preco = yf.download(

            ticker,

            period="1y",

            progress=False,

            auto_adjust=True

        )

        if df_preco.empty:

            st.warning(f"{ticker} sem dados")

            continue

        close = df_preco["Close"].squeeze()

        preco = round(

            float(close.iloc[-1]),

            2

        )

        retorno_1y = (

            (
                close.iloc[-1]
                /
                close.iloc[0]
            ) - 1

        ) * 100

        retornos = close.pct_change().dropna()

        volatilidade = (

            retornos.std()

        ) * (252 ** 0.5) * 100

        momentum = (

            (
                close.iloc[-1]
                /
                close.iloc[-90]
            ) - 1

        ) * 100

        sharpe = 0

        if volatilidade > 0:

            sharpe = retorno_1y / volatilidade

        score = 0

        if retorno_1y > 20:
            score += 25

        if momentum > 10:
            score += 25

        if sharpe > 1:
            score += 25

        if volatilidade < 40:
            score += 25

        dados.append({

            "Ticker": ticker,

            "Preço": preco,

            "Retorno 1Y %": round(retorno_1y, 2),

            "Momentum 90D %": round(momentum, 2),

            "Volatilidade %": round(volatilidade, 2),

            "Sharpe": round(sharpe, 2),

            "Score": score,
            
            "Análise IA": gerar_analise(

                retorno_1y,
                momentum,
                volatilidade,
                sharpe

    )

        })

        st.success(f"{ticker} carregado")

    except Exception as erro:

        st.error(
            f"Erro em {ticker}: {erro}"
        )

# =========================================
# DATAFRAME
# =========================================

df = pd.DataFrame(dados)

# =========================================
# RESULTADO
# =========================================

if df.empty:

    st.error("Nenhum dado encontrado.")

else:

    df = df.sort_values(

        by="Score",

        ascending=False

    )

    st.subheader("🏆 Ranking Quantitativo")

top1 = df.iloc[0]
top2 = df.iloc[1]
top3 = df.iloc[2]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "🥇 Melhor Ativo",

        top1["Ticker"],

        f'{top1["Score"]} pts'

    )

with col2:

    st.metric(

        "🥈 Segundo Lugar",

        top2["Ticker"],

        f'{top2["Score"]} pts'

    )

with col3:

    st.metric(

        "🥉 Terceiro Lugar",

        top3["Ticker"],

        f'{top3["Score"]} pts'

    )

st.dataframe(

    df.style.background_gradient(

        subset=["Score"],

        cmap="RdYlGn"

    ),

    use_container_width=True

)

st.subheader("📊 Ranking de Score")

fig = px.bar(

    df,

    x="Ticker",

    y="Score",

    color="Score",

    text="Score"

)

fig.update_layout(

    template="plotly_dark",

    height=500

)

st.plotly_chart(

    fig,

    use_container_width=True,

    key="grafico_score"

)
st.subheader("🔥 Heatmap Quantitativo")

fig_heat = px.treemap(

    df,

    path=["Ticker"],

    values="Score",

    color="Score",

    color_continuous_scale="RdYlGn"

)

fig_heat.update_layout(

    template="plotly_dark",

    height=700

)

st.plotly_chart(

    fig_heat,

    use_container_width=True,

    key="heatmap_quant"

)
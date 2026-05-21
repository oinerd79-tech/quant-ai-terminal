import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.optimize import minimize
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
# import ollama


st.set_page_config(
    page_title="Analista de Ações",
    layout="wide"
)
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2721/2721268.png",
    width=80
)

st.sidebar.title("QUANT AI")
st.markdown("""

# 📊 QUANT AI TERMINAL

### Plataforma Quantitativa Institucional com IA

---
""")

# =====================================
# LISTA DE AÇÕES
# =====================================

acoes = [

    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "AMZN"

]
# =====================================
# FUNÇÃO SEGURA
# =====================================

def valor_seguro(valor, padrao=0):

    try:

        if valor is None:
            return padrao

        if isinstance(valor, str):
            return padrao

        if np.isnan(valor):
            return padrao

        return valor

    except:

        return padrao

# =====================================
# COLETA PRINCIPAL
# =====================================

dados = []

for ticker in acoes:
    st.write(f"Processando: {ticker}")
    try:

        acao = yf.Ticker(ticker)
        info = acao.info

        preco = valor_seguro(
            info.get("currentPrice", 0)
        )

        if preco <= 0:

            st.warning(f"{ticker} sem preço válido")

            continue
        st.success(f"{ticker} carregado")
        pe = valor_seguro(
            info.get("trailingPE", 0)
        )

        peg = valor_seguro(
            info.get("pegRatio", 0)
        )

        roe = valor_seguro(
            info.get("returnOnEquity", 0)
        ) * 100

        margem = valor_seguro(
            info.get("profitMargins", 0)
        ) * 100

        receita_growth = valor_seguro(
            info.get("revenueGrowth", 0)
        ) * 100

        ev_ebitda = valor_seguro(
            info.get("enterpriseToEbitda", 0)
        )

        divida = valor_seguro(
            info.get("debtToEquity", 0)
        )

        setor = info.get("sector", "N/A")

        # =====================================
        # HISTÓRICO 15 ANOS
        # =====================================

        historico_15y = acao.history(period="15y")

        if historico_15y.empty:
            crescimento_15y = 0

        else:

            preco_inicial_15y = historico_15y["Close"].iloc[0]
            preco_final_15y = historico_15y["Close"].iloc[-1]

            crescimento_15y = (
                (
                    preco_final_15y - preco_inicial_15y
                ) / preco_inicial_15y
            ) * 100

        # =====================================
        # MOMENTUM 12M
        # =====================================

        historico_1y = acao.history(period="1y")

        if historico_1y.empty:

            momentum_12m = 0
            volatilidade = 0

        else:

            preco_inicial_1y = historico_1y["Close"].iloc[0]
            preco_final_1y = historico_1y["Close"].iloc[-1]

            momentum_12m = (
                (
                    preco_final_1y - preco_inicial_1y
                ) / preco_inicial_1y
            ) * 100

            retornos = historico_1y["Close"].pct_change()

            volatilidade = (
                retornos.std() * np.sqrt(252)
            ) * 100

        # =====================================
        # CAGR 5 ANOS
        # =====================================

        historico_5y = acao.history(period="5y")

        if historico_5y.empty:

            retorno_5y = 0
            cagr = 0
            sharpe = 0
            drawdown = 0

        else:

            preco_inicial_5y = historico_5y["Close"].iloc[0]
            preco_final_5y = historico_5y["Close"].iloc[-1]

            retorno_5y = (
                (
                    preco_final_5y - preco_inicial_5y
                ) / preco_inicial_5y
            ) * 100

            anos = 5

            cagr = (
                (
                    preco_final_5y / preco_inicial_5y
                ) ** (1 / anos) - 1
            ) * 100

            retornos_diarios = historico_5y[
                "Close"
            ].pct_change().dropna()

            volatilidade_sharpe = (
                retornos_diarios.std() * np.sqrt(252)
            )

            retorno_medio = (
                retornos_diarios.mean() * 252
            )

            if volatilidade_sharpe > 0:
                sharpe = retorno_medio / volatilidade_sharpe
            else:
                sharpe = 0

            maximo = historico_5y["Close"].cummax()

            drawdown = (
                (
                    historico_5y["Close"] - maximo
                ) / maximo
            ).min() * 100

        # =====================================
        # SCORE QUANTITATIVO
        # =====================================

        score = 0

        if pe > 0 and pe < 25:
            score += 15

        if peg > 0 and peg < 2:
            score += 15

        if roe > 15:
            score += 15

        if margem > 15:
            score += 10

        if receita_growth > 10:
            score += 15

        if crescimento_15y > 300:
            score += 15

        if momentum_12m > 15:
            score += 10

        if sharpe > 1:
            score += 10

        # =====================================
        # FAIR VALUE
        # =====================================

        fair_value = preco * (1 + (score / 100))

        upside = (
            (
                fair_value - preco
            ) / preco
        ) * 100

        # =====================================
        # SALVAR DADOS
        # =====================================
       
        dados.append({

            "Ticker": ticker,
            "Setor": setor,
            "Preço": round(preco, 2),
            "P/L": round(pe, 2),
            "PEG": round(peg, 2),
            "ROE %": round(roe, 2),
            "Margem %": round(margem, 2),
            "Receita Growth %": round(receita_growth, 2),
            "EV/EBITDA": round(ev_ebitda, 2),
            "Dívida": round(divida, 2),
            "15Y Growth %": round(crescimento_15y, 2),
            "Momentum 12M %": round(momentum_12m, 2),
            "Retorno 5Y %": round(retorno_5y, 2),
            "CAGR %": round(cagr, 2),
            "Sharpe": round(sharpe, 2),
            "Drawdown %": round(drawdown, 2),
            "Volatilidade %": round(volatilidade, 2),
            "Score": round(score, 2),
            "Fair Value": round(fair_value, 2),
            "Upside %": round(upside, 2)

        })

    except:

        pass

# =====================================
# DATAFRAME
# =====================================

if len(dados) == 0:

    st.error("Nenhum dado encontrado.")
    st.stop()


if len(dados) > 0:

    df = pd.DataFrame(dados)

else:

    st.warning(
        "Nenhum dado encontrado."
    )

    st.stop()

# =====================================
# SCORE AVANÇADO
# =====================================

df["Score Avançado"] = (
    df["Score"]
    + (df["Sharpe"] * 10)
    + (df["CAGR %"] * 0.5)
    - (abs(df["Drawdown %"]) * 0.1)
)
# =====================================
# FILTROS
# =====================================

st.sidebar.title("Filtros")

setores = st.sidebar.multiselect(
    "Setores",
    options=df["Setor"].unique(),
    default=df["Setor"].unique()
)

score_minimo = st.sidebar.slider(
    "Score Mínimo",
    0,
    200,
    20
)

upside_minimo = st.sidebar.slider(
    "Upside Mínimo %",
    -100,
    300,
    10
)

volatilidade_max = st.sidebar.slider(
    "Volatilidade Máxima %",
    0,
    100,
    60
)

# Aplicar filtros

df = df[
    (df["Setor"].isin(setores))
    &
    (df["Score"] >= score_minimo)
    &
    (df["Upside %"] >= upside_minimo)
    &
    (df["Volatilidade %"] <= volatilidade_max)
]
# =====================================
# RANKING
# =====================================

df = df.sort_values(
    by="Score Avançado",
    ascending=False
)

# =====================================
# TOP 20
# =====================================

st.subheader("🏆 Ranking Quantitativo")

st.dataframe(
    df,
    use_container_width=True
)

# =====================================
# TOP 10
# =====================================

st.subheader("📊 Top 10 Ações")

fig = px.bar(

    df.head(10),

    x="Ticker",

    y="Score Avançado",

    color="Upside %",

    text="Score Avançado",

    title="Top 10 Ações Quantitativas"

)

fig.update_layout(

    template="plotly_dark",

    height=600,

    title_font_size=28,

    font_size=14

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# MÉTRICAS
# =====================================

st.subheader("📈 Indicadores da Estratégia")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Score Médio",
        round(df["Score Avançado"].mean(), 2)
    )

with col2:

    st.metric(
        "CAGR Médio",
        f"{round(df['CAGR %'].mean(), 2)}%"
    )

with col3:

    st.metric(
        "Sharpe Médio",
        round(df["Sharpe"].mean(), 2)
    )

with col4:

    st.metric(
        "Upside Médio",
        f"{round(df['Upside %'].mean(), 2)}%"
    )

# =====================================
# MELHOR AÇÃO
# =====================================

melhor = df.iloc[0]

st.subheader("🚀 Melhor Ação do Ranking")

st.success(
    f"{melhor['Ticker']} | "
    f"Score: {round(melhor['Score Avançado'], 2)}"
)

# =====================================
# TABELA FINAL
# =====================================

st.subheader("📋 Resumo Final")

st.dataframe(

    df.style

    .background_gradient(
        cmap="viridis",
        subset=["Score Avançado"]
    )

    .format({

        "Preço": "${:.2f}",

        "Upside %": "{:.2f}%",

        "CAGR %": "{:.2f}%",

        "Sharpe": "{:.2f}"

    }),

    use_container_width=True

)
# =====================================
# BACKTEST SIMPLES
# =====================================

st.subheader("📈 Backtest da Estratégia")

top10 = df.head(10)["Ticker"].tolist()

carteira = yf.download(
    top10,
    period="5y"
)["Close"]

retornos = carteira.pct_change()

retorno_carteira = retornos.mean(axis=1)

retorno_acumulado = (
    1 + retorno_carteira
).cumprod()

spy = yf.download(
    "SPY",
    period="5y"
)

spy_close = spy["Close"].squeeze()

spy_retornos = spy_close.pct_change()

spy_acumulado = (
    1 + spy_retornos
).cumprod()

grafico = pd.DataFrame({
    "Estratégia": retorno_acumulado,
    "SPY": spy_acumulado
})

st.line_chart(grafico)
# =====================================
# PORTFOLIO OPTIMIZATION
# =====================================

st.subheader("🧠 Portfolio Optimization")

ativos = df.head(10)["Ticker"].tolist()

dados_otimizacao = yf.download(
    ativos,
    period="5y"
)["Close"]

retornos = dados_otimizacao.pct_change().dropna()

retorno_medio = retornos.mean() * 252

cov_matrix = retornos.cov() * 252

num_ativos = len(ativos)

# =====================================
# FUNÇÃO SHARPE
# =====================================

def negativo_sharpe(pesos):

    retorno = np.sum(
        retorno_medio * pesos
    )

    volatilidade = np.sqrt(
        np.dot(
            pesos.T,
            np.dot(cov_matrix, pesos)
        )
    )

    sharpe = retorno / volatilidade

    return -sharpe

# =====================================
# RESTRIÇÕES
# =====================================

restricoes = (
    {
        "type": "eq",
        "fun": lambda x: np.sum(x) - 1
    },
)

limites = tuple(
    (0, 0.30)
    for _ in range(num_ativos)
)

pesos_iniciais = num_ativos * [
    1 / num_ativos
]

# =====================================
# OTIMIZAÇÃO
# =====================================

resultado = minimize(
    negativo_sharpe,
    pesos_iniciais,
    method="SLSQP",
    bounds=limites,
    constraints=restricoes
)

pesos_otimizados = resultado.x

# =====================================
# RESULTADO FINAL
# =====================================

portfolio = pd.DataFrame({

    "Ticker": ativos,

    "Peso Ideal %": (
        pesos_otimizados * 100
    ).round(2)

})

portfolio = portfolio.sort_values(
    by="Peso Ideal %",
    ascending=False
)

st.dataframe(
    portfolio,
    use_container_width=True
)

# =====================================
# GRÁFICO
# =====================================

fig_portfolio = px.pie(
    portfolio,
    names="Ticker",
    values="Peso Ideal %",
    title="Distribuição Ideal da Carteira"
)

st.plotly_chart(
    fig_portfolio,
    use_container_width=True
)
# =====================================
# IA ANALISTA LOCAL
# =====================================

st.subheader("🤖 IA Analista Local")

melhor = df.iloc[0]

prompt = f"""
Faça uma análise profissional da ação:

Ticker: {melhor['Ticker']}

Preço: {melhor['Preço']}
P/L: {melhor['P/L']}
ROE: {melhor['ROE %']}
Momentum: {melhor['Momentum 12M %']}
CAGR: {melhor['CAGR %']}
Sharpe: {melhor['Sharpe']}
Drawdown: {melhor['Drawdown %']}
Upside: {melhor['Upside %']}

Explique:
- pontos fortes
- riscos
- qualidade da empresa
- perspectiva quantitativa
- conclusão final
"""

try:

    # response = ollama.chat(
#
#     model="tinyllama",
#
#     messages=[
#
#         {
#             "role": "user",
#             "content": prompt
#         }
#
#     ]
#
# )

    analise = resposta["message"]["content"]

    st.write(analise)

except Exception as erro:

    st.error(f"Erro IA Local: {erro}")
    # =====================================
# GERAR RELATÓRIO PDF
# =====================================

st.subheader("📄 Relatório Automático")

if st.button("Gerar Relatório PDF"):

    try:

        doc = SimpleDocTemplate(
            "relatorio_quantitativo.pdf"
        )

        estilos = getSampleStyleSheet()

        elementos = []

        titulo = Paragraph(
            "Relatório Quantitativo de Ações",
            estilos["Title"]
        )

        elementos.append(titulo)

        elementos.append(
            Spacer(1, 20)
        )

        # ======================
        # TOP 5
        # ======================

        top5 = df.head(5)

        for _, linha in top5.iterrows():

            texto = f"""
            <b>{linha['Ticker']}</b><br/>
            Score: {linha['Score Avançado']}<br/>
            CAGR: {linha['CAGR %']}%<br/>
            Sharpe: {linha['Sharpe']}<br/>
            Upside: {linha['Upside %']}%<br/>
            """

            paragrafo = Paragraph(
                texto,
                estilos["BodyText"]
            )

            elementos.append(paragrafo)

            elementos.append(
                Spacer(1, 12)
            )

        # ======================
        # IA ANALISTA
        # ======================

        analise_pdf = Paragraph(

            f"""
            <b>Análise IA:</b><br/><br/>
            {analise}
            """,

            estilos["BodyText"]

        )

        elementos.append(analise_pdf)

        doc.build(elementos)

        st.success(
            "PDF gerado com sucesso!"
        )

    except Exception as erro:

        st.error(
            f"Erro PDF: {erro}"
        )
        # =====================================
# RADAR AUTOMÁTICO
# =====================================

st.subheader("🚨 Radar Quantitativo")

# ======================
# TOP PICKS
# ======================

top_picks = df.sort_values(
    by="Score Avançado",
    ascending=False
).head(5)

st.markdown("## 🏆 Top Picks do Dia")

st.dataframe(

    top_picks[[
        "Ticker",
        "Score Avançado",
        "Momentum 12M %",
        "Sharpe",
        "Upside %"
    ]],

    use_container_width=True

)

# ======================
# MAIOR MOMENTUM
# ======================

momentum = df.sort_values(
    by="Momentum 12M %",
    ascending=False
).head(5)

st.markdown("## ⚡ Maior Momentum")

st.dataframe(

    momentum[[
        "Ticker",
        "Momentum 12M %",
        "CAGR %",
        "Sharpe"
    ]],

    use_container_width=True

)

# ======================
# MENOR RISCO
# ======================

baixo_risco = df.sort_values(
    by="Volatilidade %",
    ascending=True
).head(5)

st.markdown("## 🛡️ Menor Volatilidade")

st.dataframe(

    baixo_risco[[
        "Ticker",
        "Volatilidade %",
        "Sharpe",
        "Drawdown %"
    ]],

    use_container_width=True

)

# ======================
# MAIOR UPSIDE
# ======================

upside = df.sort_values(
    by="Upside %",
    ascending=False
).head(5)

st.markdown("## 🚀 Maior Upside")

st.dataframe(

    upside[[
        "Ticker",
        "Upside %",
        "Score Avançado",
        "CAGR %"
    ]],

    use_container_width=True

)
# =====================================
# HEATMAP DE CORRELAÇÃO
# =====================================

st.subheader("🧠 Heatmap de Correlação")

try:

    tickers_heatmap = df.head(10)[
        "Ticker"
    ].tolist()

    dados_heatmap = yf.download(

        tickers_heatmap,

        period="1y"

    )["Close"]

    retornos_heatmap = (
        dados_heatmap
        .pct_change()
        .dropna()
    )

    correlacao = (
        retornos_heatmap
        .corr()
    )

    fig_heatmap, ax = plt.subplots(
        figsize=(12, 8)
    )

    sns.heatmap(

        correlacao,

        annot=True,

        cmap="viridis",

        linewidths=0.5,

        ax=ax

    )

    plt.title(
        "Correlação entre Ativos"
    )

    st.pyplot(fig_heatmap)

except Exception as erro:

    st.error(
        f"Erro Heatmap: {erro}"
    )
    # =====================================
# MINI GRÁFICOS
# =====================================

st.subheader("📈 Mini Charts")

top_charts = df.head(4)

colunas = st.columns(2)

for i, (_, linha) in enumerate(
    top_charts.iterrows()
):

    ticker = linha["Ticker"]

    try:

        dados_chart = yf.download(

            ticker,

            period="6mo"

        )["Close"]

        fig_spark = go.Figure()

        fig_spark.add_trace(

            go.Scatter(

                x=dados_chart.index,

                y=dados_chart,

                mode="lines",

                name=ticker

            )

        )

        fig_spark.update_layout(

            template="plotly_dark",

            height=250,

            margin=dict(
                l=10,
                r=10,
                t=40,
                b=10
            ),

            title=ticker,

            showlegend=False

        )

        with colunas[i % 2]:

            st.plotly_chart(

                fig_spark,

                use_container_width=True

            )

    except Exception as erro:

        st.error(
            f"Erro gráfico {ticker}: {erro}"
        )
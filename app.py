import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Initialisation de l'app Dash
app = dash.Dash(__name__)

# Fonction pour charger les données
def load_data():
    df = pd.read_csv("bitcoin_prices.csv", sep=",", header=None, names=["datetime", "price"])
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna()
    return df

# Rapport journalier
def daily_report():
    df = load_data()
    today = pd.Timestamp.now().date()
    daily_df = df[df["datetime"].dt.date == today]
    if daily_df.empty:
        return html.P("Pas de données disponibles pour aujourd'hui.")

    open_price = daily_df.iloc[0]["price"]
    close_price = daily_df.iloc[-1]["price"]
    change = close_price - open_price
    pct_change = (change / open_price) * 100 if open_price != 0 else 0

    return html.Div([
        html.H3("📊 Rapport Bitcoin (aujourd'hui)"),
        html.P(f"Prix d'ouverture : ${open_price:,.2f}"),
        html.P(f"Prix actuel : ${close_price:,.2f}"),
        html.P(f"Variation : {change:+,.2f} USD ({pct_change:+.2f}%)"),
    ])

# Graphique principal
df = load_data()
fig = px.line(df, x="datetime", y="price", title="Évolution du Bitcoin (BTC)")
fig.update_layout(
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#00ffcc"),
    title_font=dict(color="#00ffcc", size=20),
    title_x=0.5,
    xaxis=dict(showgrid=True, gridcolor="#00ffcc"),
    yaxis=dict(showgrid=True, gridcolor="#00ffcc"),
    margin=dict(t=60, l=40, r=40, b=40)
)

# Mise en page du dashboard
app.layout = html.Div(style={
    "backgroundColor": "#0d0d0d",
    "color": "#00ffcc",
    "fontFamily": "Courier New, monospace",
    "padding": "40px"
}, children=[

    # Logo Julie & Antoni
    html.Img(
        src="/assets/logo-JulieAntoni.png",
        style={
            "display": "block",
            "margin": "0 auto",
            "height": "120px",
            "marginBottom": "20px",
            "filter": "drop-shadow(0 0 10px #00ffcc)"
        }
    ),

    # Titre
    html.H1("CryptoBoard: BTC Live Tracker", style={
        "textAlign": "center",
        "fontSize": "36px",
        "textShadow": "0 0 10px #00ffcc"
    }),

    # Compteur live
    html.Div(id="live-counter", style={
        "textAlign": "center",
        "fontSize": "42px",
        "color": "#39ff14",
        "marginBottom": "30px",
        "fontWeight": "bold",
        "textShadow": "0 0 20px #00ffcc"
    }),

    dcc.Interval(id="interval", interval=1000, n_intervals=0),

    # Graphique
    dcc.Graph(figure=fig, style={"marginBottom": "40px"}),

    # Rapport journalier
    html.Div(daily_report(), style={
        "backgroundColor": "#111",
        "border": "1px solid #00ffcc",
        "borderRadius": "10px",
        "maxWidth": "600px",
        "margin": "0 auto",
        "padding": "20px",
        "boxShadow": "0 0 20px #00ffcc"
    })
])

# Callback compteur live
@app.callback(
    Output("live-counter", "children"),
    Input("interval", "n_intervals")
)
def update_counter(n):
    df = load_data()
    if df.empty:
        return "⛔ Aucune donnée"
    latest = df.sort_values("datetime").iloc[-1]["price"]
    return f"💰 BTC/USD : ${latest:,.2f}"

# Lancer l'app
if __name__ == "__main__":
    app.run(debug=True)


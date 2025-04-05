import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

# Initialisation de l'application
app = dash.Dash(__name__)

# Fonction pour charger les données depuis population.csv
def load_data():
    df = pd.read_csv("population.csv", names=["datetime", "population"])
    df = df[~df["datetime"].str.contains("datetime", na=False)]
    df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce')
    df["population"] = pd.to_numeric(df["population"], errors='coerce')
    df = df.dropna()
    return df

# Rapport journalier
def daily_report():
    df = load_data()
    today = pd.Timestamp.now().date()
    daily_df = df[df["datetime"].dt.date == today]

    if daily_df.empty:
        return html.P("Pas de données disponibles pour aujourd'hui.")

    first = daily_df.iloc[0]["population"]
    last = daily_df.iloc[-1]["population"]
    change = last - first
    growth_pct = (change / first) * 100 if first != 0 else 0

    return html.Div([
        html.H3("📋 Rapport journalier"),
        html.P(f"Début : {int(first):,}"),
        html.P(f"Maintenant : {int(last):,}"),
        html.P(f"Croissance : {int(change):,} personnes"),
        html.P(f"Taux de croissance : {growth_pct:.6f} %"),
    ])

# Graphique
df = load_data()
fig = px.line(df, x="datetime", y="population", title="📈 Évolution de la population mondiale")
fig.update_layout(
    paper_bgcolor='#1e1e1e',
    plot_bgcolor='#2c2c2c',
    font=dict(color="white"),
    title_font=dict(size=20, color="#CCCCCC", family="Arial"),
    title_x=0.5,
    xaxis=dict(showgrid=True, gridcolor="#444"),
    yaxis=dict(showgrid=True, gridcolor="#444"),
    margin=dict(t=60, l=40, r=40, b=40)
)

# Mise en page
app.layout = html.Div(style={
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#1e1e1e",
    "padding": "40px",
    "color": "#ffffff"
}, children=[
    html.Img(
        src="/assets/logo-JulieAntoni.png",
        style={
            "display": "block",
            "margin": "0 auto",
            "height": "120px",
            "marginBottom": "30px",
            "filter": "drop-shadow(0px 0px 4px #fff)"
        }
    ),

    html.Div("Population Tracker", style={
        "textAlign": "center",
        "fontSize": "32px",
        "color": "#cccccc",
        "marginBottom": "20px",
        "fontWeight": "bold"
    }),

    # Compteur live
    html.Div(id="live-counter", style={
        "fontSize": "42px",
        "textAlign": "center",
        "color": "#00ffcc",
        "marginBottom": "30px",
        "fontWeight": "bold"
    }),

    dcc.Interval(
        id="interval-component",
        interval=1000,  # 1000 ms = 1 seconde
        n_intervals=0
    ),

    # Graphique
    dcc.Graph(figure=fig, style={"marginBottom": "40px"}),

    # Rapport journalier
    html.Div(
        daily_report(),
        style={
            "padding": "20px",
            "border": "1px solid #555",
            "borderRadius": "10px",
            "maxWidth": "500px",
            "margin": "0 auto",
            "backgroundColor": "#2a2a2a",
            "boxShadow": "0 2px 8px rgba(255, 255, 255, 0.1)"
        }
    )
])

# Callback pour mettre à jour le compteur en direct
@app.callback(
    Output("live-counter", "children"),
    Input("interval-component", "n_intervals")
)
def update_live_counter(n):
    df = load_data()
    if df.empty:
        return "Aucune donnée disponible"

    latest = df.sort_values("datetime").iloc[-1]["population"]
    return f"🌍 Population mondiale actuelle : {int(latest):,}"


# Lancement
if __name__ == '__main__':
    app.run(debug=True)

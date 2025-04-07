import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px

# Initialisation de l'app Dash
app = dash.Dash(__name__)
app.title = "CryptoBoard"
server = app.server

# Fonction pour charger les données
def load_data():
    df = pd.read_csv("/home/ubuntu/PGL_Project/Data/bitcoin_price.csv", sep=";", header=None, names=["date", "time", "price"])
    df["Date"] = pd.to_datetime(df["date"] + " " + df["time"], errors="coerce")
    df["Stock Price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna()
    df = df.sort_values("Date")
    return df[["Date", "Stock Price"]]

# Layout
app.layout = html.Div(style={
    "backgroundColor": "#0d0d0d",
    "color": "#00ffcc",
    "fontFamily": "Courier New, monospace",
    "padding": "40px"
}, children=[

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

    html.H1("CryptoBoard: BTC Live Tracker", style={
        "textAlign": "center",
        "fontSize": "36px",
        "textShadow": "0 0 10px #00ffcc"
    }),

    html.Div(id="live-counter", style={
        "textAlign": "center",
        "fontSize": "42px",
        "color": "#39ff14",
        "marginBottom": "30px",
        "fontWeight": "bold",
        "textShadow": "0 0 20px #00ffcc"
    }),

    dcc.Interval(id="interval", interval=1000, n_intervals=0),

    html.Div([
        html.Label("📅 Show data:", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.RadioItems(
            id="filter-radio",
            options=[
                {"label": "Since beginning", "value": "all"},
                {"label": "Today", "value": "today"}
            ],
            value="all",
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="btc-graph", style={"marginBottom": "40px"}),

    html.Div([
        html.Div([
            html.Button("⟵", id="prev-day", n_clicks=0, style={
                "fontSize": "24px", "backgroundColor": "#111", "color": "#00ffcc", "border": "none"
            }),
            html.Div(id="daily-report", style={
                "display": "inline-block",
                "margin": "0 20px",
                "verticalAlign": "top"
            }),
            html.Button("⟶", id="next-day", n_clicks=0, style={
                "fontSize": "24px", "backgroundColor": "#111", "color": "#00ffcc", "border": "none"
            }),
        ], style={"textAlign": "center", "marginBottom": "40px"}),

        dcc.Store(id="report-date-store"),
        dcc.Store(id="available-dates")
    ], style={
        "backgroundColor": "#111",
        "border": "1px solid #00ffcc",
        "borderRadius": "10px",
        "maxWidth": "700px",
        "margin": "0 auto",
        "padding": "20px",
        "boxShadow": "0 0 20px #00ffcc"
    })
])

# Initialisation des dates disponibles et de la date du jour — une seule fois
@app.callback(
    Output("available-dates", "data"),
    Output("report-date-store", "data"),
    Input("btc-graph", "figure"),
    State("report-date-store", "data"),
    prevent_initial_call=True
)
def initialize_data(_, current_report_date):
    if current_report_date:  # déjà initialisé
        raise dash.exceptions.PreventUpdate

    df = load_data()
    available_dates = sorted(list(df["Date"].dt.date.unique()))
    today = pd.Timestamp.now().date()
    closest = max([d for d in available_dates if d <= today], default=available_dates[0])
    return [d.isoformat() for d in available_dates], closest.isoformat()


# Navigation dans les rapports
@app.callback(
    Output("report-date-store", "data", allow_duplicate=True),
    Input("prev-day", "n_clicks"),
    Input("next-day", "n_clicks"),
    State("report-date-store", "data"),
    State("available-dates", "data"),
    prevent_initial_call=True
)
def navigate_report(prev_clicks, next_clicks, current_date, all_dates):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if current_date not in all_dates:
        raise dash.exceptions.PreventUpdate

    idx = all_dates.index(current_date)
    if btn_id == "prev-day" and idx > 0:
        return all_dates[idx - 1]
    elif btn_id == "next-day" and idx < len(all_dates) - 1:
        return all_dates[idx + 1]
    return current_date

# Mise à jour du rapport journalier
@app.callback(
    Output("daily-report", "children"),
    Output("prev-day", "disabled"),
    Output("next-day", "disabled"),
    Input("report-date-store", "data"),
    State("available-dates", "data")
)
def update_report(selected_date, all_dates):
    df = load_data()
    selected = pd.to_datetime(selected_date).date()
    daily_df = df[df["Date"].dt.date == selected]

    idx = all_dates.index(selected_date)
    disable_prev = idx == 0
    disable_next = idx == len(all_dates) - 1

    if daily_df.empty:
        return html.P(f"No data available for {selected.strftime('%B %-d, %Y')}."), disable_prev, disable_next

    daily_df = daily_df.sort_values("Date")
    open_price = daily_df.iloc[0]["Stock Price"]
    close_price = daily_df.iloc[-1]["Stock Price"]
    change = close_price - open_price
    pct_change = (change / open_price) * 100 if open_price != 0 else 0
    formatted_date = selected.strftime('%B %-d, %Y')

    return html.Div([
        html.H3(f"📊 Bitcoin Report for {formatted_date}"),
        html.P(f"Opening Price: ${open_price:,.2f}"),
        html.P(f"Current Price: ${close_price:,.2f}"),
        html.P(f"Change: {change:+,.2f} USD ({pct_change:+.2f}%)"),
    ]), disable_prev, disable_next

# Compteur live
@app.callback(
    Output("live-counter", "children"),
    Input("interval", "n_intervals")
)
def update_counter(n):
    df = load_data()
    if df.empty:
        return "⛔ No data"
    latest = df.iloc[-1]["Stock Price"]
    return f"💰 BTC/USD: ${latest:,.2f}"

# Graphique dynamique
@app.callback(
    Output("btc-graph", "figure"),
    Input("filter-radio", "value")
)
def update_graph(filter_value):
    df = load_data()
    if filter_value == "today":
        today = pd.Timestamp.now().date()
        df = df[df["Date"].dt.date == today]

    title = "Bitcoin Price Evolution (BTC/USD)"
    if filter_value == "today":
        title += " - Today"

    fig = px.line(df, x="Date", y="Stock Price", title=title)
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
    return fig

# Run app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)

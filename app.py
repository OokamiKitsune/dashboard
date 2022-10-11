import dash
from dash import html, dcc
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
from numpy import size
import pandas as pd
import plotly.express as px




# Loads dataframe from a csv

data_url = "https://raw.githubusercontent.com/plotly/datasets/master/supermarket_Sales.csv"
sales = pd.read_csv(data_url)
print(sales["Date"])
# Converts and make changes to some of the data
sales["Date"] = pd.to_datetime(sales["Date"])
print(sales["Date"])
sales = sales.sort_values("Date").set_index("Date")

sales["Revenue"] = sales["Unit price"] * sales["Quantity"]
sales.rename(columns={"Gross income": "Income after costs and taxes"}, inplace=True)

# Creates a historical graph

daily_sales_number = (
    sales["Invoice ID"].groupby(sales.index.date).nunique().rename("Number of sales")
)
title_font_size = 30

figure_daily_sales_number = px.line(
    daily_sales_number, title="Daily number of sales").update_layout(title_font_size=title_font_size)

m7d_mean_revenue = (
    sales["Revenue"].groupby(sales.index.date).sum().rolling(30, min_periods=7).mean()
)

figure_m7d_mean_revenue = px.line(
    m7d_mean_revenue, title="7-day moving average of daily revenue").update_layout(title_font_size=title_font_size)


# Add a map.
figure_locations_map = px.line_geo(data_frame=sales, title="Locations").update_layout(title_font_size=title_font_size)


# Creates a pie chart

figure_product_line = px.pie(
    sales.groupby("Product line")["Revenue"].sum().reset_index(),
    names="Product line",
    values="Revenue",
    title="Product lines ratio",
    ).update_layout(title_font_size=title_font_size)

# Creates a bar graph

figure_revenue_by_city = px.bar(
    sales.groupby(["City"])["Revenue"].sum(), title="Revenue by city"
    ).update_layout(title_font_size=title_font_size)


# Creates a table

sums = (
    sales
    [
        [
            "Revenue",
            "Tax 5%",
            "Cost of goods sold",
            "Income after costs and taxes",
        ]
    ]
    .sum()
    .rename("Value")
    .reset_index()
    .rename(columns={"index": "Item"})
) 


# Creates a datatable for the table

sums_datatable= html.Div(
    [
        html.P(),
        html.Label(
            "Revenue breakdown",
            style={"font-size": f"{title_font_size}px", "font-color": "grey"},
        ),
        html.P(),
        DataTable(
            data=sums.to_dict("records"),
            columns=[{"name": col, "id": col} for col in ["Item", "Value"]]
        ),
    ]
)

row_summary_metrics = dbc.Row(
    [
        dbc.Col("", width=1),
        dbc.Col(dcc.Graph(figure=figure_product_line)),
        dbc.Col(dcc.Graph(figure=figure_revenue_by_city)),
        dbc.Col(sums_datatable),
        dbc.Col("", width=1)
    ],
)


# Create and structure a dashboard layout using the html module.

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [

    html.H1("Sales KPIs"),
    html.H2("Sales Dataset"),
    html.Ul(
        
        [
            html.Li(f"Number of cities: {sales['City'].nunique()}"),
            html.Li(
                f"Time period: {sales.index.date[0].isoformat()[:10]} - {sales.index.date[-1].isoformat()[:10]}"
            ),
            html.Li(["Data soruce: ", html.A(data_url, href=data_url)]),
        ]
    ),
    # Adds figures to the layout. This will show the figures on the app. 
    row_summary_metrics,
    dcc.Graph(figure=figure_daily_sales_number),
    dcc.Graph(figure=figure_m7d_mean_revenue),
    dcc.Graph(figure=figure_locations_map)

])



if __name__== "__main__":
    app.run_server(debug=True)


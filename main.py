import dash
from dash import html, dash_table, dcc, Input, Output
import pandas as pd
import yfinance as yf
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import yagmail
import datetime



# Initialize the Dash app
app = dash.Dash(__name__)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read data from the CSV file
df_large_cap = pd.read_csv('large_cap_stocks.csv')
df_mid_cap = pd.read_csv('mid_cap_stocks.csv')

# Combine large and mid-cap stocks
df_screened_stocks = pd.concat([df_large_cap, df_mid_cap])

# Read data from the CSV file
df_portfolio = pd.read_csv('portfolio.csv')

#Read data from previous and current result CSV file
df_minervini_stocks = pd.read_csv('minervini_stocks.csv')
df_previous_results = pd.read_csv('previous_results.csv')
df_current_results = pd.read_csv('current_results.csv')

# Function to retrieve stock data from Yahoo Finance
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period='3y')  # Fetching historical data for the last three years

    # Check if the dataframe is empty (no data found)
    if df.empty:
        print(f"No stock data found for {ticker}")
        return None
    else:
        #print(f"Ok for {ticker}")
        return df
# Function to calculate Simple Moving Averages
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

# Define the layout of the app
app.layout = html.Div([

    # Header
    html.H1("Portfolio dashboard"),
    html.Br(),
    dbc.Accordion(
        dbc.AccordionItem(
            html.Table(
                # Header
                [html.Tr([html.Th("Condition - explanation")])]
                +
                # Body
                [
                    html.Tr(
                        [
                            html.Td(
                                "Condition 1:"
                            ),
                            html.Td(
                                "Current Price > 150 SMA and > 200 SMA"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 2:"
                            ),
                            html.Td(
                                "150 SMA > 200 SMA"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 3:"
                            ),
                            html.Td(
                                "200 SMA trending up for at least 1 month (ideally 4-5 months)"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 4:"
                            ),
                            html.Td(
                                "50 SMA> 150 SMA and 50 SMA> 200 SMA"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 5:"
                            ),
                            html.Td(
                                "Current Price > 50 SMA"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 6:"
                            ),
                            html.Td(
                                "Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)"
                            ),
                        ]),
                    html.Tr(
                        [
                            html.Td(
                                "Condition 7:"
                            ),
                            html.Td(
                                "Current Price is within 25% of 52 week high"
                            ),
                        ]),
                ]
            ),
        title="Minervini template - condition explanation",
        ),
        start_collapsed=True,
    ),

    html.Br(),
    html.H3("Table 1 - Portfolio Minervini check - details"),
    html.Br(),
    # Table for the portfolio
    dash_table.DataTable(
        id='portfolio-table',
        columns=[
            {'name': 'Ticker', 'id': 'ticker'},
            {'name': 'Stock', 'id': 'stock'},
            {'name': 'Condition 1', 'id': 'condition_1'},
            {'name': 'Condition 2', 'id': 'condition_2'},
            {'name': 'Condition 3', 'id': 'condition_3'},
            {'name': 'Condition 4', 'id': 'condition_4'},
            {'name': 'Condition 5', 'id': 'condition_5'},
            {'name': 'Condition 6', 'id': 'condition_6'},
            {'name': 'Condition 7', 'id': 'condition_7'},
        ],
        style_data_conditional=[
            {
                'if': {'column_id': col},
                'backgroundColor': 'green' if 'Green' in col else 'white',
            } for col in ['condition_1', 'condition_2', 'condition_3', 'condition_4', 'condition_5', 'condition_6', 'condition_7']
        ],
        style_cell={'textAlign': 'center'},
    ),
    html.Br(),
    html.H3("Table 2 - Portfolio only Minervini stocks"),
    html.Br(),
    dash_table.DataTable(
        id='portfolio-table2',
        columns=[
            {'name': 'Ticker', 'id': 'ticker'},
            {'name': 'Stock', 'id': 'stock'},
        ],
        style_cell={'textAlign': 'center'},

    ),
    html.Br(),
    html.H3("Table 3 - Portfolio check SMA200"),
    html.Br(),
    dash_table.DataTable(
        id='portfolio-table3',
        columns=[
            {'name': 'Ticker', 'id': 'ticker'},
            {'name': 'Stock', 'id': 'stock'},
            {'name': 'SMA200 condition', 'id': 'sma200_condition'},
            {'name': 'SMA200 Delta', 'id': 'percentage_difference'},
        ],
        style_data_conditional=[
        {
            'if': {
                'filter_query': '{sma200_condition} = Red',
                'column_id': 'sma200_condition'
            },
            'color': 'tomato'
        },
        ],
        style_cell={'textAlign': 'center'},

    ),
    html.Br(),
    html.Div([
    html.H5("SMA200 check Summary"),
    ], id='sma200-summary'),
    html.Br(),
    html.Div([

        # Button to start screening
        dbc.Button('Display portfolio graphs', id='start-screening-button', className="me-1"),

        # Button to start portfolio check
        dbc.Button('Start portfolio Minervini check', id='start-portfolio-check-button', className="me-2", color="primary", outline=True, style = {'margin-left': 20}),

        # Button to start stock screen
        dbc.Button('Display all portfolio stocks that fullfill all Minervini criterias',
                    id='start-stock-screen-button', className="me-1", style = {'margin-left': 20}),

        # Button to start stock screen
        dbc.Button('Display all Large & mid cap stocks that fullfill all Minervini criterias',
                    id='start-screening-large-mid-cap-button', className="me-1", color="primary", outline=True, style = {'margin-left': 20}),
        html.Br(),
        # Button to check if portfolio stocks are over or under SMA200
        dbc.Button('Check if portfolio stocks are over or under SMA200',
                    id='portfolio-SMA200-button', className="me-1",style = {'margin-top': 20}),

    ]),
    html.Br(),
    html.H3("Table 4 - All large & mid cap stocks that fullfill Minervini template"),
    html.Br(),
    # Table for screened Large & mid cap stocks that fullfill Minervini template
    dash_table.DataTable(
        id='screened-stocks',
        columns=[
            {'name': 'Ticker', 'id': 'ticker'},
            {'name': 'Stock', 'id': 'stock'},
        ],
    ),
    html.Br(),

    # Display changes in the summary
    html.Div([
    html.H5("Change Summary"),
    ], id='change-summary'),
    html.Div([
    html.H6("Mail")
    ], id='mail-text'),
    html.Br(),
    html.Div([
    # Button to display Minervini stocks in graph
    dbc.Button('Display Minervini stocks in graphs',
                id='minervini-graph-display-button', className="me-1"),
    dbc.Button('Send e-mail with list of Minervini stocks',
                   id='mail-button', className="me-1", style={'margin-left': 20}),
    ]),
    html.Br(),

            # Loading component for graphs, portfolio check, and stock screen
    dcc.Loading(
        id="loading-content",
        type="circle",  # You can change the type of the loading spinner (options: "circle", "default")
        children=[
            # Graphs for each stock with SMA50, SMA150, and SMA200
            html.Div([
                dcc.Graph(
                    id="graph",

                )
            ]),
        ],
    ),

    # Loading component for graphs, portfolio check, and stock screen
    dcc.Loading(
        id="loading-content2",
        type="circle",  # You can change the type of the loading spinner (options: "circle", "default")
        children=[
            # Graphs for each stock with SMA50, SMA150, and SMA200
            html.Div([
                dcc.Graph(
                    id=f"graph",

                )
            ]),
        ],
    ),

    # Additional components can be added here

], style = {'width': "90%", 'margin': "auto", 'padding-top':20} )


# Callback to update the loading spinner for graphs
@app.callback(
    Output("loading-content", "children", allow_duplicate=True),
    [Input("start-screening-button", "n_clicks")],
    prevent_initial_call=True
)
def update_loading_spinner_for_graphs(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    #if n_clicks is None or n_clicks == 0:
    #    return []  # No loading spinner when the button is not clicked
    else:
        return [dcc.Loading(
            id="loading-content",
            type="circle",
            children=[
                # Graphs for each stock with SMA50, SMA150, and SMA200
                html.Div([
                    dcc.Graph(
                        id=f"graph-{index}",
                        figure={
                            'data': [
                                {'x': get_stock_data(row['ticker']).index, 'y': get_stock_data(row['ticker']).Close, 'type': 'line', 'name': 'Closing Price'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 50), 'type': 'line', 'name': 'SMA50'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 150), 'type': 'line', 'name': 'SMA150'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 200), 'type': 'line', 'name': 'SMA200'},
                            ],
                            'layout': {
                                'title': f"Stock Data for {row['stock']} ({row['ticker']}) with SMAs",
                                'xaxis': {'title': 'Date'},
                                'yaxis': {'title': 'Stock Price'},
                            }
                        }
                    ) for index, row in df_portfolio.iterrows()
                ]),
            ],
        )]

# Callback to start portfolio check and update the table data
@app.callback(
    Output('portfolio-table', 'data', allow_duplicate=True),
    [Input("start-portfolio-check-button", "n_clicks")],
    prevent_initial_call=True
)
def start_portfolio_check(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    # Perform portfolio check
    results = []
    for index, row in df_portfolio.iterrows():
        stock_data = get_stock_data(row['ticker'])
        sma_50 = calculate_sma(stock_data, 50)
        sma_150 = calculate_sma(stock_data, 150)
        sma_200 = calculate_sma(stock_data, 200)

        condition_1 = stock_data['Close'].iloc[-1] > sma_150.iloc[-1] and stock_data['Close'].iloc[-1] > sma_200.iloc[-1]
        condition_2 = sma_150.iloc[-1] > sma_200.iloc[-1]
        # Check if there are enough data points for condition_3
        if len(sma_200) >= 21:
            condition_3 = all(
                sma_200.iloc[-i] > sma_200.iloc[-(i + 1)] for i in range(1, 21))  # Check for the last 20 days
        else:
            condition_3 = False

        condition_4 = sma_50.iloc[-1] > sma_150.iloc[-1] and sma_50.iloc[-1] > sma_200.iloc[-1]
        condition_5 = stock_data['Close'].iloc[-1] > sma_50.iloc[-1]
        condition_6 = stock_data['Close'].iloc[-1] >= 1.3 * stock_data['Low'].min()
        condition_7 = stock_data['Close'].iloc[-1] >= 0.75 * stock_data['High'].max()

        results.append({
            'stock': row['stock'],
            'condition_1': 'Green' if condition_1 else '-',
            'condition_2': 'Green' if condition_2 else '-',
            'condition_3': 'Green' if condition_3 else '-',
            'condition_4': 'Green' if condition_4 else '-',
            'condition_5': 'Green' if condition_5 else '-',
            'condition_6': 'Green' if condition_6 else '-',
            'condition_7': 'Green' if condition_7 else '-',
        })

    return results

# Callback to start stock screen and update the table data
@app.callback(
    Output('portfolio-table2', 'data', allow_duplicate=True),
    [Input("start-stock-screen-button", "n_clicks")],
    prevent_initial_call=True
)
def start_stock_screen(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    # Perform stock screen
    results = []
    for index, row in df_portfolio.iterrows():
        stock_data = get_stock_data(row['ticker'])
        sma_50 = calculate_sma(stock_data, 50)
        sma_150 = calculate_sma(stock_data, 150)
        sma_200 = calculate_sma(stock_data, 200)

        condition_1 = stock_data['Close'].iloc[-1] > sma_150.iloc[-1] and stock_data['Close'].iloc[-1] > sma_200.iloc[-1]
        condition_2 = sma_150.iloc[-1] > sma_200.iloc[-1]

        # Check if there are enough data points for condition_3
        if len(sma_200) >= 21:
            condition_3 = all(sma_200.iloc[-i] > sma_200.iloc[-(i + 1)] for i in range(1, 21))  # Check for the last 20 days
        else:
            condition_3 = False

        condition_4 = sma_50.iloc[-1] > sma_150.iloc[-1] and sma_50.iloc[-1] > sma_200.iloc[-1]
        condition_5 = stock_data['Close'].iloc[-1] > sma_50.iloc[-1]
        condition_6 = stock_data['Close'].iloc[-1] >= 1.3 * stock_data['Low'].min()
        condition_7 = stock_data['Close'].iloc[-1] >= 0.75 * stock_data['High'].max()

        # Check if all conditions are met
        if all([condition_1, condition_2, condition_3, condition_4, condition_5, condition_6, condition_7]):
            results.append({
                'ticker': row['ticker'],
                'stock': row['stock'],
            })

    return results

# Callback to update the loading spinner and screened stocks table data
@app.callback(
    [Output("loading-content", "children"),
     Output('screened-stocks', 'data'),
    Output('change-summary', 'children')
     ],
    [Input("start-screening-large-mid-cap-button", "n_clicks")],
    prevent_initial_call=True
)
def update_loading_spinner_and_screened_stocks_table(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    # Perform screening for large and mid-cap stocks
    results = []
    for index, row in df_screened_stocks.iterrows():

        stock_data = get_stock_data(row['ticker'])

        #avoid error messages when stock cannot be found
        if stock_data is not None:

            sma_50 = calculate_sma(stock_data, 50)
            sma_150 = calculate_sma(stock_data, 150)
            sma_200 = calculate_sma(stock_data, 200)

            condition_1 = stock_data['Close'].iloc[-1] > sma_150.iloc[-1] and stock_data['Close'].iloc[-1] > sma_200.iloc[-1]
            condition_2 = sma_150.iloc[-1] > sma_200.iloc[-1]

            # Check if there are enough data points for condition_3
            if len(sma_200) >= 21:
                condition_3 = all(sma_200.iloc[-i] > sma_200.iloc[-(i + 1)] for i in range(1, 21))  # Check for the last 20 days
            else:
                condition_3 = False

            condition_4 = sma_50.iloc[-1] > sma_150.iloc[-1] and sma_50.iloc[-1] > sma_200.iloc[-1]
            condition_5 = stock_data['Close'].iloc[-1] > sma_50.iloc[-1]
            condition_6 = stock_data['Close'].iloc[-1] >= 1.3 * stock_data['Low'].min()
            condition_7 = stock_data['Close'].iloc[-1] >= 0.75 * stock_data['High'].max()

            # Check if all conditions are met
            if all([condition_1, condition_2, condition_3, condition_4, condition_5, condition_6, condition_7]):
                results.append({
                    'ticker': row['ticker'],
                    'stock': row['stock'],
                })
    if results:
        df_results = pd.DataFrame(results)

        # Save current results to a global variable (if needed)
        df_current_results = df_results.copy()

        df_results.to_csv('current_results.csv', index=False)



        # Compare with previous results
    added_stocks = df_results[~df_results['ticker'].isin(df_previous_results['ticker'])]
    #print("Added stocks: ")
    #print(added_stocks)
    disappeared_stocks = df_previous_results[~df_previous_results['ticker'].isin(df_results['ticker'])]
    #print("Disappeared stocks: ")
    #print(disappeared_stocks)

    if results:
        df_results = pd.DataFrame(results)

        # Update the global variable df_current_results
        df_current_results = df_results.copy()

        # Save the current results to a CSV file
        df_results.to_csv('current_results.csv', index=False)

    # Display changes in the summary
    change_summary = html.Div([
        html.H5("Change Summary"),
        html.P(f"Added Stocks: {', '.join(added_stocks['ticker'])}" if not added_stocks.empty else "No stocks added."),
        html.P(f"Disappeared Stocks: {', '.join(disappeared_stocks['ticker'])}" if not disappeared_stocks.empty else "No stocks disappeared."),
    ])

    print("Previous result")
    print(df_previous_results)

    print("Current result")
    print(df_current_results)

    return [html.Div("..."), results , change_summary]

# Callback to update the loading spinner for graphs
@app.callback(
    Output("loading-content2", "children", allow_duplicate=True),
    [Input("minervini-graph-display-button", "n_clicks")],
    prevent_initial_call=True
)
def update_loading_spinner_for_graphs(n_clicks):
    #if n_clicks is None or n_clicks == 0:
    #    return []  # No loading spinner when the button is not clicked
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        # Load current results
        current_results = pd.read_csv("current_results.csv")

        # Save to previous results
        current_results.to_csv("previous_results.csv", index=False)

        return [dcc.Loading(
            id="loading-content2",
            type="circle",
            children=[
                # Graphs for each stock with SMA50, SMA150, and SMA200
                html.Div([
                    dcc.Graph(
                        id=f"graph-{index}",
                        figure={
                            'data': [
                                {'x': get_stock_data(row['ticker']).index, 'y': get_stock_data(row['ticker']).Close, 'type': 'line', 'name': 'Closing Price'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 50), 'type': 'line', 'name': 'SMA50'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 150), 'type': 'line', 'name': 'SMA150'},
                                {'x': get_stock_data(row['ticker']).index, 'y': calculate_sma(get_stock_data(row['ticker']), 200), 'type': 'line', 'name': 'SMA200'},
                            ],
                            'layout': {
                                'title': f"Stock Data for {row['stock']} ({row['ticker']}) with SMAs",
                                'xaxis': {'title': 'Date'},
                                'yaxis': {'title': 'Stock Price'},
                            }
                        }
                    #) for index, row in df_minervini_stocks.iterrows()
                    ) for index, row in df_current_results.iterrows()
                ]),
            ],
        )]

# Callback to check portfolio stocks and SMA200
@app.callback(
    [Output('portfolio-table3', 'data'),
    Output('sma200-summary', 'children', allow_duplicate=True),
     ],
    [Input("portfolio-SMA200-button", "n_clicks")],
    prevent_initial_call=True
)
def start_stock_screen(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    # Perform stock screen
    results = []
    for index, row in df_portfolio.iterrows():
        stock_data = get_stock_data(row['ticker'])
        sma_200 = calculate_sma(stock_data, 200)

        if stock_data['Close'].iloc[-1] > sma_200.iloc[-1]:
            results.append({
                    'ticker': row['ticker'],
                    'stock': row['stock'],
                    'sma200_condition': 'Ok',
            })
        else:
            results.append({
                'ticker': row['ticker'],
                'stock': row['stock'],
                'sma200_condition': 'Red',
            })

    #iterate through results df and calculate number / % of stocks over SMA200 and present result as HTML.DIV
    # Initialize counters
    df_result = pd.DataFrame(results, columns=['ticker', 'stock', 'sma200_condition', 'percentage_difference'])
    #print(df_result)
    ok_count = 0
    red_count = 0

    for index, row in df_result.iterrows():
        # Check the value in the "sma200_condition" column
        condition = row["sma200_condition"].strip().lower()

        # Update counters based on the condition
        if condition == "ok":
            ok_count += 1
        elif condition == "red":
            red_count += 1

    # Calculate the percentage of the portfolio over SMA200
    total_rows = len(df_result)
    percentage_over_sma200 = (ok_count / total_rows) * 100 if total_rows > 0 else 0

    # Iterate through results df and calculate percentage above/under SMA200 for each stock
    for index, row in df_result.iterrows():
        stock_data = get_stock_data(row['ticker'])
        sma_200 = calculate_sma(stock_data, 200)

        last_close_price = stock_data['Close'].iloc[-1]
        last_sma_200 = sma_200.iloc[-1]

        # Calculate the percentage difference
        percentage_difference = ((last_close_price - last_sma_200) / last_sma_200) * 100

        # Add the percentage_difference to the DataFrame
        df_result.at[index, 'percentage_difference'] = percentage_difference

    # Display the results
    #print(df_result)

    # Create a summary message with the additional information
    summary_components = [
        html.H5("Summary of SMA200 check"),
        html.P(f"Stocks over SMA200: {ok_count}" if ok_count > 0 else "No stocks over SMA200"),
        html.P(f"Stocks under SMA200: {red_count}" if red_count > 0 else "No stocks under SMA200"),
        html.P(
            f"In total {percentage_over_sma200:.2f}% of the portfolio is over SMA200" if total_rows > 0 else "No stocks in the portfolio"),
        #html.P(f"Percentage above/under SMA200 for each stock:")
    ]

    # Display the percentage difference for each stock in the summary
    #for index, row in df_result.iterrows():
    #    summary_components.append(html.P(f"{row['ticker']}: {row['percentage_difference']:.2f}%"))

    # Convert the list of components to an html.Div
    summary = html.Div(summary_components)

# start mail block
    #summary_components = html.Datalist
    current_datetime = datetime.datetime.now()
    str_date = current_datetime.strftime("%d-%m-%Y")
    body1 = df_result.to_html()
    body2 = summary_components

    EMAIL_ADDRESS1 = "mr.sven.mueller@gmail.com"
    EMAIL_ADDRESS2 = "super.toy.cars.media@gmail.com"
    EMAIL_PASSWORD = 'qdrwysjaacegaham'
    SUBJECT = "Result of the portfolio SMA200 check " + str_date
    #CONTENT = df_result.to_html() + summary_components
    body1 = body1.replace("\n", "")
    CONTENT = [body1, body2]
    try:
        # initializing the server connection
        yag = yagmail.SMTP(user=EMAIL_ADDRESS2, password=EMAIL_PASSWORD)

        # sending the email
        yag.send(to=EMAIL_ADDRESS1,
                 # subject='Result of current Minervini run',
                 subject=SUBJECT,
                 contents=CONTENT,
                 prettify_html=False)
        print("Mail ok")

    except:
        print("Error, email was not sent")

    # end mail block


    # Convert the list of components to an html.Div
    summary = html.Div(summary_components)

    # ... (rest of the code remains unchanged)

    return df_result.to_dict('records'), summary


# Callback to update the loading spinner and screened stocks table data
@app.callback(
    [Output('mail-text', 'children')],
    [Input("mail-button", "n_clicks")],
    prevent_initial_call=True
)
def update_loading_spinner_and_screened_stocks_table(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        # Load current results
        current_results = pd.read_csv("current_results.csv")

        # Save to previous results
        current_results.to_csv("previous_results.csv", index=False)

        df_current_results = pd.read_csv('current_results.csv')
        current_datetime = datetime.datetime.now()
        str_date = current_datetime.strftime("%d-%m-%Y")

        EMAIL_ADDRESS1 = "mr.sven.mueller@gmail.com"
        EMAIL_ADDRESS2 = "super.toy.cars.media@gmail.com"
        EMAIL_PASSWORD = 'qdrwysjaacegaham'
        SUBJECT = "Result of the Minervini run " + str_date
        body = df_current_results.to_html(classes='table table-stripped')
        CONTENT = body.replace("\n", "")
        try:
            # initializing the server connection
            yag = yagmail.SMTP(user=EMAIL_ADDRESS2, password=EMAIL_PASSWORD)

            # sending the email
            yag.send(to=EMAIL_ADDRESS1,
                     #subject='Result of current Minervini run',
                     subject=SUBJECT,
                     contents=CONTENT,
                     prettify_html=False)
            print("Mail ok")

        except:
            print("Error, email was not sent")

    return [html.H3("E-Mail successfully send")]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

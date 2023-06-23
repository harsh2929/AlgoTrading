import concurrent.futures
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from scipy import stats

IEX_CLOUD_API_TOKEN =
portfolio_size = 100000

def chunk_list(lst, n):

    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def fetch_stock_data(symbol):
    api_url = 
    data = requests.get(api_url).json()
    return symbol, data

def calculate_position_size(portfolio_size, stock_count):
    return portfolio_size / stock_count

def save_results_to_excel(dataframe, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name='Strategy', index=False)

    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    dollar_template = writer.book.add_format(
        {
            'num_format': '$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    integer_template = writer.book.add_format(
        {
            'num_format': '0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    percent_template = writer.book.add_format(
        {
            'num_format': '0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    column_formats = {
        'A': ['Ticker', string_template],
        'B': ['Price', dollar_template],
        'C': ['Number of Shares to Buy', integer_template],
        'D': ['Strategy', string_template],
        'E': ['Metric', string_template],
        'F': ['Weight', percent_template],
        'G': ['Score', percent_template]
    }

    for column in column_formats.keys():
        writer.sheets['Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
        writer.sheets['Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

    writer.save()


def run_trading_strategy(portfolio_size, strategy, stock_count):
    stocks = pd.read_csv('sp_500_stocks.csv')

    
    symbol_groups = chunk_list(stocks['Ticker'], 100)
    symbol_strings = []

    for symbol_group in symbol_groups:
        symbol_strings.append(','.join(symbol_group))

    my_columns = ['Ticker', 'Price', 'Number of Shares to Buy', 'Price-to-Earnings Ratio',
                  'One-Year Price Return', 'Six-Month Price Return', 'Three-Month Price Return',
                  'One-Month Price Return', 'Strategy']

    dataframe = pd.DataFrame(columns=my_columns)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(fetch_stock_data, symbol_strings)

        for result in results:
            symbol, data = result
            pe_ratio = data['quote']['peRatio']
            one_year_price_return = data['stats']['year1ChangePercent']
            six_month_price_return = data['stats']['month6ChangePercent']
            three_month_price_return = data['stats']['month3ChangePercent']
            one_month_price_return = data['stats']['month1ChangePercent']

            if strategy == 'value':
                score = 1 / pe_ratio
            elif strategy == 'growth':
                score = (one_year_price_return + six_month_price_return) / 2
            elif strategy == 'quality':
                score = (three_month_price_return + one_month_price_return) / 2
            elif strategy == 'momentum':
                score = one_month_price_return

            dataframe = dataframe.append(
                pd.Series([symbol, data['quote']['latestPrice'], 'N/A', pe_ratio,
                           one_year_price_return, six_month_price_return, three_month_price_return,
                           one_month_price_return, strategy],
                          index=my_columns),
                ignore_index=True
            )

    dataframe.sort_values('Ticker', inplace=True)
    dataframe.reset_index(drop=True, inplace=True)

    position_size = calculate_position_size(portfolio_size, stock_count)
    for i in range(len(dataframe)):
        dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / dataframe['Price'][i])

    return dataframe

value_strategy = run_trading_strategy(portfolio_size, 'value', 50)
growth_strategy = run_trading_strategy(portfolio_size, 'growth', 50)
quality_strategy = run_trading_strategy(portfolio_size, 'quality', 50)
momentum_strategy = run_trading_strategy(portfolio_size, 'momentum', 50)

save_results_to_excel(value_strategy, 'value_strategy.xlsx')
save_results_to_excel(growth_strategy, 'growth_strategy.xlsx')
save_results_to_excel(quality_strategy, 'quality_strategy.xlsx')
save_results_to_excel(momentum_strategy, 'momentum_strategy.xlsx')

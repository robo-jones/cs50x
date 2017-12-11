import requests
import re
from bs4 import BeautifulSoup
from datetime import date as Date, datetime, timedelta

# scrapes Yahoo! Finance for historical data on a given symbol. Used to construct the training set
def get_training_data(symbol, sp500_price_table, today, minus_5_years):

    balance_sheet = BeautifulSoup(requests.get('https://finance.yahoo.com/quote/{}/balance-sheet'.format(symbol)).content, 'html.parser')
    balance_nodes = [node.get_text() for node in balance_sheet.find(id='Col1-3-Financials-Proxy').tbody.find_all('td')]
    cash_flow = BeautifulSoup(requests.get('https://finance.yahoo.com/quote/{}/cash-flow'.format(symbol)).content, 'html.parser')
    cash_nodes = [node.get_text() for node in cash_flow.find(id='Col1-3-Financials-Proxy').tbody.find_all('td')]
    prices = BeautifulSoup(requests.get('https://finance.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1mo&filter=history&frequency=1mo'.format(symbol, int(minus_5_years.timestamp()), int(today.timestamp()))).content, 'html.parser')
    price_table = prices.find(id='Col1-3-HistoricalDataTable-Proxy').tbody

    # convert '-' characters into zeroes, strip commas from numbers and cast everything but dates to integers
    date_pattern = re.compile('\d*/\d*/\d*')
    for i in range(len(balance_nodes)):
        if balance_nodes[i] == '-':
            balance_nodes[i] = 0
        elif not balance_nodes[i][0].isalpha() and not date_pattern.match(balance_nodes[i]):
            balance_nodes[i] = int(balance_nodes[i].replace(',', ''))

    for i in range(len(cash_nodes)):
        if cash_nodes[i] == '-':
            cash_nodes[i] = 0
        elif not cash_nodes[i][0].isalpha() and not date_pattern.match(cash_nodes[i]):
            cash_nodes[i] = int(cash_nodes[i].replace(',', ''))

    # take the human-formatted dates, convert to a python date object, and advance them to the end of the month (prevents errors when looking up prices)
    dates = []
    raw_dates = [balance_nodes[1], balance_nodes[2], balance_nodes[3]]
    for raw_date in raw_dates:
        m_d_y = raw_date.split('/')
        date = Date(int(m_d_y[2]), int(m_d_y[0]), int(m_d_y[1]))
        while (date + timedelta(days=1)).month == date.month:
            date += timedelta(days=1)
        dates.append(date)

    # retrieve necessary data from the scraped webpages
    index = balance_nodes.index('Total Current Assets') + 1
    current_assets = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Current Liabilities') + 1
    current_liabilities = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Stockholder Equity') + 1
    total_equity = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Liabilities') + 1
    total_liabilities = balance_nodes[index:index + 3]

    index = cash_nodes.index('Net Income') + 1
    net_income = cash_nodes[index:index + 3]
    index = cash_nodes.index('Total Cash Flow From Operating Activities') + 1
    cash_flow_operations = cash_nodes[index:index + 3]
    index = cash_nodes.index('Capital Expenditures') + 1
    capital_expenditures = cash_nodes[index:index + 3]
    index = cash_nodes.index('Dividends Paid') + 1
    dividends_paid = cash_nodes[index:index + 3]


    # find closing price and S&P500 closing price for each date in yearly balance sheet
    closing_prices = []
    sp500_closing_prices = []
    for date in dates:
        # end-of-month prices are either posted on the last day of that month, or the first day of the following month
        # this block first tries the end of the month, and if that throws an error, then tries the beginning of the next
        try:
            price = price_table.find('span', string=date.strftime('%b %d, %Y')).parent.find_next_siblings(limit=5)[4].get_text().replace(',', '')
            closing_prices.append(float(price))
            sp500_price = sp500_price_table.find('span', string=date.strftime('%b %d, %Y')).parent.find_next_siblings(limit=5)[4].get_text().replace(',', '')
            sp500_closing_prices.append(float(sp500_price))
        except:
            new_date = date + timedelta(days=1)
            price = price_table.find('span', string=new_date.strftime('%b %d, %Y')).parent.find_next_siblings(limit=5)[4].get_text().replace(',', '')
            closing_prices.append(float(price))
            sp500_price = sp500_price_table.find('span', string=new_date.strftime('%b %d, %Y')).parent.find_next_siblings(limit=5)[4].get_text().replace(',', '')
            sp500_closing_prices.append(float(sp500_price))

    # calculate the fractional change in price and S&P500 price from last year to this year
    price_change = (closing_prices[0] - closing_prices[1]) / closing_prices[1]
    sp500_price_change = (sp500_closing_prices[0] - sp500_closing_prices[1]) / sp500_closing_prices[1]

    ''' Calculated Values '''
    # the stock's performance relative to the S&P500
    performance = price_change - sp500_price_change

    # various fundamental parameters
    working_capital_ratio = current_assets[1] / current_liabilities[1]
    working_capital_change = ((current_assets[1] - current_liabilities[1]) - (current_assets[2] - current_liabilities[2])) / (current_assets[2] - current_liabilities[2])
    return_on_equity = net_income[1] / total_equity[1]
    return_on_equity_change = ((net_income[1] / total_equity[1]) - (net_income[2] / total_equity[2])) / (net_income[2] / total_equity[2])
    debt_to_equity = total_liabilities[1] / total_equity[1]
    debt_to_equity_change = ((total_liabilities[1] / total_equity[1]) - (total_liabilities[2] / total_equity[2])) / (total_liabilities[2] / total_equity[2])
    comprehensive_free_cash_flow = (cash_flow_operations[1] + capital_expenditures[1] - dividends_paid[1]) / cash_flow_operations[1]
    free_cash_flow_change = ((cash_flow_operations[1] + capital_expenditures[1] - dividends_paid[1]) - (cash_flow_operations[2] + capital_expenditures[2] - dividends_paid[2])) / (cash_flow_operations[2] + capital_expenditures[2] - dividends_paid[2])
    earnings_growth = (net_income[1] - net_income[2]) / net_income[2]

    # Collect the data into a dictionary and return it
    training_data = {
        'Performance': performance,
        'Return on Equity': return_on_equity,
        'Return on Equity Change': return_on_equity_change,
        'Working Capital Ratio': working_capital_ratio,
        'Working Capital Change': working_capital_change,
        'Debt to Equity': debt_to_equity,
        'Debt to Equity Change': debt_to_equity_change,
        'Comprehensive Free Cash Flow': comprehensive_free_cash_flow,
        'Free Cash Flow Change': free_cash_flow_change,
        'Earnings Growth': earnings_growth
    }

    return training_data


# scrape and calculate current year's data for a given stock symbol from Yahoo! finance
def get_financials(symbol):

    balance_sheet = BeautifulSoup(requests.get('https://finance.yahoo.com/quote/{}/balance-sheet'.format(symbol)).content, 'html.parser')
    balance_nodes = [node.get_text() for node in balance_sheet.find(id='Col1-3-Financials-Proxy').tbody.find_all('td')]
    cash_flow = BeautifulSoup(requests.get('https://finance.yahoo.com/quote/{}/cash-flow'.format(symbol)).content, 'html.parser')
    cash_nodes = [node.get_text() for node in cash_flow.find(id='Col1-3-Financials-Proxy').tbody.find_all('td')]

    # convert '-' characters into zeroes, strip commas from numbers and cast everything but dates to integers
    date_pattern = re.compile('\d*/\d*/\d*')
    for i in range(len(balance_nodes)):
        if balance_nodes[i] == '-':
            balance_nodes[i] = 0
        elif not balance_nodes[i][0].isalpha() and not date_pattern.match(balance_nodes[i]):
            balance_nodes[i] = int(balance_nodes[i].replace(',', ''))

    for i in range(len(cash_nodes)):
        if cash_nodes[i] == '-':
            cash_nodes[i] = 0
        elif not cash_nodes[i][0].isalpha() and not date_pattern.match(cash_nodes[i]):
            cash_nodes[i] = int(cash_nodes[i].replace(',', ''))

    # retrieve necessary data from the scraped webpages
    index = balance_nodes.index('Total Current Assets') + 1
    current_assets = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Current Liabilities') + 1
    current_liabilities = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Stockholder Equity') + 1
    total_equity = balance_nodes[index:index + 3]
    index = balance_nodes.index('Total Liabilities') + 1
    total_liabilities = balance_nodes[index:index + 3]

    index = cash_nodes.index('Net Income') + 1
    net_income = cash_nodes[index:index + 3]
    index = cash_nodes.index('Total Cash Flow From Operating Activities') + 1
    cash_flow_operations = cash_nodes[index:index + 3]
    index = cash_nodes.index('Capital Expenditures') + 1
    capital_expenditures = cash_nodes[index:index + 3]
    index = cash_nodes.index('Dividends Paid') + 1
    dividends_paid = cash_nodes[index:index + 3]

    # Calculate the various fundamental parameters
    working_capital_ratio = current_assets[0] / current_liabilities[0]
    working_capital_change = ((current_assets[0] - current_liabilities[0]) - (current_assets[1] - current_liabilities[1])) / (current_assets[1] - current_liabilities[1])
    return_on_equity = net_income[0] / total_equity[0]
    return_on_equity_change = ((net_income[0] / total_equity[0]) - (net_income[1] / total_equity[1])) / (net_income[1] / total_equity[1])
    debt_to_equity = total_liabilities[0] / total_equity[0]
    debt_to_equity_change = ((total_liabilities[0] / total_equity[0]) - (total_liabilities[1] / total_equity[1])) / (total_liabilities[1] / total_equity[1])
    comprehensive_free_cash_flow = (cash_flow_operations[0] + capital_expenditures[0] - dividends_paid[0]) / cash_flow_operations[0]
    free_cash_flow_change = ((cash_flow_operations[0] + capital_expenditures[0] - dividends_paid[0]) - (cash_flow_operations[1] + capital_expenditures[1] - dividends_paid[1])) / (cash_flow_operations[1] + capital_expenditures[1] - dividends_paid[1])
    earnings_growth = (net_income[0] - net_income[1]) / net_income[1]

    # collect the data into a dictionary and return it
    financial_data = {
        'Return on Equity': return_on_equity,
        'Return on Equity Change': return_on_equity_change,
        'Working Capital Ratio': working_capital_ratio,
        'Working Capital Change': working_capital_change,
        'Debt to Equity': debt_to_equity,
        'Debt to Equity Change': debt_to_equity_change,
        'Comprehensive Free Cash Flow': comprehensive_free_cash_flow,
        'Free Cash Flow Change': free_cash_flow_change,
        'Earnings Growth': earnings_growth
    }

    return financial_data
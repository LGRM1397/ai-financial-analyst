
# -*- coding: utf-8 -*-

import yfinance as yf
from yahooquery import search
from gpt_summary import generate_gpt_portfolio_insight


# Validate tickers and weights
def validate_portfolio_inputs(tickers, weights):
    if not tickers or not weights:
        return False, "Tickers and weights cannot be empty."
    if len(tickers) != len(weights):
        return False, "The number of tickers must match the number of weights."
    if not all(isinstance(w, (int, float)) for w in weights):
        return False, "All weights must be numbers."
    if not 0.99 <= sum(weights) <= 1.01:
        return False, "Weights must sum to approximately 1.0 (100%)."
    return True, "Inputs are valid."

# Fetch basic financial info for each ticker
def fetch_portfolio_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "Name": info.get("longName") or info.get("shortName", "N/A"),
            "Ticker": ticker.upper(),
            "Country": info.get("country", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "PE": info.get("trailingPE", 0),
            "PB": info.get("priceToBook", 0),
            "ROE": info.get("returnOnEquity", 0),
            "Beta": info.get("beta", 0),
            "Debt/Equity": info.get("debtToEquity", 0)
           
        }
    except Exception as e:
        return None

    # generates GPT Insights based on user portfolio
def generate_portfolio_insight(df):
    return generate_gpt_portfolio_insight(df)



def get_portfolio_sector_weights(df):
    sector_weights = df.groupby("Sector")["Weight"].sum() * 100  # converts to %
    return sector_weights.to_dict()




def resolve_to_ticker(name_or_symbol):
    """
    Resolve user input (ticker or company name) into a valid stock ticker.
    """
    name_or_symbol = name_or_symbol.strip().upper()

    # Try if it's a valid ticker directly
    try:
        stock = yf.Ticker(name_or_symbol)
        if stock.info.get("shortName"):
            return name_or_symbol
    except:
        pass

    # Try searching by company name
    try:
        result = search(name_or_symbol)
        if result.get("quotes"):
            return result["quotes"][0]["symbol"]
    except:
        pass

    return None


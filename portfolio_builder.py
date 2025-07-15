import pandas as pd
from gpt_summary import generate_ai_portfolio_summary
from portfolio_utils import fetch_portfolio_data
from finance_utils import get_stocks_by_risk_profile
from news_utils import get_news_for_portfolio
from utils import format_number

def build_ai_portfolio(capital, preferences):
    risk = preferences["risk_level"]
    num_stocks = preferences.get("num_stocks")
    sectors = preferences.get("sectors", [])
    countries = preferences.get("countries", [])

    # Use dynamic stock selection based on risk and desired number of stocks
    # If num_stocks is None, default to 10
    tickers = get_stocks_by_risk_profile(risk, limit=num_stocks or 10)

    # If no tickers were returned, stop and show message
    if not tickers:
        return pd.DataFrame(), "No tickers available for this risk level."

    # Calculate equal allocation for each selected stock
    allocation = 1 / len(tickers)
    results = []

    for ticker in tickers:
        data = fetch_portfolio_data(ticker)
        if not isinstance(data, dict):
            continue

        invested = round(capital * allocation, 2)
        results.append({
            "Ticker": ticker,
            "Company": data.get("Name", "N/A"),
            "Sector": data.get("Sector", "N/A"),
            "Country": data.get("Country", "USA"),
            "Allocation %": format_number(allocation, style="percent"),
            "Investment (USD)": format_number(invested, style="usd"),
            "PE": format_number(data.get("PE"), style="ratio"),
            "ROE": format_number(data.get("ROE"), style="percent"),
            "Beta": format_number(data.get("Beta"), style="ratio"),
        })

    df = pd.DataFrame(results)

    # Get recent news for the selected tickers
    news_dict = get_news_for_portfolio(tickers)

    # Generate GPT summary using portfolio and preferences
    summary = generate_ai_portfolio_summary(df, capital, risk, sectors, countries, news_dict)

    return df, summary


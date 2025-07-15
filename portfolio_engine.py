from portfolio_utils import fetch_portfolio_data
import pandas as pd
from utils import format_number

def analyze_portfolio(ticker_list, allocations=None):
    """
    Analyze a portfolio of stocks.
    """
    portfolio_summary = {
        "Company": [],
        "Ticker": [],
        "Country": [],
        "Sector": [],
        "Industry": [],
        "PE": [],
        "PB": [],
        "ROE": [],
        "Beta": [],
        "Debt/Equity": [],
        "Weight": []
    }

    if allocations is None:
        allocations = [1 / len(ticker_list)] * len(ticker_list)

    for ticker, weight in zip(ticker_list, allocations):
        data = fetch_portfolio_data(ticker)
        if not isinstance(data, dict):
            continue  # Skip if data fetch failed or malformed

        portfolio_summary["Company"].append(data.get("Name", "N/A"))
        portfolio_summary["Ticker"].append(ticker)
        portfolio_summary["Country"].append(data.get("Country", "N/A"))
        portfolio_summary["Sector"].append(data.get("Sector", "N/A"))
        portfolio_summary["Industry"].append(data.get("Industry", "N/A"))
        portfolio_summary["PE"].append(data.get("PE", 0))
        portfolio_summary["PB"].append(data.get("PB", 0))
        portfolio_summary["ROE"].append(data.get("ROE", 0))
        portfolio_summary["Beta"].append(data.get("Beta", 0))
        portfolio_summary["Debt/Equity"].append(data.get("Debt/Equity", 0) / 100)
        portfolio_summary["Weight"].append(weight)
    
    df = pd.DataFrame(portfolio_summary)
    df["Weight"] = df["Weight"].astype(float)

    # Calculate weighted averages
    weighted_summary = {
        "PE (weighted avg)": (df["PE"] * df["Weight"]).sum(),
        "PB (weighted avg)": (df["PB"] * df["Weight"]).sum(),
        "ROE (weighted avg)": (df["ROE"] * df["Weight"]).sum(),
        "Beta (weighted avg)": (df["Beta"] * df["Weight"]).sum(),
        "Debt/Equity (avg)": (df["Debt/Equity"] * df["Weight"]).sum()
    }

    # Format DataFrame columns
    df["PE"] = df["PE"].apply(lambda x: format_number(x, style="ratio"))
    df["PB"] = df["PB"].apply(lambda x: format_number(x, style="ratio"))
    df["ROE"] = df["ROE"].apply(lambda x: format_number(x, style="percent"))
    df["Beta"] = df["Beta"].apply(lambda x: format_number(x, style="ratio"))
    df["Debt/Equity"] = df["Debt/Equity"].apply(lambda x: format_number(x, style="percent"))
    df["Weight"] = df["Weight"].apply(lambda x: format_number(x, style="percent"))

    # Format weighted averages
    formatted_summary = {
        "PE (weighted avg)": format_number(weighted_summary["PE (weighted avg)"], style="ratio"),
        "PB (weighted avg)": format_number(weighted_summary["PB (weighted avg)"], style="ratio"),
        "ROE (weighted avg)": format_number(weighted_summary["ROE (weighted avg)"], style="percent"),
        "Beta (weighted avg)": format_number(weighted_summary["Beta (weighted avg)"], style="ratio"),
        "Debt/Equity (avg)": format_number(weighted_summary["Debt/Equity (avg)"], style="percent")
    }

    # Reorder columns for display
    df = df[["Company", "Ticker","Country", "Sector", "Industry", "PE", "PB", "ROE", "Beta", "Debt/Equity", "Weight"]]

    return df, formatted_summary

import yfinance as yf  # This lets us get financial data from the internet
import random  # This is used to randomly select stocks

# Gets general financial data for a company
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "shortName": info.get("shortName"),
        "sector": info.get("sector"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "returnOnEquity": info.get("returnOnEquity"),
        "debtToEquity": info.get("debtToEquity"),
        "grossMargins": info.get("grossMargins"),
        "revenue": info.get("totalRevenue"),
        "netIncome": info.get("netIncomeToCommon"),
        "operatingMargin": info.get("operatingMargins"),
        "ebitda": info.get("ebitda"),
        "returnOnAssets": info.get("returnOnAssets")
    }

# Gets recent revenue history (quarterly)
def get_revenue_history(ticker):
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.quarterly_financials
        if "Total Revenue" not in income_stmt.index:
            return None
        revenue_series = income_stmt.loc["Total Revenue"]
        return revenue_series[::-1]  # Oldest to newest
    except Exception:
        return None

# Gets the most recent closing price
def get_closing_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist["Close"].iloc[-1]
    except Exception:
        return None

# Gets analyst price targets
def get_analyst_price_targets(ticker):
    try:
        stock = yf.Ticker(ticker)
        recs = stock.recommendations
        if recs is not None and not recs.empty:
            info = stock.info
            return {
                "targetLow": info.get("targetLowPrice"),
                "targetHigh": info.get("targetHighPrice"),
                "targetMean": info.get("targetMeanPrice"),
                "targetMedian": info.get("targetMedianPrice")
            }
        return None
    except Exception:
        return None

# Calculates PEG Ratio using forward PE and 5-year earnings growth estimate
def get_peg_ratio(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        peg = info.get("trailingPegRatio", None)  # Use the available key
        print(f"[PEG DEBUG] Raw PEG from Yahoo: {peg}")
        return round(peg, 2) if peg is not None else None

    except Exception as e:
        print(f"[PEG ERROR] {e}")
        return None


def get_sp500_tickers_from_etf():
    try:
        spy = yf.Ticker("SPY")
        holdings = spy.fund_holdings
        if holdings is not None and not holdings.empty:
            return holdings["Symbol"].tolist()
    except:
        pass
    # Fallback if SPY holdings fail
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "JPM", "JNJ", "V", "PG",
        "UNH", "HD", "MA", "KO", "PEP", "WMT", "CVX", "XOM", "BAC", "ORCL",
        "PFE", "VZ", "ABBV", "T", "MRK", "META", "INTC", "CRM", "NFLX", "QCOM"
    ]

def get_stocks_by_risk_profile(risk_level, limit):
    """
    Dynamically fetch stocks from SPY ETF and classify by beta.
    """
    sp500_tickers = get_sp500_tickers_from_etf()
    classified = {"Low": [], "Medium": [], "High": []}

    for ticker in sp500_tickers:
        try:
            info = yf.Ticker(ticker).info
            beta = info.get("beta")
            if beta is None:
                continue
            if beta < 0.9:
                classified["Low"].append(ticker)
            elif 0.9 <= beta <= 1.3:
                classified["Medium"].append(ticker)
            else:
                classified["High"].append(ticker)
        except:
            continue

    return random.sample(classified.get(risk_level, []), k=min(limit, len(classified.get(risk_level, []))))
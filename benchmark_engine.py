# benchmark_engine.py

import yfinance as yf
from benchmark_etfs import benchmark_map, SP500_SECTOR_WEIGHTS
import streamlit as st
from utils import format_number

@st.cache_data(ttl=3600)
def get_benchmark_metrics(sector):
    etf_ticker = benchmark_map.get(sector, "SPY")
    etf = yf.Ticker(etf_ticker)
    info = etf.info

    return {
        "Benchmark": etf_ticker,
        "Name": info.get("shortName", etf_ticker),
        "PE": format_number(info.get("trailingPE"), style="ratio"),
        "PB": format_number(info.get("priceToBook"), style="ratio"),
        "ROE": format_number(info.get("returnOnEquity"), style="percent")
}


def compare_sector_allocation(portfolio_sector_weights):
    insights = []

    for sector, port_weight in portfolio_sector_weights.items():
        # Handle string percentages like "28.1%"
        if isinstance(port_weight, str):
            port_weight = port_weight.replace("%", "").strip()
            try:
                port_weight = float(port_weight)
            except ValueError:
                port_weight = 0.0  # fallback if it can't be converted

        benchmark_weight = SP500_SECTOR_WEIGHTS.get(sector, 0.0)
        diff = port_weight - benchmark_weight

        if diff > 5:
            insights.append(f"Overexposed to {sector} (+{diff:.1f}% vs S&P 500)")
        elif diff < -5:
            insights.append(f"Underexposed to {sector} ({diff:.1f}% vs S&P 500)")

    if not insights:
        return "Your sector allocation closely matches the S&P 500 benchmark."
    
    return " | ".join(insights)


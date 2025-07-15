

# Benchmark ETFs for different sectors in app UI for each company
benchmark_map = {
    "Technology": "XLK",        # Technology Select Sector SPDR Fund
    "Financial Services": "XLF",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Healthcare": "XLV",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Communication Services": "XLC",
    "Broad Market": "SPY"       # Fallback
}

# Portfolio builder insight (Must change to live data later)

SP500_SECTOR_WEIGHTS = {
    "Technology": 28.1,
    "Healthcare": 13.0,
    "Financials": 11.0,
    "Consumer Cyclical": 10.5,
    "Communication Services": 8.8,
    "Industrials": 7.9,
    "Consumer Defensive": 6.6,
    "Energy": 4.4,
    "Utilities": 2.6,
    "Materials": 2.5,
    "Real Estate": 2.3
}
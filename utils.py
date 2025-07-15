
import yfinance as yf
import streamlit as st



# ========== Formatting Helpers ==========

def format_number(value, style="usd"):
    if value is None:
        return "N/A"

    try:
        if style == "usd":
            return f"${round(value, 2):,}" if isinstance(value, (int, float)) else value
        elif style == "percent":
            return f"{round(value * 100, 2)}%" if isinstance(value, (int, float)) else value
        elif style == "ratio":
            return f"{round(value, 2)}" if isinstance(value, (int, float)) else value
        else:
            return str(value)
    except:
        return "N/A"
    # === Clean text of special characters (for GPT or online data) ===
def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")

# === Remove company suffixes (like Inc., Corp.) for better matching ===
def clean_company_name(name):
    suffixes = ['(The)', 'Inc.', 'Corp.', 'Corporation', 'Ltd.', 'S.A.', 'LLC']
    for s in suffixes:
        name = name.replace(s, "")
    return name.strip()

# === Global Styling for Streamlit App ===
def style_ui():
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  {
            font-family: 'Arial', sans-serif !important;
            font-size: 16px !important;
        }
        .stMarkdown, .stText, .stSubheader {
            margin-bottom: 10px !important;
        }
        .stSubheader {
            margin-top: 25px !important;
            font-weight: bold !important;
        }
        .stMetric {
            font-size: 18px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # === Display a formatted financial metric with consistent layout ===
def render_metric(label, value):
    st.markdown(f"<p style='margin-bottom: 0.2rem;'><strong>{label}:</strong> {value}</p>", unsafe_allow_html=True)

def render_grouped_metrics(data, closing_price):
    st.subheader("Key Financial Metrics")

    # First row of columns
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric("Sector", data.get("sector"))
        render_metric("Market Cap", format_number(data.get("marketCap")))
        if closing_price:
            render_metric("Closing Price", format_number(closing_price, style="usd"))

    with col2:
        render_metric("Trailing PE", format_number(data.get("trailingPE"), style="usd"))
        render_metric("Forward PE", format_number(data.get("forwardPE"), style="usd"))
        render_metric("ROE", format_number(data.get("returnOnEquity"), style="percent"))

    with col3:
        render_metric("Debt/Equity", format_number(data.get("debtToEquity"), style="ratio"))
        render_metric("Gross Margin", format_number(data.get("grossMargins"), style="percent"))
        render_metric("Revenue", format_number(data.get("revenue")))

    # Second row of columns
    col4, col5, col6 = st.columns(3)
    with col4:
        render_metric("Net Income", format_number(data.get("netIncome")))
    with col5:
        render_metric("EBITDA", format_number(data.get("ebitda")))
    with col6:
        render_metric("Operating Margin", format_number(data.get("operatingMargin"), style="percent"))

    col7, _, _ = st.columns(3)
    with col7:
        render_metric("Return on Assets", format_number(data.get("returnOnAssets"), style="percent"))

def get_logo_url(ticker: str) -> str:
    try:
        ticker_data = yf.Ticker(ticker)
        info = ticker_data.info
        logo_url = info.get("logo_url", "")
        
        # Fallback to fast_info if needed
        if not logo_url:
            logo_url = ticker_data.fast_info.get("logo_url", "")

        # If still empty, return a generic placeholder
        if not logo_url:
            return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
        
        return logo_url

    except Exception as e:
        print(f"Error fetching logo for {ticker}: {e}")
        return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
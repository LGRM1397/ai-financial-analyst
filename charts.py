import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def display_stock_price_chart(ticker, clean_name):
    st.subheader("Stock Price Chart")

    # Let user select time range with session state persistence
    if "time_range" not in st.session_state:
        st.session_state.time_range = "1Y"

    st.session_state.time_range = st.selectbox(
        "Select time range",
        ["1M", "6M", "1Y", "5Y", "YTD", "MAX"],
        index=["1M", "6M", "1Y", "5Y", "YTD", "MAX"].index(st.session_state.time_range)
    )

    # Assign local variable for convenience
    time_range = st.session_state.time_range

    # Mapping for yfinance period/intervals
    range_map = {
        "1M": ("1mo", "1d"),
        "6M": ("6mo", "1d"),
        "1Y": ("1y", "1d"),
        "5Y": ("5y", "1wk"),
        "YTD": ("ytd", "1d"),
        "MAX": ("max", "1mo"),
    }

    selected_period, selected_interval = range_map[time_range]

    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period=selected_period, interval=selected_interval)

        if hist_data.empty:
            st.warning("Historical price data not available.")
            return

        # Plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data["Close"],
            name="Closing Price",
            line=dict(color="royalblue", width=2)
        ))

        fig.update_layout(
            title=f"{clean_name} ({ticker}) Stock Price - {time_range}",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching historical chart: {e}")

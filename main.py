# -*- coding: utf-8 -*-
# main.py

# Core libraries
import pandas as pd
import streamlit as st
import yfinance as yf
from io import BytesIO
import matplotlib.pyplot as plt

# Custom modules 
from finance_utils import get_peg_ratio, get_stock_info, get_analyst_price_targets
from gpt_summary import generate_summary
from utils import format_number, clean_company_name, style_ui, clean_text, render_grouped_metrics
from news_utils import get_company_news_finnhub, summarize_news_article, get_news_for_portfolio
from benchmark_engine import get_benchmark_metrics, compare_sector_allocation
from charts import display_stock_price_chart
from watchlist_utils import init_watchlist, display_watchlist_sidebar, add_to_watchlist_button
from docx_exporter import generate_word_report
from portfolio_engine import analyze_portfolio
from portfolio_utils import generate_portfolio_insight, get_portfolio_sector_weights, resolve_to_ticker
from portfolio_builder import build_ai_portfolio

st.set_page_config(page_title="My AI Financial Analyst")
st.title("My AI Financial Analyst")

style_ui()
init_watchlist()
display_watchlist_sidebar()

with st.expander("Analyze a Company", expanded=True):
    st.write("Enter a company name or ticker (e.g., Apple or AAPL).")
    st.info("For international stocks, use the full ticker (e.g., CIB for Bancolombia).")

    tickers_df = pd.read_csv("tickers.csv")

    search_query = st.text_input("Search for a company or ticker:")

    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None
    if "run_analysis" not in st.session_state:
        st.session_state.run_analysis = False

    def match_ticker(query):
        query = query.strip().lower()
        tickers_df["Security_clean"] = tickers_df["Security"].str.lower()
        matches = tickers_df[tickers_df["Security_clean"].str.contains(query)]
        return matches[["Security", "Symbol"]].values.tolist()

    if search_query:
        suggestions = match_ticker(search_query)
        if suggestions:
            st.markdown("Did you mean:")
            for name, symbol in suggestions[:5]:
                if st.button(f"{name} ({symbol})", key=f"suggestion_btn_{symbol}"):
                    st.session_state.selected_ticker = symbol
                    st.session_state.run_analysis = True
                    st.rerun()

    if st.button("Analyze", key="analyze_button"):
        if search_query:
            possible_ticker = search_query.strip().upper()
            try:
                ticker_obj = yf.Ticker(possible_ticker)
                info = ticker_obj.info
                if info and info.get("shortName"):
                    st.session_state.selected_ticker = possible_ticker
                    st.session_state.run_analysis = True
                    st.rerun()
                else:
                    matches = match_ticker(search_query)
                    if matches:
                        st.session_state.selected_ticker = matches[0][1]
                        st.session_state.run_analysis = True
                        st.rerun()
                    else:
                        st.warning("Could not find a valid ticker or match for that name.")
            except Exception as e:
                st.warning(f"Could not fetch data for that ticker. Error: {e}")
with st.expander("Analysis Results", expanded = st.session_state.run_analysis):
    if st.session_state.run_analysis and st.session_state.selected_ticker:
        final_ticker = st.session_state.selected_ticker

        with st.spinner("Fetching data..."):
            data = get_stock_info(final_ticker)

        if data:
            try:
                hist = yf.Ticker(final_ticker).history(period="1d")
                closing_price = hist["Close"].iloc[-1] if not hist.empty else None
            except:
                closing_price = None

            clean_name = clean_company_name(data.get("shortName", ""))
            st.subheader(f"Company: {clean_name} ({final_ticker})")

            if st.button("Close Analysis"):
                st.session_state.run_analysis = False
                st.session_state.selected_ticker = None
                st.rerun()

            add_to_watchlist_button(final_ticker)
            render_grouped_metrics(data, closing_price)

            peg = get_peg_ratio(final_ticker)
            if peg is not None:
                st.write(f"PEG Ratio: {peg}")
                if peg < 1:
                    st.success("This stock may be undervalued relative to growth.")
                elif 1 <= peg <= 2:
                    st.info("Fairly valued relative to growth.")
                else:
                    st.warning("This stock may be overvalued relative to growth.")
            else:
                st.write("PEG ratio not available.")

            st.subheader("Benchmark Comparison (Sector ETF)")
            sector = data.get("sector", "Unknown")
            benchmark = get_benchmark_metrics(sector)
            if benchmark:
                st.write(f"ETF Benchmark: {benchmark['Name']} ({benchmark['Benchmark']})")
                st.write(f"- PE Ratio: {benchmark['PE']}")
                st.write(f"- PB Ratio: {benchmark['PB']}")
                st.write(f"- ROE: {benchmark['ROE']}")
            else:
                st.write("Benchmark data not available.")

            valuation_label = None
            targets = get_analyst_price_targets(final_ticker)

            if targets and closing_price:
                st.subheader("Analyst Target Price vs. Current Price")
                try:
                    low = float(targets.get("targetLow", 0))
                    mean = float(targets.get("targetMean", 0))
                    high = float(targets.get("targetHigh", 0))

                    st.write(f"Target Range: ${low:.2f} - ${high:.2f}")
                    st.write(f"Average Target Price: ${mean:.2f}")
                    st.write(f"Current Price: {format_number(closing_price, style='usd')}")

                    if closing_price < low:
                        st.success("Valuation: Undervalued")
                        valuation_label = "undervalued"
                    elif low <= closing_price < mean:
                        st.info("Valuation: Fairly Valued")
                        valuation_label = "fairly valued"
                    elif mean <= closing_price <= high:
                        st.warning("Valuation: Slightly Overvalued")
                        valuation_label = "slightly overvalued"
                    elif closing_price > high:
                        st.error("Valuation: Overvalued")
                        valuation_label = "overvalued"
                    else:
                        st.info("Valuation: Unclear")
                        valuation_label = "unclear"
                except Exception as e:
                    st.warning("Unable to process analyst price targets.")
                    st.text(f"Debug Info: {e}")
            else:
                st.write("Analyst price targets not available.")

            display_stock_price_chart(final_ticker, clean_name)

            chart_buffer = BytesIO()
            time_range = st.session_state.time_range
            range_map = {
                "1M": "1mo",
                "6M": "6mo",
                "1Y": "1y",
                "5Y": "5y",
                "YTD": "ytd",
                "MAX": "max"
            }
            selected_period = range_map.get(time_range, "6mo")
            chart_data = yf.Ticker(final_ticker).history(period=selected_period)

            if not chart_data.empty and "Close" in chart_data.columns:
                plt.figure(figsize=(10, 4))
                plt.plot(chart_data.index, chart_data["Close"], label="Close Price", linewidth=2)
                plt.title(f"{clean_name} Stock Price ({time_range})")
                plt.xlabel("Date")
                plt.ylabel("Price (USD)")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()
                plt.savefig(chart_buffer, format="png", bbox_inches="tight", dpi=150)
                chart_buffer.seek(0)
                plt.close()
            else:
                chart_buffer = None
                st.warning("Chart could not be generated for this ticker.")

            st.subheader("AI-Powered Investment Summary")
            news_list = get_company_news_finnhub(final_ticker)
            summaries = []

            if isinstance(news_list, list):
                for item in news_list[:5]:
                    if isinstance(item, dict):
                        summary = summarize_news_article(item.get("title", ""), item.get("summary", ""))
                        summaries.append(summary)

            ai_summary = generate_summary(data, valuation_label=valuation_label, news_summaries=summaries)
            st.write(clean_text(ai_summary))

            st.subheader("Export Report")
            doc = generate_word_report(
                data=data,
                ticker=final_ticker,
                closing_price=closing_price,
                peg=peg,
                benchmark=benchmark,
                targets=targets,
                valuation_label=valuation_label,
                ai_summary=ai_summary,
                chart_image=chart_buffer
            )

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="Download Report (.docx)",
                data=buffer,
                file_name=f"{final_ticker}_financial_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.subheader("Recent News")
            if isinstance(news_list, list):
                for item in news_list:
                    if isinstance(item, dict):
                        st.markdown(f"**{item['title']}**")
                        if item["summary"]:
                            st.markdown(f"- {item['summary']}")
                        st.markdown(f"[Read more]({item['url']})")
                        st.markdown("---")
            else:
                st.write("No recent news available.")
        else:
            st.error("No data found.")


    #st.session_state.run_analysis = False

    # -------------------------------
    # Portfolio Builder Section
    # -------------------------------

with st.expander("Custom Portfolio Builder"):

    st.header("Smart Portfolio Builder")

    with st.form("portfolio_form"):
        tickers_input = st.text_input("Tickers (e.g., AAPL, MSFT, AMZN)")
        weights_input = st.text_input("Portfolio weights in %, optional (e.g., 40,30,30)")
        submitted = st.form_submit_button("Build Portfolio")

    weights = None

    if submitted:
    
    
        raw_inputs = [t.strip() for t in tickers_input.split(",") if t.strip()]
        tickers = []
        unresolved = []

        for item in raw_inputs:
            resolved = resolve_to_ticker(item)
            if resolved:
                tickers.append(resolved)
            else:
                unresolved.append(item)

        if unresolved:
            st.warning(f"The following entries could not be resolved: {', '.join(unresolved)}")

        if weights_input:
            try:
                weights = [float(w.strip()) / 100 for w in weights_input.split(",")]
                total = sum(weights)
                if abs(total - 1.0) > 0.01:
                    st.warning("Weights must add up to 100 percent.")
                    weights = None
                if len(weights) != len(tickers):
                    st.error("The number of weights must match the number of tickers.")
                    st.stop()
            except:
                st.error("Please enter valid numeric weights like 50,30,20")
                st.stop()

        if len(tickers) < 2:
            st.warning("Please enter at least two tickers.")
        else:
            with st.spinner("Analyzing portfolio..."):
                df, summary = analyze_portfolio(tickers, weights)

            st.subheader("Portfolio Composition")
            st.markdown("""
    This table shows financial indicators for each stock in your portfolio:

    - **PE**: Price relative to earnings. Lower = cheaper.
    - **PB**: Price relative to book value. Under 1.0 = potentially undervalued.
    - **ROE**: Return on equity. Higher = more efficient use of capital.
    - **Debt/Equity**: Lower = less risk from debt.
    - **Weight**: Allocation of each stock in your portfolio.
            """)
            st.dataframe(df)

            st.subheader("Weighted Averages")
            st.markdown("These represent the overall profile of your portfolio:")

            for k, v in summary.items():
                st.write(f"- {k}: {v}")

            # AI insight on portfolio
            insight = generate_portfolio_insight(df)
            st.subheader("AI Insight")
            st.info(insight)

            # Benchmark Comparison
            sector_weights = get_portfolio_sector_weights(df)
            sector_insight = compare_sector_allocation(sector_weights)
            st.subheader("Sector Benchmark Check (vs S&P 500)")
            st.info(sector_insight)

# AI Portfolio builder
with st.expander("AI-Powered Portfolio Builder"):

    st.subheader("Smart Portfolio Builder")

    capital = st.number_input("Enter investment capital (USD)", min_value=100.0, step=100.0)

    # Optional number of stocks
    limit_stocks = st.checkbox("Set number of stocks?")
    num_stocks = None
    if limit_stocks:
        num_stocks = st.number_input(
            "Number of stocks to include", min_value=1, max_value=50, step=1, value=10
        )

    risk_level = st.selectbox("Select your risk tolerance", ["Low", "Medium", "High"])
    sector_pref = st.text_input("Preferred sectors (optional, comma-separated)", "")
    country_pref = st.text_input("Preferred countries (optional, comma-separated)", "")

    if st.button("Build Portfolio"):
        preferences = {
            "risk_level": risk_level,
            "sectors": [s.strip() for s in sector_pref.split(",") if s.strip()],
            "countries": [c.strip() for c in country_pref.split(",") if c.strip()],
            "num_stocks": int(num_stocks) if num_stocks else None
        }

        # Call AI builder function
        ai_portfolio, ai_summary = build_ai_portfolio(capital, preferences)
        st.write("AI Portfolio Recommendation")
        st.dataframe(ai_portfolio)
        st.markdown("AI Analyst Report")
        st.write(ai_summary)


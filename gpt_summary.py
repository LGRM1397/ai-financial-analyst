import streamlit as st
from openai import OpenAI
from utils import format_number

# Initialize OpenAI client with your Streamlit secret key
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ---------------------------------------
# Generate GPT summary for one company
# ---------------------------------------
def generate_summary(data, valuation_label=None, news_summaries=None):
    news_insight = ""
    if news_summaries:
        top_news = "\n".join(f"- {item}" for item in news_summaries[:5])
        news_insight = "\n**News Highlights:**\n" + top_news

    valuation_perspective = ""
    if valuation_label:
        valuation_perspective = (
            f"\n**Valuation Status:** The stock appears **{valuation_label.upper()}** compared to analyst expectations or sector benchmarks."
        )

    prompt = f"""
You are a senior equity research analyst at a global investment firm.

Write a professional, structured investment summary based on the data below.

Your response must follow this format exactly:

**1. Executive Summary**  
Write a 3 to 4 sentence paragraph summarizing the company's investment outlook. Focus on market position, growth opportunities, and key risks.

**2. Financial Health Overview**  
Write a 3 to 4 sentence paragraph explaining the company's financial position. Mention profitability, efficiency, leverage, or valuation.

Then include 2 to 4 bullet points that justify or support your paragraph above. Start with the line:  
**Key Financial Insights:**  
- [Bullet 1]  
- [Bullet 2]  
- [Bullet 3]  
- [Bullet 4] (optional)

**3. Recent News and Sentiment**  
Write a 3 to 4 sentence paragraph analyzing recent news and its potential impact on the company's stock or operations.

Then include 2 to 4 bullet points that support your paragraph. Start with the line:  
**News Takeaways:**  
- [Bullet 1]  
- [Bullet 2]  
- [Bullet 3]  
- [Bullet 4] (optional)

**4. Recommendation**  
Write a 3 to 4 sentence paragraph providing your final recommendation. Mention key strengths, risks, and whether the stock is a Buy, Hold, or Sell.

End the report with this exact line on its own line:  
**AI Verdict: [Buy / Hold / Sell]**

**Company:** {data.get('shortName', 'Unknown')}  
**Sector:** {data.get('sector', 'Unknown')}  
**Market Capitalization:** {format_number(data.get('marketCap'))}  
**Trailing P/E Ratio:** {format_number(data.get('trailingPE'), style='ratio')}  
**Forward P/E Ratio:** {format_number(data.get('forwardPE'), style='ratio')}  
**Return on Equity (ROE):** {format_number(data.get('returnOnEquity'), style='percent')}  
**Debt-to-Equity Ratio:** {format_number(data.get('debtToEquity'), style='ratio')}  
**Gross Profit Margin:** {format_number(data.get('grossMargins'), style='percent')}  
{valuation_perspective}
{news_insight}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a helpful and professional financial analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"

# --------------------------------------------------
# Extract final GPT recommendation (Buy/Hold/Sell)
# --------------------------------------------------
def extract_ai_verdict(summary_text):
    lowered = summary_text.lower()
    if "ai verdict" in lowered:
        if "buy" in lowered:
            return "Buy"
        elif "hold" in lowered:
            return "Hold"
        elif "sell" in lowered:
            return "Sell"
    return "No clear recommendation detected."

# --------------------------------------------------
# Generate a GPT summary of the entire portfolio
# --------------------------------------------------
def generate_gpt_portfolio_insight(df):
    df_copy = df.copy()
    df_copy.columns = [col.replace("/", "_").replace(" ", "_") for col in df_copy.columns]
    table_string = df_copy.to_csv(index=False)

    prompt = f"""
You are a senior equity strategist at a top global investment firm. Analyze the following client portfolio using your expertise in portfolio theory, sector risk, valuation, and capital efficiency.

Instructions:
- Use the table below to assess diversification, valuation ratios (PE, PB), capital return (ROE), leverage (Debt_Equity), beta (if available), and sector allocations.
- Identify strengths and weaknesses in a professional tone.
- If metrics show extreme values (e.g., PE < 5 or > 40, ROE > 20%, Debt_Equity > 1.5), explain their possible implications.
- If the portfolio is overexposed to one sector or concentrated in low-quality names, highlight that.
- Suggest general improvements (diversification, defensive picks, higher-quality earnings, etc.).
- Use bullet points if helpful, but always include a summary paragraph first.

Client Portfolio:

{table_string}

Provide a clear, professional insight as if writing an internal investment note for senior partners. Avoid unnecessary repetition or fluff.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()

# ------------------------------------------------------------
# Generate a client-facing summary for a recommended portfolio
# ------------------------------------------------------------
def generate_ai_portfolio_summary(df, capital, risk_level, sectors, countries, news_dict=None):
    table_str = df.to_csv(index=False)

    # Format recent news headlines for each ticker
    if news_dict:
        news_lines = []
        for ticker, articles in news_dict.items():
            if articles:
                headline_str = "; ".join(articles[:2])
                news_lines.append(f"- {ticker}: {headline_str}")
        news_section = "\n### Recent News Highlights:\n" + "\n".join(news_lines) + "\n"
    else:
        news_section = ""

    prompt = f"""
You are a senior portfolio strategist at a top-tier investment advisory firm. Based on the client's capital and preferences, you designed a personalized portfolio using global best practices in asset allocation, risk management, and valuation.

### Client Profile:
- Total Capital: ${capital:,.2f}
- Risk Profile: {risk_level.upper()}
- Sector Preferences: {', '.join(sectors) if sectors else 'No specific preference'}
- Country Preferences: {', '.join(countries) if countries else 'No specific preference'}

### Recommended Portfolio:
{table_str}

{news_section}

### Instructions:
- Begin with a brief executive summary of the overall portfolio strategy.
- Discuss how the allocation aligns with the risk profile (conservative, balanced, aggressive).
- Highlight potential sector and regional exposures (diversified or concentrated).
- Explain any high or low valuation metrics (e.g., PE, ROE, Beta) and their implications.
- Justify choices even if sector/country preferences are loosely followed, with logic.
- Close with a short, professional assessment of potential next steps or monitoring advice.

Use a confident, professional tone as if presenting to the CIO of a private wealth fund.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

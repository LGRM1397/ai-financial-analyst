import streamlit as st
import requests
from openai import OpenAI

#Use Streamlit's secure secrets manager
client = OpenAI(api_key=st.secrets["openai_api_key"])
FINNHUB_API_KEY = st.secrets["finnhub_api_key"]

def get_company_news_finnhub(ticker):
    """Fetch recent company news with headline, summary, and URL using Finnhub API."""
    try:
        if not FINNHUB_API_KEY:
            return ["Error: Finnhub API key not found."]

        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2024-06-25&to=2025-07-02&token={FINNHUB_API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            return [f"Error: Failed to fetch news (status code {response.status_code})"]

        news_items = response.json()
        articles = []

        for item in news_items:
            title = item.get("headline", "")
            summary = item.get("summary", "")
            url = item.get("url", "")

            if title and url:
                articles.append({
                    "title": title,
                    "summary": summary,
                    "url": url
                })

            if len(articles) >= 10:  # Limit to 10 articles speed.
                break

        return articles if articles else ["No recent news available."]
    except Exception as e:
        return [f"Error: {str(e)}"]


def summarize_news_article(title, summary):
    """
    Summarizes a single news headline and snippet using GPT.
    If only the title is available, it will summarize based on that.
    """
    prompt = f"""
You're an AI analyst. Summarize this company news in 2 concise sentences, keeping it factual and neutral:

Title: {title}
Summary: {summary}

Return only the summary.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"News summary error: {e}"


def get_news_for_portfolio(tickers, limit=1):
    news_dict = {}
    for ticker in tickers:
        try:
            articles = get_company_news_finnhub(ticker)
            if articles and isinstance(articles[0], dict):
                top_articles = [a['title'] for a in articles[:limit]]
                news_dict[ticker] = top_articles
        except:
            continue
    return news_dict

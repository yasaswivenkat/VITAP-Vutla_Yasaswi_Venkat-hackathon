import os
import pandas as pd
import requests
import yfinance as yf
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path) # Force load from root directory

# Setup Gemini Client
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment.")
    client = genai.Client(api_key=api_key)
except Exception as e:
    client = None
    print(f"Warning: Could not initialize Gemini Client. {e}")

class RiskSignal(BaseModel):
    sentiment_score: float = Field(description="A numerical score from -1.0 to 1.0 indicating sentiment.")
    event_classification: str = Field(description="Categorical label: e.g., Geopolitical, Macroeconomic, Credit Event, M&A, Product Launch, None.")
    impact_score: int = Field(description="Predicted severity score 1-10 indicating potential market impact.")
    explanation: str = Field(description="Brief reason for this analysis.")

def analyze_text(text: str) -> dict:
    """
    Analyzes unstructured text using Gemini and returns structured risk signals.
    """
    if not client:
        return {"error": "Gemini Client not initialized. Check GEMINI_API_KEY."}
    
    prompt = f"Analyze the following financial text and extract risk signals:\n\n{text}"
    
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RiskSignal,
            ),
        )
        # Parse JSON string into dict
        return json.loads(response.text)
    except Exception as e:
        print(f"Error during NLP analysis: {e}")
        return {
            "sentiment_score": 0.0,
            "event_classification": "Error",
            "impact_score": 1,
            "explanation": str(e)
        }

def fetch_yfinance_news(ticker: str) -> list:
    """Source 1: Fetch recent news using yfinance."""
    tkr = yf.Ticker(ticker)
    articles = []
    
    try:
        news = tkr.news
        if news:
            for item in news[:3]: # limit to 3 for demo
                articles.append({
                    "source": "Yahoo Finance",
                    "title": item.get('title', ''),
                    "summary": item.get('summary', ''), # Note: yfinance news format changes sometimes, summary might be empty
                    "url": item.get('link', '')
                })
    except Exception as e:
        print(f"yfinance Error (Yahoo might be blocking requests): {e}")
        # Fallback to mock data if yfinance is blocked
        articles.append({
            "source": "Mocked News (Yahoo Blocked)",
            "title": f"Recent volatility observed in {ticker}",
            "summary": f"Market analysts are closely watching {ticker} amidst shifting sector trends.",
            "url": "https://finance.yahoo.com"
        })
        
    return articles

def fetch_newsapi_data(keyword: str) -> list:
    """Source 2: Fetch global macroeconomic news using News API."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        # Fallback to mock data if key is missing so the app doesn't break
        return [
            {
                "source": "Mocked News (No NewsAPI Key)",
                "title": f"Breaking: Major developments regarding {keyword}",
                "summary": f"Analysts warn that {keyword} could face massive volatility due to shifting geopolitical landscapes.",
                "url": "https://newsapi.org"
            }
        ]
        
    url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&pageSize=2&language=en&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        articles = []
        if data.get("status") == "ok":
            for item in data.get("articles", []):
                articles.append({
                    "source": item.get("source", {}).get("name", "NewsAPI"),
                    "title": item.get("title", ""),
                    "summary": item.get("description", ""),
                    "url": item.get("url", "")
                })
        return articles
    except Exception as e:
        print(f"NewsAPI Error: {e}")
        return []

def process_data_pipeline(ticker: str = None, custom_articles: list = None):
    """Runs the full ingestion and NLP pipeline."""
    if custom_articles:
        all_data = custom_articles
    else:
        # Combine Source 1 (yfinance) and Source 2 (NewsAPI)
        all_data = fetch_yfinance_news(ticker) + fetch_newsapi_data(ticker)
        
    results = []
    
    for item in all_data:
        text_to_analyze = f"Title: {item['title']}\nSummary: {item.get('summary', '')}"
        signals = analyze_text(text_to_analyze)
        
        # Combine original data with signals
        combined = {**item, **signals}
        results.append(combined)
        
    # Persist to log file
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(base_dir, 'data', 'risk_logs.csv')
        df_new = pd.DataFrame(results)
        if os.path.exists(log_path):
            df_existing = pd.read_csv(log_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(log_path, index=False)
        else:
            df_new.to_csv(log_path, index=False)
    except Exception as e:
        print(f"Failed to log to CSV: {e}")
        
    return results

if __name__ == "__main__":
    # Test the pipeline
    res = process_data_pipeline("AAPL")
    print(json.dumps(res, indent=2))

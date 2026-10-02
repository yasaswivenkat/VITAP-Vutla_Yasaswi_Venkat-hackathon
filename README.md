# Unified AI Risk Engine & Strategic Stress Testing - S&P Global & Crisil Campus Hackathon

**Candidate Name:** Vutla Yasaswi Venkat

**College Email ID:** yasaswi.23bce9575@vitapstudent.ac.in

**College / Campus:** VIT-AP

**Demo Video Link:** [Insert your Unlisted YouTube Link Here - ~5 mins recommended]

**Slide Deck Link:** [docs/presentation.pptx](docs/presentation.pptx)

## 1. Project Overview

**Problem:** Modern risk management teams struggle to instantly quantify the severity of breaking unstructured news (like geopolitical conflicts) and immediately understand their financial impact on a banking portfolio.

**Approach:** We built a unified platform that acts as an AI-driven Risk Analyst. It ingests live global news feeds, uses a Large Language Model (Google Gemini 2.5) to parse text into structured financial signals (Sentiment, Event Class, Impact Score), and conditionally triggers automated portfolio stress tests based on those signals.

## 2. Architecture & Tech Stack
- **Ingestion Layer:** Real-time data fetched via `yfinance` APIs (for financial news) **and** `NewsAPI` (for global macroeconomic news), plus historical archives.
- **NLP Engine Layer:** Text is sent to `google-genai` using Structured Outputs (JSON Schema) to extract precise metrics.
- **Application Layer:** 
  - **Module A:** Consumes `sentiment_score` to dynamically rebalance a stock index.
  - **Module B:** Consumes `event_classification` & `impact_score` to apply shocks to a synthetic wholesale banking portfolio.
  - **Module C:** Replays historical crises (e.g. SVB Collapse) to backtest the portfolio against past black-swan events.
  - **Module D:** Audit & Reporting layer that persists all AI risk extractions to a CSV for compliance tracking.
- **Tech Stack:** Python 3.11, Streamlit (Frontend UI), Plotly (Interactive Charts), Google Gemini 2.5 Flash API (AI Engine), Pandas & Numpy (Data Manipulation).

## 3. Dataset Used
- **Financial News:** Real-time headlines fetched via `yfinance` API and `NewsAPI`.
- **Synthetic Portfolio:** A custom script (`src/generate_data.py`) randomly generates a realistic wholesale banking portfolio featuring Corporate Loans, Sovereign Bonds, and MBS assets. This ensures compliance with the "no proprietary data" rule while maintaining high realism.

## 4. Quickstart & Installation
Runtime: Python 3.11+ on Windows/Linux/Mac

Step-by-step commands to set up the environment and run your code locally:
```bash
# 1. Clone the repository
git clone https://github.com/yasaswivenkat/VITAP-Vutla_Yasaswi_Venkat-hackathon.git
cd VITAP-Vutla_Yasaswi_Venkat-hackathon

# 2. Add your API Keys
# Create a .env file in the root directory and add:
# GEMINI_API_KEY="your_actual_key_here"
# NEWS_API_KEY="your_newsapi_key_here"

# 3. Create a Virtual Environment & Install Dependencies
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate
pip install -r requirements.txt

# 4. Generate the Synthetic Data
python src/generate_data.py

# 5. Launch the Dashboard
streamlit run src/app.py
```

## 5. Key Results & Domain Impact
- **What it outputs:** A 4-module enterprise dashboard featuring dynamic index rebalancing, live portfolio stress testing, historical crisis backtesting, and compliance logging.
- **Business Impact:** In financial crises, minutes matter. This engine allows risk managers at wholesale banks to instantly simulate the financial impact of breaking news on their exposure before the rest of the market reacts. It removes human bias from event categorization and can process 10,000 news articles a minute.

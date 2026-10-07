import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from engine import process_data_pipeline

st.set_page_config(page_title="Unified AI Risk Platform", layout="wide", page_icon="📈")

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Module", [
    "Module B: Stress Testing", 
    "Module A: Index Rebalancing",
    "Module C: Historical Backtesting",
    "Module D: Audit & Reporting" # NEW MODULE!
])

# Helpers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'portfolio.csv')

@st.cache_data
def load_portfolio():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        st.error(f"Portfolio data not found. Please run `python src/generate_data.py` first.")
        return pd.DataFrame()

df_portfolio = load_portfolio()

# ==========================================
# MODULE B: STRESS TESTING
# ==========================================
if app_mode == "Module B: Stress Testing":
    st.title("Strategic Portfolio Stress Testing")
    st.markdown("Visualizes the impact of real-time AI-extracted macroeconomic events on a synthetic wholesale banking portfolio.")

    if not df_portfolio.empty:
        total_exposure = df_portfolio['Exposure_USD'].sum()
        total_rwa = df_portfolio['Initial_RWA'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assets", f"{len(df_portfolio)}")
        col2.metric("Total Exposure (USD)", f"${total_exposure:,.0f}")
        col3.metric("Total Initial RWA", f"${total_rwa:,.0f}")
        
        # Portfolio Distribution Chart
        fig_dist = px.pie(df_portfolio, names='Asset_Type', values='Exposure_USD', title='Portfolio Asset Distribution', hole=0.3)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        st.markdown("---")
        st.header("Real-Time Risk Engine Analysis")
        
        ticker = st.text_input("Enter a keyword to fetch global news & analyze (e.g., TSLA, INTC, Oil, Geopolitics):", value="TSLA")
        
        if st.button("Run AI Risk Engine", type="primary"):
            with st.spinner("Fetching data and running Gemini LLM Analysis..."):
                results = process_data_pipeline(ticker=ticker)
                
                if not results:
                    st.warning("No data found for this keyword.")
                elif "error" in results[0] and results[0]["error"]:
                    st.error(results[0]["error"])
                else:
                    st.session_state['latest_signals'] = results
                    st.success("Analysis Complete!")

        if 'latest_signals' in st.session_state:
            st.subheader("Extracted Risk Signals")
            for idx, res in enumerate(st.session_state['latest_signals']):
                with st.expander(f"{res['source']} - {res['title'][:60]}..."):
                    cols = st.columns(3)
                    cols[0].metric("Sentiment Score", f"{res.get('sentiment_score', 0):.2f}")
                    cols[1].metric("Event Classification", res.get('event_classification', 'N/A'))
                    cols[2].metric("Impact Score (1-10)", res.get('impact_score', 'N/A'))
                    st.write(f"**AI Explanation:** {res.get('explanation', 'N/A')}")
            
            st.markdown("---")
            st.header("Stress Test Simulation")
            
            highest_impact_signal = max(st.session_state['latest_signals'], key=lambda x: x.get('impact_score', 0) if isinstance(x.get('impact_score'), (int, float)) else 0)
            event_type = highest_impact_signal.get('event_classification', 'None')
            impact = highest_impact_signal.get('impact_score', 0)
            
            st.info(f"**Triggering Event:** {event_type} (Impact: {impact}/10)")
            
            if isinstance(impact, (int, float)) and impact >= 7:
                st.error("🚨 HIGH IMPACT EVENT DETECTED. INITIATING SHOCKS.")
                
                shock_factor = 0.0
                if event_type == "Geopolitical": shock_factor = -0.15
                elif event_type == "Macroeconomic": shock_factor = -0.10
                elif event_type == "Credit Event": shock_factor = -0.20
                else: shock_factor = -0.05
                    
                st.write(f"**Simulated Shock:** {shock_factor*100}% adjustment to portfolio exposure value.")
                
                df_stressed = df_portfolio.copy()
                df_stressed['Stressed_Exposure'] = df_stressed['Exposure_USD'] * (1 + shock_factor)
                
                new_exposure = df_stressed['Stressed_Exposure'].sum()
                
                # Plot Before/After
                fig_stress = go.Figure(data=[
                    go.Bar(name='Original Exposure', x=['Portfolio'], y=[total_exposure], marker_color='blue'),
                    go.Bar(name='Stressed Exposure', x=['Portfolio'], y=[new_exposure], marker_color='red')
                ])
                fig_stress.update_layout(title_text='Portfolio Value: Before vs After Stress Test', barmode='group')
                st.plotly_chart(fig_stress, use_container_width=True)
                
                col1, col2 = st.columns(2)
                col1.metric("Original Exposure", f"${total_exposure:,.0f}")
                col2.metric("Stressed Exposure", f"${new_exposure:,.0f}", f"{new_exposure - total_exposure:,.0f}")
                
            else:
                st.success("No high impact event detected. Portfolio remains stable.")

# ==========================================
# MODULE A: INDEX REBALANCING
# ==========================================
elif app_mode == "Module A: Index Rebalancing":
    st.title("Tactical Index Rebalancing")
    st.markdown("Dynamically rebalances a mock stock index based on real-time NLP sentiment analysis.")

    # Mock Index setup
    index_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    if 'index_weights' not in st.session_state:
        st.session_state['index_weights'] = {stock: 100/len(index_stocks) for stock in index_stocks}
        
    st.subheader("Current Index Weights")
    
    def plot_weights(weights_dict):
        df = pd.DataFrame(list(weights_dict.items()), columns=['Stock', 'Weight (%)'])
        fig = px.pie(df, names='Stock', values='Weight (%)', hole=0.4, color='Stock')
        return fig
        
    st.plotly_chart(plot_weights(st.session_state['index_weights']), use_container_width=True)
    
    st.markdown("---")
    st.header("Real-Time Sentiment Rebalancing")
    
    if st.button("Trigger Global Rebalance", type="primary"):
        with st.spinner("Analyzing live news for all 5 index components via Gemini..."):
            adjustments = {}
            for stock in index_stocks:
                results = process_data_pipeline(ticker=stock)
                if results and "error" not in results[0]:
                    avg_sent = np.mean([r.get('sentiment_score', 0) for r in results])
                else:
                    avg_sent = 0
                adjustments[stock] = avg_sent
            
            st.subheader("AI Sentiment Results & Adjustments")
            cols = st.columns(5)
            for i, (stock, sent) in enumerate(adjustments.items()):
                cols[i].metric(stock, f"Sent: {sent:.2f}")
            
            new_weights = {}
            for stock, w in st.session_state['index_weights'].items():
                new_w = max(1, w + (adjustments[stock] * 10))
                new_weights[stock] = new_w
                
            total_w = sum(new_weights.values())
            for stock in new_weights:
                new_weights[stock] = (new_weights[stock] / total_w) * 100
                
            st.session_state['index_weights'] = new_weights
            
            st.subheader("New Rebalanced Index")
            st.plotly_chart(plot_weights(st.session_state['index_weights']), use_container_width=True)

# ==========================================
# MODULE C: HISTORICAL BACKTESTING
# ==========================================
elif app_mode == "Module C: Historical Backtesting":
    st.title("Historical Crisis Backtesting")
    st.markdown("Replays past global crises through our AI engine to see how our portfolio would have survived.")
    
    crisis = st.selectbox("Select a Historical Crisis to Simulate:", [
        "Silicon Valley Bank Collapse (March 2023)",
        "Global Pandemic Market Crash (March 2020)"
    ])
    
    mock_articles = []
    if "Bank Collapse" in crisis:
        mock_articles = [
            {"source": "Historical News", "title": "SVB Financial Group announces $1.75B stock sale", "summary": "Silicon Valley Bank is attempting to raise capital to cover a $1.8B loss on bond sales, sparking panic among VC firms and startups."},
            {"source": "Historical News", "title": "Bank run hits Silicon Valley Bank as founders pull cash", "summary": "Massive withdrawals threaten the liquidity of SVB, prompting fears of broader contagion in the regional banking sector."}
        ]
    else:
        mock_articles = [
            {"source": "Historical News", "title": "WHO declares COVID-19 a global pandemic", "summary": "Countries are locking down borders and halting economic activity, sending global supply chains into chaos."},
            {"source": "Historical News", "title": "Stock markets halt trading as S&P 500 plunges 7%", "summary": "Unprecedented sell-offs trigger circuit breakers across global exchanges amidst pandemic fears."}
        ]
        
    st.write(f"**Loaded {len(mock_articles)} historical articles from the archive.**")
    st.dataframe(pd.DataFrame(mock_articles))
    
    if st.button("Run Backtest Simulation", type="primary"):
        with st.spinner("Analyzing historical documents..."):
            results = process_data_pipeline(custom_articles=mock_articles)
            
            highest_impact = 0
            event = "None"
            for res in results:
                impact = res.get('impact_score', 0)
                if isinstance(impact, (int, float)) and impact > highest_impact:
                    highest_impact = impact
                    event = res.get('event_classification', 'None')
            
            st.success("Historical Analysis Complete!")
            st.info(f"**AI Classified Crisis As:** {event} (Severity: {highest_impact}/10)")
            
            if not df_portfolio.empty:
                total_exposure = df_portfolio['Exposure_USD'].sum()
                shock_factor = -0.25 if "Bank" in crisis else -0.35 # Massive shocks for these crises
                
                new_exposure = total_exposure * (1 + shock_factor)
                
                st.error(f"📉 **Simulated Historical Portfolio Impact: {shock_factor*100}%**")
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=['Pre-Crisis'], y=[total_exposure], name='Pre-Crisis', marker_color='blue'))
                fig.add_trace(go.Bar(x=['Post-Crisis'], y=[new_exposure], name='Post-Crisis', marker_color='red'))
                fig.update_layout(title=f"Portfolio Impact: {crisis}")
                st.plotly_chart(fig, use_container_width=True)
                
                st.metric("Total Wealth Destroyed", f"-${(total_exposure - new_exposure):,.0f}")

# ==========================================
# MODULE D: AUDIT & REPORTING
# ==========================================
elif app_mode == "Module D: Audit & Reporting":
    st.title("Enterprise Audit & Compliance Logs")
    st.markdown("All NLP extractions and risk signals are permanently persisted here for compliance reporting.")
    
    log_path = os.path.join(BASE_DIR, 'data', 'risk_logs.csv')
    
    if os.path.exists(log_path):
        df_logs = pd.read_csv(log_path)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Events Logged", len(df_logs))
        if 'impact_score' in df_logs.columns:
            avg_impact = pd.to_numeric(df_logs['impact_score'], errors='coerce').mean()
            col2.metric("Average Impact Score", f"{avg_impact:.1f}/10")
            
        st.subheader("Raw AI Extraction Logs")
        st.dataframe(df_logs, use_container_width=True)
        
        # Download button
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Compliance Report (CSV)",
            data=csv,
            file_name='enterprise_risk_audit.csv',
            mime='text/csv',
        )
    else:
        st.info("No risk logs found. Go to Module A or B and run the AI engine to generate logs!")

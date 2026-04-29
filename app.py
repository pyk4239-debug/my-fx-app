import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import warnings

# Ignore warnings and page config
warnings.filterwarnings('ignore')
st.set_page_config(page_title="캐나다 환율 모니터", page_icon="🇨🇦")

st.title("🇨🇦 실시간 CAD/KRW 환율 모니터")
st.write("실시간 금융 데이터를 바탕으로 한 환율 추이입니다.")

# Fetch data
ticker = "CADKRW=X"
try:
    # Data from Jan 2026 to today
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    if not df.empty:
        prices = df['Close']
        
        # Extract latest price
        last_price = prices.iloc[-1]
        if hasattr(last_price, 'iloc'):
            current_val = float(last_price.iloc[0])
        else:
            current_val = float(last_price)
        
        # Display Metric
        st.metric(label="현재 환율 (1 CAD)", value=f"{current_val:,.2f} 원")

        # Create Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(prices.index, prices, color='#0077b6', linewidth=2)
        ax.fill_between(prices.index, prices.values.flatten(), color='#0077b6', alpha=0.1)
        
        # User requested range (1000~1100)
        ax.set_ylim(1000, 1100)
        ax.set_title("2026 CAD/KRW Trend (Focused View)", fontsize=14)
        ax.set_ylabel("Won (KRW)")
        ax.grid(True, linestyle='--', alpha=0.5)
        
        st.pyplot(fig)
        
        st.info("이 데이터는 Yahoo Finance 실시간 정보를 바탕으로 자동 업데이트됩니다.")
    else:
        st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
except Exception as e:
    st.error(f"오류 발생: {e}")

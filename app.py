import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import warnings

# 1. 페이지 설정
warnings.filterwarnings('ignore')
st.set_page_config(page_title="캐나다 환율", page_icon="🇨🇦", layout="wide")

st.title("🇨🇦 실시간 CAD/KRW 환율 모니터")

# 2. 데이터 가져오기 (매일 데이터 유지)
ticker = "CADKRW=X"
try:
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    
    if not df.empty:
        df.index = pd.to_datetime(df.index)
        prices = df['Close']
        
        # 최신 환율 정보
        current_val = float(prices.iloc[-1].values[0]) if hasattr(prices.iloc[-1], 'values') else float(prices.iloc[-1])
        prev_val = float(prices.iloc[-2].values[0]) if len(prices) > 1 else current_val
        delta = current_val - prev_val
        
        # 연도 생략 날짜 (%m-%d)
        last_date_display = prices.index[-1].strftime('%m-%d')
        st.metric(label=f"현재 환율 ({last_date_display} 기준)", 
                  value=f"{current_val:,.2f} 원", 
                  delta=f"{delta:+.2f} 원")

        # 3. 그래프 표시 (데이터는 Daily, 라벨만 Monthly)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(prices.index, prices.values, color='#0077b6', linewidth=2)
        ax.fill_between(prices.index, prices.values.flatten(), color='#0077b6', alpha=0.1)

        # --- 이 부분이 핵심입니다 ---
        # x축 라벨을 매월 1일(MonthLocator)로 설정
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
        # 라벨 형식을 연도 제외 월-일(%m-%d)로 설정
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        ax.set_ylim(1000, 1100)
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=0) # 날짜 정자로 표시
        st.pyplot(fig)

        # 4. 하단 상세 내역 (표에서도 15일 데이터만 제외하거나 전체 유지)
        st.subheader("📅 일자별 환율 상세 내역")
        
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전일대비'] = display_df['환율(종가)'].diff()
        
        # 표의 날짜도 연도 생략
        display_df.index = display_df.index.strftime('%m-%d')
        
        # 표에서는 15일 데이터를 제외하고 싶으시면 아래 주석을 해제하세요
        # display_df = display_df[display_df.index.str.slice(3) != "15"]

        def style_delta(val):
            if val > 0: return f"▲ {val:+.2f}"
            elif val < 0: return f"▼ {val:+.2f}"
            return f"{val:,.2f}"

        display_df['전일대비'] = display_df['전일대비'].apply(style_delta)
        st.dataframe(display_df.sort_index(ascending=False), use_container_width=True)

    else:
        st.error("데이터 로드 실패")
except Exception as e:
    st.error(f"오류 발생: {e}")

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
        
        # 현재 환율 정보
        current_val = float(prices.iloc[-1].values[0]) if hasattr(prices.iloc[-1], 'values') else float(prices.iloc[-1])
        prev_val = float(prices.iloc[-2].values[0]) if len(prices) > 1 else current_val
        delta = current_val - prev_val
        
        # 연도 생략 날짜 (%m-%d)
        last_date_display = prices.index[-1].strftime('%m-%d')
        
        # 상단 지표 (상승 빨강 / 하락 파랑 적용)
        st.metric(label=f"현재 환율 ({last_date_display} 기준)", 
                  value=f"{current_val:,.2f} 원", 
                  delta=f"{delta:+.2f} 원")

        # 3. 그래프 표시 (데이터는 Daily 유지, 라벨만 월별 1일)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(prices.index, prices.values, color='#0077b6', linewidth=2)
        ax.fill_between(prices.index, prices.values.flatten(), color='#0077b6', alpha=0.1)

        # 하단 눈금을 매월 1일로 설정 (연도 제외 %m-%d)
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        ax.set_ylim(1000, 1120)
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=0) 
        st.pyplot(fig)

        # 4. 상세 내역 (상승 빨강 삼각형, 하락 파랑 삼각형 적용)
        st.subheader("📅 일자별 환율 상세 내역")
        
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전일대비'] = display_df['환율(종가)'].diff()
        
        # 날짜 인덱스에서 연도 생략
        display_df.index = display_df.index.strftime('%m-%d')

        # 등락 표시 함수 (삼각형 및 색상 로직)
        def format_delta_text(val):
            if pd.isna(val): return "-"
            if val > 0: return f"▲ {val:+.2f}" # 상승 빨강 예정
            elif val < 0: return f"▼ {val:+.2f}" # 하락 파랑 예정
            return f"{val:,.2f}"

        # 스타일 지정 함수 (상승 빨강, 하락 파랑)
        def style_delta_color(val):
            if '▲' in str(val): return 'color: red;'
            elif '▼' in str(val): return 'color: blue;'
            return ''

        display_df['전일대비'] = display_df['전일대비'].apply(format_delta_text)

        # 표 출력
        st.dataframe(
            display_df.sort_index(ascending=False).style.format({"환율(종가)": "{:,.2f}"})
            .map(style_delta_color, subset=['전일대비']),
            use_container_width=True
        )

    else:
        st.error("데이터 로드 실패")
except Exception as e:
    st.error(f"오류 발생: {e}")

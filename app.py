import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import warnings

# 1. 페이지 설정
warnings.filterwarnings('ignore')
st.set_page_config(page_title="캐나다 환율", page_icon="🇨🇦", layout="wide")

# 브라우저 번역 방지
st.markdown('<html lang="ko">', unsafe_allow_html=True)
st.title("🇨🇦 실시간 CAD/KRW 환율 모니터")

# 2. 데이터 가져오기 (토론토 기준 4월 30일 목요일 종가 반영)
ticker = "CADKRW=X"
try:
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    
    if not df.empty:
        df.index = pd.to_datetime(df.index)
        
        # [수정] 15일 데이터 제외
        df = df[df.index.day != 15]
        prices = df['Close']
        
        current_val = float(prices.iloc[-1].values[0]) if hasattr(prices.iloc[-1], 'values') else float(prices.iloc[-1])
        prev_val = float(prices.iloc[-2].values[0]) if len(prices) > 1 and hasattr(prices.iloc[-2], 'values') else (float(prices.iloc[-2]) if len(prices) > 1 else current_val)
        delta = current_val - prev_val

        # [수정] 상단 표시 날짜에서 연도 생략
        last_date_display = prices.index[-1].strftime('%m-%d')
        st.metric(label=f"현재 환율 ({last_date_display} 기준)", value=f"{current_val:,.2f} 원", delta=f"{delta:+.2f} 원")

        # 3. 그래프 표시
        fig, ax = plt.subplots(figsize=(10, 4))
        # [수정] x축 라벨 연도 생략
        display_dates = prices.index.strftime('%m-%d')
        ax.plot(display_dates, prices.values, color='#0077b6', linewidth=2)
        ax.fill_between(display_dates, prices.values.flatten(), color='#0077b6', alpha=0.1)
        
        # x축 눈금 겹침 방지
        n = len(display_dates)
        ax.set_xticks(range(0, n, max(1, n//10)))
        ax.set_ylim(1000, 1100) 
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # 4. 상세 내역 (15일 제외 및 연도 생략)
        st.subheader("📅 일자별 환율 상세 내역 (15일 제외)")
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전일대비'] = display_df['환율(종가)'].diff()
        
        # [수정] 인덱스 날짜에서 연도 생략
        display_df.index = pd.to_datetime(display_df.index).strftime('%m-%d')
        display_df = display_df.sort_index(ascending=False)

        def format_delta_text(val):
            if pd.isna(val): return "-"
            return f"▲ {val:+.2f}" if val > 0 else (f"▼ {val:+.2f}" if val < 0 else f"{val:,.2f}")

        def style_delta_color(val):
            return 'color: red;' if '▲' in str(val) else ('color: blue;' if '▼' in str(val) else '')

        display_df['전일대비'] = display_df['전일대비'].apply(format_delta_text)
        st.dataframe(display_df.style.format({"환율(종가)": "{:,.2f}"}).map(style_delta_color, subset=['전일대비']), use_container_width=True)

        st.info("💡 토론토의 목요일은 지나갔고, 이제 금요일 아침 장이 열릴 준비를 하고 있습니다.")
    else:
        st.error("데이터 로드 실패")
except Exception as e:
    st.error(f"오류: {e}")

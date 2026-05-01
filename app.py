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

# 2. 데이터 가져오기 (2026년 1월부터)
ticker = "CADKRW=X"
try:
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    
    if not df.empty:
        df.index = pd.to_datetime(df.index)
        
        # [핵심 로직] 매월 1일 데이터만 필터링 (월별 전환)
        df_monthly = df[df.index.day == 1].copy()
        
        # 최신 데이터(오늘)가 1일이 아니더라도 마지막에 포함
        if df.index[-1] not in df_monthly.index:
            df_monthly = pd.concat([df_monthly, df.iloc[[-1]]]).sort_index()
            df_monthly = df_monthly[~df_monthly.index.duplicated(keep='last')]

        prices = df_monthly['Close']
        current_val = float(prices.iloc[-1].values[0]) if hasattr(prices.iloc[-1], 'values') else float(prices.iloc[-1])
        
        # 연도 생략 표시 (%m-%d)
        last_date_display = prices.index[-1].strftime('%m-%d')
        st.metric(label=f"현재 환율 ({last_date_display} 기준)", value=f"{current_val:,.2f} 원")

        # 3. 그래프 표시
        fig, ax = plt.subplots(figsize=(10, 4))
        display_dates = prices.index.strftime('%m-%d')
        ax.plot(display_dates, prices.values, color='#0077b6', marker='o', linewidth=2)
        ax.fill_between(display_dates, prices.values.flatten(), color='#0077b6', alpha=0.1)
        ax.set_ylim(1000, 1100) 
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # 4. 상세 내역 (월별 기준)
        st.subheader("📅 월별 환율 내역 (매월 1일 기준)")
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전월대비'] = display_df['환율(종가)'].diff()
        
        # 연도 생략 및 내림차순 정렬
        display_df.index = pd.to_datetime(display_df.index).strftime('%m-%d')
        display_df = display_df.sort_index(ascending=False)

        def format_delta_text(val):
            if pd.isna(val): return "-"
            return f"▲ {val:+.2f}" if val > 0 else (f"▼ {val:+.2f}" if val < 0 else f"{val:,.2f}")

        def style_delta_color(val):
            return 'color: red;' if '▲' in str(val) else ('color: blue;' if '▼' in str(val) else '')

        display_df['전월대비'] = display_df['전월대비'].apply(format_delta_text)
        st.dataframe(display_df.style.format({"환율(종가)": "{:,.2f}"}).map(style_delta_color, subset=['전월대비']), use_container_width=True)

        st.info("💡 매월 1일 데이터를 기준으로 월간 환율 흐름을 보여줍니다.")
    else:
        st.error("데이터를 가져오지 못했습니다.")
except Exception as e:
    st.error(f"오류 발생: {e}")

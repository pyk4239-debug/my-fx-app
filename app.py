import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import warnings

# 설정 및 경고 무시
warnings.filterwarnings('ignore')
st.set_page_config(page_title="캐나다 환율 모니터", page_icon="🇨🇦")

st.title("🇨🇦 실시간 CAD/KRW 환율 모니터")

# 1. 데이터 가져오기
ticker = "CADKRW=X"
try:
    # 2026년 1월부터 데이터 로드
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    if not df.empty:
        # 데이터 정리
        prices = df['Close']
        df_sorted = df.sort_index(ascending=False) # 최신순 정렬
        
        # 현재 환율 계산
        current_val = float(prices.iloc[-1])
        prev_val = float(prices.iloc[-2]) if len(prices) > 1 else current_val
        delta = current_val - prev_val

        # 상단 메트릭 표시 (등락폭 추가)
        st.metric(label="현재 환율 (1 CAD)", 
                  value=f"{current_val:,.2f} 원", 
                  delta=f"{delta:+.2f} 원")

        # 2. 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(prices.index, prices, color='#0077b6', linewidth=2)
        ax.fill_between(prices.index, prices.values.flatten(), color='#0077b6', alpha=0.1)
        ax.set_ylim(1000, 1100)
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # 3. 일자별 등락 리스트 추가
        st.subheader("📅 일자별 환율 상세 내역")
        
        # 데이터프레임 가공 (날짜, 종가, 전일대비 등락)
        display_df = df[['Close']].copy()
        display_df['전일대비'] = display_df['Close'].diff()
        display_df = display_df.sort_index(ascending=False) # 최신 날짜가 위로

        # 테이블 스타일링 및 출력
        st.dataframe(
            display_df.style.format("{:,.2f}")
            .background_gradient(subset=['전일대비'], cmap='RdYlGn_r'), # 등락에 따라 색상 부여
            use_container_width=True
        )

        st.info("💡 위 표에서 '전일대비'가 플러스면 환율 상승, 마이너스면 하락을 의미합니다.")
    else:
        st.error("데이터를 가져오지 못했습니다.")
except Exception as e:
    st.error(f"오류 발생: {e}")

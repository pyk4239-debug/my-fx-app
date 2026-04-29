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
    df = yf.download(ticker, start="2026-01-01", auto_adjust=True)
    
    if not df.empty:
        prices = df['Close']
        
        # 현재 환율 및 전일 환율 추출
        current_val = float(prices.iloc[-1].values[0]) if hasattr(prices.iloc[-1], 'values') else float(prices.iloc[-1])
        prev_val = float(prices.iloc[-2].values[0]) if len(prices) > 1 and hasattr(prices.iloc[-2], 'values') else (float(prices.iloc[-2]) if len(prices) > 1 else current_val)
        delta = current_val - prev_val

        # 상단 메트릭 표시
        st.metric(label="현재 환율 (1 CAD)", 
                  value=f"{current_val:,.2f} 원", 
                  delta=f"{delta:+.2f} 원")

        # 2. 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(prices.index, prices.values, color='#0077b6', linewidth=2)
        ax.fill_between(prices.index, prices.values.flatten(), color='#0077b6', alpha=0.1)
        ax.set_ylim(1000, 1100)
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # 3. 일자별 환율 상세 리스트 (색상 추가 버전)
        st.subheader("📅 일자별 환율 상세 내역")
        
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전일대비'] = display_df['환율(종가)'].diff()
        display_df = display_df.sort_index(ascending=False)

        # 색상 지정 함수 (플러스는 빨강, 마이너스는 초록)
        def color_delta(val):
            if val > 0:
                color = '#ffcccc' # 연한 빨강
            elif val < 0:
                color = '#ccffcc' # 연한 초록
            else:
                color = 'white'
            return f'background-color: {color}'

        # 테이블 스타일 적용 출력
        st.dataframe(
            display_df.style.format("{:,.2f}").applymap(color_delta, subset=['전일대비']),
            use_container_width=True
        )

        st.info("💡 '전일대비' 열의 색상을 통해 환율 변동을 확인하세요!")
    else:
        st.error("데이터를 가져오지 못했습니다.")
except Exception as e:
    st.error(f"오류 발생: {e}")

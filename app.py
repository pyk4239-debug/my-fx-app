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
        # 데이터 정리 (형식 오류 방지를 위한 안전한 추출)
        prices = df['Close']
        
        # 현재 환율 및 전일 환율 추출 (데이터 타입 에러 수정)
        # .iloc[-1]이 Series를 반환할 경우를 대비해 values[0]으로 접근
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

        # 3. 일자별 환율 상세 리스트 (요청하신 기능)
        st.subheader("📅 일자별 환율 상세 내역")
        
        # 표 데이터 가공
        display_df = pd.DataFrame(prices)
        display_df.columns = ['환율(종가)']
        display_df['전일대비'] = display_df['환율(종가)'].diff()
        
        # 최신 날짜가 위로 오게 정렬
        display_df = display_df.sort_index(ascending=False)

        # 테이블 출력
        st.dataframe(
            display_df.style.format("{:,.2f}"),
            use_container_width=True
        )

        st.info("💡 Halsey Ave 댁에서 확인하는 실시간 환율 정보입니다.")
    else:
        st.error("데이터를 가져오지 못했습니다.")
except Exception as e:
    st.error(f"오류 발생: {e}")

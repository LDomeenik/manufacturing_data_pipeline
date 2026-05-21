"""
raw_eda.py

EDA 화면 렌더링 모듈
"""


import streamlit as st


# render_eda_page: EDA 화면 렌더링
def render_eda_page():
    """
    Raw 스키마의 EDA 화면을 렌더링합니다.

    Args:
        없음

    Returns:
        없음

    Raises:
        없음
    """

    # 화면 제목
    st.title("EDA")

    # 경고 화면 출력
    st.warning(
        """
        아직 EDA 기능은 연결 전입니다.  
        QC 완료 후 주문, 재고, 공정, 생산, 설비 센서 EDA를 추가합니다.
        """
    )
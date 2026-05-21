"""
raw_load.py

Raw 데이터 적재 화면 렌더링 모듈
"""

import streamlit as st


# render_raw_load_page: Raw 적재 화면 렌더링
def render_raw_load_page() -> None:
    """
    Raw 데이터 적재 화면을 렌더링합니다.

    Args:
        없음
    
    Returns:
        없음
    
    Raises:
        없음
    """

    # 화면 제목
    st.title("Raw 데이터 적재")

    # 경고 화면 출력
    st.warning(
        """
        아직 Raw 적재 기능을 연결 전입니다.
        다음 단계에서는 SQLite 연결 및 CSV 적재 기능을 추가합니다.
        """
    )
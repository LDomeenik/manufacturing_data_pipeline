"""
raw_table.py

Raw 테이블 조회 화면 렌더링 모듈
"""


import streamlit as st


# render_raw_table_page: Raw 테이블 조회 화면 렌더링
def render_raw_table_page() -> None:
    """
    Raw 테이블 조회 화면을 렌더링합니다.

    Args:
        없음

    Returns:
        없음

    Raises:
        없음
    """

    # 화면 제목
    st.title("Raw 테이블 조회")

    # 경고 화면 출력
    st.warning(
        """
        아직 Raw 테이블 조회 기능은 연결 전입니다.  
        Raw 적재 기능 구현 후 테이블 미리보기를 추가합니다.
        """
    )
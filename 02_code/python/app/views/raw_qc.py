"""
raw_qc.py

Raw QC 화면 렌더링 모듈
"""


import streamlit as st


# render_qc_page: QC 화면 렌더링
def render_qc_page() -> None:
    """
    Raw QC 화면을 렌더링합니다.

    Args:
        없음

    Returns:
        없음

    Raises:
        없음
    """

    # 화면 제목
    st.title("Raw QC")

    # 경고 화면 출력
    st.warning(
        """
        아직 QC 기능은 연결 전입니다.  
        Raw 적재 이후 row count, PK 중복, 관계 정합성 검증을 추가합니다.
        """
    )
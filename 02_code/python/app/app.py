"""
app.py

생산관리 데이터 파이프라인 Streamlit 앱 실행 진입점

기능:
    - Streamlit 페이지 기본 설정
    - 사이드바 메뉴 구성
    - 선택된 메뉴에 따라 페이지 렌더링
"""


import streamlit as st

from views.home import render_home_page
from views.raw_load import render_raw_load_page
from views.raw_table import render_raw_table_page
from views.raw_qc import render_qc_page
from views.raw_eda import render_eda_page


# main: Streamlit 앱 실행
def main() -> None:
    """
    Streamlit 앱의 메인 실행 흐름을 제어합니다.

    Args:
        없음
    
    Returns:
        없음
    
    Raises:
        없음
    """

    # 페이지 설정
    st.set_page_config(
        page_title="생산관리 데이터 파이프라인",
        page_icon="🏭",
        layout="wide"
    )

    # 사이드바 설정
    st.sidebar.title("메뉴")

    selected_menu = st.sidebar.radio(
        "이동할 화면을 선택하세요.",
        [
            "홈",
            "Raw 데이터 적재",
            "Raw 테이블 조회",
            "Raw QC",
            "EDA"
        ]
    )

    if selected_menu == "홈":
        render_home_page()
    
    elif selected_menu == "Raw 데이터 적재":
        render_raw_load_page()
    
    elif selected_menu == "Raw 테이블 조회":
        render_raw_table_page()
    
    elif selected_menu == "Raw QC":
        render_qc_page()
    
    elif selected_menu == "EDA":
        render_eda_page()

if __name__ == "__main__":
    main()
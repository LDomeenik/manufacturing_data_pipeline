"""
home.py

홈 화면 렌더링 모듈

기능:
    - 프로젝트 개요 출력
    - 개발 단계 안내
"""


import streamlit as st


# render_home_page: 홈 화면 렌더링
def render_home_page() -> None:
    """
    홈 화면을 렌더링합니다.

    Args:
        없음
    
    Returns:
        없음
    
    Raises:
        없음
    """

    # 홈 화면 제목
    st.title("생산관리 데이터 파이프라인")
    st.caption("Manufacturing Data Pipeline Dashboard")

    # 프로젝트 개요 출력
    st.markdown(
        """
        본 앱은 주문, 재고, 공정, 생산 이력, 설비 센서 데이터를 기반으로
        생상관리 분석 파이프라인을 실행하고 결과를 확인하기 위한 대시보드입니다.

        현재 MVP 단계에서는 다음 기능을 우선 제공합니다.

        - Raw 데이터 적재
        - Raw 테이블 조회
        - Raw QC 결과 확인
        - 기초 EDA 결과 확인
        """
    )

    st.divider()

    # 부제목
    st.subheader("현재 개발 단계")

    st.info(
        """
        1단계: Streamlit 앱 기본 구조 생성\n
        2단계: SQLite 연결\n
        3단계: Raw CSV 적재\n
        4단계: Raw QC\n
        5단계: EDA
        """
    )
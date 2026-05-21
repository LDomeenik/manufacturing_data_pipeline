"""
raw_table.py

Raw 테이블 조회 화면 렌더링 모듈
"""


import streamlit as st

from services.db.connection import get_engine
from services.raw.get_raw_table import (get_table_row_count, get_table_preview)


# 조회 가능한 Raw 테이블 목록
RAW_TABLES = [
    "raw_orders",
    "raw_inventory",
    "raw_process",
    "raw_production_log",
    "raw_machine_sensor"
]


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

    st.info(
        """
        SQLite Raw 테이블 데이터를 조회합니다.
        """
    )

    st.divider()

    # SQLite Engine 생성
    engine = get_engine()

    # 테이블 선택
    selected_table = st.selectbox(
        "조회할 Raw 테이블을 선택하세요.",
        RAW_TABLES
    )

    # Row Count 조회
    try:
        row_count = get_table_row_count(
            engine=engine,
            table_name=selected_table
        )

        st.subheader("테이블 정보")

        st.write(f"테이블명: {selected_table}")
        st.write(f"Row 수: {row_count:,}")

        st.divider()

        # Preview Row 수 선택
        preview_limit = st.slider(
            "미리보기 Row 수",
            min_value=5,
            max_value=100,
            value=50,
            step=5
        )

        # Preview 조회
        preview_df = get_table_preview(
            engine=engine,
            table_name=selected_table,
            limit=preview_limit
        )

        st.subheader("테이블 미리보기")

        st.dataframe(
            preview_df,
            use_container_width=True
        )

    except Exception as e:
        st.error("Raw 테이블 조회 실패")
        st.exception(e)
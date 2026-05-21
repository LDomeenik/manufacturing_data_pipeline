"""
raw_load.py

Raw 데이터 적재 화면 렌더링 모듈
"""

import streamlit as st

from services.db.connection import get_engine
from services.raw.create_raw_tables import create_raw_tables
from services.raw.load_raw_data import load_all_raw_data


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

    # 안내 문구
    st.info(
        """
        이 화면에서는 SQLite DB에 Raw 테이블을 생성하고,
        이후 CSV 데이터를 Raw 테이블에 적재합니다.
        """
    )

    st.divider()

    # Raw 테이블 생성 영역
    st.subheader("1. Raw 테이블 생성")

    if st.button("Raw 테이블 생성"):
        try:
            engine = get_engine()
            create_raw_tables(engine)

            st.success("Raw 테이블 생성 완료")
        
        except Exception as e:
            st.error("Raw 테이블 생성 실패")
            st.exception(e)
    
    st.divider()

    # CSV 적재 영역
    st.subheader("2. Raw CSV 적재")

    if st.button("Raw CSV 적재"):
        try:
            engine = get_engine()

            loaded_counts = load_all_raw_data(engine)

            st.success("Raw CSV 적재 완료")

            st.subheader("적재 결과")

            for table_name, row_count in loaded_counts.items():
                st.write(f"- {table_name}: {row_count:,} rows")
        
        except Exception as e:
            st.error("Raw CSV 적재 실패")
            st.exception(e)
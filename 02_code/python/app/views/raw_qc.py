"""
raw_qc.py

Raw QC 화면 렌더링 모듈

기능:
    - 전체 Raw QC 실행
    - 테이블별 QC 결과 선택 조회
    - QC 이상 여부 표시
"""


import pandas as pd
import streamlit as st

from services.db.connection import get_engine
from services.raw.qc_raw_data import run_all_raw_qc


# is_problem_check: QC 결과가 이상 여부 확인용인지 판단
def is_problem_check(check_name: str) -> bool:
    """
    QC 항목이 비어 있어야 정상인 검증 항목인지 판단합니다.

    Args:
        check_name (str): QC 항목명

    Returns:
        bool: 이상 여부 확인 항목 여부

    Raises:
        없음
    """

    non_problem_checks = [
        "샘플 데이터",
        "Row Count",
        "필수 컬럼 NULL/공백 확인",
        "납기일 생성 규칙",
    ]

    return check_name not in non_problem_checks


# get_qc_description: QC 항목 설명 반환
def get_qc_description(table_name: str, check_name: str) -> str:
    """
    테이블명과 QC 항목명에 따른 설명 문구를 반환합니다.

    Args:
        table_name (str): Raw 테이블명
        check_name (str): QC 항목명

    Returns:
        str: QC 설명 문구

    Raises:
        없음
    """

    descriptions = {
        "raw_orders": {
            "샘플 데이터": "주문 데이터가 의도한 컬럼 구조와 값 형태로 적재되었는지 일부 데이터를 확인합니다.",
            "Row Count": "주문 테이블의 전체 적재 건수를 확인합니다. 현재 기준 기대 row 수는 150건입니다.",
            "PK 중복 확인": "주문 고유 식별자인 order_id가 중복으로 존재하는지 확인합니다. 결과가 비어 있으면 정상입니다.",
            "필수 컬럼 NULL/공백 확인": "order_id, product_id, order_qty, order_date, due_date 필수 컬럼에 NULL 또는 공백이 있는지 확인합니다.",
            "주문 수량 정합성": "order_qty가 0 이하인 주문이 있는지 확인합니다. 주문 수량은 반드시 양수여야 합니다.",
            "납기일 정합성": "due_date가 order_date보다 빠른 주문이 있는지 확인합니다. 납기일은 주문일보다 빠를 수 없습니다.",
            "납기일 생성 규칙": "최소 납기일이 최대 주문일 기준 3일 이후인지 확인합니다. qc_result가 PASS이면 정상입니다.",
            "raw_process 조인 정합성": "주문 데이터의 product_id가 공정 기준 테이블 raw_process에 존재하는지 확인합니다.",
        },
        "raw_inventory": {
            "샘플 데이터": "원자재 재고 데이터가 의도한 컬럼 구조와 값 형태로 적재되었는지 일부 데이터를 확인합니다.",
            "Row Count": "재고 테이블의 전체 적재 건수를 확인합니다. 현재 기준 기대 row 수는 100건입니다.",
            "PK 중복 확인": "원자재 고유 식별자인 material_id가 중복으로 존재하는지 확인합니다. 결과가 비어 있으면 정상입니다.",
            "필수 컬럼 NULL/공백 확인": "material_id, unit_price, stock_qty, lead_time 필수 컬럼에 NULL 또는 공백이 있는지 확인합니다.",
            "현재 재고 수량 정합성": "stock_qty가 음수인 원자재가 있는지 확인합니다. 현재 재고 수량은 음수가 될 수 없습니다.",
            "객단가 정합성": "unit_price가 0 이하인 원자재가 있는지 확인합니다. 원자재 단가는 양수여야 합니다.",
            "입고 예정 수량 정합성": "incoming_qty가 음수인 데이터가 있는지 확인합니다. 입고 예정 수량은 음수가 될 수 없습니다.",
            "리드타임 정합성": "lead_time이 0 이하인 데이터가 있는지 확인합니다. 리드타임은 양수여야 합니다.",
            "raw_process 조인 정합성": "공정 기준 테이블 raw_process의 material_id가 재고 테이블 raw_inventory에 존재하는지 확인합니다.",
        },
        "raw_process": {
            "샘플 데이터": "제품별 공정/BOM 기준 데이터가 의도한 컬럼 구조와 값 형태로 적재되었는지 일부 데이터를 확인합니다.",
            "Row Count": "공정 기준 테이블의 전체 적재 건수를 확인합니다. 현재 기준 기대 row 수는 297건입니다.",
            "PK 중복 확인": "product_id, process_id, material_id 조합이 중복으로 존재하는지 확인합니다. 결과가 비어 있으면 정상입니다.",
            "필수 컬럼 NULL/공백 확인": "product_id, process_id, material_id, process_step, required_material_qty, standard_cycle_time 필수 컬럼에 NULL 또는 공백이 있는지 확인합니다.",
            "process_id 정합성": "process_id가 A, B, C, D, E 중 하나로 구성되어 있는지 확인합니다.",
            "process_step 매핑 정합성": "process_id와 process_step이 A=1, B=2, C=3, D=4, E=5 기준으로 올바르게 매핑되었는지 확인합니다.",
            "필요 원자재 수량 정합성": "required_material_qty가 0 이하인 데이터가 있는지 확인합니다. 필요 원자재 수량은 양수여야 합니다.",
            "표준 작업 시간 정합성": "standard_cycle_time이 0 이하인 데이터가 있는지 확인합니다. 표준 작업 시간은 양수여야 합니다.",
            "제품별 A-E 공정 존재 확인": "각 product_id가 A부터 E까지 5개 공정을 모두 가지고 있는지 확인합니다.",
            "raw_inventory 조인 정합성": "공정 기준 테이블의 material_id가 재고 테이블 raw_inventory에 존재하는지 확인합니다.",
            "raw_orders 조인 정합성": "주문 테이블 raw_orders의 product_id가 공정 기준 테이블 raw_process에 존재하는지 확인합니다.",
        },
        "raw_production_log": {
            "샘플 데이터": "과거 생산 실행 이력 데이터가 의도한 컬럼 구조와 값 형태로 적재되었는지 일부 데이터를 확인합니다.",
            "Row Count": "생산 이력 테이블의 전체 적재 건수를 확인합니다. 현재 기준 기대 row 수는 5,000건입니다.",
            "PK 중복 확인": "lot_id, process_id 조합이 중복으로 존재하는지 확인합니다. 결과가 비어 있으면 정상입니다.",
            "필수 컬럼 NULL/공백 확인": "lot_id, process_id, order_id, product_id, machine_id, total_work_time, setup_time, downtime 필수 컬럼에 NULL 또는 공백이 있는지 확인합니다.",
            "process_id 정합성": "process_id가 A, B, C, D, E 중 하나로 구성되어 있는지 확인합니다.",
            "총 작업 시간 정합성": "total_work_time이 0 이하인 생산 이력이 있는지 확인합니다. 총 작업 시간은 양수여야 합니다.",
            "준비 시간 정합성": "setup_time이 음수인 생산 이력이 있는지 확인합니다. 준비 시간은 음수가 될 수 없습니다.",
            "중단 시간 정합성": "downtime이 음수인 생산 이력이 있는지 확인합니다. 중단 시간은 음수가 될 수 없습니다.",
            "lot별 A-E 공정 존재 확인": "각 lot_id가 A부터 E까지 5개 공정을 모두 가지고 있는지 확인합니다.",
            "raw_process product_id 조인 정합성": "생산 이력의 product_id가 공정 기준 테이블 raw_process에 존재하는지 확인합니다.",
            "raw_process process_id 조인 정합성": "생산 이력의 process_id가 공정 기준 테이블 raw_process에 존재하는지 확인합니다.",
            "raw_process product_id + process_id 조인 정합성": "생산 이력의 product_id와 process_id 조합이 공정 기준 테이블 raw_process에 존재하는지 확인합니다.",
        },
        "raw_machine_sensor": {
            "샘플 데이터": "설비 센서 데이터가 의도한 컬럼 구조와 값 형태로 적재되었는지 일부 데이터를 확인합니다.",
            "Row Count": "설비 센서 테이블의 전체 적재 건수를 확인합니다. 현재 기준 기대 row 수는 234,777건입니다.",
            "PK 중복 확인": "lot_id, unit_id, process_id, machine_id 조합이 중복으로 존재하는지 확인합니다. 결과가 비어 있으면 정상입니다.",
            "필수 컬럼 NULL/공백 확인": "lot_id, unit_id, process_id, machine_id와 주요 센서 변수 및 failure_target에 NULL 또는 공백이 있는지 확인합니다.",
            "process_id 정합성": "process_id가 A, B, C, D, E 중 하나로 구성되어 있는지 확인합니다.",
            "failure_target 정합성": "failure_target 값이 0 또는 1로만 구성되어 있는지 확인합니다.",
            "raw_production_log 조인 정합성": "센서 데이터의 lot_id, process_id, machine_id 조합이 생산 이력 테이블 raw_production_log에 존재하는지 확인합니다.",
            "production_log 기준 sensor 누락 확인": "생산 이력에는 존재하지만 센서 데이터에는 없는 lot_id, process_id, machine_id 조합이 있는지 확인합니다.",
        },
    }

    return descriptions.get(table_name, {}).get(
        check_name,
        "선택한 QC 항목의 결과를 확인합니다."
    )


# render_qc_result: QC 결과 출력
def render_qc_result(
    table_name: str,
    check_name: str,
    df: pd.DataFrame
) -> None:
    """
    QC 결과를 화면에 출력합니다.

    Args:
        table_name (str): Raw 테이블명
        check_name (str): QC 항목명
        df (pd.DataFrame): QC 결과 DataFrame

    Returns:
        None

    Raises:
        없음
    """

    st.subheader(check_name)
    st.caption(get_qc_description(table_name, check_name))

    if is_problem_check(check_name) and df.empty:
        st.success("이상 없음")

    elif is_problem_check(check_name) and not df.empty:
        st.warning("확인 필요")
        st.dataframe(df, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)


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

    st.title("Raw QC")

    st.info(
        """
        전체 Raw 테이블의 기본 정보, 중복, NULL, 로직 정합성, 조인 정합성을 확인합니다.  
        QC 실행 후 테이블과 QC 항목을 선택하여 결과를 확인할 수 있습니다.
        """
    )

    st.divider()

    engine = get_engine()

    if "raw_qc_results" not in st.session_state:
        st.session_state["raw_qc_results"] = None

    if st.button("Raw QC 전체 실행"):
        try:
            st.session_state["raw_qc_results"] = run_all_raw_qc(engine)
            st.success("Raw QC 전체 실행 완료")

        except Exception as e:
            st.error("Raw QC 실행 실패")
            st.exception(e)

    st.divider()

    if st.session_state["raw_qc_results"] is None:
        st.warning("먼저 Raw QC 전체 실행 버튼을 눌러주세요.")
        return

    qc_results = st.session_state["raw_qc_results"]

    selected_table = st.selectbox(
        "QC 결과를 확인할 테이블을 선택하세요.",
        list(qc_results.keys())
    )

    selected_check = st.radio(
        "QC 항목을 선택하세요.",
        list(qc_results[selected_table].keys())
    )

    st.divider()

    result_df = qc_results[selected_table][selected_check]

    st.caption(f"선택 테이블: {selected_table}")
    render_qc_result(
        table_name=selected_table,
        check_name=selected_check,
        df=result_df
    )
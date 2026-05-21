"""
make_orders.py

데이터 명세서 기준 raw_orders.csv 생성 스크립트

기능:
    - process.csv의 product_id 기준 주문 데이터 생성
    - 2026-05-04 ~ 2026-05-15 주문 접수 기간 반영 (주말 제외)
    - 2026-05-18 생산 시작 기준 납기일 생성 (+3D)
    - raw_orders.csv 저장
"""


import pandas as pd
import numpy as np
from pathlib import Path


# 기준 설정
RANDOM_SEED = 42
N_ORDERS = 150

ORDER_START_DATE = pd.to_datetime("2026-05-04")
ORDER_END_DATE = pd.to_datetime("2026-05-15")
PRODUCTION_START_DATE = pd.to_datetime("2026-05-18")
MIN_DUE_DATE = pd.to_datetime("2026-05-21")

PROCESS_PATH = Path("00_data/01_raw_data/process.csv")
OUTPUT_PATH = Path("00_data/01_raw_data/orders.csv")


# make_orders: raw_orders 데이터 생성
def make_orders(process_path: Path, output_path: Path) -> pd.DataFrame:
    """
    raw_orders 데이터를 생성하고 CSV로 저장합니다.

    Args:
        process_path (Path): process.csv 경로
        output_path (Path): 생성된 orders.csv 저장 경로
    
    Returns:
        pd.DataFrame: 생성된 raw_orders 데이터프레임
    
    Raises:
        FileNotFoundError: 입력 파일이 존재하지 않을 경우
        KeyError: 필요한 컬럼이 process.csv에 없을 경우
    """

    # 재현성 고정
    np.random.seed(RANDOM_SEED)

    # 입력 파일이 존재하지 않을 경우 에러
    if not process_path.exists():
        raise FileNotFoundError(f"process.csv가 존재하지 않습니다: {process_path}")
    
    # process 데이터 불러오기
    process = pd.read_csv(process_path)

    # 필수 컬럼 정의 및 필수 컬럼이 없는 경우 리스트로 저장
    required_columns = ["product_id"]
    missing_columns = [col for col in required_columns if col not in process.columns]

    # 필수 컬럼이 없다면 에러
    if missing_columns:
        raise KeyError(f"process.csv에 필요한 컬럼이 없습니다: {missing_columns}")
    
    # product_id 정렬
    product_ids = sorted(process["product_id"].dropna().unique())

    # order_id 생성
    order_ids = [f"ORD{str(i).zfill(6)}" for i in range (1, N_ORDERS + 1)]

    # 제품별 주문 비중 불균등 생성
    product_weights = np.random.dirichlet(np.ones(len(product_ids)) * 1.5)

    selected_products = np.random.choice(
        product_ids,
        size=N_ORDERS,
        replace=True,
        p=product_weights
    )

    # 주문 수량 생성
    order_qty = np.random.normal(
        loc=45,
        scale=18,
        size=N_ORDERS
    ).astype(int)

    order_qty = np.clip(order_qty, 5, 120)

    # 주문 일자 생성
    order_business_dates = pd.bdate_range(
        start=ORDER_START_DATE,
        end=ORDER_END_DATE
    )

    order_dates = np.random.choice(
        order_business_dates,
        size=N_ORDERS,
        replace=True
    )

    order_dates = pd.to_datetime(order_dates)

    # 납기일 생성
    # 최소 납기일은 2026-05-21
    # 일부는 빠른 납기, 일부는 여유 납기로 생성
    due_offsets = np.random.choice(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        size=N_ORDERS,
        p=[0.03, 0.05, 0.08, 0.12, 0.16, 0.18, 0.15, 0.10, 0.07, 0.04, 0.02]
    )

    due_buisness_dates = pd.bdate_range(
        start=MIN_DUE_DATE,
        periods=11
    )

    due_dates = due_buisness_dates[due_offsets]

    # orders 데이터셋 생성
    orders = pd.DataFrame({
        "order_id" : order_ids,
        "product_id" : selected_products,
        "order_qty" : order_qty,
        "order_date" : order_dates.date,
        "due_date" : due_dates.date
    })

    orders = orders.sort_values(
        ["order_date", "due_date", "order_id"]
    ).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(output_path, index=False, encoding="utf-8-sig")

    return orders


# main: 스크립트 실행
def main():
    """
    raw_orders 생성 스크립트 실행

    Raises:
        Exception: 데이터 생성 또는 저장 실패 시 예외 발생
    """

    try:
        orders = make_orders(PROCESS_PATH, OUTPUT_PATH)

        print("orders.csv 생성 완료")
        print(f"저장 경로: {OUTPUT_PATH}")
        print(f"데이터 크기: {orders.shape}")

        print("\n미리보기")
        print(orders.head())

        print("\n제품 수")
        print(orders["product_id"].nunique())

        print("\n주문일 범위")
        print(orders["order_date"].min(), "~", orders["order_date"].max())

        print("\n주말 주문 수")
        print((pd.to_datetime(orders["order_date"]).dt.weekday >= 5).sum())

        print("\n납기일 범위")
        print(orders["due_date"].min(), "~", orders["due_date"].max())

        print("\n주말 납기 수")
        print((pd.to_datetime(orders["due_date"]).dt.weekday >= 5).sum())

        print("\n주문 수량 요약")
        print(orders["order_qty"].describe().round(2))

        print("\nPK 중복 확인")
        print(orders["order_id"].duplicated().sum())

        print("\n결측치 확인")
        print(orders.isna().sum())
    
    except Exception as e:
        print(f"orders.csv 생성 실패: {e}")

if __name__ == "__main__":
    main()
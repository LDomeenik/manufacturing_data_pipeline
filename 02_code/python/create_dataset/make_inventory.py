"""
make_inventory.py

데이터 명세서 기준 raw_inventory.csv 생성 스크립트

기능:
    - Supply Chain 기반 inventory 원천 데이터 로드
    - raw_inventory 컬럼 구조로 재생성
    - CURRENT_DATE 기준 incoming_order_date 생성
    - CSV 파일 저장
"""


import pandas as pd
import numpy as np
from pathlib import Path


# 기준 설정
RANDOM_SEED = 42
CURRENT_DATE = pd.to_datetime("2026-05-15")

INPUT_PATH = Path("00_data/00_used_data/supply_chain_data.csv")
OUTPUT_PATH = Path("00_data/01_raw_data/inventory.csv")


# make_inventory: raw_inventory 데이터 생성
def make_inventory(input_path: Path, output_path: Path) -> pd.DataFrame:
    """
    raw_inventory 데이터를 생성하고 CSV로 저장합니다.

    Args:
        input_path (Path): Supply Chain 원본 데이터 경로
        output_path (Path): 생성된 inventory.csv 저장 경로
    
    Returns:
        pd.DataFrame: 생성된 raw_inventory 데이터프레임
    
    Raises:
        FileNotFoundError: 입력 파일이 존재하지 않을 경우
        KeyError: 필요한 컬럼이 원본 데이터에 없을 경우
    """

    # 재현성 고정
    np.random.seed(RANDOM_SEED)

    # 입력 파일이 존재하지 않을 경우 에러 발생
    if not input_path.exists():
        raise FileNotFoundError(f"입력 파일이 존재하지 않습니다: {input_path}")
    
    # 입력 파일 불러오기
    df = pd.read_csv(input_path)

    # inventory 테이블 생성에 필요한 Souce 컬럼 정의
    required_columns = [
        "SKU",
        "Price",
        "Stock levels",
        "Order quantities",
        "Lead time"
    ]

    # Source 컬럼으로 필요하지만 불러온 파일에는 없는 컬럼 리스트 저장
    missing_columns = [col for col in required_columns if col not in df.columns]

    # missing_columns가 있는 경우 에러 발생
    if missing_columns:
        raise KeyError(f"원본 데이터에 필요한 컬럼이 없습니다: {missing_columns}")
    
    inventory = df[required_columns].copy()

    inventory = inventory.rename(
        columns={
            "SKU" : "material_id",
            "Price" : "unit_price",
            "Stock levels" : "stock_qty",
            "Order quantities" : "base_incoming_qty",
            "Lead time" : "lead_time"
        }
    )

    # material_id 재정의: "SKU0001 형식"
    inventory["material_id"] = [
        f"SKU{str(i).zfill(4)}" for i in range(1, len(inventory) + 1)
    ]

    # 타입 정리
    inventory["unit_price"] = inventory["unit_price"].round(2)
    inventory["stock_qty"] = inventory["stock_qty"].astype(int).clip(lower=0)
    inventory["base_incoming_qty"] = inventory["base_incoming_qty"].astype(int).clip(lower=0)
    inventory["lead_time"] = inventory["lead_time"].astype(int).clip(lower=1, upper=10)

    # 입고 예정 여부 생성
    # 0: 입고 예정 없음
    # 1: 이미 발주했지만 CURRENT_DATE 기준 아직 입고되지 않은 상태
    inventory["has_incoming"] = np.random.choice(
        [0, 1],
        size=len(inventory),
        p=[0.65, 0.35]
    )

    incoming_qty_list = []
    incoming_order_date_list = []

    for _, row in inventory.iterrows():
        has_incoming = row["has_incoming"]
        lead_time = int(row["lead_time"])
        base_incoming_qty = int(row["base_incoming_qty"])

        if has_incoming == 0 or lead_time <= 1:
            incoming_qty_list.append(0)
            incoming_order_date_list.append(None)
            continue
    
        # 입고 예정 수량
        incoming_qty = max(base_incoming_qty, 1)

        # CURRENT_DATE 기준 아직 입고되지 않은 발주일 생성
        # 조건:
        #   incoming_order_date < CURRENT_DATE
        #   incoming_order_date + lead_time > CURRENT_DATE
        max_days_before = lead_time - 1
        days_before = np.random.randint(1, max_days_before + 1)

        incoming_order_date = (
            CURRENT_DATE - pd.to_timedelta(days_before, unit="D")
        ).date()

        incoming_qty_list.append(incoming_qty)
        incoming_order_date_list.append(incoming_order_date)

    inventory["incoming_qty"] = incoming_qty_list
    inventory["incoming_order_date"] = incoming_order_date_list

    inventory = inventory[
        [
            "material_id",
            "unit_price",
            "stock_qty",
            "incoming_qty",
            "incoming_order_date",
            "lead_time"
        ]
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(output_path, index=False, encoding="utf-8-sig")

    return inventory


# main: 스크립트 실행
def main():
    """
    raw_inventory 생성 스크립트 실행

    Raises:
        Exception: 데이터 생성 또는 저장 실패 시 예외 발생
    """
    try:
        inventory = make_inventory(INPUT_PATH, OUTPUT_PATH)
    
        print("inventory.csv 생성 완료")
        print(f"저장 경로: {OUTPUT_PATH}")
        print(f"데이터 크기: {inventory.shape}")

        print("\n미리보기")
        print(inventory.head())

        print("\n입고 예정 여부")
        print((inventory["incoming_qty"] > 0).value_counts())

        print("\n결측치 확인")
        print(inventory.isna().sum())

    except Exception as e:
        print(f"저장 실패: {e}")

if __name__ == "__main__":
    main()
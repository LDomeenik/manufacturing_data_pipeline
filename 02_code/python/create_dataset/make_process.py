"""
make_process.py

데이터 명세서 기준 raw_process.csv 생성 스크립트

기능:
    - inventory.csv의 material_id를 기준으로 공정별 원자재 매핑
    - Manufacturing Predictive Dataset 기반 공정별 표준 작업 시간 생성
    - 제품별 A~E 공정/BOM 기준 데이터 생성
    - CSV 파일 저장
"""


import pandas as pd
import numpy as np
from pathlib import Path


# 기준 설정
RANDOM_SEED = 42
PRODUCT_GROUP_SIZES = [7, 5, 4, 4]
N_PRODUCTS = sum(PRODUCT_GROUP_SIZES)
GROUP_MATERIAL_POOL_SIZE = 30
GROUP_MATERIAL_RATIO = 0.7

INVENTORY_PATH = Path("00_data/01_raw_data/inventory.csv")
MFG_PATH = Path("00_data/00_used_data/hybrid_manufacturing_categorical.csv")
OUTPUT_PATH = Path("00_data/01_raw_data/process.csv")


# make_process: raw_process 데이터 생성
def make_process(
        inventory_path: Path,
        mfg_path: Path,
        output_path: Path
) -> pd.DataFrame:
    """
    raw_process 데이터를 생성하고 CSV로 저장합니다.

    Args:
        inventory_path (Path): inventory.csv 경로
        mfg_path (Path): Manufacturing 원본 데이터 경로
        output_path (Path): 생성된 process.csv 저장 경로
    
    Returns:
        pd.DataFrame: 생성된 raw_process 데이터프레임
    
    Raises:
        FileNotFoundError: 입력 파일이 존재하지 않을 경우
        KeyError: 필요한 컬럼이 원본 데이터에 없을 경우
        ValueError: 제품군 또는 원자재 pool 생성 조건이 맞지 않을 경우
    """

    # 재현성 고정
    np.random.seed(RANDOM_SEED)

    # inventory 데이터셋이 존재하지 않을 경우 에러
    if not inventory_path.exists():
        raise FileNotFoundError(f"inventory.csv가 존재하지 않습니다: {inventory_path}")
    
    # 소스 데이터셋이 존재하지 않을 경우 에러
    if not mfg_path.exists():
        raise FileNotFoundError(f"Manufacturing 원본 파일이 존재하지 않습니다: {mfg_path}")
    
    # inventory 데이터셋과 소스 데이터셋 불러오기
    inventory = pd.read_csv(inventory_path)
    mfg = pd.read_csv(mfg_path)

    # 각 데이터셋에서 필요한 컬럼 정의
    inventory_required_columns = ["material_id"]
    mfg_required_columns = ["Operation_Type", "Processing_Time"]

    # 각 데이터셋에서 부족한 컬럼을 리스트로 저장
    missing_inventory_columns = [
        col for col in inventory_required_columns if col not in inventory.columns
    ]

    missing_mfg_columns = [
        col for col in mfg_required_columns if col not in mfg.columns
    ]

    # 리스트가 있다면 에러
    if missing_inventory_columns:
        raise KeyError(f"inventory.csv에 필요한 컬럼이 없습니다: {missing_inventory_columns}")
    
    if missing_mfg_columns:
        raise KeyError(f"Manufacturing 데이터에 필요한 컬럼이 없습니다: {missing_mfg_columns}")
    
    # 조인 키가 될 material_id 정렬
    material_ids = sorted(inventory["material_id"].dropna().unique())

    # material_id별로 원자재 pool 조정
    if len(material_ids) < GROUP_MATERIAL_POOL_SIZE:
        raise ValueError(
            f"원자재 수가 제품군 material pool 크기보다 적습니다. "
            f"원자재 수: {len(material_ids)}, pool 크기: {GROUP_MATERIAL_POOL_SIZE}"
        )

    # product_id 정의
    product_ids = [
        f"PRD{str(i).zfill(4)}" for i in range(1, N_PRODUCTS + 1)
    ]

    # 제품군 정의
    product_group_map = {}

    start_idx = 0

    for group_idx, group_size in enumerate(PRODUCT_GROUP_SIZES, start=1):
        group_id = f"GROUP_{group_idx}"

        for product_id in product_ids[start_idx:start_idx + group_size]:
            product_group_map[product_id] = group_id
        
        start_idx += group_size

    # 제품군별 공통 원자재 pool 생성
    group_material_pool = {}

    for group_id in sorted(set(product_group_map.values())):
        group_material_pool[group_id] = np.random.choice(
            material_ids,
            size=GROUP_MATERIAL_POOL_SIZE,
            replace=False
        )

    # process_id, process_step, process_name 연결
    process_master = [
        ("A", 1, "Milling"),
        ("B", 2, "Lathe"),
        ("C", 3, "Drilling"),
        ("D", 4, "Grinding"),
        ("E", 5, "Additive")
    ]

    # 공정별 평균 작업 시간 생성
    cycle_time_map = (
        mfg.groupby("Operation_Type")["Processing_Time"]
        .mean()
        .round(2)
        .to_dict()
    )

    # 공정별 원자재 필요 수량 범위
    required_qty_range = {
        "Milling": (2, 5),
        "Lathe": (2, 4),
        "Drilling": (1, 3),
        "Grinding": (1, 2),
        "Additive": (3, 6)
    }

    rows = []

    for product_id in product_ids:
        group_id = product_group_map[product_id]
        group_pool = group_material_pool[group_id]

        for process_id, process_step, process_name in process_master:
            n_materials = np.random.randint(2, 5)

            n_group_materials = max(1, int(round(n_materials * GROUP_MATERIAL_RATIO)))
            n_global_materials = n_materials - n_group_materials


            selected_group_materials = np.random.choice(
                group_pool,
                size=n_group_materials,
                replace=False
            )

            if n_global_materials > 0:
                selected_global_materials = np.random.choice(
                    material_ids,
                    size=n_global_materials,
                    replace=False
                )

                selected_materials = np.unique(
                    np.concatenate([selected_group_materials, selected_global_materials])
                )
            
            else:
                selected_materials = np.unique(selected_group_materials)
            
            while len(selected_materials) < n_materials:
                extra_material = np.random.choice(material_ids)
                selected_materials = np.unique(
                    np.append(selected_materials, extra_material)
                )

            base_cycle_time = cycle_time_map.get(process_name)

            if pd.isna(base_cycle_time):
                raise KeyError(f"공정명에 해당하는 Processing_Time이 없습니다: {process_name}")
            
            # 제품별 공정별 차이 부여
            standard_cycle_time = round(
                base_cycle_time * np.random.uniform(0.9, 1.1), 2
            )

            qty_low, qty_high = required_qty_range[process_name]

            for material_id in selected_materials:
                required_material_qty = np.random.randint(
                    qty_low,
                    qty_high + 1
                )

                rows.append({
                    "product_id" : product_id,
                    "process_id" : process_id,
                    "material_id" : material_id,
                    "process_step" : process_step,
                    "required_material_qty" : required_material_qty,
                    "standard_cycle_time" : standard_cycle_time
                })
    
    process = pd.DataFrame(rows)

    process = process[
        [
            "product_id",
            "process_id",
            "material_id",
            "process_step",
            "required_material_qty",
            "standard_cycle_time"
        ]
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    process.to_csv(output_path, index=False, encoding="utf-8-sig")

    return process


# main: 스크립트 실행
def main():
    """
    raw_process 생성 스크립트 실행

    Raises:
        Exception: 데이터 생성 또는 저장 실패 시 예외 발생
    """

    try:
        process = make_process(
            INVENTORY_PATH,
            MFG_PATH,
            OUTPUT_PATH
        )

        print("process.csv 생성 완료")
        print(f"저장 경로: {OUTPUT_PATH}")
        print(f"데이터 크기: {process.shape}")

        print("\n미리보기")
        print(process.head())

        print("\n제품 수")
        print(process["product_id"].nunique())

        print("\n공정별 row 수")
        print(process["process_id"].value_counts().sort_index())

        print("\n제품별 공정 수")
        print(
            process.groupby("product_id")["process_id"]
            .nunique()
            .value_counts()
            .sort_index()
        )

        print("\n제품별 평균 원자재 row 수")
        print(
            process.groupby("product_id")
            .size()
            .describe()
            .round(2)
        )

        print("\n제품별 공정별 원자재 사용 수")
        print(
            process.groupby(["product_id", "process_id"]).size()
        )

        print("\nPK 중복 확인")
        print(
            process.duplicated(
                subset=["product_id", "process_id", "material_id"]
            ).sum()
        )

        print("\n결측치 확인")
        print(process.isna().sum())

    except Exception as e:
        print(f"process.csv 생성 실패: {e}")


if __name__ == "__main__":
    main()
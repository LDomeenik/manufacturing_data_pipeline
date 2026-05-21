"""
make_production_log.py

데이터 명세서 기준 raw_production_log.csv 생성 스크립트

기능:
    - process.csv의 product_id/process_id 기준 과거 생산 lot 생성
    - 과거 생산 주문 ID 및 lot_id 생성
    - 공정별 설비 pool 기준 machine_id 배정
    - setup_time, downtime, total_work_time 생성
    - raw_production_log.csv 저장
"""


import pandas as pd
import numpy as np
from pathlib import Path


# 기준 설정
RANDOM_SEED = 42
N_LOTS = 1000

HISTORY_START_DATE = pd.to_datetime("2026-02-01")
HISTORY_END_DATE = pd.to_datetime("2026-04-30")

PROCESS_PATH = Path("00_data/01_raw_data/process.csv")
OUTPUT_PATH = Path("00_data/01_raw_data/production_log.csv")


# make_production_log: raw_production_log 데이터 생성
def make_production_log(process_path: Path, output_path: Path) -> pd.DataFrame:
    """
    raw_production_log 데이터를 생성하고 CSV로 저장합니다.

    Args:
        process_path (Path): process.csv 경로
        output_path (Path): 생성된 production_log.csv 저장 경로
    
    Returns:
        pd.DataFrame: 생성된 raw_production_log 데이터프레임
    
    Raises:
        FileNotFoundError: 입력 파일이 존재하지 않을 경우
        KeyError: 필요한 컬럼이 process.csv에 없을 경우
    """

    # 재현성 고정
    np.random.seed(RANDOM_SEED)

    # 입력 파일이 존재하지 않으면 에러
    if not process_path.exists():
        raise FileNotFoundError(f"process.csv가 존재하지 않습니다: {process_path}")
    
    # process 데이터 불러오기
    process = pd.read_csv(process_path)

    # 필수 컬럼 정의
    required_columns = [
        "product_id",
        "process_id",
        "process_step",
        "standard_cycle_time"
    ]

    # 필수 컬럼이지만 입력 데이터에 없는 컬럼을 리스트로 저장
    missing_columns = [col for col in required_columns if col not in process.columns]

    # 리스트가 있다면 에러
    if missing_columns:
        raise KeyError(f"process.csv에 필요한 컬럼이 없습니다: {missing_columns}")
    
    # product_id + process_id 기준 공정 기준 정보 생성
    process_master = (
        process[
            [
                "product_id",
                "process_id",
                "process_step",
                "standard_cycle_time"
            ]
        ]
        .drop_duplicates()
        .sort_values(["product_id", "process_step"])
        .reset_index(drop=True)
    )

    # product_id 정렬
    product_ids = sorted(process_master["product_id"].dropna().unique())

    # 공정별 설비 pool 정의
    machine_pool = {
        "A" : ["MILL_01", "MILL_02", "MILL_03", "MILL_04"],
        "B" : ["LATHE_01", "LATHE_02", "LATHE_03", "LATHE_04"],
        "C" : ["DRILL_01", "DRILL_02", "DRILL_03"],
        "D" : ["GRIND_01", "GRIND_02", "GRIND_03"],
        "E" : ["ADD_01", "ADD_02"]
    }

    # 공정별 setup_time 범위
    setup_time_range = {
        "A" : (15, 25),
        "B" : (15, 25),
        "C" : (15, 25),
        "D" : (15, 25),
        "E" : (15, 25)
    }

    # 공정별 downtime 발생 특성
    downtime_range = {
        "A" : [(0, 8), (8, 25)],
        "B" : [(0, 8), (8, 25)],
        "C" : [(0, 10), (10, 35)],
        "D" : [(0, 10), (10, 35)],
        "E" : [(0, 15), (15, 45)]
    }

    # 과거 생산 가능일: 평일만 생성
    history_business_dates = pd.bdate_range(
        start=HISTORY_START_DATE,
        end=HISTORY_END_DATE
    )

    rows = []

    for lot_idx in range(1, N_LOTS+1):
        lot_id = f"LOT{str(lot_idx).zfill(6)}"
        order_id = f"PORD{str(lot_idx).zfill(6)}"

        product_id = np.random.choice(product_ids)

        # 과거 생산 수량: machine_sensor 생성 시 unit 수량 기준으로도 활용
        lot_qty = int(
            np.clip(
                np.random.normal(loc=45, scale=18),
                5,
                120
            )
        )

        # 과거 생산 기준일
        production_date = np.random.choice(history_business_dates)
        production_date = pd.to_datetime(production_date).date()

        product_processes = (
            process_master[process_master["product_id"] == product_id]
            .sort_values("process_step")
        )

        for _, proc in product_processes.iterrows():
            process_id = proc["process_id"]
            process_step = int(proc["process_step"])
            standard_cycle_time = float(proc["standard_cycle_time"])

            machine_id = np.random.choice(machine_pool[process_id])

            setup_low, setup_high = setup_time_range[process_id]
            setup_time = round(np.random.uniform(setup_low, setup_high), 2)

            # 일부만 긴 downtime 부여
            normal_range, abnormal_range = downtime_range[process_id]

            downtime_type = np.random.choice(
                ["normal", "abnormal"],
                p=[0.85, 0.15]
            )

            if downtime_type == "normal":
                downtime = np.random.uniform(*normal_range)
            else:
                downtime = np.random.uniform(*abnormal_range)
            
            downtime = round(downtime, 2)

            # 총 작업 시간 계산
            # standard_cycle_time은 제품 1개당 초 단위 기준으로 사용
            # total_work_time은 lot 전체 공정 소요 시간(분)
            noise_factor = np.random.uniform(0.95, 1.15)

            total_work_time = (
                (standard_cycle_time * lot_qty * noise_factor) / 60
                + setup_time
                + downtime
            )

            total_work_time = round(total_work_time, 2)

            rows.append({
                "lot_id" : lot_id,
                "process_id" : process_id,
                "order_id" : order_id,
                "product_id" : product_id,
                "machine_id" : machine_id,
                "total_work_time" : total_work_time,
                "setup_time" : setup_time,
                "downtime" : downtime
            })

    # 데이터프레임으로 변환
    production_log = pd.DataFrame(rows)

    # 컬럼 지정
    production_log = production_log[
        [
            "lot_id",
            "process_id",
            "order_id",
            "product_id",
            "machine_id",
            "total_work_time",
            "setup_time",
            "downtime"
        ]
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    production_log.to_csv(output_path, index=False, encoding="utf-8-sig")

    return production_log


# main: 스크립트 실행
def main():
    """
    raw_production_log 생성 스크립트 실행

    Raises:
        Exception: 데이터 생성 또는 저장 실패 시 예외 발생
    """

    try:
        production_log = make_production_log(PROCESS_PATH, OUTPUT_PATH)

        print("production_log.csv 생성 완료")
        print(f"저장 경로: {OUTPUT_PATH}")
        print(f"데이터 크기: {production_log.shape}")

        print("\n미리보기")
        print(production_log.head())

        print("\nlot 수")
        print(production_log["lot_id"].nunique())

        print("\n공정별 row 수")
        print(production_log["process_id"].value_counts().sort_index())

        print("\nlot별 공정 수")
        print(
            production_log.groupby("lot_id")["process_id"]
            .nunique()
            .value_counts()
            .sort_index()
        )

        print("\n설비별 row 수")
        print(production_log["machine_id"].value_counts().sort_index())

        print("\n작업 시간 요약")
        print(production_log["total_work_time"].describe().round(2))

        print("\nPK 중복 확인")
        print(
            production_log.duplicated(
                subset=["lot_id", "process_id"]
            ).sum()
        )

        print("\n결측치 확인")
        print(production_log.isna().sum())

    except Exception as e:
        print(f"production_log.csv 생성 실패: {e}")

if __name__ == "__main__":
    main()
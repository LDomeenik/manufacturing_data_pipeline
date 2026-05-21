"""
load_raw_data.py

Raw CSV 데이터를 SQLite raw 테이블에 적재하는 모듈

기능:
    - Raw CSV 파일 존재 여부 확인
    - CSV 파일 로드
    - SQLite raw 테이블 적재
    - 테이블별 적재 row 수 반환
"""


from pathlib import Path

import pandas as pd
from sqlalchemy import Engine


# Raw 데이터 폴더 경로
RAW_DATA_DIR = Path("00_data/01_raw_data")

# Raw 테이블 ↔ CSV 파일 매핑
RAW_TABLES = {
    "raw_orders" : "orders.csv",
    "raw_inventory" : "inventory.csv",
    "raw_process" : "process.csv",
    "raw_production_log" : "production_log.csv",
    "raw_machine_sensor" : "machine_sensor.csv"
}


# load_csv_to_raw_table: 단일 CSV 파일 적재
def load_csv_to_raw_table(
        engine: Engine,
        table_name: str,
        csv_path: Path
) -> int:
    """
    단일 CSV 파일을 SQLite raw 테이블에 적재합니다.

    Args:
        engine (Engine): SQLAlchemy SQLite Engine
        table_name (str): 적재 대상 테이블명
        csv_path (Path): CSV 파일 경로
    
    Returns:
        int: 적재 row 수
    
    Raises:
        FileNotFoundError: CSV 파일이 존재하지 않을 경우
    """

    # CSV 파일 존재 여부 확인
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV 파일이 존재하지 않습니다: {csv_path}"
        )
    
    # CSV 파일 로드
    df = pd.read_csv(csv_path)

    # SQLite 테이블 적재
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    return len(df)


# load_all_raw_data: 전체 Raw CSV 적재
def load_all_raw_data(engine: Engine) -> dict:
    """
    전체 Raw CSV 데이터를 SQLite raw 테이블에 적재합니다.

    Args:
        engine (Engine): SQLAlchemy SQLite Engine
    
    Returns:
        dict: 테이블별 적재 row 수
    
    Raises:
        Exception: 적재 실패 시 예외 발생
    """

    loaded_counts = {}

    for table_name, file_name in RAW_TABLES.items():
        csv_path = RAW_DATA_DIR / file_name

        row_count = load_csv_to_raw_table(
            engine=engine,
            table_name=table_name,
            csv_path=csv_path
        )

        loaded_counts[table_name] = row_count
    
    return loaded_counts
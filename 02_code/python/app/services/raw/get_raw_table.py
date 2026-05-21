"""
get_raw_table.py

SQLite Raw 테이블 조회 모듈

기능:
    - Raw 테이블 row count 조회
    - Raw 테이블 데이터 조회
"""


import pandas as pd

from sqlalchemy import Engine


# get_table_row_count: 테이블 row 수 조회
def get_table_row_count(
    engine: Engine,
    table_name: str
) -> int:
    """
    SQLite 테이블 row 수를 조회합니다.

    Args:
        engine (Engine): SQLAlchemy SQLite Engine
        table_name (str): 조회 대상 테이블명
    
    Returns:
        int: 테이블 row 수
    
    Raises:
        Exception: 조회 실패 시 예외 발생
    """

    # Raw 테이블의 row 수 조회 sql
    query = f"""
    SELECT  COUNT(*) AS row_count
      FROM  {table_name}
    """

    result = pd.read_sql(query, engine)

    return int(result.loc[0, "row_count"])


# get_table_preview: 테이블 미리보기 조회
def get_table_preview(
    engine: Engine,
    table_name: str,
    limit: int = 50
) -> pd.DataFrame:
    """
    SQLite 테이블 상위 데이터를 조회합니다.

    Args:
        engine (Engine): SQLAlchemy SQLite Engine
        table_name (str): 조회 대상 테이블명
        limit (int): 조회 row 수
    
    Returns:
        pd.DataFrame: 조회 결과 DataFrame
    
    Raises:
        Exception: 조회 실패 시 예외 발생
    """

    # Raw 테이블 조회 sql
    query = f"""
    SELECT  *
      FROM  {table_name}
     LIMIT  {limit}
    """

    df = pd.read_sql(query, engine)

    return df
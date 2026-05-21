"""
connection.py

SQLite DB 연결 모듈

기능:
    - SQLite DB 파일 경로 정의
    - SQLAlchemy Engine 생성
    - DB 연결 테스트
"""

from pathlib import Path
from sqlalchemy import create_engine, text, Engine


# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parents[5]

# DB 파일 경로
DB_PATH = BASE_DIR / "manufacturing.db"


# get_engine: SQLite Engine 생성
def get_engine() -> Engine:
    """
    SQLite DB 연결 엔진을 생성합니다.

    Args:
        없음
    
    Returns:
        sqlalchemy.Engine: SQLite 연결 엔진
    
    Raises:
        없음
    """

    # sqlalchemy.Engine 생성
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )

    return engine


# test_connection: DB 연결 테스트
def test_connection() -> bool:
    """
    SQLite DB 연결 상태를 테스트합니다.

    Args:
        없음
    
    Returns:
        bool: 연결 성공 여부
    
    Raises:
        Exception: DB 연결 실패 시 예외 발생
    """

    # 엔진 정의
    engine = get_engine()

    # DB 연결 상태 테스트
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    return True
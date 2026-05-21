"""
connection.py

PostgreSQL DB 연결 모듈

기능:
    - .env 파일에서 DB 접속 정보 로드
    - SQLAlchemy Engine 생성
"""


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


# get_engine: SQLAlchemy 엔진 생성
def get_engine() -> None:
    """
    PostgreSQL 연결 엔진을 생성합니다.

    Args:
        없음
    
    Returns:
        sqlalchemy.Engine: PostgreSQL 연결 엔진
    
    Raises:
        ValueError: 필수 DB 환경변수가 누락된 경우
    """
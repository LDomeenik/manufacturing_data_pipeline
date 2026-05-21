"""
connection.py

SQLite DB 연결 모듈

기능:
    - SQLite DB 파일 경로 정의
    - SQLAlchemy Engine 생성
    - DB 연결 테스트
"""

from pathlib import Path
from sqlalchemy import create_engine, text



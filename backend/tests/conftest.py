import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DATABASE_PATH = BACKEND_DIR / "tests" / "test.db"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import Base  # noqa: E402
from app.models import answer, question  # noqa: F401, E402


@pytest.fixture()
def db_session():
    engine = create_engine(
        f"sqlite:///{TEST_DATABASE_PATH}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 지우면 데이터 확인 가능
        # Base.metadata.drop_all(bind=engine)
        engine.dispose()


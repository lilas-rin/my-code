import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app import models, utils
from app.database import Base, get_db
from app.main import app


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session")
def user_data():
    data_path = Path(__file__).parent / "test_data" / "user.json"
    with data_path.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def test_user(db_session, user_data):
    existing_user = user_data["existing_user"]
    user = models.User(
        email=existing_user["email"],
        password=utils.hash(existing_user["password"]),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

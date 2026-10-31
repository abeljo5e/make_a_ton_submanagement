import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend and repo root are in python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole, Customer
from app.core.security import hash_password, create_access_token


# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

TEST_ENGINE = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test function."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def client(db_session):
    """Override get_db dependency to point to in-memory test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seeded_admin(db_session):
    """Seed an admin user and return user and auth token."""
    admin = User(
        full_name="System Admin",
        email="admin@brightloop.test",
        password_hash=hash_password("AdminSecure#2026"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(
        data={"sub": str(admin.id), "role": admin.role.value, "email": admin.email}
    )
    return {"user": admin, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture(scope="function")
def seeded_staff(db_session):
    """Seed a staff user and return user and auth token."""
    staff = User(
        full_name="Support Staff",
        email="staff@brightloop.test",
        password_hash=hash_password("StaffSecure#2026"),
        role=UserRole.STAFF,
        is_active=True,
    )
    db_session.add(staff)
    db_session.commit()
    db_session.refresh(staff)
    token = create_access_token(
        data={"sub": str(staff.id), "role": staff.role.value, "email": staff.email}
    )
    return {"user": staff, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture(scope="function")
def seeded_customer(db_session):
    """Seed a customer user and return user, customer profile and auth token."""
    customer = User(
        full_name="Alice Customer",
        email="alice@customer.test",
        password_hash=hash_password("AliceSecure#2026"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db_session.add(customer)
    db_session.flush()

    profile = Customer(
        user_id=customer.id,
        company_name="Acme Corp",
        phone="+1234567890",
        address="123 Market St",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(customer)

    token = create_access_token(
        data={"sub": str(customer.id), "role": customer.role.value, "email": customer.email}
    )
    return {"user": customer, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

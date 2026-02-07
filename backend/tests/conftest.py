import pytest
from sqlalchemy.orm import Session

try:
    # when running inside container symlinked layout
    from app.database import engine, SessionLocal
except Exception:
    from backend.app.database import engine, SessionLocal

@pytest.fixture
def db() -> Session:
    """Provide a transactional SQLAlchemy Session for tests.

    This fixture starts a SAVEPOINT-style nested transaction so tests can commit
    freely and at the end of the test the whole transaction is rolled back,
    leaving the database in the original state.

    Implementation adapted from SQLAlchemy testing patterns.
    """
    connection = engine.connect()
    trans = connection.begin()

    # Ensure test emails used by fixtures don't already exist
    from sqlalchemy import text
    connection.execute(text("DELETE FROM users WHERE email IN ('test@example.com','admin@example.com','other@example.com')"))

    session = Session(bind=connection)

    # start a nested transaction (SAVEPOINT)
    session.begin_nested()

    try:
        yield session
        # if test commits successfully, it is still inside the nested transaction
    finally:
        session.rollback()
        session.close()
        trans.rollback()
        connection.close()

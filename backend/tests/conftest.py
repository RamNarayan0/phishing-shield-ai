import os
import pytest
from app.db.mongodb import init_db, close_db, _client

def pytest_sessionstart(session):
    """
    Called before running any tests: guarantees all tests use the isolated
    'phishing_shield_ai_test' database, keeping 'phishing_shield_ai' pristine.
    """
    os.environ["MONGODB_DATABASE"] = "phishing_shield_ai_test"
    init_db(db_name="phishing_shield_ai_test")

def pytest_sessionfinish(session, exitstatus):
    """
    Called after all tests complete: drops the isolated test database
    and restores the default environment.
    """
    if _client is not None:
        try:
            _client.drop_database("phishing_shield_ai_test")
        except Exception:
            pass
    close_db()
    os.environ["MONGODB_DATABASE"] = "phishing_shield_ai"

@pytest.fixture(autouse=True)
def ensure_test_database_clean():
    """Ensures each test operates on an isolated clean slate in the test database."""
    init_db(db_name="phishing_shield_ai_test")
    yield

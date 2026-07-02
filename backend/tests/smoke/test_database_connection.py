from app.shared.config.settings import get_settings
from app.shared.db.session import verify_database_connection


def test_database_connection() -> None:
    settings = get_settings()
    assert verify_database_connection(settings.database_url) is True

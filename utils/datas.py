import os
from datetime import datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo(os.environ.get("APP_TIMEZONE", "America/Sao_Paulo"))


def hoje():
    """Data corrente no fuso horário da aplicação."""
    return datetime.now(FUSO).date()

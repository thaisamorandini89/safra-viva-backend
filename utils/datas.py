import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo(os.environ.get("APP_TIMEZONE", "America/Sao_Paulo"))


def hoje():
    """Data corrente no fuso horário da aplicação."""
    return datetime.now(FUSO).date()


def data_do_parametro(valor, nome):
    """Converte um parâmetro de consulta no formato AAAA-MM-DD em data; vazio vira None."""
    if not valor:
        return None
    try:
        return date.fromisoformat(valor.strip())
    except ValueError:
        raise ValueError(f"O parâmetro '{nome}' deve ser uma data no formato AAAA-MM-DD.")

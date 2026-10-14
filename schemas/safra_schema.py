from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SafraCreate(BaseModel):
    """Payload de criação de safra."""
    nome: str = Field(min_length=1, max_length=200)
    cultura: str = Field(min_length=1, max_length=100)
    id_propriedade: int
    data_inicio: date
    data_fim: Optional[date] = None
    area_plantada: Optional[Decimal] = Field(default=None, ge=0)

    @field_validator('nome', 'cultura', mode='before')
    @classmethod
    def limpar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class SafraOut(BaseModel):
    """Resposta de safra."""
    id_safra: int
    nome: str
    cultura: str
    id_propriedade: int
    nome_propriedade: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    area_plantada: Optional[float] = None
    status: Optional[bool] = None

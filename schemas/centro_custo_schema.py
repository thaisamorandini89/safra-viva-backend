from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CentroCustoCreate(BaseModel):
    """Payload de criação de centro de custo."""
    nome: str = Field(min_length=1, max_length=150)
    tipo: Literal['OPERACIONAL', 'ADMINISTRATIVO']
    descricao: Optional[str] = Field(default=None, max_length=500)

    @field_validator('tipo', mode='before')
    @classmethod
    def normalizar_tipo(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor

    @field_validator('nome', mode='before')
    @classmethod
    def limpar_nome(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class CentroCustoUpdate(BaseModel):
    """Payload de edição de centro de custo; só os campos enviados são alterados."""
    nome: Optional[str] = Field(default=None, min_length=1, max_length=150)
    tipo: Optional[Literal['OPERACIONAL', 'ADMINISTRATIVO']] = None
    descricao: Optional[str] = Field(default=None, max_length=500)
    status: Optional[bool] = None

    @field_validator('tipo', mode='before')
    @classmethod
    def normalizar_tipo(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor

    @field_validator('nome', mode='before')
    @classmethod
    def limpar_nome(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class CentroCustoOut(BaseModel):
    """Resposta de centro de custo."""
    id_centro_custo: int
    nome: str
    tipo: str
    descricao: Optional[str] = None
    status: Optional[bool] = None

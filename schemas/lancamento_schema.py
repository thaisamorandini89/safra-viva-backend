from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class RateioItem(BaseModel):
    """Parcela de rateio de uma despesa entre talhões."""
    id_talhao: int
    percentual: Decimal = Field(gt=0, le=100)


class LancamentoCreate(BaseModel):
    """Payload de criação/atualização de lançamento financeiro."""
    tipo: Literal['RECEITA', 'DESPESA']
    categoria: str = Field(min_length=1, max_length=100)
    data_lancamento: date
    valor: Decimal = Field(gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    forma_pagamento: Optional[
        Literal['DINHEIRO', 'PIX', 'BOLETO', 'CARTAO', 'TRANSFERENCIA']
    ] = None
    status: Optional[Literal['PENDENTE', 'PAGO']] = 'PENDENTE'
    observacao: Optional[str] = Field(default=None, max_length=500)
    id_empresa: Optional[int] = None
    id_propriedade: Optional[int] = None
    id_talhao: Optional[int] = None
    id_safra: Optional[int] = None
    id_centro_custo: Optional[int] = None
    rateio: Optional[List[RateioItem]] = None

    @field_validator('tipo', 'forma_pagamento', 'status', mode='before')
    @classmethod
    def normalizar_enum(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper() or None
        return valor

    @field_validator('categoria', 'descricao', 'observacao', mode='before')
    @classmethod
    def limpar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor


class RateioOut(BaseModel):
    id_rateio: Optional[int] = None
    id_talhao: int
    nome_talhao: Optional[str] = None
    percentual: float


class LancamentoOut(BaseModel):
    """Resposta de lançamento financeiro."""
    id_lancamento: str
    tipo: str
    categoria: str
    descricao: Optional[str] = None
    valor: float
    data_lancamento: Optional[str] = None
    forma_pagamento: Optional[str] = None
    status: str
    conciliado: bool
    observacao: Optional[str] = None
    id_empresa: Optional[int] = None
    id_propriedade: Optional[int] = None
    id_talhao: Optional[int] = None
    id_safra: Optional[int] = None
    id_centro_custo: Optional[int] = None
    nome_propriedade: Optional[str] = None
    nome_talhao: Optional[str] = None
    nome_safra: Optional[str] = None
    cultura: Optional[str] = None
    rateio: Optional[List[RateioOut]] = None

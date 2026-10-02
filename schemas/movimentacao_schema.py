from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class MovimentacaoCreate(BaseModel):
    """Payload de criação de movimentação de estoque."""
    id_insumo: int
    tipo_movimentacao: Literal['ENTRADA', 'SAIDA']
    quantidade: Decimal = Field(gt=0)
    id_responsavel: Optional[int] = None
    observacao: Optional[str] = Field(default=None, max_length=500)

    @field_validator('tipo_movimentacao', mode='before')
    @classmethod
    def normalizar_tipo(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor

    @field_validator('observacao', mode='before')
    @classmethod
    def limpar_observacao(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor


class MovimentacaoOut(BaseModel):
    """Resposta de movimentação registrada."""
    id_movimentacao: str
    id_insumo: int
    tipo_movimentacao: str
    quantidade: float
    data_movimentacao: Optional[str] = None
    id_responsavel: Optional[int] = None
    observacao: Optional[str] = None
    estoque_atual: float

from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

CAMPOS_ENTRADA = (
    "id_fornecedor",
    "numero_nota_fiscal",
    "numero_lote",
    "data_fabricacao",
    "data_validade",
)

CAMPOS_SAIDA = (
    "id_talhao",
    "safra",
    "id_atividade",
    "destino_finalidade",
)


class MovimentacaoCreate(BaseModel):
    """Payload de criacao de movimentacao de estoque."""

    id_insumo: int
    tipo_movimentacao: Literal['ENTRADA', 'SAIDA']
    quantidade: Decimal = Field(gt=0)
    valor_unitario: Optional[Decimal] = Field(default=None, ge=0)
    id_funcionario: Optional[str] = None
    observacao: Optional[str] = Field(default=None, max_length=500)

    id_fornecedor: Optional[int] = None
    numero_nota_fiscal: Optional[str] = Field(default=None, max_length=50)
    numero_lote: Optional[str] = Field(default=None, max_length=50)
    data_fabricacao: Optional[date] = None
    data_validade: Optional[date] = None

    id_talhao: Optional[int] = None
    safra: Optional[str] = Field(default=None, max_length=20)
    id_atividade: Optional[int] = None
    destino_finalidade: Optional[str] = Field(default=None, max_length=255)

    @field_validator('tipo_movimentacao', mode='before')
    @classmethod
    def normalizar_tipo(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor

    @field_validator(
        'observacao', 'numero_nota_fiscal', 'numero_lote',
        'safra', 'destino_finalidade', 'id_funcionario',
        mode='before'
    )
    @classmethod
    def limpar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor

    @model_validator(mode='after')
    def validar_campos_por_tipo(self):
        if self.tipo_movimentacao == 'ENTRADA':
            proibidos = [c for c in CAMPOS_SAIDA if getattr(self, c) is not None]
            if proibidos:
                raise ValueError(
                    "Os campos a seguir so sao permitidos em movimentacoes de SAIDA: "
                    + ", ".join(proibidos)
                )
        else:
            proibidos = [c for c in CAMPOS_ENTRADA if getattr(self, c) is not None]
            if proibidos:
                raise ValueError(
                    "Os campos a seguir so sao permitidos em movimentacoes de ENTRADA: "
                    + ", ".join(proibidos)
                )

        if self.data_fabricacao and self.data_validade:
            if self.data_validade < self.data_fabricacao:
                raise ValueError(
                    "A data de validade nao pode ser anterior a data de fabricacao."
                )

        return self

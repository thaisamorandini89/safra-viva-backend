from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

STATUS_ATIVIDADE = ("Planejada", "Em Andamento", "Concluída")
StatusLiteral = Literal["Planejada", "Em Andamento", "Concluída"]


class AtividadeItemInsumo(BaseModel):
    """Item de insumo utilizado na atividade (referencia o Insumo cadastrado)."""
    id_insumo: int
    quantidade: Optional[Decimal] = Field(default=None, ge=0)
    custo: Optional[Decimal] = Field(default=None, ge=0)
    # nome/unidade sao preenchidos pelo service como snapshot; ignorados na entrada


class AtividadeItemMaquina(BaseModel):
    """Item de maquina/implemento utilizado na atividade (referencia o catalogo)."""
    id_maquina: int
    horas: Optional[Decimal] = Field(default=None, ge=0)
    custo: Optional[Decimal] = Field(default=None, ge=0)


class AtividadeCreate(BaseModel):
    """Payload de criacao de uma operacao agricola."""
    id_categoria_atividade: int
    id_tipo_atividade: int
    id_talhao: int
    data_inicio: date
    status: StatusLiteral = "Planejada"
    id_funcionario: Optional[str] = None
    safra: Optional[str] = Field(default=None, max_length=20)
    data_fim: Optional[date] = None
    custo_operacao: Optional[Decimal] = Field(default=None, ge=0)
    observacoes: Optional[str] = Field(default=None, max_length=1000)
    id_empresa: Optional[int] = None
    id_propriedade: Optional[int] = None
    insumos: List[AtividadeItemInsumo] = Field(default_factory=list)
    maquinas: List[AtividadeItemMaquina] = Field(default_factory=list)

    @field_validator("id_funcionario", mode="before")
    @classmethod
    def _normaliza_responsavel(cls, v):
        if v is None:
            return v
        v = str(v).strip()
        return v or None

    @model_validator(mode="before")
    @classmethod
    def _alias_responsavel(cls, data):
        # aceita id_responsavel como alias de id_funcionario
        if isinstance(data, dict):
            if not data.get("id_funcionario") and data.get("id_responsavel"):
                data["id_funcionario"] = data["id_responsavel"]
        return data

    @model_validator(mode="after")
    def _valida_periodo(self):
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValueError("A data de termino nao pode ser anterior a data de inicio.")
        return self


class AtividadeUpdate(BaseModel):
    """Payload de atualizacao (todos os campos opcionais)."""
    id_categoria_atividade: Optional[int] = None
    id_tipo_atividade: Optional[int] = None
    id_talhao: Optional[int] = None
    data_inicio: Optional[date] = None
    status: Optional[StatusLiteral] = None
    id_funcionario: Optional[str] = None
    safra: Optional[str] = Field(default=None, max_length=20)
    data_fim: Optional[date] = None
    custo_operacao: Optional[Decimal] = Field(default=None, ge=0)
    observacoes: Optional[str] = Field(default=None, max_length=1000)
    id_empresa: Optional[int] = None
    id_propriedade: Optional[int] = None
    insumos: Optional[List[AtividadeItemInsumo]] = None
    maquinas: Optional[List[AtividadeItemMaquina]] = None

    @model_validator(mode="before")
    @classmethod
    def _alias_responsavel(cls, data):
        if isinstance(data, dict):
            if not data.get("id_funcionario") and data.get("id_responsavel"):
                data["id_funcionario"] = data["id_responsavel"]
        return data

    @model_validator(mode="after")
    def _valida_periodo(self):
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValueError("A data de termino nao pode ser anterior a data de inicio.")
        return self

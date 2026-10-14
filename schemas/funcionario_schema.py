from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _normalizar_cpf(valor):
    """Remove qualquer caractere não numérico do CPF."""
    if isinstance(valor, str):
        return ''.join(filter(str.isdigit, valor))
    return valor


class FuncionarioCreate(BaseModel):
    """Payload de criação de funcionário."""
    nome_completo: str = Field(min_length=1)
    cpf: str
    cargo: str = Field(min_length=1)
    data_admissao: date
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[str] = Field(default=None, max_length=100)
    data_desligamento: Optional[date] = None
    observacoes: Optional[str] = Field(default=None, max_length=500)

    @field_validator('nome_completo', 'cargo', mode='before')
    @classmethod
    def limpar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator('cpf', mode='before')
    @classmethod
    def validar_cpf(cls, valor):
        cpf = _normalizar_cpf(valor)
        if not cpf or len(cpf) != 11:
            raise ValueError("O CPF deve conter 11 dígitos.")
        return cpf

    @field_validator('telefone', mode='before')
    @classmethod
    def normalizar_telefone(cls, valor):
        if isinstance(valor, str):
            return ''.join(filter(str.isdigit, valor)) or None
        return valor

    @field_validator('rg', 'email', 'observacoes', mode='before')
    @classmethod
    def limpar_opcionais(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor


class FuncionarioUpdate(BaseModel):
    """Payload de atualização de funcionário (campos opcionais)."""
    nome_completo: Optional[str] = Field(default=None, min_length=1)
    cpf: Optional[str] = None
    cargo: Optional[str] = Field(default=None, min_length=1)
    data_admissao: Optional[date] = None
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[str] = Field(default=None, max_length=100)
    data_desligamento: Optional[date] = None
    observacoes: Optional[str] = Field(default=None, max_length=500)
    status: Optional[bool] = None

    @field_validator('nome_completo', 'cargo', mode='before')
    @classmethod
    def limpar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator('cpf', mode='before')
    @classmethod
    def validar_cpf(cls, valor):
        if valor is None:
            return valor
        cpf = _normalizar_cpf(valor)
        if len(cpf) != 11:
            raise ValueError("O CPF deve conter 11 dígitos.")
        return cpf

    @field_validator('telefone', mode='before')
    @classmethod
    def normalizar_telefone(cls, valor):
        if isinstance(valor, str):
            return ''.join(filter(str.isdigit, valor)) or None
        return valor

    @field_validator('rg', 'email', 'observacoes', mode='before')
    @classmethod
    def limpar_opcionais(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor


class VinculoPropriedadeCreate(BaseModel):
    """Payload para vincular um funcionário a uma propriedade."""
    id_propriedade: int

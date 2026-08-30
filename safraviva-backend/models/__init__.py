from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .empresa_agricola import EmpresaAgricola
from .regime_tributario import RegimeTributario
from .tipo_empresa import TipoEmpresa
from .tipo_solo import TipoSolo
from .classe_capacidade_uso import ClasseCapacidadeUso
from .propriedade import Propriedade
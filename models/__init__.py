from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Importações para garantir que o Flask-Migrate veja as classes
from .estado import Estado
from .cidade import Cidade
from .bairro import Bairro
from .logradouro import Logradouro
from .tipo_empresa import TipoEmpresa
from .regime_tributario import RegimeTributario
from .empresa_agricola import EmpresaAgricola
from .tipo_solo import TipoSolo
from .classe_capacidade_uso import ClasseCapacidadeUso
from .propriedade import Propriedade
from .talhao import Talhao
from .categoria_insumo import CategoriaInsumo
from .fabricante import Fabricante
from .fornecedor import Fornecedor
from .produto import Produto
from .insumo import Insumo
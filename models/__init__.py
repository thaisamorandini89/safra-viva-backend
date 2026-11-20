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
from .marca import Marca
from .funcionario import Funcionario
from .funcionario_propriedade import FuncionarioPropriedade
from .categoria_atividade import CategoriaAtividade
from .tipo_atividade import TipoAtividade
from .maquina import Maquina
from .atividade_agricola import AtividadeAgricola
from .atividade_insumo import AtividadeInsumo
from .atividade_maquina import AtividadeMaquina
from .movimentacao_estoque import MovimentacaoEstoque
from .lote_insumo import LoteInsumo
from .movimentacao_lote import MovimentacaoLote
from .safra import Safra
from .centro_custo import CentroCusto
from .lancamento_financeiro import LancamentoFinanceiro
from .rateio_lancamento import RateioLancamento
from .usuario import Usuario

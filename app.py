import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db # Importa o objeto 'db' configurado no seu models/__init__.py
from controllers.geo_controller import geo_bp
from controllers.empresa_agricola_controller import empresa_bp
from controllers.regime_tributario_controller import regime_bp
from controllers.tipo_empresa_controller import tipo_empresa_bp
from controllers.tipo_solo_controller import tipo_solo_bp
from controllers.classe_capacidade_uso_controller import classe_uso_bp
from controllers.propriedade_controller import propriedade_bp
from controllers.talhao_controller import talhao_bp
from controllers.categoria_insumo_controller import categoria_insumo_bp
from controllers.fabricante_controller import fabricante_bp
from controllers.fornecedor_controller import fornecedor_bp
from controllers.produto_controller import produto_bp
from controllers.insumo_controller import insumo_bp
from controllers.marca_controller import marca_bp
from controllers.categoria_atividade_controller import categoria_atividade_bp
from controllers.tipo_atividade_controller import tipo_atividade_bp
from controllers.maquina_controller import maquina_bp
from controllers.atividade_agricola_controller import atividade_agricola_bp
from controllers.movimentacao_controller import movimentacao_bp
from controllers.funcionario_controller import funcionario_bp
from controllers.safra_controller import safra_bp
from controllers.centro_custo_controller import centro_custo_bp
from controllers.lancamento_controller import lancamento_bp
from controllers.financeiro_controller import financeiro_bp
from controllers.auth_controller import auth_bp
from controllers.safra_ia_controller import safra_ia_bp

BLUEPRINTS = [
    geo_bp,
    empresa_bp,
    regime_bp,
    tipo_empresa_bp,
    tipo_solo_bp,
    classe_uso_bp,
    propriedade_bp,
    talhao_bp,
    categoria_insumo_bp,
    fabricante_bp,
    fornecedor_bp,
    produto_bp,
    insumo_bp,
    marca_bp,
    atividade_agricola_bp,
    categoria_atividade_bp,
    tipo_atividade_bp,
    maquina_bp,
    movimentacao_bp,
    funcionario_bp,
    safra_bp,
    centro_custo_bp,
    lancamento_bp,
    financeiro_bp,
    auth_bp,
    safra_ia_bp,
]


def create_app(config=None):
    app = Flask(__name__)
    
    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:senha_segura@db:5432/safra_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'dev-secret-troque-em-producao-com-32-chars')
    if config:
        app.config.update(config)
    
    # Inicialização das extensões
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    for bp in BLUEPRINTS:
        app.register_blueprint(bp, url_prefix='/api')

    # Rota de teste
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "Backend do SafraViva rodando com sucesso!"})
    
    return app

# Cria a instância da aplicação
app = create_app()

if __name__ == '__main__':
    # O host 0.0.0.0 é obrigatório dentro de containers Docker
    app.run(host='0.0.0.0', port=5000)
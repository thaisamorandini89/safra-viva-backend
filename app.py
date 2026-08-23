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

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:senha_segura@db:5432/safra_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialização das extensões
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Rota de teste
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "Backend do SafraViva rodando com sucesso!"})
    
    return app

# Cria a instância da aplicação
app = create_app()

# REGISTRO DO BLUEPRINT (Obrigatório)
app.register_blueprint(geo_bp, url_prefix='/api')
app.register_blueprint(empresa_bp, url_prefix='/api')
app.register_blueprint(regime_bp, url_prefix='/api')
app.register_blueprint(tipo_empresa_bp, url_prefix='/api')
app.register_blueprint(tipo_solo_bp, url_prefix='/api')
app.register_blueprint(classe_uso_bp, url_prefix='/api')
app.register_blueprint(propriedade_bp, url_prefix='/api')

if __name__ == '__main__':
    # O host 0.0.0.0 é obrigatório dentro de containers Docker
    app.run(host='0.0.0.0', port=5000)
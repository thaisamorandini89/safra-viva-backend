from flask import Blueprint

# Initialize the controllers module
geo_bp = Blueprint('geo', __name__)
empresa_bp = Blueprint('empresa', __name__)
regime_bp = Blueprint('regime', __name__)
tipo_empresa_bp = Blueprint('tipo_empresa', __name__)
tipo_solo_bp = Blueprint('tipo_solo', __name__)
classe_uso_bp = Blueprint('classe_uso', __name__)
propriedade_bp = Blueprint('propriedade', __name__)
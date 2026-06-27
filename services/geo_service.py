from models.estado import Estado
from models.cidade import Cidade

class GeoService:
    @staticmethod
    def get_all_estados():
        # Busca todos os estados e ordena pelo nome
        return Estado.query.order_by(Estado.nome_estado).all()

    @staticmethod
    def get_cidades_por_estado(id_estado):
        # Busca cidades filtrando pelo ID do estado
        return Cidade.query.filter_by(id_estado=id_estado).order_by(Cidade.nome_cidade).all()
        
    @staticmethod
    def get_all_cidades():
        # Busca todas as cidades (cuidado: são 5571 registros, use com paginação se necessário)
        return Cidade.query.order_by(Cidade.nome_cidade).all()
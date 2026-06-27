from models import db
from models.tipo_empresa import TipoEmpresa

class TipoEmpresaService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os tipos de empresa ordenados por descrição.
        """
        return TipoEmpresa.query.order_by(TipoEmpresa.descricao).all()

    @staticmethod
    def criar_tipo(dados):
        """
        Cria um novo Tipo de Empresa.
        """
        descricao = dados.get("descricao")
        if not descricao:
            raise ValueError("A descrição do tipo de empresa é obrigatória.")

        descricao_limpa = descricao.strip()
        
        # Verificar duplicados
        existente = TipoEmpresa.query.filter_by(descricao=descricao_limpa).first()
        if existente:
            raise ValueError("Já existe um tipo de empresa com esta descrição.")

        novo_tipo = TipoEmpresa(descricao=descricao_limpa)
        db.session.add(novo_tipo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o tipo de empresa: {str(e)}")

        return novo_tipo

from models import db
from models.marca import Marca


class MarcaService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todas as marcas ordenadas por descrição.
        """
        return Marca.query.order_by(Marca.descricao_marca).all()

    @staticmethod
    def _validar_descricao(dados):
        descricao = (dados or {}).get("descricao_marca")
        if not descricao or not descricao.strip():
            raise ValueError("A descrição da marca é obrigatória.")
        return descricao.strip()

    @staticmethod
    def _commit(mensagem_erro):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"{mensagem_erro}: {str(e)}")

    @staticmethod
    def criar_marca(dados):
        """
        Cria uma nova Marca.
        """
        descricao_limpa = MarcaService._validar_descricao(dados)

        existente = Marca.query.filter_by(descricao_marca=descricao_limpa).first()
        if existente:
            raise ValueError("Já existe uma marca com esta descrição.")

        nova_marca = Marca(descricao_marca=descricao_limpa)
        db.session.add(nova_marca)
        MarcaService._commit("Erro ao salvar a marca")

        return nova_marca

    @staticmethod
    def atualizar_marca(id_marca, dados):
        """
        Atualiza a descrição de uma marca existente.
        """
        marca = Marca.query.get(id_marca)
        if not marca:
            raise LookupError("Marca não encontrada.")

        descricao_limpa = MarcaService._validar_descricao(dados)

        duplicada = Marca.query.filter(
            Marca.descricao_marca == descricao_limpa,
            Marca.id_marca != id_marca,
        ).first()
        if duplicada:
            raise ValueError("Já existe uma marca com esta descrição.")

        marca.descricao_marca = descricao_limpa
        MarcaService._commit("Erro ao atualizar a marca")

        return marca

    @staticmethod
    def excluir_marca(id_marca):
        """
        Remove uma marca existente.
        """
        marca = Marca.query.get(id_marca)
        if not marca:
            raise LookupError("Marca não encontrada.")

        db.session.delete(marca)
        MarcaService._commit("Erro ao excluir a marca")

        return True

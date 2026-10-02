from models import db
from models.responsavel import Responsavel


class ResponsavelService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os responsáveis ordenados por nome.
        """
        return Responsavel.query.order_by(Responsavel.nome).all()

    @staticmethod
    def criar_responsavel(dados):
        """
        Cria um novo Responsável.
        """
        nome = (dados or {}).get("nome")
        if not nome or not str(nome).strip():
            raise ValueError("O nome do responsável é obrigatório.")

        novo = Responsavel(
            nome=str(nome).strip(),
            cargo=(dados.get("cargo") or "").strip() or None
        )

        db.session.add(novo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o responsável: {str(e)}")

        return novo

from models import db
from models.centro_custo import CentroCusto
from models.lancamento_financeiro import LancamentoFinanceiro


def serializar_centro_custo(c):
    return {
        "id_centro_custo": c.id_centro_custo,
        "nome": c.nome,
        "tipo": c.tipo,
        "descricao": c.descricao,
        "status": c.status,
    }


class CentroCustoService:
    @staticmethod
    def criar(dados):
        """Cria um centro de custo. `dados` é um CentroCustoCreate validado."""
        centro = CentroCusto(
            nome=dados.nome,
            tipo=dados.tipo,
            descricao=dados.descricao,
        )
        db.session.add(centro)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao criar o centro de custo: {str(e)}")
        return centro

    @staticmethod
    def atualizar(id_centro_custo, dados):
        """Altera os campos enviados. `dados` é um CentroCustoUpdate já validado."""
        centro = CentroCusto.query.get(id_centro_custo)
        if not centro:
            raise LookupError("Centro de custo não encontrado.")

        enviados = dados.model_fields_set
        for campo in ("nome", "tipo"):
            if campo in enviados and getattr(dados, campo) is None:
                raise ValueError(f"O campo '{campo}' não pode ficar vazio.")

        for campo in ("nome", "tipo", "descricao"):
            if campo in enviados:
                setattr(centro, campo, getattr(dados, campo))
        if dados.status is not None:
            centro.status = dados.status

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o centro de custo: {str(e)}")
        return centro

    @staticmethod
    def excluir(id_centro_custo):
        centro = CentroCusto.query.get(id_centro_custo)
        if not centro:
            raise LookupError("Centro de custo não encontrado.")
        if LancamentoFinanceiro.query.filter_by(id_centro_custo=id_centro_custo).first():
            raise ValueError(
                "O centro de custo está em uso por lançamentos financeiros e não "
                "pode ser excluído. Inative-o se não for mais usar."
            )

        db.session.delete(centro)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o centro de custo: {str(e)}")

    @staticmethod
    def listar():
        centros = CentroCusto.query.order_by(CentroCusto.nome.asc()).all()
        return [serializar_centro_custo(c) for c in centros]

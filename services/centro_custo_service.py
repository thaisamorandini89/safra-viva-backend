from models import db
from models.centro_custo import CentroCusto


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
    def listar():
        centros = CentroCusto.query.order_by(CentroCusto.nome.asc()).all()
        return [serializar_centro_custo(c) for c in centros]

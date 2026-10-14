from models import db
from models.safra import Safra
from models.propriedade import Propriedade


def serializar_safra(safra, propriedade=None):
    prop = propriedade or (
        Propriedade.query.get(safra.id_propriedade) if safra.id_propriedade else None
    )
    return {
        "id_safra": safra.id_safra,
        "nome": safra.nome,
        "cultura": safra.cultura,
        "id_propriedade": safra.id_propriedade,
        "nome_propriedade": prop.nome_propriedade if prop else None,
        "data_inicio": safra.data_inicio.isoformat() if safra.data_inicio else None,
        "data_fim": safra.data_fim.isoformat() if safra.data_fim else None,
        "area_plantada": float(safra.area_plantada) if safra.area_plantada is not None else None,
        "status": safra.status,
    }


class SafraService:
    @staticmethod
    def criar(dados):
        """Cria uma safra. `dados` é um SafraCreate já validado."""
        if not Propriedade.query.get(dados.id_propriedade):
            raise ValueError("Propriedade informada não foi encontrada.")

        safra = Safra(
            nome=dados.nome,
            cultura=dados.cultura,
            id_propriedade=dados.id_propriedade,
            data_inicio=dados.data_inicio,
            data_fim=dados.data_fim,
            area_plantada=dados.area_plantada,
        )
        db.session.add(safra)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao criar a safra: {str(e)}")
        return safra

    @staticmethod
    def listar(id_propriedade=None):
        query = Safra.query
        if id_propriedade:
            query = query.filter_by(id_propriedade=id_propriedade)
        safras = query.order_by(Safra.data_inicio.desc()).all()
        return [serializar_safra(s) for s in safras]

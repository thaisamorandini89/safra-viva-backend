from models import db
from models.lancamento_financeiro import LancamentoFinanceiro
from models.safra import Safra
from models.propriedade import Propriedade


def _validar_periodo(data_inicio, data_fim):
    if data_fim and data_fim < data_inicio:
        raise ValueError("A data de término da safra não pode ser anterior à data de início.")


def _validar_nome_unico(nome, id_propriedade, id_safra=None):
    repetida = Safra.query.filter(
        Safra.id_propriedade == id_propriedade,
        db.func.lower(Safra.nome) == nome.lower(),
    )
    if id_safra is not None:
        repetida = repetida.filter(Safra.id_safra != id_safra)
    if repetida.first():
        raise ValueError("Já existe uma safra com esse nome nesta propriedade.")


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
        _validar_periodo(dados.data_inicio, dados.data_fim)
        _validar_nome_unico(dados.nome, dados.id_propriedade)

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
    def atualizar(id_safra, dados):
        """Altera os campos enviados. `dados` é um SafraUpdate já validado."""
        safra = Safra.query.get(id_safra)
        if not safra:
            raise LookupError("Safra não encontrada.")

        enviados = dados.model_fields_set
        if "id_propriedade" in enviados and dados.id_propriedade != safra.id_propriedade:
            raise ValueError(
                "A propriedade de uma safra não pode ser alterada. "
                "Cadastre outra safra na propriedade desejada."
            )
        for campo in ("nome", "cultura", "data_inicio"):
            if campo in enviados and getattr(dados, campo) is None:
                raise ValueError(f"O campo '{campo}' não pode ficar vazio.")

        nome = dados.nome if "nome" in enviados else safra.nome
        data_inicio = dados.data_inicio if "data_inicio" in enviados else safra.data_inicio
        data_fim = dados.data_fim if "data_fim" in enviados else safra.data_fim
        _validar_periodo(data_inicio, data_fim)
        _validar_nome_unico(nome, safra.id_propriedade, id_safra=safra.id_safra)

        for campo in ("nome", "cultura", "data_inicio", "data_fim", "area_plantada"):
            if campo in enviados:
                setattr(safra, campo, getattr(dados, campo))
        if dados.status is not None:
            safra.status = dados.status

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a safra: {str(e)}")
        return safra

    @staticmethod
    def excluir(id_safra):
        safra = Safra.query.get(id_safra)
        if not safra:
            raise LookupError("Safra não encontrada.")
        if LancamentoFinanceiro.query.filter_by(id_safra=id_safra).first():
            raise ValueError(
                "A safra está em uso por lançamentos financeiros e não pode ser "
                "excluída. Inative-a se não for mais usar."
            )

        db.session.delete(safra)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a safra: {str(e)}")

    @staticmethod
    def listar(id_propriedade=None):
        query = Safra.query
        if id_propriedade:
            query = query.filter_by(id_propriedade=id_propriedade)
        safras = query.order_by(Safra.data_inicio.desc()).all()
        return [serializar_safra(s) for s in safras]

from models import db
from models.atividade import Atividade


class AtividadeService:
    @staticmethod
    def _serializar(atv):
        return {
            "id_atividade": atv.id_atividade,
            "descricao": atv.descricao,
            "data_atividade": atv.data_atividade.strftime("%Y-%m-%d") if atv.data_atividade else None,
            "status": atv.status,
        }

    @staticmethod
    def listar_todos():
        """
        Lista as atividades da mais recente para a mais antiga,
        para alimentar o seletor de "Atividade Relacionada".
        """
        atividades = Atividade.query.order_by(
            Atividade.data_atividade.desc().nullslast(),
            Atividade.descricao
        ).all()
        return [AtividadeService._serializar(a) for a in atividades]

    @staticmethod
    def criar_atividade(dados):
        """
        Cria uma nova Atividade.
        """
        descricao = (dados or {}).get("descricao")
        if not descricao or not str(descricao).strip():
            raise ValueError("A descrição da atividade é obrigatória.")

        nova = Atividade(
            descricao=str(descricao).strip(),
            data_atividade=(dados.get("data_atividade") or None),
        )

        db.session.add(nova)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a atividade: {str(e)}")

        return nova

from models import db
from models.atividade_maquina import AtividadeMaquina
from models.maquina import Maquina


class MaquinaService:
    @staticmethod
    def _serializar(m):
        return {
            "id_maquina": m.id_maquina,
            "nome": m.nome,
            "tipo": m.tipo,
            "observacoes": m.observacoes,
            "status": m.status,
        }

    @staticmethod
    def listar_todas():
        maquinas = Maquina.query.order_by(Maquina.nome.asc()).all()
        return [MaquinaService._serializar(m) for m in maquinas]

    @staticmethod
    def buscar_por_id(id_maquina):
        m = Maquina.query.get(id_maquina)
        if not m:
            raise ValueError("Máquina não encontrada.")
        return MaquinaService._serializar(m)

    @staticmethod
    def criar(dados):
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("O nome da máquina é obrigatório.")
        if Maquina.query.filter_by(nome=nome).first():
            raise ValueError("Já existe uma máquina cadastrada com este nome.")
        nova = Maquina(
            nome=nome,
            tipo=(dados.get("tipo") or "").strip() or None,
            observacoes=(dados.get("observacoes") or "").strip() or None,
            status=bool(dados.get("status", True)),
        )
        db.session.add(nova)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a máquina: {str(e)}")
        return nova

    @staticmethod
    def atualizar(id_maquina, dados):
        m = Maquina.query.get(id_maquina)
        if not m:
            raise ValueError("Máquina não encontrada.")
        if "nome" in dados:
            nome = (dados.get("nome") or "").strip()
            if not nome:
                raise ValueError("O nome da máquina não pode ficar vazio.")
            existente = Maquina.query.filter_by(nome=nome).first()
            if existente and existente.id_maquina != m.id_maquina:
                raise ValueError("Já existe uma máquina cadastrada com este nome.")
            m.nome = nome
        if "tipo" in dados:
            m.tipo = (dados.get("tipo") or "").strip() or None
        if "observacoes" in dados:
            m.observacoes = (dados.get("observacoes") or "").strip() or None
        if "status" in dados:
            m.status = bool(dados.get("status"))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a máquina: {str(e)}")
        return m

    @staticmethod
    def excluir(id_maquina):
        m = Maquina.query.get(id_maquina)
        if not m:
            raise ValueError("Máquina não encontrada.")
        if AtividadeMaquina.query.filter_by(id_maquina=id_maquina).first():
            raise ValueError(
                "A máquina está em uso por atividades registradas e não pode ser excluída."
            )
        db.session.delete(m)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a máquina: {str(e)}")
        return True

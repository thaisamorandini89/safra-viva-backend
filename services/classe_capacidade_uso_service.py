from models import db
from models.classe_capacidade_uso import ClasseCapacidadeUso

class ClasseCapacidadeUsoService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todas as classes de capacidade de uso.
        Ordenamos pelo ID para manter a sequência lógica (I, II, III...).
        """
        return ClasseCapacidadeUso.query.order_by(ClasseCapacidadeUso.id_classe_capacidade_uso).all()

    @staticmethod
    def criar_classe(dados):
        """
        Cria uma nova Classe de Capacidade de Uso.
        """
        sigla = dados.get("sigla")
        descricao = dados.get("descricao")

        if not sigla or not descricao:
            raise ValueError("A sigla (ex: I, II) e a descrição são obrigatórias.")

        sigla_limpa = sigla.strip()
        descricao_limpa = descricao.strip()
        
        existente = ClasseCapacidadeUso.query.filter_by(sigla=sigla_limpa).first()
        if existente:
            raise ValueError("Já existe uma classe de uso com esta sigla.")
        
        aptidao = dados.get("aptidao_principal", "").strip() or None

        nova_classe = ClasseCapacidadeUso(
            sigla=sigla_limpa,
            descricao=descricao_limpa,
            aptidao_principal=aptidao
        )
        
        db.session.add(nova_classe)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a classe de capacidade de uso: {str(e)}")

        return nova_classe
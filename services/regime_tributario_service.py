from models import db
from models.regime_tributario import RegimeTributario

class RegimeTributarioService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os regimes tributários ordenados por descrição.
        """
        return RegimeTributario.query.order_by(RegimeTributario.descricao).all()

    @staticmethod
    def criar_regime(dados):
        """
        Cria um novo Regime Tributário.
        """
        descricao = dados.get("descricao")
        if not descricao:
            raise ValueError("A descrição do regime tributário é obrigatória.")

        descricao_limpa = descricao.strip()
        
        # Verificar duplicados
        existente = RegimeTributario.query.filter_by(descricao=descricao_limpa).first()
        if existente:
            raise ValueError("Já existe um regime tributário com esta descrição.")

        novo_regime = RegimeTributario(descricao=descricao_limpa)
        db.session.add(novo_regime)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o regime tributário: {str(e)}")

        return novo_regime

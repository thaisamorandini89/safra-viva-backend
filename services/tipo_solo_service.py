from models import db
from models.tipo_solo import TipoSolo

class TipoSoloService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os tipos de solo ordenados por descrição.
        """
        return TipoSolo.query.order_by(TipoSolo.descricao).all()

    @staticmethod
    def criar_tipo(dados):
        """
        Cria um novo Tipo de Solo.
        """
        descricao = dados.get("descricao")
        if not descricao:
            raise ValueError("A descrição do tipo de solo é obrigatória.")

        descricao_limpa = descricao.strip()
        
        # Verificar duplicados para evitar cadastrar "Latossolo" duas vezes
        existente = TipoSolo.query.filter_by(descricao=descricao_limpa).first()
        if existente:
            raise ValueError("Já existe um tipo de solo com esta descrição.")

        # Pegando campos opcionais
        sigla = dados.get("sigla", "").strip() or None
        classe_textural = dados.get("classe_textural", "").strip() or None

        novo_tipo = TipoSolo(
            descricao=descricao_limpa,
            sigla=sigla,
            classe_textural=classe_textural
        )
        
        db.session.add(novo_tipo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o tipo de solo: {str(e)}")

        return novo_tipo
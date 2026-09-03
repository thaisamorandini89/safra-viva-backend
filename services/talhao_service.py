from models import db
from models.talhao import Talhao
from models.propriedade import Propriedade
from models.tipo_solo import TipoSolo


class TalhaoService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os talhões cadastrados,
        incluindo informações da propriedade e do tipo de solo.
        """
        talhoes = Talhao.query.order_by(Talhao.data_cadastro.desc()).all()
        resultado = []

        for talhao in talhoes:
            # Propriedade vinculada
            propriedade_nome = ""
            if talhao.id_propriedade:
                prop = Propriedade.query.get(talhao.id_propriedade)
                if prop:
                    propriedade_nome = prop.nome_propriedade

            # Tipo de Solo
            tipo_solo_desc = ""
            if talhao.id_tipo_solo:
                solo = TipoSolo.query.get(talhao.id_tipo_solo)
                if solo:
                    tipo_solo_desc = solo.descricao

            resultado.append({
                "id_talhao": talhao.id_talhao,
                "nome_talhao": talhao.nome_talhao,
                "codigo_talhao": talhao.codigo_talhao,
                "id_propriedade": talhao.id_propriedade,
                "propriedade_nome": propriedade_nome,
                "area_total": float(talhao.area_total) if talhao.area_total is not None else None,
                "area_utilizavel": float(talhao.area_utilizavel) if talhao.area_utilizavel is not None else None,
                "status_inicial": talhao.status_inicial,
                "id_tipo_solo": talhao.id_tipo_solo,
                "tipo_solo_descricao": tipo_solo_desc,
                "topografia": talhao.topografia,
                "observacoes": talhao.observacoes,
                "latitude": float(talhao.latitude) if talhao.latitude is not None else None,
                "longitude": float(talhao.longitude) if talhao.longitude is not None else None,
                "status": talhao.status,
                "data_cadastro": talhao.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if talhao.data_cadastro else None
            })

        return resultado

    @staticmethod
    def listar_por_propriedade(id_propriedade):
        """
        Retorna a lista de talhões vinculados a uma propriedade específica.
        """
        propriedade = Propriedade.query.get(id_propriedade)
        if not propriedade:
            raise ValueError("Propriedade não encontrada.")

        return [
            item for item in TalhaoService.listar_todos()
            if item["id_propriedade"] == id_propriedade
        ]

    @staticmethod
    def buscar_por_id(id_talhao):
        """
        Retorna um único talhão pelo seu id, no mesmo formato de listar_todos().
        """
        talhao = Talhao.query.get(id_talhao)
        if not talhao:
            raise ValueError("Talhão não encontrado.")

        for item in TalhaoService.listar_todos():
            if item["id_talhao"] == talhao.id_talhao:
                return item
        return None

    @staticmethod
    def _to_decimal(valor, campo):
        """Converte string/numero para float validando o campo."""
        if valor is None or valor == "":
            return None
        try:
            # Aceita valores no formato brasileiro "1.500,00" ou americano "1500.00"
            if isinstance(valor, str):
                valor = valor.strip().replace(".", "").replace(",", ".") if "," in valor else valor.strip()
            return float(valor)
        except (ValueError, TypeError):
            raise ValueError(f"O campo '{campo}' possui um valor numérico inválido.")

    @staticmethod
    def criar_talhao(dados):
        """
        Cria um novo Talhão.
        """
        # Validação de campos obrigatórios
        nome = dados.get("nome_talhao")
        codigo = dados.get("codigo_talhao")
        id_propriedade = dados.get("id_propriedade")

        if not nome or not str(nome).strip():
            raise ValueError("O nome do talhão é obrigatório.")
        if not codigo or not str(codigo).strip():
            raise ValueError("O código do talhão é obrigatório.")
        if not id_propriedade:
            raise ValueError("A propriedade vinculada é obrigatória.")

        # Verificar se a propriedade existe
        propriedade = Propriedade.query.get(id_propriedade)
        if not propriedade:
            raise ValueError("Propriedade informada não foi encontrada.")

        # Área total obrigatória
        area_total = TalhaoService._to_decimal(dados.get("area_total"), "area_total")
        if area_total is None:
            raise ValueError("A área total é obrigatória.")

        # Área utilizável: se vazia, usa a área total
        area_utilizavel = TalhaoService._to_decimal(dados.get("area_utilizavel"), "area_utilizavel")
        if area_utilizavel is None:
            area_utilizavel = area_total

        latitude = TalhaoService._to_decimal(dados.get("latitude"), "latitude")
        longitude = TalhaoService._to_decimal(dados.get("longitude"), "longitude")

        novo_talhao = Talhao(
            nome_talhao=nome.strip(),
            codigo_talhao=codigo.strip(),
            id_propriedade=id_propriedade,
            area_total=area_total,
            area_utilizavel=area_utilizavel,
            status_inicial=(dados.get("status_inicial") or "Livre").strip(),
            id_tipo_solo=dados.get("id_tipo_solo") or None,
            topografia=(dados.get("topografia") or "").strip() or None,
            observacoes=(dados.get("observacoes") or "").strip() or None,
            latitude=latitude,
            longitude=longitude
        )

        db.session.add(novo_talhao)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o talhão no banco de dados: {str(e)}")

        return novo_talhao

    @staticmethod
    def atualizar_talhao(id_talhao, dados):
        """
        Atualiza os dados de um Talhão existente.
        Apenas os campos enviados no payload são alterados.
        """
        talhao = Talhao.query.get(id_talhao)
        if not talhao:
            raise ValueError("Talhão não encontrado.")

        # Dados Básicos
        if "nome_talhao" in dados:
            nome = (dados.get("nome_talhao") or "").strip()
            if not nome:
                raise ValueError("O nome do talhão não pode ficar vazio.")
            talhao.nome_talhao = nome

        if "codigo_talhao" in dados:
            codigo = (dados.get("codigo_talhao") or "").strip()
            if not codigo:
                raise ValueError("O código do talhão não pode ficar vazio.")
            talhao.codigo_talhao = codigo

        if "id_propriedade" in dados and dados.get("id_propriedade"):
            propriedade = Propriedade.query.get(dados.get("id_propriedade"))
            if not propriedade:
                raise ValueError("Propriedade informada não foi encontrada.")
            talhao.id_propriedade = dados.get("id_propriedade")

        # Áreas
        if "area_total" in dados:
            area_total = TalhaoService._to_decimal(dados.get("area_total"), "area_total")
            if area_total is None:
                raise ValueError("A área total não pode ficar vazia.")
            talhao.area_total = area_total
        if "area_utilizavel" in dados:
            talhao.area_utilizavel = TalhaoService._to_decimal(dados.get("area_utilizavel"), "area_utilizavel")

        # Situação
        if "status_inicial" in dados:
            talhao.status_inicial = (dados.get("status_inicial") or "Livre").strip()

        # Características Técnicas
        if "id_tipo_solo" in dados:
            talhao.id_tipo_solo = dados.get("id_tipo_solo") or None
        if "topografia" in dados:
            talhao.topografia = (dados.get("topografia") or "").strip() or None
        if "observacoes" in dados:
            talhao.observacoes = (dados.get("observacoes") or "").strip() or None

        # Coordenadas
        if "latitude" in dados:
            talhao.latitude = TalhaoService._to_decimal(dados.get("latitude"), "latitude")
        if "longitude" in dados:
            talhao.longitude = TalhaoService._to_decimal(dados.get("longitude"), "longitude")

        if "status" in dados:
            talhao.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o talhão no banco de dados: {str(e)}")

        return talhao

    @staticmethod
    def excluir_talhao(id_talhao):
        """
        Exclui um Talhão pelo seu id.
        """
        talhao = Talhao.query.get(id_talhao)
        if not talhao:
            raise ValueError("Talhão não encontrado.")

        db.session.delete(talhao)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o talhão no banco de dados: {str(e)}")

        return True

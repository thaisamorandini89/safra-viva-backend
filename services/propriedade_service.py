from models import db
from models.propriedade import Propriedade
from models.empresa_agricola import EmpresaAgricola
from models.logradouro import Logradouro
from models.bairro import Bairro
from models.cidade import Cidade
from models.estado import Estado
from models.tipo_solo import TipoSolo
from models.classe_capacidade_uso import ClasseCapacidadeUso


class PropriedadeService:
    @staticmethod
    def listar_todas():
        """
        Retorna a lista de todas as propriedades cadastradas,
        incluindo informações de endereço, empresa, solo e classe de uso.
        """
        propriedades = Propriedade.query.order_by(Propriedade.data_cadastro.desc()).all()
        resultado = []

        for prop in propriedades:
            # Endereço (via logradouro)
            endereco = None
            if prop.id_logradouro:
                logr = Logradouro.query.get(prop.id_logradouro)
                if logr:
                    bairro = Bairro.query.get(logr.id_bairro)
                    bairro_nome = bairro.nome_bairro if bairro else ""

                    cidade_nome = ""
                    estado_uf = ""
                    estado_id = None
                    cidade_id = None
                    if bairro:
                        cid = Cidade.query.get(bairro.id_cidade)
                        if cid:
                            cidade_id = cid.id_cidade
                            cidade_nome = cid.nome_cidade
                            est = Estado.query.get(cid.id_estado)
                            if est:
                                estado_id = est.id_estado
                                estado_uf = est.uf_estado

                    endereco = {
                        "id_logradouro": logr.id_logradouro,
                        "cep": logr.cep,
                        "logradouro": logr.logradouro,
                        "numero": logr.numero,
                        "complemento": logr.complemento,
                        "bairro": bairro_nome,
                        "id_cidade": cidade_id,
                        "cidade": cidade_nome,
                        "id_estado": estado_id,
                        "uf": estado_uf
                    }

            # Empresa vinculada
            empresa_nome = ""
            if prop.id_empresa:
                emp = EmpresaAgricola.query.get(prop.id_empresa)
                if emp:
                    empresa_nome = emp.nome_fantasia or emp.razao_social

            # Tipo de Solo
            tipo_solo_desc = ""
            if prop.id_tipo_solo:
                solo = TipoSolo.query.get(prop.id_tipo_solo)
                if solo:
                    tipo_solo_desc = solo.descricao

            # Classe de Capacidade de Uso
            classe_uso_sigla = ""
            classe_uso_desc = ""
            if prop.id_classe_capacidade_uso:
                classe = ClasseCapacidadeUso.query.get(prop.id_classe_capacidade_uso)
                if classe:
                    classe_uso_sigla = classe.sigla
                    classe_uso_desc = classe.aptidao_principal or classe.descricao

            resultado.append({
                "id_propriedade": prop.id_propriedade,
                "nome_propriedade": prop.nome_propriedade,
                "id_empresa": prop.id_empresa,
                "empresa_nome": empresa_nome,
                "car": prop.car,
                "ccir": prop.ccir,
                "nirf": prop.nirf,
                "ponto_referencia": prop.ponto_referencia,
                "latitude": float(prop.latitude) if prop.latitude is not None else None,
                "longitude": float(prop.longitude) if prop.longitude is not None else None,
                "area_total": float(prop.area_total) if prop.area_total is not None else None,
                "area_agricultavel": float(prop.area_agricultavel) if prop.area_agricultavel is not None else None,
                "area_preservacao": float(prop.area_preservacao) if prop.area_preservacao is not None else None,
                "area_pastagem": float(prop.area_pastagem) if prop.area_pastagem is not None else None,
                "area_vegetacao_nativa": float(prop.area_vegetacao_nativa) if prop.area_vegetacao_nativa is not None else None,
                "altitude_media": prop.altitude_media,
                "id_tipo_solo": prop.id_tipo_solo,
                "tipo_solo_descricao": tipo_solo_desc,
                "id_classe_capacidade_uso": prop.id_classe_capacidade_uso,
                "classe_capacidade_uso_sigla": classe_uso_sigla,
                "classe_capacidade_uso_descricao": classe_uso_desc,
                "observacoes": prop.observacoes,
                "status": prop.status,
                "data_cadastro": prop.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if prop.data_cadastro else None,
                "endereco": endereco
            })

        return resultado

    @staticmethod
    def buscar_por_id(id_propriedade):
        """
        Retorna uma única propriedade pelo seu id, no mesmo formato de listar_todas().
        """
        prop = Propriedade.query.get(id_propriedade)
        if not prop:
            raise ValueError("Propriedade não encontrada.")

        # Reaproveita a montagem de listar_todas filtrando pelo id
        for item in PropriedadeService.listar_todas():
            if item["id_propriedade"] == prop.id_propriedade:
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
    def criar_propriedade(dados):
        """
        Cria uma nova Propriedade.
        Se os campos de endereço forem passados, cria ou associa o Logradouro/Bairro.
        """
        # Validação de campos obrigatórios
        nome = dados.get("nome_propriedade")
        id_empresa = dados.get("id_empresa")
        car = dados.get("car")

        if not nome or not str(nome).strip():
            raise ValueError("O nome da propriedade é obrigatório.")
        if not id_empresa:
            raise ValueError("A empresa agrícola vinculada é obrigatória.")
        if not car or not str(car).strip():
            raise ValueError("O CAR (Cadastro Ambiental Rural) é obrigatório.")

        # Verificar se a empresa existe
        empresa = EmpresaAgricola.query.get(id_empresa)
        if not empresa:
            raise ValueError("Empresa agrícola informada não foi encontrada.")

        # Coordenadas obrigatórias
        latitude = PropriedadeService._to_decimal(dados.get("latitude"), "latitude")
        longitude = PropriedadeService._to_decimal(dados.get("longitude"), "longitude")
        if latitude is None or longitude is None:
            raise ValueError("Latitude e Longitude são obrigatórias.")

        # Áreas
        area_total = PropriedadeService._to_decimal(dados.get("area_total"), "area_total")
        area_agricultavel = PropriedadeService._to_decimal(dados.get("area_agricultavel"), "area_agricultavel")
        area_preservacao = PropriedadeService._to_decimal(dados.get("area_preservacao"), "area_preservacao")
        if area_total is None or area_agricultavel is None or area_preservacao is None:
            raise ValueError("Área Total, Área Agricultável e Área de Preservação são obrigatórias.")

        area_pastagem = PropriedadeService._to_decimal(dados.get("area_pastagem"), "area_pastagem")
        area_vegetacao_nativa = PropriedadeService._to_decimal(dados.get("area_vegetacao_nativa"), "area_vegetacao_nativa")

        altitude_media = dados.get("altitude_media")
        altitude_media = int(altitude_media) if altitude_media not in (None, "") else None

        # Tratar Endereço (opcional) reaproveitando o padrão de Empresa Agrícola
        id_logradouro = None
        cep = dados.get("cep")
        id_cidade = dados.get("id_cidade") or dados.get("cidade_id") or dados.get("id_municipio")
        nome_bairro = dados.get("bairro")
        logradouro_nome = dados.get("logradouro")

        if cep and id_cidade and logradouro_nome:
            cep_limpo = ''.join(filter(str.isdigit, str(cep)))

            cidade = Cidade.query.get(id_cidade)
            if not cidade:
                raise ValueError("Cidade informada não foi encontrada no banco de dados.")

            # Bairro pode não vir do formulário; usa "Zona Rural" como padrão
            nome_bairro = (nome_bairro or "Zona Rural").strip()
            bairro = Bairro.query.filter_by(nome_bairro=nome_bairro, id_cidade=id_cidade).first()
            if not bairro:
                bairro = Bairro(nome_bairro=nome_bairro, id_cidade=id_cidade)
                db.session.add(bairro)
                db.session.flush()

            logr = Logradouro(
                cep=cep_limpo,
                logradouro=logradouro_nome.strip(),
                numero=(dados.get("numero") or "").strip() or None,
                complemento=(dados.get("complemento") or "").strip() or None,
                id_bairro=bairro.id_bairro
            )
            db.session.add(logr)
            db.session.flush()
            id_logradouro = logr.id_logradouro

        nova_propriedade = Propriedade(
            nome_propriedade=nome.strip(),
            id_empresa=id_empresa,
            car=car.strip(),
            ccir=(dados.get("ccir") or "").strip() or None,
            nirf=(dados.get("nirf") or "").strip() or None,
            id_logradouro=id_logradouro,
            ponto_referencia=(dados.get("ponto_referencia") or "").strip() or None,
            latitude=latitude,
            longitude=longitude,
            area_total=area_total,
            area_agricultavel=area_agricultavel,
            area_preservacao=area_preservacao,
            area_pastagem=area_pastagem,
            area_vegetacao_nativa=area_vegetacao_nativa,
            altitude_media=altitude_media,
            id_tipo_solo=dados.get("id_tipo_solo") or None,
            id_classe_capacidade_uso=dados.get("id_classe_capacidade_uso") or None,
            observacoes=(dados.get("observacoes") or "").strip() or None
        )

        db.session.add(nova_propriedade)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a propriedade no banco de dados: {str(e)}")

        return nova_propriedade

    @staticmethod
    def atualizar_propriedade(id_propriedade, dados):
        """
        Atualiza os dados de uma Propriedade existente.
        Apenas os campos enviados no payload são alterados.
        """
        prop = Propriedade.query.get(id_propriedade)
        if not prop:
            raise ValueError("Propriedade não encontrada.")

        # Vinculação
        if "nome_propriedade" in dados:
            nome = (dados.get("nome_propriedade") or "").strip()
            if not nome:
                raise ValueError("O nome da propriedade não pode ficar vazio.")
            prop.nome_propriedade = nome

        if "id_empresa" in dados and dados.get("id_empresa"):
            empresa = EmpresaAgricola.query.get(dados.get("id_empresa"))
            if not empresa:
                raise ValueError("Empresa agrícola informada não foi encontrada.")
            prop.id_empresa = dados.get("id_empresa")

        # Identificação Legal
        if "car" in dados:
            car = (dados.get("car") or "").strip()
            if not car:
                raise ValueError("O CAR não pode ficar vazio.")
            prop.car = car
        if "ccir" in dados:
            prop.ccir = (dados.get("ccir") or "").strip() or None
        if "nirf" in dados:
            prop.nirf = (dados.get("nirf") or "").strip() or None
        if "ponto_referencia" in dados:
            prop.ponto_referencia = (dados.get("ponto_referencia") or "").strip() or None

        # Coordenadas
        if "latitude" in dados:
            lat = PropriedadeService._to_decimal(dados.get("latitude"), "latitude")
            if lat is None:
                raise ValueError("Latitude inválida.")
            prop.latitude = lat
        if "longitude" in dados:
            lon = PropriedadeService._to_decimal(dados.get("longitude"), "longitude")
            if lon is None:
                raise ValueError("Longitude inválida.")
            prop.longitude = lon

        # Áreas
        if "area_total" in dados:
            prop.area_total = PropriedadeService._to_decimal(dados.get("area_total"), "area_total")
        if "area_agricultavel" in dados:
            prop.area_agricultavel = PropriedadeService._to_decimal(dados.get("area_agricultavel"), "area_agricultavel")
        if "area_preservacao" in dados:
            prop.area_preservacao = PropriedadeService._to_decimal(dados.get("area_preservacao"), "area_preservacao")
        if "area_pastagem" in dados:
            prop.area_pastagem = PropriedadeService._to_decimal(dados.get("area_pastagem"), "area_pastagem")
        if "area_vegetacao_nativa" in dados:
            prop.area_vegetacao_nativa = PropriedadeService._to_decimal(dados.get("area_vegetacao_nativa"), "area_vegetacao_nativa")
        if "altitude_media" in dados:
            altitude = dados.get("altitude_media")
            prop.altitude_media = int(altitude) if altitude not in (None, "") else None

        # Outras Informações
        if "id_tipo_solo" in dados:
            prop.id_tipo_solo = dados.get("id_tipo_solo") or None
        if "id_classe_capacidade_uso" in dados:
            prop.id_classe_capacidade_uso = dados.get("id_classe_capacidade_uso") or None
        if "observacoes" in dados:
            prop.observacoes = (dados.get("observacoes") or "").strip() or None
        if "status" in dados:
            prop.status = bool(dados.get("status"))

        # Endereço (opcional) — cria novo logradouro se dados completos forem enviados
        cep = dados.get("cep")
        id_cidade = dados.get("id_cidade") or dados.get("cidade_id") or dados.get("id_municipio")
        logradouro_nome = dados.get("logradouro")
        if cep and id_cidade and logradouro_nome:
            cep_limpo = ''.join(filter(str.isdigit, str(cep)))

            cidade = Cidade.query.get(id_cidade)
            if not cidade:
                raise ValueError("Cidade informada não foi encontrada no banco de dados.")

            nome_bairro = (dados.get("bairro") or "Zona Rural").strip()
            bairro = Bairro.query.filter_by(nome_bairro=nome_bairro, id_cidade=id_cidade).first()
            if not bairro:
                bairro = Bairro(nome_bairro=nome_bairro, id_cidade=id_cidade)
                db.session.add(bairro)
                db.session.flush()

            logr = Logradouro(
                cep=cep_limpo,
                logradouro=logradouro_nome.strip(),
                numero=(dados.get("numero") or "").strip() or None,
                complemento=(dados.get("complemento") or "").strip() or None,
                id_bairro=bairro.id_bairro
            )
            db.session.add(logr)
            db.session.flush()
            prop.id_logradouro = logr.id_logradouro

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a propriedade no banco de dados: {str(e)}")

        return prop

    @staticmethod
    def excluir_propriedade(id_propriedade):
        """
        Exclui uma Propriedade pelo seu id.
        """
        prop = Propriedade.query.get(id_propriedade)
        if not prop:
            raise ValueError("Propriedade não encontrada.")

        db.session.delete(prop)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a propriedade no banco de dados: {str(e)}")

        return True


from models import db
from models.empresa_agricola import EmpresaAgricola
from models.logradouro import Logradouro
from models.bairro import Bairro
from models.cidade import Cidade
from models.estado import Estado
from models.tipo_empresa import TipoEmpresa
from models.regime_tributario import RegimeTributario

class EmpresaAgricolaService:
    @staticmethod
    def listar_todas():
        """
        Retorna a lista de todas as empresas agrícolas cadastradas, 
        incluindo informações de endereço mapeadas.
        """
        empresas = EmpresaAgricola.query.order_by(EmpresaAgricola.data_cadastro.desc()).all()
        resultado = []
        
        for emp in empresas:
            # Carregar relações de endereço
            endereco = None
            if emp.id_logradouro:
                logr = Logradouro.query.get(emp.id_logradouro)
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
                    
            # Obter tipos estruturados
            tipo_desc = ""
            if emp.id_tipo_empresa:
                tipo = TipoEmpresa.query.get(emp.id_tipo_empresa)
                if tipo:
                    tipo_desc = tipo.descricao

            regime_desc = ""
            if emp.id_regime_tributario:
                regime = RegimeTributario.query.get(emp.id_regime_tributario)
                if regime:
                    regime_desc = regime.descricao

            resultado.append({
                "id_empresa": emp.id_empresa,
                "razao_social": emp.razao_social,
                "nome_fantasia": emp.nome_fantasia,
                "cnpj": emp.cnpj,
                "inscricao_estadual": emp.inscricao_estadual,
                "inscricao_municipal": emp.inscricao_municipal,
                "telefone": emp.telefone,
                "email": emp.email,
                "website": emp.website,
                "data_fundacao": emp.data_fundacao.strftime("%Y-%m-%d") if emp.data_fundacao else None,
                "status": emp.status,
                "data_cadastro": emp.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if emp.data_cadastro else None,
                "id_tipo_empresa": emp.id_tipo_empresa,
                "tipo_empresa_descricao": tipo_desc,
                "id_regime_tributario": emp.id_regime_tributario,
                "regime_tributario_descricao": regime_desc,
                "endereco": endereco
            })
            
        return resultado

    @staticmethod
    def criar_empresa(dados):
        """
        Cria uma nova Empresa Agrícola.
        Se os campos de endereço forem passados, cria ou associa o Logradouro, Bairro etc.
        """
        # Validação básica de campos obrigatórios
        cnpj = dados.get("cnpj")
        razao_social = dados.get("razao_social")
        email = dados.get("email")

        if not cnpj or not razao_social or not email:
            raise ValueError("CNPJ, Razão Social e E-mail são campos obrigatórios.")

        # Sanitizar CNPJ (guardar apenas números)
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ inválido. Deve conter 14 dígitos numéricos.")

        # Verificar se o CNPJ já está cadastrado
        empresa_existente = EmpresaAgricola.query.filter_by(cnpj=cnpj_limpo).first()
        if empresa_existente:
            raise ValueError("Este CNPJ já está cadastrado no sistema.")

        id_logradouro = None

        # Tratar Endereço se as informações de CEP forem fornecidas
        cep = dados.get("cep")
        id_cidade = dados.get("id_cidade") or dados.get("cidade_id") or dados.get("id_municipio")
        nome_bairro = dados.get("bairro")
        logradouro_nome = dados.get("logradouro")

        if cep and id_cidade and nome_bairro and logradouro_nome:
            # Sanitizar CEP
            cep_limpo = ''.join(filter(str.isdigit, str(cep)))
            
            # Garantir existência da Cidade
            cidade = Cidade.query.get(id_cidade)
            if not cidade:
                raise ValueError("Cidade informada não foi encontrada no banco de dados.")

            # Buscar Bairro existente na cidade ou criar novo
            bairro = Bairro.query.filter_by(
                nome_bairro=nome_bairro.strip(), 
                id_cidade=id_cidade
            ).first()
            
            if not bairro:
                bairro = Bairro(
                    nome_bairro=nome_bairro.strip(),
                    id_cidade=id_cidade
                )
                db.session.add(bairro)
                db.session.flush() # obtem o id_bairro gerado antes de commitar tudo

            # Criar novo Logradouro
            logr = Logradouro(
                cep=cep_limpo,
                logradouro=logradouro_nome.strip(),
                numero=dados.get("numero", "").strip() or None,
                complemento=dados.get("complemento", "").strip() or None,
                id_bairro=bairro.id_bairro
            )
            db.session.add(logr)
            db.session.flush()
            id_logradouro = logr.id_logradouro

        # Criar a Empresa Agrícola
        nova_empresa = EmpresaAgricola(
            razao_social=razao_social.strip(),
            nome_fantasia=dados.get("nome_fantasia", "").strip() or None,
            cnpj=cnpj_limpo,
            inscricao_estadual=dados.get("inscricao_estadual", "").strip() or None,
            inscricao_municipal=dados.get("inscricao_municipal", "").strip() or None,
            telefone=dados.get("telefone", "").strip() or None,
            email=email.strip(),
            website=dados.get("website", "").strip() or None,
            data_fundacao=dados.get("data_fundacao") or None,
            id_tipo_empresa=dados.get("id_tipo_empresa"),
            id_regime_tributario=dados.get("id_regime_tributario"),
            id_logradouro=id_logradouro
        )

        db.session.add(nova_empresa)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a empresa no banco de dados: {str(e)}")

        return nova_empresa


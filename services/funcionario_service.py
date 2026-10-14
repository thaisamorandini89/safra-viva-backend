from models import db
from models.funcionario import Funcionario
from models.funcionario_propriedade import FuncionarioPropriedade
from models.propriedade import Propriedade


class FuncionarioService:
    @staticmethod
    def _serializar(func):
        return {
            "id_funcionario": func.id_funcionario,
            "nome_completo": func.nome_completo,
            "cpf": func.cpf,
            "rg": func.rg,
            "data_nascimento": func.data_nascimento.strftime("%Y-%m-%d") if func.data_nascimento else None,
            "telefone": func.telefone,
            "email": func.email,
            "cargo": func.cargo,
            "data_admissao": func.data_admissao.strftime("%Y-%m-%d") if func.data_admissao else None,
            "data_desligamento": func.data_desligamento.strftime("%Y-%m-%d") if func.data_desligamento else None,
            "observacoes": func.observacoes,
            "status": func.status,
            "data_cadastro": func.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if func.data_cadastro else None,
        }

    @staticmethod
    def criar_funcionario(dados):
        """Cria um funcionário. `dados` é um FuncionarioCreate já validado."""
        if Funcionario.query.filter_by(cpf=dados.cpf).first():
            raise ValueError("Já existe um funcionário cadastrado com este CPF.")

        funcionario = Funcionario(
            nome_completo=dados.nome_completo,
            cpf=dados.cpf,
            rg=dados.rg,
            data_nascimento=dados.data_nascimento,
            telefone=dados.telefone,
            email=dados.email,
            cargo=dados.cargo,
            data_admissao=dados.data_admissao,
            data_desligamento=dados.data_desligamento,
            observacoes=dados.observacoes,
        )

        db.session.add(funcionario)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao cadastrar o funcionário: {str(e)}")

        return funcionario

    @staticmethod
    def buscar_por_id(id_funcionario):
        funcionario = Funcionario.query.get(id_funcionario)
        if not funcionario:
            raise ValueError("Funcionário não encontrado.")
        return FuncionarioService._serializar(funcionario)

    @staticmethod
    def listar(nome=None, cpf=None, cargo=None, id_propriedade=None, status=None):
        """Lista funcionários com filtros opcionais."""
        query = Funcionario.query

        if nome:
            query = query.filter(Funcionario.nome_completo.ilike(f"%{nome}%"))
        if cpf:
            cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
            query = query.filter(Funcionario.cpf.ilike(f"%{cpf_limpo}%"))
        if cargo:
            query = query.filter(Funcionario.cargo.ilike(f"%{cargo}%"))
        if status is not None:
            query = query.filter(Funcionario.status == status)
        if id_propriedade:
            query = (
                query.join(
                    FuncionarioPropriedade,
                    FuncionarioPropriedade.id_funcionario == Funcionario.id_funcionario
                )
                .filter(FuncionarioPropriedade.id_propriedade == id_propriedade)
                .distinct()
            )

        funcionarios = query.order_by(Funcionario.data_cadastro.desc()).all()
        return [FuncionarioService._serializar(f) for f in funcionarios]

    @staticmethod
    def atualizar_funcionario(id_funcionario, dados):
        """Atualiza um funcionário. `dados` é um FuncionarioUpdate já validado."""
        funcionario = Funcionario.query.get(id_funcionario)
        if not funcionario:
            raise ValueError("Funcionário não encontrado.")

        valores = dados.model_dump(exclude_unset=True)

        novo_cpf = valores.get("cpf")
        if novo_cpf and novo_cpf != funcionario.cpf:
            if Funcionario.query.filter_by(cpf=novo_cpf).first():
                raise ValueError("Já existe um funcionário cadastrado com este CPF.")

        for campo, valor in valores.items():
            setattr(funcionario, campo, valor)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o funcionário: {str(e)}")

        return funcionario

    @staticmethod
    def inativar_funcionario(id_funcionario):
        """Inativa o funcionário (soft delete via status)."""
        funcionario = Funcionario.query.get(id_funcionario)
        if not funcionario:
            raise ValueError("Funcionário não encontrado.")

        funcionario.status = False
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao inativar o funcionário: {str(e)}")

        return funcionario

    @staticmethod
    def vincular_propriedade(id_funcionario, id_propriedade):
        """Vincula um funcionário a uma propriedade."""
        funcionario = Funcionario.query.get(id_funcionario)
        if not funcionario:
            raise ValueError("Funcionário não encontrado.")

        propriedade = Propriedade.query.get(id_propriedade)
        if not propriedade:
            raise ValueError("Propriedade informada não foi encontrada.")

        vinculo = FuncionarioPropriedade(
            id_funcionario=id_funcionario,
            id_propriedade=id_propriedade,
        )

        db.session.add(vinculo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao vincular a propriedade: {str(e)}")

        return vinculo

    @staticmethod
    def listar_propriedades(id_funcionario):
        """Lista as propriedades vinculadas a um funcionário."""
        funcionario = Funcionario.query.get(id_funcionario)
        if not funcionario:
            raise ValueError("Funcionário não encontrado.")

        vinculos = (
            FuncionarioPropriedade.query
            .filter_by(id_funcionario=id_funcionario)
            .order_by(FuncionarioPropriedade.data_vinculacao.desc())
            .all()
        )

        resultado = []
        for vinc in vinculos:
            propriedade = Propriedade.query.get(vinc.id_propriedade)
            resultado.append({
                "id_funcionario_propriedade": vinc.id_funcionario_propriedade,
                "id_propriedade": vinc.id_propriedade,
                "nome_propriedade": propriedade.nome_propriedade if propriedade else "",
                "data_vinculacao": vinc.data_vinculacao.strftime("%Y-%m-%d %H:%M:%S") if vinc.data_vinculacao else None,
            })

        return resultado

    @staticmethod
    def indicadores():
        """Retorna os indicadores de dashboard de funcionários."""
        total = Funcionario.query.count()
        ativos = Funcionario.query.filter_by(status=True).count()
        inativos = Funcionario.query.filter_by(status=False).count()

        contagem = (
            db.session.query(
                FuncionarioPropriedade.id_propriedade,
                db.func.count(db.func.distinct(FuncionarioPropriedade.id_funcionario))
            )
            .group_by(FuncionarioPropriedade.id_propriedade)
            .all()
        )

        por_propriedade = []
        for id_propriedade, quantidade in contagem:
            propriedade = Propriedade.query.get(id_propriedade)
            por_propriedade.append({
                "id_propriedade": id_propriedade,
                "nome_propriedade": propriedade.nome_propriedade if propriedade else "",
                "quantidade": quantidade,
            })

        return {
            "total": total,
            "ativos": ativos,
            "inativos": inativos,
            "por_propriedade": por_propriedade,
        }

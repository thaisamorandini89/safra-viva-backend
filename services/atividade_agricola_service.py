from datetime import date
from decimal import Decimal

from models import db
from models.atividade_agricola import AtividadeAgricola
from models.atividade_insumo import AtividadeInsumo
from models.atividade_maquina import AtividadeMaquina
from models.categoria_atividade import CategoriaAtividade
from models.tipo_atividade import TipoAtividade
from models.talhao import Talhao
from models.funcionario import Funcionario
from models.maquina import Maquina
from models.insumo import Insumo
from models.produto import Produto


def _num(v):
    return float(v) if v is not None else None


def _data(d):
    return d.strftime("%Y-%m-%d") if d else None


class AtividadeAgricolaService:
    # ------------------------------------------------------------------ #
    # Serializacao
    # ------------------------------------------------------------------ #
    @staticmethod
    def _custo_total(atv):
        if atv.custo_operacao is not None:
            return float(atv.custo_operacao)
        total = Decimal(0)
        for i in atv.insumos:
            total += (i.custo or Decimal(0))
        for m in atv.maquinas:
            total += (m.custo or Decimal(0))
        return float(total)

    @staticmethod
    def _duracao_dias(atv):
        if not atv.data_fim:
            return 1
        return max(1, (atv.data_fim - atv.data_inicio).days + 1)

    @staticmethod
    def _atrasada(atv):
        if atv.status == "Concluída":
            return False
        prazo = atv.data_fim or atv.data_inicio
        return bool(prazo and prazo < date.today())

    @staticmethod
    def serializar(atv):
        return {
            "id_atividade_agricola": atv.id_atividade_agricola,
            "id": atv.id_atividade_agricola,
            "id_categoria_atividade": atv.id_categoria_atividade,
            "categoria": atv.categoria.nome if atv.categoria else None,
            "id_tipo_atividade": atv.id_tipo_atividade,
            "tipo_atividade": atv.tipo.descricao if atv.tipo else None,
            "id_talhao": atv.id_talhao,
            "nome_talhao": atv.talhao.nome_talhao if atv.talhao else None,
            "codigo_talhao": atv.talhao.codigo_talhao if atv.talhao else None,
            "id_propriedade": atv.id_propriedade,
            "id_empresa": atv.id_empresa,
            "safra": atv.safra,
            "id_funcionario": atv.id_funcionario,
            "id_responsavel": atv.id_funcionario,
            "responsavel": atv.funcionario.nome_completo if atv.funcionario else None,
            "status": atv.status,
            "data_inicio": _data(atv.data_inicio),
            "data_fim": _data(atv.data_fim),
            "custo_operacao": _num(atv.custo_operacao),
            "custo_total": AtividadeAgricolaService._custo_total(atv),
            "duracao_dias": AtividadeAgricolaService._duracao_dias(atv),
            "atrasada": AtividadeAgricolaService._atrasada(atv),
            "insumos_count": len(atv.insumos),
            "maquinas_count": len(atv.maquinas),
            "observacoes": atv.observacoes,
            "insumos": [
                {
                    "id_insumo": i.id_insumo,
                    "nome": i.nome,
                    "unidade": i.unidade,
                    "quantidade": _num(i.quantidade),
                    "custo": _num(i.custo),
                }
                for i in atv.insumos
            ],
            "maquinas": [
                {
                    "id_maquina": m.id_maquina,
                    "nome": m.nome,
                    "horas": _num(m.horas),
                    "custo": _num(m.custo),
                }
                for m in atv.maquinas
            ],
        }

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    @staticmethod
    def _aplicar_filtros(query, filtros):
        filtros = filtros or {}
        if filtros.get("status"):
            query = query.filter(AtividadeAgricola.status == filtros["status"])
        if filtros.get("id_categoria_atividade"):
            query = query.filter(
                AtividadeAgricola.id_categoria_atividade == filtros["id_categoria_atividade"]
            )
        if filtros.get("id_tipo_atividade"):
            query = query.filter(
                AtividadeAgricola.id_tipo_atividade == filtros["id_tipo_atividade"]
            )
        if filtros.get("id_talhao"):
            query = query.filter(AtividadeAgricola.id_talhao == filtros["id_talhao"])
        if filtros.get("safra"):
            query = query.filter(AtividadeAgricola.safra == filtros["safra"])
        return query

    @staticmethod
    def listar(filtros=None):
        query = AtividadeAgricolaService._aplicar_filtros(AtividadeAgricola.query, filtros)
        atividades = query.order_by(AtividadeAgricola.data_inicio.desc()).all()
        resultado = [AtividadeAgricolaService.serializar(a) for a in atividades]

        busca = (filtros or {}).get("busca")
        if busca:
            termo = str(busca).strip().lower()
            resultado = [
                r for r in resultado
                if termo in (r.get("tipo_atividade") or "").lower()
                or termo in (r.get("responsavel") or "").lower()
                or termo in (r.get("nome_talhao") or "").lower()
            ]
        return resultado

    @staticmethod
    def obter(id_atividade_agricola):
        atv = AtividadeAgricola.query.get(id_atividade_agricola)
        if not atv:
            raise ValueError("Atividade não encontrada.")
        return AtividadeAgricolaService.serializar(atv)

    @staticmethod
    def indicadores(filtros=None):
        atividades = AtividadeAgricolaService.listar(filtros)
        total = len(atividades)
        custo_total = sum(a["custo_total"] for a in atividades)
        em_andamento = sum(1 for a in atividades if a["status"] == "Em Andamento")
        planejadas = sum(1 for a in atividades if a["status"] == "Planejada")
        concluidas = sum(1 for a in atividades if a["status"] == "Concluída")
        atrasadas = sum(1 for a in atividades if a["atrasada"])
        return {
            "total": total,
            "custo_total": custo_total,
            "em_andamento": em_andamento,
            "planejadas": planejadas,
            "concluidas": concluidas,
            "atrasadas": atrasadas,
        }

    # ------------------------------------------------------------------ #
    # Escrita
    # ------------------------------------------------------------------ #
    @staticmethod
    def _validar_referencias(dados):
        if not CategoriaAtividade.query.get(dados["id_categoria_atividade"]):
            raise ValueError("Categoria de atividade não encontrada.")
        if not TipoAtividade.query.get(dados["id_tipo_atividade"]):
            raise ValueError("Tipo de atividade não encontrado.")
        talhao = Talhao.query.get(dados["id_talhao"])
        if not talhao:
            raise ValueError("Talhão não encontrado.")
        if dados.get("id_funcionario"):
            if not Funcionario.query.get(dados["id_funcionario"]):
                raise ValueError("Funcionário (responsável) não encontrado.")
        return talhao

    @staticmethod
    def _montar_insumos(itens):
        filhos = []
        for item in itens or []:
            insumo = Insumo.query.get(item["id_insumo"])
            if not insumo:
                raise ValueError(f"Insumo {item['id_insumo']} não encontrado.")
            produto = Produto.query.get(insumo.id_produto)
            filhos.append(AtividadeInsumo(
                id_insumo=item["id_insumo"],
                nome=produto.nome_produto if produto else None,
                unidade=produto.unidade_medida if produto else None,
                quantidade=item.get("quantidade"),
                custo=item.get("custo"),
            ))
        return filhos

    @staticmethod
    def _montar_maquinas(itens):
        filhos = []
        for item in itens or []:
            maquina = Maquina.query.get(item["id_maquina"])
            if not maquina:
                raise ValueError(f"Máquina {item['id_maquina']} não encontrada.")
            filhos.append(AtividadeMaquina(
                id_maquina=item["id_maquina"],
                nome=maquina.nome,
                horas=item.get("horas"),
                custo=item.get("custo"),
            ))
        return filhos

    @staticmethod
    def criar(dados):
        talhao = AtividadeAgricolaService._validar_referencias(dados)
        id_propriedade = dados.get("id_propriedade") or talhao.id_propriedade

        atv = AtividadeAgricola(
            id_categoria_atividade=dados["id_categoria_atividade"],
            id_tipo_atividade=dados["id_tipo_atividade"],
            id_talhao=dados["id_talhao"],
            id_propriedade=id_propriedade,
            id_empresa=dados.get("id_empresa"),
            safra=dados.get("safra"),
            id_funcionario=dados.get("id_funcionario"),
            status=dados.get("status", "Planejada"),
            data_inicio=dados["data_inicio"],
            data_fim=dados.get("data_fim"),
            custo_operacao=dados.get("custo_operacao"),
            observacoes=dados.get("observacoes"),
        )
        atv.insumos = AtividadeAgricolaService._montar_insumos(dados.get("insumos"))
        atv.maquinas = AtividadeAgricolaService._montar_maquinas(dados.get("maquinas"))

        db.session.add(atv)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a atividade: {str(e)}")
        return AtividadeAgricolaService.serializar(atv)

    @staticmethod
    def atualizar(id_atividade_agricola, dados):
        atv = AtividadeAgricola.query.get(id_atividade_agricola)
        if not atv:
            raise ValueError("Atividade não encontrada.")

        if "id_categoria_atividade" in dados and dados["id_categoria_atividade"] is not None:
            if not CategoriaAtividade.query.get(dados["id_categoria_atividade"]):
                raise ValueError("Categoria de atividade não encontrada.")
            atv.id_categoria_atividade = dados["id_categoria_atividade"]
        if "id_tipo_atividade" in dados and dados["id_tipo_atividade"] is not None:
            if not TipoAtividade.query.get(dados["id_tipo_atividade"]):
                raise ValueError("Tipo de atividade não encontrado.")
            atv.id_tipo_atividade = dados["id_tipo_atividade"]
        if "id_talhao" in dados and dados["id_talhao"] is not None:
            talhao = Talhao.query.get(dados["id_talhao"])
            if not talhao:
                raise ValueError("Talhão não encontrado.")
            atv.id_talhao = dados["id_talhao"]
            if not dados.get("id_propriedade"):
                atv.id_propriedade = talhao.id_propriedade
        if "id_propriedade" in dados and dados["id_propriedade"] is not None:
            atv.id_propriedade = dados["id_propriedade"]
        if "id_empresa" in dados:
            atv.id_empresa = dados["id_empresa"]
        if "safra" in dados:
            atv.safra = dados["safra"]
        if "id_funcionario" in dados:
            if dados["id_funcionario"] and not Funcionario.query.get(dados["id_funcionario"]):
                raise ValueError("Funcionário (responsável) não encontrado.")
            atv.id_funcionario = dados["id_funcionario"]
        if "status" in dados and dados["status"] is not None:
            atv.status = dados["status"]
        if "data_inicio" in dados and dados["data_inicio"] is not None:
            atv.data_inicio = dados["data_inicio"]
        if "data_fim" in dados:
            atv.data_fim = dados["data_fim"]
        if "custo_operacao" in dados:
            atv.custo_operacao = dados["custo_operacao"]
        if "observacoes" in dados:
            atv.observacoes = dados["observacoes"]

        if dados.get("insumos") is not None:
            atv.insumos = AtividadeAgricolaService._montar_insumos(dados.get("insumos"))
        if dados.get("maquinas") is not None:
            atv.maquinas = AtividadeAgricolaService._montar_maquinas(dados.get("maquinas"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a atividade: {str(e)}")
        return AtividadeAgricolaService.serializar(atv)

    @staticmethod
    def excluir(id_atividade_agricola):
        atv = AtividadeAgricola.query.get(id_atividade_agricola)
        if not atv:
            raise ValueError("Atividade não encontrada.")
        db.session.delete(atv)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a atividade: {str(e)}")
        return True

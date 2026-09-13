from models import db
from models.empresa_agricola import EmpresaAgricola

class EmpresaAgricolaService:
    @staticmethod
    def create_empresa_agricola(data):
        new_empresa = EmpresaAgricola(**data)
        db.session.add(new_empresa)
        db.session.commit()
        return new_empresa

    @staticmethod
    def get_all_empresas():
        return EmpresaAgricola.query.all()

    @staticmethod
    def get_empresa_by_id(empresa_id):
        return EmpresaAgricola.query.get(empresa_id)

    @staticmethod
    def update_empresa_agricola(empresa_id, data):
        empresa = EmpresaAgricola.query.get(empresa_id)
        if empresa:
            for key, value in data.items():
                setattr(empresa, key, value)
            db.session.commit()
        return empresa

    @staticmethod
    def delete_empresa_agricola(empresa_id):
        empresa = EmpresaAgricola.query.get(empresa_id)
        if empresa:
            db.session.delete(empresa)
            db.session.commit()
        return empresa
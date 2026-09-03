from models.tipo_empresa import TipoEmpresa

class TipoEmpresaService:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all_tipo_empresas(self):
        return self.db_session.query(TipoEmpresa).all()

    def get_tipo_empresa_by_id(self, tipo_empresa_id):
        return self.db_session.query(TipoEmpresa).filter_by(id=tipo_empresa_id).first()

    def create_tipo_empresa(self, tipo_empresa_data):
        new_tipo_empresa = TipoEmpresa(**tipo_empresa_data)
        self.db_session.add(new_tipo_empresa)
        self.db_session.commit()
        return new_tipo_empresa

    def update_tipo_empresa(self, tipo_empresa_id, tipo_empresa_data):
        tipo_empresa = self.get_tipo_empresa_by_id(tipo_empresa_id)
        if tipo_empresa:
            for key, value in tipo_empresa_data.items():
                setattr(tipo_empresa, key, value)
            self.db_session.commit()
            return tipo_empresa
        return None

    def delete_tipo_empresa(self, tipo_empresa_id):
        tipo_empresa = self.get_tipo_empresa_by_id(tipo_empresa_id)
        if tipo_empresa:
            self.db_session.delete(tipo_empresa)
            self.db_session.commit()
            return True
        return False
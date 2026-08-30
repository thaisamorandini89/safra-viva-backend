from models.tipo_solo import TipoSolo

class TipoSoloService:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all(self):
        return self.db_session.query(TipoSolo).all()

    def get_by_id(self, tipo_solo_id):
        return self.db_session.query(TipoSolo).filter(TipoSolo.id == tipo_solo_id).first()

    def create(self, tipo_solo_data):
        new_tipo_solo = TipoSolo(**tipo_solo_data)
        self.db_session.add(new_tipo_solo)
        self.db_session.commit()
        return new_tipo_solo

    def update(self, tipo_solo_id, tipo_solo_data):
        tipo_solo = self.get_by_id(tipo_solo_id)
        if tipo_solo:
            for key, value in tipo_solo_data.items():
                setattr(tipo_solo, key, value)
            self.db_session.commit()
        return tipo_solo

    def delete(self, tipo_solo_id):
        tipo_solo = self.get_by_id(tipo_solo_id)
        if tipo_solo:
            self.db_session.delete(tipo_solo)
            self.db_session.commit()
        return tipo_solo
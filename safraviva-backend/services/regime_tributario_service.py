from models.regime_tributario import RegimeTributario

class RegimeTributarioService:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all_regimes(self):
        return self.db_session.query(RegimeTributario).all()

    def get_regime_by_id(self, regime_id):
        return self.db_session.query(RegimeTributario).filter_by(id=regime_id).first()

    def create_regime(self, regime_data):
        new_regime = RegimeTributario(**regime_data)
        self.db_session.add(new_regime)
        self.db_session.commit()
        return new_regime

    def update_regime(self, regime_id, regime_data):
        regime = self.get_regime_by_id(regime_id)
        if regime:
            for key, value in regime_data.items():
                setattr(regime, key, value)
            self.db_session.commit()
            return regime
        return None

    def delete_regime(self, regime_id):
        regime = self.get_regime_by_id(regime_id)
        if regime:
            self.db_session.delete(regime)
            self.db_session.commit()
            return True
        return False
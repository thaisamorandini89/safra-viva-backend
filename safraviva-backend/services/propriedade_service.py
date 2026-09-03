from models.propriedade import Propriedade
from models import db

class PropriedadeService:
    @staticmethod
    def list_properties():
        return Propriedade.query.all()

    @staticmethod
    def get_property(property_id):
        return Propriedade.query.get(property_id)

    @staticmethod
    def create_property(data):
        new_property = Propriedade(**data)
        db.session.add(new_property)
        db.session.commit()
        return new_property

    @staticmethod
    def update_property(property_id, data):
        property_to_update = Propriedade.query.get(property_id)
        if property_to_update:
            for key, value in data.items():
                setattr(property_to_update, key, value)
            db.session.commit()
            return property_to_update
        return None

    @staticmethod
    def delete_property(property_id):
        property_to_delete = Propriedade.query.get(property_id)
        if property_to_delete:
            db.session.delete(property_to_delete)
            db.session.commit()
            return True
        return False
from models.classe_capacidade_uso import ClasseCapacidadeUso

class ClasseCapacidadeUsoService:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all_classes(self):
        return self.db_session.query(ClasseCapacidadeUso).all()

    def get_class_by_id(self, class_id):
        return self.db_session.query(ClasseCapacidadeUso).filter_by(id=class_id).first()

    def create_class(self, class_data):
        new_class = ClasseCapacidadeUso(**class_data)
        self.db_session.add(new_class)
        self.db_session.commit()
        return new_class

    def update_class(self, class_id, class_data):
        class_to_update = self.get_class_by_id(class_id)
        if class_to_update:
            for key, value in class_data.items():
                setattr(class_to_update, key, value)
            self.db_session.commit()
            return class_to_update
        return None

    def delete_class(self, class_id):
        class_to_delete = self.get_class_by_id(class_id)
        if class_to_delete:
            self.db_session.delete(class_to_delete)
            self.db_session.commit()
            return True
        return False
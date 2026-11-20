from app import create_app
from models import db
from models.empresa_agricola import EmpresaAgricola
from models.usuario import Usuario
from services.auth_service import AuthService

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Enquanto a migração formal (Alembic) não existe, cria só a tabela usuario se faltar.
        Usuario.__table__.create(bind=db.engine, checkfirst=True)
        empresa = EmpresaAgricola.query.order_by(EmpresaAgricola.id_empresa).first()
        criados = AuthService.garantir_usuarios_demo(empresa.id_empresa if empresa else None)
        print(f"Usuários de demonstração criados: {criados}")

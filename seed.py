import pandas as pd
from app import create_app, db
from models.estado import Estado
from models.cidade import Cidade

app = create_app()

def run_seed():
    # Mapeamento oficial IBGE
    codigo_para_sigla = {
        11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
        21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL",
        28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR",
        42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF"
    }

    with app.app_context():
        print("Iniciando script de seed...")
        try:
            df = pd.read_excel('dados.xls', skiprows=6)
        except Exception as e:
            print(f"ERRO AO LER ARQUIVO: {e}")
            return

        # --- SEED DE ESTADOS ---
        estados_unicos = df[['UF', 'Nome_UF']].drop_duplicates()
        
        for _, row in estados_unicos.iterrows():
            codigo_ibge = int(row['UF'])
            nome = row['Nome_UF']
            # Busca a sigla no dicionário, se não achar, usa 'XX'
            sigla = codigo_para_sigla.get(codigo_ibge, "XX")
            
            if not Estado.query.get(codigo_ibge):
                print(f"Inserindo Estado: {nome} ({sigla})")
                # Agora o uf_estado recebe a sigla real
                db.session.add(Estado(id_estado=codigo_ibge, uf_estado=sigla, nome_estado=nome))
        
        db.session.commit()
        
        # --- SEED DE CIDADES ---
        print("Iniciando inserção de cidades...")
        count = 0
        for _, row in df.iterrows():
            codigo_cidade = int(row['Código Município Completo'])
            nome_cidade = row['Nome_Município']
            codigo_uf = int(row['UF'])
            
            if not Cidade.query.get(codigo_cidade):
                db.session.add(Cidade(id_cidade=codigo_cidade, nome_cidade=nome_cidade, id_estado=codigo_uf))
                count += 1
        
        db.session.commit()
        print(f"Seed concluído! {count} cidades processadas com sucesso.")

if __name__ == '__main__':
    run_seed()
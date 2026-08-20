# Chama o gerador de dados para gerar todas as instâncias de teste (pequeno, médio, grande e muito grande)

import os
from data_generator import gerar_dados_hospitalares

def gerar_todas():
    cenarios = {
        "pequeno": {
            "num_quartos": 10,        
            "num_pacientes": 40, 
            "horizonte": 7
        },
        "medio": {
            "num_quartos": 30,        
            "num_pacientes": 150, 
            "horizonte": 7
        },
        "grande": {
            "num_quartos": 80,        
            "num_pacientes": 400, 
            "horizonte": 14           
        },
        "muito_grande": {
            "num_quartos": 150,       
            "num_pacientes": 800, 
            "horizonte": 14
        }
    }
    
    for nome, params in cenarios.items():
        diretorio = os.path.join("data", nome)
        os.makedirs(diretorio, exist_ok=True)
        
        print(f"Gerando instância {nome.upper()} em '{diretorio}'...")
        gerar_dados_hospitalares(
            num_quartos=params["num_quartos"],
            num_pacientes=params["num_pacientes"],
            horizonte_planejamento=params["horizonte"],
            diretorio_saida=diretorio
        )
    print("\nTodas as instâncias foram geradas com sucesso!")

if __name__ == "__main__":
    gerar_todas()
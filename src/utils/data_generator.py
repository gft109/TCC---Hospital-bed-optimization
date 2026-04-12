import csv
import random
import os

def gerar_dados_hospitalares(num_quartos=5, num_pacientes=40, horizonte_planejamento=6, diretorio_saida="data"):
    """
    Gera instâncias artificiais de pacientes e quartos baseadas em distribuições
    estatísticas. A alocação de especialidades é proporcional ao tamanho do hospital.
    """
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # =========================================================
    # DISTRIBUIÇÃO PROPORCIONAL DAS ESPECIALIDADES
    # =========================================================
    distribuicao_especialidades = {
        'Geral': 0.35,       # 35% dos quartos
        'Cardiologia': 0.25, # 25% dos quartos
        'Ortopedia': 0.20,   # 20% dos quartos
        'Neurologia': 0.10,  # 10% dos quartos
        'Pediatria': 0.10    # 10% dos quartos
    }
    
    # 1. Pré-calcula a lista exata de especialidades para os quartos
    especialidades_quartos = []
    for esp, percentual in distribuicao_especialidades.items():     
        # Calcula a quantidade exata de quartos para esta especialidade
        qtd = int(num_quartos * percentual)
        especialidades_quartos.extend([esp] * qtd)
        
    # Lida com arredondamentos matemáticos (ex: se a soma der 19 ao invés de 20 quartos)
    while len(especialidades_quartos) < num_quartos:
        especialidades_quartos.append('Geral') # Joga a sobra para a Clínica Geral
        
    # Embaralha para que os quartos não fiquem na ordem exata no CSV
    random.shuffle(especialidades_quartos)

    # Extrai os nomes e os pesos para usar no sorteio dos pacientes
    nomes_especialidades = list(distribuicao_especialidades.keys())
    pesos_especialidades = list(distribuicao_especialidades.values())

    # =========================================================
    # GERAÇÃO DOS QUARTOS E CÁLCULO DA CAPACIDADE
    # =========================================================
    caminho_quartos = os.path.join(diretorio_saida, 'room.csv')
    capacidade_total_hospital = 0  
    
    with open(caminho_quartos, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_quarto', 'capacidade', 'especialidade', 'politica_genero'])
        
        for i in range(1, num_quartos + 1):
            id_quarto = f"R{i}"
            capacidade = 3
            capacidade_total_hospital += capacidade 
            
            # Puxa a especialidade da nossa lista pré-calculada e proporcional
            especialidade = especialidades_quartos.pop()
            
            # Todos os quartos usam a política 'D' (Dinâmica) conforme a sua modelagem
            politica_genero = 'D'
            
            writer.writerow([id_quarto, capacidade, especialidade, politica_genero])

    print(f"Capacidade Física Total do Hospital: {capacidade_total_hospital} leitos.")

    # =========================================================
    # GERAÇÃO DOS PACIENTES (COM TRAVA DE VIABILIDADE)
    # =========================================================
    caminho_pacientes = os.path.join(diretorio_saida, 'patient.csv')
    ocupacao_diaria = {}
    
    with open(caminho_pacientes, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_paciente', 'genero', 'idade', 'dia_admissao', 'los', 'especialidade_requerida'])
        
        pacientes_gerados = 0
        tentativas = 0
        MAX_TENTATIVAS = 5000 
        
        while pacientes_gerados < num_pacientes and tentativas < MAX_TENTATIVAS:
            tentativas += 1
            
            dia_admissao = random.randint(1, horizonte_planejamento)
            los_float = random.gauss(mu=5.0, sigma=1.732)
            los = max(1, int(round(los_float)))
            dias_internado = range(dia_admissao, dia_admissao + los)
            
            if any(ocupacao_diaria.get(d, 0) >= capacidade_total_hospital for d in dias_internado):
                continue 
                
            for d in dias_internado:
                ocupacao_diaria[d] = ocupacao_diaria.get(d, 0) + 1
                
            pacientes_gerados += 1
            id_paciente = f"P{pacientes_gerados}"
            genero = random.choice(['M', 'F'])
            idade = random.randint(1, 90)
            
            # Sorteia a especialidade do paciente usando AS MESMAS PORCENTAGENS do hospital
            especialidade_requerida = random.choices(nomes_especialidades, weights=pesos_especialidades)
            
            writer.writerow([id_paciente, genero, idade, dia_admissao, los, especialidade_requerida])

    print(f"Sucesso! Gerados {num_quartos} quartos e {pacientes_gerados} pacientes viáveis na pasta '{diretorio_saida}/'.")
    if pacientes_gerados < num_pacientes:
        print("Aviso: O hospital lotou antes de gerar todos os pacientes pedidos!")

if __name__ == "__main__":
    gerar_dados_hospitalares()

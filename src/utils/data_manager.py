import csv
import os

def carregar_instancia_csv(diretorio="data"):
    """
    Lê os arquivos room.csv e patient.csv gerados.
    Processa os dados e retorna as estruturas necessárias para o Gurobi/Heurística.
    """
    caminho_quartos = os.path.join(diretorio, 'room.csv')
    caminho_pacientes = os.path.join(diretorio, 'patient.csv')

    # =========================================================================
    # 1. LEITURA DOS QUARTOS
    # =========================================================================
    quartos_info = {}
    quartos = []
    capacidade = {}

    with open(caminho_quartos, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            r_id = row['id_quarto']
            quartos.append(r_id)
            capacidade[r_id] = int(row['capacidade'])
            quartos_info[r_id] = {
                'especialidade': row['especialidade'],
                'politica_genero': row['politica_genero']
            }

    # =========================================================================
    # 2. LEITURA DOS PACIENTES E CÁLCULO DOS DIAS (D_p)
    # =========================================================================
    pacientes_info = {}
    pacientes = []
    genero_paciente = {}
    dias_paciente = {}
    maior_dia_hospital = 0 # Usado para definir o tamanho do horizonte de dias

    with open(caminho_pacientes, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_id = row['id_paciente']
            pacientes.append(p_id)
            genero_paciente[p_id] = row['genero']
            
            # Converte a admissão e o LOS (Length of Stay) para o subconjunto de dias contínuos
            admissao = int(row['dia_admissao'])
            los = int(row['los'])
            
            # Gera a lista de dias corretamente ex: admissão=2, los=3 -> [3-5]
            dias_internacao = list(range(admissao, admissao + los))
            dias_paciente[p_id] = dias_internacao
            
            # Atualiza qual é o último dia que o hospital terá algum paciente
            if dias_internacao[-1] > maior_dia_hospital:
                maior_dia_hospital = dias_internacao[-1]
            
            pacientes_info[p_id] = {
                'especialidade_requerida': row['especialidade_requerida']
            }

    # O horizonte do hospital vai do dia 1 até o dia da última alta
    horizonte_dias = list(range(1, maior_dia_hospital + 1))

    # =========================================================================
    # 3. PESOS E MATRIZ DE CUSTO ESTÁTICO (C_pr)
    # =========================================================================
    pesos = {
        'W_transf': 100, 
        'W_gen': 500     
    }

    custo_estatico = {}
    PENALIDADE_ESPECIALIDADE = 50

    # Pré-calcula as inadequações para todos os pares (Paciente x Quarto)
    for p in pacientes:
        for r in quartos:
            custo = 0
            esp_paciente = pacientes_info[p]['especialidade_requerida']
            esp_quarto = quartos_info[r]['especialidade']
            
            if esp_paciente != esp_quarto:
                custo += PENALIDADE_ESPECIALIDADE
                
            custo_estatico[(p, r)] = custo

    return pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos


def gerar_cenario_teste():
    """
    Gera um cenário fixo (determinístico) para validação do modelo exato e heurístico.
    Retorna as estruturas de dados e a matriz de custo estático pré-calculada (C_{p,r}).
    """
    # 1. Definição dos Horizontes e Pesos (Seção 3.2.1 do TCC)
    horizonte_dias = list(range(1, 9)) # Horizonte de 7 dias (2 a 8)
    pesos = {
        'W_transf': 100, # Penalidade alta para evitar transferências
        'W_gen': 500     # Penalidade muito alta para evitar quartos mistos
    }

    # 2. Definição dos Quartos (Capacidades e Especialidades)
    quartos_info = {
        'R1': {'capacidade': 2, 'especialidade': 'Ortopedia'},
        'R2': {'capacidade': 2, 'especialidade': 'Cardiologia'},
        'R3': {'capacidade': 1, 'especialidade': 'Geral'}
    }
    quartos = list(quartos_info.keys())
    capacidade = {r: info['capacidade'] for r, info in quartos_info.items()}

    # 3. Definição dos Pacientes (D_p, Gênero e Especialidade Requerida)
    # pacientes_info = {
    #     'P1': {'genero': 'M', 'dias': list(range(2, 6)), 'especialidade': 'Ortopedia'},
    #     'P2': {'genero': 'F', 'dias': list(range(3, 7)), 'especialidade': 'Cardiologia'},
    #     'P3': {'genero': 'M', 'dias': list(range(2, 5)), 'especialidade': 'Geral'},
    #     'P4': {'genero': 'M', 'dias': list(range(5, 9)), 'especialidade': 'Cardiologia'}
    # }
    pacientes_info = {
        'P1': {'genero': 'M', 'dias': list(range(2, 6)), 'especialidade': 'Ortopedia'},
        'P2': {'genero': 'F', 'dias': list(range(3, 7)), 'especialidade': 'Cardiologia'},
        'P3': {'genero': 'M', 'dias': list(range(2, 5)), 'especialidade': 'Geral'},
        'P4': {'genero': 'M', 'dias': list(range(5, 9)), 'especialidade': 'Cardiologia'},
        'P5': {'genero': 'M', 'dias': list(range(4, 6)), 'especialidade': 'Ortopedia'},
        'P6': {'genero': 'F', 'dias': list(range(6, 8)), 'especialidade': 'Ortopedia'},

    }
    pacientes = list(pacientes_info.keys())
    genero_paciente = {p: info['genero'] for p, info in pacientes_info.items()}
    dias_paciente = {p: info['dias'] for p, info in pacientes_info.items()}

    # 4. PRÉ-CÁLCULO DA MATRIZ DE CUSTO ESTÁTICO C_{p,r}
    # Penaliza a alocação de um paciente em um quarto de especialidade inadequada
    custo_estatico = {}
    PENALIDADE_ESPECIALIDADE = 50 

    for p in pacientes:
        for r in quartos:
            custo = 0
            esp_paciente = pacientes_info[p]['especialidade']
            esp_quarto = quartos_info[r]['especialidade']
            
            if esp_paciente != esp_quarto:
                custo += PENALIDADE_ESPECIALIDADE
                
            custo_estatico[(p, r)] = custo

    return pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos



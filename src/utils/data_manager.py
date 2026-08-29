import csv
import os
import ast
import random

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
            los_float = random.lognormvariate(mu=1.55, sigma=0.35)  # média ~5, com cauda longa
            los = max(1, int(round(los_float)))
            
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
        'W_transf': 50, # Transferência de quarto
        'W_gen': 150,    # Mistura de gênero
        'W_spec': 100,    # Especialidade inadequada
        'W_cap': 250    # Capacidade estourada
    }

    custo_estatico = {}

    # Pré-calcula as inadequações para todos os pares (Paciente x Quarto)
    for p in pacientes:
        for r in quartos:
            custo = 0
            esp_paciente = ast.literal_eval(row['especialidade_requerida'])[0]
            esp_quarto = quartos_info[r]['especialidade']
            
            if esp_paciente != esp_quarto:
                custo += pesos['W_spec']
                
            custo_estatico[(p, r)] = custo

    return pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos


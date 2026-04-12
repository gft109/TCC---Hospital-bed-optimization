import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import random
import time
import copy
import statistics
import csv



from utils.data_manager import *
from utils.gurobi import resolver_modelo_exato

def main():
    print("Iniciando a Otimização de Leitos Hospitalares...")

    
    # 1. Carrega os dados
    # Dados dos CSVs
    pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos = carregar_instancia_csv("data")
    # Dados fixos de teste
    # pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos = gerar_cenario_teste()


    # 2. Roda o Solver Exato (Gurobi)
    # 2. Roda o Solver Exato (Gurobi)
    print("\n[Executando Modelo Exato PLI (Gurobi)...]")
    resultado_gurobi = resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    
    if resultado_gurobi['custo_objetivo'] is not None:
        print(f"\nCusto Ótimo Encontrado (Lower Bound): {resultado_gurobi['custo_objetivo']}")
        print("\nMatriz de Alocação (Paciente x Dia):")
        
        # 1. Imprime o Cabeçalho com os Dias
        cabecalho_dias = "".join([f" Dia {d:02d} |" for d in horizonte_dias])
        print(f"{'Paciente':<10} |{cabecalho_dias}")
        print("-" * (13 + 9 * len(horizonte_dias))) # Linha separadora
        
        # 2. Imprime as linhas da matriz para cada paciente
        for p in pacientes:
            linha_str = f"{p:<10} |"
            for d in horizonte_dias:
                # Verifica se o paciente tem um quarto alocado naquele dia
                if d in resultado_gurobi['matriz_alocacoes'][p]:
                    quarto = resultado_gurobi['matriz_alocacoes'][p][d]
                    linha_str += f" {quarto:<6} |"
                else:
                    # Se o paciente não está internado neste dia, imprime um traço
                    linha_str += f" {'-':<6} |"
            print(linha_str)
    else:
        print("Não foi possível encontrar uma solução viável.")
        
    # 3. AQUI NO FUTURO VOCÊ CHAMARÁ A SUA HEURÍSTICA:
    # resultado_heuristica = resolver_com_memetico(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    # print(f"Custo da Heuristica: {resultado_heuristica['custo']}")

if __name__ == "__main__":
    main()
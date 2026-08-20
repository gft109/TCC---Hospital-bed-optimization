import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import random
import time
import copy
import statistics
import csv

# Dados
from utils.data_manager import carregar_instancia_csv

# Algoritmos
from utils.gurobi import resolver_modelo_exato
from heuristics.memetic_solver import resolver_algoritmo_memetico

# Utilitários
from utils.gurobi_evaluator import converter_e_avaliar_gurobi
from utils.reporter import exibir_detalhamento_performance

def main():
    print("\n ------ SISTEMA DE OTIMIZAÇÃO DE ALOCAÇÃO DE LEITOS HOSPITALARES ------\n")
    
    # 1. Carrega os dados dos CSVs
    pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos = carregar_instancia_csv("data")
    
    # 2. Roda o Modelo Exato (Gurobi) para obter o Lower Bound de referência
    # (Para instâncias grandes: limitar o tempo do Gurobi ou usar apenas a heurística)
    gurobi_res = resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    # Prepara o detalhamento da solução do gurobi
    custos_gurobi = converter_e_avaliar_gurobi(gurobi_res, pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos)
    
    # 3. Roda a heurística (Algoritmo Memético - GA + VNS) 
    params = (pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos) # encapsula os parâmetros necessários para a heurística
    melhor_sol_heuristica = resolver_algoritmo_memetico(params, horizonte_dias, geracoes=20, tam_pop=30)
    
    # 4. Exibe a tabela de resultados
    exibir_detalhamento_performance(custos_gurobi, melhor_sol_heuristica.custo_detalhado, melhor_sol_heuristica.fitness)


if __name__ == "__main__":
    main()
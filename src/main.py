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


        # # Matrix quarto x dia
        # print("\nMatriz de Ocupação (Quarto x Dia):")
        # # Cria a estrutura invertida: Quarto -> Dia -> Lista de Pacientes
        # ocupacao_quarto = {q: {d: [] for d in horizonte_dias} for q in quartos}
        # # Preenche a nova estrutura com os dados do Gurobi
        # for p, dias_alocados in resultado_gurobi['matriz_alocacoes'].items():
        #     for d, q in dias_alocados.items():
        #         ocupacao_quarto[q][d].append(p)
        # tamanho_celula = 15 
        # cabecalho_dias = "".join([f" Dia {d:02d}".ljust(tamanho_celula) + "|" for d in horizonte_dias])
        # print(f"{'Quarto':<10} |{cabecalho_dias}")
        # print("-" * (13 + (tamanho_celula + 1) * len(horizonte_dias))) # Linha separadora dinâmica
        # # Imprime as linhas da matriz para cada quarto
        # for q in quartos:
        #     linha_str = f"{q:<10} |"
        #     for d in horizonte_dias:
        #         pacientes_no_quarto = ocupacao_quarto[q][d]
                
        #         # Verifica se há pacientes alocados naquele quarto e dia
        #         if pacientes_no_quarto:
        #             # Junta os nomes dos pacientes com vírgula (Ex: "P1, P5")
        #             str_pacientes = ", ".join(pacientes_no_quarto)
        #             linha_str += f" {str_pacientes}".ljust(tamanho_celula) + "|"
        #         else:
        #             # Se o quarto estiver vazio neste dia, imprime um traço
        #             linha_str += f" -".ljust(tamanho_celula) + "|"
        #     print(linha_str)
    else:
        print("Não foi possível encontrar uma solução viável.")
        


    # 3. CHAMAR A HEURÍSTICA AQUI:
    # resultado_heuristica = resolver_com_memetico(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    # print(f"Custo da Heuristica: {resultado_heuristica['custo']}")

if __name__ == "__main__":
    main()
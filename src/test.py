import sys
import os

# Dados
from utils.data_manager import carregar_instancia_csv

# Algoritmos
from utils.gurobi import resolver_modelo_exato
from heuristics.memetic_solver import resolver_algoritmo_memetico

# Utilitários
from utils.gurobi_evaluator import converter_e_avaliar_gurobi
from utils.reporter import exibir_detalhamento_performance

def main():
    # 1. Trata o argumento de entrada da instância via terminal
    # Valores aceitos: pequeno, medio, grande, muito_grande
    tipo_instancia = "pequeno"  # Valor padrão caso nada seja passado pelo terminal
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["pequeno", "medio", "grande", "muito_grande"]:
            tipo_instancia = arg
        else:
            print(f"Aviso: Instância '{arg}' não reconhecida. Usando padrão 'pequeno'.")
            print("Opções válidas: pequeno, medio, grande, muito_grande\n")

    # Mapeia o caminho da pasta de dados correspondente à instância selecionada
    caminho_dados = os.path.join("data", tipo_instancia)
    
    print("=" * 60)
    print(f"=== SISTEMA DE OTIMIZAÇÃO DE LEITOS HOSPITALARES ===")
    print(f"Executando cenário: {tipo_instancia.upper()}")
    print(f"Origem dos dados: {caminho_dados}")
    print("=" * 60)
    
    # 2. Verifica se a instância já foi gerada
    if not os.path.exists(caminho_dados):
        print(f"\n[ERRO] O diretório '{caminho_dados}' não existe.")
        print("Por favor, execute o gerador antes de testar:")
        print("  python src/utils/generate_all_instances.py")
        return

    # 3. Carrega os dados dos arquivos CSV do cenário específico
    pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos = carregar_instancia_csv(caminho_dados)
    params = (pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos)
    
    # 4. Executa o Modelo Exato (Gurobi)
    print("\n[Executando Modelo Exato (Gurobi)...]")
    gurobi_res = resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    
    # 5. Executa a heuristica (GA + VNS)
    # (Parâmetros calibrados: 80 gerações com população de 30)
    melhor_sol_heuristica = resolver_algoritmo_memetico(params, horizonte_dias, geracoes=30, tam_pop=30)
    
    # 6. Avalia a solução do Gurobi e padroniza para a comparação
    custos_gurobi = converter_e_avaliar_gurobi(
        gurobi_res, pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos
    )
    
    # 7. Exibe a tabela comparativa de resultados
    exibir_detalhamento_performance(
        custos_gurobi, melhor_sol_heuristica.custo_detalhado, melhor_sol_heuristica.fitness
    )

if __name__ == "__main__":
    main()
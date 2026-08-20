import sys
import os
import time

# Dados
from utils.data_manager import carregar_instancia_csv

# Algoritmos
from utils.gurobi import resolver_modelo_exato
from heuristics.memetic_solver import resolver_algoritmo_memetico

# Utilitários
from heuristics.representation import Solucao
from utils.gurobi_evaluator import converter_e_avaliar_gurobi
from utils.reporter import exibir_detalhamento_performance, exportar_detalhamento_csv

def main():
    # 1. Trata o argumento de entrada da instância via terminal
    # Valores aceitos: pequeno, medio, grande, muito_grande
    tipo_instancia = "pequeno"  # Valor default
    
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
    t_inicio_gurobi = time.time()
    gurobi_res = resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    tempo_gurobi = time.time() - t_inicio_gurobi
    # Adiciona as iterações nas respostas do Gurobi (caso ele tenha achado solução)
    if gurobi_res is not None and 'iteracoes' not in gurobi_res:
        # Acessa as iterações do Simplex diretamente se a execução ocorreu com sucesso
        gurobi_res['iteracoes'] = gurobi_res.get('iteracoes', 'N/A') # (Nota: certifique-se de que gurobi.py retorna model.IterCount na chave 'iteracoes')
    Solucao.reset_comparacoes() # reseta contador de iterações

    # 5. Executa a heuristica (GA + VNS)
    print("\n[Executando Algoritmo Memético (Heurística)...]")
    t_inicio_heuristica = time.time()
    melhor_sol_heuristica = resolver_algoritmo_memetico(params, horizonte_dias, geracoes=30, tam_pop=30)
    tempo_heuristica = time.time() - t_inicio_heuristica
    # Quantidade total de comparações feitas pela Heurística
    comparacoes_heuristica = Solucao.comparacoes_custo
    
    # 6. Avalia a solução do Gurobi e padroniza para a comparação
    custos_gurobi = converter_e_avaliar_gurobi(
        gurobi_res, tempo_gurobi, pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos
    )
    
    # 7. Exibe a tabela comparativa de resultados
    exibir_detalhamento_performance(
        custos_gurobi, melhor_sol_heuristica.custo_detalhado,
        melhor_sol_heuristica.fitness, tempo_heuristica, comparacoes_heuristica
    )

    # 8.  os resultados em um arquivo CSV na pasta "resultados"
    exportar_detalhamento_csv(
        custos_gurobi, melhor_sol_heuristica.custo_detalhado,
        melhor_sol_heuristica.fitness, tempo_heuristica, comparacoes_heuristica, tipo_instancia
    )

if __name__ == "__main__":
    main()
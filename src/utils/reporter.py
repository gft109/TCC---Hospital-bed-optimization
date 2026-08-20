# Exibição formatada dos resultados

def exibir_detalhamento_performance(custos_gurobi, custos_heuristica, fitness_heuristica):
    """
    Imprime a tabela de detalhamento comparativo entre o Gurobi e o Algoritmo Memético.
    Trata valores inexistentes (None) do Gurobi exibindo-os como 'NULL'.
    """
    print("\n" + "=" * 71)
    print(" " * 16 + "DETALHAMENTO DE PERFORMANCE (GUROBI VS HEURÍSTICA)")
    print("=" * 71)
    print(f"{'Métrica':<35} | {'Gurobi (Exato)':<14} | {'Memético (Heuristica)':<10}")
    print("-" * 71)
    
    # Função auxiliar para formatar valores numéricos ou NULL
    def formatar_valor(val):
        if val is None or val == 'NULL':
            return 'NULL'
        if isinstance(val, float):
            return f"{val:.1f}"
        return str(val)

    # Imprime cada linha comparativa puxando os dados dos dicionários
    print(f"{'Custo Clínico (Especialidades)':<35} | {formatar_valor(custos_gurobi.get('clinico')):<14} | {formatar_valor(custos_heuristica.get('clinico')):<10}")
    print(f"{'Penalidades por Transferência':<35} | {formatar_valor(custos_gurobi.get('transferencias')):<14} | {formatar_valor(custos_heuristica.get('transferencias')):<10}")
    print(f"{'Penalidades por Quarto Misto':<35} | {formatar_valor(custos_gurobi.get('genero')):<14} | {formatar_valor(custos_heuristica.get('genero')):<10}")
    print(f"{'Penalidades por Excesso de Leito':<35} | {formatar_valor(custos_gurobi.get('capacidade')):<14} | {formatar_valor(custos_heuristica.get('capacidade')):<10}")
    print("-" * 71)
    
    # Custo Total
    print(f"{'CUSTO TOTAL (FUNÇÃO OBJETIVO)':<35} | {formatar_valor(custos_gurobi.get('total')):<14} | {formatar_valor(fitness_heuristica):<10}")
    print("=" * 71)
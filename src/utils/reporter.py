# Exibição formatada dos resultados

import csv
import os

def exibir_detalhamento_performance(custos_gurobi, custos_heuristica, fitness_heuristica, tempo_heuristica, comparacoes_heuristica):
    """
    Imprime a tabela de detalhamento comparativo entre o Gurobi e o Algoritmo Memético.
    Trata valores inexistentes (None) do Gurobi exibindo-os como 'NULL'.
    """
    print("\n" + "=" * 72)
    print(" " * 16 + "DETALHAMENTO DE PERFORMANCE (GUROBI VS HEURÍSTICA)")
    print("=" * 72)
    print(f"{'Métrica':<35} | {'Gurobi (Exato)':<16} | {'Memético (Heuristica)':<10}")
    print("-" * 72)
    
    # Função auxiliar para formatar valores numéricos ou NULL
    def formatar_valor(val):
        if val is None or val == 'NULL':
            return 'NULL'
        if isinstance(val, float):
            return f"{val:.1f}"
        return str(val)
    
    def formatar_tempo(val):
        if val is None or val == 'NULL':
            return 'NULL'
        return f"{val:.4f} s"


    # Custos destrinchados
    print(f"{'Custo Clínico (Especialidades)':<35} | {formatar_valor(custos_gurobi.get('clinico')):<16} | {formatar_valor(custos_heuristica.get('clinico')):<10}")
    print(f"{'Penalidades por Transferência':<35} | {formatar_valor(custos_gurobi.get('transferencias')):<16} | {formatar_valor(custos_heuristica.get('transferencias')):<10}")
    print(f"{'Penalidades por Quarto Misto':<35} | {formatar_valor(custos_gurobi.get('genero')):<16} | {formatar_valor(custos_heuristica.get('genero')):<10}")
    print(f"{'Penalidades por Excesso de Leito':<35} | {formatar_valor(custos_gurobi.get('capacidade')):<16} | {formatar_valor(custos_heuristica.get('capacidade')):<10}")
    print("-" * 72)
    
    # Custo Total (F.O)
    print(f"{'CUSTO TOTAL (FUNÇÃO OBJETIVO)':<35} | {formatar_valor(custos_gurobi.get('total')):<16} | {formatar_valor(fitness_heuristica):<10}")
    print("=" * 72)

    # Performance Computacional
    print(f"{'Tempo de Processamento':<35} | {formatar_tempo(custos_gurobi.get('tempo')):<16} | {formatar_tempo(tempo_heuristica):<10}")
    print(f"{'Número de Comparações (Custo)':<35} | {formatar_valor(custos_gurobi.get('comparacoes')):<16} | {formatar_valor(comparacoes_heuristica):<10}")
    print("="*72)


def exportar_detalhamento_csv(custos_gurobi, custos_heuristica, fitness_heuristica, tempo_heuristica, comparacoes_heuristica, tipo_instancia, pasta_saida="resultados"):
    """
    Exporta a tabela de detalhamento comparativo (Gurobi vs Heurística) para um arquivo CSV.
    Cria a pasta de resultados automaticamente se ela não existir.
    """
    # Garante que a pasta de destino exista
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Define o nome do arquivo com base no cenário testado (ex: resultados/comparativo_pequeno.csv)
    caminho_arquivo = os.path.join(pasta_saida, f"comparativo_{tipo_instancia}.csv")
    
    # Função auxiliar para tratar nulos (NULL) de forma limpa no CSV
    def tratar_nulo(val):
        return "NULL" if val is None or val == "NULL" else val

    # Estrutura os dados exatamente como na tabela do terminal
    linhas = [
        ["Metrica / Tipo de Custo", "Gurobi (Exato)", "Memetico (Heuristica)"],
        ["Custo Clinico (Especialidades)", tratar_nulo(custos_gurobi.get('clinico')), tratar_nulo(custos_heuristica.get('clinico'))],
        ["Penalidades por Transferencia", tratar_nulo(custos_gurobi.get('transferencias')), tratar_nulo(custos_heuristica.get('transferencias'))],
        ["Penalidades por Quarto Misto", tratar_nulo(custos_gurobi.get('genero')), tratar_nulo(custos_heuristica.get('genero'))],
        ["Penalidades por Excesso de Leito", tratar_nulo(custos_gurobi.get('capacidade')), tratar_nulo(custos_heuristica.get('capacidade'))],
        ["CUSTO TOTAL (FUNCAO OBJETIVO)", tratar_nulo(custos_gurobi.get('total')), fitness_heuristica],
        ["Tempo de Processamento (s)", tratar_nulo(custos_gurobi.get('tempo')), f"{tempo_heuristica:.4f}"],
        ["Numero de Comparacoes (Custo)", tratar_nulo(custos_gurobi.get('comparacoes')), comparacoes_heuristica]
    ]
    
    # Escreve o arquivo de forma limpa
    try:
        with open(caminho_arquivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(linhas)
        print(f"\n[OK] Detalhamento exportado com sucesso para: {caminho_arquivo}")
    except Exception as e:
        print(f"\n[ERRO] Falha ao exportar arquivo CSV: {e}")
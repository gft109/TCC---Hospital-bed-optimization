# Roda os experimentos acadêmicos de comparação entre o Gurobi e a heurística memética (X rodadas independentes).

import sys
import os
import time
import csv
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.data_manager import carregar_instancia_csv
from utils.gurobi import resolver_modelo_exato
from heuristics.memetic_solver import resolver_algoritmo_memetico
from heuristics.representation import Solucao
from utils.gurobi_evaluator import converter_e_avaliar_gurobi

def safe_stdev(dados):
    """Calcula desvio padrão de forma segura contra listas curtas."""
    return statistics.stdev(dados) if len(dados) > 1 else 0.0

def formatar_valor(val):
    """Formata de forma genérica valores inteiros ou textuais."""
    if val is None or val == "NULL" or val == "N/A":
        return "NULL"
    if isinstance(val, float):
        return f"{val:.1f}"
    return str(val)

def formatar_float(val, precisao=4):
    """Formata floats com segurança. Evita quebras caso receba strings ou None."""
    if val is None or val == "NULL" or val == "N/A":
        return "NULL"
    try:
        return f"{float(val):.{precisao}f}"
    except (ValueError, TypeError):
        return str(val)

def main():
    # =========================================================================
    # 1. TRATAMENTO DOS ARGUMENTOS DO TERMINAL (Cenário, Repetições e Timeout)
    # =========================================================================
    tipo_instancia = "pequeno"  # Cenário padrão entre ("pequeno", "medio", "grande", "muito_grande")
    num_repeticoes = 5          # Valor padrão em unidades
    limite_tempo_heur = 60    # Valor padrão em segundos
    
    # Captura o primeiro argumento (cenário)
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ["pequeno", "medio", "grande", "muito_grande"]:
            tipo_instancia = arg1
        else:
            print(f"Aviso: Instância '{arg1}' não reconhecida. Usando padrão 'pequeno'.")
            print("Opções válidas: pequeno, medio, grande, muito_grande\n")
            
    # Captura o segundo argumento (número de repetições)
    if len(sys.argv) > 2:
        try:
            num_repeticoes = int(sys.argv[2])
            if num_repeticoes <= 0:
                print("Aviso: O número de repetições deve ser maior que 0. Usando padrão 5.\n")
                num_repeticoes = 5
        except ValueError:
            print(f"Aviso: '{sys.argv[2]}' não é um número válido para repetições. Usando padrão 5.\n")
            num_repeticoes = 5

    # Captura o terceiro argumento (limite de tempo por rodada da heurística)
    if len(sys.argv) > 3:
        try:
            limite_tempo_heur = float(sys.argv[3])
            if limite_tempo_heur <= 0:
                print("Aviso: O limite de tempo deve ser maior que 0. Usando padrão 'Sem limite'.\n")
                limite_tempo_heur = None
        except ValueError:
            print(f"Aviso: '{sys.argv[3]}' não é um limite de tempo válido. Usando padrão 'Sem limite'.\n")
            limite_tempo_heur = None

    caminho_dados = os.path.join("data", tipo_instancia)
    pasta_saida = os.path.join("resultados", tipo_instancia)
    os.makedirs(pasta_saida, exist_ok=True)

    print("=" * 72)
    print(f"=== INICIANDO AS SIMULAÇÕES ===")
    print(f"Instância selecionada: {tipo_instancia.upper()}")
    print(f"Repetições solicitadas: {num_repeticoes}")
    print(f"Limite de tempo heur.: {f'{limite_tempo_heur} s' if limite_tempo_heur else 'Sem limite'}")
    print(f"Diretório dos dados:   {caminho_dados}")
    print(f"Diretório de saída:    {pasta_saida}")
    print("=" * 72)

    if not os.path.exists(caminho_dados):
        print(f"[ERRO] A pasta '{caminho_dados}' não foi encontrada.")
        return

    # Carrega os dados
    pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos = carregar_instancia_csv(caminho_dados)
    params = (pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos)

    # 2. Executa o Gurobi uma única vez
    print("\n[1/2] Executando Modelo Exato (Gurobi) com limite de tempo...")
    t_inicio_gurobi = time.time()
    gurobi_res = resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos)
    tempo_gurobi = time.time() - t_inicio_gurobi

    custos_gurobi = converter_e_avaliar_gurobi(
        gurobi_res, tempo_gurobi, pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos
    )

    # Resultado
    gurobi_fit = custos_gurobi.get('total')
    gurobi_fit_str = f"{gurobi_fit:.1f}" if isinstance(gurobi_fit, float) else str(gurobi_fit)
    print(f"  > Gurobi concluído  | Fitness: {gurobi_fit_str:<7} | Tempo: {tempo_gurobi:.4f} s")


    # 3. Executa a Heurística Memética N vezes
    print(f"\n[2/2] Executando Algoritmo Memético ({num_repeticoes} rodadas independentes)...")
    
    historico_runs = []
    fitness_runs = []
    tempos_runs = []
    comparacoes_runs = []
    progressoes_runs = []
    
    for r in range(1, num_repeticoes + 1):
        Solucao.reset_comparacoes()
        t_inicio = time.time()
        
        melhor_sol, hist_progresso = resolver_algoritmo_memetico(
            params, horizonte_dias, geracoes=30, tam_pop=20, verbose=False, retornar_historico=True, limite_tempo=limite_tempo_heur
        )
        
        tempo_total = time.time() - t_inicio
        comparacoes = Solucao.comparacoes_custo
        
        run_data = {
            'rodada': r,
            'total': melhor_sol.fitness,
            'clinico': melhor_sol.custo_detalhado['clinico'],
            'transferencias': melhor_sol.custo_detalhado['transferencias'],
            'genero': melhor_sol.custo_detalhado['genero'],
            'capacidade': melhor_sol.custo_detalhado['capacidade'],
            'tempo': tempo_total,
            'comparacoes': comparacoes,
            'sol_objeto': melhor_sol
        }
        
        historico_runs.append(run_data)
        fitness_runs.append(melhor_sol.fitness)
        tempos_runs.append(tempo_total)
        comparacoes_runs.append(comparacoes)
        progressoes_runs.append(hist_progresso)
        
        print(f"  > Repetição {r:02d}/{num_repeticoes:02d} concluída | Fitness: {melhor_sol.fitness:<7} | Tempo: {tempo_total:.3f} s")

    # 4. Estatísticas de Melhor/Pior/Média
    melhor_run_idx = fitness_runs.index(min(fitness_runs))
    melhor_run_dados = historico_runs[melhor_run_idx]
    historico_melhor_progresso = progressoes_runs[melhor_run_idx]

    pior_run_idx = fitness_runs.index(max(fitness_runs))
    pior_run_dados = historico_runs[pior_run_idx]

    media_fit = statistics.mean(fitness_runs)
    desvio_fit = safe_stdev(fitness_runs)

    # Prepara strings formatadas da Heurística para exibição
    tempo_gurobi_str = formatar_float(custos_gurobi.get('tempo'), 4) + " s"
    tempo_heur_melhor_str = f"{melhor_run_dados['tempo']:.4f} s"
    tempo_heur_media_str = f"{statistics.mean(tempos_runs):.4f} s (±{safe_stdev(tempos_runs):.4f} s)"

    comp_gurobi_str = formatar_valor(custos_gurobi.get('comparacoes'))
    comp_heur_melhor_str = formatar_valor(melhor_run_dados['comparacoes'])
    comp_heur_media_str = f"{statistics.mean(comparacoes_runs):.1f} (±{safe_stdev(comparacoes_runs):.1f})"

    # Exibe consolidado no terminal
    print("\n" + "="*90)
    print(" " * 24 + "CONSOLIDADO EXPERIMENTAL (GUROBI VS HEURÍSTICA)")
    print("="*90)
    print(f"{'Métrica / Tipo de Custo':<32} | {'Gurobi':<14} | {'Heur. (Melhor)':<14} | {'Heur. (Média ± DP)':<22}")
    print("-" * 90)
    
    # Linhas de Custos
    print(f"{'Custo Clínico (Especialidades)':<32} | {formatar_valor(custos_gurobi.get('clinico')):<14} | {melhor_run_dados['clinico']:<14} | {statistics.mean([x['clinico'] for x in historico_runs]):.1f} (±{safe_stdev([x['clinico'] for x in historico_runs]):.1f})")
    print(f"{'Penalidades por Transferência':<32} | {formatar_valor(custos_gurobi.get('transferencias')):<14} | {melhor_run_dados['transferencias']:<14} | {statistics.mean([x['transferencias'] for x in historico_runs]):.1f} (±{safe_stdev([x['transferencias'] for x in historico_runs]):.1f})")
    print(f"{'Penalidades por Quarto Misto':<32} | {formatar_valor(custos_gurobi.get('genero')):<14} | {melhor_run_dados['genero']:<14} | {statistics.mean([x['genero'] for x in historico_runs]):.1f} (±{safe_stdev([x['genero'] for x in historico_runs]):.1f})")
    print(f"{'Penalidades por Excesso de Leito':<32} | {formatar_valor(custos_gurobi.get('capacidade')):<14} | {melhor_run_dados['capacidade']:<14} | {statistics.mean([x['capacidade'] for x in historico_runs]):.1f} (±{safe_stdev([x['capacidade'] for x in historico_runs]):.1f})")
    print("-" * 90)
    print(f"{'CUSTO TOTAL (FUNÇÃO OBJETIVO)':<32} | {formatar_valor(custos_gurobi.get('total')):<14} | {melhor_run_dados['total']:<14} | {media_fit:.1f} (±{desvio_fit:.1f})")
    print("-" * 90)
    print(f"{'Tempo de Processamento':<32} | {tempo_gurobi_str:<14} | {tempo_heur_melhor_str:<14} | {tempo_heur_media_str:<22}")
    print(f"{'Número de Comparações (Custo)':<32} | {comp_gurobi_str:<14} | {comp_heur_melhor_str:<14} | {comp_heur_media_str:<22}")
    print("="*90)

    # 4. Gravações dos arquivos CSV
    caminho_detalhado = os.path.join(pasta_saida, "experimentos_detalhado.csv")
    with open(caminho_detalhado, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Execucao", "Custo Total", "Clinico", "Transferencias", "Genero", "Capacidade", "Tempo (s)", "Comparacoes"])
        for run in historico_runs:
            writer.writerow([
                f"Heuristica_R{run['rodada']:02d}", run['total'], run['clinico'], 
                run['transferencias'], run['genero'], run['capacidade'], 
                f"{run['tempo']:.4f}", run['comparacoes']
            ])
        writer.writerow([
            "Gurobi_Exato", formatar_valor(custos_gurobi.get('total')), formatar_valor(custos_gurobi.get('clinico')),
            formatar_valor(custos_gurobi.get('transferencias')), formatar_valor(custos_gurobi.get('genero')),
            formatar_valor(custos_gurobi.get('capacidade')), formatar_float(custos_gurobi.get('tempo'), 4), 
            formatar_valor(custos_gurobi.get('comparacoes'))
        ])

    caminho_estatistico = os.path.join(pasta_saida, "comparativo_estatistico.csv")
    with open(caminho_estatistico, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Metrica", "Gurobi (Exato)", "Heuristica (Melhor)", "Heuristica (Media)", "Heuristica (Pior)", "Heuristica (Desvio Padrao)"])
        
        def obter_estats_subcusto(chave):
            valores = [x[chave] for x in historico_runs]
            return min(valores), statistics.mean(valores), max(valores), safe_stdev(valores)

        for metrica, chave in [("Custo Clinico", "clinico"), ("Penalidade Transferencia", "transferencias"), 
                               ("Penalidade Genero", "genero"), ("Penalidade Capacidade", "capacidade")]:
            min_v, med_v, max_v, std_v = obter_estats_subcusto(chave)
            writer.writerow([metrica, formatar_valor(custos_gurobi.get(chave)), melhor_run_dados[chave], f"{med_v:.2f}", pior_run_dados[chave], f"{std_v:.2f}"])
        
        writer.writerow(["CUSTO TOTAL", formatar_valor(custos_gurobi.get('total')), melhor_run_dados['total'], f"{media_fit:.2f}", pior_run_dados['total'], f"{desvio_fit:.2f}"])
        
        min_t, med_t, max_t, std_t = obter_estats_subcusto("tempo")
        writer.writerow(["Tempo de Execucao (s)", formatar_float(custos_gurobi.get('tempo'), 4), f"{melhor_run_dados['tempo']:.4f}", f"{med_t:.4f}", f"{pior_run_dados['tempo']:.4f}", f"{std_t:.4f}"])
        min_c, med_c, max_c, std_c = obter_estats_subcusto("comparacoes")
        writer.writerow(["Numero de Comparacoes", formatar_valor(custos_gurobi.get('comparacoes')), melhor_run_dados['comparacoes'], f"{med_c:.2f}", pior_run_dados['comparacoes'], f"{std_c:.2f}"])

    print(f"\n[OK] Arquivos CSV exportados com sucesso em '{pasta_saida}/'.")

    # =========================================================================
    # 5. GRÁFICOS (Matplotlib)
    # =========================================================================
    # Boxplot
    plt.figure(figsize=(6, 5))
    plt.boxplot(fitness_runs, patch_artist=True, 
                boxprops=dict(facecolor='#D3E2F2', color='#1F77B4'),
                capprops=dict(color='#1F77B4'),
                whiskerprops=dict(color='#1F77B4'),
                flierprops=dict(marker='o', markerfacecolor='red', markersize=6, linestyle='none'),
                medianprops=dict(color='darkblue', linewidth=2))
    
    plt.title(f'Distribuição dos Custos - Heurística ({tipo_instancia.upper()})\n({num_repeticoes} Execuções Independentes)', fontsize=12, fontweight='bold', pad=15)
    plt.ylabel('Custo Total (Fitness)', fontsize=10)
    plt.xticks([1], ['Algoritmo Memético'])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    caminho_boxplot = os.path.join(pasta_saida, "boxplot.png")
    plt.savefig(caminho_boxplot, dpi=150)
    plt.close()

    # Progresso da Convergência (Melhor Execução)
    plt.figure(figsize=(8, 4.5))
    plt.plot(historico_melhor_progresso, color='#1F77B4', linewidth=2.5, label='Evolução do Custo')
    
    plt.title(f'Progresso da Convergência (Melhor Execução) - {tipo_instancia.upper()}', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Geração', fontsize=10)
    plt.ylabel('Custo Total (Fitness)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.scatter(0, historico_melhor_progresso[0], color='red', s=50, zorder=5, label=f'Inicial: {historico_melhor_progresso[0]}')
    plt.scatter(len(historico_melhor_progresso)-1, historico_melhor_progresso[-1], color='green', s=50, zorder=5, label=f'Final: {historico_melhor_progresso[-1]}')
    
    plt.legend(frameon=True, facecolor='white', edgecolor='none')
    plt.tight_layout()
    
    caminho_conv = os.path.join(pasta_saida, "convergencia.png")
    plt.savefig(caminho_conv, dpi=150)
    plt.close()

    print(f"[OK] Gráficos exportados com sucesso em '{pasta_saida}/':")
    print(f"  - boxplot.png")
    print(f"  - convergencia.png")

if __name__ == "__main__":
    main()
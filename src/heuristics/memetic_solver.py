# Algoritmo Memético (GA + VNS)

import random
import time 

from heuristics.genetic import GeneticAlgorithm
from heuristics.local_search import VNS
from heuristics.representation import Solucao

def resolver_algoritmo_memetico(params_problema, horizonte_dias, geracoes=80, tam_pop=30, taxa_busca_local=0.20, verbose=True, retornar_historico=False, limite_tempo=None):
    """
    Resolve o PBA usando um Algoritmo Memético com controle de diversidade (GA + VNS)
    para evitar a convergência prematura em mínimos locais.
    """
    if verbose:
        print("\nIniciando busca pelo Algoritmo Memético (GA + VNS)...")
    
    t_inicio_heuristica = time.time()  # tempo de inicio da rodada

    # Inicializa o GA
    ga = GeneticAlgorithm(params_problema, tamanho_populacao=tam_pop)
    ga.criar_populacao_inicial(horizonte_dias)
    
    # Inicializa o VNS
    vns = VNS(ga.populacao)
    
    # Ordena e captura o melhor inicial de forma segura
    ga.populacao.sort(key=lambda s: s.fitness)
    melhor_global = ga.populacao[0].clonar()
    
    if verbose:
        print(f"Geração 00 | Custo Inicial: {melhor_global.fitness}")

    # Histórico de convergência
    historico_fitness = [melhor_global.fitness]

    geracoes_sem_melhora = 0
    
    for g in range(1, geracoes + 1):
        # Limite de Tempo
        if limite_tempo is not None:
            tempo_decorrido = time.time() - t_inicio_heuristica
            if tempo_decorrido >= limite_tempo:
                if verbose:
                    print(f"\n[Aviso] Limite de tempo de {limite_tempo}s atingido na geração {g}. Interrompendo busca...")
                break

        nova_geracao = []
        
        # Elitismo: preserva o melhor global e o segundo melhor
        nova_geracao.append(melhor_global.clonar())
        if len(ga.populacao) > 1:
            nova_geracao.append(ga.populacao[1].clonar())
            
        # Rastreia os valores de fitness para evitar clones na população
        fitness_existentes = {ind.fitness for ind in nova_geracao}
        
        while len(nova_geracao) < ga.tamanho_populacao:
            # 1. Seleção por Torneio
            pai1 = ga.selecao_torneio()
            pai2 = ga.selecao_torneio()
            
            # 2. Crossover (Recombinação)
            if random.random() < ga.taxa_crossover:
                filho1, filho2 = ga.crossover_uniforme(pai1, pai2)
            else:
                filho1, filho2 = pai1.clonar(), pai2.clonar()
                
            # 3. Mutação Padrão
            ga.mutar(filho1)
            ga.mutar(filho2)
            
            # 4. HIBRIDIZAÇÃO SELETIVA: VNS roda com probabilidade (Evita homogeneidade)
            if random.random() < taxa_busca_local:
                filho1 = vns.buscar(filho1, max_iter=15)
            if random.random() < taxa_busca_local:
                filho2 = vns.buscar(filho2, max_iter=15)
            
            # 5. FILTRO DE CLONES: Evita inserir soluções idênticas
            for f in [filho1, filho2]:
                if len(nova_geracao) < ga.tamanho_populacao:
                    if f.fitness in fitness_existentes:
                        ga.mutar(f)
                        ga.mutar(f)
                        f.avaliar()
                    nova_geracao.append(f)
                    fitness_existentes.add(f.fitness)
                    
        # Atualiza a população com a nova geração diversificada
        ga.populacao = nova_geracao
        ga.populacao.sort(key=lambda s: s.fitness)
        
        # Verifica se houve melhora real do recorde global
        if ga.populacao[0].fitness < melhor_global.fitness:
            melhor_global = ga.populacao[0].clonar()
            geracoes_sem_melhora = 0
        else:
            geracoes_sem_melhora += 1
            
        # 6. MECANISMO DE RESTART (Recuperação de Estagnação)
        if geracoes_sem_melhora >= 10:
            ponto_corte = int(ga.tamanho_populacao * 0.6)
            for i in range(ponto_corte, ga.tamanho_populacao):
                nova_sol = Solucao(*ga.params)
                nova_sol.inicializar_aleatorio(horizonte_dias)
                nova_sol = vns.buscar(nova_sol, max_iter=5)
                ga.populacao[i] = nova_sol
                
            ga.populacao.sort(key=lambda s: s.fitness)
            geracoes_sem_melhora = 0
            
        if verbose:
            print(f"Geração {g:02d} | Melhor Custo Atual: {melhor_global.fitness}")
        
        # Armazena a evolução do melhor fitness da geração
        historico_fitness.append(melhor_global.fitness)
        
    if retornar_historico:
        return melhor_global, historico_fitness
    return melhor_global
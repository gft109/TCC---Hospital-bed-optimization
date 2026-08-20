# Operadores do GA - Algoritmo Genético - (Crossover, Mutação, Seleção)

import random
from heuristics.representation import Solucao

class GeneticAlgorithm:
    def __init__(self, params_problema, tamanho_populacao=20, taxa_crossover=0.8, taxa_mutacao=0.1):
        self.params = params_problema # Dicionário com dados do hospital
        self.tamanho_populacao = tamanho_populacao
        self.taxa_crossover = taxa_crossover
        self.taxa_mutacao = taxa_mutacao
        self.populacao = []

    def criar_populacao_inicial(self, horizonte_dias):
        self.populacao = []
        for _ in range(self.tamanho_populacao):
            sol = Solucao(*self.params)
            sol.inicializar_aleatorio(horizonte_dias)
            self.populacao.append(sol)

    def selecao_torneio(self, k=2):
        """Seleciona o melhor indivíduo entre k sorteados aleatoriamente (Seção 3.3.1 de Talbi)."""
        competidores = random.sample(self.populacao, k)
        competidores.sort(key=lambda s: s.fitness)
        return competidores[0]

    def crossover_uniforme(self, pai1, pai2):
        """Cruza duas soluções trocando a alocação completa de pacientes específicos (Seção 3.3.2)."""
        filho1 = pai1.clonar()
        filho2 = pai2.clonar()
        
        for p in pai1.pacientes:
            # Chance de 50% de herdar a agenda do pai1 ou pai2 para cada paciente
            if random.random() < 0.5:
                filho1.alocacao[p] = pai2.alocacao[p].copy()
                filho2.alocacao[p] = pai1.alocacao[p].copy()
                
        filho1.avaliar()
        child_fitness = filho2.avaliar()
        return filho1, filho2

    def mutar(self, solucao):
        """Mutação pontual: altera o quarto de um paciente em um único dia."""
        if random.random() < self.taxa_mutacao:
            p = random.choice(solucao.pacientes)
            d = random.choice(solucao.dias_paciente[p])
            novo_quarto = random.choice(solucao.quartos)
            solucao.alocacao[p][d] = novo_quarto
            solucao.avaliar()
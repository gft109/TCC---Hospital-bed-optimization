# Classe Solucao e o Avaliador de Fitness

import random

class Solucao:
    def __init__(self, pacientes, quartos, dias_paciente, genero_paciente, capacidade_quartos, custo_estatico, pesos):
        self.pacientes = pacientes
        self.quartos = quartos
        self.dias_paciente = dias_paciente
        self.genero_paciente = genero_paciente
        self.capacidade_quartos = capacidade_quartos
        self.custo_estatico = custo_estatico
        self.pesos = pesos
        
        # Representação do Cromossomo: dicionário {paciente: {dia: quarto}}
        self.alocacao = {}
        self.fitness = float('inf')
        
    def inicializar_aleatorio(self, horizonte_dias):
        """Gera uma solução inicial de forma inteligente"""
        for p in self.pacientes:
            self.alocacao[p] = {}
            
            # Filtra quartos que possuem custo clínico ZERO para o paciente p
            quartos_ideais = [r for r in self.quartos if self.custo_estatico.get((p, r), 0) == 0]
            
            # Tenta alocar em um quarto ideal, senão pega qualquer quarto disponível
            if quartos_ideais:
                quarto_escolhido = random.choice(quartos_ideais)
            else:
                quarto_escolhido = random.choice(self.quartos)
                
            for d in self.dias_paciente[p]:
                self.alocacao[p][d] = quarto_escolhido
        self.avaliar()

    def avaliar(self):
        """Calcula as penalidades e o custo total da solução (Função Objetivo do TCC)."""
        custo_clinico = 0
        custo_transferencias = 0
        custo_genero = 0
        custo_capacidade = 0 # Soft constraint de capacidade para a heurística
        
        # Rastreamento diário para capacidade e gênero
        # ocupacao_diaria[quarto][dia] = list de pacientes
        ocupacao_diaria = {q: {d: [] for d in range(1, 35)} for q in self.quartos}
        
        for p, agenda in self.alocacao.items():
            dias_internado = sorted(list(agenda.keys()))
            
            # 1. Custo Clínico (Especialidade Inadequada)
            for d, r in agenda.items():
                custo_clinico += self.custo_estatico.get((p, r), 0)
                ocupacao_diaria[r][d].append(p)
                
            # 2. Custo de Transferências (Mudar de quarto entre dias consecutivos)
            for idx in range(len(dias_internado) - 1):
                dia_atual = dias_internado[idx]
                dia_seguinte = dias_internado[idx+1]
                if agenda[dia_atual] != agenda[dia_seguinte]:
                    custo_transferencias += self.pesos['W_transf']

        # 3. Avaliação de Gênero Dinâmico e Capacidade nos Quartos por Dia
        for r in self.quartos:
            for d in range(1, 35):
                pacientes_no_quarto = ocupacao_diaria[r][d]
                num_pacientes = len(pacientes_no_quarto)
                
                if num_pacientes > 0:
                    # Verifica Capacidade Estourada
                    if num_pacientes > self.capacidade_quartos[r]:
                        # Penalidade pesada por cada leito excedido (Ex: 1000 por leito extra)
                        custo_capacidade += (num_pacientes - self.capacidade_quartos[r]) * 3000
                    
                    # Verifica Mistura de Gênero
                    generos = [self.genero_paciente[p] for p in pacientes_no_quarto]
                    if len(set(generos)) > 1: # Se houver 'M' e 'F' no mesmo dia/quarto
                        custo_genero += self.pesos['W_gen']

        # Dicionario de detalhamento dos custos da solução
        self.custo_detalhado = {
            'clinico': custo_clinico,
            'transferencias': custo_transferencias,
            'genero': custo_genero,
            'capacidade': custo_capacidade
        }
        # Fitness é a soma de todos os custos (Queremos MINIMIZAR)
        self.fitness = custo_clinico + custo_transferencias + custo_genero + custo_capacidade
        return self.fitness

    def clonar(self):
        """Cria uma cópia idêntica da solução para testes de vizinhança."""
        clone = Solucao(self.pacientes, self.quartos, self.dias_paciente, self.genero_paciente, 
                        self.capacidade_quartos, self.custo_estatico, self.pesos)
        clone.alocacao = {p: agenda.copy() for p, agenda in self.alocacao.items()}
        clone.fitness = self.fitness

        # Copia o dicionário de detalhamento dos custos da solução, se existir
        if hasattr(self, 'custo_detalhado'):
            clone.custo_detalhado = self.custo_detalhado.copy()

        return clone
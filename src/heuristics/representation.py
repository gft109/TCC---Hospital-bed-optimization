# Classe Solucao e o Avaliador de Fitness

import random

class Solucao:
    comparacoes_custo = 0 # contador de comparações de fitness para análise de desempenho

    @classmethod
    def reset_comparacoes(cls):
        """Reseta o contador de comparações para iniciar uma nova rodada do zero."""
        cls.comparacoes_custo = 0

    @property
    def chave_ordenacao(self):
        """
        Chave de comparação lexicográfica: soluções que violam a capacidade dos
        quartos são sempre consideradas piores que qualquer solução viável,
        independentemente da magnitude das demais penalidades. Entre soluções
        com o mesmo nível de violação, desempata pelo fitness normal.
        """
        violacao_capacidade = self.custo_detalhado.get('capacidade', 0)
        return (violacao_capacidade, self.fitness)

    def __init__(self, pacientes, quartos, dias_paciente, genero_paciente, capacidade_quartos, custo_estatico, pesos):
        self.pacientes = pacientes
        self.quartos = quartos
        self.dias_paciente = dias_paciente
        self.genero_paciente = genero_paciente
        self.capacidade_quartos = capacidade_quartos
        self.custo_estatico = custo_estatico
        self.pesos = pesos

         # Deriva o horizonte de dias diretamente dos dados
        if dias_paciente:
            self.horizonte_dias = max(d for dias in dias_paciente.values() for d in dias)
        else:
            self.horizonte_dias = 0
        
        # Representação do Cromossomo: dicionário {paciente: {dia: quarto}}
        self.alocacao = {}
        self.fitness = float('inf')
        
    def inicializar_aleatorio(self, horizonte_dias):
        """
        Gera a solução inicial de forma construtiva (gulosa-aleatorizada),
        respeitando a capacidade dos quartos sempre que possível, para evitar
        que a solução inicial carregue violações artificiais que não refletem
        a dificuldade real do problema.
        """
        # Ocupação diária por quarto, usada só durante a construção
        ocupacao = {r: {d: 0 for d in range(1, self.horizonte_dias + 1)} for r in self.quartos}

        # Embaralha a ordem dos pacientes a cada indivíduo, para manter diversidade na população
        ordem_pacientes = self.pacientes.copy()
        random.shuffle(ordem_pacientes)

        for p in ordem_pacientes:
            dias_p = self.dias_paciente[p]

            # 1. Prioriza quartos da especialidade correta que tenham vaga em TODOS os dias da estadia
            quartos_ideais = [r for r in self.quartos if self.custo_estatico.get((p, r), 0) == 0]
            candidatos = [
                r for r in quartos_ideais
                if all(ocupacao[r][d] < self.capacidade_quartos[r] for d in dias_p)
            ]

            # 2. Se não há quarto ideal com vaga, aceita qualquer quarto com vaga
            if not candidatos:
                candidatos = [
                    r for r in self.quartos
                    if all(ocupacao[r][d] < self.capacidade_quartos[r] for d in dias_p)
                ]

            # 3. Último recurso: nenhum quarto comporta sem estourar capacidade
            #    (permanece possível, e a violação é penalizada normalmente na avaliação)
            if not candidatos:
                candidatos = self.quartos

            quarto_escolhido = random.choice(candidatos)

            self.alocacao[p] = {}
            for d in dias_p:
                self.alocacao[p][d] = quarto_escolhido
                ocupacao[quarto_escolhido][d] += 1

        self.avaliar()

    def avaliar(self):
        """Calcula as penalidades e o custo total da solução (Função Objetivo do TCC)."""
        Solucao.comparacoes_custo += 1 
        custo_clinico = 0
        custo_transferencias = 0
        custo_genero = 0
        custo_capacidade = 0 
        
        # Rastreamento diário para capacidade e gênero
        ocupacao_diaria = {q: {d: [] for d in range(1, self.horizonte_dias + 1)} for q in self.quartos}

        
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
            for d in range(1, self.horizonte_dias + 1):
                pacientes_no_quarto = ocupacao_diaria[r][d]
                num_pacientes = len(pacientes_no_quarto)
                
                if num_pacientes > 0:
                    # Verifica Capacidade Estourada
                    if num_pacientes > self.capacidade_quartos[r]:
                        # Penalidade pesada por cada leito excedido
                        custo_capacidade += (num_pacientes - self.capacidade_quartos[r]) * self.pesos.get('W_cap')
                    
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
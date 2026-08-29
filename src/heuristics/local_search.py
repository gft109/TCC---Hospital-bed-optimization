# Algoritmo VNS ( Variable Neighborhood Search) e suas estruturas de vizinhança (Change room e Swap patients)

import random

class VNS:
    def __init__(self, solucao_base):
        self.solucao_base = solucao_base

    def vizinhanca_change_room(self, solucao, tentativas=60):
        """
        N1: Mudar Quarto (Change Room) - First Improvement.
        Transfere o paciente de quarto para toda a estadia.
        """
        for _ in range(tentativas):
            nova_sol = solucao.clonar()
            p = random.choice(nova_sol.pacientes)
            
            # Prioriza quartos ideais (especialidade correta) na maior parte das tentativas,
            # mas mantém exploração aleatória em parte delas para não perder diversidade
            quartos_ideais = [r for r in nova_sol.quartos if nova_sol.custo_estatico.get((p, r), 0) == 0]
            if quartos_ideais and random.random() < 0.7:
                novo_quarto = random.choice(quartos_ideais)
            else:
                novo_quarto = random.choice(nova_sol.quartos)
            
            # Evita trabalho se o quarto sorteado já for o atual
            dias_p = nova_sol.dias_paciente[p]
            if all(nova_sol.alocacao[p][d] == novo_quarto for d in dias_p):
                continue
                
            for d in dias_p:
                nova_sol.alocacao[p][d] = novo_quarto
                
            nova_sol.avaliar()
            if nova_sol.chave_ordenacao < solucao.chave_ordenacao:
                return nova_sol # Aceita a primeira melhora encontrada
                
        return solucao

    def vizinhanca_swap_patients(self, solucao, tentativas=60):
        """
        N2: Troca entre Pacientes (Swap Patients) - First Improvement.
        Permuta os quartos de dois pacientes que possuem interseção de dias.
        """
        for _ in range(tentativas):
            nova_sol = solucao.clonar()
            p1, p2 = random.sample(nova_sol.pacientes, 2)
            
            dias_comuns = set(nova_sol.dias_paciente[p1]).intersection(set(nova_sol.dias_paciente[p2]))
            if not dias_comuns:
                continue
                
            # Evita trocar se já estão no mesmo quarto
            if all(nova_sol.alocacao[p1][d] == nova_sol.alocacao[p2][d] for d in dias_comuns):
                continue
                
            for d in dias_comuns:
                quarto_p1 = nova_sol.alocacao[p1][d]
                quarto_p2 = nova_sol.alocacao[p2][d]
                nova_sol.alocacao[p1][d] = quarto_p2
                nova_sol.alocacao[p2][d] = quarto_p1
                
            nova_sol.avaliar()
            if nova_sol.chave_ordenacao < solucao.chave_ordenacao:
                return nova_sol # Aceita a primeira melhora encontrada
                
        return solucao

    def vizinhanca_partial_change_room(self, solucao, tentativas=60):
        """
        N3: Mudança Parcial de Quarto (PCR) - First Improvement.
        Seleciona um dia de corte e altera o quarto do paciente a partir dele (ou antes dele),
        introduzindo uma transferência controlada para liberar leitos nos dias de pico.
        """
        for _ in range(tentativas):
            nova_sol = solucao.clonar()
            p = random.choice(nova_sol.pacientes)
            dias_p = sorted(nova_sol.dias_paciente[p])
            
            # Pacientes com apenas 1 dia não podem sofrer transferência parcial
            if len(dias_p) <= 1:
                continue
                
            # Seleciona um dia de corte (split) a partir do segundo dia de internação
            dia_corte = random.choice(dias_p[1:])
            novo_quarto = random.choice(nova_sol.quartos)
            
            # Sorteia se vamos alterar os dias anteriores ao corte (Head) ou posteriores (Tail)
            mudar_cauda = random.choice([True, False])
            
            for d in dias_p:
                if mudar_cauda:
                    if d >= dia_corte:
                        nova_sol.alocacao[p][d] = novo_quarto
                else:
                    if d < dia_corte:
                        nova_sol.alocacao[p][d] = novo_quarto
                        
            nova_sol.avaliar()
            if nova_sol.chave_ordenacao < solucao.chave_ordenacao:
                return nova_sol # Aceita a primeira melhora encontrada
                
        return solucao

    def buscar(self, solucao, max_iter=50):
        """
        Laço principal do VNS alternando sequencialmente entre as 3 vizinhanças:
        N1 (Change Room) -> N2 (Swap Patients) -> N3 (Partial Change Room).
        """
        melhor_sol = solucao.clonar()
        
        for _ in range(max_iter):
            k = 1
            while k <= 3: # Explora as 3 estruturas de vizinhança sucessivamente!
                if k == 1:
                    candidata = self.vizinhanca_change_room(melhor_sol)
                elif k == 2:
                    candidata = self.vizinhanca_swap_patients(melhor_sol)
                else:
                    candidata = self.vizinhanca_partial_change_room(melhor_sol)
                
                # Se encontrou melhora, aceita e reinicia na vizinhança mais simples
                if candidata.chave_ordenacao < melhor_sol.chave_ordenacao:
                    melhor_sol = candidata
                    k = 1
                else:
                    k += 1 # Se não melhorou, passa para a próxima vizinhança do VNS
                    
        return melhor_sol

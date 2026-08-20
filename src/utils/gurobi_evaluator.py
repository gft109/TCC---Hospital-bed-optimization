# Converte a saída do gurobi no padrão desejado para comparação

from heuristics.representation import Solucao

def converter_e_avaliar_gurobi(gurobi_res, tempo_exec, pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos):
    """
    Tenta converter a saída do Gurobi em um objeto Solucao e calcula os custos.
    Se o Gurobi falhar ou não achar solução viável, retorna um dicionário com valores None.
    """
    # Se o Gurobi não encontrou solução viável
    if gurobi_res is None or gurobi_res.get('custo_objetivo') is None:
        return {
            'clinico': None,
            'transferencias': None,
            'genero': None,
            'capacidade': None,
            'total': None,
            'tempo': tempo_exec,
            'comparacoes': 'NULL'
        }
    
    # Se houver solução, cria um objeto Solucao temporário para avaliação uniforme
    sol_gurobi = Solucao(
        pacientes, quartos, dias_paciente, genero_paciente, capacidade, custo_estatico, pesos
    )
    # Injeta as alocações encontradas
    sol_gurobi.alocacao = gurobi_res['matriz_alocacoes']
    # Roda a função de avaliação - padroniza os custos
    Solucao.reset_comparacoes()
    sol_gurobi.avaliar()
    Solucao.reset_comparacoes() 

    
    # Retorna uma cópia dos custos detalhados com o total incluído
    resultado_custos = sol_gurobi.custo_detalhado.copy()
    resultado_custos['total'] = sol_gurobi.fitness
    resultado_custos['tempo'] = tempo_exec

    # Iterações do simplex
    resultado_custos['comparacoes'] = gurobi_res.get('iteracoes', 'N/A')

    return resultado_custos
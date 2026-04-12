import gurobipy as gp
from gurobipy import GRB

def resolver_modelo_exato(pacientes, genero_paciente, dias_paciente, quartos, capacidade, horizonte_dias, custo_estatico, pesos):
    """
    Traduz e resolve o Problema de Alocação de Leitos (PBA) usando PLI.
    Reflete rigorosamente as Equações da Seção 3.2 do TCC.
    """
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0) # Desativa a saída detalhada do Gurobi
    env.start()
    model = gp.Model("PBA_Exato_PLI", env=env)
    
    # =========================================================================
    # VARIÁVEIS DE DECISÃO (Equações 3.1 a 3.5 do TCC)
    # =========================================================================
    x = {} # Variável principal de alocação x_{p,r,d}
    t = {} # Variável de transferência t_{p,r,d}
    
    for p in pacientes:
        for r in quartos:
            for d in dias_paciente[p]: # Apenas os dias em que p está internado (D_p)
                x[p, r, d] = model.addVar(vtype=GRB.BINARY, name=f"x_{p}_{r}_{d}")
                t[p, r, d] = model.addVar(vtype=GRB.BINARY, name=f"t_{p}_{r}_{d}")
                
    f = model.addVars(quartos, horizonte_dias, vtype=GRB.BINARY, name="f")
    m = model.addVars(quartos, horizonte_dias, vtype=GRB.BINARY, name="m")
    b = model.addVars(quartos, horizonte_dias, vtype=GRB.BINARY, name="b")
    
    # =========================================================================
    # FUNÇÃO OBJETIVO (Equação 3.6 do TCC)
    # =========================================================================
    custos_clinicos = gp.quicksum(custo_estatico[p, r] * x[p, r, d] 
                                  for p in pacientes for r in quartos for d in dias_paciente[p])
    
    penalidade_transf = gp.quicksum(pesos['W_transf'] * t[p, r, d] 
                                    for p in pacientes for r in quartos for d in dias_paciente[p])
    
    penalidade_genero = gp.quicksum(pesos['W_gen'] * b[r, d] 
                                    for r in quartos for d in horizonte_dias)
    
    model.setObjective(custos_clinicos + penalidade_transf + penalidade_genero, GRB.MINIMIZE)
    
    # =========================================================================
    # RESTRIÇÕES (Equações 3.7 a 3.12 do TCC)
    # =========================================================================
    
    # 1. Atribuição Única e Contínua (Eq 3.7)
    for p in pacientes:
        for d in dias_paciente[p]:
            model.addConstr(gp.quicksum(x[p, r, d] for r in quartos) == 1, name=f"GarantiaIntern_{p}_{d}")
            
    # 2. Limite de Capacidade do Quarto (Eq 3.8)
    for r in quartos:
        for d in horizonte_dias:
            pacientes_no_dia = [p for p in pacientes if d in dias_paciente[p]]
            model.addConstr(gp.quicksum(x[p, r, d] for p in pacientes_no_dia) <= capacidade[r], name=f"Capac_{r}_{d}")

    # 3. Rastreamento de Transferências (Eq 3.9)
    for p in pacientes:
        dias_p = sorted(dias_paciente[p])
        for i in range(len(dias_p) - 1): # Exclui o dia da alta
            d_atual = dias_p[i]
            d_prox = dias_p[i+1]
            for r in quartos:
                model.addConstr(t[p, r, d_atual] >= x[p, r, d_atual] - x[p, r, d_prox], name=f"Transf_{p}_{r}_{d_atual}")
                
    # 4 e 5. Identificação de Presença Feminina/Masculina (Eq 3.10 e 3.11)
    for r in quartos:
        for d in horizonte_dias:
            pacientes_no_dia = [p for p in pacientes if d in dias_paciente[p]]
            for p in pacientes_no_dia:
                if genero_paciente[p] == 'F':
                    model.addConstr(f[r, d] >= x[p, r, d], name=f"Fem_{r}_{d}_{p}")
                elif genero_paciente[p] == 'M':
                    model.addConstr(m[r, d] >= x[p, r, d], name=f"Masc_{r}_{d}_{p}")

    # 6. Detecção de Mistura de Gêneros (Quarto Misto) (Eq 3.12)
    for r in quartos:
        for d in horizonte_dias:
            model.addConstr(b[r, d] >= m[r, d] + f[r, d] - 1, name=f"Misto_{r}_{d}")
            
    # =========================================================================
    # OTIMIZAÇÃO E RESULTADOS
    # =========================================================================
    model.setParam('TimeLimit', 300) # Limite de 5 minutos
    model.optimize()

    resultado = {
        "status": model.status,
        "custo_objetivo": None,
        "matriz_alocacoes": {} # <-- Alterado para um dicionário (matriz)
    }
    
    if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:
        resultado["custo_objetivo"] = model.objVal
        
        # Inicializa as "linhas" da matriz para cada paciente
        for p in pacientes:
            resultado["matriz_alocacoes"][p] = {}
            
        # Percorre as variáveis e preenche a matriz
        for p in pacientes:
            for d in dias_paciente[p]:
                for r in quartos:
                    if x[p, r, d].X > 0.5: # Se o Gurobi alocou (valor 1)
                        # Salva o quarto na posição [paciente][dia] da matriz
                        resultado["matriz_alocacoes"][p][d] = r
                            
    return resultado
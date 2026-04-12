import csv
import random
import os

def gerar_dados_hospitalares(num_quartos=5, num_pacientes=40, horizonte_planejamento=6, diretorio_saida="data"):
    """
    Gera dados garantindo:
    1. A capacidade diária nunca é ultrapassada.
    2. A internação (Admissão + LOS) termina dentro do horizonte_planejamento.
    3. Todos os pacientes são alocados (ou o máximo possível dentro do limite físico).
    """
    os.makedirs(diretorio_saida, exist_ok=True)
    especialidades = ['Ortopedia', 'Cardiologia', 'Geral', 'Neurologia', 'Pediatria']

    # 1. DEFINIÇÃO DOS QUARTOS E CAPACIDADE
    caminho_quartos = os.path.join(diretorio_saida, 'room.csv')
    capacidade_total_por_dia = 0  
    
    with open(caminho_quartos, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_quarto', 'capacidade', 'especialidade', 'politica_genero'])
        for i in range(1, num_quartos + 1):
            cap = 2 # Fixado em 2 para manter consistência com seu exemplo
            capacidade_total_por_dia += cap
            writer.writerow([f"R{i}", cap, random.choice(especialidades), 'D'])

    # 2. GERAÇÃO DE PACIENTES COM TRAVA ESTALCIONÁRIA
    caminho_pacientes = os.path.join(diretorio_saida, 'patient.csv')
    
    # Ocupação restrita estritamente ao horizonte (ex: 1 a 6)
    ocupacao_diaria = {d: 0 for d in range(1, horizonte_planejamento + 1)}
    
    pacientes_gerados = 0
    
    with open(caminho_pacientes, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id_paciente', 'genero', 'idade', 'dia_admissao', 'los', 'especialidade_requerida'])
        
        # Tentamos gerar até atingir o num_pacientes
        tentativa_paciente = 1
        while pacientes_gerados < num_pacientes and tentativa_paciente <= num_pacientes:
            # Sorteia um LOS (mínimo 1)
            los = max(1, int(round(random.gauss(3.0, 1.0)))) 
            
            # FILTRO CRÍTICO: O dia de admissão máximo permitido é:
            # horizonte - los + 1. Ex: se horizonte é 6 e LOS é 2, pode internar no dia 5 (fica 5 e 6).
            ultimo_dia_possivel = horizonte_planejamento - los + 1
            
            if ultimo_dia_possivel < 1:
                # Se o LOS sorteado é maior que o horizonte total, reduzimos o LOS para caber
                los = horizonte_planejamento
                ultimo_dia_possivel = 1

            # Tenta encontrar um dia de início que tenha vaga em todos os dias da estadia
            dias_para_testar = list(range(1, ultimo_dia_possivel + 1))
            random.shuffle(dias_para_testar)
            
            alocado = False
            for dia_inicio in dias_para_testar:
                intervalo = range(dia_inicio, dia_inicio + los)
                
                # Verifica se há leito disponível em todos os dias desse intervalo
                if all(ocupacao_diaria[d] < capacidade_total_por_dia for d in intervalo):
                    # Confirma a alocação
                    for d in intervalo:
                        ocupacao_diaria[d] += 1
                    
                    writer.writerow([
                        f"P{pacientes_gerados + 1}", 
                        random.choice(['M', 'F']), 
                        random.randint(1, 90), 
                        dia_inicio, 
                        los, 
                        random.choice(especialidades)
                    ])
                    pacientes_gerados += 1
                    alocado = True
                    break
            
            tentativa_paciente += 1

    print(f"Capacidade: {capacidade_total_por_dia} leitos/dia | Horizonte: {horizonte_planejamento} dias.")
    print(f"Total de leitos-dia disponíveis: {capacidade_total_por_dia * horizonte_planejamento}")
    print(f"Pacientes alocados: {pacientes_gerados}")

if __name__ == "__main__":
    # Note: Para 40 pacientes em 6 dias com 10 leitos (5 quartos x 2), 
    # o hospital vai lotar rápido, pois a demanda é maior que a oferta física.
    gerar_dados_hospitalares(num_quartos=5, num_pacientes=40, horizonte_planejamento=6)
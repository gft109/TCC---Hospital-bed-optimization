import csv

capacidade_total = 0
with open('data/pequeno/room.csv') as f:
    for row in csv.DictReader(f):
        capacidade_total += int(row['capacidade'])

ocupacao = {}
with open('data/pequeno/patient.csv') as f:
    for row in csv.DictReader(f):
        admissao = int(row['dia_admissao'])
        los = int(row['los'])
        for d in range(admissao, admissao + los):
            ocupacao[d] = ocupacao.get(d, 0) + 1

print(f"Capacidade total do hospital: {capacidade_total}")
for d in sorted(ocupacao):
    marca = " <-- ESTOURA" if ocupacao[d] > capacidade_total else ""
    print(f"Dia {d}: {ocupacao[d]} pacientes{marca}")
import pandas as pd

# Estrutura de exemplo para pacientes
patients_data = [
    {
        "id": 1,
        "Sexo": "M",
        "Idade": 45,
        "CID": "I21",
        "Condição": "Cardiopatia",
        "Gravidade": 8,
        "Alocação": "B101",
        "TempoEsperadoPermanencia(dias)": 7,
        "DataHoraInternacao": "2025-09-01 14:30",
        "DataHoraAlta": "2025-09-08 10:00",
    },
    {
        "id": 2,
        "Sexo": "F",
        "Idade": 62,
        "CID": "C50",
        "Condição": "Neoplasia Mamária",
        "Gravidade": 6,
        "Alocação": "B203",
        "TempoEsperadoPermanencia(dias)": 10,
        "DataHoraInternacao": "2025-09-05 09:15",
        "DataHoraAlta": "",
    },
    {
        "id": 3,
        "Sexo": "M",
        "Idade": 30,
        "CID": "A09",
        "Condição": "Infecção Gastrointestinal",
        "Gravidade": 4,
        "Alocação": "B305",
        "TempoEsperadoPermanencia(dias)": 3,
        "DataHoraInternacao": "2025-09-07 18:45",
        "DataHoraAlta": "",
    },
]

patients_df = pd.DataFrame(patients_data)

# Estrutura de exemplo para leitos
beds_data = [
    {
        "Identificador": "B101",
        "Status": "Ocupado",
        "Capacidade": 1,
        "Ocupacao": 1,
        "Ativo": True,
        "Localizacao": "Ala Cardíaca",
        "RegraOcupacao": "Adulto Masculino",
    },
    {
        "Identificador": "B203",
        "Status": "Ocupado",
        "Capacidade": 1,
        "Ocupacao": 1,
        "Ativo": True,
        "Localizacao": "Oncologia Feminina",
        "RegraOcupacao": "Adulto Feminino",
    },
    {
        "Identificador": "B305",
        "Status": "Disponível",
        "Capacidade": 1,
        "Ocupacao": 0,
        "Ativo": True,
        "Localizacao": "Clínica Geral",
        "RegraOcupacao": "Geral",
    },
]

beds_df = pd.DataFrame(beds_data)

# Salvar como CSVs
patients_csv = "src/data/patient.csv"
beds_csv = "src/data/hospitalBeds.csv"

patients_df.to_csv(patients_csv, index=False)
beds_df.to_csv(beds_csv, index=False)


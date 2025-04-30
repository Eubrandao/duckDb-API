from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import duckdb


class Dados(BaseModel):
    ano: int
    indice_educacao: float
    indice_saude: float
    observacao: str

app = FastAPI()

conn = duckdb.connect(database=':memory:', read_only=False)

def criar_tabela():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS indicadores (
            ano INTEGER,
            indice_educacao FLOAT,
            indice_saude FLOAT,
            observacao VARCHAR
        );
    """)

def popular_tabela():
    dados_iniciais = [
        {"ano": 2018, "indice_educacao": 0.55, "indice_saude": 0.6, "observacao": "Dados iniciais"},
        {"ano": 2019, "indice_educacao": 0.58, "indice_saude": 0.62, "observacao": "Pequena melhora em ambos"},
        {"ano": 2020, "indice_educacao": 0.6, "indice_saude": 0.63, "observacao": "Crescimento contínuo"},
        {"ano": 2021, "indice_educacao": 0.63, "indice_saude": 0.65, "observacao": "Avanço notável"},
        {"ano": 2022, "indice_educacao": 0.65, "indice_saude": 0.67, "observacao": "Estabilidade com leve alta"}
    ]
    for item in dados_iniciais:
        conn.execute("""
            INSERT INTO indicadores (ano, indice_educacao, indice_saude, observacao)
            VALUES (?, ?, ?, ?);
        """, (item["ano"], item["indice_educacao"], item["indice_saude"], item["observacao"]))


@app.get("/indicadores", response_model=List[Dados])
def get_indicadores():
    resultado = conn.execute("SELECT * FROM indicadores").fetchall()
    return [{"ano": row[0], "indice_educacao": row[1], "indice_saude": row[2], "observacao": row[3]} for row in resultado]


@app.post("/inserir", response_model=Dados)
def inserir_dados(dados: Dados):
    conn.execute("""
        INSERT INTO indicadores (ano, indice_educacao, indice_saude, observacao)
        VALUES (?, ?, ?, ?);
    """, (dados.ano, dados.indice_educacao, dados.indice_saude, dados.observacao))
    return dados


@app.on_event("startup")
def on_startup():
    try:
        criar_tabela()
        popular_tabela()
    except Exception as e:
        print(f"Erro durante o evento startup: {e}")



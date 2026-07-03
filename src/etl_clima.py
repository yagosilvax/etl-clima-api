import json
import requests
import pandas as pd
import os
from sqlalchemy import create_engine


def get_data():
    """Faz a requisição dos dados à API e retorna o arquivo em formato JSON local."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": [-23.5489, -22.9035],
	"longitude": [-46.6388, -43.2096],
	"hourly": "temperature_2m",
    "timezone": "America/Sao_Paulo",
	"past_days": 1,
    }

    try:
    
        response = requests.get(url,params=params)
        response.raise_for_status()
        response_json = response.json()

        with open("clima_data.json",'w') as file:
            json.dump(response_json,file,indent=4)
            return response_json
    except Exception as e:
        print(f'An error was found while trying to connect to API: {e}')
        return None

def transform_data(data):
    """Expande e transforma os dados do arquivo JSON para um formato tabular(dataframe)"""
    estados = ["SP","RJ"]

    dfs = []

    for i,estado in enumerate(estados):
        date = data[i]["hourly"]["time"]
        temp = data[i]["hourly"]["temperature_2m"]


        df_temp = pd.DataFrame({"date_time": date,
        "temperature": temp})

        df_temp["estado"]  = estado
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    df["date_time"] = pd.to_datetime(df["date_time"],errors="raise")
    return df




def load_db(df,table_name):
    """Carrega os dados tratados e padronizados no banco de dados."""

    host = os.getenv("host")
    database = os.getenv("database")
    user = os.getenv("usuario")
    port = os.getenv("port")
    password = os.getenv("senha_banco")
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    engine = create_engine(url)
    try:
        print(f"Trying to connect to {database}...")

        conn = engine.connect()
        if conn and table_name is not None and not df.empty:
            print(f'The data was inserted in {database} sucessfully!')
            return df.to_sql(name=table_name,con=engine,if_exists='append',index=False)
                
    except Exception as e:
        print(f"The connection has failed: {e}")



def main():
    print("Extracting data from Open-Meteo API...")
    dados_brutos = get_data()

    print("Transforming data...")
    df = transform_data(dados_brutos)

    load_db(df,'open_meteo_data')

main()


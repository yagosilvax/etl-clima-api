import json
import requests
import pandas as pd
import os
import logging
from sqlalchemy import create_engine,text
from dotenv import load_dotenv

logging.basicConfig(
    level = logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("etl_clima.log"),
        logging.StreamHandler()
]

)
logger = logging.getLogger(__name__)



def get_data():
    """Faz a requisição dos dados à API e retorna o arquivo em formato JSON local."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": [-23.5489, -22.9035],
	"longitude": [-46.6388, -43.2096],
	"hourly": ["temperature_2m",
            "relative_humidity_2m","precipitation","apparent_temperature"],
    "timezone": "America/Sao_Paulo",
	"past_days": 1,
    "forecast_days": 0
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
        raise

def transform_data(data):
    """Expande e transforma os dados do arquivo JSON para um formato tabular(dataframe)"""
    estados = ["SP","RJ"]

    dfs = []

    for i,estado in enumerate(estados):
        date = data[i]["hourly"]["time"]
        umidity = data[i]["hourly"]["relative_humidity_2m"]
        precipitation = data[i]["hourly"]["precipitation"]
        ap_temperature = data[i]["hourly"]["apparent_temperature"]
        temp = data[i]["hourly"]["temperature_2m"]


        df_temp = pd.DataFrame({"date_time": date,
        "temperature": temp,"umidity": umidity,"precipitation":precipitation,"apparent_temp": ap_temperature})

        df_temp["estado"]  = estado
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    df["date_time"] = pd.to_datetime(df["date_time"],errors="raise")
    df["hora"] = df["date_time"].dt.hour
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
        logger.info(f"Trying to connect to {database}...")
        with engine.begin() as conn:
            df.to_sql(name='temp_staging',con=conn,if_exists='replace',index=False)

            conn.execute(text(
            f"""INSERT INTO {table_name} (date_time,temperature,umidity,precipitation,apparent_temp,estado,hora)
                SELECT date_time,temperature,umidity,precipitation,apparent_temp,estado,hora
                FROM temp_staging
                ON CONFLICT (estado,date_time) DO NOTHING """))
            
            logger.info(f'The data was inserted in {database}.')
    except Exception as e:
        logger.error(f"The connection has failed: {e}")
        raise
        


load_dotenv(override=True)

if __name__ == "__main__":
    try:
        logger.info("Extracting data from Open-Meteo API...")
        dados_brutos = get_data()
        logger.info("Transforming data...")
        df = transform_data(dados_brutos)
        load_db(df,'open_meteo_data')
        logger.info("The pipeline has finalized sucessfully!")
    except Exception as e:
        logger.critical(f"Pipeline was interrupted:{e}")



import requests
import logging
import os
from datetime import datetime
import json

def extract_data():
    """
    It extracts currency data from AwesomeAPI and save
    the raw files in JSON format to the data/raw folder.
    """

    folder_raw = "data/raw"
    os.makedirs(folder_raw, exist_ok=True)

    moedas = ["USD-BRL","EUR-BRL","BTC-BRL"]

    for moeda in moedas:
        url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}/30"

        print(f"Iniciando extração da API {url}")
        resposta = requests.get(url)

        logging.info(f"Status Code: {resposta.status_code}")
        print(f"Status Code: {resposta.status_code}")
    
        if resposta.status_code != 200:
            logging.error("Status Code diferente de 200")
            raise Exception(f"Falha da extração. Status Code: {resposta.status_code}")

        caminho_arquivo = os.path.join(folder_raw, f"{moeda}.json")

        arquivo_json = resposta.json()
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            json.dump(arquivo_json, arquivo, indent=4, ensure_ascii=False)

        print(f"Dados extraidos com sucesso! Arquivo: {caminho_arquivo}")

    return caminho_arquivo

# The block below is for testing this file directly
if __name__ == "__main__":
    # Configure basic logging for testing
    logging.basicConfig(level=logging.INFO)
    extract_data()
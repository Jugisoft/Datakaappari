import requests
import pandas as pd

def hae_pesis_data(ottelu_id):
    # Pesistulokset API-osoite (huom: osoite voi muuttua, mutta logiikka pysyy)
    api_url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        # Täältä löytyy esimerkiksi tapahtumavirta (lyönti lyönniltä)
        tapahtumat = data.get('tapahtumat', [])
        
        # Muutetaan DataFrameksi analyysia varten
        df = pd.DataFrame(tapahtumat)
        return df
    except Exception as e:
        return f"Virhe haussa: {e}"

# Esimerkki hausta
ottelu_df = hae_pesis_data("128853")

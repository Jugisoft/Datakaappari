import streamlit as st
import pandas as pd
import requests

# Yritetään hakea suoraan uuden järjestelmän JSON-syötettä
def hae_otteludata(id):
    # Tämä on se "salainen" polku, jota sivu käyttää taustalla
    url = f"https://v2.pesistulokset.fi/api/ottelu/{id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://www.pesistulokset.fi/ottelut/{id}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

st.title("⚾ Otteludatan Syväkaappaus")

ottelu_id = "128858" # Sinun linkkisi ID

if st.button("Pura pöytäkirjan data"):
    data = hae_otteludata(ottelu_id)
    
    if data:
        st.success("Yhteys saatu! Puretaan tapahtumat...")
        
        # Pöytäkirjan tapahtumat ovat usein listana
        tapahtumat = data.get('tapahtumat', [])
        
        if tapahtumat:
            df = pd.DataFrame(tapahtumat)
            
            # Tässä on se data mitä etsit: kuka löi, mihin, ja mitä kävi
            st.write("### Kaikki ottelutapahtumat")
            st.dataframe(df)
            
            # Tehdään tästä CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Lataa raaka pöytäkirjadata (CSV)", csv, f"poytakirja_{ottelu_id}.csv")
        else:
            st.warning("Ottelu löytyi, mutta tapahtumalista on tyhjä. Peli ei ehkä ole vielä alkanut tai se on arkistoitu eri tavalla.")
    else:
        st.error("Palvelin hylkäsi pyynnön. Rajapinta on suojattu.")

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Pesis-Kaappari", layout="wide")

st.title("⚾ Otteludatan haku")

ottelu_id = st.text_input("Syötä Ottelu-ID (esim. 128858)", "128858")

if st.button("Hae ottelun tapahtumat"):
    # Yritetään hakea suoraan sivun osoitteesta
    url = f"https://www.pesistulokset.fi/ottelut/{ottelu_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            st.success("Yhteys sivustoon saatu!")
            
            # Tässä kohtaa uusi sivusto lataa datan JavaScriptillä, 
            # mikä on Pythonille vaikeaa ilman raskaampia työkaluja.
            # JOTEN: Lisätään hätävara-ohje ja tiedostonluku:
            
            st.info("Uusi sivusto on suojattu suoralta luvulta. Voit kuitenkin hakea datan näin:")
            st.markdown(f"""
            1. Mene osoitteeseen: [https://www.pesistulokset.fi/ottelut/{ottelu_id}](https://www.pesistulokset.fi/ottelut/{ottelu_id})
            2. Klikkaa **'Ottelutapahtumat'**
            3. Maalaa ja kopioi taulukko.
            4. Tallenna se CSV-tiedostoksi ja lataa se tähän alapuolelle analyysia varten.
            """)
            
        else:
            st.error(f"Sivua ei löytynyt (Virhe {response.status_code})")
    except Exception as e:
        st.error(f"Virhe: {e}")

st.divider()

# TÄMÄ ON SE TOIMIVA OSA:
st.subheader("📁 Lataa kopioimasi data")
uploaded_file = st.file_uploader("Lataa otteludata (CSV tai Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.write("### Ottelun raakadata:")
    st.dataframe(df)
    
    # Mahdollisuus ladata puhdistettu versio
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Tallenna puhdistettu CSV", csv, "ottelu_export.csv", "text/csv")

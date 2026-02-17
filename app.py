import streamlit as st
import pandas as pd
import requests

st.title("⚾ Pöytäkirjan syväpurku")

ottelu_id = st.text_input("Syötä ID", "128858")

if st.button("Pura data"):
    # TÄMÄ on se osoite, josta sivu oikeasti hakee tiedot
    api_url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://www.pesistulokset.fi",
        "Referer": "https://www.pesistulokset.fi/"
    }

    try:
        r = requests.get(api_url, headers=headers)
        
        if r.status_code == 200:
            json_data = r.json()
            st.success("Yhteys onnistui! Data löytyi.")
            
            # Puretaan tapahtumat (lyönnit, suunnat, palot jne)
            tapahtumat = json_data.get('tapahtumat', [])
            if tapahtumat:
                df = pd.DataFrame(tapahtumat)
                st.write("### Ottelun tapahtumat (Pöytäkirja)")
                st.dataframe(df)
                
                # Lataus
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Lataa raakadata CSV", csv, f"{ottelu_id}_data.csv")
            else:
                st.warning("Data löytyi, mutta se on tyhjä. Peli saattaa olla liian vanha tai vasta tulossa.")
        else:
            st.error(f"Palvelin ei anna dataa (Virhe {r.status_code})")
            st.info("Tämä tarkoittaa, että liitto on estänyt automaattiset haut pilvipalveluista.")
            
    except Exception as e:
        st.error(f"Virhe: {e}")

st.divider()
st.subheader("💡 Miksi tämä on niin vaikeaa?")
st.write("Sivusto lataa datan 'salaoven' kautta. Jos tämä nappi ei toimi, liitto on sulkenut oven roboteilta.")

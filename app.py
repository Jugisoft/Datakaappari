import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pesis-Analysaattori PRO", layout="wide")

st.title("⚾ Pesis-Analysaattori")

with st.sidebar:
    st.header("Hae Ottelu")
    # Kokeillaan ID:tä 128858
    ottelu_id = st.text_input("Ottelu-ID", "128858")
    hae = st.button("HAE JA ANALYSOI", type="primary", use_container_width=True)

if hae:
    # UUSI OSOITE: Pesistulokset.fi uusi rajapinta käyttää tätä muotoa
    # Huom: Jos peli on vuodelta 2024 tai 2025, polku voi vaihdella
    api_url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            
            # Perustiedot
            koti = data.get('koti_joukkue', {}).get('nimi', 'Koti')
            vieras = data.get('vieras_joukkue', {}).get('nimi', 'Vieras')
            st.success(f"Ottelu löytyi: {koti} - {vieras}")
            
            # Tapahtumat
            tapahtumat = data.get('tapahtumat', [])
            if tapahtumat:
                df = pd.DataFrame(tapahtumat)
                
                # --- VEDONLYÖNTIANALYYSI ---
                st.subheader("🛡️ Ulkopelin analyysi (Plug & Play)")
                
                # Lasketaan torjunnat ja yritykset
                # Suodatetaan pois tyhjät tai epäolennaiset rivit
                if 'tapahtuma_teksti' in df.columns:
                    col1, col2, col3 = st.columns(3)
                    
                    palot = len(df[df['tapahtuma_teksti'] == 'Palo'])
                    juoksut = len(df[df['tapahtuma_teksti'] == 'Juoksu'])
                    
                    col1.metric("Torjunnat (Palot)", palot)
                    col2.metric("Päästetyt juoksut", juoksut)
                    col3.metric("Tilanteita yhteensä", len(df))
                
                with st.expander("Näytä raakadata"):
                    st.dataframe(df)
            else:
                st.warning("Ottelusta ei löytynyt pelitapahtumia. Onko peli jo pelattu?")
                
        elif r.status_code == 404:
            st.error("Virhe 404: Ottelua ei löytynyt. Pesistulokset on saattanut muuttaa ID:tä tai rajapintaa.")
            st.info("Kokeile käyttää ID:tä 128853 (Tahko-KPL) testataksesi, toimiiko yhteys.")
        else:
            st.error(f"Palvelinvirhe: {r.status_code}")
            
    except Exception as e:
        st.error(f"Yhteysvirhe: {e}")

st.divider()
st.caption("Vinkki: Jos API ei vastaa, voit ladata pelin CSV-tiedoston manuaalisesti ja pudottaa sen tähän.")

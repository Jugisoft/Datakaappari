import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pesis-Analysaattori PRO", layout="wide")

st.title("⚾ Pesis-Analysaattori")

# Palkki haulle
with st.sidebar:
    st.header("Hae Ottelu")
    # Linkistä https://www.pesistulokset.fi/ottelut/128858 ID on 128858
    ottelu_id = st.text_input("Ottelu-ID", "128858")
    hae = st.button("HAE JA ANALYSOI", type="primary", use_container_width=True)

if hae:
    # Käytetään ensisijaisesti tätä API-polkua
    api_url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    
    # Lisätään otsikot, jotta palvelin ei hylkää pyyntöä
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        
        # Tarkistetaan vastaus ennen JSON-muunnosta
        if r.status_code == 200:
            data = r.json()
            
            koti = data['koti_joukkue']['nimi']
            vieras = data['vieras_joukkue']['nimi']
            
            st.success(f"Yhteys muodostettu: {koti} - {vieras}")
            
            # Tapahtumadata
            if 'tapahtumat' in data and len(data['tapahtumat']) > 0:
                df = pd.DataFrame(data['tapahtumat'])
                
                # --- VISUALISOINTI ---
                st.subheader("🛡️ Ulkopelin tilanneanalyysi")
                
                # Lasketaan yritykset ja torjunnat (yksinkertaistettu esimerkki)
                # Oikeassa datassa suodatetaan 'tapahtuma_teksti' perusteella
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Tapahtumia yhteensä", len(df))
                
                if 'tulos_teksti' in df.columns:
                    palot = len(df[df['tapahtuma_teksti'].str.contains('Palo', case=False, na=False)])
                    col2.metric("Palot (Torjunnat)", palot)
                    
                    kärkilyönnit = len(df[df['tapahtuma_teksti'].str.contains('Kärkilyönti', case=False, na=False)])
                    col3.metric("Kärkilyönnit (Päästetyt)", kärkilyönnit)

                # Näytetään raaka-data
                with st.expander("Katso kaikki ottelutapahtumat"):
                    st.dataframe(df, use_container_width=True)
                
                # CSV Lataus vedonlyöntiyhtiölle
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Lataa Plug & Play CSV", csv, f"pesis_peli_{ottelu_id}.csv", "text/csv")
                
            else:
                st.warning("Ottelusta löytyi perustiedot, mutta ei vielä pelitapahtumia (onko peli alkanut?)")
        else:
            st.error(f"Palvelin vastasi virheellä: {r.status_code}. Rajapinta saattaa olla tilapäisesti poissa käytöstä.")

    except Exception as e:
        st.error(f"Virhe: {e}")
        st.info("Kokeile tarkistaa, että ID on pelkkä numero ilman välilyöntejä.")

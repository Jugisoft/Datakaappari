import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pesis-Analysaattori PRO", layout="wide")

st.title("⚾ Pesis-Analysaattori")

# Palkki haulle
with st.sidebar:
    st.header("Hae Ottelu")
    # Otetaan ID talteen URL:sta (esim. 128858)
    ottelu_id = st.text_input("Ottelu-ID", "128858")
    hae = st.button("HAE JA ANALYSOI", type="primary", use_container_width=True)

if hae:
    # Uusi API-osoite joka vastaa uutta pesistulokset.fi-rakennetta
    api_url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    
    try:
        r = requests.get(api_url)
        data = r.json()
        
        koti = data['koti_joukkue']['nimi']
        vieras = data['vieras_joukkue']['nimi']
        
        st.header(f"{koti} vs. {vieras}")
        
        # Tapahtumadata
        df = pd.DataFrame(data['tapahtumat'])
        
        # --- PLUG & PLAY ANALYYSI VEDONLYÖNTIYHTIÖLLE ---
        st.subheader("🛡️ Ulkopelin torjuntatilastot (Live)")
        
        # Määritellään onnistumiset sisäpelin kannalta
        # (Tulostekstit voivat vaihdella: 'Palo', 'Kärkilyönti', 'Juoksu')
        if 'tulos_teksti' in df.columns:
            # Filtteröidään tilanteet (esim. 0-1 väli on tilanne jossa 1-pesä tyhjä ja yritys sinne)
            # Tässä yksinkertaistettu malli joka näyttää logiikan:
            
            summary_data = []
            vapaat = ["Vapaataival", "Harha"] # Vedonlyöntiyhtiön "V" ja "HH" sarakkeet
            
            for vali in ["0-1", "1-2", "2-3", "Kotiutus"]:
                # Etsitään kaikki yritykset kyseiselle välille
                # (Oikeassa datassa katsotaan pesätilanne-saraketta)
                yritykset = len(df) // 4 # Demo-luku
                palot = len(df[df['tapahtuma_teksti'] == 'Palo']) // 4
                
                summary_data.append({
                    "Pesäväli": vali,
                    "Yritykset (Y)": yritykset,
                    "Torjunnat (T)": palot,
                    "Torjunta-%": round((palot/yritykset)*100, 1) if yritykset > 0 else 0
                })
            
            st.table(pd.DataFrame(summary_data))
            
            # --- LUKKARI JA PELAAJASPESIAALIT ---
            st.subheader("👤 Ulkopelaajien suoritukset")
            up_cols = st.columns(2)
            
            # Kärpäset (Lukkari)
            karpaset = len(df[df['tapahtuma_teksti'].str.contains('kärpänen', case=False, na=False)])
            up_cols[0].metric("Lukkarin kärpäset", karpaset)
            
            # Harhaheitot
            harhat = len(df[df['tulos_teksti'].str.contains('harha', case=False, na=False)])
            up_cols[1].metric("Päästetyt harhat", harhat)

        # Näytetään raaka-data tarkistusta varten
        with st.expander("Katso ottelun kaikki tapahtumat"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Datan haku epäonnistui. Tarkista ID. Virhe: {e}")

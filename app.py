import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- ASETUKSET ---
st.set_page_config(page_title="Pesis Data-Kaappari PRO", layout="wide")

# CSS-tyylit käyttöliittymän parantamiseksi
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚾ Pesis Data-Kaappari & Analyysi")
st.info("Syötä ottelu-ID (esim. 128853) sivupalkkiin hakeaksesi dataa.")

# Alustetaan session_state, jotta data säilyy
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'peli_info' not in st.session_state:
    st.session_state.peli_info = None

# --- 1. DATAN HAKU API:STA ---
with st.sidebar:
    st.header("🔍 Hakupaneeli")
    ottelu_id = st.text_input("Ottelu-ID", "128853")
    hae_nappi = st.button("HAE OTTELUN TIEDOT", type="primary", use_container_width=True)

if hae_nappi:
    url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    try:
        with st.spinner('Haetaan dataa Pesistuloksista...'):
            r = requests.get(url, timeout=10)
            r.raise_for_status() # Tarkistaa että haku onnistui
            raw_data = r.json()
            
            st.session_state.peli_info = {
                "koti": raw_data['koti_joukkue']['nimi'],
                "vieras": raw_data['vieras_joukkue']['nimi'],
                "tulos": raw_data.get('tulos_teksti', "Peli kesken")
            }
            
            if 'tapahtumat' in raw_data:
                events = pd.DataFrame(raw_data['tapahtumat'])
                st.session_state.raw_df = events
                st.success(f"Ladattu: {st.session_state.peli_info['koti']} vs {st.session_state.peli_info['vieras']}")
            else:
                st.warning("Ottelusta ei löytynyt tapahtumadataa.")
    except Exception as e:
        st.error(f"Virhe haettaessa dataa: {e}")

# --- 2. ANALYYSI (Vedonlyöntiyhtiön Plug & Play) ---
if st.session_state.raw_df is not None:
    df = st.session_state.raw_df
    info = st.session_state.peli_info

    st.header(f"📊 Analyysi: {info['koti']} - {info['vieras']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛡️ Ulkopelin torjuntatehokkuus")
        
        # Laskentamalli vedonlyöntiyhtiölle
        # API:n rakenteesta riippuen haetaan onnistumiset ja yritykset
        # Tämä on esimerkki logiikasta, jota voidaan hienosäätää
        
        stats_data = []
        for vali in ["0-1", "1-2", "2-3", "3-Koti"]:
            # Tähän kohtaan rakennetaan suodatus API-datasta
            # Esim: df[df['pesavali'] == vali]
            stats_data.append({
                "Pesäväli": vali,
                "Yritykset": 10, # Esimerkkiarvo
                "Onnistumiset": 4, # Esimerkkiarvo
                "Torjunnat": 6
            })
        
        res_df = pd.DataFrame(stats_data)
        res_df['Torjunta%'] = (res_df['Torjunnat'] / res_df['Yritykset'] * 100).round(1)
        
        st.table(res_df)
        

    with col2:
        st.subheader("👤 Pelaajakohtaiset palot")
        # Jos API:ssa on 'ulkopelaaja' tai vastaava kenttä
        if 'ulkopelaaja_nimi' in df.columns:
            palot = df[df['tapahtuma'] == 'PALO']['ulkopelaaja_nimi'].value_counts()
            st.bar_chart(palot)
        else:
            st.info("Pelaajakohtaista palodataa odotetaan API:sta...")

    # --- LATAUKSET ---
    st.divider()
    st.subheader("📥 Export")
    csv_raw = df.to_csv(index=False).encode('utf-8')
    st.download_button("Lataa raaka-data kertoimenlaskentaan (CSV)", csv_raw, f"ottelu_{ottelu_id}_data.csv", "text/csv")

else:
    st.write("---")
    st.write("Odotetaan hakua... Syötä ID ja paina nappia.")

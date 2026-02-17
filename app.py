import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- ASETUKSET ---
st.set_page_config(page_title="Pesis Data-Kaappari PRO", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚾ Pesis Data-Kaappari & Analyysi")
st.info("Hae peli ID:llä (esim. 128853) tai syötä tiedot manuaalisesti.")

# --- 1. DATAN HAKU API:STA ---
with st.sidebar:
    st.header("🔍 Hae ottelu")
    ottelu_id = st.text_input("Ottelu-ID", "128853")
    hae_nappi = st.button("HAE OTTELUN TIEDOT", type="primary", use_container_width=True)

if hae_nappi:
    url = f"https://v2.pesistulokset.fi/api/ottelu/{ottelu_id}"
    try:
        r = requests.get(url)
        raw_data = r.json()
        
        # Tallennetaan session stateen
        st.session_state.peli_info = {
            "koti": raw_data['koti_joukkue']['nimi'],
            "vieras": raw_data['vieras_joukkue']['nimi'],
            "pvm": raw_data.get('paivamaara', datetime.now().strftime("%d.%m.%Y"))
        }
        
        # Tapahtumien prosessointi (lyönnit, palot jne)
        if 'tapahtumat' in raw_data:
            events = pd.DataFrame(raw_data['tapahtumat'])
            st.session_state.raw_df = events
            st.success(f"Ladattu: {st.session_state.peli_info['koti']} vs {st.session_state.peli_info['vieras']}")
    except Exception as e:
        st.error(f"Virhe haettaessa dataa: {e}")

# --- 2. ANALYYSI (Vedonlyöntiyhtiön Plug & Play) ---
if 'raw_df' in st.session_state:
    df = st.session_state.raw_df
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Ulkopelin tehokkuus (Torjunta%)")
        
        # Yksinkertaistettu logiikka: Jos tulos on palo/haava -> torjunta
        # Huom: Oikeassa APIssa sarakkeiden nimet voivat vaihdella (tulos_teksti tms)
        # Tehdään placeholder-analyysi joka näyttää rakenteen
        
        if 'tulos' in df.columns:
            # Filtteröidään tilanteet (0-1, 1-2, 2-3)
            # Tässä vaiheessa luodaan se "Plug & Play" taulukko
            st.write("Vedonlyöntiyhtiön haluamat torjuntaprosentit:")
            
            # Esimerkki koostamisesta
            stats_view = pd.DataFrame({
                "Pesäväli": ["0-1", "1-2", "2-3", "Kotiutus"],
                "Yritykset": [15, 12, 8, 10], # Tähän laskenta livenä
                "Torjunnat": [8, 6, 4, 7]
            })
            stats_view['Torjunta%'] = (stats_view['Torjunnat'] / stats_view['Yritykset'] * 100).round(1)
            st.table(stats_view)

    with col2:
        st.subheader("🎯 Pelaajasuoritukset")
        if 'ulkopelaaja' in df.columns:
            up_stats = df['ulkopelaaja'].value_counts()
            st.bar_chart(up_stats)
        else:
            st.write("Pelaajakohtaista dataa prosessoidaan...")

    # --- LATAUKSET ---
    st.divider()
    c_d1, c_d2 = st.columns(2)
    
    csv_raw = df.to_csv(index=False).encode('utf-8')
    c_d1.download_button("📥 Lataa raaka-data (CSV)", csv_raw, f"peli_{ottelu_id}_raw.csv", "text/csv")
    
    # Valmis raportti yhtiölle
    c_d2.button("📧 Lähetä raportti yhtiölle (Demo)", disabled=True)

else:
    st.write("Syötä ottelu-ID vasemmalle ja paina 'Hae'.")

# --- 3. MANUAALINEN VARASYÖTTÖ ---
with st.expander("⌨️ Manuaalinen syöttö (Hätävara)"):
    st.write("Jos API ei toimi, voit käyttää aiempaa syöttölomaketta tästä.")
    # Tähän voi kopioida aiemman lomakekoodin jos haluaa pitää molemmat

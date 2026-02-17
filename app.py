import streamlit as st
import pandas as pd

# 1. Ladataan data
st.title("⚾ Pesäpallon Ulkopelianalyysi")
st.write("Tämä sovellus laskee ulkopelin tehokkuutta ottelutapahtumista.")

# Huom: Muuta tiedostonimi vastaamaan omaa Exceliäsi tai CSV:täsi
try:
    df = pd.read_csv("testi_2.xlsx - Kysely1.csv") #
    
    # 2. Sivupalkin suodattimet
    st.sidebar.header("Suodattimet")
    jakso = st.sidebar.multiselect("Valitse jakso (period)", df['period'].unique(), default=df['period'].unique())
    vuoro = st.sidebar.multiselect("Valitse vuoropari (inning)", df['inning'].unique(), default=df['inning'].unique())

    filtered_df = df[(df['period'].isin(jakso)) & (df['inning'].isin(vuoro))] #

    # 3. Lasketaan tilastot per pesäväli
    st.subheader("Ulkopelin tehokkuus pesäväleittäin")
    pesat = ["1", "2", "3", "Koti"]
    
    stats_data = []
    for pesa in pesat:
        pesa_df = filtered_df[filtered_df['Kohdepesä'] == pesa] #
        
        palot = len(pesa_df[pesa_df['Tyyppi'] == 'Palo']) #
        haavat = len(pesa_df[pesa_df['Tyyppi'] == 'Haavoittuminen']) #
        etenemiset = len(pesa_df[pesa_df['Tyyppi'] == 'Eteneminen']) #
        yhteensa = palot + haavat + etenemiset
        
        tehokkuus = (palot + haavat) / yhteensa * 100 if yhteensa > 0 else 0
        
        stats_data.append({
            "Pesäväli": pesa,
            "Palot": palot,
            "Haavoittumiset": haavat,
            "Etenemiset (SAFE)": etenemiset,
            "Tehokkuus %": round(tehokkuus, 1)
        })

    stats_df = pd.DataFrame(stats_data)
    st.table(stats_df)

    # 4. Erityistilanteet: Kärpäset ja Lukkarityö
    st.subheader("Lukkari- ja erikoistilanteet")
    karpaset = filtered_df[filtered_df['Tapahtuma'].str.contains("kärpänen", case=False, na=False)]
    st.write(f"Tunnistetut kärpäset: **{len(karpaset)}**")
    
    if len(karpaset) > 0:
        st.write(karpaset[['period', 'inning', 'Tapahtuma']]) #

except Exception as e:
    st.error(f"Lataa data ensin! Virhe: {e}")

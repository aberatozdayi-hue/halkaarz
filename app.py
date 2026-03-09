import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# Sayfa Ayarları
st.set_page_config(page_title="Halka Arz Pro Takip", layout="wide")
st.title("📈 aberato")

# Senin Güncel Portföy Verilerin
hisseler = {
    "GENKM": {"lot": 155, "maliyet": 11.00, "symbol": "GENKM.IS"},
    "SVGYO": {"lot": 169, "maliyet": 3.25, "symbol": "SVGYO.IS"},
    "LXGYO": {"lot": 55, "maliyet": 12.05, "symbol": "LXGYO.IS"},
    "MCARD": {"lot": 9, "maliyet": 80.00, "symbol": "MCARD.IS"}
}

# Verileri Yahoo Finance üzerinden çekme fonksiyonu
@st.cache_data(ttl=300) # Verileri 5 dakikada bir yeniler
def veri_getir():
    data_list = []
    for hisse, bilgi in hisseler.items():
        try:
            ticker = yf.Ticker(bilgi["symbol"])
            # Gecikmeli son fiyatı çekiyoruz
            fiyat = ticker.fast_info['last_price']
            if fiyat is None or fiyat == 0:
                fiyat = bilgi["maliyet"]
        except:
            fiyat = bilgi["maliyet"]
        
        data_list.append({
            "Hisse": hisse,
            "Alış Fiyatı": bilgi["maliyet"],
            "Lot": bilgi["lot"],
            "Güncel Fiyat": round(fiyat, 2),
            "Maliyet": round(bilgi["lot"] * bilgi["maliyet"], 2),
            "Değer": round(bilgi["lot"] * fiyat, 2)
        })
    return pd.DataFrame(data_list)

# Tabloyu oluşturma
df = veri_getir()
df["Kar (TL)"] = df["Değer"] - df["Maliyet"]
df["Kar %"] = (df["Kar (TL)"] / df["Maliyet"]) * 100

# Görsel Arayüz
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Canlı Portföy Durumu")
    st.dataframe(df.style.format({
        "Alış Fiyatı": "{:.2f} TL", "Güncel Fiyat": "{:.2f} TL",
        "Maliyet": "{:.2f} TL", "Değer": "{:.2f} TL",
        "Kar (TL)": "{:.2f} TL", "Kar %": "%{:.2f}"
    }), use_container_width=True)

with col2:
    st.subheader("🎨 Portföy Dağılımı")
    fig = px.pie(df, values='Değer', names='Hisse', hole=0.4, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("💡 Fiyatlar Yahoo Finance üzerinden 15 dakika gecikmeli olarak otomatik güncellenmektedir.")

import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# Sayfa Ayarları
st.set_page_config(page_title="Halka Arz Pro Takip", layout="wide")
st.title("📈 aberato")

# Portföyü Hafızada Tutma (Ekleme/Çıkarma yapabilmek için)
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame({
        "Hisse": ["GENKM", "SVGYO", "LXGYO", "MCARD"],
        "Alış Fiyatı": [11.00, 3.25, 12.05, 80.00],
        "Lot": [155, 169, 55, 9]
    })

# --- YAN PANEL: Portföy Yönetimi ---
st.sidebar.header("📝 Portföy Yönetimi")

# 1. Yeni Hisse Ekleme
st.sidebar.subheader("Yeni Hisse Ekle")
yeni_hisse_ad = st.sidebar.text_input("Hisse Kodu (Örn: THYAO)")
yeni_hisse_alis = st.sidebar.number_input("Alış Fiyatı", min_value=0.0, format="%.2f")
yeni_hisse_lot = st.sidebar.number_input("Lot Sayısı", min_value=0, step=1)

if st.sidebar.button("Hisse Ekle"):
    if yeni_hisse_ad:
        yeni_hisse_ad = yeni_hisse_ad.upper()
        if yeni_hisse_ad not in st.session_state.portfolio['Hisse'].values:
            yeni_satir = pd.DataFrame({"Hisse": [yeni_hisse_ad], "Alış Fiyatı": [yeni_hisse_alis], "Lot": [yeni_hisse_lot]})
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, yeni_satir], ignore_index=True)
            st.sidebar.success(f"{yeni_hisse_ad} eklendi!")
            st.rerun()
        else:
            st.sidebar.warning("Bu hisse zaten var!")

st.sidebar.divider()

# 2. Mevcut Hisseyi Düzenle veya Sil
st.sidebar.subheader("Hisse Düzenle / Sil")
secilen_hisse = st.sidebar.selectbox("Düzenlenecek Hisse:", st.session_state.portfolio['Hisse'].tolist())
if secilen_hisse:
    mevcut_alis = float(st.session_state.portfolio.loc[st.session_state.portfolio['Hisse'] == secilen_hisse, 'Alış Fiyatı'].iloc[0])
    mevcut_lot = int(st.session_state.portfolio.loc[st.session_state.portfolio['Hisse'] == secilen_hisse, 'Lot'].iloc[0])
    
    guncel_alis = st.sidebar.number_input("Yeni Alış Fiyatı", value=mevcut_alis, format="%.2f", key="g_alis")
    guncel_lot = st.sidebar.number_input("Yeni Lot Sayısı", value=mevcut_lot, step=1, key="g_lot")
    
    col_g1, col_g2 = st.sidebar.columns(2)
    if col_g1.button("Güncelle"):
        st.session_state.portfolio.loc[st.session_state.portfolio['Hisse'] == secilen_hisse, 'Alış Fiyatı'] = guncel_alis
        st.session_state.portfolio.loc[st.session_state.portfolio['Hisse'] == secilen_hisse, 'Lot'] = guncel_lot
        st.sidebar.success("Güncellendi!")
        st.rerun()
    
    if col_g2.button("Sil"):
        st.session_state.portfolio = st.session_state.portfolio[st.session_state.portfolio['Hisse'] != secilen_hisse]
        st.sidebar.error(f"{secilen_hisse} Silindi!")
        st.rerun()

# --- CANLI VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=300)
def canli_veri_getir(portfolio_df):
    sonuclar = []
    for index, row in portfolio_df.iterrows():
        hisse = row['Hisse']
        alis = row['Alış Fiyatı']
        lot = row['Lot']
        symbol = f"{hisse}.IS"
        
        try:
            ticker = yf.Ticker(symbol)
            guncel_fiyat = ticker.fast_info['last_price']
            if guncel_fiyat is None or pd.isna(guncel_fiyat) or guncel_fiyat == 0:
                guncel_fiyat = alis
        except:
            guncel_fiyat = alis
        
        maliyet = alis * lot
        deger = guncel_fiyat * lot
        
        sonuclar.append({
            "Hisse": hisse,
            "Alış Fiyatı": alis,
            "Lot": lot,
            "Güncel Fiyat": round(guncel_fiyat, 2),
            "Maliyet": round(maliyet, 2),
            "Değer": round(deger, 2)
        })
    return pd.DataFrame(sonuclar)

# Ekrana Yazdırma İşlemleri
if not st.session_state.portfolio.empty:
    df = canli_veri_getir(st.session_state.portfolio)
    df["Kar (TL)"] = df["Değer"] - df["Maliyet"]
    df["Kar %"] = (df["Kar (TL)"] / df["Maliyet"]) * 100

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
        if df["Değer"].sum() > 0:
            fig = px.pie(df, values='Değer', names='Hisse', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Fiyatlar Yahoo Finance üzerinden 15 dakika gecikmeli olarak otomatik güncellenmektedir.")
    st.divider()

    # --- TAVAN SERİSİ TAHMİNCİSİ ---
    st.subheader("🚀 Tavan Serisi Kar Tahmincisi")
    st.info("Bu bölüm, seçtiğiniz hissenin üst üste tavan yapması durumunda oluşacak karı hesaplar.")
    
    t_hisse = st.selectbox("Tahmin Yapılacak Hisse", df["Hisse"])
    t_gun = st.slider("Kaç Gün Tavan Gider?", 1, 15, 5)
    
    if t_hisse:
        t_lot = df.loc[df['Hisse'] == t_hisse, 'Lot'].iloc[0]
        t_baslangic = df.loc[df['Hisse'] == t_hisse, 'Güncel Fiyat'].iloc[0]
        t_maliyet = df.loc[df['Hisse'] == t_hisse, 'Maliyet'].iloc[0]
        
        current_price = t_baslangic
        t_fiyatlar = []
        for i in range(t_gun):
            current_price = current_price * 1.10
            t_fiyatlar.append(round(current_price, 2))
        
        t_son_deger = t_fiyatlar[-1] * t_lot
        t_kar = t_son_deger - t_maliyet
        
        st.success(f"**{t_gun}** gün sonra tahmin edilen fiyat: **{t_fiyatlar[-1]:.2f} TL**")
        st.success(f"Tahmin edilen toplam kar: **{t_kar:,.2f} TL**")
else:
    st.warning("Portföyünüzde hisse bulunmuyor. Sol panelden hisse ekleyebilirsiniz.")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. FUNGSI LOAD DATA DENGAN ERROR HANDLING
@st.cache_data
def load_data():
    """Memuat data dari file CSV dengan error handling"""
    # Cek lokasi file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'main_data.csv')
    
    if not os.path.exists(file_path):
        file_path = 'main_data.csv'
    
    try:
        df = pd.read_csv(file_path)
        
        # Membersihkan spasi di nama kolom
        df.columns = df.columns.str.strip()
        
        # Mengonversi tipe datetime
        if 'order_purchase_timestamp' in df.columns:
            df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        
        # Mengekstrak fitur waktu
        df['year'] = df['order_purchase_timestamp'].dt.year
        df['month'] = df['order_purchase_timestamp'].dt.month
        df['month_name'] = df['order_purchase_timestamp'].dt.month_name()
        df['year_month'] = df['order_purchase_timestamp'].dt.to_period('M')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.error("Pastikan file 'main_data.csv' tersedia di folder yang sama dengan dashboard.py")
        return pd.DataFrame()

# 3. LOAD DATA
df = load_data()

# Validasi data
if df.empty:
    st.stop()

# 4. SIDEBAR FILTER
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Sesuaikan parameter di bawah untuk eksplorasi dinamis.")

# Filter Tahun
tahun_available = sorted(df['year'].unique())
selected_year = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=tahun_available,
    default=tahun_available,
    help="Pilih tahun yang ingin ditampilkan"
)
# Filter Kategori Produk
category_available = sorted(df['product_category_name'].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Pilih Kategori Produk:",
    options=category_available,
    default=[],
    help="Pilih kategori tertentu (kosongkan untuk semua)"
)
# Filter berdasarkan pilihan
df_filtered = df.copy()
if selected_year:
    df_filtered = df_filtered[df_filtered['year'].isin(selected_year)]
if selected_categories:
    df_filtered = df_filtered[df_filtered['product_category_name'].isin(selected_categories)]

# Informasi di sidebar
st.sidebar.markdown("-----")
st.sidebar.markdown("### 📊 Informasi Data")
st.sidebar.markdown(f"**Total Transaksi:** {df_filtered['order_id'].nunique():,}")
st.sidebar.markdown(f"**Total Pelanggan:** {df_filtered['customer_id'].nunique():,}")
st.sidebar.markdown(f"**Periode Data:** {df['year'].min()} - {df['year'].max()}")
st.sidebar.markdown("-----")
st.sidebar.markdown("**Dibuat oleh:** Assika Latifah Mercyana")

# 5. JUDUL DASHBOARD
st.title("📊 E-Commerce Customer Analytics Dashboard")
st.markdown("Dashboard ini menyajikan analisis tren transaksi, performa kategori produk, dan perilaku pelanggan.")
st.divider()

# 6. KEY PERFORMANCE INDICATORS (KPI)
st.subheader("📈 Key Performance Indicators (KPI)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = df_filtered['order_id'].nunique()
    st.metric("Total Transaksi", f"{total_orders:,}")

with col2:
    total_revenue = df_filtered['price'].sum()
    st.metric("Total Pendapatan", f"{total_revenue:,.0f}")

with col3:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.metric("Rata-rata Nilai Transaksi", f"{avg_order_value:,.0f}")

with col4:
    unique_customers = df_filtered['customer_id'].nunique()
    st.metric("Pelanggan Unik", f"{unique_customers:,}")

st.divider()

# 7. PERTANYAAN 1: TREN TRANSAKSI & PENDAPATAN PERIODE 2016-2018
st.header("Pertanyaan 1: Bagaimana tren pertumbuhan jumlah transaksi dan total pendapatan bulanan pada platform e-commerce selama periode 2016–2018, serta kapan terjadi puncak penjualan?")

# Agregasi bulanan
monthly_data = df_filtered.groupby(df_filtered['year_month']).agg(
    transaksi=('order_id', 'nunique'),
    pendapatan=('price', 'sum')
).reset_index()
monthly_data['tanggal'] = monthly_data['year_month'].dt.to_timestamp()
monthly_data['pendapatan_k'] = monthly_data['pendapatan'] / 1000

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_data['tanggal'], monthly_data['transaksi'], 
            marker='o', linewidth=2, markersize=6, color='steelblue')
    ax.set_xlabel('Bulan', fontsize=11)
    ax.set_ylabel('Jumlah Transaksi', fontsize=11)
    ax.set_title('Tren Jumlah Transaksi per Bulan', fontsize=13)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_data['tanggal'], monthly_data['pendapatan_k'], 
            marker='o', linewidth=2, markersize=6, color='coral')
    ax.set_xlabel('Bulan', fontsize=11)
    ax.set_ylabel('Pendapatan (Ribuan)', fontsize=11)
    ax.set_title('Tren Pendapatan per Bulan', fontsize=13)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Insight
with st.expander("Insight Pertanyaan 1", expanded=False):
    st.markdown("""
    - **Puncak tertinggi:** November 2017 (7.507 transaksi, pendapatan 1.003.862)
    - **Tren:** Meningkat dari awal periode hingga November 2017
    - **Korelasi:** Transaksi dan pendapatan bergerak searah
    """)
st.divider()

# 8. PERTANYAAN 2: KATEGORI PRODUK
st.header("Pertanyaan 2: Kategori produk apa yang memberikan kontribusi pendapatan terbesar setiap bulan, dan bagaimana pola musiman penjualannya selama periode 2016–2018?")

# Top 10 kategori berdasarkan pendapatan
category_revenue = df_filtered.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)

col1, col2 = st.columns([3, 2])

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis_r(np.linspace(0.1, 0.9, 10))
    bars = ax.barh(range(len(category_revenue)), category_revenue.values / 1000, color=colors)
    ax.set_yticks(range(len(category_revenue)))
    ax.set_yticklabels(category_revenue.index)
    ax.set_xlabel('Pendapatan (Ribuan)', fontsize=11)
    ax.set_title('Top 10 Kategori dengan Pendapatan Terbesar', fontsize=13)
    ax.invert_yaxis()
    
    for i, (bar, val) in enumerate(zip(bars, category_revenue.values / 1000)):
        ax.text(val + 5, bar.get_y() + bar.get_height()/2, f'{val:.0f}K', va='center', fontsize=9)
    
    st.pyplot(fig)

with col2:
    st.markdown("### Top 5 Kategori Produk")
    for i, (cat, val) in enumerate(category_revenue.head().items(), 1):
        st.markdown(f"{i}. **{cat}** : {val/1000:.0f}K")
    
    st.markdown("---")
    st.markdown("### Kontribusi Pendapatan")
    top5_sum = category_revenue.head(5).sum()
    total_sum = category_revenue.sum()
    st.metric("Top 5 Kategori", f"{(top5_sum / total_sum * 100):.1f}%", "dari total pendapatan")

# Pie chart top 5 vs lainnya
fig, ax = plt.subplots(figsize=(8, 6))
top5 = category_revenue.head(5)
lainnya = category_revenue[5:].sum()
plt.pie([top5.sum(), lainnya], labels=['Top 5 Kategori', 'Lainnya'], 
        autopct='%1.1f%%', colors=['#2E86AB', '#A3C4D9'], explode=(0.05, 0))
plt.title('Kontribusi Top 5 Kategori terhadap Total Pendapatan', fontsize=13)
st.pyplot(fig)

# Pola Musiman
st.subheader("Pola Musiman Top 5 Kategori")

top5_nama = category_revenue.head(5).index.tolist()
df_top5 = df_filtered[df_filtered['product_category_name'].isin(top5_nama)].copy()
df_top5['bulan'] = df_top5['order_purchase_timestamp'].dt.month

seasonal_data = df_top5.groupby(['bulan', 'product_category_name'])['price'].sum().reset_index()

fig, ax = plt.subplots(figsize=(12, 5))
for kategori in top5_nama:
    data_kategori = seasonal_data[seasonal_data['product_category_name'] == kategori]
    ax.plot(data_kategori['bulan'], data_kategori['price'] / 1000, 
            marker='o', linewidth=2, label=kategori)

ax.set_xlabel('Bulan (1=Januari, 12=Desember)', fontsize=11)
ax.set_ylabel('Pendapatan (Ribuan)', fontsize=11)
ax.set_title('Pola Musiman Pendapatan Top 5 Kategori', fontsize=13)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# Insight
with st.expander("Insight Pertanyaan 2", expanded=False):
    st.markdown(f"""
    - **Kategori terbesar:** {category_revenue.index[0]}
    - **Top 5 kategori menyumbang:** {(top5_sum / total_sum * 100):.1f}% dari total pendapatan
    - **Pola musiman:** Kategori hadiah (relogios_presentes) naik di bulan-bulan tertentu
    """)

st.divider()

# 9. ANALISIS LANJUTAN: RFM 
with st.expander("Analisis Lanjutan: Segmentasi Pelanggan (RFM)", expanded=False):
    st.markdown("### Segmentasi Pelanggan dengan Metode RFM")
    
    # Hitung RFM
    cutoff_date = df_filtered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = df_filtered.groupby('customer_id').agg(
        last_purchase=('order_purchase_timestamp', 'max'),
        Frequency=('order_id', 'nunique'),
        Monetary=('price', 'sum')
    ).reset_index()
    
    rfm['Recency'] = (cutoff_date - rfm['last_purchase']).dt.days
    rfm = rfm[['customer_id', 'Recency', 'Frequency', 'Monetary']]
    
    # Segmentasi sederhana
    def get_segment(row):
        if row['Frequency'] >= 3 and row['Monetary'] >= 500:
            return 'Champion'
        elif row['Frequency'] >= 2:
            return 'Loyal'
        elif row['Recency'] <= 90:
            return 'Potential'
        else:
            return 'At Risk'
    
    rfm['Segment'] = rfm.apply(get_segment, axis=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        segment_counts = rfm['Segment'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors_segment = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        bars = ax.bar(segment_counts.index, segment_counts.values, color=colors_segment[:len(segment_counts)])
        ax.set_xlabel('Segment', fontsize=11)
        ax.set_ylabel('Jumlah Pelanggan', fontsize=11)
        ax.set_title('Distribusi Segmentasi Pelanggan', fontsize=13)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with col2:
        st.markdown("### Insight Segmentasi")
        for seg, count in segment_counts.items():
            pct = count / len(rfm) * 100
            st.markdown(f"- **{seg}:** {count:,} pelanggan ({pct:.1f}%)")
        
        st.markdown("---")
        st.markdown("**Rekomendasi:**")
        st.markdown("- **Champion:** Program loyalitas eksklusif")
        st.markdown("- **At Risk:** Kampanye reaktivasi dengan diskon khusus")
        st.markdown("- **Potential:** Dorong repeat purchase")

st.divider()

# 12. RINGKASAN
with st.expander("📌 Executive Summary & Analysis Insight", expanded=False):
    st.markdown(f"""
    Berdasarkan observasi terhadap {total_orders:,} transaksi dari {unique_customers:,} pelanggan, ditemukan beberapa poin krusial:
    
    - **Performa Bisnis:** Puncak transaksi dan pendapatan terjadi pada November 2017, menunjukkan adanya potensi musiman yang perlu dimaksimalkan.
    
    - **Kategori Produk:** Top 5 kategori menyumbang 63,8% pendapatan. Kategori beleza_saude menjadi kontributor terbesar.
    
    - **Perilaku Pelanggan:** Mayoritas pelanggan hanya bertransaksi sekali (repeat purchase rendah). Segmentasi RFM menunjukkan perlu strategi retensi yang lebih agresif.
    
    - **Rekomendasi:** Fokus pada top 5 kategori, tingkatkan repeat purchase dengan program loyalitas, dan optimalkan promosi di bulan-bulan puncak.
    """)

# 13. FOOTER
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "© 2026 📊 Dashboard E-Commerce Analytics | Assika Latifah Mercyana"
    "</div>",
    unsafe_allow_html=True
)
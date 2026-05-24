# ─────────────────────────────────────────────
# IMPOR PUSTAKA
# ─────────────────────────────────────────────

# Pustaka pihak ketiga
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Pustaka bawaan Python
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Zonify — Retail Zone Compliance",
    layout="wide",  # Mengatur layout menjadi lebar penuh
    initial_sidebar_state="expanded"  # Sidebar dalam keadaan terbuka
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Font import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Root variables for colors */
    :root {
        --main-bg-color: #0f1117;
        --text-color: #e8eaed;
        --sidebar-bg-color: #161b27;
        --sidebar-border-color: #2a3245;
        --metric-bg-gradient: linear-gradient(135deg, #1a2236 0%, #1e2a40 100%);
        --metric-border-color: #2a3a5c;
        --section-header-border: #2a3a5c;
        --info-box-bg-gradient: linear-gradient(135deg, #0d1f3c 0%, #122040 100%);
        --info-box-border: #1e4080;
        --info-box-highlight: #4a90e2;
        --warning-box-bg-gradient: linear-gradient(135deg, #2d0d0d 0%, #3a1010 100%);
        --warning-box-border: #6b1a1a;
        --warning-box-highlight: #e05252;
    }

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: var(--main-bg-color);
        color: var(--text-color);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg-color);
        border-right: 1px solid var(--sidebar-border-color);
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: var(--metric-bg-gradient);
        border: 1px solid var(--metric-border-color);
        border-radius: 12px;
        padding: 16px 20px;
    }
    div[data-testid="metric-container"] label {
        color: #8b9bbf !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text-color) !important;
        font-size: 1.5rem !important;
        font-weight: 800;
        white-space: nowrap;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }

    /* Section header */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 28px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--section-header-border);
    }
    .section-header h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #a8c4ff;
        margin: 0;
        letter-spacing: 0.02em;
    }

    /* Info box */
    .insight-box {
        background: var(--info-box-bg-gradient);
        border: 1px solid var(--info-box-border);
        border-left: 4px solid var(--info-box-highlight);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0 16px 0;
        font-size: 0.88rem;
        color: #b8cef0;
        line-height: 1.6;
    }
    .insight-box strong { color: #7eb8ff; }

    /* Warning box */
    .violation-box {
        background: var(--warning-box-bg-gradient);
        border: 1px solid var(--warning-box-border);
        border-left: 4px solid var(--warning-box-highlight);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 10px 0 16px 0;
        font-size: 0.88rem;
        color: #f0b8b8;
        line-height: 1.6;
    }
    .violation-box strong { color: #ff8585; }

    /* Zone badge */
    .badge-red {
        background: #4a1515; color: #ff8585; padding: 3px 10px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        border: 1px solid #8b2020;
    }
    .badge-green {
        background: #0d3320; color: #5fd98a; padding: 3px 10px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        border: 1px solid #1a6640;
    }
    .badge-yellow {
        background: #3a2a00; color: #ffd166; padding: 3px 10px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        border: 1px solid #6b5000;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #8b9bbf;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4a90e2;
    }

    /* Hide default footer */
    footer { visibility: hidden; }

    /* Plotly chart background transparency */
    .js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """Hitung jarak dua koordinat GPS (meter) menggunakan Rumus Haversine."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def zone_label(pct_violation, mean=15.0, std=6.0):
    """Klasifikasi zona kritis berbasis Mean + Std — konsisten dengan pendekatan notebook.
    
    Threshold:
        Kritis   : pct > mean + std   (outlier atas)
        Waspada  : mean < pct ≤ mean + std
        Aman     : pct ≤ mean
    """
    threshold_kritis = mean + std
    if pct_violation > threshold_kritis:
        return "🔴 Zona Kritis"
    elif pct_violation > mean:
        return "🟡 Zona Waspada"
    else:
        return "🟢 Zona Aman"


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(20,28,48,0.6)",
    font=dict(family="Plus Jakarta Sans", color="#c8d4e8"),
    margin=dict(l=0, r=0, t=40, b=0),
)

COLOR_MAP = {"Indomaret": "#4a90e2", "Alfamart": "#e05252"}
KECAMATAN_COLOR = px.colors.qualitative.Set2


# ─────────────────────────────────────────────
# DATA LOADING (cached)
# ─────────────────────────────────────────────
_HERE = Path(__file__).parent  # root: dashboard/

@st.cache_data
def load_data():
    df_main = pd.read_csv(_HERE / "main_data.csv")
    df_pasar = pd.read_csv(_HERE.parent / "data" / "jaksel_pasar_final.csv")

    # Rename column agar konsisten
    df_main.rename(columns={"pelanggaran_<500m": "pelanggaran"}, inplace=True)

    # Boolean flag
    df_main["is_violation"] = df_main["pelanggaran"] == "Yes"

    # Tambah label zona per kecamatan
    kec_stats = (
        df_main.groupby("nama_kecamatan")
        .agg(
            total_minimarket=("nama_tempat", "count"),
            total_pelanggaran=("is_violation", "sum"),
            avg_jarak_m=("jarak_pasar_meter", "mean"),
            indomaret=("store", lambda x: (x == "Indomaret").sum()),
            alfamart=("store", lambda x: (x == "Alfamart").sum()),
        )
        .reset_index()
    )
    kec_stats["pct_pelanggaran"] = (
        kec_stats["total_pelanggaran"] / kec_stats["total_minimarket"] * 100
    ).round(1)
    # zona dihitung dinamis di luar load_data (bergantung radius_m & IQR)
    kec_stats["avg_jarak_km"] = (kec_stats["avg_jarak_m"] / 1000).round(2)

    return df_main, df_pasar, kec_stats


df_main, df_pasar, kec_stats = load_data()


def compute_kec_stats_dynamic(df_source, radius_m_val):
    """Hitung ulang kec_stats + zona IQR berdasarkan radius dinamis."""
    df_tmp = df_source.copy()
    df_tmp["is_violation"] = df_tmp["jarak_pasar_meter"] < radius_m_val

    ks = (
        df_tmp.groupby("nama_kecamatan")
        .agg(
            total_minimarket=("nama_tempat", "count"),
            total_pelanggaran=("is_violation", "sum"),
            avg_jarak_m=("jarak_pasar_meter", "mean"),
            indomaret=("store", lambda x: (x == "Indomaret").sum()),
            alfamart=("store", lambda x: (x == "Alfamart").sum()),
        )
        .reset_index()
    )
    ks["pct_pelanggaran"] = (
        ks["total_pelanggaran"] / ks["total_minimarket"] * 100
    ).round(1)
    ks["avg_jarak_km"] = (ks["avg_jarak_m"] / 1000).round(2)

    # Hitung threshold Mean + Std dari distribusi data aktual (konsisten dengan notebook)
    mean_pct = ks["pct_pelanggaran"].mean()
    std_pct = ks["pct_pelanggaran"].std()
    ks["zona"] = ks["pct_pelanggaran"].apply(lambda x: zone_label(x, mean_pct, std_pct))

    return ks, mean_pct, std_pct


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0 20px 0;">
            <div style="font-size:2.3rem; font-weight:800; color:#a8c4ff; letter-spacing:0.05em;">ZONIFY</div>
            <div style="font-size:0.72rem; color:#5a7090; font-weight:600; letter-spacing:0.1em; margin-top:2px;">
                SPATIAL AI · RETAIL COMPLIANCE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Radius slider — diletakkan di atas filter agar is_violation bisa dihitung ulang
    st.markdown("---")
    st.markdown("#### Batas Radius Zonasi")
    radius_m = st.slider("Radius (meter)", 100, 1000, 500, 50)

    st.markdown("---")
    st.markdown("#### Filter Data")

    # Filter kecamatan
    kecamatan_list = ["Semua Kecamatan"] + sorted(df_main["nama_kecamatan"].unique().tolist())
    selected_kecamatan = st.selectbox("Kecamatan", kecamatan_list)

    # Filter brand
    brand_options = ["Semua Brand", "Indomaret", "Alfamart"]
    selected_brand = st.selectbox("Brand Minimarket", brand_options)

    # Filter status zonasi — label menyesuaikan radius_m
    status_options = ["Semua Status", f"Melanggar (<{radius_m}m)", f"Aman (≥{radius_m}m)"]
    selected_status = st.selectbox("Status Zonasi", status_options)

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.72rem; color:#445566; line-height:1.7; text-align:center;">
            <strong style="color:#556677">Regulasi Acuan</strong><br>
            Perpres No. 112/2007<br>
            Perda DKI No. 2/2002<br>
            Kepgub DKI No. 44/2004<br><br>
            <strong style="color:#556677">CC26-PSU365</strong><br>
            Coding Camp 2026<br>DBS Foundation
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────

# [FIX] Hitung ulang is_violation berdasarkan radius_m yang dipilih user
df_main_dyn = df_main.copy()
df_main_dyn["is_violation"] = df_main_dyn["jarak_pasar_meter"] < radius_m

# [FIX] Hitung kec_stats dan IQR threshold secara dinamis
kec_stats, mean_zone, std_zone = compute_kec_stats_dynamic(df_main, radius_m)

df_filtered = df_main_dyn.copy()

if selected_kecamatan != "Semua Kecamatan":
    df_filtered = df_filtered[df_filtered["nama_kecamatan"] == selected_kecamatan]

if selected_brand != "Semua Brand":
    df_filtered = df_filtered[df_filtered["store"] == selected_brand]

# [FIX] Filter status menggunakan is_violation yang sudah dinamis
if "Melanggar" in selected_status:
    df_filtered = df_filtered[df_filtered["is_violation"] == True]
elif "Aman" in selected_status:
    df_filtered = df_filtered[df_filtered["is_violation"] == False]

# Re-calculate filtered kec_stats
kec_filtered = (
    df_filtered.groupby("nama_kecamatan")
    .agg(
        total_minimarket=("nama_tempat", "count"),
        total_pelanggaran=("is_violation", "sum"),
        avg_jarak_m=("jarak_pasar_meter", "mean"),
    )
    .reset_index()
)
kec_filtered["pct_pelanggaran"] = (
    kec_filtered["total_pelanggaran"] / kec_filtered["total_minimarket"] * 100
).round(1)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 20px 0 8px 0;">
        <h1 style="font-size:1.9rem; font-weight:800; color:#d0e4ff; margin:0; letter-spacing:-0.01em;">
            Zonify Command Center
        </h1>
        <p style="color:#5a7090; font-size:0.88rem; margin: 6px 0 0 0; font-weight:500;">
            Spatial AI for Retail Zone Compliance Mapping · Jakarta Selatan
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
total_minimarket = len(df_filtered)
total_pasar = len(df_pasar)
total_violation = df_filtered["is_violation"].sum()
pct_violation = round(total_violation / total_minimarket * 100, 1) if total_minimarket > 0 else 0
avg_jarak = round(df_filtered["jarak_pasar_meter"].mean(), 0) if total_minimarket > 0 else 0
indomaret_count = (df_filtered["store"] == "Indomaret").sum()
alfamart_count = (df_filtered["store"] == "Alfamart").sum()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Minimarket", f"{total_minimarket:,}", help="Jumlah minimarket (Alfamart + Indomaret) pada filter aktif")
with col2:
    st.metric("Pasar Tradisional", f"{total_pasar}", help="Jumlah pasar tradisional di Jakarta Selatan")
with col3:
    st.metric("Pelanggaran Zonasi", f"{int(total_violation)}",
              delta_color="inverse", help="Minimarket dalam radius <500m dari pasar tradisional")
with col4:
    st.metric("Rata-rata Jarak", f"{avg_jarak:,.0f} m", help="Rata-rata jarak minimarket ke pasar tradisional terdekat")
with col5:
    rasio = f"I: {indomaret_count} | A: {alfamart_count}"
    st.metric("Rasio Brand", rasio, help="Perbandingan jumlah Indomaret vs Alfamart")


# ─────────────────────────────────────────────
# TABS UTAMA
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Peta Distribusi",
    "Analisis EDA",
    "Zona Kritis",
    "Kalkulator Jarak",
    "Detail Data",
])


# ═══════════════════════════════════════════
# TAB 1 — PETA DISTRIBUSI SPASIAL
# ═══════════════════════════════════════════
with tab1:
    st.markdown(
        '<div class="section-header"><h2>Peta Distribusi Minimarket & Pasar Tradisional</h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="insight-box">Peta ini memvisualisasikan sebaran spasial minimarket (Alfamart & Indomaret) '
        'dan pasar tradisional di Jakarta Selatan. <strong>Titik merah</strong> menandai minimarket yang '
        f'<strong>melanggar aturan jarak &lt; {radius_m} m</strong> dari pasar tradisional. '
        '<strong>Titik biru/oranye</strong> adalah minimarket aman. <strong>Bintang hijau</strong> adalah pasar tradisional.</div>',
        unsafe_allow_html=True,
    )

    # Build scatter mapbox
    df_plot = df_filtered.copy()
    df_plot["status_label"] = df_plot.apply(
        lambda r: f"⚠️ MELANGGAR — {r['store']}" if r["is_violation"] else f"✅ Aman — {r['store']}",
        axis=1,
    )
    df_plot["color_group"] = df_plot.apply(
        lambda r: "🔴 Melanggar" if r["is_violation"] else (
            "🔵 Indomaret Aman" if r["store"] == "Indomaret" else "🟠 Alfamart Aman"
        ),
        axis=1,
    )
    df_plot["jarak_km"] = (df_plot["jarak_pasar_meter"] / 1000).round(2)

    color_discrete = {
        "🔴 Melanggar": "#e05252",
        "🔵 Indomaret Aman": "#4a90e2",
        "🟠 Alfamart Aman": "#f5a623",
    }

    fig_map = px.scatter_mapbox(
        df_plot,
        lat="latitude", lon="longitude",
        color="color_group",
        color_discrete_map=color_discrete,
        hover_name="nama_tempat",
        hover_data={
            "nama_kecamatan": True,
            "jarak_km": True,
            "pasar_terdekat": True,
            "status_label": True,
            "color_group": False,
            "latitude": False,
            "longitude": False,
        },
        labels={"jarak_km": "Jarak ke Pasar (km)", "pasar_terdekat": "Pasar Terdekat",
                "nama_kecamatan": "Kecamatan", "status_label": "Status"},
        zoom=11.2,
        center={"lat": -6.261, "lon": 106.810},
        height=520,
        mapbox_style="carto-darkmatter",
        size_max=8,
    )

    # Tambah titik pasar tradisional
    # Menambahkan data ke peta
    fig_map.add_trace(go.Scattermapbox(
        lat=df_pasar["latitude"],
        lon=df_pasar["longitude"],
        mode="markers",
        marker=dict(size=10, color="green"),
        name="🟢 Pasar Tradisional",
        hovertext=df_pasar["nama_tempat"].str.title(),
        hovertemplate="<b>%{hovertext}</b><br>Pasar Tradisional<extra></extra>",
    ))

    # Update layout peta
    fig_map.update_layout(
        title="Peta Zonasi",
        margin=dict(l=0, r=0, t=0, b=0),  # Pastikan hanya satu margin
        mapbox_style="carto-positron",
        mapbox=dict(
            center=dict(lat=-6.2, lon=106.8),  # Atur pusat peta
            zoom=12,  # Tingkat zoom awal
        ),
        uirevision="keep",  # Memastikan zoom tetap saat interaksi
    )

    # Tampilkan peta di Streamlit
    st.plotly_chart(fig_map, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 2 — ANALISIS EDA
# ═══════════════════════════════════════════
with tab2:
    st.markdown(
        '<div class="section-header"><h2>Exploratory Data Analysis — Spasial & Statistik</h2></div>',
        unsafe_allow_html=True,
    )

    # ── Q1: Distribusi brand per kecamatan ──
    st.markdown("#### Q1 · Persebaran & Rasio Ritel Modern per Kecamatan")
    st.markdown(
        '<div class="insight-box">'
        '<strong>Pertanyaan Bisnis:</strong> Bagaimana persebaran dan perbandingan rasio jumlah ritel modern '
        '(Alfamart & Indomaret) terhadap pasar tradisional di masing-masing kecamatan di Jakarta Selatan?'
        '</div>',
        unsafe_allow_html=True,
    )

    brand_kec = (
        df_filtered.groupby(["nama_kecamatan", "store"])["nama_tempat"]
        .count()
        .reset_index(name="jumlah")
    )
    fig_brand = px.bar(
        brand_kec,
        x="nama_kecamatan", y="jumlah", color="store",
        barmode="group",
        color_discrete_map=COLOR_MAP,
        labels={"nama_kecamatan": "Kecamatan", "jumlah": "Jumlah Minimarket", "store": "Brand"},
        title="Distribusi Indomaret vs Alfamart per Kecamatan",
        text_auto=True,
    )
    fig_brand.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_tickangle=-30,
        legend_title="Brand",
    )
    fig_brand.update_traces(textposition="outside", textfont_size=11)
    st.plotly_chart(fig_brand, use_container_width=True)

    # Rasio pasar:minimarket
    pasar_per_kec = df_pasar.groupby("nama_kecamatan")["nama_tempat"].count().reset_index(name="jumlah_pasar")
    mini_per_kec = df_filtered.groupby("nama_kecamatan")["nama_tempat"].count().reset_index(name="jumlah_minimarket")
    rasio_df = pd.merge(pasar_per_kec, mini_per_kec, on="nama_kecamatan", how="left").fillna(0)
    rasio_df["rasio"] = (rasio_df["jumlah_minimarket"] / rasio_df["jumlah_pasar"]).round(1)
    rasio_df = rasio_df.sort_values("rasio", ascending=True)

    fig_rasio = px.bar(
        rasio_df, x="rasio", y="nama_kecamatan", orientation="h",
        color="rasio",
        color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
        text="rasio",
        labels={"rasio": "Rasio Minimarket:Pasar", "nama_kecamatan": "Kecamatan"},
        title="Rasio Minimarket per 1 Pasar Tradisional per Kecamatan",
    )
    fig_rasio.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig_rasio.update_traces(textposition="outside", textfont_size=11)
    st.plotly_chart(fig_rasio, use_container_width=True)

    st.markdown(
        '<div class="insight-box"><strong>💡 Insight:</strong> Jagakarsa mencatat jumlah ritel modern tertinggi dengan total 102 gerai (54 Alfamart dan 48 Indomaret), menunjukkan tingginya aktivitas ekonomi dan penetrasi minimarket di wilayah tersebut, sementara Pasar Minggu memiliki rasio minimarket terhadap pasar tradisional paling tinggi yaitu sekitar 63 minimarket per 1 pasar tradisional, yang mengindikasikan dominasi ritel modern dan potensi ketidakseimbangan ekosistem perdagangan lokal; di sisi lain, Tebet dan Pancoran memiliki rasio yang relatif lebih rendah sehingga keseimbangan antara pasar tradisional dan ritel modern masih lebih terjaga.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Q2: Distribusi jarak ──
    st.markdown("#### Q2 · Distribusi Jarak Minimarket ke Pasar Tradisional")
    st.markdown(
        '<div class="insight-box">'
        '<strong>Pertanyaan Bisnis:</strong> Berapa jumlah dan persentase ritel modern yang secara spasial '
        f'terindikasi melanggar aturan zonasi (berada dalam radius &lt; {radius_m} m dari pasar tradisional)?'
        '</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([2, 1])
    with col_a:
        fig_hist = px.histogram(
            df_filtered,
            x="jarak_pasar_meter",
            nbins=40,
            color="store",
            color_discrete_map=COLOR_MAP,
            barmode="overlay",
            labels={"jarak_pasar_meter": "Jarak ke Pasar Terdekat (meter)", "count": "Frekuensi"},
            title="Distribusi Jarak Minimarket ke Pasar Tradisional",
            opacity=0.8,
        )
        fig_hist.add_vline(
            x=radius_m, line_dash="dash", line_color="#e05252", line_width=2,
            annotation_text=f"Batas {radius_m}m", annotation_position="top right",
            annotation_font_color="#e05252",
        )
        fig_hist.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        # Dynamic recalculate based on slider radius
        n_viol_dyn = (df_filtered["jarak_pasar_meter"] < radius_m).sum()
        pct_viol_dyn = round(n_viol_dyn / len(df_filtered) * 100, 1) if len(df_filtered) > 0 else 0
        n_aman = len(df_filtered) - n_viol_dyn

        fig_pie = px.pie(
            values=[n_viol_dyn, n_aman],
            names=[f"Melanggar\n(<{radius_m}m)", f"Aman\n(≥{radius_m}m)"],
            color_discrete_sequence=["#e05252", "#4a90e2"],
            title=f"Status Zonasi (radius {radius_m}m)",
            hole=0.55,
        )
        fig_pie.update_layout(**PLOTLY_LAYOUT, showlegend=True)
        fig_pie.update_traces(textfont_size=12, textposition="outside")
        st.plotly_chart(fig_pie, use_container_width=True)

        if pct_viol_dyn > 0:
            st.markdown(
                f'<div class="violation-box"><strong>{n_viol_dyn} minimarket ({pct_viol_dyn}%)</strong> '
                f'berada dalam radius &lt;{radius_m}m dari pasar tradisional dan '
                f'<strong>berpotensi melanggar regulasi zonasi</strong>.</div>',
                unsafe_allow_html=True,
            )
    n_viol_q2 = (df_filtered["jarak_pasar_meter"] < radius_m).sum()
    pct_viol_q2 = round(n_viol_q2 / len(df_filtered) * 100, 1) if len(df_filtered) > 0 else 0
    pct_aman_q2 = round(100 - pct_viol_q2, 1)
    st.markdown(
        f'<div class="insight-box"><strong>💡 Insight:</strong> Sebanyak {n_viol_q2} minimarket atau sekitar {pct_viol_q2}% '
        f'dari total ritel modern terindikasi berada dalam radius kurang dari {radius_m} meter dari pasar tradisional, '
        f'sehingga berpotensi melanggar aturan zonasi, sedangkan {pct_aman_q2}% lainnya berada pada jarak aman '
        f'(&gt;{radius_m} m). Distribusi jarak juga menunjukkan sebagian besar minimarket terkonsentrasi pada rentang '
        f'700–1500 meter dari pasar tradisional, namun masih terdapat sejumlah gerai yang berada sangat dekat dengan '
        f'pasar sehingga berpotensi meningkatkan persaingan langsung dengan pelaku ekonomi tradisional.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Q4: Dominasi brand di zona merah ──
    st.markdown("#### Q4 · Brand Dominan di Zona Pelanggaran")
    st.markdown(
        f'<div class="insight-box">'
        f'<strong>Pertanyaan Bisnis:</strong> Di antara Alfamart dan Indomaret, jenis store mana yang '
        f'lebih mendominasi di zona merah (pelanggaran &lt;{radius_m}m)?</div>',
        unsafe_allow_html=True,
    )

    viol_brand = (
        df_filtered[df_filtered["is_violation"]]
        .groupby("store")["nama_tempat"]
        .count()
        .reset_index(name="jumlah_pelanggaran")
    )
    all_brand = (
        df_filtered.groupby("store")["nama_tempat"]
        .count()
        .reset_index(name="total")
    )
    brand_compare = pd.merge(all_brand, viol_brand, on="store", how="left").fillna(0)
    brand_compare["pct_pelanggaran"] = (
        brand_compare["jumlah_pelanggaran"] / brand_compare["total"] * 100
    ).round(1)

    col_p, col_q = st.columns(2)
    with col_p:
        fig_brand_viol = px.bar(
            brand_compare, x="store", y="jumlah_pelanggaran",
            color="store",
            color_discrete_map=COLOR_MAP,
            text="jumlah_pelanggaran",
            labels={"store": "Brand", "jumlah_pelanggaran": "Jumlah Pelanggaran"},
            title="Jumlah Pelanggaran per Brand",
        )
        fig_brand_viol.update_layout(**PLOTLY_LAYOUT)
        fig_brand_viol.update_traces(textposition="outside")
        st.plotly_chart(fig_brand_viol, use_container_width=True)

    with col_q:
        fig_pct_brand = px.bar(
            brand_compare, x="store", y="pct_pelanggaran",
            color="store",
            color_discrete_map=COLOR_MAP,
            text=brand_compare["pct_pelanggaran"].astype(str) + "%",
            labels={"store": "Brand", "pct_pelanggaran": "% Pelanggaran dari Total"},
            title="Persentase Pelanggaran per Brand",
        )
        fig_pct_brand.update_layout(**PLOTLY_LAYOUT)
        fig_pct_brand.update_traces(textposition="outside")
        st.plotly_chart(fig_pct_brand, use_container_width=True)
    if len(brand_compare) >= 2:
        bc = brand_compare.set_index("store")
        alf_viol = int(bc.loc["Alfamart", "jumlah_pelanggaran"]) if "Alfamart" in bc.index else 0
        ind_viol = int(bc.loc["Indomaret", "jumlah_pelanggaran"]) if "Indomaret" in bc.index else 0
        alf_pct = bc.loc["Alfamart", "pct_pelanggaran"] if "Alfamart" in bc.index else 0
        ind_pct = bc.loc["Indomaret", "pct_pelanggaran"] if "Indomaret" in bc.index else 0
    else:
        alf_viol = ind_viol = alf_pct = ind_pct = 0
    st.markdown(
        f'<div class="insight-box"><strong>💡 Insight:</strong> Alfamart dan Indomaret memiliki jumlah pelanggaran '
        f'yang hampir seimbang di zona merah (&lt;{radius_m} m), dengan Alfamart mencatat {alf_viol} gerai dan '
        f'Indomaret {ind_viol} gerai. Namun, secara persentase terhadap total store masing-masing brand, '
        f'Alfamart memiliki tingkat pelanggaran lebih tinggi yaitu sekitar {alf_pct}%, dibandingkan Indomaret '
        f'sebesar {ind_pct}%, sehingga Alfamart relatif lebih dominan dalam zona yang berpotensi melanggar '
        f'regulasi proximity terhadap pasar tradisional.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Q5: Rata-rata jarak proximity ──
    st.markdown("#### Q5 · Rata-rata Jarak Proximity per Kecamatan")
    avg_jarak_kec = (
        df_filtered.groupby(["nama_kecamatan", "store"])["jarak_pasar_meter"]
        .mean()
        .reset_index()
    )
    avg_jarak_kec["jarak_km"] = (avg_jarak_kec["jarak_pasar_meter"] / 1000).round(2)
    avg_jarak_kec = avg_jarak_kec.sort_values("jarak_pasar_meter")

    fig_avg = px.bar(
        avg_jarak_kec, x="jarak_km", y="nama_kecamatan", color="store",
        barmode="group", orientation="h",
        color_discrete_map=COLOR_MAP,
        text="jarak_km",
        labels={"jarak_km": "Rata-rata Jarak (km)", "nama_kecamatan": "Kecamatan", "store": "Brand"},
        title="Rata-rata Jarak Minimarket ke Pasar Tradisional Terdekat (km)",
    )
    fig_avg.add_vline(
        x=radius_m / 1000, line_dash="dash", line_color="#e05252",
        annotation_text=f"Batas {radius_m}m", annotation_position="top right",
        annotation_font_color="#e05252",
    )
    fig_avg.update_layout(**PLOTLY_LAYOUT)
    fig_avg.update_traces(textposition="outside", textfont_size=10)
    st.plotly_chart(fig_avg, use_container_width=True)

    st.markdown(
        '<div class="insight-box"><strong>💡 Insight:</strong> Kebayoran Lama memiliki rata-rata jarak minimarket terhadap pasar tradisional paling tinggi, mencapai sekitar 1.66–1.89 km, menunjukkan persebaran ritel modern yang relatif jauh dan lebih aman dari pasar tradisional. Sebaliknya, Mampang Prapatan, Tebet, dan Pancoran memiliki rata-rata jarak paling rendah, berkisar 0.66–1.02 km, yang menandakan kedekatan spasial lebih tinggi antara minimarket dan pasar tradisional. Meskipun seluruh kecamatan masih berada di atas batas zonasi 500 meter secara rata-rata, beberapa wilayah dengan jarak rata-rata rendah berpotensi memiliki konsentrasi pelanggaran lebih besar pada titik-titik tertentu.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
# TAB 3 — ZONA KRITIS
# ═══════════════════════════════════════════
with tab3:
    st.markdown(
        '<div class="section-header"><h2>Analisis Zona Kritis & Oversaturasi</h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="insight-box">'
        '<strong>Pertanyaan Bisnis (Q3 & Q6):</strong> Kecamatan mana yang berada dalam tingkat ancaman '
        'tertinggi bagi pasar tradisional? Apakah terdapat kecamatan yang sebaran ritel modernnya sudah '
        'mencapai titik jenuh (oversaturated)?</div>',
        unsafe_allow_html=True,
    )

    # Ranking kecamatan
    kec_rank = kec_stats.copy().sort_values("total_pelanggaran", ascending=False)

    col_r1, col_r2 = st.columns([1.2, 1])

    with col_r1:
        fig_zone = px.bar(
            kec_rank, x="total_pelanggaran", y="nama_kecamatan",
            orientation="h",
            color="pct_pelanggaran",
            color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
            text="total_pelanggaran",
            labels={
                "total_pelanggaran": "Jumlah Pelanggaran",
                "nama_kecamatan": "Kecamatan",
                "pct_pelanggaran": "% Pelanggaran",
            },
            title="🔴 Ranking Kecamatan — Tingkat Ancaman Terhadap Pasar Tradisional",
        )
        fig_zone.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True)
        fig_zone.update_traces(textposition="outside")
        st.plotly_chart(fig_zone, use_container_width=True)

    with col_r2:
        fig_scatter_zone = px.scatter(
            kec_rank,
            x="avg_jarak_km", y="pct_pelanggaran",
            size="total_minimarket",
            color="zona",
            color_discrete_map={
                "🔴 Zona Kritis": "#e05252",
                "🟡 Zona Waspada": "#f5c518",
                "🟢 Zona Aman": "#2ecc71",
            },
            hover_name="nama_kecamatan",
            text="nama_kecamatan",
            labels={
                "avg_jarak_km": "Rata-rata Jarak ke Pasar (km)",
                "pct_pelanggaran": "% Pelanggaran Zonasi",
                "total_minimarket": "Total Minimarket",
                "zona": "Zona",
            },
            title="Bubble Chart — Jarak vs % Pelanggaran per Kecamatan",
        )
        fig_scatter_zone.add_hline(y=mean_zone + std_zone, line_dash="dash", line_color="#e05252",
                                   annotation_text=f"Threshold Kritis (mean+std={mean_zone + std_zone:.1f}%)")
        fig_scatter_zone.add_hline(y=mean_zone, line_dash="dot", line_color="#f5c518",
                                   annotation_text=f"Threshold Waspada (mean={mean_zone:.1f}%)")
        fig_scatter_zone.update_traces(textposition="top center", textfont_size=9)
        fig_scatter_zone.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_scatter_zone, use_container_width=True)

    # Tabel zona kritis
    st.markdown("#### Tabel Ranking Zona Kritis")
    kec_rank_display = kec_rank[[
        "nama_kecamatan", "total_minimarket", "total_pelanggaran",
        "pct_pelanggaran", "avg_jarak_km", "zona"
    ]].copy()
    kec_rank_display.columns = [
        "Kecamatan", "Total Minimarket", "Pelanggaran",
        "% Pelanggaran", "Avg Jarak (km)", "Status Zona"
    ]
    kec_rank_display = kec_rank_display.reset_index(drop=True)
    kec_rank_display.index = kec_rank_display.index + 1

    def highlight_zona(row):
        if "Kritis" in str(row["Status Zona"]):
            return ["background-color: #3a1010; color: #ff8585"] * len(row)
        elif "Waspada" in str(row["Status Zona"]):
            return ["background-color: #3a2a00; color: #ffd166"] * len(row)
        else:
            return ["background-color: #0a2a15; color: #5fd98a"] * len(row)

    st.dataframe(
        kec_rank_display.style.apply(highlight_zona, axis=1),
        use_container_width=True,
        height=380,
    )
    st.markdown(
    '<div class="insight-box"><strong>💡 Insight:</strong> Pesanggrahan dan Mampang Prapatan '
    'teridentifikasi sebagai zona paling kritis karena memiliki tingkat pelanggaran zonasi tertinggi '
    'serta jarak minimarket yang relatif dekat dengan pasar tradisional, sehingga mengindikasikan '
    'potensi oversaturasi ritel modern dan meningkatnya tekanan kompetitif terhadap pedagang lokal. '
    'Sebaliknya, Kebayoran Lama dan Pasar Minggu menunjukkan kondisi paling aman dan seimbang dengan '
    'tingkat pelanggaran rendah serta rata-rata jarak minimarket yang lebih jauh dari pasar tradisional. '
    'Sementara itu, Setiabudi, Pancoran, dan Kebayoran Baru berada pada kategori “zona waspada” karena '
    'mulai menunjukkan peningkatan kedekatan spasial dan potensi kompetisi apabila ekspansi ritel modern '
    'terus bertambah tanpa pengendalian zonasi yang ketat.</div>',
    unsafe_allow_html=True,
)

    st.markdown("---")

    # Q7: Profil kecamatan ideal
    st.markdown("#### Q7 · Profil Kecamatan 'Ideal' — Harmoni Ritel & Pasar Tradisional")
    st.markdown(
        '<div class="insight-box">'
        '<strong>Pertanyaan Bisnis:</strong> Bagaimana profil kecamatan "ideal" di mana ritel modern dan '
        'pasar tradisional dapat berdampingan secara harmonis?</div>',
        unsafe_allow_html=True,
    )

    ideal_kec = kec_stats[kec_stats["zona"] == "🟢 Zona Aman"].sort_values("avg_jarak_km", ascending=False)
    if not ideal_kec.empty:
        fig_ideal = px.bar(
            ideal_kec, x="nama_kecamatan", y=["indomaret", "alfamart"],
            barmode="stack",
            color_discrete_map={"indomaret": "#4a90e2", "alfamart": "#e05252"},
            labels={"nama_kecamatan": "Kecamatan", "value": "Jumlah Minimarket", "variable": "Brand"},
            title="Kecamatan 'Aman' — Komposisi Ritel (Zona Harmonis)",
            text_auto=True,
        )
        fig_ideal.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_ideal, use_container_width=True)
        st.markdown(
            '<div class="insight-box"><strong>💡 Insight:</strong> Kebayoran Lama, Pasar Minggu, Jagakarsa, '
    'Cilandak, dan Tebet dapat dikategorikan sebagai kecamatan dengan ekosistem ritel yang relatif ideal '
    'karena memiliki keseimbangan yang lebih baik antara minimarket modern dan pasar tradisional, '
    'ditandai dengan tingkat pelanggaran yang rendah hingga moderat serta jarak proximity yang relatif aman. '
    'Jagakarsa menjadi contoh menarik karena meskipun memiliki jumlah minimarket tertinggi, persebarannya '
    'masih cukup terkendali secara spasial. Sementara itu, Kebayoran Lama dan Pasar Minggu menunjukkan '
    'kondisi paling harmonis karena memiliki rata-rata jarak minimarket yang tinggi dan tingkat pelanggaran '
    'yang rendah, sehingga interaksi antara ritel modern dan pasar tradisional cenderung lebih sehat dan '
    'tidak terlalu kompetitif secara langsung.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════
# TAB 4 — KALKULATOR JARAK
# ═══════════════════════════════════════════
with tab4:
    st.markdown(
        '<div class="section-header"><h2>Kalkulator Jarak Otomatis (Haversine Formula)</h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="insight-box">'
        'Masukkan koordinat calon minimarket baru. Sistem akan menghitung jarak ke '
        '<strong>seluruh pasar tradisional</strong> di Jakarta Selatan menggunakan '
        '<strong>Rumus Haversine</strong> dan mengeluarkan status kepatuhan zonasi secara instan.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Tentang Rumus Haversine", expanded=False):
        st.markdown("""
        Rumus Haversine menghitung jarak garis lurus antara dua titik koordinat GPS di permukaan bumi:

        ```
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        d = 2R × arctan2(√a, √(1−a))
        ```
        Dimana **R = 6.371.000 meter** (jari-jari bumi). Hasil jarak bersifat absolut (bird-eye distance),
        bukan jarak jalan. Ini adalah standar internasional untuk perhitungan jarak geospasial.
        """)

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        lat_input = st.number_input(
            "Latitude Calon Minimarket",
            value=-6.250000, min_value=-6.40, max_value=-6.10,
            format="%.6f", step=-0.000001,
            help="Contoh: -6.2607 (Jakarta Selatan sekitar -6.1 s/d -6.4)"
        )
        # lat_input = -lat_abs_input
        # st.caption(f"📍 Koordinat aktual: **{lat_input:.6f}**")
    with col_in2:
        lon_input = st.number_input(
            "Longitude Calon Minimarket",
            value=106.800000, min_value=106.65, max_value=106.95,
            format="%.6f", step=0.000001,
            help="Contoh: 106.7899 (Jakarta Selatan sekitar 106.7 s/d 106.9)"
        )

    nama_calon = st.text_input("Nama Calon Minimarket (opsional)", placeholder="Contoh: Alfamart Jl. Kemang Raya")

    if st.button("Hitung Jarak & Cek Zonasi", type="primary", use_container_width=True):
        results = []
        for _, row in df_pasar.iterrows():
            dist = haversine(lat_input, lon_input, row["latitude"], row["longitude"])
            results.append({
                "Pasar Tradisional": row["nama_tempat"].title(),
                "Kecamatan": row["nama_kecamatan"],
                "Jarak (meter)": round(dist, 1),
                "Jarak (km)": round(dist / 1000, 3),
                "Status": "⚠️ MELANGGAR" if dist < radius_m else "✅ Aman",
            })

        df_result = pd.DataFrame(results).sort_values("Jarak (meter)")
        nearest = df_result.iloc[0]
        min_dist = nearest["Jarak (meter)"]
        is_viol = min_dist < radius_m

        # Hasil utama
        if is_viol:
            st.markdown(
                f'<div class="violation-box">'
                f'<strong>⛔ STATUS: DITOLAK / MELANGGAR ATURAN ZONASI</strong><br><br>'
                f'Calon minimarket <strong>"{nama_calon or "ini"}"</strong> berada hanya '
                f'<strong>{min_dist:,.0f} meter</strong> dari '
                f'<strong>{nearest["Pasar Tradisional"]}</strong> ({nearest["Kecamatan"]}).<br>'
                f'Jarak minimal yang diwajibkan regulasi adalah <strong>{radius_m} meter</strong>.'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="insight-box">'
                f'<strong>✅ STATUS: AMAN / MEMENUHI ATURAN ZONASI</strong><br><br>'
                f'Calon minimarket <strong>"{nama_calon or "ini"}"</strong> berjarak '
                f'<strong>{min_dist:,.0f} meter</strong> dari pasar terdekat '
                f'(<strong>{nearest["Pasar Tradisional"]}</strong>).<br>'
                f'Jarak ini memenuhi syarat minimal <strong>{radius_m} meter</strong>.'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Tabel semua pasar
        st.markdown("##### Jarak ke Semua Pasar Tradisional di Jakarta Selatan")

        def color_status(val):
            if "MELANGGAR" in str(val):
                return "background-color: #3a1010; color: #ff8585; font-weight:700"
            elif "Aman" in str(val):
                return "background-color: #0a2a15; color: #5fd98a"
            return ""

        # st.dataframe(
        #     df_result.style.applymap(color_status, subset=["Status"]),
        #     use_container_width=True,
        #     height=420,
        # )
        st.dataframe(
            df_result.style.map(color_status, subset=["Status"]),
            use_container_width=True,
            height=420,
        )
        
        # Mini-map lokasi
        fig_calc_map = go.Figure()
        fig_calc_map.add_trace(go.Scattermapbox(
            lat=df_pasar["latitude"], lon=df_pasar["longitude"],
            mode="markers", marker=dict(size=12, color="#5fd98a"),
            name="Pasar Tradisional",
            text=df_pasar["nama_tempat"].str.title(),
            hovertemplate="<b>%{text}</b><extra>Pasar Tradisional</extra>",
        ))
        fig_calc_map.add_trace(go.Scattermapbox(
            lat=[lat_input], lon=[lon_input],
            mode="markers", marker=dict(size=16, color="#e05252" if is_viol else "#4a90e2"),
            name=f"Calon Minimarket ({nama_calon or 'Input'})",
            hovertemplate=f"<b>{nama_calon or 'Calon Minimarket'}</b><br>{min_dist:,.0f}m ke pasar terdekat<extra></extra>",
        ))
        fig_calc_map.update_layout(
            mapbox=dict(style="carto-darkmatter", zoom=12,
                        center={"lat": lat_input, "lon": lon_input}),
            **PLOTLY_LAYOUT,
            height=380,
            legend=dict(bgcolor="rgba(15,20,35,0.85)", bordercolor="#2a3a5c", borderwidth=1),
        )
        st.plotly_chart(fig_calc_map, use_container_width=True)


# ═══════════════════════════════════════════
# TAB 5 — DETAIL DATA
# ═══════════════════════════════════════════
with tab5:
    st.markdown(
        '<div class="section-header"><h2>Detail Dataset Minimarket</h2></div>',
        unsafe_allow_html=True,
    )

    # Stats ringkas
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Total Baris Data", f"{len(df_filtered):,}")
    with col_s2:
        st.metric("Min Jarak ke Pasar", f"{df_filtered['jarak_pasar_meter'].min():,.1f} m")
    with col_s3:
        st.metric("Max Jarak ke Pasar", f"{df_filtered['jarak_pasar_meter'].max():,.1f} m")

    # Boxplot distribusi jarak per kecamatan
    fig_box = px.box(
        df_filtered,
        x="nama_kecamatan", y="jarak_pasar_meter",
        color="store", color_discrete_map=COLOR_MAP,
        labels={"nama_kecamatan": "Kecamatan", "jarak_pasar_meter": "Jarak ke Pasar (meter)", "store": "Brand"},
        title="Boxplot Distribusi Jarak per Kecamatan (Indomaret vs Alfamart)",
    )
    # fig_box.add_hline(y=500, line_dash="dash", line_color="#e05252",
    #                   annotation_text="Batas 500m Zonasi")
    fig_box.add_hline(y=radius_m, line_dash="dash", line_color="#e05252",
                      annotation_text=f"Batas {radius_m}m Zonasi")
    fig_box.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-30)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("##### Tabel Data Lengkap")
    display_cols = [
        "nama_tempat", "store", "nama_kecamatan", "nama_kelurahan",
        "jarak_pasar_meter", "pasar_terdekat", "pelanggaran",
        "rating_tempat", "user_ratings_total",
    ]
    df_display = df_filtered[display_cols].copy()
    df_display.columns = [
        "Nama Minimarket", "Brand", "Kecamatan", "Kelurahan",
        "Jarak ke Pasar (m)", "Pasar Terdekat", "Status Pelanggaran",
        "Rating", "Total Rating",
    ]

    def style_pelanggaran(val):
        if val == "Yes":
            return "background-color:#3a1010; color:#ff8585; font-weight:700"
        return "background-color:#0a2a15; color:#5fd98a"

    # st.dataframe(
    #     df_display.style.applymap(style_pelanggaran, subset=["Status Pelanggaran"]),
    #     use_container_width=True,
    #     height=480,
    # )
    st.dataframe(
        df_display.style.map(style_pelanggaran, subset=["Status Pelanggaran"]),
        use_container_width=True,
        height=480,
    )
    st.download_button(
        label="⬇️ Download Data (CSV)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="zonify_filtered_data.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#3a4a6a; font-size:0.78rem; padding: 8px 0 16px 0;">
        <strong style="color:#4a6090">Zonify Dashboard</strong> · 
        Spatial AI for Retail Zone Compliance Mapping · Jakarta Selatan<br>
        Tim CC26-PSU365 | Coding Camp 2026 powered by DBS Foundation<br>
        Regulasi: Perpres No. 112/2007 · Perda DKI No. 2/2002 · Kepgub DKI No. 44/2004
    </div>
    """,
    unsafe_allow_html=True,
)

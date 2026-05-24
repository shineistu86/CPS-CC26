# 🗺️ Zonify — Retail Zone Compliance Dashboard

**Proyek Capstone CC26-PSU365 | Coding Camp 2026 powered by DBS Foundation**

Dashboard interaktif berbasis Streamlit untuk menganalisis kepatuhan jarak 500 meter antara ritel modern (Alfamart & Indomaret) dan pasar tradisional di **Jakarta Selatan** berdasarkan data geospasial per tahun 2026.

---

## Setup Environment - Anaconda

```
conda create --name zonify-ds python=3.11
conda activate zonify-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir zonify-dashboard
cd zonify-dashboard
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```
streamlit run dashboard/dashboard.py
```

---

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── DATA_MINIMARKET_ZONASI_FINAL.csv
│   ├── jaksel_pasar_final.csv
│   └── jaksel_retail_final_v3.csv
├── README.md
├── requirements.txt
└── url.txt
```

---

## 🌐 Link Dashboard

Lihat `url.txt` untuk link deployment Streamlit Cloud.

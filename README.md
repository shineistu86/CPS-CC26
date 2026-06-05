# Zonify - Smart Retail Zoning Intelligence System

Zonify membuat sebuah pengembangan dari WebGIS Kabupaten Garut. Yaitu pendeteksian kejenuhan wilayah dan menginformasikan jumlah retail disekitarnya, serta rekomendasi koordinat yang dapat dipertimbangkan. Artinya, selain user dapat mengetahui jarak suatu retail sudah aman/melanggar, user juga dapat membuat suatu keputusan bahwa suatu retail berada di wilayah yang aman atau tidak.

## Struktur Repositori

Proyek ini diorganisasikan ke dalam beberapa direktori utama:

```text
CPS-CC26
 ┣ api/                  # Backend API Service
 ┣ data/                 # Dataset (Mentah & Bersih) serta Data Dictionary
 ┣ models/               # Model Machine Learning & Scaler yang telah dilatih
 ┣ notebooks/            # Jupyter Notebooks untuk eksperimen & riset
 ┣ outputs/              # Hasil visualisasi visual (PNG) dan peta spasial (HTML)
 ┣ zonify-streamlit/     # Source code Dashboard interaktif berbasis Streamlit
 ┣ .gitignore            # Konfigurasi file yang diabaikan oleh Git
 ┗ README.md             # Dokumentasi utama repositori

# 01_DOKUMEN_UTAMA — Direktori Laporan Akhir

Folder ini disiapkan sebagai lokasi keluaran dokumen laporan utama **System Requirement Specification (SRS) & System Architecture SiHADIR**.

> **Catatan Repository:** File biner laporan akhir (`.pdf` / `.docx`) dikumpulkan secara terpisah melalui portal pengumpulan tugas (LMS) dan di-ignore dari Git (`.gitignore`) agar repository tetap bersih dan berfokus pada kode model, spesifikasi sumber, serta skrip verifikasi.

---

## Cara Merakit / Generate Ulang Dokumen Laporan Utama

Dokumen laporan utama dirakit secara otomatis dari berkas-berkas Markdown di `../02_DOKUMENTASI_SUMBER/` (`S1` s.d. `S10`) dan gambar-gambar di `../04_DIAGRAM_DAN_VISUALISASI/` menggunakan skrip `../05_BUKTI_DAN_PENDUKUNG/build_report.py`.

### 1. Generate Laporan HTML
Dari root repository, jalankan:
```bash
python 05_BUKTI_DAN_PENDUKUNG/build_report.py
```
File HTML siap cetak akan dihasilkan di:
`05_BUKTI_DAN_PENDUKUNG/_build/RSK_FINAL.html`

### 2. Generate Laporan HTML + PDF Sekaligus
Jika di komputer terpasang Google Chrome atau Microsoft Edge, jalankan dengan 2 argumen (path HTML dan path PDF tujuan):
```bash
python 05_BUKTI_DAN_PENDUKUNG/build_report.py 05_BUKTI_DAN_PENDUKUNG/_build/RSK_FINAL.html 01_DOKUMEN_UTAMA/SiHADIR_Final_SRS_Architecture.pdf
```
Skrip akan otomatis memanggil browser dalam mode *headless* untuk merender seluruh halaman, tabel, diagram arsitektur, dan screenshot MATLAB System Composer menjadi file PDF siap kumpul di folder `01_DOKUMEN_UTAMA/` ini.

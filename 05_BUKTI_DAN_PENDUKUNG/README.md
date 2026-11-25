# 05_BUKTI_DAN_PENDUKUNG — Skrip Verifikasi, Perakit Laporan, & Bukti Uji

Folder ini menyimpan perangkat lunak pendukung (Python), log bukti eksekusi verifikasi model MATLAB, serta paket bundel untuk menjalankan model di MATLAB Online.

---

## Daftar Berkas

| Berkas | Fungsi Utama |
| :--- | :--- |
| `check_consistency.py` | **Pemeriksa Otomatis RTM & Traceability**: Memvalidasi `../02_DOKUMENTASI_SUMBER/RTM_SiHADIR.csv` terhadap ruang ID `SN-01..13`, `UC-01..12`, `F1.1..F12`, `C1.1..C6.3`, `IF-*`, distribusi tipe requirement, metode verifikasi, prioritas, dan angka terukur pada Acceptance Criteria. |
| `build_report.py` | **Perakit Laporan Otomatis (HTML & PDF)**: Menggabungkan `S1`–`S10` dari `02_DOKUMENTASI_SUMBER/`, menyisipkan seluruh diagram dari `04_DIAGRAM_DAN_VISUALISASI/`, membuat sampul, kendali dokumen, serta daftar isi otomatis. Dilengkapi *fallback* Markdown parser bawaan (tanpa wajib `pip install markdown`). |
| `S10_evidence.txt` | **Transkrip Bukti Verifikasi MATLAB R2026b**: Output asli dari eksekusi `run_sihadir_checks.m` yang membuktikan **15/15 pemeriksaan spesifikasi LULUS** dan **9/9 pemeriksaan model `.slx` LULUS**. |
| `SiHADIR_MATLAB_Online.zip` | **Paket Bundel Portabel**: Berisi ke-11 skrip `.m` terbaru dari `03_MODEL_MATLAB/` beserta `RTM_SiHADIR.csv` dalam satu arsip `.zip` datar — siap di-upload dan dijalankan langsung di **MATLAB Online** jika ingin mendemokan pembuatan `.slx` di komputer yang tidak memiliki MATLAB lokal. |

---

## Cara Menjalankan & Oprek Skrip

### 1. Menjalankan Pemeriksa Konsistensi RTM (`check_consistency.py`)
Dapat dijalankan dari root repository maupun langsung dari dalam folder `05_BUKTI_DAN_PENDUKUNG/`:
```bash
python 05_BUKTI_DAN_PENDUKUNG/check_consistency.py
```
Atau dengan menunjuk file CSV tertentu:
```bash
python 05_BUKTI_DAN_PENDUKUNG/check_consistency.py 02_DOKUMENTASI_SUMBER/RTM_SiHADIR.csv
```
- **Exit code `0`**: Seluruh 9 kategori pemeriksaan lulus (`HASIL: LULUS (0 temuan)`).
- **Exit code `1`**: Ada ID yatim (*orphan*), duplikat, sel kosong, atau acceptance tanpa angka terukur.
- **Cara Oprek**: Jika kamu menambah komponen baru (mis. `C6.4`) atau fungsi baru di dokumen, tambahkan ID tersebut ke variabel `SN`, `UC`, `FUNC`, `COMP`, `IFACE`, atau `TYPES` di bagian atas `check_consistency.py`.

### 2. Menjalankan Perakit Laporan (`build_report.py`)
- **Hanya menghasilkan file HTML** (disimpan ke `05_BUKTI_DAN_PENDUKUNG/_build/RSK_FINAL.html`):
  ```bash
  python 05_BUKTI_DAN_PENDUKUNG/build_report.py
  ```
- **Menghasilkan HTML + merender PDF otomatis** (menggunakan Chrome/Edge headless):
  ```bash
  python 05_BUKTI_DAN_PENDUKUNG/build_report.py 05_BUKTI_DAN_PENDUKUNG/_build/RSK_FINAL.html 01_DOKUMEN_UTAMA/SiHADIR_Final_SRS_Architecture.pdf
  ```
- **Cara Oprek Tampilan Laporan**:
  - Edit konstanta `GROUP`, `COURSE`, `LECTURER`, `DOC_VERSION`, `DOC_DATE`, atau HTML `COVER` di dalam `build_report.py` untuk mengubah halaman sampul.
  - Edit variabel `CSS` di dalam `build_report.py` untuk mengubah ukuran font, warna tema (`#12395B`), atau margin halaman A4.

### 3. Cara Memakai `SiHADIR_MATLAB_Online.zip` di MATLAB Online
1. Buka [MATLAB Online](https://matlab.mathworks.com/).
2. Upload dan ekstrak `SiHADIR_MATLAB_Online.zip` ke sebuah folder.
3. Di Command Window MATLAB Online, jalankan:
   ```matlab
   build_sihadir_architecture
   layout_sihadir_model
   annotate_sihadir_model
   run_sihadir_checks
   ```

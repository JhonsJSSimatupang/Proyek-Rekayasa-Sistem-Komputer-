# 03_MODEL_MATLAB — Model & Skrip MATLAB System Composer

Folder ini berisi model arsitektur fisik **SiHADIR** pada **MATLAB System Composer** beserta seluruh skrip otomatisasi untuk membangun, menyambung konektor, merapikan tata letak, memberi anotasi alokasi fungsi, memverifikasi, dan mengekspor gambar model.

---

## Daftar Berkas & Fungsinya

| Berkas | Fungsi Utama | Butuh System Composer? |
| :--- | :--- | :---: |
| `SiHADIR_Architecture.slx` | **File model asli MATLAB System Composer** (6 subsistem, 33 komponen, 72 port komponen + 30 port batas, 57 konektor). | Ya (untuk buka di GUI) |
| `SiHADIR_Architecture_Interfaces.sldd` | **Simulink Data Dictionary** yang menyimpan definisi 16 Data Interface (`IF_T2B`, `IF_B2S`, `IF_I1`..`IF_I10`, dll.) beserta elemen dan tipe datanya. | Ya |
| `sihadir_arch_spec.m` | **Single Source of Truth (SSOT)** arsitektur di MATLAB: mendefinisikan 6 subsistem, 33 komponen, 72 port, 16 interface, 27 link, dan 24 alokasi fungsi. | **Tidak** (MATLAB dasar) |
| `verify_architecture_spec.m` | Memeriksa 15 aturan konsistensi (`C1`–`C15`) atas `sihadir_arch_spec.m` dan menyilangkan alokasi fungsi terhadap `../02_DOKUMENTASI_SUMBER/RTM_SiHADIR.csv`. | **Tidak** (MATLAB dasar) |
| `sihadir_iface_name.m` | Helper pemetaan ID interface dokumen (`IF-T2B`) menjadi identifier dictionary MATLAB (`IF_T2B`). | **Tidak** |
| `build_sihadir_architecture.m` | Membangun `SiHADIR_Architecture.slx` dan `SiHADIR_Architecture_Interfaces.sldd` dari nol berdasarkan `sihadir_arch_spec.m`. | Ya |
| `wire_sihadir_model.m` | Menggambar 57 garis konektor (`12` internal S1 + `15 × 3` lintas subsistem) menggunakan API garis Simulink agar terbaca sebagai `Connectors` di System Composer. | Ya |
| `layout_sihadir_model.m` | Menata tata letak 6 subsistem di root dalam grid `3 × 2` dan merapikan komponen di dalam tiap subsistem dengan `arrangeSystem`. | Ya |
| `annotate_sihadir_model.m` | Menulis metadata `ID | jenis | fungsi` ke properti `Description` setiap blok komponen dan subsistem. | Ya |
| `render_sihadir_model.m` | Mengekspor tangkapan layar kanvas root (`SiHADIR_root.png`) dan ke-6 subsistem (`SiHADIR_S1..S6.png`). | Ya |
| `verify_built_model.m` | Memeriksa 9 aturan (`M1`–`M9`) langsung terhadap file `SiHADIR_Architecture.slx` dan `.sldd` yang tersimpan di disk. | Ya |
| `run_sihadir_checks.m` | **Skrip Master Verifikasi**: menjalankan `verify_architecture_spec`, `verify_built_model`, dan audit struktur `.slx`, lalu menyimpan log ke `S10_evidence.txt`. | Ya |
| `fix_systemcomposer_path.m` | Utility pemulih `pathdef.m` MATLAB apabila instalasi System Composer terputus dan `systemcomposer.createModel` belum terdaftar di path. | Ya |
| `PANDUAN_SystemComposer_Manual.md` | Panduan langkah demi langkah (klik-per-klik) apabila ingin membuat atau mendemokan pembuatan model secara manual lewat GUI System Composer. | Dokumentasi |

---

## Cara Menjalankan di MATLAB

### A. Membuka Model yang Sudah Jadi di GUI
1. Buka MATLAB (R2024b atau lebih baru dengan System Composer).
2. Arahkan *Current Folder* ke `03_MODEL_MATLAB`:
   ```matlab
   cd('03_MODEL_MATLAB')
   open_system('SiHADIR_Architecture.slx')
   ```
3. Double-click salah satu blok subsistem (`S1 Edge Terminal` s.d. `S6 Identity & Privacy`) untuk melihat komponen daun, port, dan konektor di dalamnya.

### B. Menjalankan Verifikasi Lengkap (15 Cek Spec + 9 Cek Model)
```matlab
cd('03_MODEL_MATLAB')
run_sihadir_checks
```

### C. Menjalankan Hanya Verifikasi Spesifikasi (Tanpa Toolbox System Composer)
Jika MATLAB yang dipakai tidak memiliki lisensi/toolbox System Composer, pemeriksaan 15 aturan arsitektur tetap bisa dijalankan:
```matlab
cd('03_MODEL_MATLAB')
s = sihadir_arch_spec();
r = verify_architecture_spec(s);
```

### D. Cara Oprek (Menambah/Mengubah Komponen, Port, atau Link)
Jangan mengedit blok secara manual satu-satu jika ingin model dan dokumen tetap sinkron. Cukup oprek satu file: **`sihadir_arch_spec.m`**:
1. Edit tabel `compData`, `ifData`, `portData`, `linkData`, atau `allocData` di dalam `sihadir_arch_spec.m`.
2. Jalankan urutan perintah ini di MATLAB untuk membangun ulang seluruh model `.slx`, `.sldd`, tata letak, anotasi, dan gambar PNG secara otomatis:
   ```matlab
   cd('03_MODEL_MATLAB')
   s = sihadir_arch_spec();
   verify_architecture_spec(s);      % Pastikan 15/15 PASS dulu
   build_sihadir_architecture();     % Bangun ulang .slx, .sldd, dan konektor
   layout_sihadir_model();           % Rapikan posisi blok
   annotate_sihadir_model();         % Tulis alokasi fungsi ke Description blok
   verify_built_model();             % Pastikan 9/9 PASS
   render_sihadir_model('SiHADIR_Architecture.slx', '../04_DIAGRAM_DAN_VISUALISASI');
   ```
3. Setelah mengubah `sihadir_arch_spec.m`, jalankan juga `python gen_arch_svg.py` dari root repository agar diagram `fig_arsitektur_sihadir.svg` dan `.mmd` ikut ter-update otomatis.

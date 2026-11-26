# 04_DIAGRAM_DAN_VISUALISASI — Katalog Diagram & Ekspor Kanvas Model

Folder ini menyimpan seluruh aset visualisasi arsitektur sistem **SiHADIR**, baik yang diekspor langsung dari model **MATLAB System Composer** maupun diagram konseptual, fungsional, dan behavioral yang disematkan ke dalam laporan akhir.

---

## Daftar Berkas Diagram

### 1. Ekspor Kanvas MATLAB System Composer (`SiHADIR_Architecture.slx`)
Dihasilkan otomatis oleh skrip `../03_MODEL_MATLAB/render_sihadir_model.m`:
- `SiHADIR_root.png` — Tampilan level root: 6 subsistem (`S1`–`S6`), 50 port batas, dan 25 konektor lintas subsistem.
- `SiHADIR_S1_Edge_Terminal.png` — Isi subsistem `S1 Edge Terminal`: 11 komponen (`C1.1`–`C1.11`), 4 port batas, 17 konektor.
- `SiHADIR_S2_Backend_Services.png` — Isi subsistem `S2 Backend Services`: 8 komponen (`C2.1`–`C2.8`), 22 port batas, 32 konektor.
- `SiHADIR_S3_Integration_Comms.png` — Isi subsistem `S3 Integration & Comms`: 3 komponen (`C3.1`–`C3.3`), 3 port batas, 3 konektor.
- `SiHADIR_S4_Data_Management.png` — Isi subsistem `S4 Data Management`: 4 komponen (`C4.1`–`C4.4`), 8 port batas, 8 konektor.
- `SiHADIR_S5_User_Interfaces.png` — Isi subsistem `S5 User Interfaces`: 3 komponen (`C5.1`–`C5.3`), 5 port batas, 5 konektor.
- `SiHADIR_S6_Identity_Privacy.png` — Isi subsistem `S6 Identity & Privacy`: 3 komponen (`C6.1`–`C6.3`), 8 port batas, 8 konektor.

### 2. Diagram Arsitektur Fisik & Fungsional
- `fig_arsitektur_sihadir.svg` & `fig_arsitektur_sihadir.png` — Diagram dekomposisi fisik 6 subsistem dan 32 komponen beserta jumlah link keluar/masuk tiap subsistem (dihasilkan dari `../gen_arch_svg.py` yang membaca `sihadir_arch_spec.m`).
- `fig_arsitektur_sihadir.mmd` — Representasi Mermaid dari 6 subsistem, 32 komponen, dan 48 link arsitektur.
- `fig_dekomposisi_fungsi.svg` — Diagram hierarki dekomposisi fungsional (`A0 Verify Classroom Attendance → F1..F12 → 24 fungsi leaf`).
- `fig_alur_presensi.svg` & `fig_alur_presensi.png` — Swimlane Functional Flow Diagram (FFD) 16 langkah proses presensi lintas 5 lane subsistem (dihasilkan dari `../gen_flow_svg.py`).

### 3. Diagram Konteks & Behavioral (Use Case & Sequence)
- `fig_context_diagram.jpg` — Context Diagram SiHADIR (`Bab S2.10`): batas sistem, 7 entitas eksternal (`E1`–`E7`), dan 14 aliran I/O (`F1`–`F14`).
- `fig_usecase_diagram.jpg` — Use Case Diagram SiHADIR (`Bab S4.2`): `UC-01` s.d. `UC-12` beserta relasi `<<include>>`.
- `fig_sd01_enrolment.jpg` — Sequence Diagram `SD-01`: Enrolment Wajah dengan Explicit Consent.
- `fig_sd02_verifikasi.jpg` — Sequence Diagram `SD-02`: Verifikasi Kehadiran Real-Time + Liveness.
- `fig_sd03_offline_sync.png` — Sequence Diagram `SD-03`: Mode Offline & Sinkronisasi Batch Idempoten.
- `fig_sd04_tutup_sesi.jpg` — Sequence Diagram `SD-04`: Penutupan Sesi & Pengiriman Rekap ke SIAKAD.

---

## Cara Generate Ulang / Oprek Diagram

1. **Update Diagram Dekomposisi Fisik (`fig_arsitektur_sihadir.svg` & `.mmd`)**:
   Dari root repository, jalankan:
   ```bash
   python gen_arch_svg.py
   ```
   *(Skrip ini membaca data komponen dan link langsung dari `03_MODEL_MATLAB/sihadir_arch_spec.m`).*

2. **Update Diagram Swimlane Alur Presensi (`fig_alur_presensi.svg`)**:
   Edit daftar `LANES` atau `STEPS` di `gen_flow_svg.py`, lalu jalankan dari root repository:
   ```bash
   python gen_flow_svg.py
   ```

3. **Update Screenshot Kanvas MATLAB System Composer (`SiHADIR_*.png`)**:
   Di MATLAB Command Window:
   ```matlab
   cd('03_MODEL_MATLAB')
   render_sihadir_model('SiHADIR_Architecture.slx', '../04_DIAGRAM_DAN_VISUALISASI')
   ```

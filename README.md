# SiHADIR — System Architecture & Engineering Project

<p align="center">
  **Sistem Informasi Kehadiran Terintegrasi**
  
  *Modeling, Architecture Design, and System Engineering*
</p>

---

## 📌 Tentang Proyek

**SiHADIR** merupakan proyek rekayasa sistem yang berfokus pada perancangan arsitektur sistem informasi kehadiran terintegrasi. Proyek ini mencakup proses identifikasi kebutuhan, perancangan arsitektur fungsional dan fisik, pemodelan komponen, pendefinisian antarmuka, serta verifikasi keterlacakan kebutuhan sistem.

Pemodelan arsitektur dilakukan menggunakan **MATLAB System Composer** untuk menggambarkan hubungan antarkomponen dan subsistem dalam sistem SiHADIR.

## 🎯 Tujuan Proyek

- Mendefinisikan kebutuhan dan spesifikasi sistem.
- Merancang arsitektur fungsional dan fisik SiHADIR.
- Memodelkan subsistem, komponen, port, dan interface.
- Menghubungkan kebutuhan dengan fungsi dan komponen sistem.
- Menyusun dokumentasi dan bukti verifikasi arsitektur.
- Menyediakan model arsitektur yang dapat dikembangkan dan dievaluasi lebih lanjut.

## 🏗️ Gambaran Arsitektur

Arsitektur SiHADIR terdiri dari enam subsistem utama:

| ID  | Subsystem           | Deskripsi                                         |
| --- | ------------------- | ------------------------------------------------- |
| S1  | Edge Terminal       | Pemrosesan pada perangkat terminal kehadiran      |
| S2  | Backend Services    | Pengelolaan layanan dan proses bisnis             |
| S3  | Integration & Comms | Integrasi dengan layanan eksternal dan komunikasi |
| S4  | Data Management     | Pengelolaan penyimpanan dan data sistem           |
| S5  | User Interfaces     | Antarmuka pengguna dan administrator              |
| S6  | Identity & Privacy  | Pengelolaan identitas, persetujuan, dan privasi   |

### Teknologi dan Komponen

- MATLAB
- Simulink
- System Composer
- Simulink Data Dictionary
- Python untuk pendukung dokumentasi dan visualisasi

## 📂 Struktur Repository

```text
Proyek-Rekayasa-Sistem-Komputer-/
│
├── 01_DOKUMEN_UTAMA/
│   └── README.md (Panduan perakitan dokumen laporan utama SRS & Arsitektur)
│
├── 02_DOKUMENTASI_SUMBER/
│   ├── README.md (Panduan struktur bab S1..S10 & cara edit RTM_SiHADIR.csv)
│   ├── S1_Audit_PRJ2_dan_ChangeLog.md .. S10_Model_MATLAB.md
│   └── RTM_SiHADIR.csv
│
├── 03_MODEL_MATLAB/
│   ├── README.md (Panduan oprek & jalankan model MATLAB System Composer)
│   ├── SiHADIR_Architecture.slx
│   ├── SiHADIR_Architecture_Interfaces.sldd
│   ├── sihadir_arch_spec.m
│   └── Skrip pembangun, pemeriksa, tata letak, dan ekspor model (.m)
│
├── 04_DIAGRAM_DAN_VISUALISASI/
│   ├── README.md (Katalog diagram & cara generate ulang visualisasi)
│   ├── SiHADIR_root.png & SiHADIR_S1..S6.png (ekspor kanvas System Composer)
│   ├── fig_arsitektur_sihadir.svg / .png / .mmd
│   ├── fig_alur_presensi.svg / .png
│   └── Diagram Context, Use Case, Sequence (SD-01..SD-04), & Dekomposisi Fungsi
│
├── 05_BUKTI_DAN_PENDUKUNG/
│   ├── README.md (Panduan skrip verifikasi RTM & perakit laporan HTML/PDF)
│   ├── S10_evidence.txt (transkrip verifikasi MATLAB 15/15 & 9/9 LULUS)
│   ├── check_consistency.py (verifikasi otomatis RTM 36 requirement LULUS)
│   ├── build_report.py (perakit laporan lengkap)
│   └── SiHADIR_MATLAB_Online.zip
│
├── gen_arch_svg.py
├── gen_flow_svg.py
└── README.md
```

## 🚀 Panduan Cepat Menjalankan & Oprek Program

Setiap folder telah dilengkapi `README.md` detail. Berikut ringkasan perintah utamanya:

### 1. Verifikasi Konsistensi RTM & Requirement (Python)
Memeriksa 36 requirement di `RTM_SiHADIR.csv` terhadap ID Stakeholder Need (`SN`), Use Case (`UC`), Fungsi (`F`), Komponen (`C`), dan Interface (`IF`):
```bash
python 05_BUKTI_DAN_PENDUKUNG/check_consistency.py
```

### 2. Generate Ulang Diagram Arsitektur & Alur Proses (Python)
Membaca langsung spesifikasi dari `03_MODEL_MATLAB/sihadir_arch_spec.m` dan menghasilkan diagram `.svg` serta `.mmd` ke folder `04_DIAGRAM_DAN_VISUALISASI/`:
```bash
python gen_arch_svg.py
python gen_flow_svg.py
```

### 3. Rakit Ulang Laporan Lengkap HTML & PDF (Python)
Menggabungkan `S1`–`S10` beserta seluruh gambar diagram dan screenshot System Composer menjadi file HTML (dan PDF otomatis bila Chrome/Edge tersedia):
```bash
python 05_BUKTI_DAN_PENDUKUNG/build_report.py
# Atau langsung cetak ke PDF:
python 05_BUKTI_DAN_PENDUKUNG/build_report.py 05_BUKTI_DAN_PENDUKUNG/_build/RSK_FINAL.html 01_DOKUMEN_UTAMA/SiHADIR_Final_SRS_Architecture.pdf
```

### 4. Membangun & Memverifikasi Model MATLAB System Composer (MATLAB R2024b+)
Jalankan di Command Window MATLAB:
```matlab
cd('03_MODEL_MATLAB')
run_sihadir_checks   % Menjalankan 15 cek spec + 9 cek model .slx + menulis S10_evidence.txt
```
Lihat [03_MODEL_MATLAB/README.md](03_MODEL_MATLAB/README.md) untuk panduan lengkap cara menambah/mengubah komponen, port, interface, atau link.

## 🧩 Model Architecture

Model utama dikembangkan menggunakan MATLAB System Composer.

Ringkasan kondisi model berdasarkan pemeriksaan terakhir:

| Elemen               | Jumlah |
| -------------------- | -----: |
| Subsystems           |      6 |
| Components           |     33 |
| Interfaces           |     16 |
| Ports (Leaf / Boundary) | 72 / 30 |
| Architecture Links   |     27 |
| Connectors (Root / Sub) | 15 / 42 |
| Function Allocations |     24 |

_Seluruh elemen di atas telah diverifikasi otomatis melalui `verify_architecture_spec.m` (15/15 LULUS), `verify_built_model.m` (9/9 LULUS), dan `check_consistency.py` (0 temuan pada 36 requirement)._

## 🔗 Traceability

Proyek ini menggunakan konsep keterlacakan (_traceability_) untuk memastikan setiap kebutuhan sistem dapat ditelusuri hingga tahap verifikasi.

Alur keterlacakan yang digunakan:

```text
Stakeholder Needs
       │
       ▼
System Requirements
       │
       ▼
System Functions
       │
       ▼
System Architecture
       │
       ▼
Components & Interfaces
       │
       ▼
Verification
```
## 🔍 Verification & Development Status

Seluruh rantai rekayasa dan model arsitektur telah melewati verifikasi otomatis (**LULUS 100%**):

- **Konsistensi RTM & Traceability (`check_consistency.py`)**: **LULUS (0 temuan)** — 36 requirement (15 FR, 6 PRF, 6 IF, 5 SEC, 4 OPS), 13/13 Stakeholder Needs, 12/12 Use Case, 24/24 fungsi leaf (+2 agregat), 33/33 komponen, 16 ICD + `internal`.
- **Spesifikasi Arsitektur (`verify_architecture_spec.m`)**: **LULUS (15/15 pemeriksaan C1–C15)** — keunikan ID, konsistensi arah & interface pada 72 port dan 27 link, serta kelengkapan alokasi 24 fungsi terhadap RTM.
- **Model MATLAB System Composer (`verify_built_model.m`)**: **LULUS (9/9 pemeriksaan M1–M9)** — 6 subsistem, 33 komponen, 72 port komponen + 30 port batas, 16 interface di `.sldd`, dan 57 garis konektor (15 di root + 42 di dalam subsistem).

## 📦 Project Deliverables

Target keluaran proyek meliputi:

- System Requirement Specification (SRS) & Architecture Report (`02_DOKUMENTASI_SUMBER/S1..S10.md`)
- Context Diagram, Use Case Diagram, & 4 Sequence Diagrams (`S2`, `S4`)
- Functional Architecture — IDEF0 & Functional Flow Diagram (`S6`, `fig_alur_presensi.svg/.png`)
- Physical Architecture & Decomposition Diagram (`S7`, `fig_arsitektur_sihadir.svg/.png`)
- Function-to-Component Allocation, N2 Matrix, ICD, & SPOF Analysis (`S8`)
- Requirements Traceability Matrix (`02_DOKUMENTASI_SUMBER/RTM_SiHADIR.csv` & `S9`)
- Verification, Acceptance Criteria, Risk Register, & Change Impact Analysis (`S5`, `S9`)
- MATLAB System Composer Model & Interface Dictionary (`03_MODEL_MATLAB/SiHADIR_Architecture.slx` & `.sldd`)

## 👥 Anggota Kelompok (Kelas B)

| No | Nama Mahasiswa | NIM |
| :-: | :--- | :--- |
| 1 | Muhamad Al Fatih | 245150301111024 |
| 2 | Jhons Janner Samuel S | 245150301111009 |
| 3 | Azzam Galen Crosdiyanto | 245150307111044 |
| 4 | Muhammad Mushlih Fajr | 245150307111047 |
| 5 | Keirio Omar Attallah | 245150307111061 |

## 👨‍💻 Project Information

| Informasi       | Keterangan                            |
| --------------- | ------------------------------------- |
| Project         | SiHADIR (Sistem Informasi Kehadiran Digital Berbasis Wajah) |
| Mata Kuliah     | CCE61317 Rekayasa Sistem Komputer (RSK) — Kelas B |
| Dosen Pengampu  | Sabriansyah Rizqika Akbar, S.T., M.Eng., Ph.D. |
| Institusi       | Program Studi Teknik Komputer, FILKOM Universitas Brawijaya |
| Modeling Tool   | MATLAB System Composer (R2026b)       |
| Supporting Tool | Python 3 (Verifikasi RTM & Visualisasi SVG/HTML/PDF) |
| Project Stage   | Final SRS & Verified System Architecture (v1.0) |

---

<p align="center">
  **SiHADIR — System Architecture Project**
  
  *Designed through System Engineering and Model-Based Architecture.*
</p>

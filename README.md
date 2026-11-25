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
Proyek RSK-System Composer/
│
├── .vscode/
│
├── 01_DOKUMEN_UTAMA/
│   └── Dokumen utama dan spesifikasi sistem
│
├── 02_DOKUMENTASI_SUMBER/
│   └── Referensi dan dokumentasi pendukung
│
├── 03_MODEL_MATLAB/
│   ├── SiHADIR_Architecture.slx
│   ├── SiHADIR_Architecture_Interfaces.sldd
│   └── File MATLAB pendukung
│
├── 04_DIAGRAM_DAN_VISUALISASI/
│   └── Diagram dan hasil visualisasi arsitektur
│
├── 05_BUKTI_DAN_PENDUKUNG/
│   └── Bukti pengujian dan dokumentasi pendukung
│
├── 99_BACKUP_BEFORE_REPAIR/
│   └── Salinan model sebelum proses perbaikan
│
├── gen_arch_svg.py
├── gen_flow_svg.py
└── README.md
```

## 🧩 Model Architecture

Model utama dikembangkan menggunakan MATLAB System Composer.

Ringkasan kondisi model berdasarkan pemeriksaan terakhir:

| Elemen               | Jumlah |
| -------------------- | -----: |
| Subsystems           |      6 |
| Components           |     33 |
| Interfaces           |     16 |
| Ports                |     72 |
| Connectors / Links   |     27 |
| Function Allocations |     24 |

_Angka tersebut merupakan hasil audit model saat ini, bukan pernyataan bahwa seluruh koneksi dan interface sudah tervalidasi._

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
## 🔍 Development Status

Proyek masih berada dalam tahap pemeriksaan dan penyempurnaan arsitektur.

Area yang menjadi perhatian:

- Validasi koneksi antarkomponen.
- Konsistensi port dan interface.
- Validasi function-to-component allocation.
- Pemeriksaan keterlacakan kebutuhan.
- Penyelarasan model dengan dokumen dan diagram.
- Verifikasi dan acceptance criteria.

## 📦 Project Deliverables

Target keluaran proyek meliputi:

- System Requirement Specification (SRS)
- Context Diagram
- Use Case Diagram
- Sequence Diagrams
- Functional Architecture
- Physical Architecture
- Function-to-Component Allocation
- Requirements Traceability Matrix (RTM)
- Verification and Acceptance Criteria
- MATLAB System Composer Model

## 👨‍💻 Project Information

| Informasi       | Keterangan                            |
| --------------- | ------------------------------------- |
| Project         | SiHADIR                               |
| Domain          | System Engineering                    |
| Modeling Tool   | MATLAB System Composer                |
| Supporting Tool | Python                                |
| Repository      | GitHub                                |
| Project Stage   | Architecture Development & Validation |

---

<p align="center">
  **SiHADIR — System Architecture Project**
  
  *Designed through System Engineering and Model-Based Architecture.*
</p>
Get-Item README.md

# 02_DOKUMENTASI_SUMBER — Sumber Bab SRS & Traceability Matrix

Folder ini menyimpan **sumber kebenaran tekstual (Markdown & CSV)** untuk seluruh bab laporan System Requirement Specification (SRS) dan System Architecture **SiHADIR**.

---

## Daftar Berkas

| Berkas | Isi Bab |
| :--- | :--- |
| `S1_Audit_PRJ2_dan_ChangeLog.md` | **Bab S1** — Audit defect PRJ1/PRJ2, perbaikan rantai jejak, dan Change Log requirement (`19 → 36 requirement`). |
| `S2_Scope_Context.md` | **Bab S2** — Identitas sistem, Problem Statement (`P1`–`P4`), MOE (`MOE-1`–`MOE-4`), System Boundary (`IN`/`OUT`), 7 External Entities (`E1`–`E7`), 14 aliran I/O Context (`F1`–`F14`), posisi Life-Cycle, Asumsi & Constraints. |
| `S3_Stakeholder_Needs.md` | **Bab S3** — 7 Stakeholder (`ST-01`–`ST-07`), 13 Stakeholder Needs (`SN-01`–`SN-13`), dan pemetaan `SN → Requirement` (`0 orphan need`). |
| `S4_UseCase_Sequence.md` | **Bab S4** — Use Case Diagram (`UC-01`–`UC-12`), spesifikasi rinci `UC-01`..`UC-04`, dan 4 Sequence Diagram (`SD-01`..`SD-04`). |
| `S5_Requirements.md` | **Bab S5** — 36 System Requirements berpola EARS (`15 FR`, `6 PRF`, `6 IF`, `5 SEC`, `4 OPS`) lengkap dengan atribut Prioritas, Metode Verifikasi, dan Acceptance Criteria terukur. |
| `S6_FunctionalArch.md` | **Bab S6** — Arsitektur Fungsional murni *WHAT*: dekomposisi `A0 → F1..F12 → 24 fungsi leaf`, tabel IDEF0 (Input, Control, Output, Mechanism), Functional Flow Diagram (FFD), dan matriks `Fungsi ↔ Requirement`. |
| `S7_PhysicalArch.md` | **Bab S7** — Arsitektur Fisik: 6 Subsistem (`S1`–`S6`), 32 Komponen (`C1.1`–`C6.3`), ringkasan port, dan 2 Trade Study kuantitatif (Lokasi Inferensi Edge vs Server vs Hybrid; Metode Liveness Passive vs Active vs Hybrid). |
| `S8_Allocation_N2_ICD_SPOF.md` | **Bab S8** — Deployment View, Matriks Alokasi `24 Fungsi → 32 Komponen`, pemeriksaan `0 komponen menganggur`, Matriks N2 antar-subsistem, 6 ICD Eksternal + 10 ICD Internal, dan Analisis SPOF. |
| `S9_RTM_Risiko_Konsistensi.md` | **Bab S9** — Ringkasan RTM, hasil verifikasi otomatis, Register Risiko (`R-01`–`R-06` + matriks 5×5), Resolusi Keputusan Final (`T-01`–`T-07`), dan Analisis Dampak Perubahan Requirement (*Change Impact Analysis*). |
| `S10_Model_MATLAB.md` | **Bab S10** — Dokumentasi implementasi dan hasil verifikasi model MATLAB System Composer (`15/15` cek spesifikasi & `9/9` cek model `.slx`). |
| `RTM_SiHADIR.csv` | **Artefak Otoritatif RTM** — 36 baris requirement dengan 10 kolom wajib (`ReqID, Type, SN, UseCase, Function, Component, Interface, Verification, Priority, Acceptance`). |

---

## Cara Oprek / Mengedit Dokumen & Validasi

1. **Mengubah Isi Bab (`S1`..`S10.md`)**:
   - Edit berkas `.md` yang diinginkan menggunakan teks editor / VS Code.
   - Jangan mengubah judul heading utama (`## 6.5 FFD — alur fungsi utama`, `## 7.2 Struktur sistem`, `## 10.4 Pemeriksaan spesifikasi`, `## 10.8 Port yang tidak tersambung`) karena judul tersebut menjadi titik jangkar (*anchor*) penyisipan gambar otomatis pada `build_report.py`.

2. **Mengubah atau Menambah Baris di `RTM_SiHADIR.csv`**:
   - Gunakan pemisah titik-koma (`;`) jika satu requirement memetakan lebih dari satu ID (contoh: `SN-01;SN-02` atau `C1.4;C1.7`).
   - Setiap kali selesai mengedit `RTM_SiHADIR.csv`, **wajib** jalankan skrip pemeriksa konsistensi:
     ```bash
     python 05_BUKTI_DAN_PENDUKUNG/check_consistency.py
     ```
   - Pastikan output akhir bertuliskan `HASIL: LULUS (0 temuan)`.

3. **Merakit Ulang Laporan setelah Edit**:
   - Jalankan `python 05_BUKTI_DAN_PENDUKUNG/build_report.py` untuk memperbarui laporan gabungan HTML/PDF.

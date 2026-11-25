# S1 — Audit PRJ2 & Change Log
Proyek: SiHADIR · CCE61317 RSK · Tim Pengembang SiHADIR (Kelas B)
Status: Final (Terverifikasi)

## A. Tabel audit (defect → perbaikan)

| # | Lokasi PRJ2 | Cacat | Bukti | Dampak rubrik | Perbaikan |
|---|---|---|---|---|---|
| 1 | §5 RTM | Hanya 19 requirement; tidak ada requirement interface, security, operational/environmental | SR-FR1..13 + SR-NFR1..6 | Requirement quality 18, coverage 7 | Naik ke 35: 14 FR + 6 PRF + 6 IF + 5 SEC + 4 OPS |
| 2 | RTM | SN-05 (tetap berfungsi saat jaringan terganggu) tidak punya requirement; FR12/FR13 justru ditrace ke SN-10 | baris SR-FR12 → SN-10 | Orphan need, RTM 12 | SN-05 → SR-FR10, SR-FR11, SR-OPS4 |
| 3 | RTM | SN-06 (kontrol buka/tutup sesi) tidak punya requirement; FR6 ditrace ke SN-03 | baris SR-FR6 → SN-03 | Orphan need | SN-06 → SR-FR8 (buka) + SR-FR9 (tutup) |
| 4 | RTM | SN-09 (indikator kesiapan perangkat) tidak punya requirement | SN-09 hanya di tabel stakeholder | Orphan need | SN-09 → SR-OPS2 |
| 5 | RTM | Trace salah: deteksi wajah ke "rekap otomatis SIAKAD" | SR-FR1 → SN-03 | Traceability | SR-FR1 → SN-01 |
| 6 | RTM | Trace salah: timestamp/NTP ke "verifikasi identitas & liveness" | SR-FR4 → SN-02 | Traceability | SR-FR6 → SN-03; SR-IF4 → SN-03 |
| 7 | RTM | Trace salah: notifikasi ke "audit trail" | SR-FR7 → SN-11 | Traceability | SR-FR12 → SN-13 (baru); SR-IF5 → SN-13 |
| 8 | RTM | Trace salah: alert admin ke "antarmuka mudah digunakan" | SR-FR11 → SN-12 | Traceability | SR-FR13 → SN-07 |
| 9 | RTM | Trace salah: consent/hapus citra/hapus template ke "integrasi sistem jelas" | SR-FR8..10 → SN-08 | Traceability, privacy | SR-SEC1..3 → SN-04 |
| 10 | RTM | Trace salah: SSO ke "integrasi sistem" padahal kebutuhan keamanan akses | SR-NFR5 → SN-08 | Traceability | SR-IF3, SR-SEC4 → SN-10 |
| 11 | Verifikasi | FRR (statistik) diverifikasi dengan "Inspeksi" | SR-NFR4 | Verification 8 | SR-PRF4 → Test |
| 12 | Atomisitas | Satu requirement memuat beberapa kondisi/kewajiban | FR2 (cocokkan + batasi roster), FR4 (timestamp + interval NTP), FR6 (buka + konsekuensi tutup), FR11 (ambang + isi alert) | Requirement quality | Dipecah: FR3/FR4; FR6/IF4; FR8/FR9; FR13 |
| 13 | EARS | Tidak ada trigger/condition; statement berupa deskripsi | FR5, FR11, NFR6 | Requirement quality | Ditulis ulang pola When/While/If–shall |
| 14 | Atribut | Tidak ada Priority, Source terpisah, Assumption, Constraint; RTM tanpa kolom Use case/Function/Component/Interface | seluruh §5 | Attributes 7, RTM 12 | Skema atribut lengkap di S5; RTM 8 kolom di S9 |
| 15 | Penomoran | SN tidak kontigu per stakeholder (ST-01 memakai 01,02,04,12) | §4 | Konsistensi | Renumber SN-01..SN-13 di S3 + tabel pemetaan |
| 16 | Arsitektur | "Terminal" dan "backend" dipakai tanpa definisi; "simpan lokal" ambigu (di mana?) | FR12 | Architecture 20 | Didefinisikan di S7 (Edge Terminal vs Backend Services) |
| 17 | Kelengkapan | Tidak ada use case, sequence, functional/physical/allocated architecture, ICD | seluruh dokumen | Architecture 20, use case 8, interface 6 | S4, S6, S7, S8 |
| 18 | Risiko | RR-01..05 tanpa likelihood×consequence; tidak ada risiko SPOF/critical interface (SIAKAD API, NTP, DB) | §6 | Risk 5 | S9: 6 risiko + skor L×C + mitigasi |
| 19 | Acceptance | Kriteria ambigu / mencampur metrik | FR2 "mahasiswa terdaftar di kelas lain"; FR3 mencampur FR dan APCER/BPCER | Verification 8 | Kriteria dipecah ke PRF3/PRF5, FR2 diganti skenario impostor terdaftar |
| 20 | PRJ1 | Posisi life-cycle kontradiktif (concept vs early engineering); "context diagram" masih daftar boundary, belum ada I/O berlabel | slide life-cycle & boundary | Scope/context 8 | Dikunci di S2: posisi = akhir Concept Development, gate ke Engineering Development; context diagram digambar ulang dengan I/O |

## B. Change log requirement (lama → baru)

| ID lama | ID baru | Alasan |
|---|---|---|
| SR-FR1 | SR-FR1 + SR-PRF2 | Deteksi dipisah dari metrik waktu |
| SR-FR2 | SR-FR3 + SR-FR4 | Pencocokan identitas vs pembatasan kandidat |
| SR-FR3 | SR-FR5 + SR-PRF5 | Kewajiban fungsional vs metrik APCER/BPCER |
| SR-FR4 | SR-FR6 + SR-IF4 | Timestamp internal vs antarmuka NTP |
| SR-FR5 | SR-FR7 | Ditulis ulang EARS |
| SR-FR6 | SR-FR8 + SR-FR9 | Buka dan tutup sesi adalah dua fungsi |
| SR-FR7 | SR-FR12 + SR-IF5 | Notifikasi vs antarmuka gateway |
| SR-FR8 | SR-SEC1 | Reklasifikasi ke security/privacy |
| SR-FR9 | SR-SEC2 | Reklasifikasi |
| SR-FR10 | SR-SEC3 | Reklasifikasi |
| SR-FR11 | SR-FR13 | Trace diperbaiki ke SN-07 |
| SR-FR12 | SR-FR10 | Trace diperbaiki ke SN-05 |
| SR-FR13 | SR-FR11 | Trace diperbaiki ke SN-05 |
| SR-NFR1 | SR-PRF2 | Reklasifikasi performance |
| SR-NFR2 | SR-PRF1 | Reklasifikasi performance |
| SR-NFR3 | SR-PRF3 | Reklasifikasi |
| SR-NFR4 | SR-PRF4 | Reklasifikasi + metode Test |
| SR-NFR5 | SR-IF3 + SR-SEC4 | Antarmuka SSO vs kontrol akses |
| SR-NFR6 | SR-OPS1 | Reklasifikasi operational |
| — | SR-FR14, SR-FR15 | Enrolment dan rekap sesi belum punya requirement |
| — | SR-IF1, SR-IF2, SR-IF6 | Antarmuka terminal–backend, backend–SIAKAD, UI–backend |
| — | SR-SEC5 | Audit log tamper-evident |
| — | SR-OPS2, SR-OPS3, SR-OPS4 | Kesiapan perangkat, kondisi pencahayaan, durasi offline |

Total: 35 requirement (14 FR, 6 PRF, 6 IF, 5 SEC, 4 OPS).

## C. ASSUMPTION (harus dikonfirmasi)
- A-01: SIAKAD menyediakan API (REST/JSON atau SOAP) dan tidak hanya impor file. Bila salah, SR-IF2 berubah menjadi antarmuka file/Excel.
- A-02: Terminal = laptop + webcam USB yang dioperasikan dosen di kelas; inferensi wajah berjalan di terminal (edge), bukan di server.
- A-03: Satu sesi = satu kelas terjadwal; 40 mahasiswa adalah batas desain per terminal.
- A-04: MATLAB R2024b atau lebih baru, dengan System Composer + Requirements Toolbox + Simulink.
- A-05: Identitas kelompok ditetapkan sebagai `Tim Pengembang SiHADIR (Kelas B)` yang beranggotakan 5 mahasiswa.

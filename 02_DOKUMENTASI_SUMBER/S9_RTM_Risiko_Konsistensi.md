# S9 — RTM, Register Risiko, dan Konsistensi Akhir

## 9.1 Struktur RTM
Matriks lengkap ada di `RTM_SiHADIR.csv` (36 baris, 1 baris per requirement). Kolom traceability:

`ReqID · Type · SN · UseCase · Function · Component · Interface · Verification · Priority · Acceptance`

Delapan kolom tengah adalah rantai jejak wajib; `Type` dan `Acceptance` melengkapi atribut requirement dari S5.

### Distribusi
| Dimensi | Sebaran |
|---|---|
| Tipe | FR 15 · PRF 6 · IF 6 · SEC 5 · OPS 4 = **36** |
| Prioritas | Must 31 · Should 5 (FR11, FR12, IF5, IF6, OPS3) |
| Verifikasi | Test 29 · Demonstration 6 · Analysis 1 |
| SN tercakup | 13/13 |
| Use case tercakup | 10/12 langsung + 2 transitif (UC-11, UC-12 ⊂ UC-02) |
| Fungsi tercakup | 26/24 leaf + 2 agregat (F2, F4) |
| Komponen tercakup | 33/33 |
| Interface tercakup | 17/17 (16 ICD + 1 `internal`) |

## 9.2 Rantai jejak per lapisan
| Lapisan | Sumber | Tujuan | Bukti kelengkapan |
|---|---|---|---|
| Problem → SN | P1–P4 (S2) | SN-01..SN-13 | setiap P punya ≥1 SN; 4/4 |
| SN → Use case | SN-01..SN-13 | UC-01..UC-12 | 13/13 SN muncul di ≥1 UC |
| Use case → Requirement | UC-01..UC-12 | SR-* | 12/12 UC punya requirement (UC-11/12 transitif) |
| Requirement → Fungsi | SR-* | F* | 36/36 terpetakan; 0 fungsi tanpa req |
| Fungsi → Komponen | F* | C* | 24/24 leaf teralokasi (S8) |
| Komponen → Interface | C* | IF-* | 33/33 komponen punya ≥1 port |
| Requirement → Verifikasi | SR-* | Test/Demo/Analysis | 36/36 punya metode + acceptance terukur |

### Contoh rantai penuh (satu requirement)
`P2 titip absen → SN-02 → UC-02 → SR-FR3 → F2.4+F2.5 → C1.4 (+C1.7) → IF-I3 → Test → "100 terdaftar → tepat 1 kandidat"`

## 9.3 Hasil pemeriksaan otomatis
Skrip: `check_consistency.py` (dapat dijalankan ulang; dipakai sebagai lampiran bukti di S11).

```
Requirements : 36
SN dipakai   : 13/13
UC dipakai   : 10/12 (transitive: UC-11, UC-12)
Fungsi       : 26/24 (+2 agregat)
Komponen     : 33/33
Interface    : 17/17
Distribusi   : FR 15, PRF 6, IF 6, SEC 5, OPS 4
Prioritas    : M 31, S 5
Verifikasi   : Test 29, Demonstration 6, Analysis 1

HASIL: LULUS (0 temuan)
```

Pemeriksaan yang dijalankan: ID unik · tidak ada sel kosong · keanggotaan ID space (SN/UC/F/C/IF) · SN tanpa requirement · fungsi tanpa requirement · komponen tanpa requirement · use case tanpa requirement · acceptance tanpa angka · kesesuaian distribusi tipe · nilai verifikasi/prioritas sah.

## 9.4 Temuan yang diperbaiki saat S9
| # | Temuan | Perbaikan | Dampak |
|---|---|---|---|
| D-01 | SR-FR3 hanya menunjuk F2.5, padahal representasi (F2.4) adalah bagian yang diuji | Function → `F2.4;F2.5` | RTM |
| D-02 | SR-FR4 (mahasiswa kelas lain) butuh roster cache, bukan hanya C1.4 | Component → `C1.4;C1.7` | RTM, S8 |
| D-03 | SR-FR5 menulis record tetapi tidak menyebut penyimpanan | Component → `C2.3;C4.2` | RTM |
| D-04 | SR-FR12 alert tampil di konsol admin | Component → `C2.6;C5.2` | RTM |
| D-05 | SR-FR13 enrolment melibatkan UI + DB, bukan hanya modul | Component → `C6.2;C4.1;C5.3` | RTM |
| D-06 | SR-FR15 umpan balik butuh orkestrasi terminal | Component → `C1.8;C1.3` | RTM |
| D-07 | SR-IF3 / SR-IF4 / SR-SEC1 / SR-SEC5 tidak menyebut connector/registry/store | Component dilengkapi | RTM |
| D-08 | SR-OPS2 memakai interface `internal` yang tidak ada di daftar ICD | Ditandai sah sebagai non-ICD | skrip |
| D-09 | S5 menulis prioritas M=30/S=6 | Dikoreksi jadi M=31/S=5 | S5 |

Semua perubahan bersifat **penajaman alokasi**; tidak ada requirement yang ditambah, dihapus, atau diubah statement-nya.

## 9.5 Register risiko
Skala L (kemungkinan) dan C (dampak) 1–5. Skor = L×C. Pita: 1–4 rendah · 5–9 sedang · 10–14 tinggi · 15–25 kritis.

| ID | Risiko | L | C | Skor | Pita | Mitigasi | Requirement terkait | Pemilik |
|---|---|---|---|---|---|---|---|---|
| R-01 | Wajah dipalsukan (foto/video/replay) sehingga absen titipan tetap lolos | 3 | 5 | 15 | Kritis | Liveness hybrid (passive + active challenge); APCER ≤5% diuji; alert ke admin pada percobaan berulang | SR-FR2, SR-PRF5, SR-FR12 | ST-02 |
| R-02 | API SIAKAD tidak tersedia atau kontrak berubah saat kelas | 4 | 4 | 16 | Kritis | Antrean + retry idempoten ≤10 mnt; rekap tetap tersimpan lokal; kontrak versi dipatok | SR-FR10, SR-FR14, SR-IF2, SR-OPS1 | ST-04 |
| R-03 | Perangkat terminal gagal saat kelas dimulai | 3 | 3 | 9 | Sedang | Self-test ≤60 s; laptop cadangan; koreksi manual dosen sebagai jalur akhir | SR-OPS2, SR-FR12 | ST-06 |
| R-04 | Data biometrik bocor atau retensi melampaui consent | 2 | 5 | 10 | Tinggi | Consent wajib; tidak menyimpan citra mentah; hapus template ≤24 jam; audit append-only | SR-SEC1, SR-SEC2, SR-SEC3, SR-SEC5 | ST-07 |
| R-05 | Akurasi turun pada pencahayaan/pose nyata di kelas | 4 | 3 | 12 | Tinggi | Ambang kalibrasi per ruang; peringatan lux di luar 300–700; fallback koreksi manual | SR-OPS3, SR-FR1, SR-PRF4 | ST-02 |
| R-06 | Penolakan pengguna (mahasiswa/dosen) karena kekhawatiran privasi atau antre | 3 | 4 | 12 | Tinggi | Transparansi consent; target p95 ≤2 s; notifikasi pengingat; sosialisasi | SR-FR11, SR-PRF2, SR-SEC1 | ST-01 |

### Matriks risiko 5×5
| C \ L | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 5 | 5 | 10 | **15 R-01** | 20 | 25 |
| 4 | 4 | 8 | **12 R-06** | **16 R-02** | 20 |
| 3 | 3 | 6 | **9 R-03** | **12 R-05** | 15 |
| 2 | 2 | 4 | 6 | 8 | 10 |
| 1 | 1 | 2 | 3 | 4 | 5 |

Tidak ada risiko yang dibiarkan tanpa mitigasi; dua risiko kritis (R-01, R-02) punya mitigasi yang sudah menjadi requirement, bukan sekadar prosedur.

## 9.6 Konsistensi silang dokumen
| Pasangan dokumen | Diperiksa | Hasil |
|---|---|---|
| S2 problem ↔ S3 SN | 4 problem punya SN | konsisten |
| S3 SN ↔ S5 requirement | 13 SN, 36 req | 0 SN yatim, 0 req tanpa SN |
| S4 UC ↔ S5 requirement | 12 UC | 12/12 tercakup (2 transitif) |
| S5 requirement ↔ S6 fungsi | 36 req, 24 leaf | 0 yatim dua arah |
| S6 fungsi ↔ S7 komponen | 24 leaf | 24/24 teralokasi |
| S7 komponen ↔ S8 interface | 33 komponen | 33/33 punya port |
| S8 ICD ↔ S5 interface req | 6 IF eksternal | 6/6 punya ICD + requirement |
| S5 verifikasi ↔ acceptance | 36 | 36/36 punya ambang angka |

## 9.7 Item terbuka (TBD) yang harus ditutup sebelum S11
| # | TBD | Pemilik keputusan | Dampak bila tidak ditutup |
|---|---|---|---|
| T-01 | Nomor kelompok (`XX`) untuk nama berkas | Jhons | nama berkas final |
| T-02 | Rentang lux 300–700 vs kondisi ruang nyata | Jhons | SR-OPS3 |
| T-03 | FR11 prioritas Should vs Must | Jhons | prioritas & cakupan uji |
| T-04 | IF6 40 pengguna serentak realistis | Jhons | SR-IF6 |
| T-05 | Batas 24 jam penghapusan template | Jhons | SR-SEC3 |
| T-06 | Apakah notifikasi SN-13 benar-benar diinginkan dosen | Jhons | SR-FR11 |
| T-07 | Apakah ST-04/ST-05 unit terpisah | Jhons | pemilik risiko |

## 9.8 ASSUMPTION
- A-24: RTM CSV adalah **artefak otoritatif**; tabel di S5 adalah narasi. Bila berbeda, CSV menang dan S5 diperbaiki.
- A-25: UC-11 dan UC-12 tidak dipetakan langsung karena merupakan «include» dari UC-02; cakupannya dihitung transitif.
- A-26: `internal` pada SR-OPS2 berarti antarmuka di dalam satu host, bukan ICD lintas komponen.

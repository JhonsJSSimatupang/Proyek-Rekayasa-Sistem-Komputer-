# S3 — Stakeholder & Stakeholder Needs (SN-01..SN-13)

## 3.1 Prinsip
- SN ditulis **bebas solusi** (outcome, bukan teknologi), satu kalimat, dapat diuji pada level MOE.
- Setiap SN punya **satu pemilik utama** (primary) dan boleh punya pemilik pendukung.
- Setiap SN wajib diturunkan ke **minimal satu requirement**; sebaliknya setiap requirement wajib punya SN sumber.
- ID SN-01..SN-12 dari PRJ2 **dipertahankan** (tidak ada renumber); yang diperbaiki adalah urutan penyajian (sebelumnya tidak kontigu per stakeholder) dan penambahan SN-13.

## 3.2 Stakeholder
| ID | Stakeholder | Peran | Kepentingan utama | Risiko bila sistem gagal |
|---|---|---|---|---|
| ST-01 | Mahasiswa | Pengguna presensi | Cepat, mudah, identitas tidak bisa diwakilkan, data biometrik terlindungi | Antre, salah status, data pribadi bocor |
| ST-02 | Dosen Pengampu | Pengendali sesi | Sesi terkendali, rekap otomatis, tetap jalan saat jaringan buruk, bisa koreksi | Waktu kuliah terpakai, rekap salah, tidak bisa mengajar |
| ST-03 | Admin Akademik | Pengelola data presensi | Rekap terintegrasi, anomali tertelusuri | Rekap tidak konsisten, sengketa tidak terbukti |
| ST-04 | Pengelola SIAKAD | Pemilik data akademik | Integrasi jelas, data tidak duplikatif | Data ganda, jadwal tidak sinkron |
| ST-05 | Unit IT | Pengelola infrastruktur & integrasi | Integrasi SSO/NTP/notifikasi, keamanan akses, audit | Celah akses, kegagalan integrasi |
| ST-06 | Administrator Infrastruktur | Kesiapan perangkat & jaringan | Indikator kesiapan, mode offline | Terminal mati saat kelas dimulai |
| ST-07 | Auditor Kepatuhan & Privasi | Pemeriksa kepatuhan | Consent, retensi, audit trail dapat diperiksa | Pelanggaran UU PDP |

## 3.3 Stakeholder needs
| SN | Pernyataan kebutuhan | Primary | Pendukung | Rasional |
|---|---|---|---|---|
| SN-01 | Proses presensi harus cepat, efisien, dan mudah digunakan sehingga tidak menghabiskan waktu kuliah | ST-01 | ST-02 | MOE-1; keluhan antrean |
| SN-02 | Identitas harus diverifikasi sebagai kehadiran fisik orang yang benar, bukan sekadar nama | ST-02 | ST-01 | P2 titip absen |
| SN-03 | Rekap kehadiran harus terbentuk otomatis dan terkirim ke SIAKAD tanpa rekap manual | ST-02 | ST-03, ST-04 | P3; MOE-3 |
| SN-04 | Data biometrik harus dilindungi, dikumpulkan dengan consent, dan dapat dihapus | ST-01 | ST-07 | P4; C-01 UU PDP |
| SN-05 | Sistem harus tetap mencatat kehadiran saat jaringan terganggu dan menyelaraskan data setelah pulih | ST-02 | ST-06 | C-03; kelas tidak boleh berhenti |
| SN-06 | Dosen harus dapat mengendalikan pembukaan dan penutupan sesi presensi | ST-02 | — | Batas kewenangan akademik |
| SN-07 | Koreksi manual harus tercatat dan dapat ditelusuri kembali | ST-02 | ST-03 | Sengketa nilai kehadiran |
| SN-08 | Antarmuka ke SIAKAD, SSO, NTP, dan gateway notifikasi harus terdefinisi dan andal | ST-04 | ST-05 | Integrasi lintas sistem |
| SN-09 | Kesiapan perangkat terminal harus dapat diketahui sebelum sesi dimulai | ST-06 | ST-02 | Kegagalan di menit pertama kelas |
| SN-10 | Akses ke sistem dan data harus terbatas pada peran yang berwenang | ST-05 | ST-07 | Keamanan akses |
| SN-11 | Setiap aktivitas penting harus terekam dalam audit trail yang dapat diperiksa | ST-03 | ST-05, ST-07 | Akuntabilitas & audit |
| SN-12 | Antarmuka pengguna harus mudah dipahami dan memberi umpan balik yang jelas | ST-01 | ST-02, ST-03 | Adopsi; kesalahan operator |
| SN-13 | Mahasiswa yang belum tercatat harus diberi pemberitahuan proaktif sebelum sesi berakhir | ST-02 | ST-01 | Mengurangi Alfa yang tidak disengaja |

## 3.4 Peta SN → requirement (final 36 requirement)
| SN | Requirement turunan | Jml |
|---|---|---|
| SN-01 | SR-FR1, SR-FR3, SR-FR15, SR-PRF1, SR-PRF2 | 5 |
| SN-02 | SR-FR2, SR-FR3, SR-FR4, SR-PRF3, SR-PRF4, SR-PRF5 | 6 |
| SN-03 | SR-FR5, SR-FR6, SR-FR14, SR-PRF6, SR-IF2 | 5 |
| SN-04 | SR-FR13, SR-SEC1, SR-SEC2, SR-SEC3 | 4 |
| SN-05 | SR-FR9, SR-FR10, SR-OPS1, SR-OPS4 | 4 |
| SN-06 | SR-FR7, SR-FR8 | 2 |
| SN-07 | SR-FR12, SR-SEC5 | 2 |
| SN-08 | SR-IF1, SR-IF2, SR-IF3, SR-IF4, SR-IF5 | 5 |
| SN-09 | SR-OPS2 | 1 |
| SN-10 | SR-SEC4, SR-IF3 | 2 |
| SN-11 | SR-SEC5 | 1 |
| SN-12 | SR-FR15, SR-IF6, SR-PRF2 | 3 |
| SN-13 | SR-FR11, SR-IF5 | 2 |

Catatan: beberapa requirement melayani lebih dari satu SN (mis. SR-FR3 untuk SN-01 dan SN-02). Relasi many-to-many dicatat di RTM S9.

## 3.5 Bukti cakupan
- Orphan need (SN tanpa requirement): **0** (SN-05, SN-06, SN-09 kini tertutup; SN-12 juga).
- Requirement tanpa SN sumber: **0** (semua 36 punya sumber).
- Requirement final: **36** = 15 FR + 6 PRF + 6 IF + 5 SEC + 4 OPS.
- Koreksi hitungan dari S1: FR 14 → 15 (SR-FR15 umpan balik status ke mahasiswa), sehingga total 35 → 36. Angka 36 yang berlaku.

## 3.6 Perbaikan trace terhadap PRJ2
| Requirement | Trace PRJ2 | Trace final | Alasan |
|---|---|---|---|
| Deteksi wajah | SN-03 | SN-01 | Rekap SIAKAD bukan alasan deteksi wajah |
| Timestamp | SN-02 | SN-03 | Waktu terkait pencatatan & rekap, bukan liveness |
| Notifikasi | SN-11 | SN-13 | Notifikasi proaktif adalah need tersendiri |
| Alert admin | SN-12 | SN-07 | Anomali & audit, bukan kemudahan UI |
| Consent/hapus | SN-08 | SN-04 | Integrasi bukan alasan privasi |
| SSO | SN-08 | SN-10 (+SN-08) | SSO adalah kontrol akses |
| Offline | SN-10, SN-07 | SN-05 | Kebutuhan kontinuitas operasional |

## 3.7 ASSUMPTION
- A-01..A-08 (dari S2)
- A-09: rekap dikirim **push** oleh SiHADIR ke SIAKAD melalui API, bukan ditarik SIAKAD.
- A-10: SN-13 (notifikasi) dimiliki Dosen sebagai pemilik utama; mahasiswa sebagai penerima manfaat.

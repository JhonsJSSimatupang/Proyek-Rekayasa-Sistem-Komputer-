# S8 — Allocation, N2/ICD, SPOF

## 8.1 Deployment view (siapa jalan di mana)
| Host | Komponen |
|---|---|
| Laptop terminal (edge) | C1.1–C1.11, C5.3 |
| Server backend | C2.1–C2.8, C3.1–C3.3, C4.1–C4.4, C6.1–C6.3 |
| Browser dosen/admin | C5.1, C5.2 |

Catatan penajaman S7: `C1.7` menjadi **Roster & Template Cache** karena pencocokan di edge memerlukan template sesi aktif. `C1.10 Time Client` terhubung langsung ke server NTP eksternal (`E6`) tanpa melalui backend.

## 8.2 Allocation matrix (function → component)
| Fungsi | Komponen primer | Pendukung | Interface | Requirement |
|---|---|---|---|---|
| F1.1 Open Session | C2.2 | C5.1, C1.7, C4.1 | IF-UI2B, IF-I9 | FR7 |
| F1.2 Close Session | C2.2 | C5.1, C2.4 | IF-UI2B, internal | FR8 |
| F2.1 Acquire Image | C1.1 | C1.3 | IF-I1 | OPS3 |
| F2.2 Detect Face | C1.4 | C1.2, C1.3 | IF-I2 | FR1 |
| F2.3 Verify Liveness | C1.5 | C1.2, C1.3 | IF-I1, internal | FR2, PRF5 |
| F2.4 Represent Face | C1.4 | C1.2, C1.3 | IF-I2 | FR3 |
| F2.5 Match Identity | C1.4 | C1.7, C4.1 | IF-I3, IF-I9 | FR3, FR4, PRF3, PRF4 |
| F3 Determine Status | C1.3 (penetapan di terminal), C2.4 (finalisasi di backend) | C2.3 | IF-I4, IF-I8 | FR6 |
| F4.1 Persist Record | C2.3 | C4.2 | IF-I5 | FR5 |
| F4.2 Buffer Record | C1.6 | C1.3, C1.9 | IF-I4 | FR9, OPS4 |
| F4.3 Synchronize Record | C1.9 | C2.1, C2.3 | IF-T2B | FR10, IF1 |
| F5.1 Compile Recap | C2.5 | C4.2, C2.3 | IF-I6, internal | FR14 |
| F5.2 Transmit Recap | C3.1 | C2.5 | IF-B2S | FR14, PRF6, IF2 |
| F6.1 Notify Student | C2.6 | C3.2, C2.2, C4.2 | IF-B2GW, IF-I6, internal | FR11, IF5 |
| F6.2 Alert Administrator | C2.6 | C5.2, C2.3 | IF-UI2B, internal | FR12 |
| F7.1 Capture Consent | C6.1 | C5.3, C2.1, C4.4 | IF-I10 | SEC1 |
| F7.2 Enrol Template | C6.2 | C1.4, C1.3, C2.1, C4.1 | IF-I2, IF-T2B | FR13, SEC2 |
| F7.3 Erase Biometric Data | C6.3 | C2.1, C4.1, C2.7, C4.3 | IF-UI2B, IF-I7, internal | SEC3 |
| F8.1 Authenticate User | C2.8 | C3.3 | IF-B2SSO | IF3 |
| F8.2 Authorize Role | C2.1 | C2.8 | IF-UI2B, internal | SEC4 |
| F9 Record Audit Trail | C2.7 | C4.3, C2.1, C2.3, C6.1, C6.3 | IF-I7 | SEC5 |
| F10 Present Feedback | C1.8 | C1.3, C5.1, C2.1 | IF-I4, IF-UI2B | FR15, IF6, PRF2 |
| F11 Monitor Readiness | C1.11 | C1.2, C1.3 | internal | OPS2 |
| F12 Synchronize Time | C1.10 | — (langsung ke E6 NTP) | IF-T2NTP, internal | FR5, IF4 |

## 8.3 Cek komponen menganggur
| Komponen | Fungsi | Status |
|---|---|---|
| C1.1 | F2.1 | aktif |
| C1.2 | F2.2–F2.5, F11 | aktif |
| C1.3 | F2, F3, F10 | aktif |
| C1.4 | F2.2, F2.4, F2.5, F7.2 | aktif |
| C1.5 | F2.3 | aktif |
| C1.6 | F4.2 | aktif |
| C1.7 | F1.1, F2.5 | aktif |
| C1.8 | F10 | aktif |
| C1.9 | F4.2, F4.3 | aktif |
| C1.10 | F12 | aktif |
| C1.11 | F11 | aktif |
| C2.1 | F4.3, F7.1, F7.2, F7.3, F8.2, F10 | aktif |
| C2.2 | F1.1, F1.2 | aktif |
| C2.3 | F4.1, F4.3 | aktif |
| C2.4 | F1.2, F3 | aktif |
| C2.5 | F5.1, F5.2 | aktif |
| C2.6 | F6.1, F6.2 | aktif |
| C2.7 | F9 | aktif |
| C2.8 | F8.1, F8.2 | aktif |
| C3.1 | F5.2 | aktif |
| C3.2 | F6.1 | aktif |
| C3.3 | F8.1 | aktif |
| C4.1 | F2.5, F7.2, F7.3 | aktif |
| C4.2 | F4.1, F5.1 | aktif |
| C4.3 | F7.3, F9 | aktif |
| C4.4 | F7.1 | aktif |
| C5.1 | F1.1, F1.2, F10 | aktif |
| C5.2 | F6.2, F7.3 | aktif |
| C5.3 | F7.1, F7.2 | aktif |
| C6.1 | F7.1 | aktif |
| C6.2 | F7.2 | aktif |
| C6.3 | F7.3 | aktif |

Kesimpulan: 24 fungsi leaf teralokasi (25 alokasi karena `F3` di `C1.3` dan `C2.4`); 32 komponen aktif; **0 fungsi tanpa komponen, 0 komponen tanpa fungsi**.

## 8.4 N2 matrix (level subsistem)
Baris = pengirim, kolom = penerima. `—` = tidak ada aliran langsung.

| From \ To | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| S1 | — | record, batch sync, template enrolment (IF-T2B) | — | — | — | — |
| S2 | roster + template (IF-I9) | — | rekap, notif, auth (IF-B2S, B2GW, B2SSO) | record, audit (IF-I5, I7) | view, alert (IF-UI2B) | template, perintah hapus, consent (IF-T2B, UI2B, I10) |
| S3 | — | — | — | — | — | — |
| S4 | — | data rekap, daftar belum tercatat, set template (IF-I6, I9) | — | — | — | — |
| S5 | — | perintah/kueri, consent (IF-UI2B, I10) | — | — | — | — |
| S6 | — | audit consent/hapus (IF-I7) | — | consent, template, perintah hapus (IF-I10, T2B, internal) | — | — |

Catatan: hubungan ke NTP (`E6`), SIAKAD (`E4`), SSO (`E5`), dan gateway notifikasi (`E7`) adalah antarmuka eksternal (8.5), bukan N2 antar-subsistem.

## 8.5 ICD — antarmuka eksternal
| ID | Sumber → Tujuan | Informasi | Media/Protokol | Timing/kinerja | Req |
|---|---|---|---|---|---|
| IF-T2B | C1.3/C1.9 → C2.1 (serta penerusan C2.1 → C6.2 → C4.1) | record kehadiran, template enrolment, consent (`record:json, template:blob, consent:json`) | HTTPS/REST JSON, mTLS | p95 ≤2 s/record; retry backoff | IF1, FR10, FR13, SEC2 |
| IF-B2S | C2.5 → C3.1 → E4 SIAKAD | rekap sesi (`recap:json, ack:json`) | HTTPS REST (atau SOAP) | ≤60 s/sesi; idempotency `session_id` | IF2, FR14, PRF6 |
| IF-B2SSO | C2.8 → C3.3 → E5 SSO | auth request / token (`authRequest:json, token:string`) | OIDC atau SAML 2.0 over HTTPS | token ≤8 jam | IF3 |
| IF-T2NTP | C1.10 → E6 NTP | query waktu (`timeQuery:struct, timeReply:struct`) | NTPv4 UDP/123 | ≤15 menit; \|Δ\|≤1 s | IF4, FR5 |
| IF-B2GW | C2.6 → C3.2 → E7 Gateway | payload notifikasi (`message:json, deliveryStatus:string`) | HTTPS REST | ≤60 s; status kirim | IF5, FR11 |
| IF-UI2B | C5.1/C5.2 → C2.1, C2.1 → C2.2/C5.1/C6.3, C2.6 → C5.2 | perintah sesi, kueri, koreksi, view, alert, perintah hapus (`command:json, query:json, view:json`) | HTTPS REST | p95 ≤1 s @40 pengguna | IF6, FR7, FR8, FR12, SEC3, SEC4 |

## 8.6 ICD — antarmuka internal
| ID | Sumber → Tujuan | Informasi (elemen di spec) | Media | Timing |
|---|---|---|---|---|
| IF-I1 | C1.1 → C1.3 dan C1.3 → C1.5 | frame kamera & frame uji liveness (`frame:video`) | USB/MIPI & in-process | ≥15 fps |
| IF-I2 | C1.3 → C1.4 dan C1.4 → C1.3 | frame wajah & vektor embedding untuk enrolment (`frame:video, embedding:vector`) | in-process | ≤0,5 s |
| IF-I3 | C1.4 → C1.3 | identitas kandidat + skor kemiripan (`identity:string, score:double`) | in-process | ≤1 s |
| IF-I4 | C1.3 → C1.6, C1.3 → C1.8, C1.6 → C1.9 | record lokal & tampilan umpan balik (`record:struct, display:string`) | local storage / IPC | ≤100 ms |
| IF-I5 | C2.3 → C4.2 | record kehadiran tervalidasi (`record:struct`) | SQL | ≤200 ms |
| IF-I6 | C4.2 → C2.5 dan C4.2 → C2.6 | data baca rekap sesi & daftar mahasiswa belum tercatat (`recap:table`) | SQL | ≤2 s |
| IF-I7 | C2.1/C2.3/C6.1/C6.3 → C2.7 dan C2.7 → C4.3 | entri audit lintas-potong & simpan ke Audit Store (`auditEntry:struct`) | internal RPC & append-only SQL | ≤100 ms |
| IF-I8 | C2.4 → C2.3 | status kehadiran terfinalisasi (`status:enum`) | internal API | ≤100 ms |
| IF-I9 | C4.1 → C2.2, C2.2 → C1.7, C1.7 → C1.4 | roster + set template sesi aktif (`roster:table, templateSet:blob`) | SQL / HTTPS / local cache | ≤5 s saat buka sesi |
| IF-I10 | C5.3 → C2.1 → C6.1 → C4.4 | bukti persetujuan biometrik (`consentProof:struct`) | HTTPS REST & SQL | ≤500 ms |

## 8.7 SPOF analysis
| # | Komponen | Mode kegagalan | Dampak | Deteksi | Mitigasi | Residual |
|---|---|---|---|---|---|---|
| 1 | C4.1 Template DB | instance mati | verifikasi sesi baru gagal memuat template | health check | backup harian; template sesi di-cache di C1.7; restore ≤30 mnt | sesi baru tertunda |
| 2 | C2.1 API Gateway | satu titik masuk | sinkronisasi & perintah UI berhenti | health check | mode offline terminal (F4.2) & penetapan status mandiri di C1.3 | data tertunda |
| 3 | E4 SIAKAD / C3.1 | API tidak tersedia | rekap tertunda | retry gagal | antrean + retry ≤10 mnt + alert admin | rekap pending |
| 4 | C1.2 Compute Unit | laptop mati | kelas tanpa presensi | readiness monitor | laptop cadangan + koreksi manual dosen | manual |
| 5 | E6 NTP / C1.10 | waktu tidak tersedia | timestamp drift | selisih >1 s | jam monotonik + flag + alert (C1.10 langsung ke E6 tanpa bergantung backend) | record bertanda |
| 6 | C2.8 / C3.3 SSO | SSO down | dosen/admin tak bisa login | login gagal | token aktif tetap berlaku; akun break-glass + audit | akses terbatas |
| 7 | C1.6 Local Store | kapasitas penuh | verifikasi baru ditolak | alert 80% | auto-purge record tersinkron | gangguan singkat |

## 8.8 Keputusan Desain Final & ASSUMPTION
- **D1 (Penetapan status mandiri di terminal):** Terminal bekerja mandiri; status *Hadir/Terlambat* ditetapkan di `C1.3` (`F3` dengan aturan jendela waktu). Backend (`C2.4 Rule Engine`) memfinalisasi saat tutup sesi (menetapkan *Alfa*) dan memvalidasi status.
- **D2 (Time Client langsung ke NTP):** `C1.10 Time Client` terhubung langsung ke NTP eksternal (`E6`). Terminal tidak bergantung pada backend untuk waktu.
- **D3 (Enrolment di terminal):** Terminal membentuk template (embedding dari `C1.4`), menghapus citra mentah di terminal, lalu mengirim template lewat `C2.1 API Gateway` ke `C6.2 Enrolment Module` untuk disimpan ke `C4.1 Template DB`.
- **D4 (Penyimpanan consent):** Bukti consent disimpan di `C4.4 Consent Registry` melalui `C6.1 Consent Module`, sedangkan `C2.7 Audit Service` mencatat kejadiannya.
- **D5 (Liveness mendahului pencocokan):** `C1.3` mengirim frame ke `C1.5`; hanya jika liveness lolos, hasil pencocokan dari `C1.4` dipakai.
- **D6 (API Gateway pintu tunggal):** `C2.1 API Gateway` adalah satu-satunya pintu klien (terminal, UI dosen, UI admin, UI enrolment) ke backend setelah otorisasi `C2.8`.
- **D7 (Audit lintas-potong):** `C2.7 Audit Service` dipanggil dari `C2.1`, `C2.3`, `C6.1`, dan `C6.3`.
- **D8 (Makna `internal`):** `internal` berarti aliran kontrol di dalam satu zona tepercaya (terminal atau backend), bukan ICD lintas-zona. Satu-satunya link lintas-subsistem bertipe `internal` adalah `C6.3 → C4.1` (perintah hapus), dan keduanya berada di zona backend.
- **A-21:** Template sesi diunduh ke terminal saat buka sesi (maks 40 template).
- **A-22:** mTLS tersedia di terminal (sertifikat perangkat).
- **A-23:** Akun break-glass hanya untuk admin, tercatat di audit.

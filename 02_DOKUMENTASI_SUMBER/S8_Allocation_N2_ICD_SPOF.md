# S8 — Allocation, N2/ICD, SPOF

## 8.1 Deployment view (siapa jalan di mana)
| Host | Komponen |
|---|---|
| Laptop terminal (edge) | C1.1–C1.11, C5.3, C6.1, C6.2 |
| Server backend | C2.1–C2.8, C3.1–C3.4, C4.1–C4.4, C6.3 |
| Browser dosen/admin | C5.1, C5.2 |

Catatan penajaman S7: C1.7 menjadi **Roster & Template Cache** (ID tetap) karena pencocokan di edge memerlukan template sesi aktif.

## 8.2 Allocation matrix (function → component)
| Fungsi | Komponen primer | Pendukung | Interface | Requirement |
|---|---|---|---|---|
| F1.1 Open Session | C2.2 | C5.1, C1.7 | IF-UI2B, IF-I9 | FR7 |
| F1.2 Close Session | C2.2 | C5.1, C2.4 | IF-UI2B | FR8 |
| F2.1 Acquire Image | C1.1 | C1.3 | IF-I1 | OPS3 |
| F2.2 Detect Face | C1.4 | C1.2 | IF-I2 | FR1 |
| F2.3 Verify Liveness | C1.5 | C1.2 | IF-I3 | FR2, PRF5 |
| F2.4 Represent Face | C1.4 | C1.2 | IF-I2 | FR3 |
| F2.5 Match Identity | C1.4 | C1.7, C4.1 | IF-I3, IF-I9 | FR3, FR4, PRF3, PRF4 |
| F3 Determine Status | C2.4 | C2.3 | IF-I8 | FR6 |
| F4.1 Persist Record | C2.3 | C4.2 | IF-I5 | FR5 |
| F4.2 Buffer Record | C1.6 | C1.9 | IF-I4 | FR9, OPS4 |
| F4.3 Synchronize Record | C1.9 | C2.1, C2.3 | IF-T2B | FR10, IF1 |
| F5.1 Compile Recap | C2.5 | C4.2 | IF-I6 | FR14 |
| F5.2 Transmit Recap | C3.1 | C2.5 | IF-B2S | FR14, PRF6, IF2 |
| F6.1 Notify Student | C2.6 | C3.2 | IF-B2GW | FR11, IF5 |
| F6.2 Alert Administrator | C2.6 | C5.2 | IF-UI2B | FR12 |
| F7.1 Capture Consent | C6.1 | C5.3, C4.4 | IF-I10 | SEC1 |
| F7.2 Enrol Template | C6.2 | C1.4, C4.1 | IF-T2B | FR13, SEC2 |
| F7.3 Erase Biometric Data | C6.3 | C4.1, C4.3 | IF-UI2B | SEC3 |
| F8.1 Authenticate User | C2.8 | C3.3 | IF-B2SSO | IF3 |
| F8.2 Authorize Role | C2.1 | C2.8 | IF-UI2B | SEC4 |
| F9 Record Audit Trail | C2.7 | C4.3 | IF-I7 | SEC5 |
| F10 Present Feedback | C1.8 | C1.3, C5.1 | IF-I4 | FR15, IF6, PRF2 |
| F11 Monitor Readiness | C1.11 | C1.2 | internal | OPS2 |
| F12 Synchronize Time | C1.10 | C3.4 | IF-T2NTP | FR5, IF4 |

## 8.3 Cek komponen menganggur
| Komponen | Fungsi | Status |
|---|---|---|
| C1.1 | F2.1 | aktif |
| C1.2 | F2.2–F2.5, F11 | aktif |
| C1.3 | F2, F10 | aktif |
| C1.4 | F2.2, F2.4, F2.5, F7.2 | aktif |
| C1.5 | F2.3 | aktif |
| C1.6 | F4.2 | aktif |
| C1.7 | F1.1, F2.5 | aktif |
| C1.8 | F10 | aktif |
| C1.9 | F4.2, F4.3 | aktif |
| C1.10 | F12 | aktif |
| C1.11 | F11 | aktif |
| C2.1 | F4.3, F8.2 | aktif |
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
| C3.4 | F12 | aktif |
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

Kesimpulan: 24 fungsi teralokasi; 33 komponen aktif; **0 fungsi tanpa komponen, 0 komponen tanpa fungsi**.

## 8.4 N2 matrix (level subsistem)
Baris = pengirim, kolom = penerima. `—` = tidak ada aliran langsung.

| From \ To | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| S1 | — | record, batch sync | — | — | — | frame enrolment |
| S2 | roster, sesi, ambang | — | rekap, notif, auth, waktu | tulis/baca | view | template, consent |
| S3 | — | ack, token, status, waktu | — | — | — | — |
| S4 | — | hasil kueri | — | — | — | — |
| S5 | — | perintah/kueri | — | — | — | — |
| S6 | — | template/consent | — | — | — | — |

## 8.5 ICD — antarmuka eksternal
| ID | Sumber → Tujuan | Informasi | Media/Protokol | Timing/kinerja | Req |
|---|---|---|---|---|---|
| IF-T2B | C1.3/C1.9 → C2.1 | record kehadiran, template, consent | HTTPS/REST JSON, mTLS | p95 ≤2 s/record; retry backoff | IF1 |
| IF-B2S | C3.1 → E4 SIAKAD | rekap sesi | HTTPS REST (atau SOAP) | ≤60 s/sesi; idempotency `session_id` | IF2 |
| IF-B2SSO | C3.3 → E5 SSO | auth request / token | OIDC atau SAML 2.0 over HTTPS | token ≤8 jam | IF3 |
| IF-T2NTP | C1.10 → E6 NTP | query waktu | NTPv4 UDP/123 | ≤15 menit; \|Δ\|≤1 s | IF4 |
| IF-B2GW | C3.2 → E7 Gateway | payload notifikasi | HTTPS REST | ≤60 s; status kirim | IF5 |
| IF-UI2B | C5.1/C5.2 → C2.1 | perintah sesi, kueri, koreksi | HTTPS REST | p95 ≤1 s @40 pengguna | IF6 |

## 8.6 ICD — antarmuka internal
| ID | Sumber → Tujuan | Informasi | Media | Timing |
|---|---|---|---|---|
| IF-I1 | C1.1 → C1.3 | frame | USB/MIPI | ≥15 fps |
| IF-I2 | C1.3 → C1.4 | frame | in-process | ≤0,5 s |
| IF-I3 | C1.4 → C1.3 | identitas + skor | in-process | ≤1 s |
| IF-I4 | C1.3 → C1.6/C1.8 | record, tampilan | local | ≤100 ms |
| IF-I5 | C2.3 → C4.2 | record | SQL | ≤200 ms |
| IF-I6 | C2.5 → C4.2 | rekap (baca) | SQL | ≤2 s |
| IF-I7 | C2.7 → C4.3 | entri audit | append-only | ≤100 ms |
| IF-I8 | C2.4 → C2.3 | status | internal API | ≤100 ms |
| IF-I9 | C2.2 → C1.7 | roster + template sesi | HTTPS | ≤5 s saat buka sesi |
| IF-I10 | C6.1 → C4.4 | bukti consent | SQL | ≤500 ms |

## 8.7 SPOF analysis
| # | Komponen | Mode kegagalan | Dampak | Deteksi | Mitigasi | Residual |
|---|---|---|---|---|---|---|
| 1 | C4.1 Template DB | instance mati | verifikasi gagal total | health check | backup harian; template sesi di-cache di C1.7; restore ≤30 mnt | sesi baru tertunda |
| 2 | C2.1 API Gateway | satu titik masuk | sinkronisasi berhenti | health check | mode offline terminal (F4.2) | data tertunda |
| 3 | E4 SIAKAD / C3.1 | API tidak tersedia | rekap tertunda | retry gagal | antrean + retry ≤10 mnt + alert admin | rekap pending |
| 4 | C1.2 Compute Unit | laptop mati | kelas tanpa presensi | readiness monitor | laptop cadangan + koreksi manual dosen | manual |
| 5 | E6 NTP / C3.4 | waktu tidak tersedia | timestamp drift | selisih >1 s | jam monotonik + flag + alert | record bertanda |
| 6 | C2.8 / C3.3 SSO | SSO down | dosen/admin tak bisa login | login gagal | token aktif tetap berlaku; akun break-glass + audit | akses terbatas |
| 7 | C1.6 Local Store | kapasitas penuh | verifikasi baru ditolak | alert 80% | auto-purge record tersinkron | gangguan singkat |

## 8.8 ASSUMPTION
- A-21: template sesi diunduh ke terminal saat buka sesi (maks 40 template).
- A-22: mTLS tersedia di terminal (sertifikat perangkat).
- A-23: akun break-glass hanya untuk admin, tercatat di audit.

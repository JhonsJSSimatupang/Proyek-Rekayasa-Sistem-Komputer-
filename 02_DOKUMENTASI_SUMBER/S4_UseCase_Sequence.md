# S4 — Use Case & Sequence Diagram

## 4.1 Aktor
| Aktor | Jenis | Use case utama |
|---|---|---|
| Mahasiswa | Primer | UC-01, UC-02 |
| Dosen | Primer | UC-04, UC-05, UC-06 |
| Admin Akademik | Primer | UC-07, UC-08 |
| SIAKAD | Sekunder (sistem) | UC-04 |
| Gateway Notifikasi | Sekunder (sistem) | UC-10 |
| Scheduler (waktu) | Sekunder (sistem) | UC-10 |
| SSO Kampus | Sekunder (sistem) | UC-09 |

## 4.2 Use case diagram
```mermaid
flowchart LR
  M(("Mahasiswa")); D(("Dosen")); A(("Admin Akademik"))
  S1(("SIAKAD")); S2(("Gateway Notifikasi")); S3(("Scheduler")); S4(("SSO"))

  subgraph SoI["SiHADIR"]
    UC01(["UC-01 Enrol wajah + consent"])
    UC02(["UC-02 Verifikasi kehadiran"])
    UC03(["UC-03 Catat offline & sinkron"])
    UC04(["UC-04 Tutup sesi & rekap SIAKAD"])
    UC05(["UC-05 Buka sesi"])
    UC06(["UC-06 Koreksi manual"])
    UC07(["UC-07 Tangani alert spoofing"])
    UC08(["UC-08 Hapus template"])
    UC09(["UC-09 Login SSO"])
    UC10(["UC-10 Kirim notifikasi pengingat"])
    UC11(["UC-11 Verifikasi liveness"])
    UC12(["UC-12 Cocokkan identitas"])
  end

  M --> UC01
  M --> UC02
  D --> UC05
  D --> UC04
  D --> UC06
  A --> UC07
  A --> UC08
  D --> UC09
  A --> UC09
  S1 --- UC04
  S2 --- UC10
  S3 --- UC10
  S4 --- UC09
  UC02 -.->|include| UC11
  UC02 -.->|include| UC12
  UC04 -.->|include| UC03
```
Caption: garis putus-putus = `<<include>>`; aktor sistem di kanan adalah aktor sekunder.

## 4.3 UC-01 Enrol Wajah dengan Consent
| Item | Isi |
|---|---|
| Aktor primer / sekunder | Mahasiswa / Admin Akademik (pengawasan) |
| SN terkait | SN-04, SN-02, SN-01 |
| Requirement | SR-FR13, SR-SEC1, SR-SEC2, SR-SEC3 |
| Trigger | Mahasiswa memulai enrolment di terminal (jadwal enrolment atau atas arahan admin) |
| Pre-condition | Mahasiswa terdaftar di SIAKAD (A-07); belum ada template aktif atau sedang memperbarui; naskah consent versi terkini tersedia |
| Post-condition sukses | Template aktif tersimpan; consent tercatat (NIM, waktu, versi naskah); citra mentah terhapus ≤100 s |
| Post-condition gagal | Tidak ada template setengah jadi; penolakan consent tercatat di audit |

**Main flow**
1. Sistem menampilkan naskah consent versi X beserta tujuan, retensi, dan hak hapus.
2. Mahasiswa mencentang "setuju".
3. Sistem mengirim bukti consent lewat API Gateway ke Consent Module untuk disimpan di Consent Registry (`C4.4`), dan Audit Service mencatat kejadiannya.
4. Sistem meminta mahasiswa memposisikan wajah pada area tangkap.
5. Terminal menangkap 3–5 frame dan memeriksa kualitas (blur, pencahayaan, tepat satu wajah).
6. Terminal (`C1.4` → `C1.3`) mengekstrak embedding, membentuk template, dan menghapus citra mentah di terminal (<=100 s).
7. Terminal mengirim template lewat API Gateway (`C2.1`) ke Enrolment Module (`C6.2`), yang menyimpannya ke Template DB (`C4.1`).
8. Sistem menampilkan konfirmasi.

**Alternative flow**
- A1 (kualitas gagal): sistem menampilkan panduan perbaikan; ulangi langkah 4–5 maksimal 3 kali.
- A2 (consent ditolak): enrolment dibatalkan; tidak ada template; kejadian dicatat; mahasiswa tetap dapat hadir melalui koreksi manual dosen (UC-06).

**Exception / failure**
- E1 kamera tidak terdeteksi → pesan + status terminal *not ready* (SR-OPS2).
- E2 penyimpanan gagal → rollback transaksi, tidak ada template parsial.

**Kebutuhan khusus:** durasi ≤60 s per mahasiswa (A-11); UI berbahasa Indonesia (C-06).

## 4.4 UC-02 Verifikasi Kehadiran dengan Liveness
| Item | Isi |
|---|---|
| Aktor primer / sekunder | Mahasiswa / Dosen (memantau) |
| SN terkait | SN-01, SN-02 |
| Requirement | SR-FR1, SR-FR2, SR-FR3, SR-FR4, SR-FR5, SR-FR6, SR-FR15, SR-PRF1, SR-PRF2, SR-PRF3, SR-PRF4, SR-PRF5 |
| Trigger | Mahasiswa berdiri di depan terminal saat sesi berstatus OPEN |
| Pre-condition | Sesi OPEN; roster sesi tersedia (online atau cache); template aktif ada; jam terminal tersinkron |
| Post-condition sukses | Satu record kehadiran tersimpan (lokal + backend), status ditampilkan ≤2 s, audit tercatat |
| Post-condition gagal | Tidak ada record; percobaan tercatat; jika memenuhi ambang, alert spoofing dikirim |

**Main flow**
1. Kamera aktif; sistem mendeteksi wajah dalam area tangkap.
2. Sistem memverifikasi liveness (kedipan/gerak/tekstur kulit).
3. Jika live, sistem mengekstrak embedding.
4. Sistem mencocokkan hanya terhadap template mahasiswa pada roster sesi aktif.
5. Jika skor ≥ ambang, aplikasi terminal (`C1.3`) menentukan status (Hadir/Terlambat) menggunakan aturan jendela waktu dan waktu dari Time Client (`C1.10`).
6. Sistem menyimpan record (NIM, waktu, terminal, skor, status, sumber=auto) ke local store.
7. Sistem mengirim record ke backend secara asinkron.
8. Sistem menampilkan nama + status kepada mahasiswa.

**Alternative flow**
- A1 (liveness gagal): tolak verifikasi, tampilkan pesan; tambah penghitung percobaan; bila ≥3 dalam 5 menit → SR-FR12.
- A2 (tidak dikenali): tawarkan ulang maksimal 3 kali; jika tetap gagal, arahkan ke dosen untuk koreksi manual (UC-06).
- A3 (sudah tercatat): tampilkan "sudah tercatat"; tidak membuat record baru (idempoten).

**Exception / failure**
- E1 backend tidak terjangkau → record tetap disimpan lokal, status "tertunda sinkron" (SR-FR9).
- E2 offset jam >1 s → record diberi flag waktu tidak valid + alert ke dosen; record tidak dibuang.

**Kebutuhan khusus:** p95 ≤2 s (SR-PRF2); 40 mahasiswa ≤180 s (SR-PRF1); FAR ≤0,01% (SR-PRF3); FRR ≤3% (SR-PRF4); APCER/BPCER ≤5% (SR-PRF5).

## 4.5 UC-03 Catat Offline & Sinkronisasi
| Item | Isi |
|---|---|
| Aktor primer / sekunder | Dosen, Administrator Infrastruktur / Backend |
| SN terkait | SN-05 |
| Requirement | SR-FR9, SR-FR10, SR-OPS4, SR-IF1 |
| Trigger | Koneksi terminal→backend terputus saat sesi OPEN, atau pulih kembali |
| Pre-condition | Sesi OPEN; roster sudah di-cache; local store tersedia |
| Post-condition sukses | 0 record hilang, 0 duplikat; seluruh record tersinkron |
| Post-condition gagal | Record tetap di local store; kegagalan dilaporkan, tidak hilang diam-diam |

**Main flow**
1. Terminal mendeteksi kegagalan koneksi (timeout).
2. Terminal beralih ke mode offline dan menampilkan indikator.
3. Verifikasi tetap berjalan; setiap record ditulis ke local store dengan timestamp asli dan UUID.
4. Setelah koneksi pulih, terminal mengirim batch record (idempoten berdasarkan UUID).
5. Backend mengembalikan ack per record.
6. Terminal menandai record tersinkron dan menampilkan ringkasan.

**Alternative flow**
- A1 (record sudah ada di backend): backend mengabaikan duplikat, mengembalikan status "already exists".
- A2 (sebagian gagal): retry dengan backoff; sisa kegagalan dilaporkan ke dosen/admin.

**Exception / failure**
- E1 local store penuh → verifikasi baru ditolak dengan pesan jelas + alert (bukan kehilangan data senyap).
- E2 perangkat mati saat offline → record yang sudah ditulis tetap ada (write-ahead).

**Kebutuhan khusus:** mampu offline ≥60 menit (SR-OPS4); sinkron ≤5 menit setelah pulih (kriteria SR-FR10).

## 4.6 UC-04 Tutup Sesi & Rekap ke SIAKAD
| Item | Isi |
|---|---|
| Aktor primer / sekunder | Dosen / SIAKAD, Gateway Notifikasi |
| SN terkait | SN-03, SN-06, SN-13 |
| Requirement | SR-FR8, SR-FR11, SR-FR14, SR-PRF6, SR-IF2 |
| Trigger | Dosen menekan "Tutup Sesi" atau jadwal sesi berakhir |
| Pre-condition | Sesi OPEN; record tersedia (tersinkron atau di local store) |
| Post-condition sukses | Rekap diterima SIAKAD ≤10 menit; status sesi CLOSED; audit tercatat |
| Post-condition gagal | Rekap tersimpan dan ditandai "pending"; admin mendapat alert |

**Main flow**
1. Dosen menekan "Tutup Sesi"; sistem meminta konfirmasi.
2. Sistem menolak verifikasi baru.
3. Sistem menetapkan Alfa bagi mahasiswa yang belum tercatat.
4. Sistem menyusun rekap (NIM, status, waktu, sumber auto/manual).
5. Sistem mengirim rekap ke SIAKAD dengan kunci idempotensi `session_id`.
6. SIAKAD mengembalikan ack + receipt.
7. Sistem menampilkan ringkasan dan status pengiriman.

**Alternative flow**
- A1 (record belum tersinkron): sistem menyelesaikan sinkronisasi (UC-03) sebelum menyusun rekap.
- A2 (SIAKAD menolak validasi): tampilkan pesan, simpan rekap, alert admin.

**Exception / failure**
- E1 SIAKAD tidak tersedia → retry hingga 10 menit; setelah itu eskalasi + status pending.
- E2 sesi ditutup tanpa sengaja → pembukaan kembali hanya oleh admin, tercatat di audit (SN-07).

**Kebutuhan khusus:** ≤10 menit setelah tutup (SR-PRF6); notifikasi pengingat dikirim 10 menit sebelum tutup (SR-FR11).

## 4.7 Sequence diagram

### SD-01 Enrolment + consent
```mermaid
sequenceDiagram
  actor M as Mahasiswa
  participant UI as Enrolment UI (C5.3)
  participant T as Terminal App (C1.3)
  participant K as Kamera (C1.1)
  participant FR as Face Recog (C1.4)
  participant GW as API Gateway (C2.1)
  participant CM as Consent Module (C6.1)
  participant CR as Consent Registry (C4.4)
  participant EM as Enrolment Module (C6.2)
  participant DB as Template DB (C4.1)
  participant AL as Audit Service (C2.7)

  M->>UI: mulai enrolment & baca naskah consent vX
  M->>UI: centang setuju
  UI->>GW: consentOut (IF-I10)
  GW->>CM: consentOut (IF-I10)
  CM->>CR: simpan bukti consent (IF-I10)
  CM->>AL: catat kejadian consent (IF-I7)
  T->>K: capture 3-5 frame
  K-->>T: frame (IF-I1)
  T->>FR: frameOut (IF-I2)
  FR-->>T: embedOut (template embedding, IF-I2)
  T->>T: hapus citra mentah di terminal (<=100 s)
  T->>GW: enrolOut (template, IF-T2B)
  GW->>EM: enrolOut (IF-T2B)
  EM->>DB: tplOut -> tplStoreIn (simpan template, IF-T2B)
  T-->>M: konfirmasi enrolment
```

### SD-02 Verifikasi kehadiran + liveness
```mermaid
sequenceDiagram
  actor M as Mahasiswa
  participant K as Kamera (C1.1)
  participant TC as Time Client (C1.10)
  participant T as Status Rule / Terminal App (C1.3)
  participant LV as Liveness Engine (C1.5)
  participant FR as Face Recognition (C1.4)
  participant LS as Local Store (C1.6)
  participant SA as Sync Agent (C1.9)
  participant GW as API Gateway (C2.1)
  participant AS as Attendance Service (C2.3)

  M->>K: hadir fisik di depan terminal
  K->>T: camOut (frame, IF-I1)
  T->>LV: liveFrameOut (IF-I1)
  LV-->>T: liveOut (liveness OK)
  T->>FR: frameOut (hanya jika liveness lolos, IF-I2)
  FR->>FR: cocokkan dengan template sesi dari C1.7 (IF-I9)
  FR-->>T: matchOut (identitas + skor, IF-I3)
  TC-->>T: timeOut (waktu tersinkron)
  T->>T: tetapkan status Hadir/Terlambat (aturan jendela waktu, F3)
  T->>LS: recordOut (simpan record lokal, IF-I4)
  T-->>M: displayOut (nama + status <=2 s, IF-I4)
  LS->>SA: storeOut (IF-I4)
  SA->>GW: syncOut (batch/async record, IF-T2B)
  GW->>AS: apiOut -> recIn
```

### SD-03 Offline → sinkronisasi
```mermaid
sequenceDiagram
  participant T as Terminal (C1.3/C1.9)
  participant LS as Local Store (C1.6)
  participant GW as API Gateway (C2.1)
  participant AS as Attendance Service (C2.3)

  T->>GW: POST /records (IF-T2B)
  GW-->>T: timeout
  T->>T: mode offline (indikator aktif)
  T->>LS: tulis record (UUID + timestamp asli, IF-I4)
  Note over T,LS: verifikasi & penetapan status di C1.3 tetap berjalan
  T->>GW: batch POST /records via C1.9 (retry, IF-T2B)
  GW->>AS: teruskan record
  GW-->>T: 200 ack per record
  T->>LS: tandai tersinkron
  T-->>T: ringkasan 0 hilang / 0 duplikat
```

### SD-04 Tutup sesi → rekap SIAKAD
```mermaid
sequenceDiagram
  actor D as Dosen
  participant UI as UI Dosen (C5.1)
  participant GW as API Gateway (C2.1)
  participant SS as Session Service (C2.2)
  participant RE as Rule Engine (C2.4)
  participant AS as Attendance Service (C2.3)
  participant DB as Attendance DB (C4.2)
  participant RS as Recap Service (C2.5)
  participant SC as SIAKAD Connector (C3.1)
  participant SI as SIAKAD (E4)

  D->>UI: Tutup Sesi
  UI->>GW: uiOut (closeSession, IF-UI2B)
  GW->>SS: cmdOut (IF-UI2B)
  SS->>RE: sessionOut -> closeIn (pemicu tutup sesi)
  RE->>AS: statusOut -> statusIn (finalisasi status Alfa, IF-I8)
  AS->>DB: recOut -> recIn (simpan finalisasi, IF-I5)
  AS->>RS: doneOut -> trigIn (pemicu rekap)
  DB->>RS: recapOut -> recapIn (data rekap, IF-I6)
  RS->>SC: recapOut -> recapIn (IF-B2S)
  SC->>SI: POST /attendance-recap (idempotency key, IF-B2S)
  SI-->>SC: 201 + receipt
  GW-->>UI: viewOut -> viewIn (ringkasan + status terkirim)
```

## 4.8 ASSUMPTION
- A-11: enrolment ≤60 detik per mahasiswa.
- A-12: mahasiswa tidak login; identifikasi dilakukan lewat wajah, bukan akun.
- A-13: pembukaan kembali sesi yang sudah ditutup hanya oleh Admin Akademik (bukan dosen).

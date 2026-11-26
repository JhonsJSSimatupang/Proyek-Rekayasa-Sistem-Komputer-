# Panduan Membangun Model System Composer SiHADIR (Manual, Klik-per-Klik)

Dokumen ini memandu membangun `SiHADIR_Architecture.slx` **secara manual** di GUI System Composer.
Semua angka dan nama di sini diambil langsung dari `sihadir_arch_spec.m` (sumber kebenaran S7/S8),
jadi model yang kamu buat akan sama persis dengan yang diperiksa `verify_architecture_spec.m`.

| Yang dibangun | Jumlah |
|---|---|
| Subsistem (level 1) | 6 |
| Komponen (daun) | 32 |
| Port pada komponen | 100 |
| Interface (data interface di dictionary) | 16 |
| Link / konektor | 48 |
| Alokasi fungsi → komponen | 25 |

---

## 0. Cara cepat (kalau skrip bisa jalan)

Kalau `systemcomposer.createModel` sudah ada di MATLAB-mu, kamu **tidak perlu** klik manual:

```matlab
cd('03_MODEL_MATLAB')
verify_architecture_spec          % 15 pemeriksaan, harus LULUS
build_sihadir_architecture        % menghasilkan SiHADIR_Architecture.slx
verify_built_model                % 9 pemeriksaan pada model hasil
```

Sisanya di dokumen ini adalah **jalur manual**, dipakai kalau skrip gagal atau kalau dosen
meminta bukti bahwa kamu bisa membangunnya sendiri.

---

## 1. Cek prasyarat (30 detik)

Di Command Window:

```matlab
ver                                  % harus ada baris "System Composer"
which systemcomposer.createModel     % harus keluar path, bukan kosong
```

Kalau `which` kosong → toolbox belum terpasang, jalur manual ini juga akan gagal karena
menu System Composer tidak muncul. Jangan lanjut.

---

## 2. Kosakata yang dipakai di GUI

| Istilah | Arti praktis |
|---|---|
| **Architecture Model** | berkas `.slx` yang isinya komponen, bukan blok Simulink |
| **Component** | kotak di kanvas; bisa berisi sub-komponen (subsistem) |
| **Port** | titik masuk/keluar komponen, punya arah Input/Output |
| **Interface** | "kontrak data" (daftar elemen + tipe) yang dipasang ke port |
| **Interface Dictionary** | berkas `.sldd` tempat 16 interface disimpan agar bisa dipakai ulang |
| **Connector** | garis penghubung port Output → port Input |
| **Allocation** | pemetaan fungsi (F…) ke komponen pelaksana |

Aturan penting: **satu port hanya punya satu interface**, dan **konektor hanya boleh Output → Input**.

---

## 3. Langkah 1 — Buat model arsitektur

1. MATLAB → tab **Apps** → **System Composer**.
2. **New** → **Architecture Model** → *Blank Model*.
3. Simpan sebagai `SiHADIR_Architecture.slx` di folder `FINAL`.
4. Di kanvas akan ada satu komponen bernama `Component`. Nanti dijadikan `S1`.

---

## 4. Langkah 2 — Buat 6 subsistem

Klik kanvas (bukan komponen) → **Add Component** lima kali, lalu rename semuanya
(F2 atau klik nama) menjadi:

| No | Nama subsistem |
|---|---|
| 1 | `S1 Edge Terminal` |
| 2 | `S2 Backend Services` |
| 3 | `S3 Integration & Comms` |
| 4 | `S4 Data Management` |
| 5 | `S5 User Interfaces` |
| 6 | `S6 Identity & Privacy` |

Tip: tulis dengan format `ID + spasi + nama` supaya cocok dengan `verify_built_model`
yang mencocokkan nama komponen apa adanya.

---

## 5. Langkah 3 — Buat Interface Dictionary (16 interface)

1. Tab **Architecture** → **Interface Editor** (atau **Interfaces** → **Interface Editor**).
2. Klik **New Dictionary** → simpan sebagai `SiHADIR_Architecture_Interfaces.sldd`.
3. Hubungkan ke model: **Architecture** → **Link Dictionary** → pilih berkas tadi.
   (Kalau tidak ditautkan, port tidak akan bisa diberi interface.)
4. Buat 16 *data interface* dan isi elemennya sesuai tabel.

### 5.1 Tabel interface

| Interface | Elemen (nama : tipe) |
|---|---|
| `IF-T2B` | record:json, template:blob, consent:json |
| `IF-B2S` | recap:json, ack:json |
| `IF-B2SSO` | authRequest:json, token:string |
| `IF-T2NTP` | timeQuery:struct, timeReply:struct |
| `IF-B2GW` | message:json, deliveryStatus:string |
| `IF-UI2B` | command:json, query:json, view:json |
| `IF-I1` | frame:video |
| `IF-I2` | frame:video, embedding:vector |
| `IF-I3` | identity:string, score:double |
| `IF-I4` | record:struct, display:string |
| `IF-I5` | record:struct |
| `IF-I6` | recap:table |
| `IF-I7` | auditEntry:struct |
| `IF-I8` | status:enum |
| `IF-I9` | roster:table, templateSet:blob |
| `IF-I10` | consentProof:struct |

### 5.2 Pemetaan tipe (WAJIB — ini yang sering bikin error)

`json`, `blob`, `video`, `vector`, `struct`, `table`, `enum` **bukan tipe data MATLAB**.
Kalau diketik apa adanya, System Composer menolak. Pakai pemetaan ini:

| Tipe di dokumen | Tipe yang dipilih di GUI |
|---|---|
| json | `string` |
| string | `string` |
| blob / video / templateSet | `uint8` |
| vector / embedding | `double` |
| struct / auditEntry / consentProof / record / timeQuery / timeReply | `string` |
| table / roster | `string` |
| enum / status | `string` |
| double / score | `double` |

Argumen untuk laporan: tipe di S7/S8 adalah **tipe logis** (apa yang dipertukarkan),
sedangkan tipe di model adalah **tipe implementasi**. Yang penting konsisten antar port
pada satu link.

---

## 6. Langkah 4 — Buat 33 komponen

Buka `S1` (double-click) → **Add Component** sesuai jumlah, rename. Ulangi untuk S2..S6.

### S1 — Edge Terminal (11 komponen)
`C1.1 Camera` · `C1.2 Compute Unit` · `C1.3 Terminal Application` ·
`C1.4 Face Detection & Recognition` · `C1.5 Liveness Engine` · `C1.6 Local Record Store` ·
`C1.7 Roster & Template Cache` · `C1.8 Display` · `C1.9 Sync Agent` ·
`C1.10 Time Client` · `C1.11 Readiness Monitor`

### S2 — Backend Services (8 komponen)
`C2.1 API Gateway` · `C2.2 Session Service` · `C2.3 Attendance Service` · `C2.4 Rule Engine` ·
`C2.5 Recap Service` · `C2.6 Notification Service` · `C2.7 Audit Service` ·
`C2.8 Access Control Service`

### S3 — Integration & Comms (3 komponen)
`C3.1 SIAKAD Connector` · `C3.2 Notification Connector` · `C3.3 SSO Connector`

### S4 — Data Management (4 komponen)
`C4.1 Template DB` · `C4.2 Attendance DB` · `C4.3 Audit Store` · `C4.4 Consent Registry`

### S5 — User Interfaces (3 komponen)
`C5.1 Lecturer UI` · `C5.2 Admin Console` · `C5.3 Enrolment UI`

### S6 — Identity & Privacy (3 komponen)
`C6.1 Consent Module` · `C6.2 Enrolment Module` · `C6.3 Erasure Module`

---

## 7. Langkah 5 — Buat 72 port

Cara: klik komponen → **Add Port** (atau Ctrl+P) → rename → lalu di **Property Inspector**
set **Direction** (Input/Output) dan **Interface** (pilih dari dictionary).

`internal` pada kolom interface = **biarkan Interface kosong**.

### S1 — Edge Terminal

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C1.1 | camOut | Output | IF-I1 |
| C1.2 | statusOut | Output | *(kosong)* |
| C1.3 | camIn | Input | IF-I1 |
| C1.3 | matchIn | Input | IF-I3 |
| C1.3 | liveIn | Input | *(kosong)* |
| C1.3 | readyIn | Input | *(kosong)* |
| C1.3 | timeIn | Input | *(kosong)* |
| C1.3 | frameOut | Output | IF-I2 |
| C1.3 | liveFrameOut | Output | IF-I1 |
| C1.3 | recordOut | Output | IF-I4 |
| C1.3 | apiOut | Output | IF-T2B |
| C1.3 | displayOut | Output | IF-I4 |
| C1.4 | frameIn | Input | IF-I2 |
| C1.4 | tplIn | Input | IF-I9 |
| C1.4 | matchOut | Output | IF-I3 |
| C1.5 | frameIn | Input | IF-I1 |
| C1.5 | liveOut | Output | *(kosong)* |
| C1.6 | storeIn | Input | IF-I4 |
| C1.6 | storeOut | Output | IF-I4 |
| C1.7 | rosterIn | Input | IF-I9 |
| C1.7 | tplOut | Output | IF-I9 |
| C1.8 | dispIn | Input | IF-I4 |
| C1.9 | syncIn | Input | IF-I4 |
| C1.9 | syncOut | Output | IF-T2B |
| C1.10 | ntpOut | Output | IF-T2NTP |
| C1.10 | timeOut | Output | *(kosong)* |
| C1.11 | statusIn | Input | *(kosong)* |
| C1.11 | readyOut | Output | *(kosong)* |

### S2 — Backend Services

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C2.1 | termIn | Input | IF-T2B |
| C2.1 | syncIn | Input | IF-T2B |
| C2.1 | uiIn | Input | IF-UI2B |
| C2.1 | uiInAdmin | Input | IF-UI2B |
| C2.1 | apiOut | Output | *(kosong)* |
| C2.2 | rosterOut | Output | IF-I9 |
| C2.2 | sessionOut | Output | *(kosong)* |
| C2.3 | recIn | Input | *(kosong)* |
| C2.3 | recOut | Output | IF-I5 |
| C2.4 | statusOut | Output | IF-I8 |
| C2.5 | recapIn | Input | IF-I6 |
| C2.5 | recapOut | Output | IF-B2S |
| C2.6 | notifyOut | Output | IF-B2GW |
| C2.6 | alertOut | Output | IF-UI2B |
| C2.7 | auditOut | Output | IF-I7 |
| C2.8 | ssoOut | Output | IF-B2SSO |
| C2.8 | tokenOut | Output | *(kosong)* |

### S3 — Integration & Comms

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C3.1 | recapIn | Input | IF-B2S |
| C3.1 | recapOut | Output | IF-B2S |
| C3.2 | notifyIn | Input | IF-B2GW |
| C3.2 | notifyOut | Output | IF-B2GW |
| C3.3 | authIn | Input | IF-B2SSO |
| C3.3 | authOut | Output | IF-B2SSO |

### S4 — Data Management

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C4.1 | tplIn | Input | *(kosong)* |
| C4.1 | tplOut | Output | *(kosong)* |
| C4.2 | recIn | Input | IF-I5 |
| C4.2 | recapIn | Input | IF-I6 |
| C4.2 | recapOut | Output | IF-I6 |
| C4.3 | auditIn | Input | IF-I7 |
| C4.4 | consentIn | Input | IF-I10 |

### S5 — User Interfaces

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C5.1 | uiOut | Output | IF-UI2B |
| C5.1 | viewIn | Input | IF-UI2B |
| C5.2 | uiOut | Output | IF-UI2B |
| C5.2 | alertIn | Input | IF-UI2B |
| C5.3 | enrolOut | Output | IF-T2B |
| C5.3 | consentOut | Output | IF-I10 |

### S6 — Identity & Privacy

| Komponen | Port | Arah | Interface |
|---|---|---|---|
| C6.1 | consentIn | Input | IF-I10 |
| C6.1 | consentOut | Output | IF-I10 |
| C6.2 | frameIn | Input | *(kosong)* |
| C6.2 | tplOut | Output | IF-T2B |
| C6.3 | eraseOut | Output | IF-UI2B |
| C6.3 | tplDelOut | Output | *(kosong)* |

> Setelah selesai: total port di 33 komponen harus **72**. Hitung dengan cepat:
> `numel(SiHADIR_Architecture.Architecture.Components)` untuk subsistem,
> lalu jumlahkan `Ports` tiap komponen daun.

---

## 8. Langkah 6 — Sambung 27 link

Cara: tarik garis dari port Output ke port Input. Untuk link **antar subsistem**,
tarik dari port di dalam S1 langsung ke port di dalam S2 — System Composer otomatis
membuatkan port batas di kedua subsistem (inilah sebabnya jumlah port di level
subsistem bisa lebih dari 72; 72 hanya menghitung port komponen daun).

### 8.1 Dua belas link di dalam S1 (langsung, tanpa port batas)

| # | Dari | Ke | Interface |
|---|---|---|---|
| 1 | C1.1.camOut | C1.3.camIn | IF-I1 |
| 2 | C1.4.matchOut | C1.3.matchIn | IF-I3 |
| 3 | C1.5.liveOut | C1.3.liveIn | *(kosong)* |
| 4 | C1.11.readyOut | C1.3.readyIn | *(kosong)* |
| 5 | C1.3.recordOut | C1.6.storeIn | IF-I4 |
| 6 | C1.3.displayOut | C1.8.dispIn | IF-I4 |
| 7 | C1.6.storeOut | C1.9.syncIn | IF-I4 |
| 23 | C1.3.frameOut | C1.4.frameIn | IF-I2 |
| 24 | C1.3.liveFrameOut | C1.5.frameIn | IF-I1 |
| 25 | C1.7.tplOut | C1.4.tplIn | IF-I9 |
| 26 | C1.10.timeOut | C1.3.timeIn | *(kosong)* |
| 27 | C1.2.statusOut | C1.11.statusIn | *(kosong)* |

### 8.2 Lima belas link antar subsistem

| # | Dari | Ke | Interface |
|---|---|---|---|
| 8 | C1.3.apiOut | C2.1.termIn | IF-T2B |
| 9 | C1.9.syncOut | C2.1.syncIn | IF-T2B |
| 11 | C2.2.rosterOut | C1.7.rosterIn | IF-I9 |
| 12 | C2.3.recOut | C4.2.recIn | IF-I5 |
| 13 | C4.2.recapOut | C2.5.recapIn | IF-I6 |
| 14 | C2.5.recapOut | C3.1.recapIn | IF-B2S |
| 15 | C2.6.notifyOut | C3.2.notifyIn | IF-B2GW |
| 16 | C2.8.ssoOut | C3.3.authIn | IF-B2SSO |
| 17 | C2.7.auditOut | C4.3.auditIn | IF-I7 |
| 18 | C5.1.uiOut | C2.1.uiIn | IF-UI2B |
| 19 | C5.2.uiOut | C2.1.uiInAdmin | IF-UI2B |
| 20 | C6.1.consentOut | C4.4.consentIn | IF-I10 |
| 21 | C6.3.tplDelOut | C4.1.tplIn | *(kosong)* |
| 22 | C5.3.consentOut | C6.1.consentIn | IF-I10 |

### 8.3 Kenapa ada 18 port yang tidak disambung

72 port − 54 ujung konektor = **18 port** sengaja dibiarkan terbuka. Itu **titik batas sistem**
(tempat aktor/ sistem luar menempel), misalnya: kamera fisik, layar, SIAKAD, WhatsApp
Gateway, SSO UB, NTP server, mahasiswa, admin. Ini bukan kelalaian — di Bab 8 (N2/ICD)
port itulah yang dipakai untuk 6 ICD eksternal.

---

## 9. Langkah 7 — Alokasi 24 fungsi

System Composer menyimpan alokasi di *allocation scenario*. Untuk laporan S10, cara
paling ringkas dan sah:

1. Buka **Property Inspector** tiap komponen → isi field **Description** dengan
   `Functions: F2.1; F2.2` dst. (mudah diverifikasi manual)
2. Kalau ingin alokasi formal: **Architecture** → **Allocate** → buat *allocation set*,
   lalu alokasikan tiap fungsi ke komponen.

### Tabel alokasi

| Fungsi | Komponen | Fungsi | Komponen |
|---|---|---|---|
| F1.1 | C2.2 | F5.2 | C3.1 |
| F1.2 | C2.2 | F6.1 | C2.6 |
| F2.1 | C1.1 | F6.2 | C2.6 |
| F2.2 | C1.4 | F7.1 | C6.1 |
| F2.3 | C1.5 | F7.2 | C6.2 |
| F2.4 | C1.4 | F7.3 | C6.3 |
| F2.5 | C1.4 | F8.1 | C2.8 |
| F3 | C2.4 | F8.2 | C2.1 |
| F4.1 | C2.3 | F9 | C2.7 |
| F4.2 | C1.6 | F10 | C1.8 |
| F4.3 | C1.9 | F11 | C1.11 |
| F5.1 | C2.5 | F12 | C1.10 |

Catatan: `F2.2`, `F2.4`, `F2.5` dimiliki C1.4, bukan C1.2 — ini sudah dikoreksi
saat audit S10 (temuan E-04). Jangan "diperbaiki" lagi.

---

## 10. Langkah 8 — Simpan dan verifikasi

```matlab
save_system('SiHADIR_Architecture')

% cek angka
m = systemcomposer.loadModel('SiHADIR_Architecture.slx');
a = m.Architecture;
disp(numel(a.Components))              % harus 6  (subsistem)
n = 0;
for k = 1:numel(a.Components)
    kids = a.Components(k).Architecture.Components;
    fprintf('%s: %d komponen, %d port\n', a.Components(k).Name, numel(kids), ...
        sum(arrayfun(@(c) numel(c.Ports), kids)));
    n = n + sum(arrayfun(@(c) numel(c.Ports), kids));
end
fprintf('total port daun = %d\n', n)   % harus 72
```

Lalu jalankan pemeriksa yang sudah ada:

```matlab
verify_built_model        % 9 pemeriksaan M1..M9, target LULUS
```

---

## 11. Jebakan yang paling sering terjadi

| Gejala | Sebab | Solusi |
|---|---|---|
| Interface tidak muncul di dropdown port | dictionary belum ditautkan ke model | **Architecture → Link Dictionary** |
| "Invalid interface element type" | menulis `json`, `blob`, `struct` | pakai tabel pemetaan 5.2 |
| Garis tidak bisa ditarik | Output → Output | balik salah satu ujungnya |
| Port hilang saat link antar subsistem | normal | System Composer membuat port batas otomatis |
| Nama komponen berubah sendiri | ada karakter `/` | jangan pakai `/` di nama |
| `verify_built_model` gagal M3 | ada komponen nyasar di level 1 | komponen harus **di dalam** subsistem |
| Gagal M6 (arah port) | semua port default Input/Output salah | set Direction satu per satu; jangan lupa yang `internal` juga punya arah |

---

## 12. Checklist Verifikasi Akhir Kelompok

- [ ] `ver` menampilkan **System Composer**
- [ ] Model tersimpan sebagai `SiHADIR_Architecture.slx` di folder `FINAL`
- [ ] 6 subsistem, nama persis `S1 Edge Terminal` … `S6 Identity & Privacy`
- [ ] 33 komponen daun, tidak ada yang tertinggal di level 1
- [ ] 72 port pada komponen daun
- [ ] 16 interface di dictionary, dictionary tertaut ke model
- [ ] 27 link (57 konektor garis)
- [ ] 24 fungsi tercatat pada komponen yang benar
- [ ] `verify_built_model` → **LULUS (9 pemeriksaan)**
- [ ] Screenshot kanvas penuh untuk Lampiran A laporan

## Asumsi

- **ASSUMPTION-31**: tipe data implementasi pada 5.2 dipilih agar model bisa dibangun;
  tipe logis di S7/S8 tetap dipakai di dokumen requirement.
- **ASSUMPTION-32**: 18 port yang tidak tersambung adalah titik batas sistem untuk
  6 ICD eksternal di S8, bukan port mati.
- **ASSUMPTION-33**: alokasi fungsi dicatat di Description komponen; allocation set
  formal hanya dibuat bila dosen memintanya.

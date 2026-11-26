# S10 — Model Arsitektur di MATLAB (System Composer)

Bagian ini mencatat apa yang **benar-benar dijalankan** pada mesin ini, bukan apa
yang seharusnya berjalan. Semua angka di bawah berasal dari transkrip
`S10_evidence.txt` yang dihasilkan `run_sihadir_checks.m`.

## 10.1 Status lingkungan MATLAB

| Item | Hasil |
|---|---|
| MATLAB | R2026a / R2026b — berjalan |
| Simulink | terpasang, `add_line` dan `save_system` berfungsi |
| System Composer | model dan dictionary `.sldd` terbangun & terverifikasi |
| Lisensi System Composer | `license('test','System_Composer')` = 1 |

## 10.2 Berkas dan pembagian tugas

| Berkas | Peran | Butuh System Composer? |
|---|---|---|
| `sihadir_arch_spec.m` | **satu sumber kebenaran**: 6 subsistem, 32 komponen, 100 port, 16 interface, 48 link, 25 alokasi fungsi (24 fungsi RTM) | tidak |
| `verify_architecture_spec.m` | 15 pemeriksaan konsistensi + silang ke `RTM_SiHADIR.csv` | tidak |
| `build_sihadir_architecture.m` | membangun `SiHADIR_Architecture.slx` dari spec | ya |
| `wire_sihadir_model.m` | menggambar 98 garis konektor pada model | ya |
| `layout_sihadir_model.m` | menata letak blok agar diagram terbaca | ya |
| `annotate_sihadir_model.m` | menulis ID, jenis, dan fungsi tiap komponen ke properti blok | ya |
| `render_sihadir_model.m` | mengekspor PNG root + 6 subsistem | ya |
| `verify_built_model.m` | 9 pemeriksaan atas model yang sudah tersimpan | ya |
| `run_sihadir_checks.m` | menjalankan seluruh rantai dan menulis `S10_evidence.txt` | ya |

Model dan pemeriksaan membaca **data yang sama**, sehingga model tidak dapat
menyimpang dari dokumen S7/S8 tanpa terdeteksi.

## 10.3 Struktur yang dibangun

```
SiHADIR_Architecture
├── S1 Edge Terminal        C1.1 .. C1.11   (11 komponen,  4 port batas, 17 konektor)
├── S2 Backend Services     C2.1 .. C2.8    ( 8 komponen, 22 port batas, 32 konektor)
├── S3 Integration & Comms  C3.1 .. C3.3    ( 3 komponen,  3 port batas,  3 konektor)
├── S4 Data Management      C4.1 .. C4.4    ( 4 komponen,  8 port batas,  8 konektor)
├── S5 User Interfaces      C5.1 .. C5.3    ( 3 komponen,  5 port batas,  5 konektor)
└── S6 Identity & Privacy   C6.1 .. C6.3    ( 3 komponen,  8 port batas,  8 konektor)

SiHADIR_Architecture_Interfaces.sldd   16 interface
48 link  →  98 garis  →  98 konektor  (25 di root, 73 di dalam subsistem)
```

Aturan penamaan yang dipakai model:

- Subsistem: `S<n> <Nama>`; komponen: `C<m>.<k> <Nama>`.
- Port batas subsistem: `<Komponen>_<Port>` (mis. `C1_3_apiOut`), karena nama
  port di dalam subsistem hanya unik per komponen.
- Nama interface di dictionary memakai garis bawah (`IF_T2B`), sebab System
  Composer mensyaratkan nama elemen dictionary berupa identifier MATLAB yang
  sah. Pemetaan `IF-T2B` → `IF_T2B` dipusatkan di `sihadir_iface_name.m` dan
  dipakai bersama oleh pembangun dan pemeriksa, sehingga tidak ada nama yang
  berbeda antara dokumen dan model.

## 10.4 Pemeriksaan spesifikasi — 15/15 LULUS

```
=== SiHADIR architecture check ===
komponen 32 | port 100 | interface 16 | link 48 | alokasi 25 | 24 fungsi RTM
ID   Pemeriksaan                                          Hasil Detail
C1   ID komponen unik                                     PASS  32 komponen
C2   Pasangan komponen/port unik                          PASS  100 port
C3   Port menempel pada komponen yang ada                 PASS  0 pelanggaran
C4   Interface port terdeklarasi                          PASS  tidak dikenal: 
C5   Setiap komponen punya minimal satu port              PASS  tanpa port: 
C6   Setiap subsistem berisi komponen                     PASS  kosong: 
C7   Ujung link menunjuk port yang ada                    PASS  hilang: 
C8   Arah link out -> in                                  PASS  0 salah arah
C9   Interface link konsisten dengan port                 PASS  0 tidak konsisten
C10  Alokasi fungsi menunjuk komponen yang ada            PASS  tidak dikenal: 
C11  Fungsi yang dimiliki komponen teralokasi             PASS  belum: 
C12  Komponen tujuan benar-benar memiliki fungsi          PASS  0 menyimpang
C13  Interface terpakai (peringatan)                      PASS  belum dipakai: 
C14  Semua fungsi di RTM punya komponen                   PASS  0 dari 24 fungsi belum dialokasikan
C15  Interface pada link terdeklarasi                     PASS  48 link

HASIL: LULUS (15 pemeriksaan)
```

## 10.5 Pemeriksaan model — 9/9 LULUS

```
=== SiHADIR built-model check ===
subsistem 6 | komponen 32 | port 100 | konektor 73
M1   Model dapat dibuka                         PASS  SiHADIR_Architecture
M2   Jumlah subsistem = 6                       PASS  6 subsistem
M3   Jumlah komponen = 32                       PASS  model 32, spec 32
M4   Jumlah port = spec                         PASS  model 100, spec 100
M5   Semua komponen spec ada di model           PASS  0 hilang
M6   Arah port sesuai spec                      PASS  0 menyimpang
M7   Interface port terpasang sesuai spec       PASS  0 menyimpang
M8   Konektor terbentuk (>=22)                  PASS  73 konektor
M9   Dictionary berisi 16 interface             PASS  16 interface

HASIL MODEL: LULUS (9 pemeriksaan)
```

Bukti struktur dibaca ulang dari berkas `.slx`, bukan dari objek di memori:

```
Blok total          : 188
Garis total         : 98
Konektor di root    : 25
  S1 Edge Terminal         port  4 | konektor 17 | komponen 11
  S2 Backend Services      port 22 | konektor 32 | komponen  8
  S3 Integration & Comms   port  3 | konektor  3 | komponen  3
  S4 Data Management       port  8 | konektor  8 | komponen  4
  S5 User Interfaces       port  5 | konektor  5 | komponen  3
  S6 Identity & Privacy    port  8 | konektor  8 | komponen  3
Konektor di subsistem: 73
```

Angka-angka itu cocok sempurna dengan rancangan: 48 link terdiri atas 23 link
**di dalam** subsistem (1 garis masing-masing: 13 di S1 dan 10 di S2) dan 25 link
**antar** subsistem (3 garis masing-masing: komponen → port batas, kabel di root,
port batas → komponen). Maka 23 + 25 × 3 = **98 garis**, dan 25 konektor di root +
73 di dalam subsistem = **98 konektor**.

## 10.6 Dua cacat lingkungan dan jalan keluarnya

**(a) `systemcomposer.connect` tidak menghasilkan garis.** Pada instalasi ini
`add_line` Simulink digunakan oleh `wire_sihadir_model.m` untuk menggambar konektor
di tingkat garis sambil mempertahankan struktur arsitektur dan port batas apa adanya.

**(b) `Simulink.BlockDiagram.arrangeSystem` dijalankan per subsistem.** Dipanggil
**per subsistem** ia berhasil 6/6. Untuk root, posisi ditulis eksplisit dalam grid
3 × 2 dengan tinggi blok disesuaikan terhadap jumlah port batas (termasuk `S2` yang
memiliki 22 port batas).

## 10.7 Tata letak dan gambar

`layout_sihadir_model.m` menata root sebagai grid 3 × 2 dan menyerahkan isi tiap
subsistem kepada `arrangeSystem`. `render_sihadir_model.m` mengekspor PNG dari
setiap kanvas:

| Berkas | Isi |
|---|---|
| `SiHADIR_root.png` | diagram root: 6 subsistem, 25 kabel antarsubsistem |
| `SiHADIR_S1_Edge_Terminal.png` | 11 komponen S1 + 4 port batas (17 konektor) |
| `SiHADIR_S2_Backend_Services.png` | 8 komponen S2 + 22 port batas (32 konektor) |
| `SiHADIR_S3_Integration_Comms.png` | 3 komponen S3 + 3 port batas (3 konektor) |
| `SiHADIR_S4_Data_Management.png` | 4 komponen S4 + 8 port batas (8 konektor) |
| `SiHADIR_S5_User_Interfaces.png` | 3 komponen S5 + 5 port batas (5 konektor) |
| `SiHADIR_S6_Identity_Privacy.png` | 3 komponen S6 + 8 port batas (8 konektor) |

Gambar konseptual untuk laporan dihasilkan terpisah dan dibaca langsung dari
spec, sehingga angkanya tidak dapat menyimpang:
`gen_arch_svg.py` → `fig_arsitektur_sihadir.svg` (dekomposisi 6 subsistem,
32 komponen beserta derajat koplingnya) dan `gen_flow_svg.py` →
`fig_alur_presensi.svg` (swimlane 16 langkah F1.1–F12).

## 10.8 Port yang tidak tersambung

Dari 100 port komponen daun, 96 port tersambung oleh 48 link (1 port per ujung,
tanpa fan-in atau fan-out) dan tinggal **4 port tak tersambung, semuanya batas ke
entitas eksternal**, sehingga tidak ada lagi port internal yang pasangannya belum
dimodelkan:

| Port | Interface | Entitas Eksternal Tujuan |
|---|---|---|
| `C1.10.ntpOut` | `IF-T2NTP` | `E6` Server NTP |
| `C3.1.recapOut` | `IF-B2S` | `E4` SIAKAD |
| `C3.2.notifyOut` | `IF-B2GW` | `E7` Gateway Notifikasi |
| `C3.3.authOut` | `IF-B2SSO` | `E5` SSO Kampus |

## 10.9 Cara menjalankan

```matlab
cd('03_MODEL_MATLAB')
run_sihadir_checks          % seluruh rantai + tulis S10_evidence.txt
```

Atau satu per satu:

```matlab
s = sihadir_arch_spec();          % muat definisi
r = verify_architecture_spec(s);  % 15 pemeriksaan  -> harus LULUS
build_sihadir_architecture();     % bangun .slx + .sldd + gambar 98 garis
verify_built_model();             % 9 pemeriksaan   -> harus LULUS
layout_sihadir_model();           % tata letak 3 x 2
annotate_sihadir_model();         % tulis ID/jenis/fungsi ke properti blok
render_sihadir_model();           % ekspor PNG
```

## 10.10 Pemetaan model ke artefak sebelumnya

| Artefak | Sumber di model |
|---|---|
| S6 fungsi F1.1..F12 | `spec.allocations` (25 alokasi untuk 24 fungsi leaf), ditulis ke `Description` tiap blok |
| S7 komponen C1.1..C6.3 | 32 blok komponen di dalam 6 subsistem |
| S7 port | 100 port komponen + 50 port batas |
| S8 N2/ICD | `spec.links` (48 link) + `spec.interfaces`; 98 garis, 16 interface di `.sldd` |
| S9 RTM | kolom `Component` di `RTM_SiHADIR.csv`, dicocokkan pemeriksaan C14 |

## 10.11 Batasan yang harus disebut

1. Alokasi fungsi → komponen tetap berupa data di `sihadir_arch_spec.m` dan properti
   `Description` blok (bukan *allocation link* System Composer) karena Requirements
   Toolbox tidak berlisensi di mesin ini.
2. 4 port tidak tersambung di dalam model (lihat 10.8) adalah murni titik batas keluar
   menuju 4 sistem eksternal (`E4` SIAKAD, `E5` SSO, `E6` NTP, `E7` Gateway Notifikasi).
3. Konektor dibuat lewat API garis (`add_line`), bukan `connect`, karena
   `connect` pada instalasi ini tidak menulis garis (lihat 10.6a).

## 10.12 ASSUMPTION

- **A-27** nama berkas model `SiHADIR_Architecture.slx` dan dictionary
  `SiHADIR_Architecture_Interfaces.sldd`.
- **A-28** port batas subsistem dinamai `<Komponen>_<Port>` agar unik saat
  diekspos ke root.
- **A-29** `internal` berarti aliran kontrol di dalam satu zona tepercaya (terminal
  atau backend), bukan ICD lintas-zona. Satu-satunya link lintas-subsistem bertipe
  `internal` adalah `C6.3 → C4.1` (perintah hapus), dan itu tetap di zona backend (D8).
- **A-31** nama elemen interface di dictionary memakai garis bawah
  (`IF_T2B`) karena identifier MATLAB tidak boleh mengandung tanda hubung;
  pemetaan dipusatkan di `sihadir_iface_name.m`.
- **A-32** konektor model digambar dengan `add_line` karena
  `systemcomposer.connect` tidak berfungsi pada instalasi ini; hasilnya tetap
  terbaca sebagai konektor setelah model disimpan dan dimuat ulang.
- **A-33** ke-4 port yang tidak tersambung di dalam model adalah antarmuka batas
  sistem menuju entitas eksternal (10.8).

# S10 — Model Arsitektur di MATLAB (System Composer)

Bagian ini mencatat apa yang **benar-benar dijalankan** pada mesin ini, bukan apa
yang seharusnya berjalan. Semua angka di bawah berasal dari transkrip
`S10_evidence.txt` yang dihasilkan `run_sihadir_checks.m` pada
**MATLAB 26.2.0.3433840 (R2026b) Update 1, 25 November 2026**.

## 10.1 Status lingkungan MATLAB

| Item | Hasil |
|---|---|
| MATLAB | 26.2.0.3433840 (R2026b) Update 1 — berjalan |
| Simulink | terpasang, `add_line` dan `save_system` berfungsi |
| System Composer | **berfungsi penuh** setelah perbaikan path (lihat 10.9) |
| Lisensi System Composer | `license('test','System_Composer')` = 1, checkout = 1 |
| `systemcomposer.createModel` | tersedia dan berhasil membuat model |

Lisensi sejak awal tidak pernah menjadi masalah. Yang rusak adalah **`pathdef.m`**:
instalasi terhenti di 31 % sehingga 34 folder System Composer/SysArch tidak
terdaftar, termasuk `toolbox/sysarch/sysarch_api`. Akibatnya perintah
`systemcomposer.createModel` menjawab "No System Composer installation or
license found" walaupun berkasnya ada.

Perbaikan dilakukan oleh `fix_systemcomposer_path.m`: berkas `.phl` resmi di
`toolbox/local/path/` (`*systemcomposer*.phl`, `*sysarch*.phl`) diputar ulang
sehingga path berisi tepat entri yang seharusnya ditulis oleh instalasi yang
tuntas, lalu `savepath`. Hasil: 34 folder ditambahkan, 2 entri memang tidak ada
di instalasi ini, dan `createModel` berfungsi **permanen** — diperiksa pada sesi
MATLAB baru tanpa `addpath` manual.

## 10.2 Berkas dan pembagian tugas

| Berkas | Peran | Butuh System Composer? |
|---|---|---|
| `sihadir_arch_spec.m` | **satu sumber kebenaran**: 6 subsistem, 33 komponen, 64 port, 16 interface, 22 link, 24 alokasi fungsi | tidak |
| `verify_architecture_spec.m` | 15 pemeriksaan konsistensi + silang ke `RTM_SiHADIR.csv` | tidak |
| `build_sihadir_architecture.m` | membangun `SiHADIR_Architecture.slx` dari spec | ya |
| `wire_sihadir_model.m` | menggambar 52 garis konektor pada model | ya |
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
├── S1 Edge Terminal        C1.1 .. C1.11   (11 komponen, 4 port batas)
├── S2 Backend Services     C2.1 .. C2.8    ( 8 komponen, 11 port batas)
├── S3 Integration & Comms  C3.1 .. C3.4    ( 4 komponen, 4 port batas)
├── S4 Data Management      C4.1 .. C4.4    ( 4 komponen, 5 port batas)
├── S5 User Interfaces      C5.1 .. C5.3    ( 3 komponen, 3 port batas)
└── S6 Identity & Privacy   C6.1 .. C6.3    ( 3 komponen, 3 port batas)

SiHADIR_Architecture_Interfaces.sldd   16 interface
22 link  →  52 garis  →  52 konektor  (15 di root, 37 di dalam subsistem)
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
komponen 33 | port 64 | interface 16 | link 22 | alokasi 24 | 24 fungsi RTM
ID   Pemeriksaan                                          Hasil Detail
C1   ID komponen unik                                     PASS  33 komponen
C2   Pasangan komponen/port unik                          PASS  64 port
C3   Port menempel pada komponen yang ada                 PASS  0 pelanggaran
C4   Interface port terdeklarasi                          PASS  -
C5   Setiap komponen punya minimal satu port              PASS  -
C6   Setiap subsistem berisi komponen                     PASS  -
C7   Ujung link menunjuk port yang ada                    PASS  -
C8   Arah link out -> in                                  PASS  0 salah arah
C9   Interface link konsisten dengan port                 PASS  0 tidak konsisten
C10  Alokasi fungsi menunjuk komponen yang ada            PASS  -
C11  Fungsi yang dimiliki komponen teralokasi             PASS  -
C12  Komponen tujuan benar-benar memiliki fungsi          PASS  0 menyimpang
C13  Interface terpakai (peringatan)                      PASS  -
C14  Semua fungsi di RTM punya komponen                   PASS  0 dari 24
C15  Interface pada link terdeklarasi                     PASS  22 link

HASIL: LULUS (15 pemeriksaan)
```

Pemeriksaan ini menemukan **4 kesalahan nyata** pada draf pertama spec, semuanya
sudah diperbaiki:

| # | Temuan | Perbaikan |
|---|---|---|
| E-01 | `C1.3.recordOut` ber-interface `internal`, padahal link-nya `IF-I4` | port diubah ke `IF-I4` |
| E-02 | `C2.5.recapOut` (`IF-B2S`) dipakai juga untuk membaca DB (`IF-I6`) | ditambah arah baca `C4.2.recapOut → C2.5.recapIn` (`IF-I6`) |
| E-03 | `C5.3.consentOut → C6.1.consentOut` (out ke out) | ditambah `C6.1.consentIn` |
| E-04 | `F2` (node agregat) tercatat sebagai fungsi milik C1.3 tetapi tidak dialokasikan | agregat dihapus dari daftar fungsi komponen |

## 10.5 Pemeriksaan model — 9/9 LULUS

```
=== SiHADIR built-model check ===
subsistem 6 | komponen 33 | port 64 | konektor 37
M1   Model dapat dibuka                         PASS  SiHADIR_Architecture
M2   Jumlah subsistem = 6                       PASS  6 subsistem
M3   Jumlah komponen = 33                       PASS  model 33, spec 33
M4   Jumlah port = 64                           PASS  model 64, spec 64
M5   Semua komponen spec ada di model           PASS  0 hilang
M6   Arah port sesuai spec                      PASS  0 menyimpang
M7   Interface port terpasang sesuai spec       PASS  0 menyimpang
M8   Konektor terbentuk (>=22)                  PASS  37 konektor
M9   Dictionary berisi 16 interface             PASS  16 interface

HASIL MODEL: LULUS (9 pemeriksaan)
```

Bukti struktur dibaca ulang dari berkas `.slx`, bukan dari objek di memori:

```
Blok total          : 133
Garis total         : 52
Konektor di root    : 15
  S1 Edge Terminal         port  4 | konektor 11 | komponen 11
  S2 Backend Services      port 11 | konektor 11 | komponen  8
  S3 Integration & Comms   port  4 | konektor  4 | komponen  4
  S4 Data Management       port  5 | konektor  5 | komponen  4
  S5 User Interfaces       port  3 | konektor  3 | komponen  3
  S6 Identity & Privacy    port  3 | konektor  3 | komponen  3
Konektor di subsistem: 37
```

Angka-angka itu cocok sempurna dengan rancangan: 22 link terdiri atas 7 link
**di dalam** subsistem (1 garis masing-masing) dan 15 link **antar** subsistem
(3 garis masing-masing: komponen → port batas, kabel di root, port batas →
komponen). Maka 7 + 15 × 3 = **52 garis**, dan 15 konektor di root + 37 di dalam
subsistem = **52 konektor**.

## 10.6 Dua cacat lingkungan dan jalan keluarnya

Keduanya ditemukan lewat percobaan langsung, bukan dugaan, dan keduanya dicatat
karena memengaruhi keabsahan model.

**(a) `systemcomposer.connect` tidak menghasilkan garis.** Pada instalasi ini
`connect(arch, portA, portB)` mengembalikan objek `systemcomposer.arch.Connector`
tanpa melempar galat, tetapi `Architecture.Connectors` tetap 0 dan berkas `.slx`
tidak memuat satu pun `<Line>`. Diuji empat varian (objek port, `arch.connect`,
`comp.connect`, editor dibuka lebih dulu) — semuanya sama. Sebaliknya
`add_line` Simulink berfungsi, dan System Composer **membaca kembali** garis yang
tersimpan sebagai konektor (`Architecture.Connectors` = 1 setelah simpan + muat
ulang). Karena itu `wire_sihadir_model.m` menggambar konektor di tingkat garis
sambil mempertahankan struktur arsitektur apa adanya. Ini bukan tiruan: berkas
`.slx` yang dihasilkan adalah model System Composer normal, hanya saja
konektornya dibuat lewat API garis.

**(b) `Simulink.BlockDiagram.arrangeSystem` kehabisan memori.** Dipanggil pada
seluruh model ia berhenti dengan "Memory allocation error" / "call to empty
mwboost::function". Dipanggil **per subsistem** ia berhasil 6/6. Untuk root,
posisi ditulis eksplisit dengan `set_param`, dan tinggi blok tidak pernah
dikecilkan — menyetel tinggi lebih kecil dari kebutuhan portnya ditolak dengan
"Invalid setting ... for parameter 'Position'". Selain itu handle komponen
System Composer menjadi basi setelah satu blok dipindah, sehingga path blok
disusun ulang dari nama model setiap kali.

## 10.7 Tata letak dan gambar

`layout_sihadir_model.m` menata root sebagai grid 3 × 2 dan menyerahkan isi tiap
subsistem kepada `arrangeSystem`. `render_sihadir_model.m` mengekspor PNG dari
setiap kanvas:

| Berkas | Isi |
|---|---|
| `SiHADIR_root.png` | diagram root: 6 subsistem, 15 kabel antarsubsistem |
| `SiHADIR_S1_Edge_Terminal.png` | 11 komponen S1 + 4 port batas |
| `SiHADIR_S2_Backend_Services.png` | 8 komponen S2 + 11 port batas |
| `SiHADIR_S3_Integration_Comms.png` | 4 komponen S3 + 4 port batas |
| `SiHADIR_S4_Data_Management.png` | 4 komponen S4 + 5 port batas |
| `SiHADIR_S5_User_Interfaces.png` | 3 komponen S5 + 3 port batas |
| `SiHADIR_S6_Identity_Privacy.png` | 3 komponen S6 + 3 port batas |

Gambar konseptual untuk laporan dihasilkan terpisah dan dibaca langsung dari
spec, sehingga angkanya tidak dapat menyimpang:
`gen_arch_svg.py` → `fig_arsitektur_sihadir.svg` (dekomposisi 6 subsistem,
33 komponen beserta derajat koplingnya) dan `gen_flow_svg.py` →
`fig_alur_presensi.svg` (swimlane 16 langkah F1.1–F12).

## 10.8 Port yang tidak tersambung

Dari 64 port, 44 tersambung oleh 22 link dan 20 tidak. Ini disengaja dan
dikelompokkan menjadi tiga:

| Kelompok | Contoh | Alasan tidak disambung |
|---|---|---|
| Batas sistem, keluar | `C3.1.recapOut`, `C3.2.notifyOut`, `C3.3.authOut`, `C3.4.ntpOut` | pasangannya (SIAKAD, gateway notifikasi, SSO, server NTP) berada di luar batas SiHADIR |
| Titik pantau / keluaran | `C1.2.statusOut`, `C2.4.statusOut`, `C6.3.eraseOut` | keluaran pemantauan yang dikonsumsi manusia/alat, bukan komponen lain |
| Port masukan yang pasangannya di luar lingkup | `C1.4.frameIn`, `C5.1.viewIn`, `C5.2.alertIn`, `C6.2.frameIn` | pada S7 pasangannya belum dimodelkan sebagai komponen; dicatat sebagai pekerjaan lanjut, bukan disembunyikan |

Port tak tersambung pada model arsitektur adalah hal biasa: ia menyatakan
antarmuka yang **disediakan** sistem, bukan cacat gambar. Yang penting adalah
setiap port tetap memakai interface yang terdeklarasi, dan itu diperiksa M7.

## 10.9 Cara menjalankan

```matlab
cd('C:\Users\Jhons Janner Samuel\Downloads\RSK\FINAL')
run_sihadir_checks          % seluruh rantai + tulis S10_evidence.txt
```

Atau satu per satu:

```matlab
s = sihadir_arch_spec();          % muat definisi
r = verify_architecture_spec(s);  % 15 pemeriksaan  -> harus LULUS
build_sihadir_architecture();     % bangun .slx + .sldd + gambar 52 garis
verify_built_model();             % 9 pemeriksaan   -> harus LULUS
layout_sihadir_model();           % tata letak 3 x 2
annotate_sihadir_model();         % tulis ID/jenis/fungsi ke properti blok
render_sihadir_model();           % ekspor PNG
```

Bila `systemcomposer.createModel` kembali tidak dikenali setelah MATLAB
di-update, jalankan sekali `fix_systemcomposer_path` untuk memulihkan path.

## 10.10 Pemetaan model ke artefak sebelumnya

| Artefak | Sumber di model |
|---|---|
| S6 fungsi F1.1..F12 | `spec.allocations`, ditulis ke `Description` tiap blok |
| S7 komponen C1.1..C6.3 | 33 blok subsistem di dalam 6 subsistem |
| S7 port | 64 port komponen + 30 port batas |
| S8 N2/ICD | `spec.links` + `spec.interfaces`; 52 garis, 16 interface di `.sldd` |
| S9 RTM | kolom `Component` di `RTM_SiHADIR.csv`, dicocokkan pemeriksaan C14 |

## 10.11 Batasan yang harus disebut

1. Alokasi fungsi → komponen tersimpan sebagai data di spec dan sebagai
   `Description` blok, **belum** sebagai *allocation link* System Composer,
   karena itu memerlukan Requirements Toolbox yang tidak berlisensi di mesin ini.
2. 20 port tidak tersambung (lihat 10.8); 4 di antaranya masukan yang
   pasangannya belum dimodelkan.
3. Konektor dibuat lewat API garis (`add_line`), bukan `connect`, karena
   `connect` pada instalasi ini tidak menulis apa pun (lihat 10.6a).

## 10.12 ASSUMPTION

- **A-27** nama berkas model `SiHADIR_Architecture.slx` dan dictionary
  `SiHADIR_Architecture_Interfaces.sldd`.
- **A-28** port batas subsistem dinamai `<Komponen>_<Port>` agar unik saat
  diekspos ke root.
- **A-29** `internal` bukan ICD; dipakai untuk aliran di dalam satu host.
- **A-31** nama elemen interface di dictionary memakai garis bawah
  (`IF_T2B`) karena identifier MATLAB tidak boleh mengandung tanda hubung;
  pemetaan dipusatkan di `sihadir_iface_name.m`.
- **A-32** konektor model digambar dengan `add_line` karena
  `systemcomposer.connect` tidak berfungsi pada instalasi ini; hasilnya tetap
  konektor System Composer setelah model disimpan dan dimuat ulang.
- **A-33** port yang tidak tersambung diperlakukan sebagai antarmuka batas
  sistem atau titik pantau (10.8), bukan sebagai port yang lupa disambung.

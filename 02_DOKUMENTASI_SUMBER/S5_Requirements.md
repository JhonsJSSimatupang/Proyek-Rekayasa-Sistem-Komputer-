# S5 — Requirements v2 (36 requirement, EARS)

Aturan: satu requirement = satu `shall` (atomik); setiap statement memakai pola EARS; setiap acceptance criteria memuat **unit–kondisi–ambang**.
Prioritas: M = Must, S = Should. Verifikasi: I = Inspection, A = Analysis, D = Demonstration, T = Test.

## 5.1 Functional (15)
| ID | Statement (EARS) | Pola | SN | P | Verif | Acceptance criteria |
|---|---|---|---|---|---|---|
| SR-FR1 | Ketika kamera terminal aktif dan sebuah wajah berada di area tangkap, sistem harus mendeteksi keberadaan wajah pada frame dalam ≤0,5 detik. | Event | SN-01 | M | T | Pada 200 frame kondisi standar (300–700 lux): ≥98% frame berisi tepat satu wajah terdeteksi ≤0,5 s; 0 deteksi pada 50 frame tanpa wajah. |
| SR-FR2 | Ketika wajah terdeteksi, sistem harus memverifikasi liveness sebelum melakukan pencocokan identitas dan menolak subjek yang gagal liveness. | Event | SN-02 | M | T | Dari 50 subjek yang gagal liveness, 0 menghasilkan record kehadiran; setiap keputusan liveness tercatat di audit. |
| SR-FR3 | Ketika subjek lolos verifikasi liveness, sistem harus mencocokkan embedding wajahnya dan menghasilkan tepat satu kandidat identitas terbaik beserta skor kemiripan. | Event | SN-02 | M | T | 100 subjek terdaftar → 100% menghasilkan tepat 1 kandidat + skor; 100 subjek tidak terdaftar → 100% "tidak ada kandidat di atas ambang". |
| SR-FR4 | Ketika sesi presensi berstatus OPEN, sistem harus membatasi kandidat pencocokan hanya pada mahasiswa yang terdaftar pada roster sesi tersebut. | State | SN-02 | M | T | 50 percobaan oleh mahasiswa terdaftar di kelas lain → 0 record dibuat pada sesi ini. |
| SR-FR5 | Ketika kehadiran diverifikasi, sistem harus mencatat waktu kejadian memakai waktu tersinkron NTP dan menyimpannya bersama record. | Event | SN-03 | M | T | 100 record uji memiliki field waktu; selisih terhadap referensi NTP ≤1 s pada 10 pengukuran selama 2 jam. |
| SR-FR6 | Ketika record kehadiran dibentuk, sistem harus menetapkan status Hadir, Terlambat, atau Alfa berdasarkan jendela waktu mata kuliah. | Event | SN-03 | M | T | 30 kasus batas (tepat batas, −1 s, +1 s) → 100% sesuai aturan; 0 status di luar tiga nilai. |
| SR-FR7 | Ketika dosen memilih "Buka Sesi" untuk sesi terjadwal, sistem harus mengaktifkan sesi dan memuat roster peserta dari SIAKAD atau cache. | Event | SN-06 | M | D | 10 sesi uji: sesi OPEN ≤5 s; roster 40/40; bila SIAKAD tak tersedia, roster dari cache dan ditandai. |
| SR-FR8 | Ketika dosen mengonfirmasi "Tutup Sesi", sistem harus menutup sesi sehingga verifikasi baru ditolak dan mahasiswa yang belum tercatat ditetapkan Alfa. | Event | SN-06 | M | D | Setelah tutup, 100% verifikasi baru ditolak; jumlah Alfa = 40 − jumlah tercatat. |
| SR-FR9 | Jika koneksi terminal ke backend terputus selama sesi OPEN, sistem harus tetap mencatat kehadiran ke penyimpanan lokal dengan timestamp asli dan UUID. | Unwanted | SN-05 | M | T | Simulasi putus 30 menit, 40 verifikasi → 40/40 record lengkap (NIM, waktu, UUID); 0 hilang. |
| SR-FR10 | Ketika koneksi terminal ke backend pulih, sistem harus mengirim seluruh record tertunda secara otomatis dan idempoten. | Event | SN-05 | M | T | Sinkron selesai ≤5 menit; 0 hilang, 0 duplikat pada 10 skenario. |
| SR-FR11 | Ketika tersisa 10 menit sebelum sesi berakhir, sistem harus mengirim notifikasi kepada setiap mahasiswa pada roster yang belum tercatat. | Event | SN-13 | S | T | 5 sesi uji: 100% mahasiswa belum tercatat menerima pesan ≤60 s; mahasiswa tercatat tidak menerima. |
| SR-FR12 | Jika satu terminal mendeteksi ≥3 kegagalan liveness dalam 5 menit, sistem harus mengirim alert ke konsol Admin Akademik. | Unwanted | SN-07 | S | T | 10 simulasi: alert muncul ≤30 s setelah percobaan ke-3, memuat ID terminal, ruang, waktu. |
| SR-FR13 | Ketika mahasiswa menyelesaikan alur enrolment, sistem harus membentuk dan menyimpan satu template wajah yang terhubung ke NIM. | Event | SN-04 | M | D | 20 enrolment → 20 template unik (1 per NIM); ≥19/20 dikenali pada percobaan pertama kondisi standar. |
| SR-FR14 | Ketika sesi ditutup, sistem harus menyusun rekap kehadiran dan mengirimkannya ke SIAKAD. | Event | SN-03 | M | T | 10 sesi uji: 10/10 rekap diterima; 40 baris (NIM, status, waktu); ack tersimpan. |
| SR-FR15 | Setelah verifikasi selesai, sistem harus menampilkan nama/NIM dan status kehadiran mahasiswa pada layar terminal. | Event | SN-12 | M | D | 40 verifikasi: 40/40 menampilkan nama + status ≤2 s; 0 data mahasiswa lain tampil. |

## 5.2 Performance (6)
| ID | Statement | Pola | SN | P | Verif | Acceptance |
|---|---|---|---|---|---|---|
| SR-PRF1 | Sistem harus memverifikasi 40 mahasiswa berturut-turut dalam satu sesi dalam ≤180 detik. | Ubiquitous | SN-01 | M | T | 3 simulasi kelas 40 → seluruh verifikasi selesai ≤180 s. |
| SR-PRF2 | Sistem harus menyelesaikan satu verifikasi (deteksi, liveness, pencocokan, umpan balik) dalam ≤2 detik pada persentil ke-95. | Ubiquitous | SN-01, SN-12 | M | T | p95 dari 200 verifikasi kondisi standar ≤2 s. |
| SR-PRF3 | Sistem harus memiliki False Acceptance Rate ≤0,01%. | Ubiquitous | SN-02 | M | T | ≥10.000 perbandingan impostor → ≤1 kecocokan palsu. |
| SR-PRF4 | Sistem harus memiliki False Rejection Rate ≤3%. | Ubiquitous | SN-02 | M | T | 300 percobaan mahasiswa terdaftar → ≤9 ditolak pada percobaan pertama. |
| SR-PRF5 | Sistem harus memiliki APCER ≤5% dan BPCER ≤5% pada anti-spoofing. | Ubiquitous | SN-02 | M | T | 200 serangan → ≤10 diterima; 200 subjek asli → ≤10 ditolak. |
| SR-PRF6 | Sistem harus mengirim rekap ke SIAKAD dalam ≤10 menit setelah sesi ditutup. | Event | SN-03 | M | T | 10 sesi uji → 10/10 terkirim ≤10 menit. |

## 5.3 Interface (6)
| ID | Statement | Pola | SN | P | Verif | Acceptance |
|---|---|---|---|---|---|---|
| SR-IF1 | Terminal harus mengirim record kehadiran ke backend melalui HTTPS/REST (JSON) memuat NIM, session_id, timestamp, UUID, skor, status, dengan respons ≤2 detik per record. | Ubiquitous | SN-08 | M | T | 100 record uji: 100% skema valid; p95 respons ≤2 s; payload tidak valid → 4xx tercatat. |
| SR-IF2 | Backend harus mengirim rekap ke API SIAKAD memakai kunci idempotensi session_id dan menerima ack berisi receipt dalam ≤60 detik per sesi. | Ubiquitous | SN-03, SN-08 | M | T | 10 sesi → 10 ack; pengiriman ulang session_id sama → 0 duplikat. |
| SR-IF3 | Backend harus mengautentikasi dosen dan admin melalui SSO kampus (OIDC atau SAML 2.0) dan hanya menerima token bertanda tangan valid dengan masa berlaku ≤8 jam. | Ubiquitous | SN-08, SN-10 | M | T | 20 login akun valid → 20 berhasil; token palsu/kedaluwarsa → 100% ditolak. |
| SR-IF4 | Terminal dan backend harus menyinkronkan waktu ke NTP kampus minimal setiap 15 menit dan menjaga selisih ≤1 detik. | Ubiquitous | SN-08, SN-03 | M | T | 10 pengukuran/2 jam: selisih ≤1 s; log interval ≤15 menit. |
| SR-IF5 | Backend harus mengirim notifikasi ke gateway WhatsApp/e-mail melalui HTTPS API dan menerima status pengiriman ≤60 detik. | Ubiquitous | SN-08, SN-13 | S | T | 20 notifikasi uji → 20 status ≤60 s; payload memuat NIM, MK, waktu, tautan. |
| SR-IF6 | Antarmuka dosen dan admin harus mengambil/mengirim data via API backend dengan respons ≤1 detik untuk 95% permintaan pada 40 pengguna bersamaan. | Ubiquitous | SN-12 | S | T | Uji beban 40 pengguna → p95 ≤1 s; 0 error 5xx. |

## 5.4 Security & Privacy (5)
| ID | Statement | Pola | SN | P | Verif | Acceptance |
|---|---|---|---|---|---|---|
| SR-SEC1 | Sistem harus meminta dan mencatat persetujuan eksplisit sebelum enrolment wajah dimulai, menyimpan NIM, waktu, dan versi naskah consent. | Event | SN-04 | M | D | 20 enrolment → 20 consent tercatat; tanpa centang → 0/10 enrolment lolos. |
| SR-SEC2 | Setelah embedding berhasil dibentuk, sistem harus menghapus citra wajah mentah dalam ≤100 detik. | Event | SN-04 | M | T | 20 enrolment → pemeriksaan penyimpanan: 0 berkas citra mentah ≤100 s. |
| SR-SEC3 | Ketika Admin Akademik mengajukan penghapusan template atas permintaan mahasiswa, sistem harus menghapus template dan mencatatnya di audit log ≤24 jam. | Event | SN-04 | M | T | 10 permintaan → 10 template terhapus; wajah tidak dikenali pada 10 percobaan; entri audit ada. |
| SR-SEC4 | Sistem harus membatasi akses berdasarkan peran (mahasiswa, dosen, admin, auditor) dan menolak akses tanpa token SSO valid. | Ubiquitous | SN-10 | M | T | 20 percobaan akses lintas peran → 20 ditolak; akses tanpa token → 100% ditolak. |
| SR-SEC5 | Sistem harus mencatat buka/tutup sesi, koreksi manual, enrolment, penghapusan template, dan alert spoofing ke audit log append-only. | Ubiquitous | SN-07, SN-11 | M | T | 50 aksi uji → 50 entri (aktor, waktu, objek, aksi); edit/hapus via aplikasi → 0 berhasil. |

## 5.5 Operational & Environmental (4)
| ID | Statement | Pola | SN | P | Verif | Acceptance |
|---|---|---|---|---|---|---|
| SR-OPS1 | Backend harus tersedia ≥99% pada jam kuliah 07.00–21.00 WIB. | Ubiquitous | SN-05 | M | A | Log monitoring 4 minggu: downtime ≤1% dari total jam kuliah. |
| SR-OPS2 | Ketika terminal dinyalakan, sistem harus menjalankan self-test (kamera, koneksi backend, sinkronisasi waktu, ruang penyimpanan) dan menampilkan status siap/tidak siap ≤60 detik. | Event | SN-09 | M | D | 10 boot → 10/10 status ≤60 s; kamera dicabut → "tidak siap" + penyebab. |
| SR-OPS3 | Sistem harus mempertahankan akurasi pengenalan pada pencahayaan 300–700 lux dan memberi peringatan bila di luar rentang. | State | SN-02 | S | T | Pada 300/500/700 lux → FRR ≤3%; pada 100 lux → peringatan tampil. |
| SR-OPS4 | Sistem harus mampu beroperasi offline minimal 60 menit per sesi tanpa kehilangan record. | State | SN-05 | M | T | Offline 60 menit, 40 verifikasi → 40/40 record utuh dan tersinkron setelah pulih. |

## 5.6 Pemeriksaan kualitas
- Jumlah `shall` per statement: 1 (kecuali SR-IF3 yang memuat autentikasi + validasi token; lihat catatan).
- Setiap statement punya trigger/state/condition atau bersifat ubiquitous yang jelas.
- Semua acceptance criteria memuat ambang numerik + kondisi + unit.
- Tidak ada duplikat: SR-FR14 (perilaku menyusun & mengirim) berbeda dari SR-PRF6 (batas waktu); SR-FR2 (kewajiban menolak) berbeda dari SR-PRF5 (laju kesalahan).
- Distribusi: 15 FR, 6 PRF, 6 IF, 5 SEC, 4 OPS = **36**; prioritas M=31, S=5.

## 5.7 ASSUMPTION
- A-14: ambang kemiripan wajah ditetapkan saat kalibrasi (bukan requirement), disimpan sebagai parameter.
- A-15: SR-IF3 dipertahankan sebagai satu requirement antarmuka; aspek kontrol akses ada di SR-SEC4.

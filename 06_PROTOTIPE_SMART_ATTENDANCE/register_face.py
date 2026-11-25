
import os
import re
import cv2
import time
import subprocess
import sys
import face_recognition
import numpy as np

from pathlib import Path
from datetime import datetime

#Paths 
BASE_DIR   = Path(__file__).parent
FACES_DIR  = BASE_DIR / "data" / "faces"
FACES_DIR.mkdir(parents=True, exist_ok=True)

# ─── Konfigurasi 
TARGET_PHOTOS     = 5        # jumlah foto yang diambil per mahasiswa (makin besar = makin lama)
AUTO_CAPTURE      = True     # True = otomatis ambil foto saat wajah stabil
AUTO_INTERVAL     = 1      # jeda antar auto-capture (detik)
BLUR_THRESHOLD    = 30.0     # makin tinggi = makin ketat (cek kejelasan foto)
MIN_FACE_SIZE     = 90      # ukuran minimum wajah (pixel) agar foto valid

# ─── Warna, agar selaras di UI. format: (B, G, R)
C_GREEN   = (34, 197, 94)
C_RED     = (60,  60, 220)
C_YELLOW  = (0,  200, 220)
C_WHITE   = (255, 255, 255)
C_BLACK   = (0,   0,   0)
C_GRAY    = (160, 160, 160)
C_DARK    = (25,  25,  25)
C_BLUE    = (220, 130,  30)
C_CYAN    = (220, 200,  50)


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT FORM — NIM & NAMA via keyboard di jendela OpenCV|| MEMUDAHKAN gui

def draw_input_screen(frame: np.ndarray, nim: str, name: str,
                      active_field: str, error_msg: str) -> np.ndarray:
    """Render form input di atas frame kamera (semi-transparan)."""
    h, w = frame.shape[:2]
    overlay = frame.copy()


    px, py, pw, ph = w // 2 - 280, h // 2 - 160, 560, 320
    cv2.rectangle(overlay, (px, py), (px + pw, py + ph), (20, 20, 30), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Border panel
    cv2.rectangle(frame, (px, py), (px + pw, py + ph), C_BLUE, 2)

    # Judul
    cv2.putText(frame, "REGISTRASI MAHASISWA",
                (px + 100, py + 35), cv2.FONT_HERSHEY_DUPLEX, 0.75, C_YELLOW, 1, cv2.LINE_AA)
    cv2.line(frame, (px + 20, py + 50), (px + pw - 20, py + 50), C_BLUE, 1)

    # Field NIM
    nim_color  = C_CYAN if active_field == "nim" else C_GRAY
    name_color = C_CYAN if active_field == "name" else C_GRAY

    cv2.putText(frame, "NIM :", (px + 30, py + 90),
                cv2.FONT_HERSHEY_PLAIN, 1.2, C_WHITE, 1, cv2.LINE_AA)
    nim_box_color = C_CYAN if active_field == "nim" else (70, 70, 80)
    cv2.rectangle(frame, (px + 100, py + 72), (px + pw - 30, py + 100), nim_box_color, 2)
    nim_display = nim + ("_" if active_field == "nim" and int(time.time() * 2) % 2 == 0 else "")
    cv2.putText(frame, nim_display, (px + 110, py + 93),
                cv2.FONT_HERSHEY_PLAIN, 1.3, nim_color, 1, cv2.LINE_AA)

    # Field Nama
    cv2.putText(frame, "Nama:", (px + 30, py + 145),
                cv2.FONT_HERSHEY_PLAIN, 1.2, C_WHITE, 1, cv2.LINE_AA)
    name_box_color = C_CYAN if active_field == "name" else (70, 70, 80)
    cv2.rectangle(frame, (px + 100, py + 127), (px + pw - 30, py + 155), name_box_color, 2)
    name_display = name + ("_" if active_field == "name" and int(time.time() * 2) % 2 == 0 else "")
    cv2.putText(frame, name_display, (px + 110, py + 148),
                cv2.FONT_HERSHEY_PLAIN, 1.3, name_color, 1, cv2.LINE_AA)

    # Petunjuk tombol
    hints = [
        "TAB     → pindah field",
        "ENTER   → lanjut ambil foto",
        "ESC     → batal / keluar",
    ]
    for i, hint in enumerate(hints):
        cv2.putText(frame, hint, (px + 30, py + 195 + i * 22),
                    cv2.FONT_HERSHEY_PLAIN, 0.95, C_GRAY, 1, cv2.LINE_AA)

    # Error
    if error_msg:
        cv2.putText(frame, f"! {error_msg}", (px + 30, py + 285),
                    cv2.FONT_HERSHEY_PLAIN, 1.0, C_RED, 1, cv2.LINE_AA)

    return frame


def get_student_info(cap) -> tuple[str, str] | None:
    """
    Tampilkan form input di atas feed kamera.
    Kembalikan (nim, name) atau None jika dibatalkan.
    """
    nim          = ""
    name         = ""
    active_field = "nim"
    error_msg    = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = draw_input_screen(frame, nim, name, active_field, error_msg)
        cv2.imshow("Smart Attendance - Registrasi", frame)

        key = cv2.waitKey(30) & 0xFF

        if key == 27:   # 27 = ESC
            return None

        elif key == 9:  # 9 = TAB — pindah field
            active_field = "name" if active_field == "nim" else "nim"
            error_msg    = ""

        elif key == 13:  # ENTER — validasi & lanjut
            nim  = nim.strip()
            name = name.strip()

            if not nim:
                active_field = "nim"
                error_msg    = "NIM tidak boleh kosong"
            elif not name:
                active_field = "name"
                error_msg    = "Nama tidak boleh kosong"
            elif not re.fullmatch(r"[0-9]+", nim):
                active_field = "nim"
                error_msg    = "NIM hanya boleh angka"
            else:
                return nim, name

        elif key == 8:  # Backspace
            if active_field == "nim":
                nim = nim[:-1]
            else:
                name = name[:-1]
            error_msg = ""

        elif 32 <= key <= 126:  # karakter printable
            ch = chr(key)
            if active_field == "nim":
                if ch.isdigit():
                    nim += ch
                error_msg = "" if ch.isdigit() else "NIM hanya boleh angka"
            else:
                name      += ch
                error_msg  = ""
def check_blur(gray: np.ndarray) -> float:
    """Laplacian variance — makin tinggi makin tajam."""
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def check_brightness(gray: np.ndarray) -> float:
    return float(np.mean(gray))

def quality_ok(frame: np.ndarray, face_loc: tuple) -> tuple[bool, str]:
    """
    Periksa kualitas frame.
    Kembalikan (ok, pesan_masalah).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = check_blur(gray)
    if blur < BLUR_THRESHOLD:
        return False, f"Foto buram (skor: {blur:.0f})"

    brightness = check_brightness(gray)
    if brightness < 40:
        return False, "Terlalu gelap"
    if brightness > 230:
        return False, "Terlalu terang"

    top, right, bottom, left = face_loc
    face_h = bottom - top
    if face_h < MIN_FACE_SIZE:
        return False, f"Wajah terlalu kecil, dekatkan ke kamera"

    return True, ""
def draw_capture_ui(frame: np.ndarray, nim: str, name: str,
                    photo_count: int, target: int,
                    face_loc: tuple | None, quality_msg: str,
                    last_saved: np.ndarray | None,
                    auto_progress: float,
                    status_msg: str) -> None:
    h, w = frame.shape[:2]

    # ── Info mahasiswa (atas) 
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 55), C_DARK, -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    cv2.putText(frame, f"NIM: {nim}   Nama: {name}",
                (12, 22), cv2.FONT_HERSHEY_DUPLEX, 0.60, C_YELLOW, 1, cv2.LINE_AA)
    cv2.putText(frame,
                f"Foto: {photo_count}/{target}   " +
                ("SPACE = ambil foto manual  |  " if not AUTO_CAPTURE else "") +
                "ESC = batal  |  ENTER = selesai",
                (12, 44), cv2.FONT_HERSHEY_PLAIN, 0.95, C_GRAY, 1, cv2.LINE_AA)

    #Kotak wajah 
    if face_loc:
        top, right, bottom, left = face_loc
        ok = not quality_msg
        color = C_GREEN if ok else C_YELLOW

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Sudut dekoratif
        cl, ct = 14, 3
        for (x, y, dx, dy) in [(left, top, 1, 1), (right, top, -1, 1),
                                (left, bottom, 1, -1), (right, bottom, -1, -1)]:
            cv2.line(frame, (x, y), (x + dx * cl, y), color, ct)
            cv2.line(frame, (x, y), (x, y + dy * cl), color, ct)

        # Auto-capture progress bar di bawah kotak wajah
        if AUTO_CAPTURE and ok and auto_progress > 0:
            bar_w = right - left
            filled = int(bar_w * auto_progress)
            cv2.rectangle(frame, (left, bottom + 6), (right, bottom + 14), (60, 60, 60), -1)
            cv2.rectangle(frame, (left, bottom + 6), (left + filled, bottom + 14), C_GREEN, -1)

    #Status di bawah layar
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, h - 50), (w, h), C_DARK, -1)
    cv2.addWeighted(overlay2, 0.75, frame, 0.25, 0, frame)

    if quality_msg:
        cv2.putText(frame, f"! {quality_msg}",
                    (12, h - 28), cv2.FONT_HERSHEY_PLAIN, 1.1, C_RED, 1, cv2.LINE_AA)
    elif status_msg:
        cv2.putText(frame, status_msg,
                    (12, h - 28), cv2.FONT_HERSHEY_PLAIN, 1.1, C_GREEN, 1, cv2.LINE_AA)
    else:
        mode = "AUTO — posisikan wajah dan tahan diam" if AUTO_CAPTURE \
               else "MANUAL — tekan SPACE untuk ambil foto"
        cv2.putText(frame, mode,
                    (12, h - 28), cv2.FONT_HERSHEY_PLAIN, 1.1, C_CYAN, 1, cv2.LINE_AA)

    # Progress bar foto
    bar_total = w - 24
    bar_fill  = int(bar_total * photo_count / max(target, 1))
    cv2.rectangle(frame, (12, h - 14), (w - 12, h - 6), (60, 60, 60), -1)
    cv2.rectangle(frame, (12, h - 14), (12 + bar_fill, h - 6), C_GREEN, -1)
    cv2.putText(frame, f"{photo_count}/{target}",
                (w // 2 - 12, h - 7), cv2.FONT_HERSHEY_PLAIN, 0.8, C_WHITE, 1)

    # ── Preview foto terakhir (pojok kanan atas) 
    if last_saved is not None:
        thumb = cv2.resize(last_saved, (100, 80))
        frame[8 : 88, w - 108 : w - 8] = thumb
        cv2.rectangle(frame, (w - 108, 8), (w - 8, 88), C_GREEN, 1)
        cv2.putText(frame, "Foto terakhir",
                    (w - 108, 102), cv2.FONT_HERSHEY_PLAIN, 0.8, C_GRAY, 1)

def capture_photos(cap, nim: str, name: str) -> int:
    """
    Loop pengambilan foto wajah.
    Kembalikan jumlah foto yang berhasil disimpan.
    """
    # Buat folder mahasiswa. format: nim_nama
    folder_name  = f"{nim}_{name.replace(' ', '_')}"
    student_dir  = FACES_DIR / folder_name
    student_dir.mkdir(parents=True, exist_ok=True)

    # Hapus foto lama jika ada
    for old in student_dir.glob("*.jpg"):
        old.unlink()
    photo_count  = 0
    last_capture = 0.0
    last_saved   = None
    status_msg   = ""
    status_until = 0.0
    auto_start   = 0.0  
    print(f"\n[REG] Memulai pengambilan foto untuk: {nim} | {name}")
    print(f"      Target: {TARGET_PHOTOS} foto | Folder: {student_dir}\n")

    while photo_count < TARGET_PHOTOS:
        ret, frame = cap.read()
        if not ret:
            break

        now      = time.time()
        display  = frame.copy()

        # Deteksi wajah (kecil dulu untuk kecepatan)
        small    = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb      = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs     = face_recognition.face_locations(rgb, model="hog")

        face_loc    = None
        quality_msg = ""
        auto_prog   = 0.0

        if locs:
            top_s, right_s, bottom_s, left_s = locs[0]
            face_loc = (top_s * 2, right_s * 2, bottom_s * 2, left_s * 2)

            ok, quality_msg = quality_ok(frame, face_loc)

            if ok:
                # Hitung progres auto-capture
                if AUTO_CAPTURE:
                    if auto_start == 0.0:
                        auto_start = now
                    elapsed   = now - auto_start
                    auto_prog = min(elapsed / AUTO_INTERVAL, 1.0)

                    if elapsed >= AUTO_INTERVAL and (now - last_capture) >= AUTO_INTERVAL:
                        _save_photo(frame, student_dir, photo_count)
                        last_saved   = frame.copy()
                        photo_count += 1
                        last_capture = now
                        auto_start   = 0.0
                        status_msg   = f"Foto {photo_count} tersimpan!"
                        status_until = now + 1.5
                        print(f"  [FOTO {photo_count}] Auto-capture OK")
            else:
                auto_start = 0.0  # reset jika kualitas buruk

        else:
            quality_msg = "Wajah tidak terdeteksi"
            auto_start  = 0.0

        # Status sementara (flash message)
        if now > status_until:
            status_msg = ""

        draw_capture_ui(display, nim, name, photo_count, TARGET_PHOTOS,
                        face_loc, quality_msg, last_saved,
                        auto_prog, status_msg if now <= status_until else "")

        cv2.imshow("Smart Attendance - Registrasi", display)
        key = cv2.waitKey(30) & 0xFF

        if key == 27:   # ESC — batalkan
            print("  [BATAL] Pengambilan foto dibatalkan.")
            return 0

        elif key == 32 and not AUTO_CAPTURE:  # SPACE — manual capture
            if face_loc and not quality_msg:
                _save_photo(frame, student_dir, photo_count)
                last_saved   = frame.copy()
                photo_count += 1
                last_capture = now
                status_msg   = f"Foto {photo_count} tersimpan!"
                status_until = now + 1.5
                print(f"  [FOTO {photo_count}] Manual capture OK")
            else:
                print(f"  [SKIP] Kualitas kurang: {quality_msg}")

        elif key == 13 and photo_count > 0:  # ENTER — selesai lebih awal
            print(f"  [DONE] Selesai lebih awal dengan {photo_count} foto.")
            break

    print(f"\n[OK] {photo_count} foto disimpan di: {student_dir}\n")
    return photo_count

def _save_photo(frame: np.ndarray, folder: Path, index: int) -> None:
    filename = folder / f"face_{index + 1:02d}.jpg"
    cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

def show_summary(cap, nim: str, name: str, photo_count: int) -> bool:
    start = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        overlay = frame.copy()
        px, py, pw, ph = w // 2 - 240, h // 2 - 130, 480, 260
        cv2.rectangle(overlay, (px, py), (px + pw, py + ph), (15, 15, 25), -1)
        cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
        cv2.rectangle(frame, (px, py), (px + pw, py + ph), C_GREEN, 2)

        cv2.putText(frame, "REGISTRASI BERHASIL",
                    (px + 95, py + 35), cv2.FONT_HERSHEY_DUPLEX, 0.72, C_GREEN, 1, cv2.LINE_AA)
        cv2.line(frame, (px + 20, py + 50), (px + pw - 20, py + 50), C_GREEN, 1)

        cv2.putText(frame, f"NIM  : {nim}",
                    (px + 30, py + 85), cv2.FONT_HERSHEY_PLAIN, 1.1, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Nama : {name}",
                    (px + 30, py + 110), cv2.FONT_HERSHEY_PLAIN, 1.1, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Foto : {photo_count} gambar tersimpan",
                    (px + 30, py + 135), cv2.FONT_HERSHEY_PLAIN, 1.1, C_GREEN, 1, cv2.LINE_AA)

        cv2.line(frame, (px + 20, py + 155), (px + pw - 20, py + 155), (60, 60, 80), 1)

        cv2.putText(frame, "[E] Encode sekarang (siap untuk absensi)",
                    (px + 30, py + 180), cv2.FONT_HERSHEY_PLAIN, 1.0, C_YELLOW, 1, cv2.LINE_AA)
        cv2.putText(frame, "[N] Daftar mahasiswa berikutnya",
                    (px + 30, py + 202), cv2.FONT_HERSHEY_PLAIN, 1.0, C_CYAN, 1, cv2.LINE_AA)
        cv2.putText(frame, "[Q] Keluar",
                    (px + 30, py + 224), cv2.FONT_HERSHEY_PLAIN, 1.0, C_GRAY, 1, cv2.LINE_AA)

        cv2.imshow("Smart Attendance - Registrasi", frame)
        key = cv2.waitKey(30) & 0xFF

        if key in (ord("e"), ord("E")):
            return "encode"
        elif key in (ord("n"), ord("N")):
            return "next"
        elif key in (ord("q"), ord("Q"), 27):
            return "quit"

#  MAIN LOOP
def run_encode():
    """Panggil encode_faces.py sebagai subprocess."""
    print("\n[INFO] Menjalankan encode_faces.py ...\n")
    script = BASE_DIR / "encode_faces.py"
    subprocess.run([sys.executable, str(script)], check=False)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak ditemukan.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("=" * 55)
    print("   Smart Attendance — Program Registrasi Wajah")
    print("=" * 55)
    print(f"   Mode     : {'Auto-capture' if AUTO_CAPTURE else 'Manual (SPACE)'}")
    print(f"   Target   : {TARGET_PHOTOS} foto per mahasiswa")
    print(f"   Simpan ke: {FACES_DIR}")
    print("=" * 55 + "\n")

    need_encode = False

    while True:
        # 1. Input NIM & Nama
        info = get_student_info(cap)
        if info is None:
            break

        nim, name = info
        print(f"\n[INPUT] NIM: {nim} | Nama: {name}")

        # 2. Ambil foto
        photo_count = capture_photos(cap, nim, name)
        if photo_count == 0:
            # Dibatalkan — kembali ke form input
            continue

        # 3. Ringkasan & pilihan
        action = show_summary(cap, nim, name, photo_count)

        if action == "encode":
            cap.release()
            cv2.destroyAllWindows()
            run_encode()
            print("\n[DONE] Selesai. Jalankan 'python attendance.py' untuk mulai absensi.")
            return

        elif action == "next":
            need_encode = True
            continue

        else:  # quit
            break
    cap.release()
    cv2.destroyAllWindows()

    if need_encode:
        ans = input("\nMau encode sekarang? (y/n): ").strip().lower()
        if ans == "y":
            run_encode()

    print("\n[SELESAI] Program registrasi ditutup.\n")
if __name__ == "__main__":
    main()

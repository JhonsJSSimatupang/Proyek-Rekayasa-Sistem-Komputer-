import pickle
import time
import cv2
import face_recognition
import numpy as np
import openpyxl
from datetime import datetime, date
from pathlib import Path
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
BASE_DIR        = Path(__file__).parent
ENCODINGS_PKL   = BASE_DIR / "data" / "encodings" / "encodings.pkl"
ATTENDANCE_DIR  = BASE_DIR / "data" / "attendance"
ATTENDANCE_DIR.mkdir(parents=True, exist_ok=True)
COOLDOWN_SECONDS    = 30        # jeda minimum antar absensi orang yang sama
FRAME_SCALE         = 0.5       # skala frame untuk mempercepat detection
TOLERANCE           = 0.50      # threshold kecocokan wajah (makin kecil = makin ketat)
RECOGNITION_FRAMES  = 5         # frame berturut-turut yang harus cocok sebelum dicatat

#untuk warna kotak dan teks.
COLOR_GREEN  = (34, 197, 94)
COLOR_RED    = (60, 60, 220)
COLOR_YELLOW = (0, 200, 220)
COLOR_WHITE  = (255, 255, 255)
COLOR_BLACK  = (0, 0, 0)
COLOR_GRAY   = (150, 150, 150)
COLOR_DARK   = (30, 30, 30)
#  EXCEL HANDLER
def get_attendance_file() -> Path:
    today     = date.today().strftime("%Y-%m-%d")
    xlsx_path = ATTENDANCE_DIR / f"attendance_{today}.xlsx" #bakal buat file baru untuk hari itu

    if not xlsx_path.exists():
        _create_excel(xlsx_path)

    return xlsx_path

def _header_style() -> dict:
    fill   = PatternFill("solid", fgColor="1E3A5F")
    font   = Font(bold=True, color="FFFFFF", size=11)
    align  = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    return {"fill": fill, "font": font, "alignment": align, "border": border}
#cuman buat header aja.
def _create_excel(path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Absensi"

    # Header
    headers = ["No", "NIM", "Nama", "Tanggal", "Waktu", "Status"]
    ws.append(headers)

    style = _header_style()
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx)
        for attr, val in style.items():
            setattr(cell, attr, val)

    # Lebar kolom
    widths = {"A": 6, "B": 16, "C": 25, "D": 14, "E": 12, "F": 12}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    ws.row_dimensions[1].height = 22
    wb.save(path)
    
def save_attendance(nim: str, name: str) -> None:
    """Tambahkan satu baris absensi ke file Excel hari ini."""
    path = get_attendance_file()
    wb   = openpyxl.load_workbook(path)
    ws   = wb.active

    now  = datetime.now()
    row  = ws.max_row + 1
    no   = row - 1      # baris 1 adalah header

    data = [no, nim, name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "Hadir"]

    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    fill_even = PatternFill("solid", fgColor="EFF6FF")

    for col_idx, value in enumerate(data, start=1):
        cell = ws.cell(row=row, column=col_idx, value=value)
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if row % 2 == 0:
            cell.fill = fill_even

    wb.save(path)
    print(f"[SAVE] {nim} | {name} → {path.name}")

#  ENCODER LOADER
def load_encodings() -> tuple[list, list, list]:
    """
    Kembalikan (nims, names, all_encodings) dalam urutan yang sinkron
    untuk dipakai di face_recognition.compare_faces.
    """
    if not ENCODINGS_PKL.exists():
        raise FileNotFoundError(
            f"File encodings tidak ditemukan: {ENCODINGS_PKL}\n"
            "Jalankan 'python encode_faces.py' terlebih dahulu."
        )

    with open(ENCODINGS_PKL, "rb") as f:
        data = pickle.load(f)  # { nim: { name, encodings: [array,...] } }

    nims, names, encodings = [], [], []
    for nim, info in data.items():
        for enc in info["encodings"]:
            nims.append(nim)
            names.append(info["name"])
            encodings.append(enc)

    print(f"[INFO] Loaded {len(set(nims))} mahasiswa, {len(encodings)} total encoding.")
    return nims, names, encodings



#  OVERLAY / DRAWING HELPERS / BOX


def draw_face_box(
    frame: np.ndarray,
    top: int, right: int, bottom: int, left: int,
    label: str,
    color: tuple,
    sub_label: str = "",
) -> None:
    """Gambar kotak wajah dengan label di atas/bawah, gaya modern."""
    # Kotak utama
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    corner_len = 16
    thickness  = 3
    for (x, y, dx, dy) in [
        (left, top, 1, 1), (right, top, -1, 1),
        (left, bottom, 1, -1), (right, bottom, -1, -1),
    ]:
        cv2.line(frame, (x, y), (x + dx * corner_len, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + dy * corner_len), color, thickness)

    # Label background
    label_h = 22
    cv2.rectangle(frame, (left, top - label_h - 4), (right, top), color, -1)
    cv2.putText(
        frame, label,
        (left + 6, top - 8),
        cv2.FONT_HERSHEY_DUPLEX, 0.52,
        COLOR_WHITE, 1, cv2.LINE_AA
    )
    # Sub-label (waktu / nim)
    if sub_label:
        cv2.rectangle(frame, (left, bottom), (right, bottom + 20), color, -1)
        cv2.putText(
            frame, sub_label,
            (left + 6, bottom + 15),
            cv2.FONT_HERSHEY_PLAIN, 1.0,
            COLOR_WHITE, 1, cv2.LINE_AA
        )

def draw_hud(frame: np.ndarray, total_present: int, fps: float) -> None:
    """Gambar HUD info di pojok kiri atas."""
    h, w = frame.shape[:2]
    now  = datetime.now().strftime("%H:%M:%S")
    today = date.today().strftime("%A, %d %B %Y")

    # Panel semi-transparan
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (280, 80), COLOR_DARK, -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    cv2.putText(frame, "SMART ATTENDANCE",  (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.55, COLOR_YELLOW, 1, cv2.LINE_AA)
    cv2.putText(frame, today,               (10, 40), cv2.FONT_HERSHEY_PLAIN,  0.95, COLOR_WHITE,  1, cv2.LINE_AA)
    cv2.putText(frame, f"Waktu   : {now}",  (10, 58), cv2.FONT_HERSHEY_PLAIN,  0.95, COLOR_WHITE,  1, cv2.LINE_AA)
    cv2.putText(frame, f"Hadir   : {total_present} orang  |  FPS: {fps:.1f}",
                                            (10, 74), cv2.FONT_HERSHEY_PLAIN,  0.95, COLOR_GREEN,  1, cv2.LINE_AA)

    # Petunjuk keluar
    cv2.putText(frame, "Tekan [Q] untuk keluar",
                (w - 205, h - 12), cv2.FONT_HERSHEY_PLAIN, 0.95, COLOR_GRAY, 1, cv2.LINE_AA)


#  MAIN LOOP
def run_attendance() -> None:
    try:
        known_nims, known_names, known_encs = load_encodings()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return

    # ── Buka kamera ──────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak ditemukan.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("\n[START] Smart Attendance berjalan. Tekan 'q' untuk keluar.\n")

    # ── State ─────────────────────────────────────────────────────────────────
    last_seen:     dict[str, float]      = {}   # nim → timestamp terakhir absen
    frame_counter: dict[str, int]        = {}   # nim → berapa frame berturut cocok
    attended_today: set[str]             = set()

    prev_time   = time.time()
    fps         = 0.0
    process_every = 2  # proses tiap N frame untuk efisiensi

    frame_no = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_no += 1
        now_ts = time.time()

        # ── FPS hitung
        fps       = 1.0 / max(now_ts - prev_time, 1e-6)
        prev_time = now_ts

        display_frame = frame.copy()
        results: list[dict] = []

        # ── Detection (setiap N frame)
        if frame_no % process_every == 0:
            small   = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
            rgb     = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            locs    = face_recognition.face_locations(rgb, model="hog")
            encs    = face_recognition.face_encodings(rgb, locs)

            for enc, loc in zip(encs, locs):
                top_s, right_s, bottom_s, left_s = loc

                # Scale balik ke ukuran asli
                scale  = 1.0 / FRAME_SCALE
                top    = int(top_s    * scale)
                right  = int(right_s  * scale)
                bottom = int(bottom_s * scale)
                left   = int(left_s   * scale)

                # Pencocokan
                distances = face_recognition.face_distance(known_encs, enc)
                best_idx  = int(np.argmin(distances)) if len(distances) else -1

                if best_idx >= 0 and distances[best_idx] <= TOLERANCE:
                    nim  = known_nims[best_idx]
                    name = known_names[best_idx]
                    dist = distances[best_idx]

                    # Counter frame berturut-turut
                    frame_counter[nim] = frame_counter.get(nim, 0) + 1

                    # Cek cooldown & confidence frame
                    cooldown_ok = (now_ts - last_seen.get(nim, 0)) >= COOLDOWN_SECONDS
                    confident   = frame_counter[nim] >= RECOGNITION_FRAMES

                    if cooldown_ok and confident and nim not in attended_today:
                        save_attendance(nim, name)
                        last_seen[nim]   = now_ts
                        attended_today.add(nim)
                        frame_counter[nim] = 0

                    elif not cooldown_ok:
                        frame_counter[nim] = 0  # reset counter jika cooldown

                    results.append({
                        "nim": nim, "name": name,
                        "dist": dist,
                        "box": (top, right, bottom, left),
                        "recorded": nim in attended_today,
                        "confident": confident,
                    })
                else:
                    results.append({
                        "nim": None, "name": "Tidak Dikenal",
                        "dist": 1.0,
                        "box": (top, right, bottom, left),
                        "recorded": False,
                        "confident": False,
                    })

        # ── Gambar hasil 
        for r in results:
            top, right, bottom, left = r["box"]

            if r["nim"] is None:
                color     = COLOR_RED
                main_lbl  = "Tidak Dikenal"
                sub_lbl   = ""
            elif r["recorded"]:
                color     = COLOR_GREEN
                ts        = datetime.fromtimestamp(last_seen[r["nim"]]).strftime("%H:%M:%S")
                main_lbl  = f"{r['nim']}  {r['name']}"
                sub_lbl   = f"Absen: {ts}"
            else:
                color     = COLOR_YELLOW
                conf_pct  = max(0, int((1 - r["dist"]) * 100))
                main_lbl  = f"{r['nim']}  {r['name']}"
                sub_lbl   = f"Conf: {conf_pct}%"

            draw_face_box(display_frame, top, right, bottom, left,
                          main_lbl, color, sub_lbl)

        # ── HUD 
        draw_hud(display_frame, len(attended_today), fps)

        cv2.imshow("Smart Attendance System", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # ── Cleanup 
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[DONE] Sesi selesai. Total hadir: {len(attended_today)} orang.")
    print(f"[FILE] Tersimpan di: {get_attendance_file()}\n")


# ─── Entry 
if __name__ == "__main__":
    run_attendance()

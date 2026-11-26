#!/usr/bin/env python3
"""Assemble S1..S10 into one submission-ready HTML (and PDF via Edge/Chrome).

The chapters are the S1..S10 Markdown files in 02_DOKUMENTASI_SUMBER/, used
verbatim so the report cannot drift from the reviewed documents. This script
adds:
  * a cover page with complete group member names & NIMs and a document-control page,
  * an automatically generated Table of Contents (Daftar Isi),
  * the diagrams (context, use case, sequence SD-01..SD-04, functional
    decomposition, FFD swimlane, physical decomposition, and all 7 MATLAB
    System Composer model exports) at the exact points where the text refers to them,
  * print CSS (A4, Times New Roman 11 pt, page break before every chapter).

Works with `python-markdown` if installed, or falls back to a built-in pure-Python
Markdown renderer so it runs out-of-the-box on any standard Python 3 environment.

Run:
    python 05_BUKTI_DAN_PENDUKUNG/build_report.py
"""

import html as html_mod
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import markdown as _md_pkg
except ImportError:
    _md_pkg = None

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if (HERE.parent / "02_DOKUMENTASI_SUMBER").exists() else HERE
SRC_DIR = ROOT / "02_DOKUMENTASI_SUMBER" if (ROOT / "02_DOKUMENTASI_SUMBER").exists() else HERE
DIAG_DIR = ROOT / "04_DIAGRAM_DAN_VISUALISASI" if (ROOT / "04_DIAGRAM_DAN_VISUALISASI").exists() else HERE
OUT_DIR = HERE / "_build"
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (OUT_DIR / "RSK_FINAL.html")

# Path to DIAG_DIR (04_DIAGRAM_DAN_VISUALISASI/)
IMG = DIAG_DIR.resolve().as_uri() if len(sys.argv) > 1 else "../../04_DIAGRAM_DAN_VISUALISASI"

CHAPTERS = [
    ("S1_Audit_PRJ2_dan_ChangeLog.md", "Audit PRJ2 & Change Log"),
    ("S2_Scope_Context.md", "Overview, Problem, Scope, Boundary, Context"),
    ("S3_Stakeholder_Needs.md", "Stakeholder & Needs"),
    ("S4_UseCase_Sequence.md", "Use Case & Sequence"),
    ("S5_Requirements.md", "Requirements (EARS)"),
    ("S6_FunctionalArch.md", "Arsitektur Fungsional"),
    ("S7_PhysicalArch.md", "Arsitektur Fisik"),
    ("S8_Allocation_N2_ICD_SPOF.md", "Alokasi, N2, ICD, SPOF"),
    ("S9_RTM_Risiko_Konsistensi.md", "RTM, Risiko, Konsistensi"),
    ("S10_Model_MATLAB.md", "Model Arsitektur di MATLAB (System Composer)"),
]

GROUP = "Tim Pengembang SiHADIR (Kelas B)"
COURSE = "CCE61317 Rekayasa Sistem Komputer (RSK)"
LECTURER = "Sabriansyah Rizqika Akbar, S.T., M.Eng., Ph.D."
DOC_VERSION = "1.0 (Final)"
DOC_DATE = "26 November 2026"
REPO_URL = "https://github.com/JhonsJSSimatupang/Proyek-Rekayasa-Sistem-Komputer-"

# Mapping of Mermaid blocks per file (in order of appearance) to rendered figure HTML
MERMAID_REPLACEMENTS = {
    "S2_Scope_Context.md": [
        f'<figure><img src="{IMG}/fig_context_diagram.jpg" style="max-width:82%;max-height:460px">'
        '<figcaption>Gambar 2.1 &mdash; Context Diagram SiHADIR: batas sistem (System of Interest), '
        '7 entitas eksternal (E1&ndash;E7), dan 14 aliran masuk/keluar (F1&ndash;F14).</figcaption></figure>'
    ],
    "S4_UseCase_Sequence.md": [
        f'<figure><img src="{IMG}/fig_usecase_diagram.jpg" style="max-width:78%;max-height:520px">'
        '<figcaption>Gambar 4.1 &mdash; Use Case Diagram SiHADIR (UC-01 s.d. UC-12 beserta aktor primer dan sekunder).</figcaption></figure>',
        f'<figure><img src="{IMG}/fig_sd01_enrolment.jpg" style="max-width:88%">'
        '<figcaption>Gambar 4.2 &mdash; Sequence Diagram SD-01: Enrolment Wajah dengan Explicit Consent.</figcaption></figure>',
        f'<figure><img src="{IMG}/fig_sd02_verifikasi.jpg" style="max-width:96%">'
        '<figcaption>Gambar 4.3 &mdash; Sequence Diagram SD-02: Verifikasi Kehadiran Real-Time + Liveness.</figcaption></figure>',
        f'<figure><img src="{IMG}/fig_sd03_offline_sync.png" style="max-width:78%">'
        '<figcaption>Gambar 4.4 &mdash; Sequence Diagram SD-03: Pencatatan Mode Offline dan Sinkronisasi Batch Idempoten.</figcaption></figure>',
        f'<figure><img src="{IMG}/fig_sd04_tutup_sesi.jpg" style="max-width:88%">'
        '<figcaption>Gambar 4.5 &mdash; Sequence Diagram SD-04: Penutupan Sesi, Finalisasi Alfa, dan Pengiriman Rekap ke SIAKAD.</figcaption></figure>',
    ],
    "S6_FunctionalArch.md": [
        f'<figure><img src="{IMG}/fig_dekomposisi_fungsi.svg" style="width:100%">'
        '<figcaption>Gambar 6.1 &mdash; Dekomposisi Fungsional SiHADIR: A0 Verify Classroom Attendance '
        'menjadi 12 kelompok fungsi (F1&ndash;F12) dan 24 fungsi leaf.</figcaption></figure>',
        f'<figure><img src="{IMG}/fig_alur_presensi.png" style="max-width:92%">'
        '<figcaption>Gambar 6.2 &mdash; Alur Proses Presensi SiHADIR (Swimlane FFD): 16 langkah '
        '(F1.1&ndash;F12) lintas lima lane subsistem yang dapat ditelusuri ke requirement di S5.</figcaption></figure>',
    ],
    "S7_PhysicalArch.md": [
        f'<figure><img src="{IMG}/fig_arsitektur_sihadir.png" style="width:100%">'
        '<figcaption>Gambar 7.1 &mdash; Dekomposisi Fisik SiHADIR: 6 subsistem (S1&ndash;S6), '
        '32 komponen (C1.1&ndash;C6.3), beserta derajat kopling keluar/masuk tiap subsistem.</figcaption></figure>'
    ],
}

# Additional figures inserted right after specific headings (for S10 MATLAB screenshots)
FIGURES = {
    "S10_Model_MATLAB.md": [
        ("## 10.4 Pemeriksaan spesifikasi",
         f'<figure><img src="{IMG}/SiHADIR_root.png" style="width:100%">'
         '<figcaption>Gambar 10.1 &mdash; Diagram root <i>SiHADIR_Architecture.slx</i> '
         'sebagaimana tersimpan di MATLAB System Composer: 6 subsistem, 50 port batas, 25 konektor antarsubsistem. '
         'Diekspor langsung dari model.</figcaption></figure>'),
        ("## 10.8 Port yang tidak tersambung",
         '<h3>Diagram Ekspor Kanvas Tiap Subsistem (MATLAB System Composer)</h3>'
         + "".join(
             f'<figure><img src="{IMG}/{f}" style="width:96%">'
             f'<figcaption>Gambar 10.{i + 2} &mdash; {cap}</figcaption></figure>'
             for i, (f, cap) in enumerate([
                 ("SiHADIR_S1_Edge_Terminal.png", "S1 Edge Terminal: 11 komponen (C1.1–C1.11), 4 port batas, 17 konektor."),
                 ("SiHADIR_S2_Backend_Services.png", "S2 Backend Services: 8 komponen (C2.1–C2.8), 22 port batas, 32 konektor."),
                 ("SiHADIR_S3_Integration_Comms.png", "S3 Integration &amp; Comms: 3 komponen (C3.1–C3.3), 3 port batas, 3 konektor."),
                 ("SiHADIR_S4_Data_Management.png", "S4 Data Management: 4 komponen (C4.1–C4.4), 8 port batas, 8 konektor."),
                 ("SiHADIR_S5_User_Interfaces.png", "S5 User Interfaces: 3 komponen (C5.1–C5.3), 5 port batas, 5 konektor."),
                 ("SiHADIR_S6_Identity_Privacy.png", "S6 Identity &amp; Privacy: 3 komponen (C6.1–C6.3), 8 port batas, 8 konektor."),
             ])
         )),
    ],
}

CSS = """
@page { size: A4; margin: 2.2cm 2.0cm 2.2cm 2.0cm; }
body { font-family: "Times New Roman", Georgia, serif; font-size: 10.8pt; line-height: 1.35;
       color: #111; text-align: justify; }
h1 { font-family: Arial, Helvetica, sans-serif; font-size: 16.5pt; color: #12395B;
     border-bottom: 2px solid #12395B; padding-bottom: 4pt; margin: 0 0 10pt 0; }
h2 { font-family: Arial, Helvetica, sans-serif; font-size: 12.5pt; color: #12395B;
     margin: 14pt 0 5pt 0; page-break-after: avoid; break-after: avoid; }
h3 { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; color: #234;
     margin: 10pt 0 4pt 0; page-break-after: avoid; break-after: avoid; }
h4 { font-family: Arial, Helvetica, sans-serif; font-size: 10.2pt; margin: 8pt 0 3pt 0; }
p  { margin: 0 0 6pt 0; }
ul, ol { margin: 0 0 6pt 0; padding-left: 18pt; }
li { margin-bottom: 2pt; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.8pt; background: #F2F4F7;
       padding: 0 2pt; border-radius: 2pt; }
pre { font-family: Consolas, "Courier New", monospace; font-size: 8.2pt; background: #F7F8FA;
      border: 1px solid #D5DAE0; border-left: 3px solid #12395B;
      padding: 6pt 8pt; margin: 6pt 0 8pt 0; white-space: pre-wrap;
      line-height: 1.22; page-break-inside: avoid; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt;
        font-family: Arial, Helvetica, sans-serif; margin: 5pt 0 9pt 0;
        page-break-inside: auto; }
th { background: #E7EDF3; border: 1px solid #9AA8B6; padding: 3pt 4pt;
     text-align: left; font-weight: 600; color: #12395B; }
td { border: 1px solid #B7C2CD; padding: 3pt 4pt; vertical-align: top; }
tr { page-break-inside: avoid; break-inside: avoid; }
blockquote { margin: 6pt 0 6pt 12pt; padding: 4pt 8pt; border-left: 3px solid #C6A15B;
             background: #FDF8EC; font-size: 9.8pt; }
figure { margin: 8pt 0 12pt 0; page-break-inside: avoid; break-inside: avoid; text-align: center; }
figure img { max-width: 100%; height: auto; border: 1px solid #E1E6EB; border-radius: 3pt; padding: 2pt; background: #FFF; }
figcaption { font-family: Arial, Helvetica, sans-serif; font-size: 8.8pt; color: #333;
             text-align: center; margin-top: 4pt; font-style: italic; }
.chapter { page-break-before: always; break-before: page; }
.cover { text-align: center; padding-top: 18pt; }
.cover .rule { border-top: 3px double #12395B; margin: 14pt 0; }
.cover h1 { border: none; font-size: 26pt; text-align: center; margin: 4pt 0; }
.cover .sub { font-size: 14.5pt; color: #12395B; margin: 6pt 0 0 0; font-family: Arial, sans-serif; font-weight: 600; }
.cover .meta { font-size: 11pt; color: #333; font-family: Arial, sans-serif; }
.meta-table { width: 86%; margin: 20pt auto 0 auto; font-size: 10.2pt;
              font-family: "Times New Roman", serif; border: 1px solid #D5DAE0; }
.meta-table td { border: 1px solid #E1E6EB; padding: 4pt 7pt; text-align: left; }
.meta-table td.k { width: 32%; font-weight: 600; background: #F7F9FB; color: #12395B; font-family: Arial, sans-serif; font-size: 9.5pt; }
.toc-list { list-style: none; padding-left: 0; font-family: Arial, sans-serif; font-size: 9.5pt; }
.toc-list li.toc-h1 { font-weight: 700; color: #12395B; margin-top: 6pt; }
.toc-list li.toc-h2 { padding-left: 16pt; color: #222; font-weight: 400; }
.toc-list a { text-decoration: none; color: inherit; }
"""

COVER = f"""
<div class="cover">
  <p class="meta" style="margin-bottom:6pt;font-weight:700;color:#12395B">FAKULTAS ILMU KOMPUTER &bull; UNIVERSITAS BRAWIJAYA</p>
  <p class="meta" style="margin-bottom:22pt">PROGRAM STUDI TEKNIK KOMPUTER</p>
  <div class="rule"></div>
  <p class="sub">Final System Requirement Specification &amp; System Architecture</p>
  <h1>SiHADIR</h1>
  <p class="sub" style="font-size:12.5pt;font-weight:400">Sistem Informasi Kehadiran Digital Mahasiswa Berbasis Pengenalan Wajah</p>
  <div class="rule"></div>
  <table class="meta-table">
    <tr><td class="k">Mata Kuliah</td><td>{COURSE}</td></tr>
    <tr><td class="k">Dosen Pengampu</td><td>{LECTURER}</td></tr>
    <tr><td class="k">Kelompok</td><td>{GROUP}</td></tr>
    <tr><td class="k">Anggota Kelompok</td><td>
      1. Muhamad Al Fatih &mdash; NIM 245150301111024<br>
      2. Jhons Janner Samuel S &mdash; NIM 245150301111009<br>
      3. Azzam Galen Crosdiyanto &mdash; NIM 245150307111044<br>
      4. Muhammad Mushlih Fajr &mdash; NIM 245150307111047<br>
      5. Keirio Omar Attallah &mdash; NIM 245150307111061
    </td></tr>
    <tr><td class="k">Versi Dokumen</td><td>{DOC_VERSION}</td></tr>
    <tr><td class="k">Tanggal</td><td>{DOC_DATE}</td></tr>
    <tr><td class="k">Repository GitHub</td><td><code>{REPO_URL}</code></td></tr>
  </table>
  <p style="margin-top:32pt;font-size:9.8pt;color:#444;text-align:center">
    Dokumen ini disusun dari rantai rekayasa sistem yang terverifikasi otomatis:<br>
    <b>Problem &rarr; Stakeholder Needs &rarr; Use Case &rarr; Requirement (EARS) &rarr; Functional Architecture
    &rarr; Physical Architecture &rarr; Allocated Architecture &rarr; Interface (ICD) &rarr; MATLAB System Composer Model &rarr; Verification &amp; Acceptance</b>.
  </p>
</div>
"""

CONTROL_HEADER = """
<div class="chapter">
<h1>Kendali Dokumen &amp; Ringkasan Eksekutif</h1>
<table>
<tr><th style="width:14%">Versi</th><th style="width:20%">Tanggal</th><th style="width:18%">Status</th><th>Perubahan Utama</th></tr>
<tr><td>0.1</td><td>November 2026</td><td>Draf</td><td>Audit PRJ1/PRJ2, penetapan scope, system boundary, dan 13 stakeholder needs.</td></tr>
<tr><td>0.5</td><td>November 2026</td><td>Draf</td><td>Pemodelan 12 use case, 4 sequence diagram, dan 36 requirement berpola EARS.</td></tr>
<tr><td>0.8</td><td>November 2026</td><td>Draf</td><td>Arsitektur fungsional (IDEF0 &amp; FFD) dan fisik, alokasi 24 fungsi, matriks N2, 16 ICD, analisis SPOF.</td></tr>
<tr><td>1.0</td><td>26 November 2026</td><td>Final (Verified)</td><td>RTM 36 baris (0 temuan), register risiko, Change Impact Analysis, model MATLAB System Composer (.slx &amp; .sldd) lulus 15/15 cek spesifikasi dan 9/9 cek model.</td></tr>
</table>

<h2>Ringkasan Metrik Rekayasa Terverifikasi</h2>
<table>
<tr><th>Aspek Rekayasa</th><th>Jumlah / Status</th><th>Bukti &amp; Artefak</th></tr>
<tr><td>Stakeholder / Stakeholder Needs</td><td>7 Stakeholder / 13 Needs (SN-01..SN-13)</td><td>Bab S3 (0 orphan need)</td></tr>
<tr><td>Use Case / Sequence Diagram</td><td>12 Use Case (4 rinci) / 4 Sequence Diagram</td><td>Bab S4 (UC-01..UC-12, SD-01..SD-04)</td></tr>
<tr><td>System Requirements (EARS)</td><td>36 Requirement (15 FR, 6 PRF, 6 IF, 5 SEC, 4 OPS)</td><td>Bab S5, <code>RTM_SiHADIR.csv</code></td></tr>
<tr><td>Arsitektur Fungsional</td><td>12 kelompok fungsi (F1&ndash;F12), 24 fungsi leaf</td><td>Bab S6, <code>fig_alur_presensi.svg</code></td></tr>
<tr><td>Arsitektur Fisik (Subsistem / Komponen / Port)</td><td>6 Subsistem / 33 Komponen / 72 Port (+30 Port Batas)</td><td>Bab S7, <code>SiHADIR_Architecture.slx</code></td></tr>
<tr><td>Antarmuka (ICD) / Link / Konektor / Alokasi</td><td>16 ICD / 27 Link / 57 Konektor (15 root + 42 sub) / 24 Alokasi</td><td>Bab S8, <code>SiHADIR_Architecture_Interfaces.sldd</code></td></tr>
<tr><td>Verifikasi Otomatis RTM (<code>check_consistency.py</code>)</td><td><b>LULUS (0 temuan pada 36 requirement)</b></td><td>Bab S9</td></tr>
<tr><td>Verifikasi Spesifikasi Arsitektur (<code>verify_architecture_spec.m</code>)</td><td><b>LULUS (15/15 pemeriksaan C1&ndash;C15)</b></td><td>Bab S10, <code>S10_evidence.txt</code></td></tr>
<tr><td>Verifikasi Model System Composer (<code>verify_built_model.m</code>)</td><td><b>LULUS (9/9 pemeriksaan M1&ndash;M9)</b></td><td>Bab S10, <code>S10_evidence.txt</code></td></tr>
<tr><td>Register Risiko &amp; Change Impact Analysis</td><td>6 Risiko Utama (L&times;C) + 3 Skenario Dampak Perubahan</td><td>Bab S9</td></tr>
</table>

<h2>Daftar Isi</h2>
[[TOC]]
</div>
"""


def slugify(text):
    s = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "sec"


def inline_fmt(text):
    """Pure-Python inline markdown formatter (code, bold, italic)."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) >= 2:
            out.append(f"<code>{html_mod.escape(p[1:-1])}</code>")
        else:
            s = p
            s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
            s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
            s = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", s)
            out.append(s)
    return "".join(out)


def fallback_md_to_html(text):
    """Built-in Markdown-to-HTML converter supporting tables, code blocks, lists, blockquotes, and raw HTML."""
    lines = text.splitlines()
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Raw HTML block (<figure>, <h3>, <div, etc.)
        if stripped.startswith("<figure") or stripped.startswith("<h3") or stripped.startswith("<div"):
            out.append(line)
            i += 1
            continue

        # Fenced code block
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(html_mod.escape(lines[i]))
                i += 1
            if i < n:
                i += 1
            out.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
            continue

        # Heading
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            lvl = len(m.group(1))
            content = inline_fmt(m.group(2).strip())
            hid = slugify(content)
            style = ' style="page-break-before: always; break-before: page;"' if lvl == 1 else ""
            out.append(f'<h{lvl} id="{hid}"{style}>{content}</h{lvl}>')
            i += 1
            continue

        # Table
        if "|" in stripped and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|[\s:\-|]*$", lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2  # skip header and separator
            rows = []
            while i < n and "|" in lines[i].strip() and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tbl = ["<table><thead><tr>"]
            for h in headers:
                tbl.append(f"<th>{inline_fmt(h)}</th>")
            tbl.append("</tr></thead><tbody>")
            for r in rows:
                tbl.append("<tr>")
                for c in r:
                    tbl.append(f"<td>{inline_fmt(c)}</td>")
                tbl.append("</tr>")
            tbl.append("</tbody></table>")
            out.append("".join(tbl))
            continue

        # Blockquote
        if stripped.startswith(">"):
            bq = []
            while i < n and lines[i].strip().startswith(">"):
                bq.append(inline_fmt(lines[i].strip().lstrip(">").strip()))
                i += 1
            out.append("<blockquote><p>" + " ".join(bq) + "</p></blockquote>")
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                item_text = re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()
                i += 1
                while i < n and lines[i].startswith("  ") and not re.match(r"^\s*[-*]\s+", lines[i]):
                    item_text += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline_fmt(item_text)}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                i += 1
                while i < n and lines[i].startswith("   ") and not re.match(r"^\s*\d+\.\s+", lines[i]):
                    item_text += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline_fmt(item_text)}</li>")
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        # Paragraph
        p_lines = []
        while i < n:
            cur = lines[i].strip()
            if (not cur or cur.startswith("#") or cur.startswith("```") or cur.startswith(">")
                    or cur.startswith("<figure") or cur.startswith("<h3")
                    or re.match(r"^[-*]\s+", cur) or re.match(r"^\d+\.\s+", cur)
                    or ("|" in cur and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|[\s:\-|]*$", lines[i + 1].strip()))):
                break
            p_lines.append(inline_fmt(cur))
            i += 1
        if p_lines:
            out.append("<p>" + " ".join(p_lines) + "</p>")

    return "\n".join(out)


def md_to_html(text):
    if _md_pkg is not None:
        html = _md_pkg.markdown(
            text,
            extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
            output_format="html5",
        )
        html = re.sub(
            r"<h1([^>]*)>(.*?)</h1>",
            lambda m: f'<h1 id="{slugify(m.group(2))}"{m.group(1)} style="page-break-before: always; break-before: page;">{m.group(2)}</h1>',
            html,
        )
        html = re.sub(
            r"<h2([^>]*)>(.*?)</h2>",
            lambda m: f'<h2 id="{slugify(m.group(2))}"{m.group(1)}>{m.group(2)}</h2>',
            html,
        )
        return html
    return fallback_md_to_html(text)


def replace_mermaid_blocks(name, text):
    repls = list(MERMAID_REPLACEMENTS.get(name, []))
    if not repls:
        return text

    def _sub(match):
        if repls:
            return "\n" + repls.pop(0) + "\n"
        return match.group(0)

    return re.sub(r"```mermaid\s*.*?\s*```", _sub, text, flags=re.DOTALL)


def insert_figures(name, text):
    text = replace_mermaid_blocks(name, text)
    for anchor, block in FIGURES.get(name, []):
        if anchor not in text:
            print(f"  ! anchor tidak ditemukan di {name}: {anchor}", file=sys.stderr)
            continue
        head, tail = text.split(anchor, 1)
        line_end = tail.find("\n")
        title = tail[:line_end] if line_end >= 0 else ""
        rest = tail[line_end + 1:] if line_end >= 0 else ""
        text = f"{head}{anchor}{title}\n\n{block}\n\n{rest}"
    return text


def extract_toc(markdown_texts):
    items = ['<ul class="toc-list">']
    for md in markdown_texts:
        in_code = False
        for line in md.splitlines():
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            m1 = re.match(r"^#\s+(.*)$", s)
            m2 = re.match(r"^##\s+(.*)$", s)
            if m1:
                t = m1.group(1).strip()
                items.append(f'<li class="toc-h1"><a href="#{slugify(t)}">{html_mod.escape(t)}</a></li>')
            elif m2:
                t = m2.group(1).strip()
                items.append(f'<li class="toc-h2"><a href="#{slugify(t)}">{html_mod.escape(t)}</a></li>')
    items.append("</ul>")
    return "\n".join(items)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw_chapters = []
    html_chapters = []
    for name, title in CHAPTERS:
        path = SRC_DIR / name
        if not path.exists():
            sys.exit(f"bab tidak ditemukan: {path}")
        raw_md = path.read_text(encoding="utf-8")
        raw_chapters.append(raw_md)
        processed = insert_figures(name, raw_md)
        html_chapters.append(md_to_html(processed))
        print(f"  + {name} -> {title}")

    toc_html = extract_toc(raw_chapters)
    control_html = CONTROL_HEADER.replace("[[TOC]]", toc_html)

    parts = [
        '<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">'
        f"<title>SiHADIR — Final SRS &amp; System Architecture ({GROUP})</title>"
        f"<style>{CSS}</style></head><body>",
        COVER,
        control_html,
        *html_chapters,
        "</body></html>",
    ]
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nHTML: {OUT} ({OUT.stat().st_size} byte)")

    if len(sys.argv) > 2:
        pdf_out = Path(sys.argv[2]).resolve()
        pdf_out.parent.mkdir(parents=True, exist_ok=True)
        browsers = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        ]
        browser = next((b for b in browsers if b.exists()), None)
        if browser:
            with tempfile.TemporaryDirectory() as prof:
                cmd = [
                    str(browser),
                    "--headless=new",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    f"--user-data-dir={prof}",
                    f"--print-to-pdf={pdf_out}",
                    OUT.as_uri(),
                ]
                subprocess.run(cmd, check=True)
            print(f"PDF : {pdf_out} ({pdf_out.stat().st_size} byte)")


if __name__ == "__main__":
    main()

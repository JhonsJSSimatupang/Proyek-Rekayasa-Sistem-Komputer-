#!/usr/bin/env python3
"""Generate the SiHADIR physical-decomposition figure from sihadir_arch_spec.m.

Reads the MATLAB spec (single source of truth) and writes:
  fig_arsitektur_sihadir.svg   - subsystem/component decomposition, self-contained SVG
  fig_arsitektur_sihadir.mmd   - the same content plus every link, as Mermaid

Why the figure carries no arrows: with 27 links over six columns the curved
routes crossed the component boxes and were unreadable. The figure therefore
shows the decomposition (what exists and where it lives), while the 27 links
and 16 interfaces are drawn in the System Composer model and tabulated in S8.
Each subsystem column carries its boundary-port and link counts so the figure
still says how heavily each subsystem is coupled.

No third-party packages required.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "03_MODEL_MATLAB" / "sihadir_arch_spec.m"
if not SPEC.exists():
    SPEC = HERE / "sihadir_arch_spec.m"
OUT_DIR = HERE / "04_DIAGRAM_DAN_VISUALISASI"
if not OUT_DIR.exists():
    OUT_DIR = HERE

COLORS = {
    "S1": ("#E8F1FB", "#2F6FB2"),
    "S2": ("#EAF6EC", "#2E7D4F"),
    "S3": ("#FFF4E5", "#B4741E"),
    "S4": ("#F3EDF9", "#6B4C9A"),
    "S5": ("#FDECEF", "#B03A4E"),
    "S6": ("#E9F5F6", "#20707A"),
}


def parse_spec(text):
    subs, comps, links = [], [], []

    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("'"):
            continue
        fields = re.findall(r"'([^']*)'", s)
        if len(fields) < 4:
            continue

        # component row: Cx.y, Name, kind, Sx, {...}
        if re.fullmatch(r"C\d+\.\d+", fields[0]) and re.fullmatch(r"S\d", fields[3]):
            comps.append({"id": fields[0], "name": fields[1],
                          "kind": fields[2], "sub": fields[3]})

        # link row: Cx.y, port, Cx.y, port, IF
        elif (re.fullmatch(r"C\d+\.\d+", fields[0])
              and re.fullmatch(r"C\d+\.\d+", fields[2]) and len(fields) >= 5):
            links.append({"src": fields[0], "src_port": fields[1],
                          "dst": fields[2], "dst_port": fields[3],
                          "if": fields[4]})

    for line in text.splitlines():
        m = re.match(r"\s*'(S\d)',\s*'([^']+)'", line)
        if m:
            subs.append({"id": m.group(1), "name": m.group(2)})

    return subs, comps, links


def layout(subs, comps):
    node_w, node_h, gap = 190, 44, 11
    col_w, margin_top, margin_left = 214, 74, 34
    header_h, pad = 34, 14

    nodes = {}
    cols = {}
    for i, sub in enumerate(subs):
        x = margin_left + i * col_w
        members = [c for c in comps if c["sub"] == sub["id"]]
        height = header_h + pad + len(members) * (node_h + gap) + pad
        cols[sub["id"]] = {"x": x, "y": margin_top, "w": col_w - 16, "h": height,
                           "name": sub["name"], "n": len(members)}
        for j, c in enumerate(members):
            nodes[c["id"]] = {
                "x": x + 8,
                "y": margin_top + header_h + pad + j * (node_h + gap),
                "w": col_w - 32,
                "h": node_h,
                "id": c["id"],
                "name": c["name"],
                "sub": c["sub"],
            }

    width = margin_left * 2 + len(subs) * col_w
    max_h = max(c["h"] for c in cols.values()) if cols else 400
    height = margin_top + max_h + 96
    return nodes, cols, width, height


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def coupling(links, sid_of, sid):
    """(outgoing, incoming) cross-subsystem link counts for one subsystem."""
    out_n = sum(1 for l in links if sid_of[l["src"]] == sid and sid_of[l["dst"]] != sid)
    in_n = sum(1 for l in links if sid_of[l["dst"]] == sid and sid_of[l["src"]] != sid)
    return out_n, in_n


def build_svg(subs, comps, links, nodes, cols, width, height):
    sid_of = {c["id"]: c["sub"] for c in comps}
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Segoe UI, Arial, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="17" '
        f'font-weight="600" fill="#1F2933">SiHADIR — Dekomposisi Fisik '
        f'({len(subs)} subsistem, {len(comps)} komponen)</text>',
        f'<text x="{width/2}" y="50" text-anchor="middle" font-size="10.5" '
        f'fill="#616E7C">Setiap komponen memuat fungsi yang dialokasikan di S8; '
        f'tautan dan antarmuka digambar pada model System Composer</text>',
    ]

    # subsystem containers
    for sid, c in cols.items():
        fill, stroke = COLORS.get(sid, ("#F5F5F5", "#666"))
        out.append(f'<rect x="{c["x"]}" y="{c["y"]}" width="{c["w"]}" height="{c["h"]}" '
                   f'rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        out.append(f'<text x="{c["x"] + c["w"]/2}" y="{c["y"] + 16}" text-anchor="middle" '
                   f'font-size="12.5" font-weight="700" fill="{stroke}">'
                   f'{sid} · {esc(c["name"])}</text>')
        out.append(f'<text x="{c["x"] + c["w"]/2}" y="{c["y"] + 29}" text-anchor="middle" '
                   f'font-size="9" fill="{stroke}">{c["n"]} komponen</text>')

    # nodes
    for n in nodes.values():
        _, stroke = COLORS.get(n["sub"], ("#F5F5F5", "#666"))
        cx = n["x"] + n["w"] / 2
        out.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" '
                   f'rx="6" fill="#FFFFFF" stroke="{stroke}" stroke-width="1.1"/>')
        out.append(f'<text x="{cx}" y="{n["y"] + 17}" text-anchor="middle" font-size="9" '
                   f'font-weight="700" fill="{stroke}">{n["id"]}</text>')
        out.append(f'<text x="{cx}" y="{n["y"] + 32}" text-anchor="middle" font-size="9.8" '
                   f'fill="#1F2933">{esc(n["name"])}</text>')

    # coupling summary under every column
    for sid, c in cols.items():
        o, i = coupling(links, sid_of, sid)
        out.append(f'<text x="{c["x"] + c["w"]/2}" y="{c["y"] + c["h"] + 20}" '
                   f'text-anchor="middle" font-size="9.5" fill="#3E4C59">'
                   f'keluar {o} · masuk {i} link</text>')

    # legend
    ly = height - 30
    out.append(f'<text x="34" y="{ly}" font-size="9.5" fill="#616E7C">'
               f'Kotak berwarna = subsistem; kotak putih = komponen. '
               f'Arah dan nama antarmuka tiap tautan ada pada tabel N2 (S8) '
               f'dan pada SiHADIR_Architecture.slx.</text>')
    out.append('</svg>')
    return "\n".join(out)


def build_mermaid(subs, comps, links):
    lines = ["flowchart LR"]
    for s in subs:
        lines.append(f'  subgraph {s["id"]}["{s["id"]} · {s["name"]}"]')
        for c in comps:
            if c["sub"] == s["id"]:
                lines.append(f'    {c["id"].replace(".", "_")}["{c["id"]} {c["name"]}"]')
        lines.append("  end")
    for l in links:
        a = l["src"].replace(".", "_")
        b = l["dst"].replace(".", "_")
        label = "" if l["if"] == "internal" else f'|{l["if"]}|'
        lines.append(f"  {a} -->{label} {b}")
    lines.append('  E6_NTP(("E6 NTP Server"))')
    lines.append('  C1_10 -->|IF-T2NTP| E6_NTP')
    return "\n".join(lines)


def main():
    if not SPEC.exists():
        sys.exit(f"spec tidak ditemukan: {SPEC}")
    subs, comps, links = parse_spec(SPEC.read_text(encoding="utf-8"))
    if not (subs and comps and links):
        sys.exit(f"parse gagal: subs={len(subs)} comps={len(comps)} links={len(links)}")

    nodes, cols, w, h = layout(subs, comps)
    svg_path = OUT_DIR / "fig_arsitektur_sihadir.svg"
    svg_path.write_text(build_svg(subs, comps, links, nodes, cols, w, h), encoding="utf-8")
    (OUT_DIR / "fig_arsitektur_sihadir.mmd").write_text(
        build_mermaid(subs, comps, links), encoding="utf-8")

    print(f"subsistem : {len(subs)}")
    print(f"komponen  : {len(comps)}")
    print(f"link      : {len(links)}")
    print(f"svg       : {svg_path.name} ({svg_path.stat().st_size} byte, {w}x{h})")


if __name__ == "__main__":
    main()

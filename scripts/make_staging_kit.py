#!/usr/bin/env python3
"""
TriNetra-IN staging kit generator (Amendment v2.6, Section 4-6).

Creates everything needed to run the 120 physical journeys, so the only manual
work left is physical handling: packing, manipulating, photographing, weighing.

It does NOT create any observation, weight, photo or result. It only plans the
study and prints labels and instructions. The truth commitment it writes must be
committed to git BEFORE the first package is staged (Gate G-2).

Usage:
    python make_staging_kit.py --seed 20261026 --n 120 --out kit_output
    python make_staging_kit.py --seed 777 --n 10 --pilot --out pilot_kit

Requires: Python 3.9+, reportlab (pip install reportlab).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import secrets
import string
from datetime import datetime, timezone

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------------
# Design (Amendment v2.6, Section 5)
# ----------------------------------------------------------------------------
MAIN_CELLS = [
    ("INTACT", 30),
    ("FLYER_CHANGE", 12),
    ("FWD_DAMAGE", 14),
    ("DOORSTEP_SUB", 14),
    ("CUSTOMER_TAMPER", 14),
    ("REVERSE_TAMPER", 12),
    ("DEGRADED", 12),
    ("AMBIGUOUS_GLARE", 12),
]
PILOT_CELLS = [
    ("INTACT", 3), ("FLYER_CHANGE", 1), ("FWD_DAMAGE", 1), ("DOORSTEP_SUB", 1),
    ("CUSTOMER_TAMPER", 1), ("REVERSE_TAMPER", 1), ("DEGRADED", 1), ("AMBIGUOUS_GLARE", 1),
]

# Manipulation used inside DEGRADED / AMBIGUOUS journeys, with its interval
HIDDEN_MANIPULATIONS = [("FWD_DAMAGE", "S1"), ("CUSTOMER_TAMPER", "S2"), ("REVERSE_TAMPER", "S3")]
INTERVAL_OF = {
    "INTACT": "none", "FLYER_CHANGE": "none", "FWD_DAMAGE": "S1", "DOORSTEP_SUB": "S1",
    "CUSTOMER_TAMPER": "S2", "REVERSE_TAMPER": "S3",
}
BOUNDS = {"S1": ("CP1", "CP2"), "S2": ("CP2", "CP3"), "S3": ("CP3", "CP4")}
AFTER_CP = {"S1": "CP1", "S2": "CP2", "S3": "CP3"}  # manipulation happens after this checkpoint
EXPECTED_LABEL = {
    "none": "ATTR_CONFIRMED_LEGITIMATE",
    "S1": "ATTR_STAGE_FORWARD_TRANSIT",
    "S2": "ATTR_STAGE_CONSUMER_CUSTODY",
    "S3": "ATTR_STAGE_REVERSE_TRANSIT",
}
# 0 g = WEIGHT-MATCHED: the stager adds filler so the parcel weighs the same as before.
# These journeys can only be caught by seal, identity or visual evidence (realistic fraud).
MASS_CHANGES_G = [0, 0, 10, 20, 50, 100, 150]

# Layered tamper-evident seals (like jewellery packaging):
#   L1  transit seal on the courier flyer, one per leg: forward (applied at CP1) and return (applied at CP3)
#   L2  tamper sticker across the product box opening (stays on for the whole journey)
#   L3  numbered item tag, tied around the product box with a cable tie (stays on for the whole journey)
# A seal can be TORN (visibly broken / missing) or REPLACED (a look-alike seal with a different ID).
INSTRUCTIONS = {
    "INTACT": "No manipulation. Hand over the parcel between checkpoints without touching any seal.",
    "FLYER_CHANGE": "After CP1 capture: cut open the forward flyer, move the box (L2/L3 untouched) into a NEW flyer "
                    "and close it with the NEW FLYER SEAL listed below. Give the CP2 capturer the carrier note "
                    "'flyer replaced at hub, new seal <ID>'. This is a permitted, logged change.",
    "FWD_DAMAGE": "After CP1 capture: drop the parcel once from about 1 m onto one corner, or press a visible dent "
                  "into the box through the flyer. Do NOT break any seal. Film it.",
    "DOORSTEP_SUB": "After CP1 capture: replace the WHOLE parcel with the decoy parcel you prepared: a different "
                    "item in a similar box, carrying the DECOY L2 sticker and DECOY L3 tag, inside a flyer closed "
                    "with the DECOY L1 seal. Hand the decoy to the CP2 capturer as if it were the original. Film it.",
    "CUSTOMER_TAMPER": "After CP2 capture (box is out of its flyer): break the L2 sticker and cut the L3 tag, swap or "
                       "remove the mass shown below, then close the box. SEAL ACTION decides what is left on the box. "
                       "Film it.",
    "REVERSE_TAMPER": "After CP3 capture (box is in its return flyer): slit the flyer, break L2 and cut L3, swap or "
                      "remove the mass shown below, then re-close everything. SEAL ACTION decides what is left. "
                      "Film it.",
}
SEAL_ACTION_TEXT = {
    "torn": "TORN: leave the broken L2 sticker on and leave the L3 tag cut or missing (and the L1 seal torn, "
            "if this is reverse transit). Re-close with plain tape.",
    "replaced": "REPLACED: remove the broken seals and apply the REPLACEMENT seals listed on this card, neatly, "
                "so they look normal. Only their IDs differ.",
    "subtle": "SUBTLE: lift one corner of the L2 sticker by about 1 cm and press it back. Do not touch L3. "
              "Mass change 0 g. The capture card asks for glare over this area.",
}

ALPHABET = string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789"


def code(rng: random.Random, prefix: str, k: int = 5) -> str:
    return prefix + "".join(rng.choice(ALPHABET) for _ in range(k))


def build_assignment(cells, seed: int):
    rng = random.Random(seed)
    rows, used = [], set()

    def sid(prefix):
        x = code(rng, prefix, 6)
        while x in used:
            x = code(rng, prefix, 6)
        used.add(x)
        return x

    for cell, n in cells:
        for _ in range(n):
            jc = code(rng, "J-")
            while jc in used:
                jc = code(rng, "J-")
            used.add(jc)
            row = {
                "journey_code": jc, "cell": cell, "manipulation": cell, "interval": INTERVAL_OF.get(cell, ""),
                "manipulate_after": "", "mass_change_g": "", "weight_matched": "n/a", "seal_action": "none",
                "degraded_cp": "none", "degradation": "none", "glare_cps": "none",
                "expected_omega": "DET", "expected_label": "",
                # layered seals (genuine)
                "l1_fwd_seal": sid("SEAL-"), "l2_box_seal": sid("SEAL-"), "l3_item_tag": sid("TAG-"),
                "l1_ret_seal": sid("SEAL-"),
                # look-alikes used only by the stager
                "new_l1_fwd_seal": "", "decoy_l1_seal": "", "decoy_l2_seal": "", "decoy_l3_tag": "",
                "repl_l1_ret_seal": "", "repl_l2_seal": "", "repl_l3_tag": "",
            }
            if cell in ("DEGRADED", "AMBIGUOUS_GLARE"):
                manip, interval = rng.choice(HIDDEN_MANIPULATIONS)
                row["manipulation"], row["interval"] = manip, interval
            if row["interval"] in AFTER_CP:
                row["manipulate_after"] = AFTER_CP[row["interval"]]
            m = row["manipulation"]
            if m in ("CUSTOMER_TAMPER", "REVERSE_TAMPER", "DOORSTEP_SUB"):
                row["mass_change_g"] = "0" if cell == "AMBIGUOUS_GLARE" else str(rng.choice(MASS_CHANGES_G))
                row["weight_matched"] = "yes" if row["mass_change_g"] == "0" else "no"
            if m == "FLYER_CHANGE":
                row["new_l1_fwd_seal"] = sid("SEAL-")
                row["seal_action"] = "flyer_replaced_logged"
            if m == "DOORSTEP_SUB":
                row["decoy_l1_seal"], row["decoy_l2_seal"], row["decoy_l3_tag"] = sid("SEAL-"), sid("SEAL-"), sid("TAG-")
                row["seal_action"] = "all_decoy"
            if m in ("CUSTOMER_TAMPER", "REVERSE_TAMPER"):
                row["seal_action"] = "subtle" if cell == "AMBIGUOUS_GLARE" else rng.choice(["torn", "replaced"])
                if row["seal_action"] == "replaced":
                    row["repl_l2_seal"], row["repl_l3_tag"] = sid("SEAL-"), sid("TAG-")
                    if m == "REVERSE_TAMPER":
                        row["repl_l1_ret_seal"] = sid("SEAL-")
            if cell == "DEGRADED":
                row["degraded_cp"] = rng.choice(BOUNDS[row["interval"]])
                row["degradation"] = "DARK_PHOTO+SCALE_ERROR"
                row["expected_omega"] = "DEG"
                row["expected_label"] = "ATTR_ABSTAIN_DEGRADED"
            elif cell == "AMBIGUOUS_GLARE":
                row["glare_cps"] = "+".join(BOUNDS[row["interval"]])
                row["expected_omega"] = "IND"
                row["expected_label"] = "ATTR_ABSTAIN_INDISTINGUISHABLE"
            else:
                row["expected_label"] = EXPECTED_LABEL[row["interval"]]
            rows.append(row)
    rng.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["run_order"] = i
        r["session"] = (i - 1) // 15 + 1
    return rows


def split_calibration(rows, seed: int, frac: float = 0.2):
    """Stratified calibration/test split by cell, exactly round(n*frac) calibration journeys
    (largest-remainder allocation across cells; Amendment v2.6, Section 5)."""
    rng = random.Random(seed + 1)
    by_cell = {}
    for r in rows:
        by_cell.setdefault(r["cell"], []).append(r)
    target = round(len(rows) * frac)
    quota = {c: int(len(v) * frac) for c, v in by_cell.items()}
    rema = sorted(by_cell, key=lambda c: (-(len(by_cell[c]) * frac - quota[c]), rng.random()))
    for c in rema[: target - sum(quota.values())]:
        quota[c] += 1
    for c, cell_rows in by_cell.items():
        cal = set(id(x) for x in rng.sample(cell_rows, quota[c]))
        for r in cell_rows:
            r["split"] = "calibration" if id(r) in cal else "test"


def commitments(rows):
    """Salted SHA-256 commitment per journey; salts stay restricted."""
    public, salts = [], {}
    for r in sorted(rows, key=lambda x: x["journey_code"]):
        salt = secrets.token_hex(16)
        payload = json.dumps({k: r[k] for k in sorted(r) if k not in ("run_order", "session")}, sort_keys=True)
        digest = hashlib.sha256((salt + "|" + payload).encode()).hexdigest()
        salts[r["journey_code"]] = salt
        public.append({"journey_code": r["journey_code"], "sha256": digest})
    return public, salts


# ----------------------------------------------------------------------------
# PDF helpers
# ----------------------------------------------------------------------------
def qr(c, data, x, y, size):
    w = QrCodeWidget(data)
    b = w.getBounds()
    d = Drawing(size, size, transform=[size / (b[2] - b[0]), 0, 0, size / (b[3] - b[1]), 0, 0])
    d.add(w)
    renderPDF.draw(d, c, x, y)


def wrap(c, text, x, y, width, font="Helvetica", size=9, leading=11):
    c.setFont(font, size)
    words, line = text.split(), ""
    for w in words:
        trial = (line + " " + w).strip()
        if c.stringWidth(trial, font, size) > width:
            c.drawString(x, y, line)
            y -= leading
            line = w
        else:
            line = trial
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


SEAL_FIELDS = ["l1_fwd_seal", "l2_box_seal", "l3_item_tag", "l1_ret_seal", "new_l1_fwd_seal", "decoy_l1_seal",
               "decoy_l2_seal", "decoy_l3_tag", "repl_l1_ret_seal", "repl_l2_seal", "repl_l3_tag"]


def seal_labels(path, rows):
    """3 x 8 grid of QR labels showing only the ID. Genuine, decoy and replacement labels look identical.
    SEAL- labels are stickers (L1 flyer seals, L2 box stickers); TAG- labels are tied on with a cable tie (L3)."""
    labels = []
    for r in sorted(rows, key=lambda x: x["run_order"]):
        labels.extend(r[f] for f in SEAL_FIELDS if r[f])
    c = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    cols, rows_per = 3, 8
    lw, lh = (W - 20 * mm) / cols, (H - 20 * mm) / rows_per
    for i, seal in enumerate(labels):
        if i and i % (cols * rows_per) == 0:
            c.showPage()
        k = i % (cols * rows_per)
        x = 10 * mm + (k % cols) * lw
        y = H - 10 * mm - (k // cols + 1) * lh
        c.setDash(2, 2)
        c.rect(x + 2, y + 2, lw - 4, lh - 4)
        c.setDash()
        qr(c, seal, x + 5 * mm, y + 5 * mm, lh - 10 * mm)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + lh - 2 * mm, y + lh / 2 - 3, seal)
    c.save()


def stager_cards(path, rows, pilot):
    c = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    per_page, card_h = 2, (H - 20 * mm) / 2
    for i, r in enumerate(sorted(rows, key=lambda x: x["run_order"])):
        if i and i % per_page == 0:
            c.showPage()
        y0 = H - 10 * mm - (i % per_page + 1) * card_h
        c.rect(10 * mm, y0 + 2, W - 20 * mm, card_h - 4)
        top = y0 + card_h - 10 * mm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(15 * mm, top, f"STAGER CARD  {r['journey_code']}   run #{r['run_order']}  session {r['session']}"
                     + ("   [PILOT - excluded from analysis]" if pilot else ""))
        c.setFont("Helvetica", 9)
        c.drawString(15 * mm, top - 13, "RESTRICTED: the capturer must never see this card.")
        y = top - 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(15 * mm, y, f"Cell: {r['cell']}    Manipulation: {r['manipulation']}    Interval: {r['interval']}")
        y -= 14
        y = wrap(c, f"Pack with: L2 box sticker {r['l2_box_seal']}, L3 item tag {r['l3_item_tag']}. Give the capturer "
                    f"flyer seal {r['l1_fwd_seal']} for CP1 and {r['l1_ret_seal']} for CP3.", 15 * mm, y, W - 35 * mm,
                 size=9, leading=11)
        y -= 1
        extra = []
        if r["mass_change_g"]:
            extra.append(f"Mass change: {r['mass_change_g']} g")
        if r["seal_action"] not in ("none",):
            extra.append(f"Seal action: {r['seal_action']}")
        for f, lab in [("new_l1_fwd_seal", "New flyer seal"), ("decoy_l1_seal", "Decoy L1"), ("decoy_l2_seal", "Decoy L2"),
                       ("decoy_l3_tag", "Decoy L3"), ("repl_l1_ret_seal", "Repl. L1 return"), ("repl_l2_seal", "Repl. L2"),
                       ("repl_l3_tag", "Repl. L3")]:
            if r[f]:
                extra.append(f"{lab}: {r[f]}")
        if extra:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(15 * mm, y, "   ".join(extra))
            y -= 14
        else:
            y -= 4
        instr = INSTRUCTIONS.get(r["manipulation"], "")
        if r["manipulate_after"]:
            instr = f"[Do this between {r['manipulate_after']} and the next checkpoint] " + instr
        y = wrap(c, "Do: " + instr, 15 * mm, y, W - 35 * mm, size=10, leading=12)
        if r["seal_action"] in SEAL_ACTION_TEXT:
            y = wrap(c, "Seal action: " + SEAL_ACTION_TEXT[r["seal_action"]], 15 * mm, y - 2, W - 35 * mm, size=10, leading=12)
        if r.get("weight_matched") == "yes":
            y = wrap(c, "WEIGHT-MATCHED: mass change is 0 g. Add filler (washers/sand) until the parcel weighs the "
                        "same as at the previous checkpoint (within 1 g). Only the seal/appearance should reveal it.",
                     15 * mm, y - 2, W - 35 * mm, font="Helvetica-Bold", size=10, leading=12)
        if r["cell"] == "DEGRADED":
            y = wrap(c, f"Degradation: the capture card tells the capturer to shoot {r['degraded_cp']} in the dark "
                        "and record SCALE ERROR. Check it was done.", 15 * mm, y - 2, W - 35 * mm, size=10, leading=12)
        if r["cell"] == "AMBIGUOUS_GLARE":
            y = wrap(c, f"Keep the defect SMALL: a dent under 1 cm for transit damage, or the SUBTLE seal lift for tamper. The capture card asks for flash glare over the "
                        f"box top at {r['glare_cps']}.", 15 * mm, y - 2, W - 35 * mm, size=10, leading=12)
        y -= 6
        c.setFont("Helvetica", 9)
        for line in ["Overhead video file: ________________________   Item ID used: __________",
                     "ACTUAL manipulation (write exactly what happened): _______________________________________",
                     "Deviation from plan? (Y/N) ___  Notes: _________________________________________________",
                     "Stager: __________   Time (UTC) start ________ end ________"]:
            c.drawString(15 * mm, y, line)
            y -= 13
    c.save()


def capture_cards(path, rows, pilot):
    """Capturer cards: journey QR + checklist, NO cell or manipulation info."""
    c = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    per_page, card_h = 2, (H - 20 * mm) / 2
    for i, r in enumerate(sorted(rows, key=lambda x: x["run_order"])):
        if i and i % per_page == 0:
            c.showPage()
        y0 = H - 10 * mm - (i % per_page + 1) * card_h
        c.rect(10 * mm, y0 + 2, W - 20 * mm, card_h - 4)
        qr(c, r["journey_code"], W - 50 * mm, y0 + card_h - 45 * mm, 35 * mm)
        top = y0 + card_h - 12 * mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(15 * mm, top, f"CAPTURE CARD  {r['journey_code']}   run #{r['run_order']}"
                     + ("  [PILOT]" if pilot else ""))
        y = top - 18
        c.setFont("Helvetica", 9)
        y = wrap(c, "Weigh the BOX ONLY (never with a flyer), 3 times, lifting it off between readings. Photograph "
                    "the box TOP and LABEL SIDE, the L2 box sticker and the L3 item tag up close, and every flyer seal "
                    "BEFORE you open it. Same distance and angles every time.", 15 * mm, y, W - 75 * mm, size=9, leading=11)
        y -= 4
        steps = {
            "CP1": f"Box: top, label, L2, L3 photos; weigh. Then put the box in a flyer, close it with seal "
                   f"{r['l1_fwd_seal']}, photograph the seal.",
            "CP2": "Photograph the flyer seal (do not open yet). Open the flyer. Box: top, label, L2, L3 photos; weigh.",
            "CP3": f"Box: top, label, L2, L3 photos; weigh. Then put the box in a return flyer, close it with seal "
                   f"{r['l1_ret_seal']}, photograph the seal.",
            "CP4": "Photograph the return flyer seal (do not open yet). Open the flyer. Box: top, label, L2, L3 photos; weigh.",
        }
        for cp in ["CP1 dispatch", "CP2 delivery/OBD", "CP3 return pickup", "CP4 warehouse intake"]:
            key = cp.split()[0]
            special = ""
            if r["cell"] == "DEGRADED" and r["degraded_cp"] == key:
                special = "  >> SPECIAL: lights OFF for ALL photos; record scale as ERROR (no weights)"
            if r["cell"] == "AMBIGUOUS_GLARE" and key in r["glare_cps"]:
                special = "  >> SPECIAL: flash ON, glare covering the box top and L2 sticker"
            c.setFont("Helvetica-Bold", 10)
            c.drawString(15 * mm, y, cp + special)
            y -= 12
            y = wrap(c, steps[key], 18 * mm, y, W - 75 * mm, size=8.5, leading=10)
            c.setFont("Helvetica", 9)
            c.drawString(18 * mm, y, "[ ] top [ ] label [ ] L2 [ ] L3 [ ] flyer seal   w1 _____ g  w2 _____ g  w3 _____ g   time _____")
            y -= 11
            c.drawString(18 * mm, y, "Seal IDs read: L1 ________ L2 ________ L3 ________   Carrier note: ______________  Capturer: ____")
            y -= 15
    c.save()


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=120, choices=[10, 120])
    ap.add_argument("--pilot", action="store_true", help="10-journey pilot (excluded from analysis)")
    ap.add_argument("--out", default="kit_output")
    a = ap.parse_args()
    if a.pilot != (a.n == 10):
        ap.error("use --n 10 together with --pilot, or --n 120 without it")

    cells = PILOT_CELLS if a.pilot else MAIN_CELLS
    rows = build_assignment(cells, a.seed)
    if not a.pilot:
        split_calibration(rows, a.seed)
    else:
        for r in rows:
            r["split"] = "pilot"

    restricted = os.path.join(a.out, "restricted")
    printd = os.path.join(a.out, "print")
    public = os.path.join(a.out, "public")
    for d in (restricted, printd, public):
        os.makedirs(d, exist_ok=True)

    fields = ["run_order", "session", "journey_code", "cell", "manipulation", "interval", "manipulate_after",
              "mass_change_g", "weight_matched", "seal_action", "degraded_cp", "degradation", "glare_cps",
              "expected_omega", "expected_label"] + SEAL_FIELDS + ["split"]
    write_csv(os.path.join(restricted, "assignment.csv"), sorted(rows, key=lambda x: x["run_order"]), fields)

    pub, salts = commitments(rows)
    with open(os.path.join(restricted, "salts.json"), "w") as f:
        json.dump(salts, f, indent=1)
    manifest = {
        "protocol": "TriNetra amendment v2.6.0",
        "kind": "pilot" if a.pilot else "main",
        "n": len(rows),
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed_sha256": hashlib.sha256(str(a.seed).encode()).hexdigest(),
        "commitments": pub,
    }
    mpath = os.path.join(public, f"truth_manifest_{'pilot' if a.pilot else 'main'}.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=1)
    manifest_hash = hashlib.sha256(open(mpath, "rb").read()).hexdigest()

    # Public: capture order without any cell information
    write_csv(os.path.join(public, "capture_order.csv"), sorted(rows, key=lambda x: x["run_order"]),
              ["run_order", "session", "journey_code"])
    with open(os.path.join(public, "capture_sheet_template.csv"), "w", newline="") as f:
        csv.writer(f).writerow(["journey_code", "cp", "photo_top", "photo_label", "photo_l2", "photo_l3", "photo_l1",
                                "w1_g", "w2_g", "w3_g", "scale_id", "scale_status", "l1_seal_read", "l1_state",
                                "l2_seal_read", "l2_state", "l3_tag_read", "l3_state", "lighting_note",
                                "carrier_note", "capturer", "timestamp_local"])
    with open(os.path.join(restricted, "staging_log_template.csv"), "w", newline="") as f:
        csv.writer(f).writerow(["journey_code", "actual_manipulation", "actual_interval", "actual_mass_change_g",
                                "actual_seal_action", "layers_breached", "seal_ids_applied_by_stager",
                                "degraded_cp_actual", "glare_actual", "item_id", "overhead_video_file",
                                "overhead_video_sha256", "deviation", "notes", "stager", "start_utc", "end_utc"])

    seal_labels(os.path.join(printd, "seal_labels.pdf"), rows)
    stager_cards(os.path.join(restricted, "stager_cards.pdf"), rows, a.pilot)
    capture_cards(os.path.join(printd, "capture_cards.pdf"), rows, a.pilot)

    counts = {}
    for r in rows:
        counts[r["cell"]] = counts.get(r["cell"], 0) + 1
    print(f"Journeys: {len(rows)}  cells: {counts}")
    if not a.pilot:
        print("Split:", {s: sum(r['split'] == s for r in rows) for s in ('calibration', 'test')})
    print(f"Truth manifest: {mpath}\nManifest SHA-256: {manifest_hash}")
    print("NEXT: commit public/truth_manifest_*.json to git BEFORE staging (Gate G-2). "
          "Keep restricted/ out of git and away from the capturer.")


if __name__ == "__main__":
    main()

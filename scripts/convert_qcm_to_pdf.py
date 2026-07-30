#!/usr/bin/env python3
"""
Convertit tous les fichiers Markdown du dossier qcm/ en PDF professionnels (dossier pdf/).
Utilise Google Chrome en mode headless pour un rendu typographique propre.
"""

from __future__ import annotations

import base64
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QCM_DIR = ROOT / "qcm"
PDF_DIR = ROOT / "pdf"
CSS_FILE = ROOT / "scripts" / "assets" / "qcm-pdf.css"
VENDOR_DIR = ROOT / "scripts" / ".vendor"
LOGO_FILE = ROOT / "images" / "logo-livecampus.png"
PROFILE_FILE = ROOT / "images" / "profil.png"
EMAIL_TO = "y.aumagy@gmail.com"
EMAIL_TO_NAME = "M. AUMAGY Yannick"
EMAIL_FROM_NAME = "Antoine MASIA"

CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
]


def find_chrome() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Aucun navigateur Chromium trouvé (Chrome / Chromium / Edge)."
    )


def ensure_markdown() -> None:
    vendor = str(VENDOR_DIR)
    if vendor not in sys.path:
        sys.path.insert(0, vendor)

    try:
        import markdown  # noqa: F401
        return
    except ImportError:
        pass

    print("→ Installation locale de markdown (scripts/.vendor)…")
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(VENDOR_DIR),
            "--quiet",
            "markdown",
        ],
    )
    if vendor not in sys.path:
        sys.path.insert(0, vendor)


def file_to_data_uri(path: Path, *, max_side: int = 256, jpeg_quality: int = 78) -> str:
    """Réduit et compresse les images pour un PDF plus léger / plus fluide."""
    vendor = str(VENDOR_DIR)
    if vendor not in sys.path:
        sys.path.insert(0, vendor)

    try:
        from PIL import Image
        from io import BytesIO
    except ImportError:
        print("→ Installation locale de pillow (scripts/.vendor)…")
        VENDOR_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                str(VENDOR_DIR),
                "--quiet",
                "pillow",
            ],
        )
        if vendor not in sys.path:
            sys.path.insert(0, vendor)
        from PIL import Image
        from io import BytesIO

    with Image.open(path) as img:
        img = img.convert("RGBA")
        w, h = img.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        # Logo : garder la transparence PNG ; photo : JPEG plus léger
        if path.suffix.lower() == ".png" and "logo" in path.name.lower():
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True)
            mime = "image/png"
        else:
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            buf = BytesIO()
            background.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
            mime = "image/jpeg"

        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:{mime};base64,{encoded}"


def build_cyber_layer() -> str:
    # Conservé pour compatibilité d'appel : fond géré en CSS (plus léger).
    return ""


def extract_meta(md_text: str) -> dict[str, str]:
    meta = {
        "student": "Étudiant",
        "livrable": "QUIZ",
        "chapitres": "",
        "modalite": "Travail individuel",
        "title": "Remédiation et Législation",
    }

    m_title = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if m_title:
        meta["title"] = m_title.group(1).strip()

    for key, pattern in [
        ("student", r"\*\*Étudiant\s*:\*\*\s*(.+)"),
        ("livrable", r"\*\*Livrable\s*:\*\*\s*(.+)"),
        ("chapitres", r"\*\*Chapitres couverts\s*:\*\*\s*(.+)"),
        ("modalite", r"\*\*Modalité\s*:\*\*\s*(.+)"),
    ]:
        match = re.search(pattern, md_text, re.IGNORECASE)
        if match:
            meta[key] = match.group(1).strip()

    return meta


def build_header(meta: dict[str, str], logo_uri: str, profile_uri: str) -> str:
    subtitle_bits = [meta["livrable"]]
    if meta["chapitres"]:
        subtitle_bits.append(f"Chapitres {meta['chapitres']}")
    subtitle_bits.append(meta["modalite"])
    subtitle = " · ".join(subtitle_bits)

    return f"""
<header class="doc-header">
  <div class="doc-header__brand">
    <img class="doc-header__logo" src="{logo_uri}" alt="Livecampus" />
    <div class="doc-header__meta">
      <p class="school">Livecampus</p>
      <p class="doc-title">{html.escape(meta["title"])}</p>
      <p class="doc-sub">{html.escape(subtitle)}</p>
    </div>
  </div>
  <div class="doc-header__profile">
    <div class="doc-header__profile-text">
      <p class="name">{html.escape(meta["student"])}</p>
      <p class="role">Étudiant</p>
    </div>
    <img class="doc-header__photo" src="{profile_uri}" alt="Photo de profil" />
  </div>
</header>
"""


def md_to_html(
    md_text: str,
    css: str,
    title: str,
    logo_uri: str,
    profile_uri: str,
) -> str:
    import markdown

    meta = extract_meta(md_text)
    body = markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )
    header = build_header(meta, logo_uri, profile_uri)
    cyber = build_cyber_layer()

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <style>
{css}
  </style>
</head>
<body class="qcm-doc">
{cyber}
<div class="doc-wrap">
{header}
{body}
<footer class="doc-footer">
  <span>Livecampus — Remédiation et Législation</span>
  <span>{html.escape(meta["student"])} — {html.escape(meta["livrable"])}</span>
</footer>
</div>
</body>
</html>
"""


def build_email_draft(meta: dict[str, str], pdf_name: str) -> str:
    livrable = meta.get("livrable", "QUIZ")
    chapitres = meta.get("chapitres", "").strip()
    titre = meta.get("title", "Remédiation et Législation")

    if chapitres:
        sujet = f"[Livecampus] {titre} — {livrable} (chapitres {chapitres})"
        accroche = (
            f"Je vous prie de trouver ci-joint mon livrable {livrable} "
            f"portant sur les chapitres {chapitres} du cours « {titre} »."
        )
    else:
        sujet = f"[Livecampus] {titre} — {livrable}"
        accroche = (
            f"Je vous prie de trouver ci-joint mon livrable {livrable} "
            f"du cours « {titre} »."
        )

    return f"""À : {EMAIL_TO}
Destinataire : {EMAIL_TO_NAME}
De : {EMAIL_FROM_NAME}

Objet :
{sujet}

--------------------------------------------------
CORPS DU MAIL (copier-coller)
--------------------------------------------------

Bonjour {EMAIL_TO_NAME},

{accroche}

Le fichier joint est nommé :
{pdf_name}

Je reste disponible pour tout complément d'information.

Cordialement,
{EMAIL_FROM_NAME}
"""


def write_email_draft(meta: dict[str, str], pdf_path: Path) -> Path:
    draft = build_email_draft(meta, pdf_path.name)
    out = PDF_DIR / f"EMAIL_{pdf_path.stem}.txt"
    out.write_text(draft, encoding="utf-8")
    return out


def chrome_print_pdf(chrome: Path, html_path: Path, pdf_path: Path) -> None:
    html_uri = html_path.resolve().as_uri()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        "--no-margins",
        html_uri,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def convert_all() -> None:
    ensure_markdown()
    chrome = find_chrome()
    css = CSS_FILE.read_text(encoding="utf-8")

    if not LOGO_FILE.is_file():
        raise FileNotFoundError(f"Logo introuvable : {LOGO_FILE}")
    if not PROFILE_FILE.is_file():
        raise FileNotFoundError(f"Photo de profil introuvable : {PROFILE_FILE}")

    logo_uri = file_to_data_uri(LOGO_FILE)
    profile_uri = file_to_data_uri(PROFILE_FILE)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    md_files = sorted(QCM_DIR.glob("*.md"))

    if not md_files:
        print("Aucun fichier .md trouvé dans qcm/")
        return

    print(f"→ Conversion de {len(md_files)} fichier(s) Markdown → PDF")
    print(f"  Source : {QCM_DIR}")
    print(f"  Sortie : {PDF_DIR}")
    print(f"  Moteur : {chrome.name}")
    print("  Branding : logo Livecampus + photo de profil")
    print()

    with tempfile.TemporaryDirectory(prefix="qcm-pdf-") as tmp:
        tmp_dir = Path(tmp)
        for md_path in md_files:
            title = md_path.stem
            md_text = md_path.read_text(encoding="utf-8")
            html_doc = md_to_html(md_text, css, title, logo_uri, profile_uri)
            html_path = tmp_dir / f"{title}.html"
            html_path.write_text(html_doc, encoding="utf-8")

            out_pdf = PDF_DIR / f"{title}.pdf"
            chrome_print_pdf(chrome, html_path, out_pdf)
            size_kb = out_pdf.stat().st_size / 1024
            print(f"  ✓ {out_pdf.name} ({size_kb:.0f} Ko)")

            meta = extract_meta(md_text)
            email_path = write_email_draft(meta, out_pdf)
            print(f"  ✓ {email_path.name} (mail prêt à coller)")

    print()
    print(f"✓ Terminé. PDF disponibles dans : {PDF_DIR}")


def main() -> int:
    if not QCM_DIR.is_dir():
        print(f"Erreur : dossier qcm/ introuvable ({QCM_DIR})", file=sys.stderr)
        return 1
    if not CSS_FILE.is_file():
        print(f"Erreur : CSS introuvable ({CSS_FILE})", file=sys.stderr)
        return 1

    try:
        convert_all()
    except subprocess.CalledProcessError as exc:
        print("Erreur lors de la génération PDF :", file=sys.stderr)
        print(exc.stderr or exc.stdout or exc, file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

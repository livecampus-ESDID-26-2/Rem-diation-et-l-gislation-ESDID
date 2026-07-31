#!/usr/bin/env python3
"""
Convertit les fichiers Markdown de qcm/ et mini-cas/ en PDF professionnels (dossier pdf/).
Utilise Google Chrome en mode headless pour un rendu typographique propre.
"""

from __future__ import annotations

import base64
import html
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIRS = [ROOT / "qcm", ROOT / "mini-cas"]
PDF_DIR = ROOT / "pdf"
IMAGES_DIR = ROOT / "images"
CSS_FILE = ROOT / "scripts" / "assets" / "qcm-pdf.css"
VENDOR_DIR = ROOT / "scripts" / ".vendor"
LOGO_FILE = IMAGES_DIR / "logo-livecampus.png"
PROFILE_FILE = IMAGES_DIR / "antoine_masia.png"
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


def is_diagram_image(path: Path) -> bool:
    name = path.name.lower()
    return "schema" in name or "diagram" in name or "figure" in name


def file_to_data_uri(
    path: Path,
    *,
    max_side: int = 256,
    jpeg_quality: int = 78,
) -> str:
    """Réduit / encode les images pour le HTML → PDF.

    Photos : JPEG compact.
    Schémas / logos : PNG (pas d’artefacts JPEG sur le texte).
    """
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

    keep_png = "logo" in path.name.lower() or is_diagram_image(path)

    with Image.open(path) as img:
        w, h = img.size
        scale = min(1.0, max_side / max(w, h))

        if keep_png:
            # Conserver le mode d’origine autant que possible (fonds sombres OK)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA") if "A" in img.getbands() else img.convert("RGB")
            if scale < 1.0:
                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True, compress_level=6)
            mime = "image/png"
        else:
            img = img.convert("RGBA")
            if scale < 1.0:
                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            buf = BytesIO()
            background.save(
                buf, format="JPEG", quality=jpeg_quality, optimize=True, progressive=True
            )
            mime = "image/jpeg"

        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:{mime};base64,{encoded}"


def slugify_name(name: str) -> str:
    """'MASIA Antoine' -> 'antoine_masia' ; 'BADET Mael' -> 'mael_badet'."""
    cleaned = unicodedata.normalize("NFKD", name)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    parts = re.findall(r"[A-Za-z0-9]+", cleaned)
    if len(parts) >= 2:
        # NOM Prenom -> prenom_nom
        return f"{parts[-1].lower()}_{parts[0].lower()}"
    return "_".join(p.lower() for p in parts)


def find_member_photo(name: str) -> Path | None:
    slug = slugify_name(name)
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = IMAGES_DIR / f"{slug}{ext}"
        if candidate.is_file():
            return candidate
    return None


def member_sort_key(name: str) -> tuple[str, str]:
    """Clé de tri alphabétique NOM puis prénom ('MASIA Antoine' -> ('MASIA', 'ANTOINE'))."""
    cleaned = unicodedata.normalize("NFKD", name)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    parts = re.findall(r"[A-Za-z0-9]+", cleaned)
    if not parts:
        return ("", "")
    if len(parts) == 1:
        return (parts[0].upper(), "")
    return (parts[0].upper(), " ".join(parts[1:]).upper())


def sort_members_alpha(members: list[str]) -> list[str]:
    return sorted(members, key=member_sort_key)


def last_name_from_member(name: str) -> str:
    """'MASIA Antoine' -> 'MASIA'."""
    cleaned = unicodedata.normalize("NFKD", name)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    parts = re.findall(r"[A-Za-z0-9]+", cleaned)
    return parts[0].upper() if parts else "MEMBRE"


def build_group_pdf_stem(meta: dict, fallback_stem: str) -> str:
    """
    NOM_DU_COURS_NOM1_NOM2_NOM3_MINI_CAS_1_G1
    Noms de famille en ordre alphabétique. Conserve le suffixe MINI_CAS_… du fichier source.
    """
    members = sort_members_alpha(meta.get("members") or [])
    last_names = [last_name_from_member(m) for m in members]
    last_names = [n for n in last_names if n]
    if not last_names:
        return fallback_stem

    names_part = "_".join(last_names)

    match = re.search(r"(MINI_CAS_\d+_G\d+)$", fallback_stem, re.IGNORECASE)
    if match:
        suffix = match.group(1).upper()
        return f"REMEDIATION_ET_LEGISLATION_{names_part}_{suffix}"

    groupe = str(meta.get("groupe") or "G1").upper().replace(" ", "")
    livrable = str(meta.get("livrable") or "MINI_CAS_1")
    livrable_slug = re.sub(r"[^A-Za-z0-9]+", "_", livrable).strip("_").upper()
    return f"REMEDIATION_ET_LEGISLATION_{names_part}_{livrable_slug}_{groupe}"


def extract_group_members(md_text: str) -> list[str]:
    match = re.search(
        r"\*\*Membres du groupe\s*:\*\*\s*\n((?:[-*]\s+.+\n?)+)",
        md_text,
        re.IGNORECASE,
    )
    if not match:
        return []
    members = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith(("-", "*")):
            members.append(re.sub(r"^[-*]\s+", "", line).strip())
    return sort_members_alpha(members)


def extract_meta(md_text: str) -> dict[str, str]:
    meta = {
        "student": "Étudiant",
        "livrable": "QUIZ",
        "chapitres": "",
        "modalite": "Travail individuel",
        "groupe": "",
        "professeur": "",
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
        ("groupe", r"\*\*Groupe\s*:\*\*\s*(.+)"),
        ("professeur", r"\*\*Professeur\s*:\*\*\s*(.+)"),
    ]:
        match = re.search(pattern, md_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            value = re.sub(r"\*\*(.+?)\*\*", r"\1", value)
            meta[key] = value

    members = extract_group_members(md_text)
    if members:
        meta["student"] = ", ".join(members)
        meta["members"] = members  # type: ignore[assignment]
    else:
        meta["members"] = []  # type: ignore[assignment]

    return meta


def is_group_doc(meta: dict) -> bool:
    modalite = str(meta.get("modalite", "")).lower()
    livrable = str(meta.get("livrable", "")).lower()
    return "groupe" in modalite or "mini cas" in livrable or "mini-cas" in livrable


def strip_cover_meta_from_markdown(md_text: str) -> str:
    """Retire le titre + métadonnées (page de garde générée à part)."""
    match = re.search(r"^##\s+", md_text, re.MULTILINE)
    if not match:
        return md_text
    return md_text[match.start() :].lstrip()


def build_cover_page(meta: dict, logo_uri: str, profile_uri: str) -> str:
    """Page de garde complète : école, cours, professeur, membres."""
    members = meta.get("members") or []
    cards = []
    for name in members:
        photo = find_member_photo(name)
        photo_uri = file_to_data_uri(photo, max_side=360, jpeg_quality=90) if photo else profile_uri
        cards.append(
            f"""
            <article class="cover-card">
              <img src="{photo_uri}" alt="{html.escape(name)}" />
              <p class="cover-card__name">{html.escape(name)}</p>
            </article>
            """
        )

    ecole = "Livecampus"
    cours = meta.get("title") or "Remédiation et Législation"
    professeur = meta.get("professeur") or "M. AUMAGY Yannick"
    livrable = meta.get("livrable") or "MINI CAS 1"
    groupe = meta.get("groupe") or ""
    chapitres = meta.get("chapitres") or ""

    details = []
    details.append(f"<div><span>École</span><strong>{html.escape(ecole)}</strong></div>")
    details.append(f"<div><span>Cours</span><strong>{html.escape(cours)}</strong></div>")
    details.append(f"<div><span>Professeur</span><strong>{html.escape(professeur)}</strong></div>")
    details.append(f"<div><span>Livrable</span><strong>{html.escape(livrable)}</strong></div>")
    if groupe:
        details.append(f"<div><span>Groupe</span><strong>{html.escape(groupe)}</strong></div>")
    if chapitres:
        details.append(
            f"<div><span>Chapitres</span><strong>{html.escape(chapitres)}</strong></div>"
        )

    return f"""
<section class="cover-page">
  <div class="cover-page__top">
    <img class="cover-page__logo" src="{logo_uri}" alt="Livecampus" />
    <p class="cover-page__school">{html.escape(ecole)}</p>
    <h1 class="cover-page__title">{html.escape(cours)}</h1>
    <p class="cover-page__livrable">{html.escape(livrable)}</p>
  </div>

  <div class="cover-page__details">
    {''.join(details)}
  </div>

  <div class="cover-page__members">
    <p class="cover-page__members-label">Membres du groupe</p>
    <div class="cover-page__gallery">
      {''.join(cards)}
    </div>
  </div>
</section>
"""


def build_header(meta: dict, logo_uri: str, profile_uri: str) -> str:
    if is_group_doc(meta):
        return build_cover_page(meta, logo_uri, profile_uri)

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


def heading_slug(text: str) -> str:
    cleaned = unicodedata.normalize("NFKD", text)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    cleaned = cleaned.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return cleaned or "section"


def extract_sommaire_entries(md_text: str) -> list[dict]:
    """Titres ## et sous-titres ### pour le sommaire."""
    entries: list[dict] = []
    seen: dict[str, int] = {}
    for match in re.finditer(r"^(#{2,3})\s+(.+)$", md_text, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
        slug = heading_slug(title)
        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 0
        entries.append(
            {
                "level": level,
                "title": title,
                "slug": slug,
                "page": None,
            }
        )
    return entries


def build_sommaire(entries: list[dict]) -> str:
    if not entries:
        return ""

    items = []
    for entry in entries:
        level = entry["level"]
        title = entry["title"]
        slug = entry["slug"]
        page = entry.get("page")
        page_label = str(page) if page else "…"
        css_mod = "sommaire__row--h2" if level == 2 else "sommaire__row--h3"
        display_title = title.upper() if level == 2 else title

        items.append(
            f"""
            <li class="sommaire__item {css_mod}">
              <a class="sommaire__row" href="#{html.escape(slug)}">
                <span class="sommaire__label">{html.escape(display_title)}</span>
                <span class="sommaire__dots" aria-hidden="true"></span>
                <span class="sommaire__page">{html.escape(page_label)}</span>
              </a>
            </li>
            """
        )

    return f"""
<section class="sommaire-page">
  <h2 class="sommaire__title">Sommaire</h2>
  <ol class="sommaire__list">
    {''.join(items)}
  </ol>
</section>
"""


def inject_heading_ids(html_body: str, entries: list[dict]) -> str:
    """Ajoute les id sur les <h2>/<h3> dans l'ordre du sommaire."""
    result = html_body
    for entry in entries:
        level = entry["level"]
        title = entry["title"]
        slug = entry["slug"]
        tag = f"h{level}"
        escaped_title = re.escape(html.escape(title))
        pattern = re.compile(
            rf"<{tag}>(\s*{escaped_title}\s*)</{tag}>",
            re.IGNORECASE,
        )
        replaced, count = pattern.subn(rf'<{tag} id="{slug}">\1</{tag}>', result, count=1)
        if count:
            result = replaced
            continue

        result, _ = re.subn(
            rf"<{tag}(?![^>]*\bid=)([^>]*)>",
            rf'<{tag} id="{slug}"\1>',
            result,
            count=1,
        )
    return result


def embed_local_images(html_body: str, base_dir: Path) -> str:
    """Remplace les <img src=\"...\"> locaux par des data-URI."""

    def replacer(match: re.Match[str]) -> str:
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
            return match.group(0)
        path = (base_dir / src).resolve()
        if not path.is_file():
            # Essai relatif à la racine du projet
            alt = (ROOT / src.lstrip("./")).resolve()
            if alt.is_file():
                path = alt
            else:
                # Essai dans images/
                name = Path(src).name
                candidate = IMAGES_DIR / name
                if candidate.is_file():
                    path = candidate
                else:
                    return match.group(0)
        try:
            # Schémas : pleine résolution (plafond haut) + PNG
            # Photos MD : un peu plus larges qu’avant
            if is_diagram_image(path):
                uri = file_to_data_uri(path, max_side=2400)
                tag = f'{prefix}{uri}{suffix}'
                if 'class="' in tag:
                    tag = tag.replace('class="', 'class="doc-schema ', 1)
                else:
                    tag = tag.replace("<img", '<img class="doc-schema"', 1)
                return tag
            uri = file_to_data_uri(path, max_side=1600, jpeg_quality=90)
            return f"{prefix}{uri}{suffix}"
        except Exception:
            return match.group(0)

    return re.sub(
        r'(<img\b[^>]*\bsrc=["\'])([^"\']+)(["\'])',
        replacer,
        html_body,
        flags=re.IGNORECASE,
    )


def normalize_search_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFKD", text)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    cleaned = cleaned.lower().replace("’", "'").replace("`", "'")
    return re.sub(r"\s+", " ", cleaned).strip()


def resolve_sommaire_pages(pdf_path: Path, entries: list[dict], *, page_offset: int = 1) -> list[dict]:
    """
    Trouve la page de chaque titre dans un PDF (sans sommaire),
    puis applique un offset (ex: +1 si on insère une page sommaire).
    """
    try:
        import fitz
    except ImportError:
        return entries

    doc = fitz.open(pdf_path)
    page_texts = [normalize_search_text(page.get_text()) for page in doc]
    doc.close()

    resolved: list[dict] = []
    search_from = 0  # index de page dans le PDF sans sommaire

    for entry in entries:
        title_norm = normalize_search_text(entry["title"])
        found_page = None

        # Cherche d'abord à partir de la dernière position (ordre du document)
        for idx in range(search_from, len(page_texts)):
            if title_norm and title_norm in page_texts[idx]:
                found_page = idx + 1
                search_from = idx  # le sous-titre suivant peut être sur la même page
                break

        if found_page is None:
            for idx, text in enumerate(page_texts):
                if title_norm and title_norm in text:
                    found_page = idx + 1
                    search_from = idx
                    break

        updated = dict(entry)
        updated["page"] = (found_page + page_offset) if found_page else None
        resolved.append(updated)

    return resolved


def wrap_keep_together_blocks(html_body: str) -> str:
    """Empêche les titres orphelins et les tableaux coupés en bas de page.

    - Figure + légende collés
    - Titre de section (h3) + intro + schéma collés (évite le gros trou
      quand l'image seule est poussée à la page suivante)
    - Chaque h4 + son contenu jusqu'au prochain titre
    """
    # Figure + légende (*Schéma — …*)
    html_body = re.sub(
        r"(<p>\s*)?(<img\b[^>]*class=\"[^\"]*doc-schema[^\"]*\"[^>]*>)(</p>)?"
        r"\s*(<p>\s*<em>[\s\S]*?</em>\s*</p>)",
        r'<div class="figure">\2\4</div>',
        html_body,
        flags=re.IGNORECASE,
    )

    # h3 + court préambule + figure → un seul bloc (pas de texte orphelin)
    html_body = re.sub(
        r"(<h3\b[^>]*>[\s\S]*?</h3>\s*(?:<p>[\s\S]*?</p>\s*){0,3})"
        r'(<div class="figure">[\s\S]*?</div>)',
        r'<div class="keep-together section-figure">\1\2</div>',
        html_body,
        flags=re.IGNORECASE,
    )

    heading_re = re.compile(r"(?P<h><h([2-4])\b[^>]*>.*?</h\2>)", re.IGNORECASE | re.DOTALL)
    matches = list(heading_re.finditer(html_body))
    if not matches:
        return html_body

    parts: list[str] = []
    cursor = 0
    for i, match in enumerate(matches):
        start = match.start()
        level = int(match.group(2))
        parts.append(html_body[cursor:start])

        end = matches[i + 1].start() if i + 1 < len(matches) else len(html_body)
        block = html_body[start:end]

        # Ne pas re-envelopper ce qui est déjà dans section-figure
        already_wrapped = html_body[max(0, start - 80) : start].rstrip().endswith(
            'section-figure">'
        ) or html_body[max(0, start - 80) : start].rstrip().endswith("section-figure\">")

        if already_wrapped:
            parts.append(block)
        elif level == 4 or (level == 3 and "<table" in block.lower()):
            parts.append(f'<div class="keep-together">{block}</div>')
        else:
            parts.append(block)
        cursor = end

    parts.append(html_body[cursor:])
    return "".join(parts)


def md_to_html(
    md_text: str,
    css: str,
    title: str,
    logo_uri: str,
    profile_uri: str,
    *,
    include_sommaire: bool = True,
    sommaire_entries: list[dict] | None = None,
) -> str:
    import markdown

    meta = extract_meta(md_text)
    group = is_group_doc(meta)
    body_src = strip_cover_meta_from_markdown(md_text) if group else md_text
    body = markdown.markdown(
        body_src,
        extensions=["extra", "sane_lists", "smarty"],
        extension_configs={
            # Numéros = ordre des définitions (alignées sur l’ordre d’apparition dans le texte)
            "footnotes": {"USE_DEFINITION_ORDER": True},
        },
        output_format="html5",
    )
    # base_dir = dossier du markdown (mini-cas/ ou qcm/) pour résoudre les images relatives
    # On passe IMAGES_DIR via les chemins relatifs du md
    body = embed_local_images(body, ROOT)
    body = wrap_keep_together_blocks(body)
    header = build_header(meta, logo_uri, profile_uri)

    sommaire = ""
    if group:
        entries = sommaire_entries or extract_sommaire_entries(body_src)
        body = inject_heading_ids(body, entries)
        if include_sommaire:
            sommaire = build_sommaire(entries)

    footer_right = (
        f"Groupe {meta['groupe']} — {meta['livrable']}"
        if meta.get("groupe")
        else f"{meta['student']} — {meta['livrable']}"
    )

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
<div class="doc-wrap">
{header}
{sommaire}
{body}
<footer class="doc-footer">
  <span>Livecampus — Remédiation et Législation</span>
  <span>{html.escape(footer_right)}</span>
</footer>
</div>
</body>
</html>
"""


def build_email_draft(meta: dict, pdf_name: str) -> str:
    livrable = meta.get("livrable", "QUIZ")
    chapitres = meta.get("chapitres", "").strip()
    titre = meta.get("title", "Remédiation et Législation")
    groupe = meta.get("groupe", "").strip()
    members = meta.get("members") or []

    if groupe:
        sujet = f"[Livecampus] {titre} — {livrable} — Groupe {groupe}"
        if chapitres:
            sujet += f" (chapitres {chapitres})"
        accroche = (
            f"Je vous prie de trouver ci-joint le livrable {livrable} "
            f"réalisé par le groupe {groupe}"
        )
        if chapitres:
            accroche += f" portant sur les chapitres {chapitres}"
        accroche += f" du cours « {titre} »."
        if members:
            accroche += "\n\nMembres du groupe : " + ", ".join(members) + "."
    elif chapitres:
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


def write_email_draft(meta: dict, pdf_path: Path) -> Path:
    draft = build_email_draft(meta, pdf_path.name)
    out = PDF_DIR / f"EMAIL_{pdf_path.stem}.txt"
    out.write_text(draft, encoding="utf-8")
    return out


def chrome_print_pdf(
    chrome: Path,
    html_path: Path,
    pdf_path: Path,
    *,
    number_pages: bool = True,
) -> None:
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
    if number_pages:
        add_page_numbers(pdf_path)


def add_page_numbers(pdf_path: Path) -> None:
    """Ajoute 'Page X / Y' en bas de chaque page."""
    try:
        import fitz
    except ImportError:
        print("  ⚠ PyMuPDF indisponible : pages non numérotées")
        return

    doc = fitz.open(pdf_path)
    total = doc.page_count
    for i, page in enumerate(doc, start=1):
        label = f"Page {i} / {total}"
        rect = page.rect
        # Bande basse dédiée à la pagination
        page.insert_textbox(
            fitz.Rect(36, rect.height - 28, rect.width - 36, rect.height - 10),
            label,
            fontsize=8,
            fontname="helv",
            color=(0.36, 0.42, 0.49),
            align=fitz.TEXT_ALIGN_CENTER,
        )
        # Liseré discret
        page.draw_line(
            fitz.Point(36, rect.height - 32),
            fitz.Point(rect.width - 36, rect.height - 32),
            color=(0.84, 0.89, 0.94),
            width=0.6,
        )
    doc.saveIncr()
    doc.close()


def collect_markdown_files() -> list[Path]:
    files: list[Path] = []
    for directory in SOURCE_DIRS:
        if directory.is_dir():
            files.extend(sorted(directory.glob("*.md")))
    return files


def convert_all() -> None:
    ensure_markdown()
    chrome = find_chrome()
    css = CSS_FILE.read_text(encoding="utf-8")

    if not LOGO_FILE.is_file():
        raise FileNotFoundError(f"Logo introuvable : {LOGO_FILE}")
    if not PROFILE_FILE.is_file():
        raise FileNotFoundError(f"Photo de profil introuvable : {PROFILE_FILE}")

    logo_uri = file_to_data_uri(LOGO_FILE, max_side=512)
    profile_uri = file_to_data_uri(PROFILE_FILE, max_side=360, jpeg_quality=90)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    md_files = collect_markdown_files()

    if not md_files:
        print("Aucun fichier .md trouvé dans qcm/ ou mini-cas/")
        return

    print(f"→ Conversion de {len(md_files)} fichier(s) Markdown → PDF")
    print(f"  Sources : qcm/ + mini-cas/")
    print(f"  Sortie  : {PDF_DIR}")
    print(f"  Moteur  : {chrome.name}")
    print()

    with tempfile.TemporaryDirectory(prefix="livrables-pdf-") as tmp:
        tmp_dir = Path(tmp)
        for md_path in md_files:
            title = md_path.stem
            md_text = md_path.read_text(encoding="utf-8")
            meta = extract_meta(md_text)
            pdf_stem = (
                build_group_pdf_stem(meta, title)
                if is_group_doc(meta)
                else title
            )
            out_pdf = PDF_DIR / f"{pdf_stem}.pdf"
            html_path = tmp_dir / f"{pdf_stem}.html"
            origin = md_path.parent.name

            if is_group_doc(meta):
                body_src = strip_cover_meta_from_markdown(md_text)
                entries = extract_sommaire_entries(body_src)

                # Passe 1 : sans sommaire, pour localiser les pages des titres
                draft_pdf = tmp_dir / f"{pdf_stem}_draft.pdf"
                html_draft = md_to_html(
                    md_text,
                    css,
                    pdf_stem,
                    logo_uri,
                    profile_uri,
                    include_sommaire=False,
                    sommaire_entries=entries,
                )
                html_path.write_text(html_draft, encoding="utf-8")
                chrome_print_pdf(chrome, html_path, draft_pdf, number_pages=False)

                entries = resolve_sommaire_pages(draft_pdf, entries, page_offset=1)

                # Passe 2 : sommaire avec numéros de page
                html_final = md_to_html(
                    md_text,
                    css,
                    pdf_stem,
                    logo_uri,
                    profile_uri,
                    include_sommaire=True,
                    sommaire_entries=entries,
                )
                html_path.write_text(html_final, encoding="utf-8")
                chrome_print_pdf(chrome, html_path, out_pdf, number_pages=True)
            else:
                html_doc = md_to_html(md_text, css, pdf_stem, logo_uri, profile_uri)
                html_path.write_text(html_doc, encoding="utf-8")
                chrome_print_pdf(chrome, html_path, out_pdf, number_pages=True)

            size_kb = out_pdf.stat().st_size / 1024
            print(f"  ✓ [{origin}] {out_pdf.name} ({size_kb:.0f} Ko)")

            email_path = write_email_draft(meta, out_pdf)
            print(f"  ✓ {email_path.name} (mail prêt à coller)")

    print()
    print(f"✓ Terminé. PDF disponibles dans : {PDF_DIR}")


def main() -> int:
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

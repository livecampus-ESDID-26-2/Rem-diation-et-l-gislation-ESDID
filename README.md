# Remédiation et Législation — Modalités des livrables

## Types de travaux

| Type | Modalité | Description |
|------|----------|-------------|
| **Quiz** | Travail **individuel** | Questions de compréhension et d'analyse portant sur les chapitres du cours |
| **Mini-cas** | Travail de **groupe** | Étude de cas pratique à traiter collectivement |

---

## Nomenclature des fichiers

Respecter strictement le format suivant pour chaque dépôt (PDF) :

### Quiz (individuel)

```text
NOM_DU_COURS_NOM_PRENOM_QUIZ_N1.pdf
```

**Exemple :**

```text
REMEDIATION_ET_LEGISLATION_MASIA_ANTOINE_QUIZ_N1.pdf
```

### Mini-cas (groupe)

```text
NOM_DU_COURS_NOM1_NOM2_NOM3_MINI_CAS_1_G1.pdf
NOM_DU_COURS_NOM1_NOM2_NOM3_MINI_CAS_2_G1.pdf
```

**Exemples :**

```text
REMEDIATION_ET_LEGISLATION_BADET_LEBLOND_LOURENCO_MASIA_MINI_CAS_1_G1.pdf
REMEDIATION_ET_LEGISLATION_BADET_LEBLOND_LOURENCO_MASIA_MINI_CAS_2_G1.pdf
```

> Inclure **tous les noms de famille** des membres du groupe, **par ordre alphabétique**.  
> Remplacer `G1` par le numéro de votre groupe (`G1`, `G2`, etc.).

---

## Règles de nommage

- Tout en **MAJUSCULES**
- Séparateurs : **underscores** (`_`) uniquement
- Pas d'accents, d'espaces ni de caractères spéciaux
- Extension finale : `.pdf`

---

## Organisation du dépôt

```text
cours/       → supports de cours (chapitres)
qcm/         → quiz individuels (brouillons Markdown)
mini-cas/    → mini-cas de groupe (brouillons Markdown)
pdf/         → livrables PDF générés
docs/        → mini-app HTML (bibliothèque + pages statiques)
scripts/     → outils (conversion MD → PDF / HTML)
```

## Génération des PDF et de la mini-app

Depuis la racine du projet :

```bash
./scripts/convert_qcm_to_pdf.sh
```

Le script :

1. Convertit **tous** les `.md` de `qcm/` et `mini-cas/` en PDF A4 (`pdf/`)
2. Génère aussi des **pages HTML uniques** (même style CSS que le PDF) pour :
   - `cours/`
   - `qcm/`
   - `mini-cas/`
3. Met à jour `docs/manifest.json` et la bibliothèque `docs/index.html`
4. Crée un fichier `EMAIL_*.txt` prêt à envoyer à **M. AUMAGY Yannick** (`y.aumagy@gmail.com`)

Options :

```bash
./scripts/convert_qcm_to_pdf.sh --html-only   # mini-app seulement (pas besoin de Chrome)
./scripts/convert_qcm_to_pdf.sh --pdf-only    # PDF seulement
```

Prévisualisation locale :

```bash
python3 -m http.server 8000 --directory docs
```

Puis ouvrir [http://localhost:8000](http://localhost:8000).

Pour un mini-cas de groupe, les photos des membres sont prises automatiquement dans `images/` (`prenom_nom.png`).

Prérequis PDF : Google Chrome (ou Chromium / Edge) installé sur macOS.

## Publier la mini-app sur GitHub Pages

1. Pousser le dépôt sur GitHub (avec le dossier `docs/` généré).
2. Sur GitHub : **Settings → Pages**.
3. Source : **Deploy from a branch**.
4. Branch : `main` (ou `master`), dossier **/docs**.
5. Enregistrer ; l’URL sera du type `https://<user>.github.io/<repo>/`.

Après chaque modification de cours / quiz / mini-cas : relancer le script, committer `docs/`, puis pousser.

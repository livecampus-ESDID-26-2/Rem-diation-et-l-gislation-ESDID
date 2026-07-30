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
NOM_DU_COURS_NOM_PRENOM_MINI_CAS_1_G1.pdf
```

**Exemple :**

```text
REMEDIATION_ET_LEGISLATION_MASIA_ANTOINE_MINI_CAS_1_G1.pdf
```

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
cours/     → supports de cours (chapitres)
qcm/       → quiz individuels (brouillons Markdown)
pdf/       → livrables PDF générés
scripts/   → outils (conversion MD → PDF)
```

## Génération des PDF (quiz)

Depuis la racine du projet :

```bash
./scripts/convert_qcm_to_pdf.sh
```

Le script crée le dossier `pdf/` et convertit **tous** les `.md` de `qcm/` en PDF A4 professionnels (via Google Chrome headless + feuille de style académique).

Il génère aussi un fichier `EMAIL_*.txt` prêt à copier-coller pour envoyer le livrable à **M. AUMAGY Yannick** (`y.aumagy@gmail.com`).

Prérequis : Google Chrome (ou Chromium / Edge) installé sur macOS.

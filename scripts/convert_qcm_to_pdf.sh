#!/usr/bin/env bash
# Convertit tous les fichiers Markdown du dossier qcm/ en PDF professionnels.
# Usage : ./scripts/convert_qcm_to_pdf.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/convert_qcm_to_pdf.py"

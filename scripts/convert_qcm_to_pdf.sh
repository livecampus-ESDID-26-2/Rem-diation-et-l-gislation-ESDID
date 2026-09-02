#!/usr/bin/env bash
# Génère les PDF (pdf/) et la mini-app HTML (docs/).
# Usage :
#   ./scripts/convert_qcm_to_pdf.sh
#   ./scripts/convert_qcm_to_pdf.sh --html-only
#   ./scripts/convert_qcm_to_pdf.sh --pdf-only

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/convert_qcm_to_pdf.py" "$@"

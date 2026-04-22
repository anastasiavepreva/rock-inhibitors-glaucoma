#!/usr/bin/env bash
# Setup script: clones upstream repositories at pinned commits and applies patches.
# Usage: bash scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
METHODS_DIR="${REPO_ROOT}/methods"
PATCHES_DIR="${REPO_ROOT}/patches"

mkdir -p "${METHODS_DIR}"

# ── RxnFlow ──────────────────────────────────────────────────────────────────
RXNFLOW_REPO="https://github.com/SeonghwanSeo/RxnFlow.git"
RXNFLOW_COMMIT="23017e364017138cf56e11ebe5a171cfdc58aeef"

echo "==> Cloning RxnFlow..."
git clone "${RXNFLOW_REPO}" "${METHODS_DIR}/rxnflow"
cd "${METHODS_DIR}/rxnflow"
git checkout "${RXNFLOW_COMMIT}"
echo "==> Applying RxnFlow patch..."
git apply "${PATCHES_DIR}/rxnflow.patch"
cd "${REPO_ROOT}"

# ── TacoGFN ──────────────────────────────────────────────────────────────────
TACOGFN_REPO="https://github.com/tsa87/tacogfn.git"
TACOGFN_COMMIT="fd50d992fbea63860eee2f48baa816b6e38c8586"

echo "==> Cloning TacoGFN..."
git clone "${TACOGFN_REPO}" "${METHODS_DIR}/tacogfn"
cd "${METHODS_DIR}/tacogfn"
git checkout "${TACOGFN_COMMIT}"
if [ -f "${PATCHES_DIR}/tacogfn.patch" ]; then
    echo "==> Applying TacoGFN patch..."
    git apply "${PATCHES_DIR}/tacogfn.patch"
fi
cd "${REPO_ROOT}"

# ── DrugFlow ─────────────────────────────────────────────────────────────────
DRUGFLOW_REPO="https://github.com/LPDI-EPFL/DrugFlow.git"
DRUGFLOW_COMMIT="TODO_PIN_COMMIT_HASH"

echo "==> Cloning DrugFlow..."
git clone "${DRUGFLOW_REPO}" "${METHODS_DIR}/drugflow"
cd "${METHODS_DIR}/drugflow"
git checkout "${DRUGFLOW_COMMIT}"
# No patch needed for DrugFlow
cd "${REPO_ROOT}"

# ── EvoSBDD ──────────────────────────────────────────────────────────────────
# EvoSBDD uses a custom implementation (no upstream repo to clone).
# The full code is provided in methods/evosbdd/.
echo "==> EvoSBDD: custom implementation, no upstream clone needed."

# ── FREED++ ──────────────────────────────────────────────────────────────────
FREEDPP_REPO="https://github.com/AIRI-Institute/FFREED.git"
FREEDPP_COMMIT="a73f22a53ea505f35b52bcd387c274391fe0fcda"

echo "==> Cloning FREED++..."
git clone "${FREEDPP_REPO}" "${METHODS_DIR}/freedpp"
cd "${METHODS_DIR}/freedpp"
git checkout "${FREEDPP_COMMIT}"
if [ -f "${PATCHES_DIR}/freedpp.patch" ]; then
    echo "==> Applying FREED++ patch..."
    git apply --whitespace=nowarn "${PATCHES_DIR}/freedpp.patch"
fi
cd "${REPO_ROOT}"

# ── Symlink shared assets ────────────────────────────────────────────────────
echo "==> Linking ocular property models into method directories..."
for method_dir in "${METHODS_DIR}"/*/; do
    ln -sf "${REPO_ROOT}/models"/*.pkl "${method_dir}" 2>/dev/null || true
done

echo ""
echo "Setup complete. Next steps:"
echo "  1. Install dependencies for each method (see upstream READMEs)"
echo "  2. Download ROCK-2 receptor: wget -P data/receptor/ https://files.rcsb.org/download/6ED6.pdb"
echo "  3. Follow run instructions in README.md"

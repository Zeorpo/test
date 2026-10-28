#!/usr/bin/env bash
# Run every suite whose tools are present; say clearly what was skipped.
cd "$(dirname "$0")/.." || exit 2
status=0
step() { echo; echo "=== $1"; }

step "lint"
python3 tests/lint_skills.py || status=1

step "router (tuning: must pass)"
python3 tests/router/run_tests.py tuning || status=1

step "router (holdout: generalisation, informational)"
python3 tests/router/run_tests.py holdout || echo "(below target; see tests/router/README.md)"

step "blender claims"
PY=${PYTHON:-python3}
if $PY -c "import bpy" 2>/dev/null; then
  $PY tests/blender/claims.py 2>&1 | grep -E "^(PASS|FAIL|Blender|[0-9]+/[0-9]+|\s+->)" || status=1
elif command -v blender >/dev/null; then
  blender -b --factory-startup --python tests/blender/claims.py 2>&1 | grep -E "^(PASS|FAIL|Blender|[0-9]+/[0-9]+|\s+->)" || status=1
else
  echo "SKIPPED: neither 'import bpy' nor a 'blender' binary is available (pip install bpy==5.2.3 on Python 3.13)"
fi

step "gltf / gltfpack"
if command -v node >/dev/null && ($PY -c "import bpy" 2>/dev/null || command -v blender >/dev/null); then
  (cd tests/gltf && { [ -d node_modules ] || npm install --silent; } \
    && { $PY make_fixture.py /tmp/art_fixture.glb >/dev/null 2>&1 || blender -b --factory-startup --python make_fixture.py -- /tmp/art_fixture.glb >/dev/null 2>&1; } \
    && node check.mjs /tmp/art_fixture.glb) || status=1
else
  echo "SKIPPED: needs node and Blender"
fi
exit $status

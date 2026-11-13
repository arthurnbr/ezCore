#!/usr/bin/env bash
# Route MeshTag.kicad_pcb with Freerouting, import the session, fill zones, run DRC.
# Usage: tools/route_pcb.sh   (run from hardware/ or anywhere; paths are resolved)
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
PCB="$HERE/MeshTag.kicad_pcb"
DSN="/tmp/mt.dsn"
SES="/tmp/mt.ses"
JAR="${FREEROUTING_JAR:-/tmp/tools/freerouting.jar}"
JAVA="${JAVA25:-/usr/lib/jvm/java-25-openjdk-amd64/bin/java}"
export KIPRJMOD="$HERE"

echo ">> export DSN"
python3 - "$PCB" "$DSN" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ExportSpecctraDSN(b, sys.argv[2])
PY

echo ">> autoroute (Freerouting)"
"$JAVA" -jar "$JAR" -de "$DSN" -do "$SES" \
  --router.autorouter.max_passes 200 2>&1 \
  | grep -iE "stage completed|unrouted|saved output|finished with state" || true

echo ">> import SES"
python3 - "$PCB" "$SES" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ImportSpecctraSES(b, sys.argv[2])
b.Save(sys.argv[1])
print("tracks:", len(list(b.GetTracks())))
PY

echo ">> finalize (keep-outs + GND pours + fill)"
python3 "$HERE/tools/build_pcb.py" finalize
echo ">> DRC"
kicad-cli pcb drc "$PCB" -o /tmp/drc.rpt --severity-error --exit-code-violations || true
tail -1 /tmp/drc.rpt
grep -oE '\[[a-z_]+\]' /tmp/drc.rpt | sort | uniq -c || true

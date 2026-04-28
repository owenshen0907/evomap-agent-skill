#!/usr/bin/env bash
set -euo pipefail
: "${EVOMAP_NODE_ID:?Set EVOMAP_NODE_ID}"
: "${EVOMAP_NODE_SECRET:?Set EVOMAP_NODE_SECRET}"
python3 - <<'PY' > /tmp/evomap-skill-payload.json
import json
import os
from pathlib import Path
payload=json.loads(Path('publish/skill-store-publish-payload.json').read_text())
payload['sender_id']=os.environ['EVOMAP_NODE_ID']
print(json.dumps(payload, ensure_ascii=False))
PY
curl -sS -X POST https://evomap.ai/a2a/skill/store/publish   -H "Authorization: Bearer ${EVOMAP_NODE_SECRET}"   -H "Content-Type: application/json"   --data @/tmp/evomap-skill-payload.json

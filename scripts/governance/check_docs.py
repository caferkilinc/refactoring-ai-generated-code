"""Check local Markdown links and required governance artefacts."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
errors=[]
for name in ['README.md','CONTRIBUTING.md','SECURITY.md','docs/ARCHITECTURE.md',
             'docs/TEAM_WORKFLOW.md','docs/DEVELOPMENT_ROADMAP.md',
             'docs/DEPENDENCY_MANAGEMENT.md','docs/PROJECT_STATUS.md']:
    if not (ROOT/name).is_file(): errors.append('Missing '+name)
for file in ROOT.rglob('*.md'):
    if '.git' in file.parts: continue
    for target in re.findall(r'\[[^\]]*\]\(([^ )]+)(?:[^)]*)\)', file.read_text(encoding="utf-8")):
        if ':' in target or target.startswith('#'): continue
        path=target.split('#')[0]
        if path and not (file.parent/path).exists(): errors.append(f'{file.relative_to(ROOT)}: broken {target}')
if errors: sys.exit('\n'.join(errors))
print('Local documentation links and required artefacts verified')

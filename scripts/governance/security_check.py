"""Deterministic repository hygiene, not a complete vulnerability scanner."""
import re
import subprocess
from pathlib import Path
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
errors=[]
for name in files:
    path=Path(name)
    if not path.is_file(): continue
    if path.suffix.lower() in ('.docx','.pem','.key','.p12') or name.startswith(('uploads/','private/')):
        errors.append('Private artefact: '+name)
    if path.name.startswith('.env') and path.name!='.env.example': errors.append('Environment secret file: '+name)
    try: content=path.read_text()
    except UnicodeError: continue
    for pattern in [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                    r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',
                    r'AKIA[0-9A-Z]{16}']:
        if re.search(pattern, content): errors.append('Potential credential: '+name)
if errors: raise SystemExit('\n'.join(errors))
print('Repository hygiene checks passed; not a claim of full security analysis')

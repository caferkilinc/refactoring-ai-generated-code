"""Deterministic repository hygiene, not a complete vulnerability scanner."""
import re
import subprocess
from pathlib import Path

PATTERNS = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
            r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}',
            r'AKIA[0-9A-Z]{16}', r'sk-(?:proj|svcacct)-[A-Za-z0-9_-]{20,}']

def file_errors(root, name):
    path = root / name
    errors = []
    # Do not follow repository links into host files or directories.
    relative = Path(name)
    if any((root / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts)+1)):
        return ['Symlink requires a separate security policy: ' + name]
    if not path.is_file():
        return []
    parts = {p.lower() for p in relative.parts}
    if path.suffix.lower() in ('.docx', '.pem', '.key', '.p12') or parts & {'uploads', 'private'}:
        errors.append('Private artefact: ' + name)
    if path.name.startswith('.env') and path.name != '.env.example':
        errors.append('Environment secret file: ' + name)
    # Invalid bytes must not make a file silently unscannable. ASCII keys remain visible.
    content = path.read_bytes().decode('utf-8', errors='replace')
    if any(re.search(pattern, content) for pattern in PATTERNS):
        errors.append('Potential credential: ' + name)
    return errors

def main():
    names = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode('utf-8').split('\0')
    errors = [error for name in set(names) if name for error in file_errors(Path.cwd(), name)]
    if errors:
        raise SystemExit('\n'.join(sorted(errors)))
    print('Repository hygiene checks passed; not a claim of full security analysis')

if __name__ == '__main__':
    main()

"""Transactional update of an owned edition; preserve the previous install intact.

Refuses running processes, modified/unknown files, reparse points or unexpected
locations. Only explicitly verified edition directories may be renamed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import psutil
from edition import EDITIONS, profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    parser.add_argument('--source-root', default='dist/dual-final')
    args = parser.parse_args()
    product = profile(args.edition)['product']
    programs = (Path(os.environ['LOCALAPPDATA'])/'Programs').resolve()
    target = programs/product
    backup = programs/f'{product}.backup-{time.time_ns()}'
    assert target.resolve().parent == backup.resolve().parent == programs
    assert target.name == product and not target.is_symlink() and not target.is_junction()
    owner = json.loads((target/'.dsh-pet-lite-owner.json').read_text(encoding='utf-8-sig'))
    assert owner['product'] == product
    for process in psutil.process_iter(['exe']):
        if process.info['exe'] and Path(process.info['exe']).resolve() == target/f'{product}.exe':
            raise RuntimeError('Exit the owned edition before updating')
    actual = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
    expected = {str(Path(p['path'])).replace('\\', '/') for p in owner['files']} | {'.dsh-pet-lite-owner.json'}
    assert actual == expected, 'Unknown or missing installation files; preserve and inspect manually'
    for record in owner['files']:
        path = target/record['path']
        assert path.resolve().is_relative_to(target)
        assert all(not p.is_symlink() and not p.is_junction() for p in [path, *path.parents] if p.is_relative_to(target))
        with path.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest().lower() == record['sha256'].lower(), record['path']
    env = os.environ.copy()
    # Windows PowerShell must resolve its own modules, not inherit pwsh 7's list.
    env.pop('PSModulePath', None)
    env.pop('PSMODULEPATH', None)
    inspected = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-File',
        str(Path(__file__).with_name('inspect_shortcuts.ps1')), '-Edition', args.edition], env=env, text=True))
    approved = {row['path'] for row in inspected}
    # Keep rollback links in local build evidence, never scattered over the Desktop.
    archive = Path(__file__).resolve().parents[1]/'build/install-backups'/f'{product}-{time.time_ns()}'
    archive.mkdir(parents=True)
    saved_links = []
    for index, value in enumerate(owner['shortcuts']):
        link = Path(value)
        assert link.name == profile(args.edition)['title']+'.lnk'
        if link.exists():
            assert str(link) in approved, 'Shortcut is outside verified per-user locations'
            saved = archive/f'{index}-{link.name}'
            saved_links.append((link, saved))
    try:
        for link, saved in saved_links:
            link.rename(saved)
        target.rename(backup)
        subprocess.run(['powershell', '-NoProfile', '-File', str(Path(__file__).with_name('install.ps1')),
                        '-Edition', args.edition, '-SourceRoot', args.source_root], env=env, check=True)
    except Exception:
        if backup.exists():
            if target.exists():
                target.rename(programs/f'{product}.failed-{time.time_ns()}')
            backup.rename(target)
        for link, saved in saved_links:
            if saved.exists():
                if link.exists():
                    link.rename(archive/f'failed-{time.time_ns()}-{link.name}')
                shutil.copy2(saved, link)
        raise RuntimeError('Update failed; previous installation and shortcuts restored') from None
    print(json.dumps({'edition': args.edition, 'installed': str(target), 'rollback': str(backup)}))


if __name__ == '__main__':
    main()

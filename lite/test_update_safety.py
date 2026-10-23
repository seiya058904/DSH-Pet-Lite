"""Updates must reject uncertain ownership before moving any user files."""
import hashlib
import errno
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
import update_edition


@pytest.mark.parametrize('problem', ['unknown_file', 'modified_file', 'running'])
def test_refuses_uncertain_or_running_install_before_mutation(tmp_path, monkeypatch, problem):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    target = tmp_path/'Programs/DSH-Pet-Lite-Ultra'
    target.mkdir(parents=True)
    exe = target/'DSH-Pet-Lite-Ultra.exe'
    exe.write_bytes(b'owned test data, never executed')
    owner = {'product': 'DSH-Pet-Lite-Ultra', 'files': [{'path': exe.name,
             'sha256': hashlib.sha256(exe.read_bytes()).hexdigest()}], 'shortcuts': []}
    marker = target/'.dsh-pet-lite-owner.json'
    marker.write_text(json.dumps(owner))
    if problem == 'unknown_file':
        (target/'user-note.txt').write_text('must survive')
    elif problem == 'modified_file':
        exe.write_bytes(b'user changed payload')
    processes = [SimpleNamespace(info={'exe': str(exe)})] if problem == 'running' else []
    monkeypatch.setattr(update_edition.psutil, 'process_iter', lambda _: processes)
    monkeypatch.setattr(sys, 'argv', ['update_edition.py', '--edition', 'ultra'])
    before = {p.name: p.read_bytes() for p in target.iterdir()}
    with pytest.raises((AssertionError, RuntimeError)):
        update_edition.main()
    assert {p.name: p.read_bytes() for p in target.iterdir()} == before
    assert list((tmp_path/'Programs').iterdir()) == [target]


@pytest.mark.parametrize('installer_fails', [False, True])
def test_cross_volume_shortcut_archive_and_rollback(tmp_path, monkeypatch, installer_fails):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setattr(update_edition, '__file__', str(tmp_path/'checkout/lite/update_edition.py'))
    target = tmp_path/'Programs/DSH-Pet-Lite-Ultra'
    target.mkdir(parents=True)
    exe = target/'DSH-Pet-Lite-Ultra.exe'
    exe.write_bytes(b'previous owned executable')
    link = tmp_path/'Desktop/DSH Pet Lite Ultra.lnk'
    link.parent.mkdir()
    link.write_bytes(b'previous owned shortcut')
    owner = {'product': target.name, 'files': [{'path': exe.name,
             'sha256': hashlib.sha256(exe.read_bytes()).hexdigest()}], 'shortcuts': [str(link)]}
    (target/'.dsh-pet-lite-owner.json').write_text(json.dumps(owner))
    monkeypatch.setattr(update_edition.psutil, 'process_iter', lambda _: [])
    monkeypatch.setattr(update_edition.subprocess, 'check_output', lambda *a, **k: json.dumps([{'path': str(link)}]))
    rename = os.rename
    def cross_volume_rename(source, destination, *args, **kwargs):
        if Path(source).suffix == '.lnk':
            raise OSError(errno.EXDEV, 'Simulated different volume for shortcut backup')
        return rename(source, destination, *args, **kwargs)
    monkeypatch.setattr(os, 'rename', cross_volume_rename)
    def install(*args, **kwargs):
        target.mkdir()
        exe.write_bytes(b'new executable')
        link.write_bytes(b'new shortcut')
        if installer_fails:
            raise RuntimeError('Owned simulated installer failure')
    monkeypatch.setattr(update_edition.subprocess, 'run', install)
    monkeypatch.setattr(sys, 'argv', ['update_edition.py', '--edition', 'ultra'])
    if installer_fails:
        with pytest.raises(RuntimeError, match='restored'):
            update_edition.main()
        assert exe.read_bytes() == b'previous owned executable'
        assert link.read_bytes() == b'previous owned shortcut'
    else:
        update_edition.main()
        assert exe.read_bytes() == b'new executable'
        assert link.read_bytes() == b'new shortcut'
        backup = next((tmp_path/'Programs').glob('DSH-Pet-Lite-Ultra.backup-*'))
        assert (backup/exe.name).read_bytes() == b'previous owned executable'
    archived = list((tmp_path/'checkout/build/install-backups').rglob('0-*.lnk'))
    assert len(archived) == 1 and archived[0].read_bytes() == b'previous owned shortcut'

"""Updates must reject uncertain ownership before moving any user files."""
import hashlib
import json
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

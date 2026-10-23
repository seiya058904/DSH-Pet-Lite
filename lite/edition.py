"""Explicit edition contract shared by source launch, tests and packaging."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDITIONS = ('full', 'ultra')
VERSION = '1.0.0'


def profile(edition):
    if edition not in EDITIONS:
        raise ValueError(f'Unknown edition: {edition}')
    return {'edition': edition, 'version': VERSION,
            'product': f'DSH-Pet-Lite-{edition.title()}',
            'title': f'DSH Pet Lite {edition.title()}'}


def assets_for(edition):
    profile(edition)
    return ROOT / ('assets' if edition == 'full' else 'assets-ultra')


def build_identity():
    path = ROOT / 'build-info.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None

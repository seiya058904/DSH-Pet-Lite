"""Record the actual source snapshot without inventing a clean commit identity."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from edition import EDITIONS, assets_for, profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    args = parser.parse_args()
    data = profile(args.edition)
    data['source_sha'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    inputs = ['lite/app.py', 'lite/edition.py', 'lite/roaming.py', 'lite/DSH-Pet-Lite.spec',
              'lite/requirements.txt', 'lite/requirements-build.txt', 'lite/licenses',
              'lite/assets-core' if args.edition == 'core' else 'lite/assets-ultra',
              'LICENSE', 'THIRD_PARTY_NOTICES.md']
    data['dirty'] = bool(subprocess.check_output(['git', 'status', '--porcelain', '--', *inputs]))
    data['manifest_sha256'] = hashlib.sha256((assets_for(args.edition)/'manifest.json').read_bytes()).hexdigest()
    target = Path('build/identity')/args.edition/'build-info.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps(data))


if __name__ == '__main__':
    main()

"""Package one explicit edition; never modify the historical single-edition build."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from edition import EDITIONS, VERSION, profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    parser.add_argument('--dist', type=Path, default=Path('dist/core-ultra'))
    args = parser.parse_args()
    product = profile(args.edition)['product']
    bundle = args.dist/product
    shutil.copyfile(Path(__file__).with_name('Uninstall-DSH-Pet-Lite.ps1'), bundle/'Uninstall-DSH-Pet-Lite.ps1')
    target = args.dist/f'{product}-v{VERSION}-win-x64-portable.zip'
    with ZipFile(target, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(bundle.rglob('*')):
            if path.is_file():
                archive.write(path, Path(product)/path.relative_to(bundle))
    with target.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    data = {'edition': args.edition, 'file': target.name, 'sha256': digest,
            'zip_bytes': target.stat().st_size,
            'expanded_bytes': sum(p.stat().st_size for p in bundle.rglob('*') if p.is_file())}
    (args.dist/f'{args.edition}-package.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps(data))


if __name__ == '__main__':
    main()

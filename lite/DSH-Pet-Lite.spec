# Isolated import graph: deliberately does not collect the upstream pet package.
from pathlib import Path
import os
import sys
root = Path(SPECPATH).parent
sys.path.insert(0, str(root / 'lite'))
from edition import assets_for, profile
from pack_assets import pack_assets
edition = os.environ['DSH_BUILD_EDITION']
product = profile(edition)['product']
identity = Path(os.environ['DSH_BUILD_INFO'])
packed_assets = pack_assets(assets_for(edition), root / 'build/packed-assets' / edition)
a = Analysis([str(root / 'lite/app.py')], pathex=[str(root / 'lite')],
    binaries=[], datas=[(str(packed_assets), 'assets'), (str(identity), '.'),
                        (str(root / 'LICENSE'), '.'),
                        (str(root / 'THIRD_PARTY_NOTICES.md'), '.'),
                        (str(root / 'ASSET_LICENSE.md'), '.'),
                        (str(root / 'lite/licenses'), 'licenses')],
    hiddenimports=[], hookspath=[], runtime_hooks=[],
    # Python 3.12 random uses builtin _sha2. Its optional hashlib fallback must
    # not pull in the unused OpenSSL backend; builtin hashlib algorithms remain.
    excludes=['_hashlib', 'pet', 'PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick',
              'PySide6.QtMultimedia', 'PySide6.QtOpenGL', 'PySide6.QtSql',
              'PySide6.QtPrintSupport', 'PySide6.QtSvg', 'PIL', 'numpy', 'cv2',
              'onnxruntime', 'rapidocr', 'psutil', 'imageio_ffmpeg', 'edge_tts',
              'keyring', 'winrt', 'tkinter', 'unittest', 'pytest'] + (['roaming'] if edition == 'ultra' else []),
    noarchive=False)
# Raster QWidget backend: inspect PE imports before dropping optional image/OpenGL backends.
plugins = {'qwindows.dll', 'qico.dll', 'qwebp.dll', 'qmodernwindowsstyle.dll'}
a.binaries = [item for item in a.binaries
              if (('/plugins/' not in item[0].replace('\\', '/') or
                   Path(item[0]).name.lower() in plugins)
                  and Path(item[0]).name.lower() not in
                  {'qt6network.dll', 'qt6svg.dll', 'opengl32sw.dll'})]
# This app never installs a QTranslator. Its bilingual menu text is in app.py.
# Keep license texts; omit only Qt's unused compiled UI translations.
a.datas = [item for item in a.datas if not
           (item[0].replace('\\', '/').startswith('PySide6/translations/') and item[0].endswith('.qm'))]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=product,
          debug=False, strip=False, upx=False, console=False,
          icon=str(assets_for(edition) / 'lite.ico'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=product)

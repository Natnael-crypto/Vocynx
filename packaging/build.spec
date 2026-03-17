# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

# Collect huggingface / faster-whisper data files if necessary
datas = collect_data_files("faster_whisper")
datas += [('../vocyn_icon.ico', '.')]
datas += [('../vocyn/assets/start_rec.wav', 'vocyn/assets')]
datas += [('../vocyn/assets/*.svg', 'vocyn/assets')]
datas += [('../vocyn/licenses/*', 'vocyn/licenses')]

a = Analysis(
    ['../main.py'],
    pathex=['..'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'sounddevice',
        'numpy',
        'keyboard',
        'pynput',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'faster_whisper',
        'deep_translator',
        'openai',
        'groq'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DExtras',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtSensors',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtPositioning',
        'PySide6.QtLocation',
        'PySide6.QtWebSockets',
        'PySide6.QtWebChannel',
        'PySide6.QtRemoteObjects',
        'PySide6.QtDesigner',
        'PySide6.QtPrintSupport',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtUiTools',
        'PySide6.QtXml',
        'PySide6.QtDBus',
        'PySide6.QtNetwork',
        'torch',
        'tensorflow',
        'tensorboard',
        'lxml',
        'onnx',
        'IPython',
        'jedi',
        'scipy',
        'pandas',
        'matplotlib',
        'PIL',
        'tkinter',
        'docutils'
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='vocyn',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../vocyn_icon.ico'],
)

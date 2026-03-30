block_cipher = None
a = Analysis(['qt_app_v2_optimized.py'], pathex=['.'], binaries=[], datas=[('resources/spic_logo.png', 'resources'), ('resources/eparser_empty.db', 'resources')], hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=[], win_no_prefer_redirects=False, win_private_assemblies=False, cipher=block_cipher, noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='EFileParser', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='resources/spic_logo.png')
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='EFileParser')

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['engine.py'],
             pathex=['/Users/karlmonaghan/Projects/rogue'],
             binaries=[],
             datas=[ ( 'data/names.txt', 'data' ),
                      ( 'data/fonts', 'data/fonts' ),
                      ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='engine',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

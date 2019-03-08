# -*- mode: python -*-

block_cipher = None


a = Analysis(['main-gui.py', 'aria2.py', 'base.py', 'gl.py', 'ui/Misc.py', 'ui/UI_About.py', 'ui/UI_DownloadList.py', 'ui/UI_Main.py', 'ui/UI_NewTask.py', 'ui/UI_Setting.py', 'ui/UI_TaskDetails.py', 'ui/WidgetTaskActive.py', 'ui/WidgetTask.py', 'ui/WidgetTaskStopped.py', 'ui/WidgetTaskWaiting.py'],
             pathex=['D:\\CodeProjects\\aria2-pyui'],
             binaries=[],
             datas=[('D:\\CodeProjects\\aria2-pyui\\icons', 'icons'), ('D:\\CodeProjects\\aria2-pyui\\qss', 'qss'), ('D:\\CodeProjects\\aria2-pyui\\aria2', 'aria2'),
             ('logging.conf', '.')],
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
          [],
          exclude_binaries=True,
          name='main-gui',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main-gui')

pyinstaller -w main-gui.spec
del "dist\main-gui\data\setting.json"
copy /Y aria2.session  "dist\main-gui\data"
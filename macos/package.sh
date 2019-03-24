pyinstaller -w main-gui.spec
cp ./logging.conf ./dist/main-gui/data
echo "" > ./dist/main-gui/data/aria2.session
rm ./dist/main-gui/data/setting.json

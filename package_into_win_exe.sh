#wine ~/.wine/drive_c/users/medaphor/Local\ Settings/Application\ Data/Programs/Python/Python38/Scripts/pip.exe install pyinstaller
#wine ~/.wine/drive_c/users/medaphor/Local\ Settings/Application\ Data/Programs/Python/Python38/Scripts/pip.exe install pyqt5
#wine ~/.wine/drive_c/users/medaphor/Local\ Settings/Application\ Data/Programs/Python/Python38/Scripts/pip.exe install playsound==1.2.2

wine ~/.wine/drive_c/users/medaphor/Local\ Settings/Application\ Data/Programs/Python/Python38/Scripts/pyinstaller.exe --onefile  --add-data 'config.json;.' --add-data 'weights.json;.' --add-data 'phrases.json;.' --add-data 'audio/*mp3;audio' main.py

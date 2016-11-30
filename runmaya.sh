WINNAME="cygwin"
if [ "$OSTYPE" = "$WINNAME" ]
then
    export PYTHONPATH="$PYTHONPATH;C:\\Users\\Tim\\Projects\\MayaGameJam"
    export MAYA_SCRIPT_PATH="$MAYA_SCRIPT_PATH;C:\\Users\\Tim\\Projects\\MayaGameJam"
    export XBMLANGPATH="$XBMLANGPATH;C:\\Users\\Tim\\Projects\\MayaGameJam"
    `OS=""; TMP=""; TEMP=""; cygstart "C:\\Program Files\\Autodesk\\Maya2017\\bin\\maya.exe"`
else
    export PYTHONPATH=$PYTHONPATH:/Users/timothyso/Projects/MayaGameJam
    export MAYA_SCRIPT_PATH=$MAYA_SCRIPT_PATH:/Users/timothyso/Projects/MayaGameJam
    export XBMLANGPATH=$XBMLANGPATH:/Users/timothyso/Projects/MayaGameJam
    `open /Applications/Autodesk/maya2016/Maya.app/`
fi

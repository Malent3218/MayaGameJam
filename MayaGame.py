import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.mel
import ctypes
import os
import sys
import shutil
from math import fabs
import subprocess
import threading
import sys
import time
from maya import OpenMaya
print OpenMaya.MFileIO
import maya.utils

class GameThread(threading.Thread):
    Instance = None
    def __init__(self):
        threading.Thread.__init__(self)
        self.curSelection = None
        self.prevTarnsform = None
        self.keepRunning = True

        self.playerSphere = cmds.polySphere(sx = 10, sy = 10, name = "Player")


    def __del__(self):
        cmds.delete(self.playerSphere)

    def run(self):
        # window = cmds.window( "pyEnginePropertyWindow", title="pyEngine Property Window", widthHeight=(440, 440) , topLeftCorner=[100, 100])
        # scroll = cmds.scrollLayout("_mainScroll", height = 470  )
        # cmds.columnLayout( adjustableColumn=False, columnOffset=("both", 4) )
        # cmds.textField( "editor", width = 100, height = 100)
        # cmds.showWindow( "pyEnginePropertyWindow" )
        i = 0
        while self.keepRunning:
            #maya.utils.executeDeferred(DeferredFunc, i, {'frame': i * 3})
            i += 1
            time.sleep(0.1)


def CreateGameThread(arg):
    print "Dbg: Launching Observer thread that will save currently edited script and change selection"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop exisitng thread
    #start new thread
    GameThread.Instance = GameThread()
    GameThread.Instance.start()
def KillGameThread():
    print "Dbg: Killing Observer thread"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop exisitng thread


def LoaderAddObject(arg):
    p = cmds.textScrollList('packages', query = True, selectItem = True)
    s = cmds.textScrollList('metascripts', query = True, selectItem = True)

    print "Loading script:", s[0], "from package:", p[0]
    d = PyClient.assetmanagercommon.runMetaScript(p[0], s[0])

    pathFilename = PyClient.assetmanagercommon.appendPathToAssetsIn(d['t']['mayaRep']).replace('\\', '/')
    mFileIO = OpenMaya.MFileIO()

    print mFileIO.importFile(pathFilename, None, 0, "PEObject0")
    lastTransformAdded = None
    maxId = -1
    lastPath = None
    itDag = OpenMaya.MItDag( OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kTransform )
    while not itDag.isDone():
        path = OpenMaya.MDagPath()
        itDag.getPath( path )
        fnTransform = OpenMaya.MFnTransform( path.node() )
        name = fnTransform.partialPathName()
        if name.startswith("PEObject"):
            id = int(name[len('PEObject'):name.find(':')])
            print "PEObject Detected: ", name, 'ID:', id
            if id > maxId:
                maxId = id
                lastTransformAdded = fnTransform
                lastPath = path

        itDag.next()
    if maxId == -1 or not lastTransformAdded:
        print "Error: Could not find PEObject that was added last"
        return
    print "Adding notes to the last transform"
    dagModifier = OpenMaya.MDagModifier()
    print dagModifier
    #notes = dagModifier.createNode('notes')
    if cmds.objExists(name):
        print "Dbg: Object exists. Adding attribute metaScript"
        cmds.select(name)
        cmds.addAttr( shortName='metaScript', dt='string')
        cmds.setAttr('%s.%s'%(name,'metaScript'), d['t']['callerScript'], type='string')
        script = cmds.getAttr('%s.%s'%(name,'metaScript'))
        print repr(script)

        cmds.addAttr( shortName='peuuidStr', dt='string')
        peuuidStr = peuuid.conv.regisrtyTo4UInt32()
        if peuuidStr.endswith(','):
            peuuidStr = peuuidStr[:-1]
        cmds.setAttr('%s.%s'%(name,'peuuidStr'), peuuidStr, type='string')
        peuuidStr = cmds.getAttr('%s.%s'%(name,'peuuidStr'))
        print repr(peuuidStr)
    else:
        print "Error: object %s does not exist" % name

def ControlsUI():
    if cmds.window( "MayaGameControlsUI", exists=True ):
        cmds.deleteUI( "MayaGameControlsUI", window=True )
    if cmds.windowPref( "MayaGameControlsUI", exists=True ):
        cmds.windowPref( "MayaGameControlsUI", remove=True )

    window = cmds.window( "MayaGameControlsUI", title="Maya Game Controls", widthHeight=(440, 200) , topLeftCorner=[100, 100])

    scroll = cmds.scrollLayout("mainScroll", height = 200 )

    cmds.columnLayout( adjustableColumn=False, columnOffset=("both", 4) )


    cmds.rowLayout(numberOfColumns=2, columnWidth=[(1,200), (2, 200)], columnAlign2=('left', 'left'))
    cmds.text( 'label_select_package', label="Select Package", width = 100)
    cmds.setParent( ".." )

    cmds.button( "restart_btn", label="Restart Game", enable = 1, command=CreateGameThread, align="center", width = 150 )

    cmds.rowLayout(numberOfColumns=2, columnWidth=[(1,200), (2, 200)], columnAlign2=('left', 'left'))
    cmds.textField( "editor", width = 100)
    cmds.checkBox( 'debug_output_chkbx', label = "Debug Output", changeCommand = DebugOutputChange)
    cmds.setParent( ".." )

    cmds.showWindow( "MayaGameControlsUI" )

    CreateGameThread(1)

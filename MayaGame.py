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
import Queue
from maya import OpenMaya
print OpenMaya.MFileIO
import maya.utils

class GameThread(threading.Thread):
    Instance = None
    def __init__(self):
        threading.Thread.__init__(self)
        print "constructor"
        self.curSelection = None
        self.prevTarnsform = None
        self.keepRunning = True
        self.inputQueue = Queue.Queue()
        maya.utils.executeDeferred(self.Initialize)

    def Initialize(self):
        self.playerSphere = cmds.polySphere(sx = 10, sy = 10, name = "Player")
        self.playerX = 0;
        self.playerY = 0;

    def CleanUp(self):
        print "Deleting", self.playerSphere
        cmds.delete(self.playerSphere)

    def run(self):
        # window = cmds.window( "pyEnginePropertyWindow", title="pyEngine Property Window", widthHeight=(440, 440) , topLeftCorner=[100, 100])
        # scroll = cmds.scrollLayout("_mainScroll", height = 470  )
        # cmds.columnLayout( adjustableColumn=False, columnOffset=("both", 4) )
        # cmds.textField( "editor", width = 100, height = 100)
        # cmds.showWindow( "pyEnginePropertyWindow" )
        i = 0
        while self.keepRunning:
            maya.utils.executeDeferred(self.HandleInput)
            i += 1
            time.sleep(0.1)

        maya.utils.executeDeferred(self.CleanUp)

    def SendInputMessage(self, message):
        self.inputQueue.put(message)

    def HandleInput(self):
        while not self.inputQueue.empty():
            inputString = self.inputQueue.get();
            functionMap = {"BUTTON_UP":     [self.MovePlayer, 0.0, 1.0],
                           "BUTTON_DOWN":   [self.MovePlayer, 0.0, -1.0],
                           "BUTTON_LEFT":   [self.MovePlayer, -1.0, 0.0],
                           "BUTTON_RIGHT":  [self.MovePlayer, 1.0, 0.0]}
            t = functionMap[inputString]
            print t[1:]
            t[0](t[1:])
            self.inputQueue.task_done()

    def MovePlayer(self, direction):
        self.playerX += direction[0]
        self.playerY += direction[1]
        cmds.move( self.playerX, self.playerY, 0, self.playerSphere )


def CreateGameThread(arg):
    print "Dbg: Launching Game thread"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop exisitng thread
        time.sleep(0.5) # let thread finish cleaning up
    #start new thread
    GameThread.Instance = GameThread()
    GameThread.Instance.start()

def KillGameThread():
    print "Dbg: Stopping Game thread"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop exisitng thread

def PushButtonUp(arg):
    if GameThread.Instance != None:
        GameThread.Instance.SendInputMessage("BUTTON_UP")

def PushButtonLeft(arg):
    if GameThread.Instance != None:
        GameThread.Instance.SendInputMessage("BUTTON_LEFT")

def PushButtonDown(arg):
    if GameThread.Instance != None:
        GameThread.Instance.SendInputMessage("BUTTON_DOWN")

def PushButtonRight(arg):
    if GameThread.Instance != None:
        GameThread.Instance.SendInputMessage("BUTTON_RIGHT")

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

    cmds.button( "restart_btn", label="Restart Game", enable = 1, command=CreateGameThread, align="center", width = 150 )

    cmds.rowLayout(numberOfColumns=3, columnWidth=[(1,50), (2, 50), (3, 50)], columnAlign3=('center', 'center', 'center'))
    cmds.canvas();
    cmds.button( "up_btn", label="Up", enable = 1, command=PushButtonUp, align="center", width = 50 )
    cmds.canvas();
    cmds.setParent("..");

    cmds.rowLayout(numberOfColumns=3, columnWidth=[(1,50), (2, 50), (3, 50)], columnAlign3=('center', 'center', 'center'))
    cmds.button( "left_btn", label="Left", enable = 1, command=PushButtonLeft, align="center", width = 50 )
    cmds.button( "down_btn", label="Down", enable = 1, command=PushButtonDown, align="center", width = 50 )
    cmds.button( "right_btn", label="Right", enable = 1, command=PushButtonRight, align="center", width = 50 )
    cmds.setParent("..");

    cmds.showWindow( "MayaGameControlsUI" )

    CreateGameThread(1)

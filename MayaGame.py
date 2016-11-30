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
    class ButtonState:
        def __init__(self):
            self.pressed = False
            self.released = False
            self.held = False

        def __str__(self):
            return '\n'.join(['Pressed: ' + str(self.pressed), 'Released: ' + str(self.released), 'Held: ' + str(self.held)])

    Instance = None
    def __init__(self):
        threading.Thread.__init__(self)
        self.curSelection = None
        self.prevTarnsform = None
        self.keepRunning = True
        self.inputQueue = Queue.Queue()
        self.inputMap = { 'KEY_UP'   : 'up',
                          'KEY_DOWN' : 'down',
                          'KEY_LEFT' : 'left',
                          'KEY_RIGHT': 'right' }
        self.buttonState = {'up'   : GameThread.ButtonState(),
                            'down' : GameThread.ButtonState(),
                            'left' : GameThread.ButtonState(),
                            'right': GameThread.ButtonState()}

        self.eventMap = {}
        # eventMap = {"KEY_UP":     (self.MovePlayer, 0.0, 1.0),
        #             "KEY_DOWN":   (self.MovePlayer, 0.0, -1.0),
        #             "KEY_LEFT":   (self.MovePlayer, -1.0, 0.0),
        #             "KEY_RIGHT":  (self.MovePlayer, 1.0, 0.0)}
        maya.utils.executeDeferred(self.Initialize)

    def Initialize(self):
        self.playerSphere = cmds.polySphere(sx = 10, sy = 10, name = 'Player')
        self.playerX = 0;
        self.playerY = 0;

    def CleanUp(self):
        cmds.delete(self.playerSphere)

    def run(self):
        # window = cmds.window( "pyEnginePropertyWindow", title="pyEngine Property Window", widthHeight=(440, 440) , topLeftCorner=[100, 100])
        # scroll = cmds.scrollLayout("_mainScroll", height = 470  )
        # cmds.columnLayout( adjustableColumn=False, columnOffset=("both", 4) )
        # cmds.textField( "editor", width = 100, height = 100)
        # cmds.showWindow( "pyEnginePropertyWindow" )
        self.lastClock = time.clock()
        while self.keepRunning:
            self.HandleInput()
            maya.utils.executeDeferred(self.Update)
            time.sleep(0.0166666)

        maya.utils.executeDeferred(self.CleanUp)

    def Update(self):
        frameStartClock = time.clock()
        deltaTime = frameStartClock - self.lastClock
        # DON'T TOUCH OR PLACE ANY UPDATE CODE BEFORE THIS LINE

        if self.buttonState['up'].held:
            self.MovePlayer((0.0, 5.0 * deltaTime))

        if self.buttonState['down'].held:
            self.MovePlayer((0.0, -5.0 * deltaTime))

        if self.buttonState['left'].held:
            self.MovePlayer((-5.0 * deltaTime, 0.0))

        if self.buttonState['right'].held:
            self.MovePlayer((5.0 * deltaTime, 0.0))

        # DON'T TOUCH OR PLACE ANY UPDATE CODE AFTER THIS LINE
        self.lastClock = frameStartClock

    def SendInputMessage(self, key, state):
        self.inputQueue.put((key, state))

    def HandleInput(self):
        # clear pressed and released states
        for buttonState in self.buttonState.values():
            buttonState.pressed = False
            buttonState.released = False

        while not self.inputQueue.empty():
            key, state = self.inputQueue.get()
            # update inputState
            button = self.inputMap.get(key, None)
            if button != None and button in self.buttonState:
                buttonState = self.buttonState[button]
                if state == 'PRESSED':
                    buttonState.pressed = True
                    buttonState.held = True
                elif state == 'RELEASED':
                    buttonState.released = True
                    buttonState.held = False
                else:
                    print 'ERROR: Invalid input state', state

            # handle events
            eventString = key + '_' + state
            t = self.eventMap.get(eventString, None)
            if t != None:
                t[0](t[1:])

            self.inputQueue.task_done()

    def MovePlayer(self, direction):
        self.playerX += direction[0]
        self.playerY += direction[1]
        cmds.move( self.playerX, self.playerY, 0, self.playerSphere )


def CreateGameThread(arg=False):
    print "Dbg: Launching Game thread"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop existing thread
    #start new thread
    GameThread.Instance = GameThread()
    GameThread.Instance.start()

def KillGameThread(arg=False):
    print "Dbg: Stopping Game thread"
    if GameThread.Instance != None:
        GameThread.Instance.keepRunning = False # stop existing thread
        GameThread.Instance = None
        cmds.hotkeySet( 'MayaGame', edit=True, delete=True )


def PushKeyUp(pressed=False):
    if GameThread.Instance != None:
        if pressed:
            GameThread.Instance.SendInputMessage("KEY_UP", "PRESSED")
        else:
            GameThread.Instance.SendInputMessage("KEY_UP", "RELEASED")

def PushKeyLeft(pressed=False):
    if GameThread.Instance != None:
        if pressed:
            GameThread.Instance.SendInputMessage("KEY_LEFT", "PRESSED")
        else:
            GameThread.Instance.SendInputMessage("KEY_LEFT", "RELEASED")

def PushKeyDown(pressed=False):
    if GameThread.Instance != None:
        if pressed:
            GameThread.Instance.SendInputMessage("KEY_DOWN", "PRESSED")
        else:
            GameThread.Instance.SendInputMessage("KEY_DOWN", "RELEASED")

def PushKeyRight(pressed=False):
    if GameThread.Instance != None:
        if pressed:
            GameThread.Instance.SendInputMessage("KEY_RIGHT", "PRESSED")
        else:
            GameThread.Instance.SendInputMessage("KEY_RIGHT", "RELEASED")

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

def SetHotKeys():
    if 'MayaGame' in cmds.hotkeySet( q=True, hotkeySetArray=True):
        cmds.hotkeySet( 'MayaGame', edit=True, delete=True )
    cmds.hotkeySet( 'MayaGame', current=True )
    cmds.nameCommand( 'pushKeyUp', ann='Push Up Key', c='python("MayaGame.PushKeyUp(True)")' )
    cmds.nameCommand( 'pushKeyDown', ann='Push Down Key', c='python("MayaGame.PushKeyDown(True)")' )
    cmds.nameCommand( 'pushKeyLeft', ann='Push Left Key', c='python("MayaGame.PushKeyLeft(True)")' )
    cmds.nameCommand( 'pushKeyRight', ann='Push Right Key', c='python("MayaGame.PushKeyRight(True)")' )
    cmds.nameCommand( 'releaseKeyUp', ann='Release Up Key', c='python("MayaGame.PushKeyUp(False)")' )
    cmds.nameCommand( 'releaseKeyDown', ann='Release Down Key', c='python("MayaGame.PushKeyDown(False)")' )
    cmds.nameCommand( 'releaseKeyLeft', ann='Release Left Key', c='python("MayaGame.PushKeyLeft(False)")' )
    cmds.nameCommand( 'releaseKeyRight', ann='Release Right Key', c='python("MayaGame.PushKeyRight(False)")' )
    cmds.hotkey( keyShortcut='Up', name='pushKeyUp', releaseName='releaseKeyUp' )
    cmds.hotkey( keyShortcut='Down', name='pushKeyDown', releaseName='releaseKeyDown' )
    cmds.hotkey( keyShortcut='Left', name='pushKeyLeft', releaseName='releaseKeyLeft' )
    cmds.hotkey( keyShortcut='Right', name='pushKeyRight', releaseName='releaseKeyRight' )

def ControlsUI():
    if cmds.window( "MayaGameControlsUI", exists=True ):
        cmds.deleteUI( "MayaGameControlsUI", window=True )
    if cmds.windowPref( "MayaGameControlsUI", exists=True ):
        cmds.windowPref( "MayaGameControlsUI", remove=True )

    window = cmds.window( "MayaGameControlsUI", title="Maya Game Controls", widthHeight=(440, 200) , topLeftCorner=[100, 100], closeCommand=KillGameThread)

    scroll = cmds.scrollLayout("mainScroll", height = 200 )

    cmds.columnLayout( adjustableColumn=False, columnOffset=("both", 4) )

    cmds.button( "restart_btn", label="Restart Game", enable = 1, command=CreateGameThread, align="center", width = 150 )

    # cmds.rowLayout(numberOfColumns=3, columnWidth=[(1,50), (2, 50), (3, 50)], columnAlign3=('center', 'center', 'center'))
    # cmds.canvas();
    # cmds.button( "up_btn", label="Up", enable = 1, command=PushButtonUp, align="center", width = 50 )
    # cmds.canvas();
    # cmds.setParent("..");
    #
    # cmds.rowLayout(numberOfColumns=3, columnWidth=[(1,50), (2, 50), (3, 50)], columnAlign3=('center', 'center', 'center'))
    # cmds.button( "left_btn", label="Left", enable = 1, command=PushButtonLeft, align="center", width = 50 )
    # cmds.button( "down_btn", label="Down", enable = 1, command=PushButtonDown, align="center", width = 50 )
    # cmds.button( "right_btn", label="Right", enable = 1, command=PushButtonRight, align="center", width = 50 )
    # cmds.setParent("..");

    cmds.showWindow( "MayaGameControlsUI" )

    CreateGameThread(1)

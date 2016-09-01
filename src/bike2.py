import random
import os
import sys

# STILL TODO
# TODO replace RND with random.random()

#CONST Mode = 8
#In QB45, Screen Mode 8 was 640x480, 16 colors

class Point3D(object):
    def __init__(self):
        #self.v = [0.0, 0.0, 0.0] # TODO perhaps use a list, rather than 3 floats.
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def __getitem__(self, index):
        ## accessor
        pass

    def __setitem__(self, index):
        ## set item property
        pass


class Point2D(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

            
class LineType(object):
    def __init__(self):
        self.StartPt = 0
        self.EndPt = 0

class RampType(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.incline = 0.0
        self.length = 0.0   #length of ramp
        self.dist = 0.0     #length of jump (gap), dist btwn up ramp and down ramp

class RiderType(object):
    def __init__(self):
        self.maxspd = 0.0   #max. speed rider can reach
        self.xvel = 0.0     #x-component of speed coming off a ramp
        self.yvel = 0.0     #y-component "    "     "     "  "   "
        self.jump = 0.0     #added y-component when rider pulls up off a ramp
        self.pump = 0.0     #pedaling (pumping) power
        self.turn = 0.0     #turning speed

class ColorType(object):
    def __init__(self):
        # TODO replace .r, .g, and .b with tuples? Figure out how to use @property, to allow you to set individual items of the tuple, using .r, .g, .b?
        self.r = 0.0
        self.g = 0.0
        self.b = 0.0

class PointLineObj(object):
    def __init__(self):
        self.position = Point3D()
        self.points = []
        self.lines = []     # Store points maybe as list objects
        # TODO each PointLineObj should have either rotation matrices, or quaternions (straight-up orientations)

    def addPoint(point):
        """ Take in a Point3D object. Append the point object to self.points """
        # TODO maybe make it possible to clear the points list?
        self.points.append(point)

    def addLine(line):
        """ Take in a LineType object. Append the line object to self.lines """
        self.lines.append(line)
        

class Bike(PointLineObj):
    def __init__(self):
        ## TODO pick up from here
        self.frame = PointLineObj()         # A bike contains a frame
        self.handlebars = PointLineObj()    # A bike also contains handlebars
        self.colors = []    # a list of ColorType objects, f.k.a. BikeCol (to be set by InitBike())
        self.style = 0      # TODO: consider replacing with a BikeStyle object (right now, style is an int, which dictates which of a predefined set of styles the bike could have)
        self.scale = 1.0

class BikeStyle(object):
    def __init__(self):
        spokeColor = ColorType()        # BikeCol(4)
        tireColor = ColorType()         # BikeCol(2)
        frameColor = ColorType()        # BikeCol(1) ?? TODO: verify frame color
        barColor = ColorType()          # BikeCol(2) ?? TODO: verify handlebar color


CONST StandardY = 315
CONST Factor = .25
CONST FinalLevel = 6
CONST MaxPts = 150


# NOTE: DIM SHARED shares variable values with sub-procedures without passing the value in a parameter.

## Vars related to rendering the logo at intro time (TODO put into class)
DIM SHARED InPts(1 TO MaxPts) AS Point3D, OutPts(1 TO MaxPts) AS Point3D            # Global arrays. InPts is input to Rotate funcs. It appears to be used only for the logos in the Intro
DIM SHARED Pts2D(1 TO MaxPts) AS Point2D                                            # Array that stores computed projections of points. InPts and OutPts are in 3D; Pts2D is the projection of OutPts onto the screen surface
DIM SHARED Lines(1 TO MaxPts * 3) AS LineType                                       # Lines is an array that holds the line data for the logo.
DIM SHARED NumPts, NumLines

DIM SHARED XPD(1 TO MaxPts) AS Point2D, XPDLine(1 TO MaxPts) AS LineType            # Points and such for XPD logo

## Vars related to rendering bike
DIM SHARED FrameInPts(1 TO MaxPts) AS Point3D, BarInPts(1 TO MaxPts) AS Point3D
DIM SHARED FrameOutPts(1 TO MaxPts) AS Point3D, BarOutPts(1 TO MaxPts) AS Point3D
DIM SHARED BikePts2D(1 TO MaxPts) AS Point2D, BarPts2D(1 TO MaxPts) AS Point2D
DIM SHARED BikeLine(1 TO MaxPts) AS LineType, BarLine(1 TO MaxPts) AS LineType
DIM SHARED NumPtsF, NumLinesF, NumPtsH, NumLinesH
DIM SHARED x, y, z, Txf, Tyf, Tzf, Txh, Tyh, Tzh                                    # Replace x,y,z with bike.position; and Tx,Ty,Tz with something.. matrices or quats
  #T(n)f is the angle (theta) on the n axis of the frame
  #T(n)h is the angle on the n axis of the handlbars (used for bar tricks)
  #x, y, and z are the bike's coordinates
DIM SHARED BikeCol(1 TO 4), BikeStyle, Scale, Level, LevelFinished

## Vars related to level
DIM SHARED Ramp(1 TO 20) AS RampType
DIM SHARED NumRamps, CurRamp, InAir, Tricking, Trick, MemAngle, TrickPhase, Crash
DIM SHARED MsgFrames, msg, LocateRow, NumTricks
DIM SHARED TotNumTricks, TimesUsed(1 TO 20), Worth(1 TO 20)

## Vars related to game state/engine
DIM SHARED Paused, Quit
DIM SHARED FPS, FPStimerA, FPStimerB

## Vars related to player
DIM SHARED Biker AS RiderType, Score, AddScore, RiderName$, MaxBikes
DIM SHARED q AS STRING * 1: q = CHR$(34)

## Vars related to level
DIM SHARED ScoreToBeat(1 TO FinalLevel)
DIM SHARED RunReport$(1 TO 20), TrickCounter
DIM SHARED lx, ly, lz, lScale
DIM SHARED DrawPoints, Track3D, CrowdOn, DoRunSummary, VSync, SloMo


# NOTE: This is where the script starts in QBASIC. This is technically pre-game init stuff. It should go into an init function
FPS = 0

MaxBikes = 11

DIM SHARED NumTrophies(1 TO 13)

# TODO convert to file i/o
# TODO also, watch out for QBASIC 1-based stuff.. you were an amateur when you made this
RESTORE ScoresToBeat
for n = 1 TO FinalLevel
    READ ScoreToBeat(n)  # TODO move ScoreToBeat into the level manager
NEXT n
 
CALL Intro


#=-=-=-=-=-=-=-=-=
#Default Options
#=-=-=-=-=-=-=-=-=
Track3D = -1
DrawPoints = 0
DoRunSummary = -1
CrowdOn = 0
VSync = 0
SloMo = 0
#=-=-=-=-=-=-=-=-=

Menu:
## convert file i/o to Python
## NOTE: You did some hackage to compute a # of trophies won, using 'extended' ascii characters ( > 128)
## THe problem is: back in the day, QBASIC used an encoding called cp437 (a.k.a. DOS United States).
## Nowadays, a more common encoding is a different one: UTF-8. We'll need to re-work the i/o here
#OPEN "trophies.dat" FOR INPUT AS #1
#    FOR n = 1 TO 13
#        INPUT #1, Temp$
#        NumTrophies(n) = VAL(CHR$(ASC(Temp$) - 128))
#    NEXT n
#CLOSE

## TODO un-hardcode the initialization here, and make file i/o
for i in range(0, 14):
    NumTrophies[i] = 0


#=-=-=-=-=-=-=-=-=
#Check to see if player has gotten secret biker #1
#=-=-=-=-=-=-=-=-=
StopFlag = False
for n in range(1, 11 + 1):    #TODO: don't hardcode. Research your code - why 1 - 11?
    if NumTrophies(n) < 1:
        StopFlag = True
        break
if not StopFlag:
    MaxBikes = 12

#=-=-=-=-=-=-=-=-=

#=-=-=-=-=-=-=-=-=
#Check to see if player has gotten secret biker #2
#=-=-=-=-=-=-=-=-=
StopFlag = False
for n = range(1, 12 + 1):       # Counts 1 to 12. TODO: don't hardcode. Research your code - why 1 - 12?
    if NumTrophies(n) < 2:
        StopFlag = True
        break
if not StopFlag:
    MaxBikes = 13
#=-=-=-=-=-=-=-=-=


SCREEN Mode, 0, 1, 0:   # TODO remove (i.e. replace video stuff with pygame video init

InitBike()

# NOTE: MainMenu is the main menu. Once the main menu exits, the game begins. In QBASIC, you had put the entire game at level 0 (i.e., it's not in a function or anything).
# TODO: Put game play into a game loop
MainMenu()
CLS                     # TODO remove

Level = 1
InitBike()
InitLevel(Level)

CONST AnnounceFrames = 25 # TODO replace with a timer (see Falldown x64. In QBASIC, We used to be able to rely on VSYNC, so we could specify a number of frames to wait, to use as a timer. Nowadays, it's better to use a timer
LocateRow = 12  # TODO replace/remove. LOCATE is a qbasic-only thing

msg = "Level " + LTRIM$(STR$(Level))           # TODO make Msg a local var (it's currently global)
message LocateRow, msg, INT(AnnounceFrames)    # TODO replace these message calls with the messaging system from Falldown x64

# TODO: Convert TIMER to pygame get_ticks() or whatever (or some other high-res timer)
FPStimerA = INT(TIMER)      # TODO replace FPStimerA and B with pygame.time.get_ticks() calls
FPStimerB = FPStimerA + 1

prev_time = pygame.time.get_ticks()


DO      # TODO pythonize. This is where the game loop starts. Perhaps it should be the PlayingState

    curr_time = pygame.time.get_ticks()
	dt_s = (curr_time - prev_time) / 1000.0
	prev_time = curr_time

    if Crash:					# TODO put Crash into game vital stats
        InitBike()
        InitLevel(Level)
    
    if LevelFinished:		# TODO make LevelFinished a vital stat
        InitBike()
        Level = Level + 1
    
        if Level > FinalLevel:
            message 12, STRING$(80, " "), 1
            message 12, "GAME OVER - Press <Enter> to return to main menu.", 1
         
            if NumTrophies(BikeStyle) < 2:	# NOTE: here, BikeStyle operates like "SelectedRider"
				# write trophy data to file
                NumTrophies(BikeStyle) = NumTrophies(BikeStyle) + 1
    
                message 13, "Congratulations, you got a trophy!!!", 1
                OPEN "trophies.dat" FOR OUTPUT AS #1    # TODO pythonize file output
                    FOR n = 1 TO 13
                        PRINT #1, CHR$(ASC(LTRIM$(STR$(NumTrophies(n)))) + 128)
                    NEXT n
                CLOSE
         
            DrawLevel()
			DrawBike()
            #doMessage LocateRow, msg, 1
            PCOPY 1, 0: CLS                 # TODO: port pcopy/cls to pygame
            WHILE INKEY$ <> CHR$(13): WEND  # TODO pythonize
            GOTO Menu                       # TODO get rid of Goto. Here, we should be returning from the game play function to the main menu

        InitLevel(Level)
        msg = "Level " + LTRIM$(STR$(Level))
        message LocateRow, msg, INT(AnnounceFrames)
    
    
    if Quit:            # TODO Pythonize bool - Quit should be accessible to the engine
        Quit = False
        GOTO Menu       # TODO get rid of Goto. Return from func, or change state, or whatever
    
    
    DoControls()
    if Tricking:
        DoTrick(Trick)
    CALL RotateBike(Txf, Tyf + 180, Tzf)
    CALL RotateBar(Txh, Tyh + 180, Tzh)
    
    doMessage LocateRow, msg, MsgFrames
    
    Move  #Animate
    CALL CheckRamp(CurRamp)
    
    #if FPS >= 10:   #try to speed things up on slower computers
    DrawLevel()
    DrawBike()
    DrawStatus()    # TODO: status can be an overlay on the game window
    PCOPY 1, 0: CLS
    #END IF
    
    AutoDecel()     # TODO replace AutoDecel hackery with proper physics
    
LOOP        # TODO pythonize. This is where the game loop ends




## TODO Fix a bunch of global vars. Basically, this entire game was made using global vars in QB. Some of those will need to be converted to members of classes. Others may need to be local vars within functions

## Also, port QBASIC syntax to Python

#==============================================================================
#SUB AutoDecel
#This sub handles rolling friction
#The Physics handler will subsume this sub.
#==============================================================================
#TODO: this should be a member function of a bike class. Or otherwise, should be a part of a physics class that operates on bike objects
def AutoDecel():
# TODO add params to this function. In the QBASIC version, you made all vars global. Terrible design :-D
    if not InAir:       # InAir should be part of the bike object (also TODO: make a bike object :-D)
        Biker.xvel = Biker.xvel - .075
        if Biker.xvel <= 0:
            Biker.xvel = 0


#==============================================================================
#FUNCTION getBeatLevelMsg()
#This function returns a random beat-the-level phrase
#==============================================================================
def getBeatLevelMsg(successPhrases):
    i = int( random.random() * len(successPhrases) ) + 1
    return successPhrases[i]

#==============================================================================
#SUB CheckRamp (n)
#Rudimentary collision detection -- test whether the bike has hit a ramp
#==============================================================================
def CheckRamp(n):
    if InAir:   # TODO: InAir should belong to the bike object
        return

    # TODO List of Ramp objects should belong to the Level object (also TODO: make a Level object :-D)
    ex = Ramp(n).x + Ramp(n).length * coss(360 - Ramp(n).incline)
    ey = Ramp(n).y + Ramp(n).length * sinn(360 - Ramp(n).incline)

    if Ramp(n).x <= BarPts2D(5).x:  # TODO don't hardcode points.. Use references
        Tzf = 360 - Ramp(n).incline # TODO compose rotation matrices. i.e. the bike as a whole will have its own rotation matrix; then, the handlebars will have a matrix, and so will the frame. (And also tires, eventually)
        Tzh = Tzf

        Biker.yvel = Biker.jump * (Biker.xvel * sinn(Tzf)) + 2.25    #1.5707 # TODO do better math than this. You came up with these numbers just through trial and error.. what looked good
        Biker.xvel = Biker.xvel * coss(Tzf)

        y = ey - 18 # TODO: Fix. Don't hardcode bike's y-position when jumping. Use collision detection, or otherwise math formulas to determine the bike's position on the ramp

        InAir = True

#==============================================================================
#FUNCTION coss (x)
#Returns the cosine of x, where x is an angle in degrees
#==============================================================================
def coss(x):
    val = math.cos(toRad(x))
    if abs(val) < 0.00001:
        val = 0.0
    return val


#==============================================================================
#FUNCTION getCrashedMsg
#Returns a random crash phrase
#==============================================================================
def getCrashedMsg():
    # TODO: Perhaps crashPhrases should belong to the game object
    p = int(random.random() * len(crashPhrases)) + 1
    return crashPhrases[p]


#==============================================================================
#SUB Creditz
#Displays the credits.  Spelled with a z.  Because that's how we roll.
#==============================================================================
def Creditz:
# TODO: Make Creditz a game state (note that I did not convert it to a function ()). Then, main game can Transition into game state and whatever.

    lx = 80
    ly = 175
    lz = -60
    lScale = 80
    max = 0
    flag = 1    # TODO find out what flag is :-D
    
    RESTORE CreditzData         # Replace restore/read with either file i/o or otherwise hardcoded lists
    READ NumPages
    
    DIM NumLinesPerPage(1 TO NumPages)
    
    FOR n = 1 TO NumPages
        READ NumLinesPerPage(n)
        if NumLinesPerPage(n) > max:
            max = NumLinesPerPage(n)
    NEXT n
    
    DIM Page$(1 TO NumPages, 1 TO max)
    
    FOR n = 1 TO NumPages
        FOR nn = 1 TO NumLinesPerPage(n)
            READ Page$(n, nn)
        NEXT nn
    NEXT n
    
    XPDScale = 2: inc = .5
    
    DO  # TODO replace do/loop with while loop
        XPDx = 560
        XPDy = 225
        
        if XPDScale > 4 OR XPDScale < 2:
            inc = -inc
        
        XPDScale = XPDScale + inc
        
        
        RESTORE XPDData
        READ NumPt
        FOR n = 1 TO NumPt
            READ XPD(n).x, XPD(n).y
        
            XPD(n).x = (XPDScale * XPD(n).x) + XPDx
            XPD(n).y = (XPDScale * (2 - XPD(n).y)) + XPDy
        NEXT n
        
        RESTORE XPDLineData
        READ NumLn
        FOR n = 1 TO NumLn
            READ XPDLine(n).StartPt, XPDLine(n).EndPt
        NEXT n
        
        FOR n = 1 TO NumLn
            PtAx = XPD(XPDLine(n).StartPt).x
            PtAy = XPD(XPDLine(n).StartPt).y
            PtBx = XPD(XPDLine(n).EndPt).x
            PtBy = XPD(XPDLine(n).EndPt).y
        
            LINE (PtAx, PtAy)-(PtBx, PtBy), 15
        NEXT n
        
        #FOR n = 1 TO NumPts
        #    CIRCLE (XPD(n).x, XPD(n).y), 1, 11
        #NEXT n
        
        ty = ty + 15 MOD 360
        
        message 1, STRING$(80, "-"), 1
        message 2, "Trick Biker - Creditz", 1
        message 3, STRING$(80, "-"), 1
        
        LRow = 12 - INT(NumLinesPerPage(flag) / 2)
        
        LOCATE LRow, 1
        
        FOR n = 0 TO NumLinesPerPage(flag) - 1
            if n = 0:
                COLOR 14
            else:
                COLOR 15
            message LRow + n, Page$(flag, n + 1), 1
        NEXT n
        
        #message 21, "Copyright (C) 2000 by Lou Herard for " + q + "Who's The MAN?" + q + " Software.", 1
        message 5, "<J> and <L> scroll, <Esc> exits", 1
        message 23, "Copyright (C) '2K by Lou Herard for Y2K Compliant Software", 1
        
        DrawBike
        CALL Rotate(0, ty, 0)
        RenderLogo
        
        PCOPY 1, 0  # replace with pygame flip-buffers or whatever
        CLS
        
        ## TODO: Convert SELECT CASE statements to if/elif/else blocks. Python does not have switch/select
        a$ = INKEY$
        SELECT CASE UCASE$(a$)
        CASE "J"
            flag = flag - 1
            if flag < 1:
                flag = NumPages
        CASE "L"
            flag = flag + 1
            if flag > NumPages:
                flag = 1
        CASE CHR$(27)
            EXIT SUB
        END SELECT
        
        
        LOOP
END SUB



#==============================================================================
#FUNCTION getDidNotClearJumpMsg
#Returns a random phrase to describe you not clearing the jump (this is rare,
#but it could happen)
#==============================================================================
def getDidNotClearJumpMsg():
    p = int(random.random() * len(rampCrashPhrases)) + 1
    return rampCrashPhrases[p]


#==============================================================================
#SUB DoControls
#Handle keyboard input
#==============================================================================
def DoControls:
    # This will be the input handling function of the playing game state
    # TODO pygame-ize this
    a$ = INKEY$
    
    SELECT CASE a$
    CASE "l", "L"
        if InAir = 0:
            Biker.xvel = Biker.xvel + Biker.pump
            if Biker.xvel >= Biker.maxspd:
                Biker.xvel = Biker.maxspd
     
    CASE "j"
        if InAir AND not Tricking:
            Trick = 1
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "J"
        if InAir AND not Tricking:
            Trick = 2
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "k"
        if InAir AND not Tricking:
            Trick = 3
            Tricking = -1
            MemAngle = Tyh
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "K"
        if InAir AND not Tricking:
            Trick = 4
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
        CASE "i"
        if InAir AND not Tricking:
            Trick = 5
            Tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "I"
        if InAir AND not Tricking:
            Trick = 16
            Tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "u"
        if InAir AND not Tricking:
            Trick = 7
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "U"
        if InAir AND not Tricking:
            Trick = 9
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "o"
        if InAir AND not Tricking: 
            Trick = 8
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
     
    CASE "O"
        if InAir AND not Tricking:
            Trick = 10
            Tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "h"
        if InAir AND not Tricking:
            Trick = 11
            Tricking = -1
            NumTricks = NumTricks + 1
            MemAngle = Tzf
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "H"
        if InAir AND not Tricking:
            Trick = 12
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "y"
        if InAir AND not Tricking:
            Trick = 13
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
            MemAngle = Tzf
        END IF
    
    CASE "Y"
        if InAir AND not Tricking:
            Trick = 14
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
            MemAngle = Tzf
        END IF
    
    CASE "n"
        if InAir AND not Tricking:
            MemAngle = Tzf
            Trick = 15
            Tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "N"
        if InAir AND not Tricking:
            Trick = 6
            Tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    
    #Lean back
    CASE "q"
        if InAir AND not Tricking:
            Tzf = Tzf - Biker.turn / 2
            Tzh = Tzh - Biker.turn / 2
    
    #Lean forward
    CASE "w"
        if InAir AND not Tricking:
            Tzf = Tzf + Biker.turn / 2
            Tzh = Tzh + Biker.turn / 2
    
    CASE "p", "P"
    if Paused = 0:
        doMessage LocateRow, msg, MsgFrames
        s$ = "-=* PHAT FREEZE FRAME SNAPSHOT *=-"
        LOCATE 6, 41 - LEN(s$) / 2: PRINT s$
        DrawLevel
        DrawBike
        DrawStatus
        PCOPY 1, 0: CLS
        Paused = -1
        WHILE INKEY$ = "": WEND
        Paused = 0
    END IF
         
    
    CASE CHR$(27)
        Quit = True
        EXIT SUB
    
    END SELECT


#==============================================================================
#SUB MainMenu
#This is a misnomer--it's actually the game's main menu
#==============================================================================
def MainMenu()      #Also the Game Menu:
ComeHere:
    # Select a random bike style for the main menu demo
    style = int(random.random() * 10) + 1
    RESTORE BikeColorData       # TODO make into a python list
    FOR n = 1 TO style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    
    flag = 1                    # TODO possibly rename flag. It is actually the selected menu item
    Scale = 175
    
    Txf = 0: Tyf = 0: Tzf = 0
    Txh = 0: Tyh = 0: Tzh = 0
    
    DO  # TODO I guess change this into a while True loop?
        for demo in range(0, 7):
            x = 440     # NOTE: x, and y are global vars meant to hold the bike position. Replace with properties of the Bike class
            y = 200
            yi = -20    # yi is a y-pos increment (this approximates gravity) TODO: replace with physics-based gravity
            for ang in range(0, 360 + 1, 15):
                x = x - 11
                y = y + yi: yi = yi + 1.6
                
                if demo == 0:           #Corkscrew (like anyone can really do this)
                    Txf = ang
                    Txh = ang
                elif demo == 1:         #Horizontal 360
                    Tyf = ang
                    Tyh = ang
                elif demo == 2:         #Flip
                    Tzf = ang
                    Tzh = ang
                elif demo == 3:         #Flair
                    Txf = ang
                    Tyf = ang
                    Txh = ang
                    Tyh = ang
                elif demo == 4:         #Tailwhip
                    Tyf = ang
                elif demo == 5:         #BarSpin
                    Tyh = 2 * ang
                elif demo == 6:         #Tabletop
                    if ang <= 90:
                        Txf = ang
                        Txh = ang
                    if ang >= 270:
                        Txf = 360 - ang
                        Txh = 360 - ang
                
                #PRINT "Cycle: "; demo
                
                
                #==================
                #     Do Game Menu
                #==================
                # TODO replace with a pygame menu -- use your menu class from falldown x64
                message 1, STRING$(80, "-"), 1
                message 2, "Trick Biker!!!", 1
                message 3, STRING$(80, "-"), 1
                message 4, "<I> and <K> navigate this menu, <Esc> quits.", 1
                message 6, "Instructions", 1
                message 10, "Start Game", 1
                message 14, "Options", 1
                message 18, "Creditz", 1
                message 20, STRING$(80, "-"), 1
                message 21, "By Lou Herard - (C) 2000 by Y2K Compliant Software", 1
                message 22, STRING$(80, "-"), 1
                
                flagY = (flag * 4 * 14) + 14
                LINE (200, flagY)-(440, flagY + 14), 4, B
                
                a$ = INKEY$
                SELECT CASE UCASE$(a$)
                    CASE "K"
                        flag = flag + 1
                        if flag > 4:
                            flag = 1
                    CASE "I"
                        flag = flag - 1
                        if flag < 1:
                            flag = 4
                    CASE CHR$(27)
                        END
                    CASE CHR$(13)
                        SELECT CASE flag
                            CASE 1
                                CALL Instructions
                                CLS
                            CASE 2
                                CALL SelectBike
                                if Quit:
                                    Quit = False
                                    CLS
                                    GOTO ComeHere
                                END IF
                                EXIT SUB
                            CASE 3
                                CALL OptionsMenu
                                CLS
                            CASE 4
                                CALL Creditz
                                CLS
                        END SELECT
                END SELECT
                
                #-------
                #Rotate and Translate Points
                #-------
                
                CALL RotateBike(Txf, Tyf, Tzf)
                CALL RotateBar(Txh, Tyh, Tzh)
                DrawBike
                
                
                PCOPY 1, 0: CLS         ## TODO: replace PCOPY calls with pygame buffer swap calls
                if VSync:
                    WAIT &H3DA, 8       ## TODO get rid of WAIT. It is a QBASIC-specific thing
                
        NEXT demo
    LOOP
END SUB


#==============================================================================
#SUB doMessage (row, Text$, frames)
#Displays a message on the screen
#==============================================================================
def doMessage(row, Text$, frames):
    # TODO replace with the messaging system you created for falldown
    if MsgFrames <= 0:
        msg = "": EXIT SUB
    MsgFrames = MsgFrames - 1
    LOCATE row, 41 - LEN(Text$) / 2
    PRINT Text$



#==============================================================================
#SUB DoTrick (n)
#Execute tricks
#==============================================================================
def DoTrick(n):
    SELECT CASE n
        CASE 1                #360 degree turn
            Tyh = Tyh + (Biker.turn * 1) / 1.5
            Tyf = Tyf + (Biker.turn * 1) / 1.5
            Tzf = Tzf + 1
            Tzh = Tzh + 1
            if Tyf MOD 360 = 0:
                Tricking = 0
                msg = "360 Turn!!!"
            END IF
    
        CASE 2                #Tailwhip
            Tyf = Tyf + Biker.turn
            Tzf = Tzf + 1
            Tzh = Tzh + 1
            if Tyf MOD 360 = 0:
                Tricking = 0
                msg = "Tailwhip!!!"
            END IF
    
        CASE 3                #180 degree barturn
            if TrickPhase = 1:
                Tyh = Tyh + Biker.turn
            if TrickPhase = 6:
                Tyh = Tyh - Biker.turn
         
            Tzf = Tzf + 1
            Tzh = Tzh + 1
         
            if Tyh MOD 90 = 0:
                TrickPhase = TrickPhase + 1
            if Tyh = MemAngle:
                Tricking = 0
                MemAngle = 0
                TrickPhase = 1
                msg = "X-Up!!!"
            END IF
    
        CASE 4                #360 degree barspin
            Tyh = Tyh + Biker.turn
            if Tyh MOD 360 = 0:
                Tricking = 0
                msg = "Barspin!!!"
            END IF
            Tzf = Tzf + 1
            Tzh = Tzh + 1
    
        CASE 5                #Backflip
            tfactor = 5 / 2
            Tzf = Tzf - Biker.turn / tfactor
            Tzh = Tzh - Biker.turn / tfactor
            if Tzf <= MemAngle - 330:
                Tricking = 0
                MemAngle = 0
                msg = "Backflip!!!"
            END IF
    
        CASE 6                #Inverted 180
            tfactor = 5 / 2 #either 2 or 5/2
            Txf = Txf + Biker.turn / tfactor
            Txh = Txh + Biker.turn / tfactor

            Tyf = Tyf + Biker.turn / tfactor
            Tyh = Tyh + Biker.turn / tfactor

            Tzf = Tzf + 2
            Tzh = Tzh + 2

            if Txf MOD 360 = 0 :
                Tricking = 0
                msg = "Inverted 180!!!"
            END IF
    
        CASE 7            #Corkscrew (don't try this at home)
            Txf = Txf + Biker.turn / 2
            Txh = Txh + Biker.turn / 2
            Tzf = Tzf + 1: Tzh = Tzh + 1
    
            if Txf MOD 360 = 0:
                Tricking = 0
                msg = "Corkscrew!!!"
            END IF
    
        CASE 8            #Double Barspin Tailwhip
            Tyf = Tyf - Biker.turn
            Tyh = Tyh + Biker.turn * 2
            Tzf = Tzf + 1
            Tzh = Tzh + 1
    
            if Tyf MOD 360 = 0:
                Tricking = 0
                msg = "Double Barspin/Tailwhip!!!"
            END IF
        
        CASE 9            #Wicked Tabletop
            if TrickPhase = 1:
                Txf = Txf + Biker.turn / 2
                Txh = Txh + Biker.turn / 2
            END IF
            if TrickPhase = 5:
                Txf = Txf - Biker.turn / 2
                Txh = Txh - Biker.turn / 2
            END IF
         
            Tzf = Tzf + 2
            Tzh = Tzh + 2
         
            if Txf MOD 90 = 0:
                TrickPhase = TrickPhase + 1
            if Txf MOD 360 = 0:
                Tricking = 0
                TrickPhase = 1
                msg = "Tabletop!!!"
            END IF
    
        CASE 10         #Twisting Corkscrew
            tfactor = 5 / 2
                Tzf = Tzf - Biker.turn / tfactor
                Tzh = Tzh - Biker.turn / tfactor
                Txf = Txf - Biker.turn / tfactor
                Txh = Txh - Biker.turn / tfactor
                     
            if Tzf <= MemAngle - 330 :
                Txf = 0: Txh = 0
                Tricking = 0
                MemAngle = 0
                TrickPhase = 1
                msg = "Twisting Corkscrew!!!"
            END IF
    
            CASE 11             #Backflip Tailwhip
                if TrickPhase = 1 OR TrickPhase = 2 OR TrickPhase = 3:
                    Tzf = Tzf - Biker.turn * (1 / 3)
                    Tzh = Tzh - Biker.turn * (1 / 3)
                END IF
    
                if TrickPhase = 1 AND Tzf <= MemAngle - 90:
                    TrickPhase = 2
    
                if TrickPhase = 2:
                    Tyf = Tyf + Biker.turn / (3 / 2)
                END IF
    
                if TrickPhase = 2 AND Tyf MOD 360 = 0:
                    TrickPhase = 3
    
                if Tzf <= MemAngle - 330:
                    Tricking = 0
                    MemAngle = 0
                    TrickPhase = 1
                    msg = "Backflip Tailwhip!!!"
                END IF
         
            CASE 12                     #360 turn + 360 barspin
            Tzf = Tzf + 1
            Tzh = Tzh + 1
                if TrickPhase = 1:
                    Tyf = Tyf + Biker.turn / 2
                    Tyh = Tyh + Biker.turn / 2
                END IF
                if TrickPhase = 2:
                    Tyh = Tyh - Biker.turn
                END IF
                if TrickPhase = 3: 
                    Tyf = Tyf + Biker.turn / 2
                    Tyh = Tyh - Biker.turn
                END IF
    
                if TrickPhase = 1 AND Tyf MOD 180 = 0:
                    TrickPhase = 2
                if TrickPhase = 2 AND Tyh MOD 360 = 0:
                    TrickPhase = 3
                if TrickPhase = 3 AND Tyf MOD 360 = 0:
                    Tricking = 0
                    TrickPhase = 1
                    msg = "360 Turn + Barspin!!!"
                END IF
    
            CASE 13                         #Air Endo
                if TrickPhase = 1:
                    Tzf = Tzf + Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
                if TrickPhase > 4:
                    Tzf = Tzf - Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
    
                if Tzf >= MemAngle + 60:
                    TrickPhase = TrickPhase + 1
                if TrickPhase > 4 AND Tzf <= MemAngle + 30:
                    Tricking = 0
                    TrickPhase = 1
                    MemAngle = 0
                    msg = "Air Endo!!!"
                END IF
    
            CASE 14                         #Air Endo plus bar twist
                if TrickPhase = 1:
                    Tzf = Tzf + Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
             
                if TrickPhase = 1 AND Tzf >= MemAngle + 60:
                    TrickPhase = 2
                if TrickPhase = 3 AND Tyh MOD 360 = 0:
                    TrickPhase = 4
    
                if TrickPhase = 2:
                    Tyh = Tyh - Biker.turn / 2
                END IF
            
                if (TrickPhase = 2 OR TrickPhase = 3) AND Tyh MOD 180 = 0:
                    TrickPhase = TrickPhase + 1
    
                if TrickPhase = 3:
                    Tyh = Tyh + Biker.turn / 2
                END IF
    
                if TrickPhase = 4:
                    Tzf = Tzf - Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
         
                
                if TrickPhase = 4 AND Tzf <= MemAngle + 30:
                    Tricking = 0
                    TrickPhase = 1
                    MemAngle = 0
                    msg = "Air Endo + Bar Twist!!!"
                END IF
    
            CASE 15                 #Turndown
                if TrickPhase = 1:
                    Tyf = Tyf - Biker.turn * (1 / 2)
                    Tzf = Tzf + Biker.turn * (1 / 2)
                    Tzh = Tzh + Biker.turn * (1 / 2)
                END IF
                
                if Tyf MOD 90 = 0:
                    TrickPhase = TrickPhase + 1
    
                if TrickPhase = 6:
                    Tyf = Tyf + Biker.turn * (1 / 2)
                    Tzf = Tzf - Biker.turn * (1 / 2)
                    Tzh = Tzh - Biker.turn * (1 / 2)
                END IF
    
                if TrickPhase = 6 AND Tyf MOD 360 = 0:
                    Tzf = Tzf + 30
                    Tzh = Tzf
                    TrickPhase = 1
                    Tricking = 0
                    msg = "Turndown!!!"
                END IF
    
                #Tzf = 80: Txf = 0
                #Tyh = 0: Tzh = Tzf: Txh = 0
    
            CASE 16             #Flair
                if TrickPhase = 1: #OR TrickPhase = 3
                    Tzf = Tzf - (Biker.turn * .4)
                    Tzh = Tzh - (Biker.turn * .4)
                END IF
    
                if TrickPhase = 3:
                    Tzf = Tzf - (Biker.turn * .5)
                    Tzh = Tzh - (Biker.turn * .5)
                END IF
    
                if TrickPhase = 1 AND Tzf <= MemAngle - 135:
                    TrickPhase = 2
    
                if TrickPhase = 2:
                    Tzf = Tzf - (Biker.turn * .25)
                    Tzh = Tzh - (Biker.turn * .25)
    
                    Tyf = Tyf + (Biker.turn * .5)
                    Tyh = Tyh + (Biker.turn * .5)
                END IF
    
                if TrickPhase = 2 AND Tyf MOD 360 = 0:
                    TrickPhase = 3
    
                if TrickPhase = 3 AND Tzf <= MemAngle - 330:
                    Tricking = 0
                    TrickPhase = 1
                    MemAngle = 0
                    msg = "Flair!!!"
                END IF
    
    
    END SELECT
    
     
    
        if Tricking = 0 :
                AddScore = INT(AddScore + Worth(Trick) - ((Factor * TimesUsed(Trick)) * Worth(Trick)))
                if AddScore <= 0:
                    AddScore = 1
                TimesUsed(Trick) = TimesUsed(Trick) + 1
                msg = msg + " - " + LTRIM$(STR$(AddScore)) + " pts. "
                if NumTricks > 1:
                    msg = msg + " " + LTRIM$(STR$(NumTricks)) + " TRICK COMBO!!!"
                RunReport$(TrickCounter) = msg
                message LocateRow, msg, AnnounceFrames
        END IF
    
    if SloMo:
        FOR l = 1 TO 50
            WAIT &H3DA, 8
        NEXT l
    END IF
    
    
    
    
#==============================================================================
#SUB DrawBike
#Draw the bike
#==============================================================================
def DrawBike:
    
    #------
    #Draw Lines
    #------
    FOR n = 1 TO NumLinesF
        #col = 5
        SELECT CASE n
            CASE 1 TO 4     #=-=-= Spoke Color. This can be changed. =-=-=
                col = BikeCol(4)
     
            CASE 5 TO 24, 41 TO 45
                col = 8
    
            CASE 25 TO 33
                col = BikeCol(1)
    
            CASE else:
                col = BikeCol(2)#8             #=-=-= Tire Color.    Don't change this =-=-=
        END SELECT
    
    
        LINE (BikePts2D(BikeLine(n).StartPt).x, BikePts2D(BikeLine(n).StartPt).y)-(BikePts2D(BikeLine(n).EndPt).x, BikePts2D(BikeLine(n).EndPt).y), col
    NEXT n
    
    FOR n = 1 TO NumLinesH
        SELECT CASE n
            CASE 1 TO 4
                col = BikeCol(3)
            CASE 5 TO 24
                col = 8
            CASE 25 TO 30
                col = BikeCol(1)
            CASE 31 TO 38
                col = 8
        END SELECT
    
        LINE (BarPts2D(BarLine(n).StartPt).x, BarPts2D(BarLine(n).StartPt).y)-(BarPts2D(BarLine(n).EndPt).x, BarPts2D(BarLine(n).EndPt).y), col
    NEXT n
    
    if DrawPoints:
        FOR n = 1 TO NumPtsF
            CIRCLE (BikePts2D(n).x, BikePts2D(n).y), 1, 14
        NEXT n
    
        FOR n = 1 TO NumPtsH
            CIRCLE (BarPts2D(n).x, BarPts2D(n).y), 1, 14
        NEXT n
    END IF
    
END SUB


#==============================================================================
#SUB DrawLevel
#
#==============================================================================
def DrawLevel:
    #TODO: Make this function take in a parameter. The parameter should be a Level object. The level should contain a list of ramps, and whatever else
    FOR n = 1 TO NumRamps
        sx = Ramp(n).x
        sy = Ramp(n).y

        ex = Ramp(n).x + Ramp(n).length * coss(360 - Ramp(n).incline)
        ex2 = Ramp(n).x + Ramp(n).length * coss(Ramp(n).incline)
        if n > 1:
            ex22 = Ramp(n - 1).x + os + Ramp(n - 1).dist
            ex22 = ex22 + Ramp(n - 1).length * coss(Ramp(n - 1).incline)
        END IF
        ey = Ramp(n).y + Ramp(n).length * sinn(360 - Ramp(n).incline)

        if Track3D:
            tw = 44         #track width
            os = -5         #3d illusion offset
        else:
            tw = 0
            os = 0
        END IF

        SELECT CASE n
            CASE 1
                #StandardY is a CONST.    Value is 315
                LINE (0, StandardY - 10 - tw)-(Ramp(n).x, StandardY - 10 - tw), 7
                LINE (0, StandardY - 10 + tw)-(Ramp(n).x + os, StandardY - 10 + tw), 7
            CASE else:
                LINE (ex22, StandardY - 10 - tw)-(Ramp(n).x, StandardY - 10 - tw)
                LINE (ex22 + os, StandardY - 10 + tw)-(Ramp(n).x + os, StandardY - 10 + tw)
                    if n = NumRamps:
                        LINE (ex2 + Ramp(n).dist, StandardY - 10 - tw)-(639, StandardY - 10 - tw)
                        LINE (ex2 + Ramp(n).dist, StandardY - 10 + tw)-(639, StandardY - 10 + tw)
                    END IF
        END SELECT

        LINE (sx + os, sy + tw)-(ex + os, ey + tw)
        LINE (sx + os + Ramp(n).dist, ey + tw)-(ex2 + os + Ramp(n).dist, sy + tw)

        LINE (sx, sy - tw)-(ex, ey - tw)
        LINE (sx + Ramp(n).dist, ey - tw)-(ex2 + Ramp(n).dist, sy - tw)

        LINE (sx + os, sy + tw)-(sx, sy - tw)
        LINE (ex + os, ey + tw)-(ex, ey - tw)
        LINE (sx + os + Ramp(n).dist, ey + tw)-(sx + Ramp(n).dist, ey - tw)
        LINE (ex2 + os + Ramp(n).dist, sy + tw)-(ex2 + Ramp(n).dist, sy - tw)

        #PAINT (sx, sy), 6, 15
        #PAINT (ex2 + Ramp(n).dist - 2, ey), 6, 15

        #CIRCLE (sx, sy), 4, 4

    NEXT n
END SUB


#==============================================================================
#SUB DrawStatus
#Display the status/score stuff on the screen
#==============================================================================
def DrawStatus:
    LOCATE 1, 1
    PRINT "Speed"
    
    l = 120
    w = 4
    by = 5
    bx = 50
    
    LINE (bx - 1, by)-(bx + l + 1, by + w), BikeCol(1), B
    LINE (bx, by + 1)-(bx + l * (Biker.xvel / Biker.maxspd), by + w - 1), BikeCol(2), BF
    
    LOCATE 1, 25: PRINT "Score: "; LTRIM$(STR$(Score))
    LOCATE 1, 40: PRINT "Level "; LTRIM$(STR$(Level))
    LOCATE 1, 50: PRINT "Score to beat = "; LTRIM$(STR$(ScoreToBeat(Level))); " pts."
    #LOCATE 2, 1: PRINT FPS
    END SUB

#==============================================================================
#SUB DrawTrophies (NumToDraw, StartX)
#==============================================================================
def DrawTrophies(NumToDraw, StartX):
    StartY = 50
    Tscale = 3
    
    RESTORE TrophyData
    READ NumTPts
    
    DIM Trophy(1 TO NumTPts) AS Point2D
    
    FOR n = 1 TO NumTPts
        READ Trophy(n).x, Trophy(n).y
    NEXT n
    
    FOR n = 1 TO NumTPts
        Trophy(n).x = Tscale * Trophy(n).x
        Trophy(n).y = Tscale * (8 - Trophy(n).y)
    NEXT n
    
    RESTORE TrophyLineData
    READ NumTLns
    
    DIM TrophyLines(1 TO NumTLns) AS LineType
    FOR n = 1 TO NumTLns
        READ TrophyLines(n).StartPt, TrophyLines(n).EndPt
    NEXT n
    
    TInCol = 14
    TOutCol = 6
    
    FOR c = 0 TO (NumToDraw - 1)
    FOR n = 1 TO NumTLns
        PtAx = (Trophy(TrophyLines(n).StartPt).x + StartX + (40 * c))
        PtAy = (Trophy(TrophyLines(n).StartPt).y + StartY)
        PtBx = (Trophy(TrophyLines(n).EndPt).x + StartX + (40 * c))
        PtBy = (Trophy(TrophyLines(n).EndPt).y + StartY)
    
        LINE (PtAx, PtAy)-(PtBx, PtBy), TOutCol
    NEXT n
    
    PAINT (PtAx + 3.5, PtAy), TInCol, TOutCol
    NEXT c
END SUB


#==============================================================================
#SUB InitBike
#==============================================================================
def InitBike:
    #-------
    #Read Points
    #-------
    RESTORE FrameData
    READ NumPtsF
    FOR n = 1 TO 6
        READ FrameInPts(n).x, FrameInPts(n).y, FrameInPts(n).z
    NEXT n

    # TODO remove multiple loads of the bike model. We only need to load once
    exePath = os.path.dirname(sys.argv[0])
    with open( exePath + os.path.normpath("../data/bike_model.json") ) as fd:  # TODO add try/except here
        bikeModel = json.load(fd)
    
    # NOTE: You're an a-hole.. you calculated the wheel points. To properly render the bike, you'll need to change the point/line indices
    Rad = 4.5
    CircPoints = 20
    CenterX = -22
    CenterY = -5
    LeftX = CenterX - Rad
    RightX = CenterX + Rad
    Increment = (RightX - LeftX) / (CircPoints / 2)
    
    # NOTE: Pts 0 - 6 (er, I guess 1 - 6, since I wrote this with base 1), are.. interior frame pts? (diamond)
    FOR n = 7 TO 26     # Rear tire
        SELECT CASE n
           CASE IS <= 7 + (CircPoints / 2)
               FrameInPts(n).x = LeftX + ((n - 7) * Increment)
               FrameInPts(n).y = SQR((Rad ^ 2) - ((FrameInPts(n).x - CenterX) ^ 2)) + CenterY
           CASE IS > 7 + (CircPoints / 2)
               FrameInPts(n).x = RightX - ((n - 17) * Increment)
               FrameInPts(n).y = -SQR((Rad ^ 2) - ((FrameInPts(n).x - CenterX) ^ 2)) + CenterY
        END SELECT

        FrameInPts(n).z = 0
    NEXT n
    
    FOR n = 27 TO NumPtsF   # Rear wheel forks and such
        READ FrameInPts(n).x, FrameInPts(n).y, FrameInPts(n).z
    NEXT n
    
    RESTORE HandleBarData
    READ NumPtsH
    FOR n = 1 TO 2
        READ BarInPts(n).x, BarInPts(n).y, BarInPts(n).z
    NEXT n
    
    CircPoints = 20
    CenterX = 0
    CenterY = -5
    LeftX = CenterX - Rad
    RightX = CenterX + Rad
    Increment = (RightX - LeftX) / (CircPoints / 2)
    
    FOR n = 3 TO 22
        SELECT CASE n
           CASE IS <= 3 + (CircPoints / 2)
               BarInPts(n).x = LeftX + ((n - 3) * Increment)
               BarInPts(n).y = SQR((Rad ^ 2) - ((BarInPts(n).x - CenterX) ^ 2)) + CenterY
           CASE IS > 3 + (CircPoints / 2)
               BarInPts(n).x = RightX - ((n - 13) * Increment)
               BarInPts(n).y = -SQR((Rad ^ 2) - ((BarInPts(n).x - CenterX) ^ 2)) + CenterY
        END SELECT

        BarInPts(n).z = 0
    NEXT n
    
    FOR n = 23 TO NumPtsH
        READ BarInPts(n).x, BarInPts(n).y, BarInPts(n).z
    NEXT n
    
    
    Score = 0
    Paused = 0
    #BikeStyle = 5
    
    RESTORE BikeColorData
    FOR n = 1 TO BikeStyle
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    RESTORE BikerData
    FOR n = 1 TO BikeStyle
        READ Biker.maxspd, Biker.jump, Biker.pump, Biker.turn
    NEXT n
    
    RESTORE FrameLineData
    READ NumLinesF
    FOR n = 1 TO NumLinesF
        READ BikeLine(n).StartPt, BikeLine(n).EndPt
    NEXT n
    
    RESTORE BarLineData
    READ NumLinesH
    FOR n = 1 TO NumLinesH
        READ BarLine(n).StartPt, BarLine(n).EndPt
    NEXT n
    
    RESTORE TrickPointData
    READ TotNumTricks
    FOR n = 1 TO TotNumTricks
        READ Worth(n)
        TimesUsed(n) = 0
    NEXT n
END SUB


#==============================================================================
#SUB InitLevel (lev)
#==============================================================================
def InitLevel(lev):
    # TODO perhaps move levels into text files? Or perhaps into a separate module?

    z = -60        			#z offset: keep this around -50 or -60
    AddScore = 0        	# AddScore appears to be the score? Belongs in a game stats class
    Scale = 120         	# Scale is used in Rotate functions. May need to substitute a camera class?
    LevelFinished = False  	# LevelFinished belongs in a game stats class
    Crash = False       	# Crash is a bool to say whether or not player crashed. Belongs in a game stats class
    CurRamp = 1         	# The current ramp in the level (this probably won't be necessary once we have legit collision detection
    TrickPhase = 1      	# TrickPhase tracks the segment of a multi-phase trick
    NumTricks = 0       	# Tracks how many tricks the player has performed (belongs in game stats class)
    MsgFrames = 0       	# Used in messaging (how many frames to leave the message up for)
    msg = ""           		# Used in messaging - the message text itself
    InAir = 0           	# True if biker is in the air (after a jump)
    Tricking = 0        	# Bool flag -- true if user is currently performing a trick
    TrickCounter = 0    	# Hmm, not sure how this differs from NumTricks. TODO read the code

    x = 120                 # Bike position on screen
    y = StandardY - 20 - 10

    Txf = 0                 # Bike Euler angles
    Txh = 0

    Tyf = 0
    Tyh = 0

    Tzf = 0
    Tzh = 0

    Biker.xvel = 0
    Biker.yvel = 0

    SELECT CASE lev
        CASE 1
            NumRamps = 3

            Ramp(1).x = 600
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 45
            Ramp(1).length = 45
            Ramp(1).dist = 220

            Ramp(2).x = 1400
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 33
            Ramp(2).length = 60
            Ramp(2).dist = 220

            Ramp(3).x = 2200
            Ramp(3).y = StandardY - 10
            Ramp(3).incline = 50
            Ramp(3).length = 30
            Ramp(3).dist = 220

        CASE 2
            NumRamps = 5

            Ramp(1).x = 500
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 30
            Ramp(1).length = 45
            Ramp(1).dist = 200

            Ramp(2).x = 1300
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 40
            Ramp(2).length = 45
            Ramp(2).dist = 250

            Ramp(3).x = 2100
            Ramp(3).y = StandardY - 10
            Ramp(3).incline = 40
            Ramp(3).length = 40
            Ramp(3).dist = 170
    
            Ramp(4).x = 2900
            Ramp(4).y = StandardY - 10
            Ramp(4).incline = 30
            Ramp(4).length = 45
            Ramp(4).dist = 220
            
            Ramp(5).x = 3700
            Ramp(5).y = StandardY - 10
            Ramp(5).incline = 40
            Ramp(5).length = 40
            Ramp(5).dist = 150

        CASE 3
            NumRamps = 4
    
            Ramp(1).x = 540
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 25
            Ramp(1).length = 35
            Ramp(1).dist = 170
     
            Ramp(2).x = 1080
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 35
            Ramp(2).length = 35
            Ramp(2).dist = 170
    
            Ramp(3).x = 1620
            Ramp(3).y = StandardY - 10
            Ramp(3).incline = 45
            Ramp(3).length = 35
            Ramp(3).dist = 190
    
            Ramp(4).x = 2160
            Ramp(4).y = StandardY - 10
            Ramp(4).incline = 50
            Ramp(4).length = 35
            Ramp(4).dist = 210

        CASE 4
            NumRamps = 4
     
            Ramp(1).x = 600
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 45
            Ramp(1).length = 35
            Ramp(1).dist = 200
    
            Ramp(2).x = 1200
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 45
            Ramp(2).length = 35
            Ramp(2).dist = 200
    
            Ramp(3).x = 1800
            Ramp(3).y = StandardY - 10
            Ramp(3).incline = 45
            Ramp(3).length = 35
            Ramp(3).dist = 200
    
            Ramp(4).x = 2400
            Ramp(4).y = StandardY - 10
            Ramp(4).incline = 35
            Ramp(4).length = 35
            Ramp(4).dist = 200

        CASE 5
            NumRamps = 6
    
            Ramp(1).x = 600
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 35
            Ramp(1).length = 35
            Ramp(1).dist = 200
    
            Ramp(2).x = 1200
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 40
            Ramp(2).length = 35
            Ramp(2).dist = 200
    
            Ramp(3).x = 1800
            Ramp(3).y = StandardY - 10
            Ramp(3).incline = 35
            Ramp(3).length = 35
            Ramp(3).dist = 200
    
            Ramp(4).x = 2400
            Ramp(4).y = StandardY - 10
            Ramp(4).incline = 40
            Ramp(4).length = 35
            Ramp(4).dist = 200
    
            Ramp(5).x = 3000
            Ramp(5).y = StandardY - 10
            Ramp(5).incline = 35
            Ramp(5).length = 35
            Ramp(5).dist = 200
    
            Ramp(6).x = 3600
            Ramp(6).y = StandardY - 10
            Ramp(6).incline = 35
            Ramp(6).length = 35
            Ramp(6).dist = 200

        CASE 6
            NumRamps = 2
    
            Ramp(1).x = 600
            Ramp(1).y = StandardY - 10
            Ramp(1).incline = 55
            Ramp(1).length = 35
            Ramp(1).dist = 220
    
            Ramp(2).x = 1200
            Ramp(2).y = StandardY - 10
            Ramp(2).incline = 55
            Ramp(2).length = 35
            Ramp(2).dist = 220

    END SELECT
END SUB

#==============================================================================
#SUB Instructions
#==============================================================================
def Instructions:
    # TODO make this its own gamestate
    RESTORE InstructionsData
    READ Lines
    DIM Text$(1 TO Lines)
    
    FOR n = 1 TO Lines
        READ Text$(n)
    NEXT n
    flag = 1: range = 7     #num of rows of text to print
    
    DO
        CLS
        message 1, STRING$(80, "-"), 1
        message 2, "Trick Biker - Instructions", 1
        message 3, STRING$(80, "-"), 1
        
        
        #range = row 5 to 19
        LOCATE 5
        
        FOR n = flag TO flag + range
            PRINT Text$(n)
            PRINT
        NEXT n
        
        message 21, STRING$(80, "-"), 1
        message 22, "<I and K> scroll, <Esc> quits.", 1
        message 23, STRING$(80, "-"), 1
        
        PCOPY 1, 0
        
        a$ = INKEY$
        
        SELECT CASE UCASE$(a$)
            CASE "I"
                flag = flag - 1
                if flag < 1 : flag = 1
            CASE "K"
                flag = flag + 1
                if flag > Lines - range : flag = Lines - range
            CASE CHR$(27)
                CLS
                EXIT SUB
        END SELECT
        
    LOOP
    
    END SUB

#==============================================================================
#SUB Intro
#==============================================================================
def Intro:
    lScale = 375
    lz = -60
    lx = 320
    ly = 175
    
    #Get the points that are in the logo
    RESTORE LogoData
    READ NumPts
    FOR n = 1 TO NumPts
        READ InPts(n).x, InPts(n).y, InPts(n).z
    NEXT n
    
    #Get the line data that will make the logo
    RESTORE LineData
    READ NumLines
    FOR n = 1 TO NumLines
        READ Lines(n).StartPt, Lines(n).EndPt
    NEXT n
    
    SCREEN Mode, 0, 1, 0
    if Mode <> 9 :
        WINDOW SCREEN (0, 0)-(639, 349)
    END IF
    
    tx = 0: ty = 0: tz = 0
    
    DO
        tx = tx + 6
        ty = ty - 12
        tz = tz + 3
        
        CALL Rotate(tx, ty, tz)
        RenderLogo
        message 23, "A Y2K Compliant Game...", 1
        PCOPY 1, 0: CLS
        
    LOOP WHILE INKEY$ = ""
    
    XPDx = 320: XPDy = 125: XPDScale = 10
    
    RESTORE XPDData
    READ NumPt
    FOR n = 1 TO NumPt
        READ XPD(n).x, XPD(n).y
     
        XPD(n).x = (XPDScale * XPD(n).x) + XPDx
        XPD(n).y = (XPDScale * (4 - XPD(n).y)) + XPDy
    NEXT n
    
    RESTORE XPDLineData
    READ NumLn
    FOR n = 1 TO NumLn
        READ XPDLine(n).StartPt, XPDLine(n).EndPt
    NEXT n
    
    FOR n = 1 TO NumLn
        PtAx = XPD(XPDLine(n).StartPt).x
        PtAy = XPD(XPDLine(n).StartPt).y
        PtBx = XPD(XPDLine(n).EndPt).x
        PtBy = XPD(XPDLine(n).EndPt).y
     
        LINE (PtAx, PtAy)-(PtBx, PtBy), 15
    NEXT n
    
    #FOR n = 1 TO NumPts
    #    CIRCLE (XPD(n).x, XPD(n).y), 1, 1
    #NEXT n
    
    LINE (0, 115)-(639, 125), 15, B
    LINE (0, 205)-(639, 215), 15, B
    
    PAINT (105, 165), 15, 15            #Paint around the X
    PAINT (220, 145), 15, 15
    PAINT (220, 185), 15, 15
    PAINT (245, 165), 15, 15
    
    PAINT (300, 150), 15, 15            #Paint around the P
    PAINT (300, 190), 15, 15
    PAINT (365, 128), 15, 15
    
    PAINT (400, 165), 15, 15            #Paint around the D
    PAINT (500, 165), 15, 15
    
    PAINT (0, 0), 2, 15
    PAINT (0, 349), 2, 15
    
    x = 320: y = 30: z = -60: Scale = 165
    
    Style = 8
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 10, 300, 30
    RotateBar 10, 340, 30
    DrawBike
    
    x = 520: y = 64: z = -60: Scale = 165
    
    Style = 3
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 0, 180, -25
    RotateBar 0, 180, -25
    DrawBike
    
    x = 120: y = 30: z = -60: Scale = 140
    
    Style = 5
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 70, 180, -15
    RotateBar 70, 180, -15
    DrawBike
    
    message 23, "XPDient Software Solutions", 1
    
    PCOPY 1, 0: CLS
    WHILE INKEY$ = "": WEND
    
END SUB

#==============================================================================
#FUNCTION LostLevel$
#==============================================================================
def LostLevel$:
    RESTORE failurePhrases
    READ NumPhrases
    RANDOMIZE TIMER
    p = INT(RND * NumPhrases) + 1
    
    FOR n = 1 TO p
        READ s$
    NEXT n
    
    return s$
    

#==============================================================================
#SUB message (row, Text$, frames)
#==============================================================================
def message(row, Text$, frames):
    MsgFrames = frames
    LOCATE row, 41 - LEN(Text$) / 2
    PRINT Text$
    END SUB

#==============================================================================
#SUB Move
#==============================================================================
def Move:
    FOR n = 1 TO NumRamps
        Ramp(n).x = Ramp(n).x - Biker.xvel
    NEXT n

    xAdd1 = Ramp(CurRamp).x + Ramp(CurRamp).dist
    #CIRCLE (xAdd1, StandardY - 10), 3, 3
  
    if InAir:
        y = y + Biker.yvel
        Biker.yvel = Biker.yvel + 2.1
    
        if not Tricking :
            Tzf = Tzf + 3: Tzh = Tzf
            #if (Tzf - 360) MOD 360 > 10 : message 5, "Lean Back!!!", 1
        END IF
    
        if Biker.yvel > 0 AND (BikePts2D(21).y > StandardY - 25 OR BarPts2D(17).y > StandardY - 25):
            DidNotClearRamp = (BikePts2D(3).x < xAdd1)
    
            y = StandardY - 30
            Biker.yvel = 0
    
            if Tricking OR DidNotClearRamp :
                CLS
                msg = "": MsgFrames = 0
                if Tricking :
                    message 12, getCrashedMsg(), 1
                else:
                    message 12, getDidNotClearJumpMsg(), 1
                END IF
    
                message 14, "Press <Enter> to continue.", 1
                Crash = True
                y = StandardY - 15
    
                if (Tyf + 180) MOD 360 >= 270 AND (Tyf + 180) MOD 360 <= 90 :
                    Tzh = 180: Tzf = 180
                else:
                    Tzh = 0: Tzf = 0
                END IF
            
                Txf = 70: Txh = 70
    
                CALL RotateBike(Txf, Tyf + 180, Tzf)
                CALL RotateBar(Txh, Tyh + 180, Tzh)
                DrawLevel
                DrawBike
                PCOPY 1, 0: CLS
                WHILE INKEY$ <> CHR$(13): WEND
                Biker.xvel = 0
                EXIT SUB
            END IF
    
            if not Crash:
                CurRamp = CurRamp + 1
    
            InAir = 0
            Score = Score + AddScore
            NumTricks = 0
            AddScore = 0
            Tzf = 0
            Tzh = 0
            one = 15        #Tab stops
    
            if CurRamp > NumRamps:
                CALL RotateBike(Txf, Tyf + 180, Tzf)
                CALL RotateBar(Txh, Tyh + 180, Tzh)
                DrawLevel
                DrawBike
                DrawStatus
                message 14, "Press <Enter> to continue.", 1
    
                if Score >= ScoreToBeat(Level) :
                    LevelFinished = True
                    message 10, getBeatLevelMsg(successPhrases), 1
                    doMessage LocateRow, msg, MsgFrames
    
                else:
    
                    InitBike
                    InitLevel(Level)
                    message 10, LostLevel$, 1
                    message LocateRow, STRING$(80, " "), 1
                 
                    #if Level <= FinalLevel :
                    #    msg = "Level " + LTRIM$(STR$(Level))
                    #    Message LocateRow, msg, INT(AnnounceFrames / 2)
                    #END IF
                
                END IF
    
                PCOPY 1, 0: CLS
                WHILE INKEY$ <> CHR$(13): WEND
    
                if DoRunSummary:
                    if LevelFinished:
                        RunSummary
                    END IF
                END IF
    
            END IF
    END IF
END SUB

#==============================================================================
#SUB OptionsMenu
#==============================================================================
def OptionsMenu:
    CLS
    one = 20: two = 50
    max = 7
    flag = 1
    
    DO
        message 1, STRING$(80, "-"), 1
        message 2, "Trick Biker - Options", 1
        message 3, STRING$(80, "-"), 1
        message 23, "<I> and <K> select, <Enter> confirms selection, <Esc> exits", 1
        
        
        LOCATE 5
        if DrawPoints = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Draw Debug Points"; TAB(two); Status$
        
        LOCATE 7
        if Track3D = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "3D Track"; TAB(two); Status$
        
        LOCATE 9
        if DoRunSummary = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Do Run Summary"; TAB(two); Status$
        
        LOCATE 11
        if CrowdOn = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Draw Crowd (not implemented)"; TAB(two); Status$
        
        LOCATE 13
        if VSync = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "VSync"; TAB(two); Status$
        
        LOCATE 15
        if SloMo = -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Slow-Motion Tricks"; TAB(two); Status$
        
        LOCATE 17
        PRINT TAB(one); "View Intro Again"
        
        flagY = (flag * 2 * 14) + 14 * 2
        LINE (80, flagY)-(560, flagY + 14), 4, B
        
        PCOPY 1, 0: CLS
        
        a$ = INKEY$
        SELECT CASE UCASE$(a$)
            CASE "I"
                flag = flag - 1
                if flag < 1 : flag = max
        
            CASE "K"
                flag = flag + 1
                if flag > max : flag = 1
        
            CASE CHR$(13)
                SELECT CASE flag
                    CASE 1
                        if DrawPoints = 0 :
                            DrawPoints = -1
                        else:
                            DrawPoints = 0
                        END IF
                 
                    CASE 2
                        if Track3D = 0 :
                            Track3D = -1
                        else:
                            Track3D = 0
                        END IF
                 
                    CASE 3
                        if DoRunSummary = 0 :
                            DoRunSummary = -1
                        else:
                            DoRunSummary = 0
                        END IF
                 
                    CASE 5
                        if VSync = 0 :
                            VSync = -1
                        else:
                            VSync = 0
                        END IF
                 
                    CASE 6
                        if SloMo = 0 :
                            SloMo = -1
                        else:
                            SloMo = 0
                        END IF
        
                    CASE 7
                        CALL Intro
                        Scale = 175
                    END SELECT
        
            CASE CHR$(27)
                EXIT SUB
        END SELECT
        
    LOOP
END SUB


#==============================================================================
#SUB RenderLogo
#==============================================================================
def RenderLogo:
    #FOR n = 1 TO NumPts
    #    CIRCLE (Pts2D(n).x, Pts2D(n).y), 1, 14
    #NEXT n
    
    FOR n = 1 TO NumLines
        PointA = Lines(n).StartPt
        PointB = Lines(n).EndPt
    
    SELECT CASE n
        CASE 1 TO 36
            col = 4
        CASE 37 TO 84
            col = 15
        CASE 85 TO 129
            col = 1
    END SELECT
    LINE (Pts2D(PointA).x, Pts2D(PointA).y)-(Pts2D(PointB).x, Pts2D(PointB).y), col
    NEXT n
END SUB


#==============================================================================
#SUB Rotate (xa, ya, za)
#==============================================================================
def Rotate(xa, ya, za):
    # This is a janky matrix multiplication hack. This is x rotation, then y rotation, then z rotation (multiplied out by hand and written as the composed formula)
    FOR n = 1 TO NumPts
        ax = (coss(ya) * coss(za))
        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
        
        bx = (coss(ya) * sinn(za))
        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
        
        cx = (-sinn(ya))
        cy = (sinn(xa) * coss(ya))
        cz = (coss(xa) * coss(ya))
        
        OutPts(n).x = ((InPts(n).x * ax) + (InPts(n).y * ay) + InPts(n).z * az)
        OutPts(n).y = ((InPts(n).x * bx) + (InPts(n).y * by) + InPts(n).z * bz)
        OutPts(n).z = ((InPts(n).x * cx) + (InPts(n).y * cy) + InPts(n).z * cz)
        
        Pts2D(n).x = 640 - (lScale * (OutPts(n).x / (OutPts(n).z + lz)) + lx)
        Pts2D(n).y = lScale * (OutPts(n).y / (OutPts(n).z + lz)) + ly
        
    NEXT n

END SUB

#==============================================================================
#SUB RotateBar (xa, ya, za)
#==============================================================================
def RotateBar(xa, ya, za):
    FOR n = 1 TO NumPtsH
        ax = (coss(ya) * coss(za))
        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
        
        bx = (coss(ya) * sinn(za))
        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
        
        cx = (-sinn(ya))
        cy = (sinn(xa) * coss(ya))
        cz = (coss(xa) * coss(ya))
        
        BarOutPts(n).x = ((BarInPts(n).x * ax) + (BarInPts(n).y * ay) + BarInPts(n).z * az)
        BarOutPts(n).y = ((BarInPts(n).x * bx) + (BarInPts(n).y * by) + BarInPts(n).z * bz)
        BarOutPts(n).z = ((BarInPts(n).x * cx) + (BarInPts(n).y * cy) + BarInPts(n).z * cz)
        
        BarPts2D(n).x = Scale * (BarOutPts(n).x / (BarOutPts(n).z + z)) + x
        BarPts2D(n).y = Scale * (BarOutPts(n).y / (BarOutPts(n).z + z)) + y
        
    NEXT n

END SUB

#==============================================================================
#SUB RotateBike (xa, ya, za)
#==============================================================================
def RotateBike(xa, ya, za):
    FOR n = 1 TO NumPtsF
        ax = (coss(ya) * coss(za))
        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
        
        bx = (coss(ya) * sinn(za))
        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
        
        cx = (-sinn(ya))
        cy = (sinn(xa) * coss(ya))
        cz = (coss(xa) * coss(ya))
        
        FrameOutPts(n).x = ((FrameInPts(n).x * ax) + (FrameInPts(n).y * ay) + FrameInPts(n).z * az)
        FrameOutPts(n).y = ((FrameInPts(n).x * bx) + (FrameInPts(n).y * by) + FrameInPts(n).z * bz)
        FrameOutPts(n).z = ((FrameInPts(n).x * cx) + (FrameInPts(n).y * cy) + FrameInPts(n).z * cz)
        
        BikePts2D(n).x = Scale * (FrameOutPts(n).x / (FrameOutPts(n).z + z)) + x
        BikePts2D(n).y = Scale * (FrameOutPts(n).y / (FrameOutPts(n).z + z)) + y
        
    NEXT n
    
END SUB

#==============================================================================
#SUB RunSummary
#==============================================================================
def RunSummary:
    range = 3
    flag = 1
    
    DO
        LOCATE 1, 1
        PRINT STRING$(80, "-")
        message 2, "Run Summary for Level " + LTRIM$(STR$(Level)), 1
        LOCATE 4, 1: PRINT STRING$(80, "-")
        message 6, "Biker: " + RiderName$, 1
        LOCATE 7: PRINT STRING$(80, "-")
        LOCATE 8, 1
        FOR n = flag TO flag + range        #TrickCounter
            PRINT TAB(3); LTRIM$(STR$(n));
            PRINT TAB(10); RunReport$(n)
        NEXT n
        PRINT
        PRINT STRING$(80, "-")
        PRINT TAB(3); "Total: "; TAB(10); LTRIM$(STR$(Score)); " pts.";
        PRINT TAB(30); "<I and K> scroll, <Enter> continues."
        PRINT STRING$(80, "-")
        
        message 23, "Press <Enter> to continue.", 1
        DrawBike
        DrawLevel
        PCOPY 1, 0: CLS
        
        a$ = INKEY$
        SELECT CASE UCASE$(a$)
            CASE "I"
                flag = flag - 1
                if flag < 1 : flag = 1
            CASE "K"
                flag = flag + 1
                if flag > TrickCounter - range : flag = TrickCounter - range
            CASE CHR$(13)
                EXIT SUB
            END SELECT
        
    LOOP
    #WHILE INKEY$ <> CHR$(13): WEND
END SUB

#==============================================================================
#SUB SelectBike
#==============================================================================
def SelectBike:
    CLS
    ang = 0
    Tzf = 0: Tzh = Tzf
    x = 320: y = 130: Scale = 336: Style = 1: Txf = 0: Txh = Txf
    GOSUB Update
    
    DO
    message 1, STRING$(80, "-"), 1
    message 2, "Trick Biker - Select Bike", 1
    message 3, STRING$(80, "-"), 1
    message 23, "<J> and <L> select, <Enter> confirms selection.", 1
    
    a$ = INKEY$
    SELECT CASE UCASE$(a$)
        CASE "J"
            Style = Style - 1
            if Style < 1 : Style = MaxBikes
            GOSUB Update
        CASE "L"
            Style = Style + 1
            if Style > MaxBikes : Style = 1
            GOSUB Update
        CASE CHR$(13)
            BikeStyle = Style
            RiderName$ = msg
            EXIT SUB
        CASE CHR$(27)
            Quit = True
            EXIT SUB
    END SELECT
    
    SELECT CASE Style
        CASE 1
            msg = q + "Gnarly" + q + " Charlie Robinson"
        CASE 2
            msg = "Upton " + q + "Ups" + q + " Malone"
        CASE 3
            msg = "* Justin Grady *"
        CASE 4
            msg = "Abner Brown"
        CASE 5
            msg = "* John Turner *"
        CASE 6
            msg = "Carl Greene"
        CASE 7
            msg = "David Gonzalez"
        CASE 8
            msg = "*** Lou Herard ***"
        CASE 9
            msg = "Willie the Wildcat"
        CASE 10
            msg = "Mike " + q + "Blues" + q + " Klues"
        CASE 11
            msg = "Jamal Jenkins"
        CASE 12
            msg = "Ultimus"
        CASE 13
            msg = "Popeye"
        CASE else:
            msg = ""
    END SELECT
    
    message 5, msg, 1
    
    ang = ang + 6 MOD 360
    #ang = 90
    Tyf = ang: Tyh = Tyf
    
    CALL DrawTrophies(NumTrophies(Style), 500)
    CALL RotateBike(Txf, Tyf + 180, Tzf)
    CALL RotateBar(Txh, Tyh + 180, Tzh)
    DrawBike
    
    LOCATE 16, 25: PRINT "Speed"
    LOCATE 18, 25: PRINT "Jump"
    bx = 270: w = 7
    maxjmp = 2.8: maxspeed = 22 #these were taken from DATA
    
    by1 = 15 * 14 + 2         #spd
    by2 = 17 * 14 + 2         #jmp
    LINE (bx - 1, by1)-(bx + 101, by1 + w), 14, B
    LINE (bx, by1 + 1)-(bx + 100 * Biker.maxspd / maxspeed, by1 + w - 1), 6, BF
    
    LINE (bx - 1, by2)-(bx + 101, by2 + w), 14, B
    LINE (bx, by2 + 1)-(bx + 100 * Biker.jump / maxjmp, by2 + w - 1), 6, BF
    
    PCOPY 1, 0: CLS
    LOOP
    
    
Update:
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    RESTORE BikerData
    FOR n = 1 TO Style
        READ Biker.maxspd, Biker.jump, Biker.pump, Biker.turn
    NEXT n
    
    RETURN
END SUB

#==============================================================================
#FUNCTION sinn (x)
#==============================================================================
def sinn(x):
    sinn = SIN(toRad(x))
END FUNCTION

#==============================================================================
#FUNCTION toRad (x)
#==============================================================================
def toRad(x):
    toRad = (x MOD 360) * (3.14159 / 180)
END FUNCTION



#===========================================================================================================
# TODO get rid of all this hardcoded crap. At the time you made this game, you didn't know how to do file IO
# All of these data points belong in a file
TrickPointData:
DATA 16       : #Total # of tricks
DATA 100      : #Point worth of trick 1
DATA 150      : #Point worth of trick 2
DATA 125
DATA 150
DATA 250
DATA 350
DATA 200
DATA 175
DATA 200
DATA 300
DATA 330
DATA 375
DATA 75
DATA 200
DATA 100
DATA 275




BikeColorData: # TODO put these bike colors into the bike class
#Format BodyCol1, BodyCol2, FrontSpokeCol,BackSpokeCol
DATA 15,1,15,15   : #Type 1  - Standard bike
DATA 9,14,6,6     : #Type 2  - Standard bike 2
DATA 7,7,8,8      : #Type 3  - Justin Grady's Chrome Bike
DATA 4,12,1,1     : #Type 4  - Standard bike 3
#DATA 9,13,5,8     : #Type 5  - John Turner's Haro Shredder
DATA 1,1,5,8      : #John Turner's Haro Shredder
DATA 3,11,2,10    : #Type 6  - Standard bike 4
DATA 14,6,15,1    : #Type 7  - Standard bike 5
DATA 8,4,7,7      : #Type 8  - Lou Herard's Schwinn Predator
DATA 15,7,14,1    : #Type 9  - Standard bike 6: Wheeling Special
DATA 1,9,11,11    : #Type 10 - Standard bike 7
DATA 6,5,5,6      : #Type 11 - Standard bike 8

DATA 4,4,4,4      : #Ultimus
DATA 10,15,14,14  : #Popeye

BikerData:
#Format: maxspd, jump, pump, turn
DATA 17,2.2,3,45  : #Gnarly Robinson
DATA 15,2.8,3,45  : #Upton "Ups" Malone
DATA 22,1.7,2,45  : #Justin Grady
DATA 19,1.95,2,45  : #Abner Brown
DATA 18,2.2,3,45  : #John Turner
DATA 21,1.8,3,45  : #Carl Greene
DATA 22,1.7,3,45 : #David Gonzalez
DATA 18,2.1,3,45  : #Lou Herard
DATA 21,1.75,4,45  : #Willie the Wildcat
DATA 16,2.35,2,45 : #Mike "Blues" Klues
DATA 20,1.8,3,45  : #Jamal Jenkins
DATA 18,2.0,2,90  : #Ultimus (secret character)
DATA 18,2.1,3,90  : #Popeye

ScoresToBeat:
DATA 1000     : #Score to beat for level 1
DATA 1350     : #Score to beat for level 2
DATA 1250
DATA 1500
DATA 1900
DATA 1000

InstructionsData:
#Format: Text, AlignFlag (0 = left align, 1 = center align)
DATA 101   : #number of lines
DATA "   Chrome Peaks, California: the boom town of biking.  You're the new dude in"
DATA "town with the bad attitude.  What would that be?  That you're the best damn"
DATA "biker in the land.  Well, now's your chance to prove it.  With plenty of ramps"
DATA "around, you have all sorts of opportunities to show off your stuff.  And just"
DATA "how will you do that?"

DATA "- <l> Pedals (tap, don't hold), <p> pauses for a phat freeze frame"
DATA "- <q> leans back (in air), <w> leans forward (in air)"
DATA "- <h, j, k, y, u, i, o, and n> all do certain tricks"
DATA "- <H, J, K, Y, U, I, O, and N> all do certain other tricks "
DATA "- You'll have to figure out which is which (HINT: Some are slower than others)."

DATA "    Generally, the moves that include <Shift> are a bit more risky than the"
DATA "tricks that don't.  They usually count for more points, though, so you should"
DATA "try to use them when you can.  Also, look for combos that will earn you points."
DATA "The more moves you do in one jump, the fewer points you have to collect in the"
DATA "following jumps.  Now I've said enough.  Go bike."
DATA ""
DATA "---------------------------"
DATA "Game Format                "
DATA "---------------------------"
DATA "    Each level has a set number of ramps and a set point total that you need to"
DATA "meet or beat, in order to advance.  Don't overuse tricks, because their worth"
DATA "depreciates.  The pattern goes like this: Take, for example, a 400 pt. trick."
DATA "      Usage:            Worth:"
DATA "      First time:       400 pts"
DATA "      Second time:      300 pts"
DATA "      Third time:       200 pts"
DATA "      Fourth time:      100 pts"
DATA "      Fifth+ time:        1 pt."
DATA "    The moral of the story is vary your tricks.  Also, different bikes have"
DATA "different abilities: speed, jumping, and acceleration (not shown on bike"
DATA "selection screen).  So, you'll have to change up your routines with different"
DATA "bikes in order to achieve the given point totals.  If you fail, chances are"
DATA "that the CPU brain of this program will make fun of you.  So don't bonk."

DATA "---------------------------"
DATA "How to read the Run Summary"
DATA "---------------------------"
DATA "    It's really simple.  Let's look at an example (points are NOT the same as"
DATA "in the game)."
DATA ""
DATA "  1   Tailwhip!!!  50 pts"
DATA "  2   90 Barturn!!! 99 pts 2 TRICK COMBO!!!"
DATA "  3   360 turn!!!  149 pts 3 TRICK COMBO!!!"
DATA "  4   Backflip!!! 75 pts"
DATA "  etc..."
DATA "    So, your first trick was a tailwhip worth 50 pts.  Then you threw in a 90"
DATA "degree barturn worth 49 pts (50 + 49 = 99) for a 2 trick combo.  In the same"
DATA "combo, you busted out a phat 360 worth 50 pts (99 + 50 = 149) to complete the"
DATA "3 trick combo.  So, basically, the numbers on the left are the count of how"
DATA "many tricks you did.  The point totals are the total number of points you got"
DATA "for the entire combo, not each individual trick.  And if you want to know how"
DATA "many tricks you did in your combo, just look at the last combo number before"
DATA "the next blank combo line.  In this case, your first three tricks made up a"
DATA "3 trick combo.  Got it?  Well, if you don't it's not my problem."
DATA ""
DATA "Okay, NOW I've said enough.  Go bike."
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA "HA HA! You're still reading the instructions.  What a putz.  Go play the game."
DATA "There's nothing else to see."
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA "Man, you're still here?  Go away!"
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA "OK.  Now this is getting ridiculous.  Go play the game already!!!"
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA ""
DATA "Lou Herard is the supreme ruler of the universe."
DATA "<<< End of Text ... Really >>>"






LogoData:
DATA 86
DATA -16,14,2       : #Front side of Y
DATA -13,14,2
DATA -13,2,2
DATA -10,2,2
DATA -10,14,2
DATA -7,14,2
DATA -7,0,2
DATA -10,-3,2
DATA -10,-14,2
DATA -13,-14,2
DATA -13,-3,2
DATA -16,0,2

DATA -16,14,-2       : #Back side of Y
DATA -13,14,-2
DATA -13,2,-2
DATA -10,2,-2
DATA -10,14,-2
DATA -7,14,-2
DATA -7,0,-2
DATA -10,-3,-2
DATA -10,-14,-2
DATA -13,-14,-2
DATA -13,-3,-2
DATA -16,0,-2

DATA -4,7,2         : #Front side of 2
DATA -4,10,2
DATA -1,14,2
DATA 1,14,2
DATA 4,10,2
DATA 4,2,2
DATA -1,-5,2
DATA -1,-8,2
DATA 4,-8,2
DATA 4,-14,2
DATA -4,-14,2
DATA -4,-5,2
DATA 1,2,2
DATA 1,10,2
DATA -1,10,2
DATA -1,7,2

DATA -4,7,-2         : #Back side of 2
DATA -4,10,-2
DATA -1,14,-2
DATA 1,14,-2
DATA 4,10,-2
DATA 4,2,-2
DATA -1,-5,-2
DATA -1,-8,-2
DATA 4,-8,-2
DATA 4,-14,-2
DATA -4,-14,-2
DATA -4,-5,-2
DATA 1,2,-2
DATA 1,10,-2
DATA -1,10,-2
DATA -1,7,-2

DATA 8,14,2       : #Front side of K"
DATA 11,14,2
DATA 11,2,2
DATA 13,6,2
DATA 13,14,2
DATA 16,14,2
DATA 16,6,2
DATA 13,0,2
DATA 16,-6,2
DATA 16,-14,2
DATA 13,-14,2
DATA 13,-6,2
DATA 11,-2,2
DATA 11,-14,2
DATA 8,-14,2

DATA 8,14,-2       : #Back side of K"
DATA 11,14,-2
DATA 11,2,-2
DATA 13,6,-2
DATA 13,14,-2
DATA 16,14,-2
DATA 16,6,-2
DATA 13,0,-2
DATA 16,-6,-2
DATA 16,-14,-2
DATA 13,-14,-2
DATA 13,-6,-2
DATA 11,-2,-2
DATA 11,-14,-2
DATA 8,-14,-2


LineData:
DATA 129

DATA 1,2      : #Front Side of Y
DATA 2,3
DATA 3,4
DATA 4,5
DATA 5,6
DATA 6,7
DATA 7,8
DATA 8,9
DATA 9,10
DATA 10,11
DATA 11,12
DATA 12,1
DATA 13,14      : #Back side of Y
DATA 14,15
DATA 15,16
DATA 16,17
DATA 17,18
DATA 18,19
DATA 19,20
DATA 20,21
DATA 21,22
DATA 22,23
DATA 23,24
DATA 24,13

DATA 1,13       : #Connect the front of Y to back of Y
DATA 2,14
DATA 3,15
DATA 4,16
DATA 5,17
DATA 6,18
DATA 7,19
DATA 8,20
DATA 9,21
DATA 10,22
DATA 11,23
DATA 12,24

DATA 25,26          : #Front side of 2
DATA 26,27
DATA 27,28
DATA 28,29
DATA 29,30
DATA 30,31
DATA 31,32
DATA 32,33
DATA 33,34
DATA 34,35
DATA 35,36
DATA 36,37
DATA 37,38
DATA 38,39
DATA 39,40
DATA 40,25

DATA 41,42          : #Back side of 2
DATA 42,43
DATA 43,44
DATA 44,45
DATA 45,46
DATA 46,47
DATA 47,48
DATA 48,49
DATA 49,50
DATA 50,51
DATA 51,52
DATA 52,53
DATA 53,54
DATA 54,55
DATA 55,56
DATA 56,41

DATA 25,41          : #Connect front of 2 to back of 2
DATA 26,42
DATA 27,43
DATA 28,44
DATA 29,45
DATA 30,46
DATA 31,47
DATA 32,48
DATA 33,49
DATA 34,50
DATA 35,51
DATA 36,52
DATA 37,53
DATA 38,54
DATA 39,55
DATA 40,56

DATA 57,58          : #Front side of K
DATA 58,59
DATA 59,60
DATA 60,61
DATA 61,62
DATA 62,63
DATA 63,64
DATA 64,65
DATA 65,66
DATA 66,67
DATA 67,68
DATA 68,69
DATA 69,70
DATA 70,71
DATA 71,57

DATA 72,73          : #Back side of K
DATA 73,74
DATA 74,75
DATA 75,76
DATA 76,77
DATA 77,78
DATA 78,79
DATA 79,80
DATA 80,81
DATA 81,82
DATA 82,83
DATA 83,84
DATA 84,85
DATA 85,86
DATA 86,72

DATA 57,72          : #Connect front of K to back of K
DATA 58,73
DATA 59,74
DATA 60,75
DATA 61,76
DATA 62,77
DATA 63,78
DATA 64,79
DATA 65,80
DATA 66,81
DATA 67,82
DATA 68,83
DATA 69,84
DATA 70,85
DATA 71,86


#TODO Move Credits into its own game state
CreditzData:
DATA 10        : #Number of Pages

DATA 2        : #Number of lines on page 1
DATA 2        : #Number of lines on page 2
DATA 2        : #etc...
DATA 2
DATA 8
DATA 2
DATA 4
DATA 8
DATA 7
DATA 4

DATA "-= Lead Programmer =-"   : #Data for page 1
DATA "Lou Herard"

DATA "-= Assistant Programmer =-"    : #Data for page 2
DATA "Lou Herard"

DATA "-= Design =-"        : #etc...
DATA "Lou Herard"

DATA "-= 3D Routine =-"
DATA "Lou Herard"

DATA "-= Beta Testing =-"
DATA "Lou Herard"
DATA "Justin Grady"
DATA "John Turner"
DATA "Jeremy Goodman"
DATA "Nanette Tarbouni"
DATA "Bob Hallman"
DATA "Aashay Desai"

DATA "-= Trick Anims =-"
DATA "Lou Herard"

DATA "-= Special Bikes =-"
DATA "Lou Herard"
DATA "Justin Grady"
DATA "John Turner"

DATA "-= Special Thanks =-"
DATA "ESPN for trick names (which still aren't all right)"
DATA "Acclaim Max Sports for trick names"
DATA "My beta testers for playing my game"
DATA "Mr. Hallman for teaching me how to make my code look good"
DATA "Any math teacher who helped me learn 3D formulas"
DATA "Just about any author who wrote a book on 3D graphics"
DATA "You for playing my game and ACTUALLY READING THE CREDITS!"

DATA "-= Y2K Compliant Software Staff =-"
DATA "Lou Herard - Programmer"
DATA "Lou Herard - Producer"
DATA "Lou Herard - Chief Editor"
DATA "Bob Hallman - Editor"
DATA "Bob Hallman - Logic Wizard"
DATA "Bob Hallman - Code Buster"

DATA "-= XPDient Developers Staff =-"
DATA "Lou Herard - Advertiser"
DATA "Lou Herard - Promoter"
DATA "Lou Herard - Developer"

TrophyData:
DATA 14     : #Number of points
DATA-4,7
DATA 4,7
DATA 3.5,5
DATA 3,4
DATA 2,3
DATA 1,2
DATA 1,1
DATA 3,-0
DATA -3,-0
DATA -1,1
DATA -1,2
DATA -2,3
DATA -3,4
DATA -3.5,5

TrophyLineData:
DATA 14
DATA 1,2
DATA 2,3
DATA 3,4
DATA 4,5
DATA 5,6
DATA 6,7
DATA 7,8
DATA 8,9
DATA 9,10
DATA 10,11
DATA 11,12
DATA 12,13
DATA 13,14
DATA 14,1


XPDData:
DATA 32
DATA -15,4
DATA -13,4
DATA -10,1
DATA -7,4
DATA -5,4
DATA -9,0
DATA -5, -4
DATA -7,-4
DATA -10,-1
DATA -13,-4
DATA -15,-4
DATA -11,0
DATA 3,4
DATA 5,2
DATA 5,0
DATA 3,-2
DATA -3,-2
DATA -3,-4
DATA -3,2
DATA 3,2
DATA 3,0
DATA -3,0
DATA 5,4
DATA 13,4
DATA 15,2
DATA 15,-2
DATA 13,-4
DATA 5,-4
DATA 7,1
DATA 13,1
DATA 13,-1
DATA 7,-1

XPDLineData:
DATA 34
DATA 1,2
DATA 2,3
DATA 3,4
DATA 4,5
DATA 5,6
DATA 6,7
DATA 7,8
DATA 8,9
DATA 9,10
DATA 10,11
DATA 11,12
DATA 12,1
DATA 5,13
DATA 13,14
DATA 14,15
DATA 15,16
DATA 16,17
DATA 17,18
DATA 18,7
DATA 7,5
DATA 19,20
DATA 20,21
DATA 21,22
DATA 22,19
DATA 23,24
DATA 24,25
DATA 25,26
DATA 26,27
DATA 27,28
DATA 28,23
DATA 29,30
DATA 30,31
DATA 31,32
DATA 32,29





def main():
    random.seed()

    # TODO maybe put all this stuff into a file and load it at game startup
    successPhrases = [ \
    "Alright, man, you beat the level!  Good job!"
    , "That was trick biking at its finest.  You rule."
    , "You made it!  Nice trickin'!"
    , "Where'd you come from, planet Bikelonia?  You're awesome!"
    , "You da MAN!!!"
    , "Yeah, alright!  You won, man!  Now get the hell out of here."
    , "SWEEEEET run, man.  Absolutely top-notch biking."
    , "The level has suffered defeat at your hands."
    , "Can I have your autograph?"
    , "Wow!  You got so high, you need a drug test.  Awesome."
    , "Alright, admit it.  You're an angel from Biker's Heaven."
    ]

failurePhrases = [ \
    "Aww, man, you didn't make it.  Now you've gotta do it all over."
    , "Well, it was a nice run, but you didn't win anything."
    , "Maybe that score will win somewhere else, but not here in Chrome Peaks."
    , "Look at your score, then look at the required score.  See any differences?"
    , "That's a nice score.  Too bad it's NOT GOOD ENOUGH."
    , "Maybe it's the shoes.  It's gotta be the shoes.  THEY SUCK!!!"
    , "That was great, but you didn't win anything.  Go back and do it again."
    , "INSUFFICIENT SCORE PROVIDED.  PLEASE INSERT MORE POINTS."
    , "Yeah, you beat the level! -- Oh, wait, no you didn't."
    , "Maybe if you doubled your score, you'd beat this level."
    ]

crashPhrases = [ \
    "Crash!!!"
    , "OOOH!!!  That had to hurt."
    , "Ow!  I would not like to be you right now."
    , "Medic!!!"
    , "Uh, excuse me, can we get an ambulance around here, please?"
    , "I hope your mom's not watching you fall like this."
    , "Do you know how to ride a bike?"
    , "Man, you suck."
    , "Yeah, the point of the game is to land the tricks."
    , "Oh, I can't watch this."
    , "Well, at least we know you can fall."
    , "Wow!  So tell me, what's the dirt taste like?"
    , "I hope you were wearing your helmet."
    , "That was one sick crack your head made when you hit the ground."
    , "It's a good thing that there's not really anybody on that bike."
    , "911!!!"
    , "Oh, you just broke yourself (like you didn't notice)."
    ]

rampCrashPhrases = [ \ 
    "Umm, you were supposed to jump over the gap, not into it."
    , "Next time, try clearing the jump."
    , "Oh, man, that's pathetic."
    , "You bring shame to the name of all trick bikers."
    , "Yeah, now you know why they call it a landing ramp."
    , "Should I wire landing lights into the track?"
    , "I hope you never become a pilot."
    ]

    MainMenu()


if __name__ == '__main__':
    main()

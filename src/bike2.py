#!/usr/bin/env python2

import pygame
import random
import os
import sys
import logging

# pymkfgame imports
import math
from pymkfgame.core.game_application import GameApplication
from pymkfgame.mkfmath import matrix
from pymkfgame.mkfmath import vector

import game_state_main_menu

# STILL TODO
# TODO replace RND with random.random()

#==============================================================================
class Point3D(object):
    def __init__(self, px=0.0, py=0.0, pz=0.0):
        #self.v = [0.0, 0.0, 0.0] # TODO perhaps use a list, rather than 3 floats.
        self.x = px
        self.y = py
        self.z = pz

    def __getitem__(self, index):
        ## accessor
        # TODO rework this Point3D class. You were taking shortcuts to get a quick demo running. But you should make this class use a list as its underlying data structure; and then write an access that returns an item from the array
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z


    def __setitem__(self, index):
        ## set item property
        pass


#==============================================================================
class Point2D(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

            
#==============================================================================
class LineType(object):
    def __init__(self):
        self.StartPt = 0
        self.EndPt = 0

#==============================================================================
class RampType(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.incline = 0.0
        self.length = 0.0   #length of ramp
        self.dist = 0.0     #length of jump (gap), dist btwn up ramp and down ramp

#==============================================================================
class RiderType(object):
    def __init__(self):
        self.maxspd = 0.0   #max. speed rider can reach
        self.xvel = 0.0     #x-component of speed coming off a ramp
        self.yvel = 0.0     #y-component "    "     "     "  "   "
        self.jump = 0.0     #added y-component when rider pulls up off a ramp
        self.pump = 0.0     #pedaling (pumping) power
        self.turn = 0.0     #turning speed

#==============================================================================
class ColorType(object):
    def __init__(self):
        # TODO replace .r, .g, and .b with tuples? Figure out how to use @property, to allow you to set individual items of the tuple, using .r, .g, .b?
        self.r = 0.0
        self.g = 0.0
        self.b = 0.0
        

#==============================================================================
class PointLineObj(object):
    """ A wireframe model

        NOTE: for 3D object representation, there are better data structures, e.g. polygon/vertex/edge. Consult your Library, and/or the googles

    """
    def __init__(self):
        self.position = Point3D()
        self.points = []        # these are the actual model points
        self._xpoints = []      # these are the transformed points; recomputed every frame, based on transformations
        self.lines = []     # Store points maybe as list objects
        self.thx = 0.0  # Euler angles; used for computing rotations
        self.thy = 0.0
        self.thz = 0.0
        self.matTrans = matrix.Matrix() # TODO be smarter about the matrices? Make an overall transformation matrix that is Trans x Rot?
        self.matRot = matrix.Matrix()
        self.children = {}  # A dict of sub-objects (e.g., bike is a composite obj, containing a frame model and handlebars model

    def addPoint(self, point):
        """ Take in a Point3D object. Append the point object to self.points """
        # TODO maybe make it possible to clear the points list?
        self.points.append(point)

    def addLine(self, line):
        """ Take in a LineType object. Append the line object to self.lines """
        self.lines.append(line)

    def draw(self, render_surface, obj_ref=None, composed_xform=matrix.Matrix.matIdent()):
        """ Recursively compose transformations and draw objects """
        if obj_ref is None:
            obj_ref = self

        ##    # TODO finish computing child transform (rot + trans + whatever else you want)
        obj_ref.matRot = matrix.Matrix.matRotY(obj_ref.thy * math.pi / 180)
        obj_ref.matTrans = matrix.Matrix.matTrans(obj_ref.position.x, obj_ref.position.y, obj_ref.position.z)

        # Note: we postmult trans 1st and rot 2nd because the transform are applied right-to-left. e.g.,
        # M = TRv, where T is translate, R is rot, and v is the vector. R is applied 1st, because it's closest to v
        local_composed_xform = matrix.mMultmat(composed_xform, obj_ref.matTrans)
        local_composed_xform = matrix.mMultmat(local_composed_xform, obj_ref.matRot)

        if obj_ref.children:
            for _, child_obj in obj_ref.children.iteritems():
                self.draw(render_surface, child_obj, local_composed_xform)

        # if no children, then compute final transformation matrix and render
        del obj_ref._xpoints[:]

        for point in obj_ref.points:
            p = matrix.mMultvec(local_composed_xform, vector.Vector(point.x, point.y, point.z, 1.0))  # Use a vector, as required by pymkfmath's matrix multiplication api (and don't forget to set homogeneous coord to 1!!)
            obj_ref._xpoints.append(Point3D(p.x, p.y, p.z))     # Then convert back to Point3D to comply with the original code for this game (TODO make some synergies between Point3D and Vector)

        for lineData in obj_ref.lines:
            startPt = lineData[0] - 1   # subtract 1 because we programmed this game in QBASIC with base = 1, not 0
            endPt = lineData[1] - 1

            # Note; for now, we're ignoring z; we only care to test out the frame drawing in 2D
            spCoords = obj_ref._xpoints[startPt]
            epCoords = obj_ref._xpoints[endPt]
            #logging.debug("sPt:{} - {}, ePt:{} - {}".format(startPt, spCoords, endPt, epCoords))
            pygame.draw.line(render_surface, (220, 220, 220), (spCoords[0], spCoords[1]), (epCoords[0], epCoords[1]) )

#==============================================================================
class Bike(PointLineObj):
    def __init__(self):
        self.model = PointLineObj()
        self.colors = []    # a list of ColorType objects, f.k.a. BikeCol (to be set by InitBike())
        self.style = 0      # TODO: consider replacing with a BikeStyle object (right now, style is an int, which dictates which of a predefined set of styles the bike could have)
        self.scale = 1.0
        self.position = Point3D()
        self.velocity = Vector()

        self.crashed = False
        self.tricking = False
        self.trickPhase = 1

    def Init(self):
        """ Initialize bike object
        
            NOTE: This replaces QBASIC InitBike()
        """
        dirname = os.path.dirname( sys.argv[0] )
        with open(os.path.normpath(dirname + "../data/bike_model.json", 'r')) as fd:
            raw_bike_model = json.load(fd)
        #logging.debug("raw_bike_model:{}".format(raw_bike_model))

        # Construct the bike model
        self.position = Point3D(0.0, 0.0, 0.0)
        self.model.position = Point3D(0.0, 0.0, 0.0)    # Force a new obj, not simply a ref to self.position (could also write a "copy" function, similar to a copy constructor, but Python doesn't have copy constructors

        self.model.children['frame'] = PointLineObj()
        #self.model.children['frame'].position = Point3D(-11,0,0) # Displacement from local origin
        for item in raw_bike_model['frame_point_data']:
            pt = Point3D( item[0], item[1], item[2])
            self.model.children['frame'].addPoint(pt)
        # Also copy the line data
        self.model.children['frame'].lines.extend(raw_bike_model['frame_line_data'])  # Couldn't also used addLine() by iterating through my line data and calling addLine(), one by one

        # Now, do the handlebar
        self.model.children['handlebar'] = PointLineObj()
        for item in raw_bike_model['handlebar_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['handlebar'].addPoint(pt)
        self.model.children['handlebar'].lines.extend(raw_bike_model['handlebar_line_data'])

        # Rear tire
        self.model.children['frame'].children['wheel'] = PointLineObj()
        self.model.children['frame'].children['wheel'].position = Point3D(-22,-5,0)
        for item in raw_bike_model['wheel_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['frame'].children['wheel'].addPoint(pt)
        self.model.children['frame'].children['wheel'].lines.extend(raw_bike_model['wheel_line_data'])

        # Front tire
        self.model.children['handlebar'].children['wheel'] = PointLineObj()
        self.model.children['handlebar'].children['wheel'].position = Point3D(0,-5,0)

        for item in raw_bike_model['wheel_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['handlebar'].children['wheel'].addPoint(pt)
        self.model.children['handlebar'].children['wheel'].lines.extend(raw_bike_model['wheel_line_data'])

        ##TODO finish converting the commented-out code to either be in a bike member function, or otherwise wherever it belongs
        ###BikeStyle = 5
        ##
        ### TODO Bike styles and such should be initialized elsewhere (perhaps in general game init)
        ##RESTORE BikeColorData
        ##FOR n = 1 TO BikeStyle
        ##    READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
        ##NEXT n
        ##
        ##RESTORE BikerData
        ##FOR n = 1 TO BikeStyle
        ##    READ Biker.maxspd, Biker.jump, Biker.pump, Biker.turn
        ##NEXT n
        ##
        ### TODO move trick point initialization to be with level initializtion
        ##RESTORE TrickPointData
        ##READ TotNumTricks
        ##FOR n = 1 TO TotNumTricks
        ##    READ Worth(n)
        ##    TimesUsed(n) = 0
        ##NEXT n


#==============================================================================
# TODO remove all these variable definitions and stuff.. Or, move them into the appropriate score and Pythonize them
####CONST StandardY = 315
####CONST Factor = .25
####CONST FinalLevel = 6
####CONST MaxPts = 150
####
####
##### NOTE: DIM SHARED shares variable values with sub-procedures without passing the value in a parameter.
####
###### Vars related to rendering the logo at intro time (TODO put into class)
####DIM SHARED InPts(1 TO MaxPts) AS Point3D, OutPts(1 TO MaxPts) AS Point3D            # Global arrays. InPts is input to Rotate funcs. It appears to be used only for the logos in the Intro
####DIM SHARED Pts2D(1 TO MaxPts) AS Point2D                                            # Array that stores computed projections of points. InPts and OutPts are in 3D; Pts2D is the projection of OutPts onto the screen surface
####DIM SHARED Lines(1 TO MaxPts * 3) AS LineType                                       # Lines is an array that holds the line data for the logo.
####DIM SHARED NumPts, NumLines
####
####DIM SHARED XPD(1 TO MaxPts) AS Point2D, XPDLine(1 TO MaxPts) AS LineType            # Points and such for XPD logo
####
###### Vars related to rendering bike
####DIM SHARED FrameInPts(1 TO MaxPts) AS Point3D, BarInPts(1 TO MaxPts) AS Point3D
####DIM SHARED FrameOutPts(1 TO MaxPts) AS Point3D, BarOutPts(1 TO MaxPts) AS Point3D
####DIM SHARED BikePts2D(1 TO MaxPts) AS Point2D, BarPts2D(1 TO MaxPts) AS Point2D
####DIM SHARED BikeLine(1 TO MaxPts) AS LineType, BarLine(1 TO MaxPts) AS LineType
####DIM SHARED NumPtsF, NumLinesF, NumPtsH, NumLinesH
####DIM SHARED x, y, z, Txf, Tyf, Tzf, Txh, Tyh, Tzh                                    # Replace x,y,z with bike.position; and Tx,Ty,Tz with something.. matrices or quats
####  #T(n)f is the angle (theta) on the n axis of the frame
####  #T(n)h is the angle on the n axis of the handlbars (used for bar tricks)
####  #x, y, and z are the bike's coordinates
####DIM SHARED BikeCol(1 TO 4), BikeStyle, Scale, Level, LevelFinished
####
###### Vars related to level
####DIM SHARED Ramp(1 TO 20) AS RampType
####DIM SHARED NumRamps, CurRamp, InAir, Tricking, Trick, MemAngle, TrickPhase, Crash
####DIM SHARED MsgFrames, msg, LocateRow, NumTricks
####DIM SHARED TotNumTricks, TimesUsed(1 TO 20), Worth(1 TO 20)
####
###### Vars related to game state/engine
####DIM SHARED Paused, Quit
####DIM SHARED FPS, FPStimerA, FPStimerB
####
###### Vars related to player
####DIM SHARED Biker AS RiderType, Score, AddScore, RiderName$, MaxBikes
####DIM SHARED q AS STRING * 1: q = CHR$(34)
####
###### Vars related to level
####DIM SHARED ScoreToBeat(1 TO FinalLevel)
####DIM SHARED RunReport$(1 TO 20), TrickCounter
####DIM SHARED lx, ly, lz, lScale
####DIM SHARED DrawPoints, Track3D, CrowdOn, DoRunSummary, VSync, SloMo

#==============================================================================
# Here is where the game begins
#==============================================================================
# NOTE: This is where the script starts in QBASIC. This is technically pre-game init stuff. It should go into an init function


## TODO Fix a bunch of global vars. Basically, this entire game was made using global vars in QB. Some of those will need to be converted to members of classes. Others may need to be local vars within functions

## Also, port QBASIC syntax to Python

###==============================================================================
###FUNCTION coss (x)
###Returns the cosine of x, where x is an angle in degrees
###==============================================================================
### TODO maybe add this to pymkfgame.math?
##def coss(x):
##    val = math.cos(toRad(x))
##    if abs(val) < 0.00001:
##        val = 0.0
##    return val
##
### TODO possibly add to pymkfgame.math
###==============================================================================
###FUNCTION sinn (x)
###==============================================================================
##def sinn(x):
##    sinn = SIN(toRad(x))
##END FUNCTION
##
### TODO possibly add to pymkfgame.math
###==============================================================================
###FUNCTION toRad (x)
###==============================================================================
##def toRad(x):
##    toRad = (x MOD 360) * (3.14159 / 180)
##END FUNCTION
##
##
##
### TODO replace all message and doMessage calls with pymkfgame.display_msg or pymkfgame.display_msg_manager (message starts the message, doMessage does the updates/removal of expired messages)
###==============================================================================
###SUB message (row, Text$, frames)
###==============================================================================
##def message(row, Text$, frames):
##    MsgFrames = frames
##    LOCATE row, 41 - LEN(Text$) / 2
##    PRINT Text$
##    END SUB
##
###==============================================================================
###SUB doMessage (row, Text$, frames)
###Displays a message on the screen
###==============================================================================
##def doMessage(row, Text$, frames):
##    # TODO replace with the messaging system you created for falldown
##    if MsgFrames <= 0:
##        msg = "": EXIT SUB
##    MsgFrames = MsgFrames - 1
##    LOCATE row, 41 - LEN(Text$) / 2
##    PRINT Text$



###==============================================================================
###SUB Rotate (xa, ya, za)
###==============================================================================
### TODO remove this function -- we can handle transformations (and also projection) with pymkfgame
##def Rotate(xa, ya, za):
##    # This is a janky matrix multiplication hack. This is x rotation, then y rotation, then z rotation (multiplied out by hand and written as the composed formula)
##    FOR n = 1 TO NumPts
##        ax = (coss(ya) * coss(za))
##        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
##        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
##        
##        bx = (coss(ya) * sinn(za))
##        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
##        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
##        
##        cx = (-sinn(ya))
##        cy = (sinn(xa) * coss(ya))
##        cz = (coss(xa) * coss(ya))
##        
##        OutPts(n).x = ((InPts(n).x * ax) + (InPts(n).y * ay) + InPts(n).z * az)
##        OutPts(n).y = ((InPts(n).x * bx) + (InPts(n).y * by) + InPts(n).z * bz)
##        OutPts(n).z = ((InPts(n).x * cx) + (InPts(n).y * cy) + InPts(n).z * cz)
##        
##        Pts2D(n).x = 640 - (lScale * (OutPts(n).x / (OutPts(n).z + lz)) + lx)
##        Pts2D(n).y = lScale * (OutPts(n).y / (OutPts(n).z + lz)) + ly
##        
##    NEXT n
##
##END SUB
##
###==============================================================================
###SUB RotateBar (xa, ya, za)
###==============================================================================
### TODO remove this function -- we can handle transformations (and also projection) with pymkfgame
##def RotateBar(xa, ya, za):
##    FOR n = 1 TO NumPtsH
##        ax = (coss(ya) * coss(za))
##        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
##        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
##        
##        bx = (coss(ya) * sinn(za))
##        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
##        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
##        
##        cx = (-sinn(ya))
##        cy = (sinn(xa) * coss(ya))
##        cz = (coss(xa) * coss(ya))
##        
##        BarOutPts(n).x = ((BarInPts(n).x * ax) + (BarInPts(n).y * ay) + BarInPts(n).z * az)
##        BarOutPts(n).y = ((BarInPts(n).x * bx) + (BarInPts(n).y * by) + BarInPts(n).z * bz)
##        BarOutPts(n).z = ((BarInPts(n).x * cx) + (BarInPts(n).y * cy) + BarInPts(n).z * cz)
##        
##        BarPts2D(n).x = Scale * (BarOutPts(n).x / (BarOutPts(n).z + z)) + x
##        BarPts2D(n).y = Scale * (BarOutPts(n).y / (BarOutPts(n).z + z)) + y
##        
##    NEXT n
##
##END SUB
##
###==============================================================================
###SUB RotateBike (xa, ya, za)
###==============================================================================
### TODO remove this function -- we can handle transformations (and also projection) with pymkfgame
##def RotateBike(xa, ya, za):
##    FOR n = 1 TO NumPtsF
##        ax = (coss(ya) * coss(za))
##        ay = (sinn(xa) * sinn(ya) * coss(za)) + (coss(xa) * -sinn(za))
##        az = (coss(xa) * sinn(ya) * coss(za)) + (-sinn(xa) * -sinn(za))
##        
##        bx = (coss(ya) * sinn(za))
##        by = (sinn(xa) * sinn(ya) * sinn(za)) + (coss(xa) * coss(za))
##        bz = (coss(xa) * sinn(ya) * sinn(za)) + (-sinn(xa) * coss(za))
##        
##        cx = (-sinn(ya))
##        cy = (sinn(xa) * coss(ya))
##        cz = (coss(xa) * coss(ya))
##        
##        FrameOutPts(n).x = ((FrameInPts(n).x * ax) + (FrameInPts(n).y * ay) + FrameInPts(n).z * az)
##        FrameOutPts(n).y = ((FrameInPts(n).x * bx) + (FrameInPts(n).y * by) + FrameInPts(n).z * bz)
##        FrameOutPts(n).z = ((FrameInPts(n).x * cx) + (FrameInPts(n).y * cy) + FrameInPts(n).z * cz)
##        
##        BikePts2D(n).x = Scale * (FrameOutPts(n).x / (FrameOutPts(n).z + z)) + x
##        BikePts2D(n).y = Scale * (FrameOutPts(n).y / (FrameOutPts(n).z + z)) + y
##        
##    NEXT n
##    
##END SUB

#===========================================================================================================
# TODO get rid of all this hardcoded crap. At the time you made this game, you didn't know how to do file IO
# All of these data points belong in a file

def main():
    # NOTE: Couldn't decide whether to put pygame.init() at this level or in the GameApplication class. It probably belongs in GameApplication (in an Init()) function of sorts..)
    pygame.init()

    game = GameApplication()
    #game.changeState(game_state_intro.GameStateImpl.Instance())
    game.changeState(game_state_main_menu.GameStateImpl.Instance())

    # NOTE timer should be part of application class, too, but this is hack'n'slash.. No time to fix it!!
    prev_time = pygame.time.get_ticks()

    while game.isRunning:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time

        # ----- Process events
        game.processEvents()

        # ----- Process commands
        game.processCommands()

        # ----- Update stuff
        game.update(dt_s)

        # ----- pre-render 
        game.preRenderScene()

        # ----- Draw stuff
        game.renderScene()

        # ----- post-render (e.g. score/overlays)
        game.postRenderScene()

    # Do any engine cleanup here

    # TODO Treat game states here the same way you did in Falldown x64 - they can be "functions" in this file, but each game_state should have its own event handler, input processor, etc
    #MainMenu()



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main()

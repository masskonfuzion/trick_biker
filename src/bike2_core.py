""" This module contains code from the original bike2 game, which is essential to the game, but for which I haven't decided whether to bake into the engine or lump together as one module or as separate modules.
"""
import json
import pygame
import os
import sys
import logging
import math
from pymkfgame.mkfmath import matrix
from pymkfgame.mkfmath import vector
from pymkfgame.mkfmath.common import DEGTORAD
from pymkfgame.collision import aabb
from pymkfgame.gameobj.gameobj import GameObj

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
    def __init__(self, x=0.0, y=0.0, incline=0.0, length=0.0, dist=0.0):
        self.x = x
        self.y = y
        self.incline = incline
        self.length = length    #length of ramp
        self.dist = dist        #length of jump (gap), dist btwn up ramp and down ramp

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
class Wireframe(object):
    """ A wireframe model

        NOTE: for 3D object representation, there are better data structures, e.g. polygon/vertex/edge. Consult your Library, and/or the googles

    """
    # TODO probably break the Wireframe class into its own module
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
class Bike(GameObj):
    # NOTE: Remember that GameObj has xyz coords (position), and so does Wireframe. Make sure to keep them synchronized
    # TODO probably break Bike class into its own module
    # TODO add a draw() function, which should draw the bike's model
    def __init__(self):
        self.model = Wireframe()
        self.aabb = aabb.AABB()
        self.colors = []    # a list of ColorType objects, f.k.a. BikeCol (to be set by InitBike())
        self.style = 0      # TODO: consider replacing with a BikeStyle object (right now, style is an int, which dictates which of a predefined set of styles the bike could have)
        self.scale = 1.0
        self.position = Point3D()   # Note that we're using Point3D for bike's position, even though GameObj has a position.. Revisit this
        self.velocity = vector.Vector()
        self.gamestatsRef = None    # A reference to the game engine's gamestats object
        self.mmRef = None           # A reference to the game engine's message manager

        self.crashed = False
        self.inAir = False
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

        self.model.children['frame'] = Wireframe()
        #self.model.children['frame'].position = Point3D(-11,0,0) # Displacement from local origin
        for item in raw_bike_model['frame_point_data']:
            pt = Point3D( item[0], item[1], item[2])
            self.model.children['frame'].addPoint(pt)
        # Also copy the line data
        self.model.children['frame'].lines.extend(raw_bike_model['frame_line_data'])  # Couldn't also used addLine() by iterating through my line data and calling addLine(), one by one

        # Now, do the handlebar
        self.model.children['handlebar'] = Wireframe()
        for item in raw_bike_model['handlebar_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['handlebar'].addPoint(pt)
        self.model.children['handlebar'].lines.extend(raw_bike_model['handlebar_line_data'])

        # Rear tire
        self.model.children['frame'].children['wheel'] = Wireframe()
        self.model.children['frame'].children['wheel'].position = Point3D(-22,-5,0)
        for item in raw_bike_model['wheel_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['frame'].children['wheel'].addPoint(pt)
        self.model.children['frame'].children['wheel'].lines.extend(raw_bike_model['wheel_line_data'])

        # Front tire
        self.model.children['handlebar'].children['wheel'] = Wireframe()
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
        ##    READ self.gamestatsRef.trickPointValue(n)
        ##    self.gamestatsRef.timesUsed[n] = 0
        ##NEXT n

    def update(self, dt_s):
        # TODO add setting of transformations
        TODO = 1000
        self.updateTransform(dt_s)
        self.aabb.computeBounds(self.model) # TODO see aabb module for thoughts on computeBounds() vs update()
        self.updateTrick( TODO )    # Make sure updateTrick cals the proper functions to set the bike's transform

    def draw(self, screen):
        self.model.draw(screen)
        self.aabb.draw(screen)  # For debuggind

    #==============================================================================
    #SUB Move
    #==============================================================================
    # TODO move this into a bike update function
    def updateTransform(self, dt_s):
        # Compose rotation matrices in this order (in the code) ZYX, which will be applied as X, then Y, then Z (because the engine post-multiplies
        matCompose = matrix.mMultmat( matrix.Matrix.matRotZ(self.model.thz * DEGTORAD), matrix.Matrix.matRotY(self.model.thy * DEGTORAD) )
        self.model.matRot = matrix.mMultmat( matCompose, matrix.Matrix.matRotX(self.model.thx * DEGTORAD) )


        # TODO split out the in-air rotation from translation
        if self.inAir:
            if not self.tricking :
                self.model.children['frame'].thz = self.model.children['frame'].thz + 3
                self.model.children['handlebar'].thz = self.model.children['frame'].thz    # If we're in the air, and not tricking, then we're slightly rotating   # TODO fix the angle references here. should be members of this class
            
            # TODO fix gravity (well.. do a real gravity calculation.. this is hackery)
            self.position[1] = self.position[1] + Biker.yvel
            Biker.yvel = Biker.yvel + 2.1   # The 2.1 here is some arbitrary constant found, probably, by experimentation

        self.model.matTrans = matrix.Matrix.matTrans(self.model.position.x, self.model.position.y, self.model.position.z)

        # TODO also do physics/friction/deceleration
  

    #==============================================================================
    #SUB DoTrick (n)
    #Execute tricks
    #==============================================================================
    # TODO any call to updateTrick should be made from the bike's update() function
    def updateTrick(self, n):
        if n == 1:               #360 degree turn
            self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + (Biker.turn * 1) / 1.5
            self.model.children['frame'].thy = self.model.children['frame'].thy + (Biker.turn * 1) / 1.5
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
            if self.model.children['frame'].thy % 360 == 0: # TODO for all modulo math, make sure we're properly testing against 0 or whatever number (make sure your ints are good)
                self.tricking = 0
                self.gamestatsRef.trickMsg = "360 Turn!!!"
        
        elif n == 2:               #Tailwhip
            self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
            if self.model.children['frame'].thy % 360 == 0:
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Tailwhip!!!"
        
        elif n == 3:               #180 degree barturn
            if self.trickPhase == 1:
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn
            if self.trickPhase == 6:
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy - Biker.turn
         
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
         
            if self.model.children['handlebar'].thy % 90 == 0:
                self.trickPhase = self.trickPhase + 1
            if self.model.children['handlebar'].thy == MemAngle: # TODO MemAngle used to be a global var.. Fix this!
                self.tricking = 0
                MemAngle = 0
                self.trickPhase = 1
                self.gamestatsRef.trickMsg = "X-Up!!!"
        
        elif n == 4:               #360 degree barspin
            self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn
            if self.model.children['handlebar'].thy % 360 == 0:
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Barspin!!!"

            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
        
        elif n == 5:               #Backflip
            tfactor = 5 / 2
            self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn / tfactor
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - Biker.turn / tfactor
            if self.model.children['frame'].thz <= MemAngle - 330:
                self.tricking = 0
                MemAngle = 0
                self.gamestatsRef.trickMsg = "Backflip!!!"
        
        elif n == 6:               #Inverted 180
            tfactor = 5 / 2 #either 2 or 5/2
            self.model.children['frame'].thx = self.model.children['frame'].thx + Biker.turn / tfactor
            self.model.children['handlebar'].thx = self.model.children['handlebar'].thx + Biker.turn / tfactor
    
            self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn / tfactor
            self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn / tfactor
    
            self.model.children['frame'].thz = self.model.children['frame'].thz + 2
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 2
    
            if self.model.children['frame'].thx % 360 == 0 :
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Inverted 180!!!"
        
        elif n == 7:           #Corkscrew (don't try this at home)
            self.model.children['frame'].thx = self.model.children['frame'].thx + Biker.turn / 2
            self.model.children['handlebar'].thx = self.model.children['handlebar'].thx + Biker.turn / 2
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
        
            if self.model.children['frame'].thx % 360 == 0:
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Corkscrew!!!"
        
        elif n == 8:           #Double Barspin Tailwhip
            self.model.children['frame'].thy = self.model.children['frame'].thy - Biker.turn
            self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn * 2
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
        
            if self.model.children['frame'].thy % 360 == 0:
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Double Barspin/Tailwhip!!!"
        
        elif n == 9:           #Wicked Tabletop
            if self.trickPhase == 1:
                self.model.children['frame'].thx = self.model.children['frame'].thx + Biker.turn / 2
                self.model.children['handlebar'].thx = self.model.children['handlebar'].thx + Biker.turn / 2

            if self.trickPhase == 5:
                self.model.children['frame'].thx = self.model.children['frame'].thx - Biker.turn / 2
                self.model.children['handlebar'].thx = self.model.children['handlebar'].thx - Biker.turn / 2
         
            self.model.children['frame'].thz = self.model.children['frame'].thz + 2
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 2
         
            if self.model.children['frame'].thx % 90 == 0:
                self.trickPhase = self.trickPhase + 1
            if self.model.children['frame'].thx % 360 == 0:
                self.tricking = 0
                self.trickPhase = 1
                self.gamestatsRef.trickMsg = "Tabletop!!!"
        
        elif n == 10:        #Twisting Corkscrew
            tfactor = 5 / 2
            self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn / tfactor
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - Biker.turn / tfactor
            self.model.children['frame'].thx = self.model.children['frame'].thx - Biker.turn / tfactor
            self.model.children['handlebar'].thx = self.model.children['handlebar'].thx - Biker.turn / tfactor
                     
            if self.model.children['frame'].thz <= MemAngle - 330 :
                self.model.children['frame'].thx = 0
                self.model.children['handlebar'].thx = 0
                self.tricking = 0
                MemAngle = 0
                self.trickPhase = 1
                self.gamestatsRef.trickMsg = "Twisting Corkscrew!!!"
        
        elif n == 11:            #Backflip Tailwhip
            if self.trickPhase == 1 or self.trickPhase == 2 or self.trickPhase == 3:
                self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn * (1 / 3)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - Biker.turn * (1 / 3)
        
            if self.trickPhase == 1 and self.model.children['frame'].thz <= MemAngle - 90:
                self.trickPhase = 2
        
            if self.trickPhase == 2:
                self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn / (3 / 2)
        
            if self.trickPhase == 2 and self.model.children['frame'].thy % 360 == 0:
                self.trickPhase = 3
        
            if self.model.children['frame'].thz <= MemAngle - 330:
                self.tricking = 0
                MemAngle = 0
                self.trickPhase = 1
                self.gamestatsRef.trickMsg = "Backflip Tailwhip!!!"
             
        elif n == 12:                    #360 turn + 360 barspin
            self.model.children['frame'].thz = self.model.children['frame'].thz + 1
            self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
            if self.trickPhase == 1:
                self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn / 2
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn / 2

            if self.trickPhase == 2:
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy - Biker.turn

            if self.trickPhase == 3: 
                self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn / 2
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy - Biker.turn
        
            if self.trickPhase == 1 and self.model.children['frame'].thy % 180 == 0:
                self.trickPhase = 2
            if self.trickPhase == 2 and self.model.children['handlebar'].thy % 360 == 0:
                self.trickPhase = 3
            if self.trickPhase == 3 and self.model.children['frame'].thy % 360 == 0:
                self.tricking = 0
                self.trickPhase = 1
                self.gamestatsRef.trickMsg = "360 Turn + Barspin!!!"
        
        elif n == 13:                        #Air Endo
            if self.trickPhase == 1:
                self.model.children['frame'].thz = self.model.children['frame'].thz + Biker.turn * (1 / 4)
                self.model.children['handlebar'].thz = self.model.children['frame'].thz

            if self.trickPhase > 4:
                self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn * (1 / 4)
                self.model.children['handlebar'].thz = self.model.children['frame'].thz
        
            if self.model.children['frame'].thz >= MemAngle + 60:
                self.trickPhase = self.trickPhase + 1

            if self.trickPhase > 4 and self.model.children['frame'].thz <= MemAngle + 30:
                self.tricking = 0
                self.trickPhase = 1
                MemAngle = 0
                self.gamestatsRef.trickMsg = "Air Endo!!!"
        
        elif n == 14:                        #Air Endo plus bar twist
            if self.trickPhase == 1:
                self.model.children['frame'].thz = self.model.children['frame'].thz + Biker.turn * (1 / 4)
                self.model.children['handlebar'].thz = self.model.children['frame'].thz
            
            if self.trickPhase == 1 and self.model.children['frame'].thz >= MemAngle + 60:
                self.trickPhase = 2

            if self.trickPhase == 3 and self.model.children['handlebar'].thy % 360 == 0:
                self.trickPhase = 4
        
            if self.trickPhase == 2:
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy - Biker.turn / 2
            
            if (self.trickPhase == 2 or self.trickPhase == 3) and self.model.children['handlebar'].thy % 180 == 0:
                self.trickPhase = self.trickPhase + 1
        
            if self.trickPhase == 3:
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + Biker.turn / 2
        
            if self.trickPhase == 4:
                self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn * (1 / 4)
                self.model.children['handlebar'].thz = self.model.children['frame'].thz
            
            if self.trickPhase == 4 and self.model.children['frame'].thz <= MemAngle + 30:
                self.tricking = 0
                self.trickPhase = 1
                MemAngle = 0
                self.gamestatsRef.trickMsg = "Air Endo + Bar Twist!!!"
        
        elif n == 15:                #Turndown
            if self.trickPhase == 1:
                self.model.children['frame'].thy = self.model.children['frame'].thy - Biker.turn * (1 / 2)
                self.model.children['frame'].thz = self.model.children['frame'].thz + Biker.turn * (1 / 2)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + Biker.turn * (1 / 2)
            
            if self.model.children['frame'].thy % 90 == 0:
                self.trickPhase = self.trickPhase + 1
        
            if self.trickPhase == 6:
                self.model.children['frame'].thy = self.model.children['frame'].thy + Biker.turn * (1 / 2)
                self.model.children['frame'].thz = self.model.children['frame'].thz - Biker.turn * (1 / 2)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - Biker.turn * (1 / 2)
        
            if self.trickPhase == 6 and self.model.children['frame'].thy % 360 == 0:
                self.model.children['frame'].thz = self.model.children['frame'].thz + 30
                self.model.children['handlebar'].thz = self.model.children['frame'].thz
                self.trickPhase = 1
                self.tricking = 0
                self.gamestatsRef.trickMsg = "Turndown!!!"
        
            #self.model.children['frame'].thz = 80: self.model.children['frame'].thx = 0
            #self.model.children['handlebar'].thy = 0: self.model.children['handlebar'].thz = self.model.children['frame'].thz: self.model.children['handlebar'].thx = 0
        
        elif n == 16:            #Flair
            if self.trickPhase == 1: #or self.trickPhase == 3
                self.model.children['frame'].thz = self.model.children['frame'].thz - (Biker.turn * .4)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - (Biker.turn * .4)
        
            if self.trickPhase == 3:
                self.model.children['frame'].thz = self.model.children['frame'].thz - (Biker.turn * .5)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - (Biker.turn * .5)
        
            if self.trickPhase == 1 and self.model.children['frame'].thz <= MemAngle - 135:
                self.trickPhase = 2
        
            if self.trickPhase == 2:
                self.model.children['frame'].thz = self.model.children['frame'].thz - (Biker.turn * .25)
                self.model.children['handlebar'].thz = self.model.children['handlebar'].thz - (Biker.turn * .25)
        
                self.model.children['frame'].thy = self.model.children['frame'].thy + (Biker.turn * .5)
                self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + (Biker.turn * .5)
        
            if self.trickPhase == 2 and self.model.children['frame'].thy % 360 == 0:
                self.trickPhase = 3
        
            if self.trickPhase == 3 and self.model.children['frame'].thz <= MemAngle - 330:
                self.tricking = 0
                self.trickPhase = 1
                MemAngle = 0
                self.gamestatsRef.trickMsg = "Flair!!!"
        

        if self.tricking == 0 :
            # TODO QBASIC was 1-based; Make sure all your list indices and what not have the correct number base (case in point: self.gamestatsRef.addscore
            self.gamestatsRef.addScore = int(self.gamestatsRef.addScore + self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick] - ((self.gamestatsRef.factor * self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick]) * self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick]))    # TODO fix. All of this stuff is going to fail (these are QBASIC arrays; you need Python)
            if self.gamestatsRef.addScore <= 0:
                self.gamestatsRef.addScore = 1
            self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick] += 1
            self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " - " + str(self.gamestatsRef.addScore) + " pts. "   # Note: we could use better Python string processing here.. we're just duplicating the QBASIC way
            if self.gamestatsRef.numTricks > 1:
                self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " " + str(self.gamestatsRef.numTricks) + " TRICK COMBO!!!"
            self.gamestatsRef.runReport.append(self.gamestatsRef.trickMsg)

            #self.mmRef.setMessage(self.gamestatsRef.trickMsg, [ 400, 300 ], (192, 64, 64), 5 )  # TODO reinstate this message. It should be triggered when you land a trick, then expire after a few seconds
        
##Initial trick point values. TODO put this into a class maybe?
##TrickPointData:
##DATA 16       : #Total # of tricks
##DATA 100      : #Point worth of trick 1
##DATA 150      : #Point worth of trick 2
##DATA 125
##DATA 150
##DATA 250
##DATA 350
##DATA 200
##DATA 175
##DATA 200
##DATA 300
##DATA 330
##DATA 375
##DATA 75
##DATA 200
##DATA 100
##DATA 275

        #TODO: Delete SloMo?
        #if SloMo:
        #    FOR l = 1 TO 50
        #        WAIT &H3DA, 8
        #    NEXT l
        #END IF

    
#==============================================================================
class LevelManager(object):
    # TODO make LevelManager its own module, probably
    def __init__(self):
        self.currentLevel = 0
        self.levelFinished = False
        self.finalLevel = 0     # Initialize final level when loading level data or something
        self.curRamp = 0

        self.numRamps = 0
        self.y_ground = 325

        self.ramps = []
        self.scoreToBeat = 0

        # TODO probably add some functions to set currentLevel? Or otherwise manipulate directly from wherever..
        pass


    #==============================================================================
    #SUB InitLevel (self.currentLevel)
    #==============================================================================
    def InitLevel():
        # TODO perhaps move levels into text files? Or perhaps into a separate module?
        # TODO convert to file i/o. Score-to-beat stuff should belong in a level object, perhaps
        # TODO also, watch out for QBASIC 1-based stuff.. you were an amateur when you made this
        # TODO also, convert InitLevel to Python

        del self.ramgs[:]

        Scale = 120         	    # Scale is used in Rotate functions. May need to substitute a camera class?
        self.levelFinished = False  # self.levelFinished belongs in a game stats class or a level manager
        self.curRamp = 1         	# The current ramp in the level (this probably won't be necessary once we have legit collision detection
        #NumTricks = 0       	    # Tracks how many tricks the player has performed (belongs in game stats class) # TODO probably delete this line
        #TrickCounter = 0    	    # Hmm, not sure how this differs from NumTricks. TODO read the code             # TODO probably delete this line
        MsgFrames = 0       	    # Used in messaging (how many frames to leave the message up for)
        msg = ""           		    # Used in messaging - the message text itself
    
    
        # TODO take in a bike obj and set the bike's position (and the bike model's position, which are separate values)
        x = 120                     # Bike position on screen (TODO: Decide. LevelManager probably shouldn't be responsible for this? Or, maybe it should, in which case, InitLevel needs a reference to the bike)
        y = self.y_ground - 20 - 10
        z = -60        			    #z offset: keep this around -50 or -60
    
        # TODO make sure variable scoping is correct. You went through a pass of simply converting loose variables into object-oriented objects/members/etc
        bike.reset()
    
        Biker.xvel = 0
        Biker.yvel = 0
    
        # TODO - populate self.ramps here. Make Pythonic
        if self.currentLevel == 1:
            self.ramps.append( RampType(x=600,y=self.y_ground - 10, incline=45, length=45, dist=220) )
            self.ramps.append( RampType(x=1400, y=self.y_ground - 10, incline=33, length=60, dist=220) )
            self.ramps.append( RampType(x=2200, y=self.y_ground - 10, incline=50, length=30, dist=220) )
            self.scoreToBeat = 1000     #Score to beat for level 1
    
        elif self.currentLevel == 2:
            self.ramps.append( RampType(x=500, y=self.y_ground - 10, incline=30, length=45, dist=200) )
            self.ramps.append( RampType(x=1300, y=self.y_ground - 10, incline=40, length=45, dist=250) )
            self.ramps.append( RampType(x=2100, y=self.y_ground - 10, incline=40, length=40, dist=170) )
            self.ramps.append( RampType(x=2900, y=self.y_ground - 10, incline=30, length=45, dist=220) )
            self.ramps.append( RampType(x=3700, y=self.y_ground - 10, incline=40, length=40, dist=150) )
            self.scoreToBeat = 1350     #Score to beat for level 2
    
        elif self.currentLevel == 3:
            self.ramps.append( RampType(x=540, y=self.y_ground - 10, incline=25, length=35, dist=170) )
            self.ramps.append( RampType(x=1080, y=self.y_ground - 10, incline=35, length=35, dist=170) )
            self.ramps.append( RampType(x=1620, y=self.y_ground - 10, incline=45, length=35, dist=190) )
            self.ramps.append( RampType(x=2160, y=self.y_ground - 10, incline=50, length=35, dist=210) )
            self.scoreToBeat = 1250
    
        elif self.currentLevel == 4:
            self.ramps.append( RampType(x=600, y=self.y_ground - 10, incline=45, length=35, dist=200) )
            self.ramps.append( RampType(x=1200, y=self.y_ground - 10, incline=45, length=35, dist=200) )
            self.ramps.append( RampType(x=1800, y=self.y_ground - 10, incline=45, length=35, dist=200) )
            self.ramps.append( RampType(x=2400, y=self.y_ground - 10, incline=35, length=35, dist=200) )
            self.scoreToBeat = 1500
    
        elif self.currentLevel == 5:
            self.ramps.append( RampType(x=600, y=self.y_ground - 10, incline=35, length=35, dist=200) )
            self.ramps.append( RampType(x=1200, y=self.y_ground - 10, incline=40, length=35, dist=200) )
            self.ramps.append( RampType(x=1800, y=self.y_ground - 10, incline=35, length=35, dist=200) )
            self.ramps.append( RampType(x=2400, y=self.y_ground - 10, incline=40, length=35, dist=200) )
            self.ramps.append( RampType(x=3000, y=self.y_ground - 10, incline=35, length=35, dist=200) )
            self.ramps.append( RampType(x=3600, y=self.y_ground - 10, incline=35, length=35, dist=200) )
            self.scoreToBeat = 1900
    
        elif self.currentLevel == 6:
            self.ramps.append( RampType(x=600, y=self.y_ground - 10, incline=55, length=35, dist=220) )
            self.ramps.append( RampType(x=1200, y=self.y_ground - 10, incline=55, length=35, dist=220) )
            self.scoreToBeat = 1000
    
    def update(dt_s, bike):
        """ Update the level manager (e.g., things like curRamp and such)

            Note: This takes in the bike object so it can know the bike's position and track current ramp, and such.
            To be more general, this function can maybe take in a dict of gameobjects
        """
        # TODO decide -- do we want LevelManager to have an update function? Or do we want to 'manually' update the level by calling checkRamp from the game loop?
        pass

    #==============================================================================
    #SUB drawLevel
    #
    #==============================================================================
    def drawLevel(self, screen):
        #TODO: Make this function take in a parameter. The parameter should be a Level object. The level should contain a list of ramps, and whatever else
        for n in range(0, len(self.ramps)):
            sx = self.ramps[n].x
            sy = self.ramps[n].y
    
            ex = self.ramps[n].x + self.ramps[n].length * coss(360 - self.ramps[n].incline)
            ex2 = self.ramps[n].x + self.ramps[n].length * coss(self.ramps[n].incline)
            if n > 1:
                ex22 = Ramp(n - 1).x + os + Ramp(n - 1).dist
                ex22 = ex22 + Ramp(n - 1).length * coss(Ramp(n - 1).incline)
            ey = self.ramps[n].y + self.ramps[n].length * sinn(360 - self.ramps[n].incline)
    
            if Track3D:
                tw = 44         #track width (an offset to give the illusion of 3D)
                os = -5         #3d illusion offset
            else:
                tw = 0
                os = 0
    
            if n == 1:
                pygame.draw.line(screen, (192, 192, 192), (0, self.y_ground - 10 - tw), (self.ramps[n].x, self.y_ground - 10 - tw))
                pygame.draw.line(screen, (192, 192, 192), (0, self.y_ground - 10 + tw), (self.ramps[n].x + os, self.y_ground - 10 + tw))

            else:
                pygame.draw.line(screen, (192, 192, 192), (ex22, self.y_ground - 10 - tw), (self.ramps[n].x, self.y_ground - 10 - tw)) 
                pygame.draw.line(screen, (192, 192, 192), (ex22 + os, self.y_ground - 10 + tw), (self.ramps[n].x + os, self.y_ground - 10 + tw))

                if n == self.levelMgr.numRamps:
                    pygame.draw.line(screen, (192, 192, 192), (ex2 + self.ramps[n].dist, self.y_ground - 10 - tw), (639, self.y_ground - 10 - tw))
                    pygame.draw.line(screen, (192, 192, 192), (ex2 + self.ramps[n].dist, self.y_ground - 10 + tw), (639, self.y_ground - 10 + tw))
    
            pygame.draw.line(screen, (192, 192, 192), (sx + os, sy + tw), (ex + os, ey + tw))
            pygame.draw.line(screen, (192, 192, 192), (sx + os + self.ramps[n].dist, ey + tw), (ex2 + os + self.ramps[n].dist, sy + tw))
    
            pygame.draw.line(screen, (192, 192, 192), (sx, sy - tw), (ex, ey - tw))
            pygame.draw.line(screen, (192, 192, 192), (sx + self.ramps[n].dist, ey - tw), (ex2 + self.ramps[n].dist, sy - tw))
    
            pygame.draw.line(screen, (192, 192, 192), (sx + os, sy + tw), (sx, sy - tw))
            pygame.draw.line(screen, (192, 192, 192), (ex + os, ey + tw), (ex, ey - tw))
            pygame.draw.line(screen, (192, 192, 192), (sx + os + self.ramps[n].dist, ey + tw), (sx + self.ramps[n].dist, ey - tw))
            pygame.draw.line(screen, (192, 192, 192), (ex2 + os + self.ramps[n].dist, sy + tw), (ex2 + self.ramps[n].dist, sy - tw))
    
            #PAINT (sx, sy), 6, 15
            #PAINT (ex2 + self.ramps[n].dist - 2, ey), 6, 15
    
            #CIRCLE (sx, sy), 4, 4
    

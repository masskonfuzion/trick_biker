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
from pymkfgame.mkfmath.common import DEGTORAD, coss, sinn, EPSILON, floatEq
from pymkfgame.collision import aabb
from pymkfgame.gameobj.gameobj import GameObj

###==============================================================================
##class World(object):
##    ''' A "world" class for physics. '''
##    def __init__(self):
##        self.gravity = Vector()
##
##    def setGravity(self, x, y, z):
##        self.gravity[0] = x;
##        self.gravity[1] = y;
##        self.gravity[2] = z;

#==============================================================================
class AngularVelocity(object):
    ''' A class to track the angular velocity of the wheels.
    
        This is a total hack. In the game, it only considers angular velocity caused by
        the bike moving along the X-Z plane. In a bigger, better game, we would use rigid body physics.
    '''
    def __init__(self, friction=0.05):
        self.angVel = 0.0
        self.angle = 0.0
        self.friction = friction    # A damping factor to slow the wheel's rotation down when it's free-rolling (i.e. not touching the ground)
        self.radius = 0.0   # NOTE! Make sure to set the radius!

    def setAngVelFromLinearVel(self, linearVel, dt_s=1.0):
        ''' Compute angular velocity of the wheel, given a linear velocity of the bike. Set this AngularVelocity object's angular velocity

            NOTE: This is not a general solution; it is specific. This function assumes that the bike
            is traveling along x axis only, and has only 1 component in its velocity vector
        '''
        # The angle swept by a point on the circle is ratio of the distance traveled to the circumference of the
        # circle (I think.. I'm doing this in my head.. I could look it up, but... what fun would that be?
        # This function also is a super-simplified calculation
        self.angVel = ( linearVel / (2.0 * math.pi * self.radius) ) * dt_s

    def updateAngle(self):
        self.angle = (self.angle + self.angVel) % 360.0
        

#==============================================================================
class Point3D(object):
    def __init__(self, px=0.0, py=0.0, pz=0.0):
        #self.v = [0.0, 0.0, 0.0] # TODO perhaps use a list, rather than 3 floats.
        self.x = px
        self.y = py
        self.z = pz

    def __str__(self):
        return "[ {}, {}, {} ]".format(self.x, self.y, self.z)

    def __repr__(self):
        return "Point3D({}, {}, {})".format(self.x, self.y, self.z)

    def __getitem__(self, index):
        ## accessor
        # TODO rework this Point3D class. You were taking shortcuts to get a quick demo running. But you should make this class use a list as its underlying data structure; and then write an access that returns an item from the array
        # TODO perhaps Point3D should default to w = 1.0, where Vector defaults to w = 0.0. Otherwise, maybe get rid of Point3D entirely, and only use Vectors?
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z


    def __setitem__(self, index, value):
        # NOTE: This is hackeration and is kinda ugly. But it works (unless you give bad input, e.g., an index < 0 or index > 2
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)


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
        

# TODO convert haphazard tricks to use Trick objects
#==============================================================================
class Trick(object):
    def __init__(self):
        self.trickPhases = []

#==============================================================================
class TrickPhase(object):
    def __init__(self):
        self.actions = []   # A list of SIMULTANEOUS actions (e.g. handlebar spin, frame rotate).. TODO come up with a syntax for defining trickphases
        self.trigger = None # A trigger to tell when the current trickPhase is over

#==============================================================================
class Wireframe(object):
    """ A wireframe model

        NOTE: for 3D object representation, there are better data structures, e.g. polygon/vertex/edge. Consult your Library, and/or the googles

    """
    # TODO probably break the Wireframe class into its own module
    # TODO maybe make Wireframe derive from a Drawable class, which contains the transformation matrices
    def __init__(self):
        self.position = Point3D()
        self.points = []        # these are the actual model points
        self._xpoints = []      # these are the transformed points; recomputed every frame, based on transformations
        self.lines = []     # Store points maybe as list objects
        self.thx = 0.0  # Euler angles; used for computing rotations
        self.thy = 0.0
        self.thz = 0.0
        self.matTrans = matrix.Matrix()
        self.matRot = matrix.Matrix()
        self.children = {}  # A dict of sub-objects (e.g., bike is a composite obj, containing a frame model and handlebars model
        self.collisionGeom = None

    def addPoint(self, point):
        """ Take in a Point3D object. Append the point object to self.points """
        # TODO maybe make it possible to clear the points list?
        self.points.append(point)

    def addLine(self, line):
        """ Take in a LineType object. Append the line object to self.lines """
        self.lines.append(line)

    def draw(self, render_surface, obj_ref=None, matView=matrix.Matrix.matIdent(), matViewport=matrix.Matrix.matIdent()):
        """ Recursively draw objects """
        # TODO add a view transform parameter to all draw functions? (Maybe add it to the gameobj base class or whatever?)
        if obj_ref is None:
            obj_ref = self

        if obj_ref.children:
            for _, child_obj in obj_ref.children.iteritems():
                self.draw(render_surface, child_obj, matView, matViewport)

        # Compute model points/vertices (well, right now, it's points..) transformed by view matrix # TODO! Also do this when drawing the track
        xpoints_viewport = []
        for xpoint_model in obj_ref._xpoints:
            #import pdb; pdb.set_trace()
            # Apply the view matrix and perspective division
            p = matrix.mMultvec(matView, vector.Vector(xpoint_model[0], xpoint_model[1], xpoint_model[2], 1.0)) # TODO btw, standardize - use Point3D, which should include homogeneous coord; or don't. But don't waste time converting types

            #print "model: ({:3f}, {:3f}, {:3f}, {:3f}) -> modelview: ({:3f}, {:3f}, {:3f}, {:3f})".format(xpoint_model.x, xpoint_model.y, xpoint_model.z, 1.0, p.x, p.y, p.z, p.w)

            vp = matrix.mMultvec(matViewport, p)    # NOTE ideally, we could work in-place on these points/vertices

            xpoints_viewport.append( Point3D(vp.x, vp.y, vp.z)  )  # Not sure if it matters that we force xpoints_viewport to be a Point3D, but we do it because we made model._xpoints a Point3D
            #print "modelview: ({:3f}, {:3f}, {:3f}, {:3f}) -> viewport: ({:3f}, {:3f}, {:3f}, {:3f})".format(p.x, p.y, p.z, p.w, vp.x, vp.y, vp.z, vp.w)
            
        for lineData in obj_ref.lines:
            startPt = lineData[0] - 1   # subtract 1 because we programmed this game in QBASIC with base = 1, not 0
            endPt = lineData[1] - 1

            #import pdb; pdb.set_trace()

            # Note; for now, we're ignoring z; we only care to test out the frame drawing in 2D
            spCoords = xpoints_viewport[startPt]
            epCoords = xpoints_viewport[endPt]
            #logging.debug("sPt:{} - {}, ePt:{} - {}".format(startPt, spCoords, endPt, epCoords))
            pygame.draw.line(render_surface, (220, 220, 220), (spCoords[0], spCoords[1]), (epCoords[0], epCoords[1]) )

        if obj_ref.collisionGeom:
            # TODO add a debug mode.. we don't ALWAYS want to draw the geom
            obj_ref.collisionGeom.draw(render_surface, matView=matView, matViewport=matViewport)

    def updateModelTransform(self, obj_ref=None, composed_xform=matrix.Matrix.matIdent()):
        ''' Update _xpoints based ONLY on the "model" transforms -- translation and rotation

            This function updates the geometry of the bike, whether or not it is being drawn. This function is
            used for computing where the bike is, in the world, for collision detection, etc.
        '''
        if obj_ref is None:
            obj_ref = self

        obj_ref.matRot = matrix.mMultmat( matrix.Matrix.matRotZ(obj_ref.thz * DEGTORAD), matrix.Matrix.matRotY(obj_ref.thy * DEGTORAD) )
        obj_ref.matRot = matrix.mMultmat( obj_ref.matRot, matrix.Matrix.matRotX(obj_ref.thx * DEGTORAD) )
        obj_ref.matTrans = matrix.Matrix.matTrans(obj_ref.position.x, obj_ref.position.y, obj_ref.position.z)

        # Note: we postmult trans 1st and rot 2nd because the transform are applied right-to-left. e.g.,
        # M = TRv, where T is translate, R is rot, and v is the vector. R is applied 1st, because it's closest to v
        ##local_composed_xform = matrix.mMultmat(composed_xform, obj_ref.matTrans)
        ##local_composed_xform = matrix.mMultmat(local_composed_xform, obj_ref.matRot)

        local_composed_xform = matrix.mMultmat(composed_xform, obj_ref.matTrans)
        local_composed_xform = matrix.mMultmat(local_composed_xform, obj_ref.matRot)

        #print "Child objects:{}".format(obj_ref.children)
        if obj_ref.children:
            for _, child_obj in obj_ref.children.iteritems():
                self.updateModelTransform(child_obj, local_composed_xform)

        # if no children, then compute final transformation matrix and render
        del obj_ref._xpoints[:]

        for point in obj_ref.points:
            p = matrix.mMultvec(local_composed_xform, vector.Vector(point.x, point.y, point.z, 1.0))  # Use a vector, as required by pymkfmath's matrix multiplication api (and don't forget to set homogeneous coord to 1
            #print "{}: point ({}, {}, {}) -> _xpoint ({}, {}, {})".format(obj_ref, point.x, point.y, point.z, p.x, p.y, p.z)
            obj_ref._xpoints.append(Point3D(p.x, p.y, p.z))     # Then convert back to Point3D to comply with the original code for this game (TODO make some synergies between Point3D and Vector)
            # TODO optimize some stuff. Here, you construct Vectors for matrix mult, but then you construct Point3Ds. You do the same thing again in draw().. wasteful
        obj_ref.collisionGeom.computeBounds(obj_ref)    # TODO give collision geoms ability to recompute bounds without passing in an object all the time? maybe give the geom a reference to the object it's bounding

        # TODO delete these debugging lines
        #print "obj_ref id {}: xpoints: {}".format(id(obj_ref), obj_ref._xpoints)
        #print "AABB id {}: {}".format(id(obj_ref.collisionGeom), obj_ref.collisionGeom)
        #print "-" * 40

    def resetModelTransform(self, obj_ref=None):
        ''' Recursively reset all models' Euler orientation to 0 degrees '''
        if obj_ref is None:
            obj_ref = self

        self.thx = 0.0
        self.thy = 0.0
        self.thz = 0.0

        if obj_ref.children:
            for _, child_obj in obj_ref.children.iteritems():
                self.resetModelTransform(child_obj)


    # TODO probably want to generalize the calls to store/get transformed points/lines/etc from the models. Conceivably, we would want to get multiple instances of the data, possibly returned from a func, rather than stored in class member data

#==============================================================================
class Bike(GameObj):
    # NOTE: Remember that GameObj has xyz coords (position), and so does Wireframe. Make sure to keep them synchronized
    # TODO probably break Bike class into its own module
    # TODO Add a dict of AngularVelocity objs to this object; one for front wheel, one for rear. Use them to update wheel transformations when doing bike.update()
    def __init__(self):
        super(Bike, self).__init__()

        self.model = Wireframe()
        self.model.collisionGeom = aabb.AABB()
        self.colors = []    # a list of ColorType objects, f.k.a. BikeCol (to be set by InitBike())
        self.wheelAngVel = { 'handlebar': AngularVelocity()
                           , 'frame': AngularVelocity()
                           }
        self.style = 0      # TODO: consider replacing with a BikeStyle object (right now, style is an int, which dictates which of a predefined set of styles the bike could have)
        self.scale = 1.0
        #self.position = Point3D()   # Note that we're using Point3D for bike's position, even though GameObj has a position.. Revisit this     # TODO delete this
        #self.velocity = vector.Vector()  # TODO note that Bike is a gameobj, which has _position, _velocity, and _acceleration. Here you're defining a new position, and all that.
        self.gamestatsRef = None    # A reference to the game engine's gamestats object
        self.mmRef = None           # A reference to the game engine's message manager
        self.levelMgrRef = None     # A reference to the game engine's level manager (We can probably do better than assigning all of these references. Maybe give a reference to the game engine itself, and one to the gamestate)
        self.rider = RiderType()    # rider replaced Biker from the QBASIC game

        self.crashed = False
        self.inAir = False
        self.tricking = False       # TODO make sure to keep tricking data type consistent. It's bool here, int elsewhere
        self.trickPhase = 1
        self.memAngle = 0

    def Init(self):
        """ Initialize bike object
        
            NOTE: This replaces QBASIC InitBike()
        """
        # TODO clean up Init(). There should be a separate model loading that occurs when the Bike object is created, but not every time the bike is reset (e.g. when it crash-lands)
        dirname = os.path.dirname( sys.argv[0] )
        #print "dirname:{}".format("/".join((dirname, "../data/bike_model.json")))
        with open(os.path.normpath("/".join((dirname, "../data/bike_model.json"))), 'r') as fd:
            raw_bike_model = json.load(fd)
        #logging.debug("raw_bike_model:{}".format(raw_bike_model))

        # Construct the bike model
        self._position = vector.Vector(0.0, 0.0, 0.0, 1.0)  # TODO seriously.. either incorporate Point3D into the engine or don't..
        self.model.position = Point3D(0.0, 0.0, 0.0)    # Force a new obj, not simply a ref to self.position (could also write a "copy" function, similar to a copy constructor, but Python doesn't have copy constructors

        self.model.children['frame'] = Wireframe()
        self.model.children['frame'].collisionGeom = aabb.AABB()

        #self.model.children['frame'].position = Point3D(-11,0,0) # Displacement from local origin
        for item in raw_bike_model['frame_point_data']:
            pt = Point3D( item[0], item[1], item[2])
            self.model.children['frame'].addPoint(pt)
        # Also copy the line data
        self.model.children['frame'].collisionGeom.computeBounds(self.model.children['frame'])  # TODO fix the janky function call for the computeBounds calls
        self.model.children['frame'].lines.extend(raw_bike_model['frame_line_data'])  # Could've also used addLine() by iterating through my line data and calling addLine(), one by one

        # Now, do the handlebar
        self.model.children['handlebar'] = Wireframe()
        self.model.children['handlebar'].collisionGeom = aabb.AABB()
        for item in raw_bike_model['handlebar_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['handlebar'].addPoint(pt)
        self.model.children['handlebar'].collisionGeom.computeBounds(self.model.children['handlebar'])  # TODO optimize the computeBounds calls, maybe, by taking in a transformation of the already existing computed bounds? (i.e. calculate once, then simply transform the calculated box?)
        self.model.children['handlebar'].lines.extend(raw_bike_model['handlebar_line_data'])

        # Rear tire
        self.model.children['frame'].children['wheel'] = Wireframe()
        self.model.children['frame'].children['wheel'].collisionGeom = aabb.AABB()
        self.model.children['frame'].children['wheel'].position = Point3D(-22,-5,0)
        for item in raw_bike_model['wheel_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['frame'].children['wheel'].addPoint(pt)
        self.model.children['frame'].children['wheel'].collisionGeom.computeBounds(self.model.children['frame'].children['wheel'])
        self.wheelAngVel['frame'].radius = (self.model.children['frame'].children['wheel'].collisionGeom._maxPt[0] - self.model.children['frame'].children['wheel'].collisionGeom._minPt[0]) / 2.0
        self.model.children['frame'].children['wheel'].lines.extend(raw_bike_model['wheel_line_data'])

        # Front tire
        self.model.children['handlebar'].children['wheel'] = Wireframe()
        self.model.children['handlebar'].children['wheel'].collisionGeom = aabb.AABB()
        self.model.children['handlebar'].children['wheel'].position = Point3D(0,-5,0)

        for item in raw_bike_model['wheel_point_data']:
            pt = Point3D( item[0], item[1], item[2] )
            self.model.children['handlebar'].children['wheel'].addPoint(pt)
        self.model.children['handlebar'].children['wheel'].collisionGeom.computeBounds(self.model.children['handlebar'].children['wheel'])
        self.wheelAngVel['handlebar'].radius = (self.model.children['handlebar'].children['wheel'].collisionGeom._maxPt[0] - self.model.children['frame'].children['wheel'].collisionGeom._minPt[0]) / 2.0
        self.model.children['handlebar'].children['wheel'].lines.extend(raw_bike_model['wheel_line_data'])

        self.model.updateModelTransform()      # This is necessary to compute transformed points, to be able to draw the bike right away

        # TODO: remove duplicate inits. We have these vars in the constructor for reference; they should be managed outside the constructor
        self.crashed = False
        self.inAir = False
        self.tricking = False
        self.trickPhase = 1

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
        ##    READ self.rider.maxspd, self.rider.jump, self.rider.pump, self.rider.turn
        ##NEXT n
        ##
        ### TODO move trick point initialization to be with level initializtion
        ##RESTORE TrickPointData
        ##READ TotNumTricks
        ##FOR n = 1 TO TotNumTricks
        ##    READ self.gamestatsRef.trickPointValue(n)
        ##    self.gamestatsRef.timesUsed[n] = 0
        ##NEXT n

    #==============================================================================
    #SUB Move
    #==============================================================================
    def update(self, dt_s):
        # TODO add setting of transformations
        # TODO do physics integrations. after all integrations are done and what not, then compute matrix transformations and resulting points/etc

        TODO = 1000

        # Start off calculating acceleration due to gravity
        self._acceleration[0] = self.levelMgrRef.gravity[0]
        self._acceleration[1] = self.levelMgrRef.gravity[1]
        self._acceleration[2] = self.levelMgrRef.gravity[2]

        if self.inAir:
            if not self.tricking :
                # If we're in the air, and not tricking, then we're slightly rotating. Update the bike's top-level transform
                self.model.thz = self.model.thz - (30 * dt_s)        # Pitch the nose down by a small angular velocity (to approximate the nose drifting towards the ground when the biker hangs in the air)
                #print self.model.thz
        else:
            self._acceleration = vector.vSub(self._acceleration, self.levelMgrRef.gravity)

        # TODO add any other contributors to acceleration (e.g., the ground, pushing up, negating gravity)
            
        # TODO add gravity, friction, etc. Basically, add simple rigid body physics (if we can consider rigid body physics simple)
        # TODO holy crap, seriously. Fix the weirdness.. gameobj's have _position; Wireframes have position..
        self._position[0] += self._velocity[0] * dt_s
        self._position[1] += self._velocity[1] * dt_s
        self.model.position = Point3D(self._position[0], self._position[1], self._position[2])

        self._velocity[0] += self._acceleration[0] * dt_s
        self._velocity[1] += self._acceleration[1] * dt_s

        # Compute wheel angular velocity from linear velocity (note that linear velocity is already time-scaled, so we don't have to also time-scale the angular velocities
        if self.model.children['handlebar'].children['wheel'].collisionGeom._minPt[1] <= self.levelMgrRef.y_ground:
            self.wheelAngVel['handlebar'].setAngVelFromLinearVel(self._velocity[0])  # Set angular velocity
            self.wheelAngVel['handlebar'].updateAngle()                             # Update angle based on angular velocity
        else:
            pass    # TODO let the wheel free-wheel; use friction?

        self.model.updateModelTransform()  # Translate/rotate the bike (NOTE: this is regular ol' motion; for tricking, see updateTrick)
        self.updateTrick( self.gamestatsRef.activeTrick, dt_s )    # Make sure updateTrick calls the proper functions to set the bike's transform

    def draw(self, screen, matView=matrix.Matrix.matIdent(), matViewport=matrix.Matrix.matIdent()):
        self.model.draw(screen, matView=matView, matViewport=matViewport)

    #==============================================================================
    #SUB DoTrick (n)
    #Execute tricks
    #==============================================================================
    # TODO any call to updateTrick should be made from the bike's update() function
    def updateTrick(self, n, dt_s):
        if self.tricking:
            if n == 1:               #360 degree turn
                # Test zero crossing for angle.  # TODO make this into a general function
                rot_vel = self.rider.turn * dt_s
                self.model.thz += dt_s  # inject some nose angle drift into the equation
                if self.model.thy <= 360.0 and (self.model.thy + rot_vel) > 360.0:  
                    # if current angle < threshold and angular velocity sweeps across threshold in this update
                    self.model.thy = 0.0    # Snap bike model Y rotation angle to 0
                    self.tricking = 0
                    self.gamestatsRef.trickMsg = "360 Turn!!!"
                else:
                    self.model.thy += rot_vel
            
            elif n == 2:               #Tailwhip
                rot_vel = self.rider.turn * dt_s
                self.model.thz += dt_s  # inject some nose angle drift
                if self.model.children['frame'].thy <= 360.0 and (self.model.children['frame'].thy + rot_vel) > 360.0:  
                    self.model.children['frame'].thy = 0.0  # Snap bike frame to 0 Y angle
                    self.tricking = 0
                    self.gamestatsRef.trickMsg = "Tailwhip!!!"
                else:
                    self.model.children['frame'].thy += rot_vel

            
            elif n == 3:               #180 degree barturn -- this is a real X-Up
                # TODO revisit the x-up. I'm not sure if it's working correctly
                rot_vel = self.rider.turn * dt_s
                self.model.thz += dt_s  # inject some nose angle drift
                if self.trickPhase == 1:
                    self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + rot_vel
                    
                    if self.model.children['handlebar'].thy <= 180.0 and (self.model.children['handlebar'].thy + rot_vel) > 180.0:
                        self.trickPhase = 2
                elif self.trickPhase == 2:
                    self.model.children['handlebar'].thy = self.model.children['handlebar'].thy - rot_vel
             
                    if self.model.children['handlebar'].thy >= 0.0 and (self.model.children['handlebar'].thy - rot_vel) < 0.0:
                        self.trickPhase = 3
                        self.model.children['handlebar'].thy = 0.0
                #if self.model.children['handlebar'].thy == self.memAngle:
                elif self.trickPhase == 3:
                    self.tricking = 0
                    #self.model.children['handlebar'].thy = self.memAngle
                    self.model.children['handlebar'].thy = 0.0
                    self.memAngle = 0
                    self.trickPhase = 1
                    self.gamestatsRef.trickMsg = "X-Up!!!"
            
            elif n == 4:               #360 degree barspin
                rot_vel = self.rider.turn * dt_s
                self.model.thz += dt_s  # inject some nose angle drift
                if self.model.children['handlebar'].thy <= 360.0 and self.model.children['handlebar'].thy + rot_vel > 360.0:
                    self.tricking = 0
                    self.gamestatsRef.trickMsg = "Barspin!!!"
                    self.model.children['handlebar'].thy = 0.0
                else:
                    self.model.children['handlebar'].thy += self.rider.turn * dt_s
            
            elif n == 5:               #Backflip
                tfactor = 0.6   # Arbitrary multiplier to slow down rotation rate of backflip
                rot_vel = self.rider.turn * tfactor * dt_s
                if self.model.thz <= self.memAngle - 15 and (self.model.thz + rot_vel) % 360.0 > self.memAngle - 15:
                    self.tricking = 0
                    self.model.thz = self.memAngle - 15
                    self.memAngle = 0
                    self.gamestatsRef.trickMsg = "Backflip!!!"
                else:
                    self.model.thz = (self.model.thz + rot_vel) % 360.0

            
            elif n == 6:               #Inverted 180    # .... isn't this a 360??
                tfactor = 5 / 2 #either 2 or 5/2
                #self.model.children['frame'].thx = self.model.children['frame'].thx + self.rider.turn / tfactor
                #self.model.children['handlebar'].thx = self.model.children['handlebar'].thx + self.rider.turn / tfactor
                rot_vel_x = self.rider.turn * dt_s * .6
                self.model.thx += rot_vel_x
    
                #self.model.children['frame'].thy = self.model.children['frame'].thy + self.rider.turn / tfactor
                #self.model.children['handlebar'].thy = self.model.children['handlebar'].thy + self.rider.turn / tfactor
                rot_vel_y = self.rider.turn * dt_s * .6
                self.model.thy += rot_vel_y
    
                #self.model.children['frame'].thz = self.model.children['frame'].thz + 2
                #self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 2
                rot_vel_z = -self.rider.turn * dt_s * .05
                self.model.thz += rot_vel_z
    
                #if self.model.children['frame'].thx % 360 == 0 :
                if self.model.thx <= 360 and self.model.thx + rot_vel_x > 360.0:
                    self.tricking = 0
                    self.model.thx = 0
                    self.model.thy = 0
                    self.model.thz = 0
                    self.gamestatsRef.trickMsg = "Inverted 180!!!"
            
            elif n == 7:           #Corkscrew (don't try this at home)
                rot_vel_x = self.rider.turn * dt_s
                self.model.thx += rot_vel_x

                #rot_vel_z = self.rider.turn * dt_s
                #self.model.thz + rot_vel_z
            
                if self.model.thx <= 360.0 and self.model.thx + rot_vel_x > 360.0:
                    self.tricking = 0
                    self.model.thx = 0.0
                    self.gamestatsRef.trickMsg = "Corkscrew!!!"
            
            elif n == 8:           #Double Barspin Tailwhip
                rot_vel = self.rider.turn * dt_s
                self.model.children['frame'].thy += rot_vel
                self.model.children['handlebar'].thy -= rot_vel * 2
                #self.model.children['frame'].thz = self.model.children['frame'].thz + 1
                #self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
            
                if self.model.children['frame'].thy <= 360.0 and self.model.children['frame'].thy + rot_vel > 360.0:
                    self.tricking = 0
                    self.model.children['frame'].thy = 0.0
                    self.model.children['handlebar'].thy = 0.0
                    self.gamestatsRef.trickMsg = "Double Barspin/Tailwhip!!!"
            
            elif n == 9:           #Wicked Tabletop
                #rot_vel_z = self.rider.turn * dt_s 
                #self.model.thz += rot_vel_z
             
                if self.trickPhase == 1:
                    rot_vel_x = self.rider.turn * dt_s * 0.5
                    self.model.thx += rot_vel_x

                elif self.trickPhase > 1 and self.trickPhase < 5:
                    rot_vel_x = self.rider.turn * dt_s * 0.5    # Terrible design here... This assignment is necessary to implement the "delay" while holding the tabletop trick in theh air

                elif self.trickPhase == 5:
                    rot_vel_x = -self.rider.turn * dt_s * 0.5
                    self.model.thx += rot_vel_x
             
                    #if self.model.children['frame'].thx % 360 == 0:
                    if self.model.thx >= 0.0 and self.model.thx + rot_vel_x < 0.0:
                        self.tricking = 0
                        self.trickPhase = 1
                        self.model.thx = 0.0
                        self.gamestatsRef.trickMsg = "Tabletop!!!"
            
                #if self.model.children['frame'].thx % 90 == 0:

                if self.model.thx <= 90.0 and self.model.thx + rot_vel_x > 90.0:
                    self.model.thx = 90.0
                    self.trickPhase += 1
                    # TODO make a way to hold a trick for a certain amount of time

            elif n == 10:        #Twisting Corkscrew
                rot_vel = self.rider.turn * dt_s * .6

                self.model.thz += rot_vel
                self.model.thx += rot_vel

                if self.model.thz >= self.memAngle + 330 :
                    self.model.thx = 0.0
                    self.tricking = 0
                    self.memAngle = 0
                    self.trickPhase = 1
                    self.gamestatsRef.trickMsg = "Twisting Corkscrew!!!"
            
            elif n == 11:            #Backflip Tailwhip
                rot_vel_backflip = self.rider.turn * dt_s * .6
                self.model.thz += rot_vel_backflip

                if self.trickPhase == 1 and self.model.thz >= self.memAngle + 90:
                    self.trickPhase = 2
            
                elif self.trickPhase == 2:
                    rot_vel_tailwhip = self.rider.turn * dt_s * .8

                    #print "thy:{}, rot_vel:{}".format(self.model.children['frame'].thy, rot_vel_tailwhip)

                    if self.model.children['frame'].thy <= 360.0 and self.model.children['frame'].thy + rot_vel_tailwhip > 360.0:
                        self.trickPhase = 3
                        self.model.children['frame'].thy = 0.0
                    else:
                        self.model.children['frame'].thy += rot_vel_tailwhip
            
                elif self.trickPhase == 3:
                    if self.model.thz >= self.memAngle + 330:
                        self.tricking = 0
                        self.memAngle = 0
                        self.trickPhase = 1
                        self.gamestatsRef.trickMsg = "Backflip Tailwhip!!!"
                        #self.model.children['frame'].thy = 0.0
                 
            elif n == 12:                    #360 turn + 360 barspin
                #self.model.children['frame'].thz = self.model.children['frame'].thz + 1
                #self.model.children['handlebar'].thz = self.model.children['handlebar'].thz + 1
                
                if self.trickPhase == 1:
                    rot_vel_360 = self.rider.turn * dt_s
                    self.model.thy += rot_vel_360

                    if self.model.thy <= 180 and self.model.thy + rot_vel_360 > 180:
                        self.trickPhase = 2

                if self.trickPhase == 2:
                    rot_vel_barspin = -self.rider.turn * dt_s * 2.0
                    self.model.children['handlebar'].thy += rot_vel_barspin

                    if self.model.children['handlebar'].thy >= -360.0 and self.model.children['handlebar'].thy + rot_vel_barspin < -360.0:
                        self.model.children['handlebar'].thy = 0.0
                        self.trickPhase = 3

                if self.trickPhase == 3: 
                    rot_vel_360 = self.rider.turn * dt_s
                    self.model.thy += rot_vel_360

                    #rot_vel_barspin = -self.rider.turn * dt_s
                    #self.model.children['handlebar'].thy += rot_vel_barspin
            
                    if self.model.thy <= 360.0 and self.model.thy + rot_vel_360 > 360.0:
                        self.tricking = 0
                        self.trickPhase = 1
                        self.model.thy = 0.0
                        self.model.children['handlebar'].thy = 0.0
                        self.gamestatsRef.trickMsg = "360 Turn + Barspin!!!"
            
            elif n == 13:                        #Air Endo
                if self.trickPhase == 1:
                    rot_vel = -self.rider.turn * dt_s * 0.6
                    self.model.thz += rot_vel

                if self.model.thz <= self.memAngle - 60:
                    self.trickPhase = self.trickPhase + 1

                if self.trickPhase > 4:
                    rot_vel = self.rider.turn * dt_s * 0.6
                    self.model.thz += rot_vel

                    if self.model.thz >= self.memAngle - 10:
                        self.tricking = 0
                        self.trickPhase = 1
                        self.memAngle = 0
                        self.gamestatsRef.trickMsg = "Air Endo!!!"

            elif n == 14:                        #Air Endo plus bar twist
                if self.trickPhase == 1:
                    rot_vel = -self.rider.turn * dt_s * 0.6
                    self.model.thz += rot_vel
                
                    if self.model.thz <= self.memAngle - 60:
                        self.trickPhase = 2
                        #print "to trickphase 2"

                elif self.trickPhase == 2:
                    rot_vel = -self.rider.turn * dt_s
                    self.model.children['handlebar'].thy += rot_vel
                    #print self.model.children['handlebar'].thy
                    if self.model.children['handlebar'].thy >= -180.0 and self.model.children['handlebar'].thy + rot_vel < -180.0:
                        self.model.children['handlebar'].thy = -180.0
                        self.trickPhase = 3
                        #print "to trickphase 3"

                elif self.trickPhase == 3:
                    rot_vel = self.rider.turn * dt_s
                    self.model.children['handlebar'].thy += rot_vel
                    if self.model.children['handlebar'].thy <= 0.0 and self.model.children['handlebar'].thy + rot_vel > 0.0:
                        self.model.children['handlebar'].thy = 0.0
                        self.trickPhase = 4
                        #print "to trickphase 4"
            
                elif self.trickPhase == 4:
                    rot_vel = self.rider.turn * dt_s * 0.6
                    self.model.thz += rot_vel
                
                    if self.model.thz >= self.memAngle - 10:
                        self.tricking = 0
                        self.trickPhase = 1
                        self.memAngle = 0
                        self.gamestatsRef.trickMsg = "Air Endo + Bar Twist!!!"
                        #print "Sweet!"
            
            elif n == 15:                #Turndown  # TODO make a correct turndown.. This isn't a turndown

                if self.trickPhase == 1:
                    rot_vel_z = self.rider.turn * dt_s
                    self.model.thz += rot_vel_z
                    
                    if self.model.thz <= 80.0 and self.model.thz + rot_vel_z > 80.0:
                        self.trickPhase = 2

                elif self.trickPhase == 2:
                    rot_vel_y = self.rider.turn * dt_s * 0.8
                    self.model.children['handlebar'].thy += rot_vel_y

                    if self.model.children['handlebar'].thy <= 180.0 and self.model.children['handlebar'].thy + rot_vel_y > 180.0:
                        self.model.children['handlebar'].thy = 180.0
                        self.trickPhase = 3

                elif self.trickPhase == 3:
                    rot_vel_y = -self.rider.turn * dt_s * 0.8
                    self.model.children['handlebar'].thy += rot_vel_y
                    if self.model.children['handlebar'].thy >= 0.0 and self.model.children['handlebar'].thy + rot_vel_y < 0.0:
                        self.model.children['handlebar'].thy = 0.0
                        self.trickPhase = 4

                elif self.trickPhase == 4:
                    rot_vel_z = -self.rider.turn * dt_s
                    self.model.thz += rot_vel_z
                    
                    if self.model.thz >= self.memAngle and self.model.thz + rot_vel_z < self.memAngle:
                        self.model.thz = self.memAngle
                        self.trickPhase = 1
                        self.tricking = 0
                        self.gamestatsRef.trickMsg = "Turndown!!!"
            
            elif n == 16:            #Flair
                if self.trickPhase == 1: #or self.trickPhase == 3
                    rot_vel_z = self.rider.turn * dt_s  # multiply the rotational velocity by some factor to maek the action look good
                    self.model.thz += rot_vel_z
            
                    if self.model.thz >= self.memAngle + 15:
                        self.trickPhase = 2
            
                if self.trickPhase == 2:
                    rot_vel_z = self.rider.turn * dt_s * .5
                    self.model.thz += rot_vel_z
            
                    rot_vel_y = self.rider.turn * dt_s * 0.5
                    self.model.thy += rot_vel_y
            
                    if self.model.thy < 360.0 and self.model.thy + rot_vel_y >= 360.0:
                        self.model.thy = 0.0
                        self.trickPhase = 3
            
                if self.trickPhase == 3:
                    rot_vel = self.rider.turn * dt_s * 0.5
                    self.model.thz += rot_vel
            
                    if self.trickPhase == 3 and self.model.thz >= self.memAngle + 330:
                        self.tricking = 0
                        self.trickPhase = 1
                        self.model.thz = self.memAngle
                        self.memAngle = 0
                        self.gamestatsRef.trickMsg = "Flair!!!"

        else:   # not tricking:
            # NOTE the following code was in this location in the QBASIC game, because all the variables were global. But in the Python version, this stuff probably belongs in the playing state code, so we copied it
            # there. You can probably delete the commented-out code here
            # TODO QBASIC was 1-based; Make sure all your list indices and what not have the correct number base (case in point: self.gamestatsRef.addscore
            #self.gamestatsRef.addScore = int(self.gamestatsRef.addScore + self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick - 1] - ((self.gamestatsRef.factor * self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick - 1]) * self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick - 1]))  # in QBASIC, tricks were base 1, but now we're using base 0
            #if self.gamestatsRef.addScore <= 0:
            #    self.gamestatsRef.addScore = 1
            #self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick - 1] += 1 # TODO rearrange trick tracking to be a class; e.g. trick1.timesUsed, trick1.originalPointTotal, etc.
            #self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " - " + str(self.gamestatsRef.addScore) + " pts. "   # Note: we could use better Python string processing here.. we're just duplicating the QBASIC way
            #if self.gamestatsRef.numTricks > 1:
            #    self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " " + str(self.gamestatsRef.numTricks) + " TRICK COMBO!!!"
            #self.gamestatsRef.runReport.append(self.gamestatsRef.trickMsg)
            #self.gamestatsRef.activeTrick = 0   # NOTE: it's necessary to set activeTrick to 0 here... but why?

            if self.gamestatsRef.activeTrick > 0:
                #import pdb; pdb.set_trace()
                # NOTE: Addscore is used to add up all the scores of all tricks being performed as part of a combo
                addScoreIncrement = int(self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick - 1] - (self.gamestatsRef.factor * self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick - 1] * self.gamestatsRef.trickPointValue[self.gamestatsRef.activeTrick - 1]))     # in QBASIC, tricks were base 1, but now we're using base 0
                addScoreIncrement = max(addScoreIncrement, 1)
                self.gamestatsRef.addScore +=  addScoreIncrement

                self.gamestatsRef.timesUsed[self.gamestatsRef.activeTrick - 1] += 1 # TODO rearrange trick tracking to be a class; e.g. trick1.timesUsed, trick1.originalPointTotal, etc.
                self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " - " + str(self.gamestatsRef.addScore) + " pts. "   # Note: we could use better Python string processing here.. we're just duplicating the QBASIC way
                if self.gamestatsRef.numTricks > 1:
                    self.gamestatsRef.trickMsg = self.gamestatsRef.trickMsg + " " + str(self.gamestatsRef.numTricks) + " TRICK COMBO!!!"
                self.gamestatsRef.runReport.append(self.gamestatsRef.trickMsg)
                self.gamestatsRef.activeTrick = 0

                self.mmRef.setMessage(self.gamestatsRef.trickMsg, [ 400, 300 + self.gamestatsRef.numTricks * 14 ], (192, 64, 64), 3 )  # TODO reinstate this message. It should be triggered when you land a trick, then expire after a few seconds
        
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
        self.gravity = vector.Vector(0.0, -140, 0.0)    # Gravity: set it and forget it
        self.currentLevel = 0
        self.levelPassed = False
        self.finalLevel = 6     # TODO find a better way to Initialize final level. Right now, it's hardcoded. Maybe we can put level data in a file
        self.curRamp = 0
        self.trackHalfWidth = 25.0   # Track width is 2 * this number

        self.y_ground = 0

        self.ramps = []
        self.scoreToBeat = 0

        # TODO probably add some functions to set currentLevel? Or otherwise manipulate directly from wherever..
        pass


    #==============================================================================
    #SUB InitLevel (self.currentLevel)
    #==============================================================================
    def InitLevel(self):
        # TODO perhaps move levels into text files? Or perhaps into a separate module?
        # TODO convert to file i/o. Score-to-beat stuff should belong in a level object, perhaps
        # TODO also, watch out for QBASIC 1-based stuff.. you were an amateur when you made this
        # TODO also, convert InitLevel to Python

        del self.ramps[:]

        Scale = 120         	    # Scale is used in Rotate functions. May need to substitute a camera class?
        self.levelPassed = False    # self.levelPassed belongs in a game stats class or a level manager
        self.curRamp = 0         	# The current ramp in the level (this probably won't be necessary once we have legit collision detection
        #NumTricks = 0       	    # Tracks how many tricks the player has performed (belongs in game stats class) # TODO probably delete this line
        #TrickCounter = 0    	    # Hmm, not sure how this differs from NumTricks. TODO read the code             # TODO probably delete this line
        self.trickCounter = 0
        MsgFrames = 0       	    # Used in messaging (how many frames to leave the message up for)
        msg = ""           		    # Used in messaging - the message text itself
    
    
        # TODO take in a bike obj and set the bike's _position (and the bike model's position, which are separate values)
        # TODO - x, y, and z are candidates for deletion
        x = 120                     # Bike _position on screen (TODO: Decide. LevelManager probably shouldn't be responsible for this? Or, maybe it should, in which case, InitLevel needs a reference to the bike)
        y = self.y_ground - 20 - 10
        z = -60        			    #z offset: keep this around -50 or -60
    
        # TODO make sure variable scoping is correct. You went through a pass of simply converting loose variables into object-oriented objects/members/etc
        #bike.reset()   # TODO maybe take in a reference to the bike as a param?
        #Biker.xvel = 0
        #Biker.yvel = 0
    
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
    
    def update(self, dt_s, bike):
        """ Update the level manager (e.g., things like curRamp and such)

            Note: This takes in the bike object so it can know the bike's _position and track current ramp, and such.
            To be more general, this function can maybe take in a dict of gameobjects
        """
        # TODO decide -- do we want LevelManager to have an update function? Or do we want to 'manually' update the level by calling checkRamp from the game loop?
        pass

    #==============================================================================
    #SUB drawLevel
    #
    #==============================================================================
    def drawLevel(self, screen, stats_and_configs, matView=matrix.Matrix.matIdent(), matViewport=matrix.Matrix.matIdent()):
        # TODO maybe come back and optimize performance here? (reduce # of floating pt operations?)
        for n in range(0, len(self.ramps)):
            ramp_length = self.ramps[n].length * coss(self.ramps[n].incline)
            ramp_height = self.ramps[n].length * sinn(self.ramps[n].incline)
            ramp_gap = self.ramps[n].dist

            # TODO maybe hack this stuff up a little when it comes to 3D track rendering
            launch_sx = self.ramps[n].x
            launch_sy = self.ramps[n].y
            launch_sz = 0.0

            launch_ex = self.ramps[n].x + ramp_length
            launch_ey = self.ramps[n].y + ramp_height
            launch_ez = 0.0

            land_ex = launch_ex + ramp_gap
            land_ey = launch_ey
            land_ez = 0.0

            land_sx = land_ex + ramp_length
            land_sy = self.ramps[n].y
            land_sz = 0.0

            # Apply view transformation first, then do perspective division, then do viewport transformation
            # TODO add a test, like in bike.draw() to only do perspective division if the w component is not 1?
            epsilon = 1e-6

            launch_start_near = matrix.mMultvec(matView, vector.Vector(launch_sx, launch_sy, self.trackHalfWidth, 1.0))
            launch_start_near_viewport = matrix.mMultvec(matViewport, launch_start_near)


            launch_start_far = matrix.mMultvec(matView, vector.Vector(launch_sx, launch_sy, -self.trackHalfWidth, 1.0))
            launch_start_far_viewport = matrix.mMultvec(matViewport, launch_start_far)
            
            launch_end_near = matrix.mMultvec(matView, vector.Vector(launch_ex, launch_ey, self.trackHalfWidth, 1.0))
            launch_end_near_viewport = matrix.mMultvec(matViewport, launch_end_near)

            launch_end_far = matrix.mMultvec(matView, vector.Vector(launch_ex, launch_ey, -self.trackHalfWidth, 1.0))
            launch_end_far_viewport = matrix.mMultvec(matViewport, launch_end_far)

            land_start_near = matrix.mMultvec(matView, vector.Vector(land_sx, land_sy, self.trackHalfWidth, 1.0))
            land_start_near_viewport = matrix.mMultvec(matViewport, land_start_near)

            land_start_far = matrix.mMultvec(matView, vector.Vector(land_sx, land_sy, -self.trackHalfWidth, 1.0))
            land_start_far_viewport = matrix.mMultvec(matViewport, land_start_far)

            land_end_near = matrix.mMultvec(matView, vector.Vector(land_ex, land_ey, self.trackHalfWidth, 1.0))
            land_end_near_viewport = matrix.mMultvec(matViewport, land_end_near)

            land_end_far = matrix.mMultvec(matView, vector.Vector(land_ex, land_ey, -self.trackHalfWidth, 1.0))
            land_end_far_viewport = matrix.mMultvec(matViewport, land_end_far)

            pygame.draw.line(screen, (192, 192, 192), (launch_start_near_viewport[0], launch_start_near_viewport[1]), (launch_end_near_viewport[0], launch_end_near_viewport[1]))
            pygame.draw.line(screen, (192, 192, 192), (launch_start_far_viewport[0], launch_start_far_viewport[1]), (launch_end_far_viewport[0], launch_end_far_viewport[1]))

            pygame.draw.line(screen, (192, 192, 192), (land_start_near_viewport[0], land_start_near_viewport[1]), (land_end_near_viewport[0], land_end_near_viewport[1]))
            pygame.draw.line(screen, (192, 192, 192), (land_start_far_viewport[0], land_start_far_viewport[1]), (land_end_far_viewport[0], land_end_far_viewport[1]))

            pygame.draw.line(screen, (192, 192, 192), (launch_end_near_viewport[0], launch_end_near_viewport[1]), (launch_end_far_viewport[0], launch_end_far_viewport[1]))
            pygame.draw.line(screen, (192, 192, 192), (land_end_near_viewport[0], land_end_near_viewport[1]), (land_end_far_viewport[0], land_end_far_viewport[1]))


#class AABBTreeNode(object):
#    ''' A node-based hierarchy of AABBs
#    '''
#    #TODO decide whether to put AABBTree into pymkfgame collision code or what.
#
#    def __init__(self):
#        self.modelRef = None    # A reference to a model containing vertices to bound (bind?)
#                                # NOTE: AABBs in the tree should be able to compute their own extents, based on the geometric information about the model they bound (i.e., vertices and transformations)
#        self.children = {}
#
#    def addChild(self, childName, childRef):
#        self.children[childName] = childRef
#        
#
## TODO - the goal is to be able to walk a model hierarchy and create AABB nodes for each item in the model. Probably need to use a breadth-first traversal of the model, to be able to properly populate the AABBTree
#
#
#class AABBTree(object):
#    def __init__(self):
#        self.nodes = []
#
#    def autoBuildTree(self, model):
#        ''' Automagically build an AABB tree from a given model
#        '''
#        # Breadth-first traversal
#
#        if model.children:
#            pass

        

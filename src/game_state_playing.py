from pymkfgame.core.message_queue import MessageQueue
from pymkfgame.display_msg.display_msg import DisplayMessage
from pymkfgame.display_msg.display_msg_manager import DisplayMessageManager
from pymkfgame.core.game_state_base import GameStateBase
from pymkfgame.mkfmath.common import DEGTORAD, RADTODEG, coss, sinn
from pymkfgame.mkfmath.vector import *
from pymkfgame.mkfmath.matrix import *
from pymkfgame.mkfmath.refframe import *
from pymkfgame.collision.dist_and_xsect import *
import random

from bike2_core import *

#==============================================================================
class KeyboardStateManager(object):
    ''' Super-simple class to store keyboard state.

        Could be way more feature-packed or robust...
    '''
    def __init__(self):
        self.trickModifierKeys = [pygame.K_RSHIFT, pygame.K_LSHIFT]
        self.trickModifier = False      # Maybe future work could develop this class better; I just wanted to get something simple working
        self.menuActionKeys = [pygame.K_RETURN]
        self.menuActionKeyPressed = False   # This flag only tracks when a key is pressed, but not whether it's held or whatever.. Super simple

class PlayingSubstate(object):
    """ This class implements an enum that allows the Playing state to keep track of its sub-states (e.g. Load level; playing; player crashed; game over; etc. """
    uninitialized = -1
    startlevel = 0
    playing = 1
    crashed = 2
    resetlevel = 3      # TODO: remove? may not be necessary
    finishlevel = 4
    runsummary = 5
    gameover = 6

    # NOTE: haven't decided whether I want to have this class simply be an enum, or an actual object, with methods and such
    #def __init__:
    #    self.value = PlayingSubstate.uninitialized

    #def set(self, newState):
    #    self.value = newState

    #def get(self):
    #    return self.value


class GameplayStats(object):
    
    def __init__(self):
        # TODO consider all your notes and such; movidy the stuff
        # In-game stats
        self.score = 0
        self.paused = 0
        self.maxBikes = 11
        self.numTrophies = [ 0 ]   # A list, to be read from/written to file (perhaps dotaccessdict, config file) TODO read from file. Right now, we're hard-coding the list
        self.scoreToBeat = []   # A list, to be read from/written to file (perhaps dotaccessdict, config file) TODO on second thought, remove this from game stats; it should belong to a level object
        self.bikeStyle = 0      # TODO update bikeStyle. It's meant to indicate which character you're playing as

        # Options/Config
        self.doRunSummary = True    # TODO: Remove; shouldn't be optional... Always do the run summary...
        self.crowdOn = False
        self.sloMo = False
        # NOTE: the currentLevel is stored in the LevelManager.

        # Trick-related info
        self.numTricks = 0          # Num of tricks in a trick combo (resets to 0 upon landing; perhaps name this better?)
        self.addScore = 0           # Used to keep track of the added-up score of tricks in a combo (resets once the trick is landed.. or crashed...)
        self.trickArraySize = 16
        self.trickPointValue = [ 100, 150, 125, 150, 250, 350, 200, 175, 200, 300, 330, 375, 75, 200, 100, 275 ]   # Point values of tricks (e.g. 0th item in array is the point value for Trick #1)
        self.timesUsed = []
        self.trickCounter = 0       # This appears to be an index for the # of tricks performed in a level, for run-report purposes (e.g. a 5-trick combo counts as 1 trickCounter, for the run report.. if that makes sense)
        self.activeTrick = 0        # Note: to be consistent the QBASIC version, we'll make activeTrick go from 1 - whatever # of tricks we want. 0 means no active trick
        self.trickMsg = ""          # Message to display while tricking (e.g. prints out the trick combo as you're performing it)

        # End-of-level summary
        self.runReport = []
        self.reset()
        # TODO make sure to use your resetXYZ helper functions when starting/restarting levels

        # Possibly used for debugging
        self.drawPoints = False

        # Misc
        self.factor = .25   # some factor used for calculating trick/scombo scores. It's pretty arbitrary

    def reset(self):
        self.score = 0
        self.paused = 0
        self.numTricks = 0          # Num of tricks in a trick combo (resets to 0 upon landing; perhaps name this better?)
        self.addScore = 0           # Used to keep track of the added-up score of tricks in a combo (resets once the trick is landed.. or crashed...)
        self.activeTrick = 0        # Note: to be consistent the QBASIC version, we'll make activeTrick go from 1 - whatever # of tricks we want. 0 means no active trick
        self.trickMsg = ""          # Message to display while tricking (e.g. prints out the trick combo as you're performing it)

        # TODO perhaps also add other stuff into this function, e.g. addScore, numTricks, trickCounter, etc
        if self.timesUsed:  # if list exists already, zero it out
            for i in range(0, self.trickArraySize):
                self.timesUsed[i] = 0
        else:               # if this is the first-time use, then create the list
            for i in range(0, self.trickArraySize):
                self.timesUsed.append(0)

        del self.runReport[:]   # Clear out the run report for a new level

    def loadTrophies(self):
        ## TODO convert file i/o to Python
        ## NOTE: You did some hackage to compute a # of trophies won, using 'extended' ascii characters ( > 128)
        ## THe problem is: back in the day, QBASIC used an encoding called cp437 (a.k.a. DOS United States).
        ## Nowadays, a more common encoding is a different one: UTF-8. We'll need to re-work the i/o here
        #OPEN "trophies.dat" FOR INPUT AS #1
        #    FOR n = 1 TO 13
        #        INPUT #1, Temp$
        #        self.numTrophies[n] = VAL(CHR$(ASC(Temp$) - 128))
        #    NEXT n
        #CLOSE
        
        ## TODO un-hardcode the initialization here, and make file i/o 
        ## TODO Make json. Come back and do this later
        for i in range(0, 14):  # 14 bikers with which to earn trophies (i.e., finish the game)
            self.numTrophies[i] = 0
        
        
        ## TODO fix this crap -- there's no reason to loop through this; once you have trophies loaded from file, you can simply check 
        ## TODO make a player/character class, where there's a property, e.g. unlocked = false for the secret characters.. until they're unlocked. Then unlocked = true
        #=-=-=-=-=-=-=-=-=
        #Check to see if player has gotten secret biker #1
        #=-=-=-=-=-=-=-=-=
        StopFlag = False
        for n in range(1, 11 + 1):    #TODO: don't hardcode. Research your code - why 1 + 11? (I think because 11 bikers plus 2 extra/secret guys)
            if self.numTrophies[n] < 1:
                StopFlag = True
                break
        if not StopFlag:
            self.maxBikes = 12   # TODO Don't do this..; instead have the max be whatever it's going to be, and specify whether the bike is locked or unlocked (e.g. keep a list of biker/character objects, where the bonus characters start off with locked=True, or something)
        
        #=-=-=-=-=-=-=-=-=
        
        #=-=-=-=-=-=-=-=-=
        #Check to see if player has gotten secret biker #2
        #=-=-=-=-=-=-=-=-=
        StopFlag = False
        for n in range(1, 12 + 1):       # Counts 1 to 12. TODO: don't hardcode. Research your code - why 1 - 12?
            if self.numTrophies[n] < 2:
                StopFlag = True
                break
        if not StopFlag:
            self.maxBikes = 13
        #=-=-=-=-=-=-=-=-=

    # TODO maybe put all this stuff into a file and load it at game startup
    successPhrases = [ "Alright, man, you beat the level!  Good job!"
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

    failurePhrases = [ "Aww, man, you didn't make it.  Now you've gotta do it all over."
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

    crashPhrases = [ "Crash!!!"
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

    rampCrashPhrases = [ "Umm, you were supposed to jump over the gap, not into it."
        , "Next time, try clearing the jump."
        , "Oh, man, that's pathetic."
        , "You bring shame to the name of all trick bikers."
        , "Yeah, now you know why they call it a landing ramp."
        , "Should I wire landing lights into the track?"
        , "I hope you never become a pilot."
        ]

#==============================================================================

class GameStateImpl(GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        #super(GameStateImpl, self).__init__()
        #self.SetName("Playing State")
        #print "GAMESTATE Playing State __init__ running (creating data members and method functions)"
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateImpl.__instance is None:
            GameStateImpl.__instance = super(GameStateImpl, GameStateImpl).__new__(GameStateImpl)
            GameStateImpl.__instance.__init__()
            GameStateImpl.__instance.SetName("Playing")
            #print "GAMESTATE Playing State creating __instance object {}".format(GameStateImpl.__instance)

        #print "GAMESTATE Playing State getting __instance {}".format(GameStateImpl.__instance)
        return GameStateImpl.__instance

    def Init(self, appRef, takeWith=None):
        self.gamestats = GameplayStats()  # TODO make sure variable scoping and/or function parameters are straight

        self.substate = PlayingSubstate()
        #self.substate = PlayingSubstate.startlevel  # TODO decide if you prefer to have an object with constructor/methods/etc
        self.substate = PlayingSubstate.uninitialized
        self.appRef = appRef
        self.kbStateMgr = KeyboardStateManager()

        self.levelMgr = LevelManager()
        self.mm = DisplayMessageManager()   # TODO - maybe make names more descriptive? DisplayMessageManager is for (and only for) event-based messages that will appear for some amount of time, then disappear

        self.staticMsg = {}            # a dict to store static DisplayMessage objects ("static" means they appear indefinitely as opposed to DisplayMessageManager messages, which expire after some time)
        self.InitializeStaticMessages()

        self.runSummaryDisplayMsgs = []

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        # Register Event Listeners
        #self._eventQueue.RegisterListener('ball', self.ball.controlState, 'PlayerControl') # Change this to be self.bike
        #self._eventQueue.RegisterListener('mixer', self.mixer, 'PlaySfx')
        self._eventQueue.RegisterListener('engine', self.appRef, 'Application') # Register the game engine to listen to messages with topic, "Application"

        self.bike = Bike()   # TODO make sure variable scoping and/or function parameters are straight
        self.bike.gamestatsRef = self.gamestats # give the bike a reference to gamestats
        self.bike.mmRef = self.mm               # give the bike a reference to the message manager
        self.bike.levelMgrRef = self.levelMgr   # give the bike a reference to the level manager

        self.refFrame = ReferenceFrame()

    def Cleanup(self):
        pass

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        pass

    def InitializeStaticMessages(self):
        # TODO/NOTE: the position list could just as easily be a tuple (might even lead to better performance?)
        # TODO speaking of positions, we'll definitely need to tweak the positioning of these messages, and possibly (probably) allow dynamic positioning
        self.staticMsg['score'] = DisplayMessage()
        self.staticMsg['score'].create(txtStr="Score: ", position=[80, 10], color=(192, 64, 64))
        self.staticMsg['score'].alive = True

        self.staticMsg['level'] = DisplayMessage()
        self.staticMsg['level'].create(txtStr="Level: ", position=[150, 10], color=(192, 64, 64))
        self.staticMsg['level'].alive = True

        self.staticMsg['scoreToBeat'] = DisplayMessage()
        self.staticMsg['scoreToBeat'].create(txtStr="Score to beat: ", position=[250, 10], color=(192,64,64))
        self.staticMsg['scoreToBeat'].alive = True

        self.staticMsg['speed'] = DisplayMessage()
        self.staticMsg['speed'].create(txtStr="Speed: ", position=[5,10], color=(192,64,64))
        self.staticMsg['speed'].alive = True

        self.staticMsg['info'] = DisplayMessage()   # This message will be used for crash/pass level/fail level/etc. messages
        self.staticMsg['info'].create(txtStr="", position=[320, 200], color=(192,64,64))
        self.staticMsg['info'].alive = False

        self.staticMsg['presskey'] = DisplayMessage()   # This message will be used for crash/pass level/fail level/etc. messages
        self.staticMsg['presskey'].create(txtStr="", position=[320, 400], color=(192,64,64))
        self.staticMsg['presskey'].alive = False

    def EnqueueApplicationQuitMessage(self):
        """Enqueue a message for the application to shut itself down
        """
        # TODO maybe make this function (EnqueueQuit) a part of the base gamestate class?
        self._eventQueue.Enqueue( { 'topic': 'Application',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'setRunningFlagToFalse'
                                               , 'params' : ''
                                               }
                                  } )

    def ProcessEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                self.EnqueueApplicationQuitMessage()
            if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.doControls(event)


    def ProcessCommands(self):
        # TODO maybe put this command extraction logic into a function at the application class level (or base gamestate level). We're reusing the logic in every gamestate instance
        msg = self._eventQueue.Dequeue()
        while msg:
            #print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                #print "DEBUG Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

                # Evaluate the 'action' key to know what to do. The action dictates what other information is required to be in the message
                if msg['payload']['action'] == 'call_function':
                    # The registered listener had better have the function call available heh... otherwise, kaboom
                    objRef = listener_obj_dict['ref']
                    fn_ptr = getattr(objRef, msg['payload']['function_name'])
                    argsDict = eval("dict({})".format(msg['payload']['params']))    # params should be a comma-separated list of key=value pairs, e.g. "a = 5, b = 3"

                    #print "function args: {}".format(argsDict)
                    if argsDict:
                        # In this particular gamestate, we want an argsdict to translate to kwargs. This is because the mixer class is written with kwargs (other classes in other gamestates use dicts, in which case, we pass in argsDict as-is))
                        fn_ptr(self, **argsDict)
                    else:
                        fn_ptr(self)

                #elif msg['payload']['action'] == 'notify':
                #    # The "notify" action merely notifies the listener that an action happened, but does not
                #    # call for a specific action to be taken


            msg = self._eventQueue.Dequeue()

    def Update(self, dt_s):
        # TODO put in fixed timestep updating. We want to update every cycle, but only draw when it's time to
        # TODO note: there are probably things that should ALWAYS happen in the Update function, no matter the substate (e.g. message manager updates?
        self.mm.update(dt_s)    # TODO possibly also pass in a reference to the gameplay stats object? (that's how we did it Falldown)

        if self.substate == PlayingSubstate.uninitialized:
            # This state represents the very beginning of the game; one-time startup stuff. 
            self.levelMgr.currentLevel = 1
            self.substate = PlayingSubstate.startlevel

        elif self.substate == PlayingSubstate.startlevel:
            # TODO break playingsubstates into their own functions, maybe
            # Initialize bike
            self.bike.Init()    # TODO move this out of update()? I'm not sure I like having it here # TODO evaluate -- do we need to totally reinit here (Init() loads the model from disk.. Might be overkill)
            #import pdb; pdb.set_trace()
            #bike_y_pos_offset = (self.bike.model.children['frame'].children['wheel'].collisionGeom._maxPt[1] - self.bike.model.children['frame'].children['wheel'].collisionGeom._minPt[1]) / 2.0
            bike_y_pos_offset = 10 # hard-coded - 5 for bike wheel radius, + 5 more because wheel is situated at y = -5
            bike_y_floor = self.levelMgr.y_ground + bike_y_pos_offset

            self.bike._position = Vector(320, bike_y_floor, 0, 1)        # TODO make a function that synchronizes bike _position with bike model position
            self.bike.model.position = Point3D(320, bike_y_floor, 0)             # NOTE: +15 to offset model offset an wheel radius
            self.bike._velocity = Vector(0,0,0)
            self.bike._acceleration = Vector(0,0,0)

            self.bike.rider.maxspd = 130.0  # TODO don't hardcode biker abilities
            self.bike.rider.pump = 12.0     # TODO don't hardcode biker abilities
            self.bike.rider.jump = 3.0      # TODO don't hardcode biker abilities
            self.bike.rider.turn = 270.0    # degrees per second # TODO don't hardcode biker abilities

            ## TODO Do something useful with frames of reference. The stuff you're doing with it right now is for testing purposes and will probably be replaced. Also, refFrame isn't defined in state.Init(). It's defined here
            self.refFrame.setUpVector(0,-1,0)
            self.refFrame.setLookVector(0,0,-1)
            self.refFrame.setPosition(-320, 0, 0)   # TODO figure out positioning. I believe the reference frame should be positioned at origin (0,0,0)

            ##self.refFrame.setPosition(350, self.levelMgr.y_ground + 30, -50)
            ##look = Vector(self.bike._position[0] - self.refFrame.position[0], self.bike._position[1] - self.refFrame.position[1], self.bike._position[2] - self.refFrame.position[2])
            ##self.refFrame.setLookVector(look[0], look[1], look[2])
            #vNormalize(self.refFrame.look)
            #import pdb; pdb.set_trace()
            self.bike.model.updateModelTransform()
            # TODO make viewport matrix, as well. Viewport happens after projection, so the main point is to compute vertices to fit in a desired viewport/window within the screen

            # Display level start message
            self.levelMgr.levelPassed = False
            self.levelMgr.InitLevel()
            self.mm.setMessage("Level {}!".format(self.levelMgr.currentLevel), [ 400, 200 ], (192, 64, 64), 2 )  # TODO un-hardcode the render position of the message. But otherwise, use this as a template to replace other message and doMessage calls
            self.gamestats.reset()

            # Clear info & presskey messages
            self.staticMsg['info'].alive = False
            self.staticMsg['presskey'].alive = False

            self.substate = PlayingSubstate.playing # TODO maybe put a couple of seconds' delay before substate change, or maybe require a keypress
        elif self.substate == PlayingSubstate.playing:
            ## TODO note/correct - there is some redundancy between the RiderType class and the Bike class. e.g., RiderType has xvel, and Bike have velocity Vector (which has an x component)
    
            self.bike.update(dt_s)
            self.refFrame.setPosition(-self.bike._position[0], 0, 0) # Move the camera (follow the bike) (note the negative sign..)
            self.checkRamp(self.levelMgr.curRamp)    # TODO possibly move the checkRamp call into the playing substate?

            if self.bike.inAir:
                # This is rudimentary "collision detection" (more like a boundary test) for determining when the bike lands (self.levelMgr.y_ground is ground level)

                if self.bike._velocity[1] < 0 and self.bike.model.collisionGeom._minPt[1] <= self.levelMgr.y_ground:  # TODO make sure that biker's yvel is 0 when on the ground; otherwise this test will trigger false positives
                    # If you're here, you've landed
                    #bike_y_pos_offset = (self.bike.model.children['frame'].children['wheel'].collisionGeom._maxPt[0] - self.bike.model.children['frame'].children['wheel'].collisionGeom._minPt[0]) / 2.0
                    bike_y_pos_offset = 10 # hard-coded - 5 for bike wheel radius, + 5 more because wheel is situated at y = -5
                    bike_y_floor = math.floor(self.levelMgr.y_ground + bike_y_pos_offset)
                    self.bike._position[1] = bike_y_floor
                    self.bike.model.position[1] = bike_y_floor
                    #self.bike._position[1] = self.levelMgr.y_ground
                    #self.bike.model.position[1] = self.levelMgr.y_ground
                    self.bike._velocity[1] = 0.0

                    # TODO after doing rough-cut aabb test, do more precise testing.. somehow. Maybe an intersection test of the wireframe with the ground?
                    # TODO Maybe store ramp geometry in the level object; you're recalculating coordinates that you calculated in order to be able to draw the level. Add collision detection
                    ramp_length = self.levelMgr.ramps[self.levelMgr.curRamp].length * coss(self.levelMgr.ramps[self.levelMgr.curRamp].incline)
                    ramp_height = self.levelMgr.ramps[self.levelMgr.curRamp].length * sinn(self.levelMgr.ramps[self.levelMgr.curRamp].incline)
                    ramp_gap = self.levelMgr.ramps[self.levelMgr.curRamp].dist

                    launch_sx = self.levelMgr.ramps[self.levelMgr.curRamp].x
                    launch_sy = self.levelMgr.ramps[self.levelMgr.curRamp].y

                    launch_ex = self.levelMgr.ramps[self.levelMgr.curRamp].x + ramp_length
                    launch_ey = self.levelMgr.ramps[self.levelMgr.curRamp].y + ramp_height

                    land_ex = launch_ex + ramp_gap
                    land_ey = launch_ey

                    land_sx = land_ex + ramp_length
                    land_sy = self.levelMgr.ramps[self.levelMgr.curRamp].y

                    # TODO modify this -- use collision detection
                    DidNotClearRamp = self.bike.model.collisionGeom._minPt[0] < land_ex    # You didn't clear the jump if you land before the lip of the landing ramp # TODO make the landing calculation more robust. Should be able to land on the ramp
            
                    #import pdb; pdb.set_trace()
                    if self.bike.tricking or DidNotClearRamp:
                        msg = ""
                        if self.bike.tricking :
                            self.staticMsg['info'].alive = True
                            self.staticMsg['info'].changeText(getCrashedMsg(self.gamestats.crashPhrases))
                            # NOTE: we only set the message here. The drawStatus function will render the message.  But also NOTE: we'll need to make sure to clear out the txtStr property to clear out messages (e.g. "You crashed" messages)
                        else:
                            self.staticMsg['info'].alive = True
                            self.staticMsg['info'].changeText(getDidNotClearJumpMsg(self.gamestats.rampCrashPhrases))
                        # Aside: I know the code is weird in this game; I'm porting from QBASIC.. give me a break
                        self.staticMsg['presskey'].alive = True
                        self.staticMsg['presskey'].changeText("Press <Enter> to continue.")
                        self.bike.crashed = True
                        self.substate = PlayingSubstate.crashed
                        self.bike._position[1] = bike_y_floor
            
                        if (self.bike.model.children['frame'].thy + 180) % 360 >= 270 and (self.bike.model.children['frame'].thy + 180) % 360 <= 90 :
                            self.bike.model.children['handlebar'].thz = 180
                            self.bike.model.children['frame'].thz = 180

                        else:
                            self.bike.model.children['handlebar'].thz = 0
                            self.bike.model.children['frame'].thz = 0
                    
                        self.bike.model.children['frame'].thx = 70
                        self.bike.model.children['handlebar'].thx = 70
            
                        # TODO why did I do thy + 180? Also... Why did I hardcode thx's to 70, above?? Look at the original source
                        # Ohhh I think this is where we draw the bike in a crashed state
                        #CALL RotateBike(self.bike.model.children['frame'].thx, self.bike.model.children['frame'].thy + 180, self.bike.model.children['frame'].thz)
                        #CALL RotateBar(self.bike.model.children['handlebar'].thx, self.bike.model.children['handlebar'].thy + 180, self.bike.model.children['handlebar'].thz)

                        # We compose rotation matrices in ZYX order, so they're applied in XYZ order
                        # Note: There has to be a better way to access vars and functions.. These lines of code are super long...
                        self.bike.model.children['handlebar'].matRot = matrix.mMultmat( matrix.Matrix.matRotZ(self.bike.model.children['handlebar'].thz), matrix.Matrix.matRotY(self.bike.model.children['handlebar'].thy)  )
                        self.bike.model.children['handlebar'].matRot = matrix.mMultmat( self.bike.model.children['handlebar'].matRot, matrix.Matrix.matRotX(self.bike.model.children['handlebar'].thx) )

                        self.bike.model.children['frame'].matRot = matrix.mMultmat( matrix.Matrix.matRotZ(self.bike.model.children['frame'].thz), matrix.Matrix.matRotY(self.bike.model.children['frame'].thy)  )
                        self.bike.model.children['frame'].matRot = matrix.mMultmat( self.bike.model.children['frame'].matRot, matrix.Matrix.matRotX(self.bike.model.children['frame'].thx) )

                        self.bike._velocity[0] = 0.0                            # TODO maybe move this hard-coded velocity assignment into a physics simulation

                    else:
                        # Note: the following stuff is what happens once a trick is landed. Perhaps put into a helper function
                        self.bike.inAir = False

                        #import pdb; pdb.set_trace()
                        self.gamestats.score += self.gamestats.addScore
                        self.gamestats.addScore = 0 # Reset addscore on a successful landing; it tallies the point total of all tricks performed in a combo, and resets when the trick/combo is landed
                        self.gamestats.numTricks = 0
                        self.bike.model.thz = 0                         # Set the parent transformation to 0 deg about Z
                        self.bike.model.children['frame'].thz = 0       # TODO: evaluate: is it necessary to also set child transforms after the parent transform? Probably yes
                        self.bike.model.children['handlebar'].thz = 0
                        one = 15        #Tab stops
                        self.levelMgr.curRamp += 1   # TODO manage curRamp better. Maybe take a BSP-type approach? i.e, look at all ramps, but only process a ramp is the bike's x pos < ramp's x pos

                if self.levelMgr.curRamp == len(self.levelMgr.ramps):  # You've finished the level
                    #import pdb; pdb.set_trace()
                    # TODO Make the end-of-level work without the crashing the program
                    self.staticMsg['presskey'].alive = True
                    self.staticMsg['presskey'].changeText("Press <Enter> to continue.")
            
                    self.substate = PlayingSubstate.finishlevel
                    if self.gamestats.score >= self.levelMgr.scoreToBeat:
                        #import pdb; pdb.set_trace()
                        self.levelMgr.levelPassed = True  # TODO evaluate whether this flag is necessary. If we need to stay in the level state for a while, then keep it. But if it makes more sense to increment the level counter here, and go to a new substate, then do that
                        # TODO as always, look at what function is being called here
                        self.staticMsg['info'].alive = True
                        self.staticMsg['info'].changeText(getBeatLevelMsg(self.gamestats.successPhrases))
                        # TODO add level increment here - level += 1; initlevel; etc
            
                    else:
                        self.staticMsg['info'].alive = True
                        self.staticMsg['info'].changeText(getLostLevelMsg(self.gamestats.failurePhrases))
                    # TODO wait for keypress here? Should there be substates for all these little things, like a substate for game-finished-at-first, and then for game-still-finished-show-run-summary, etc?
                    #WHILE INKEY$ <> CHR$(13): WEND
            
            else:
                if self.bike.onRamp:
                    # NOTE we pass here because the bike-is-on-ramp case is handled in checkRamp
                    # Also note: Holy Lord, this is such bad style...
                    pass
                else:
                    # TODO store bike_y_pos_offset as a member of bike, or some class. It's scattered all over the place, being redefined as needed
                    bike_y_pos_offset = 10 # hard-coded - 5 for bike wheel radius, + 5 more because wheel is situated at y = -5
                    bike_y_floor = math.floor(self.levelMgr.y_ground + bike_y_pos_offset)
                    self.bike._position[1] = bike_y_floor
                    self.bike.model.position[1] = bike_y_floor

        elif self.substate == PlayingSubstate.crashed:
            # If we crashed, then wait here for user input, then go back to startLevel

            #self.bike.Init()    # TODO evaluate -- do we need to totally reinit here (Init() loads the model from disk.. Might be overkill)
            #self.levelMgr.InitLevel(self.levelMgr.currentLevel)    # TODO replace with level manager

            if self.kbStateMgr.menuActionKeyPressed:
                self.mm.clear()
                self._eventQueue.Clear()
                self._eventQueue.Initialize(64) # TOOD perhaps don't hardcode the # of events that can be handled by this queue

                self.bike.model.resetModelTransform()
    
                #self.substate = PlayingSubstate.resetlevel     # TODO remove? Probably don't need PlayingSubstate.resetlevel
                self.substate = PlayingSubstate.startlevel
                # TODO perhaps wait for user input? (put that logic into ProcessEvents)

        elif self.substate == PlayingSubstate.finishlevel:
            # TODO make sure the game switches into this substate
            if self.kbStateMgr.menuActionKeyPressed:

                if self.levelMgr.levelPassed:
                    self.levelMgr.currentLevel = self.levelMgr.currentLevel + 1
                    self.levelMgr.levelPassed = False   # I think we reset this when we init a new level, but just to be sure, do it here. Then review the code later, and remove extraneous crap.

                    self.substate = PlayingSubstate.runsummary
                    # Create a list of DisplayMsg objects to be displayed in the run summary substate
                    # (we init here so that the runsummary substate can be concerned only with displaying the
                    # run summary, and then cleaning up when transitioning out of that substate)

                    headerY = 80   # TODO make the run report compute its size and position itself on screen
                    msgIndex = 0

                    self.runSummaryDisplayMsgs.append(DisplayMessage())
                    msgRef = self.runSummaryDisplayMsgs[msgIndex]    # Get a reference to the most recently created DisplayMsg
                    msgRef.create(txtStr="Tricks that You Pulled Off!! (Ohh yeahhh!)", position=[320, headerY + msgIndex * 12])

                    initialReportY = 100
                    msgIndex += 1
                    for msg in self.gamestats.runReport:
                        self.runSummaryDisplayMsgs.append(DisplayMessage())
                        msgRef = self.runSummaryDisplayMsgs[msgIndex]
                        # TODO improve the DisplayMessage interface & constructor to allow more flexibility / better access to data members
                        msgRef.create(txtStr=msg, position=[320, initialReportY + msgIndex * 12])
                        msgRef.alive = True # NOTE: No need to set ttl; these messages are static because we'll intentionally not update them.
                        # TODO seriously, update the DisplayMessage class to allow for static messages -- ttl = -1 or something like that
                        msgIndex += 1

                    if self.levelMgr.currentLevel > self.levelMgr.finalLevel:
                        self.staticMsg['info'].alive = True
                        self.staticMsg['info'].changeText("GAME OVER")
                        self.staticMsg['presskey'].alive = True
                        self.staticMsg['presskey'].changeText("Press <Enter> to return to main menu.")
                     
                        # TODO still review this code. Most of it was written in QBASIC days, when you really sucked at programming
                        if self.gamestats.numTrophies[self.gamestats.bikeStyle] < 2:    # NOTE: here, bikeStyle operates like "SelectedRider"
	                		# write trophy data to file
                            self.gamestats.numTrophies[self.gamestats.bikeStyle] += 1
                    
                            self.staticMsg['info'].alive = True
                            self.staticMsg['info'].changeText("Congratulations, you got a trophy!!!")

                            #OPEN "trophies.dat" FOR OUTPUT AS #1    # TODO don't delete this; pythonize file output
                            #    FOR n = 1 TO 13
                            #        PRINT #1, CHR$(ASC(LTRIM$(STR$(self.gamestats.numTrophies[n]))) + 128)
                            #    NEXT n
                            #CLOSE
                else:
                    self.substate = PlayingSubstate.startlevel
                
        elif self.substate == PlayingSubstate.runsummary:
            # TODO refactor this code to initialize display obj's before switching into this substate; then, don't keep reassigning alive and text?
            self.staticMsg['presskey'].alive = True
            self.staticMsg['presskey'].changeText("Press <Enter> to return to go to next level")

            if self.kbStateMgr.menuActionKeyPressed:
                    self.substate = PlayingSubstate.startlevel
                    del self.runSummaryDisplayMsgs[:]

        elif self.substate == PlayingSubstate.gameover:
            #TODO high scores
            #TODO go back to main menu (state change; not a mere substate change)
            #if self.kbStateMgr.menuActionKeyPressed:   # TODO uncomment this line when you're ready
            pass

        self.kbStateMgr.menuActionKeyPressed = False    # Clear the action key flag. This is important; it's used for "wait states", like "Press Enter to continue" before transitioning from, e.g. crashed to startlevel


    def PreRenderScene(self):
        pass

    def RenderScene(self):
        # TODO put in fixed timestep updating / some time of timer class. We want to update every cycle, but only draw when it's time to. Something like: if timer.timeToDraw: draw it else: return
        # TODO all objects should update their vertices based on view transforms here. Ideally, we should use a vertex buffer to combine all renderable vertices, and then apply the xform to the buffer.. But, we're not there yet
        self.appRef.surface_bg.fill((0,0,0))

        # =====================================================================
        # Viewport matrix
        # =====================================================================
        # Set up viewport transformation # TODO put viewport transformation into a class?
        screensize = self.appRef.surface_bg.get_size()

        vl = 0
        vr = screensize[0]
        vt = 0
        vb = screensize[1]  # Note: Top is 0 because Pygame puts (0,0) at top-left of screen
        vf = 1.0
        vn = -1.0   # Note that "near" is -1, because we're a left-handed coord system. Because math (+z goes into screen)
        viewportMatrix = matrix.Matrix((vr - vl) / 2.0, 0, 0, 0,
                                       0, (vt - vb) / 2.0, 0, 0,
                                       0, 0, (vf - vn) / 2.0, 0,
                                       (vr + vl) / 2.0, (vt + vb) / 2.0, (vf + vn) / 2.0, 1)

        #viewportMatrix = matrix.Matrix.matIdent()

        # =====================================================================
        # View matrix (i.e., camera/"lookat")
        # =====================================================================
        # Get the view matrix (i.e. camera view)
        #viewMatrix = matrix.Matrix.matIdent()
        cam_dist = 400 

        # --- 3rd person view from side
        #camPosition = Vector(self.bike._position[0], self.bike._position[1] + 250, -360)  # Flying camera (Skycam)
        camPosition = Vector(self.bike._position[0], 0, -250)  # Camera on ground
        viewMatrix = self.refFrame.getLookAtMatrix(camPosition[0], camPosition[1], camPosition[2], self.bike._position[0], self.bike._position[1], self.bike._position[2], 0, 1, 0)  # Camera looks up at bike on jumps

        ## --- First person view NOTE: Doesn't work, because I'm not clipping. Also, I think I need the composed transformation matrix for the bike frame, not just the bike's overall deally
        #camOffset = Vector(-30, 25, 10)
        #lookVector = Vector(1000,0,-10)

        #bikeTransform = matrix.mMultmat(matrix.Matrix.matRotY(self.bike.model.thy), matrix.Matrix.matRotX(self.bike.model.thx))# TODO this should probably be a member fn of Wireframe -- to get the transform
        #bikeTransform = matrix.mMultmat(matrix.Matrix.matRotZ(self.bike.model.thz), bikeTransform)

        #camPosition = matrix.mMultvec(bikeTransform, camOffset)
        #camPosition = vAdd(self.bike._position, camPosition)

        #lookPoint = matrix.mMultvec(bikeTransform, lookVector)
        #lookPoint = vAdd(camPosition, lookPoint)

        #print "camPosition:{}, lookPoint:{}".format(camPosition, lookPoint)
        #viewMatrix = self.refFrame.getLookAtMatrix(camPosition[0], camPosition[1], camPosition[2], lookPoint[0], lookPoint[1], lookPoint[2], 0, 1, 0)

        #viewMatrix = matrix.Matrix.matIdent()
        #print "viewMatrix\n{}".format(viewMatrix)

        # =====================================================================
        # Projection matrix
        # =====================================================================
        projectionMatrix = self.refFrame.getPerspectiveProjectionMatrix(60.0, screensize[0] / screensize[1], 1.0, 200.0)
        #projectionMatrix = self.refFrame.getPerspectiveProjectionMatrix(30.0, screensize[0] / screensize[1], 0.5, 5.0)
        #projectionMatrix = matrix.Matrix.matIdent()
        #print "projection matrix\n{}".format(projectionMatrix)


        # =====================================================================
        # Matrix composition
        # =====================================================================
        composedProjAndView = matrix.mMultmat(projectionMatrix, viewMatrix)
        #composedProjAndView = viewMatrix
        #composedProjAndView = projectionMatrix
        #composedProjAndView = matrix.Matrix.matIdent()

        self.levelMgr.drawLevel(self.appRef.surface_bg, self.gamestats, matView=composedProjAndView, matViewport=viewportMatrix)
        self.bike.draw(self.appRef.surface_bg, matView=composedProjAndView, matViewport=viewportMatrix)
        self.mm.draw(self.appRef.surface_bg)

        #self.levelMgr.drawLevel(self.appRef.surface_bg, self.gamestats, matView=viewMatrix)
        #self.bike.draw(self.appRef.surface_bg, matView=viewMatrix)

    def PostRenderScene(self):
        self.drawStatus(self.appRef.surface_bg)    # TODO: Pythonize. status can be an overlay on the game window

        # This is admittedly a janky way to get the run summary in.. But then again, how far from my normal is that, really?
        if self.substate == PlayingSubstate.runsummary:
            self.runSummary()
        pygame.display.flip()

    #==============================================================================
    #SUB self.drawStatus
    #Display the status/score stuff on the screen
    #==============================================================================
    def drawStatus(self, screen):
        l = 120
        w = 4
        by = 5
        bx = 50

        if self.bike.rider.maxspd == 0.0:
            self.bike.rider.maxspd = 1.0 # TODO delete this hack; the purpose of it is to simply get the game up and running, before implementing character selection
        pygame.draw.rect(self.appRef.surface_bg, (255,255,255),  (bx - 1, by, l + 1, w)) 
        pygame.draw.rect(self.appRef.surface_bg, (0,255,0), (bx, by + 1, l * (self.bike._velocity[0] / self.bike.rider.maxspd), w - 1))
        
        self.staticMsg['speed'].changeText("Speed: {}".format(self.bike.rider.xvel))
        textSurfaceSpeed = self.staticMsg['speed'].getTextSurface(self.mm._font)    # Here we're using the message manager's font
        self.appRef.surface_bg.blit(textSurfaceSpeed, (self.staticMsg['speed']._position[0], self.staticMsg['speed']._position[1]))

        self.staticMsg['score'].changeText("Score: {}".format(self.gamestats.score))
        textSurfaceScore = self.staticMsg['score'].getTextSurface(self.mm._font)    # Here we're using the message manager's font
        self.appRef.surface_bg.blit(textSurfaceScore, (self.staticMsg['score']._position[0], self.staticMsg['score']._position[1]))

        self.staticMsg['level'].changeText("Level: {}".format(self.levelMgr.currentLevel))
        textSurfaceLevel = self.staticMsg['level'].getTextSurface(self.mm._font)
        self.appRef.surface_bg.blit(textSurfaceLevel, (self.staticMsg['level']._position[0], self.staticMsg['level']._position[1]))

        self.staticMsg['scoreToBeat'].changeText("Score to beat: {}".format(self.levelMgr.scoreToBeat))
        textSurfaceScoreToBeat = self.staticMsg['scoreToBeat'].getTextSurface(self.mm._font)
        self.appRef.surface_bg.blit(textSurfaceScoreToBeat, (self.staticMsg['scoreToBeat']._position[0], self.staticMsg['scoreToBeat']._position[1]))

        #if self.staticMsg['info']._text:   # Render info message if it exists
        if self.staticMsg['info'].alive:
            textSurfaceInfo = self.staticMsg['info'].getTextSurface(self.mm._font)
            self.appRef.surface_bg.blit(textSurfaceInfo, (self.staticMsg['info']._position[0], self.staticMsg['info']._position[1]))

        #if self.staticMsg['presskey']._text:   # Render info message if it exists
        if self.staticMsg['presskey'].alive:   # Render info message if it exists
            textSurfaceInfo = self.staticMsg['presskey'].getTextSurface(self.mm._font)
            self.appRef.surface_bg.blit(textSurfaceInfo, (self.staticMsg['presskey']._position[0], self.staticMsg['presskey']._position[1]))

# PlayingState-specific helper functions

#==============================================================================
#SUB doControls
#Handle keyboard input
#==============================================================================
    def doControls(self, event):
        # This will be the input handling function of the playing game state
        
        #CASE "p", "P"
        ## TODO revisit.. gamestats.paused?? Let's make pause its own game_state..
        #if gamestats.paused == 0:
        #    s$ = "-=* PHAT FREEZE FRAME SNAPSHOT *=-"
        #    LOCATE 6, 41 - LEN(s$) / 2: PRINT s$
        #    self.levelMgr.drawLevel()
        #    bike.draw()
        #    self.drawStatus
        #    PCOPY 1, 0: CLS
        #    gamestats.paused = 1
        #    WHILE INKEY$ = "": WEND
        #    gamestats.paused = 0
        #END IF
        
        # TODO perhaps honor the escape key?
        #CASE CHR$(27)
        #    Quit = True
        #    EXIT SUB

        # TODO revisit the logic here
        if event.type == pygame.KEYDOWN:
            if event.key in self.kbStateMgr.trickModifierKeys:
                self.kbStateMgr.trickModifier = True

            if event.key == pygame.K_l:
                if not self.bike.inAir:
                    self.bike._velocity[0] += self.bike.rider.pump
                    if self.bike._velocity[0] >= self.bike.rider.maxspd:
                        self.bike._velocity[0] = self.bike.rider.maxspd

            elif self.bike.inAir and not self.bike.tricking:
                if event.key == pygame.K_j:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 2   # Note: self.gamestats.activeTrick is the trick identifier (selects which trick animation to play)
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                    else:
                        self.gamestats.activeTrick = 1
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                elif event.key == pygame.K_k:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 4
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                    else:
                        self.gamestats.activeTrick = 3
                        self.bike.tricking = 1
                        #self.bike.memAngle = self.bike.model.children['handlebar'].thy  # Use handlebar angle because this trick is a handlebar spin
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                elif event.key == pygame.K_i:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 16
                        self.bike.tricking = 1
                        self.bike.memAngle = self.bike.model.thz
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1

                    else:
                        self.gamestats.activeTrick = 5
                        self.bike.tricking = 1
                        self.bike.memAngle = self.bike.model.thz
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                elif event.key == pygame.K_u:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 9
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                    else:
                        self.gamestats.activeTrick = 7
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
                
                elif event.key == pygame.K_o:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 10
                        self.bike.tricking = 1
                        self.bike.memAngle = self.bike.model.thz
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                    else: 
                        self.gamestats.activeTrick = 8
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
             
                elif event.key == pygame.K_h:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 12
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                    else:
                        self.gamestats.activeTrick = 11
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.bike.memAngle = self.bike.model.thz
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                elif event.key == pygame.K_y:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 14
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
                        self.bike.memAngle = self.bike.model.thz
            
                    else: 
                        self.gamestats.activeTrick = 13
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
                        self.bike.memAngle = self.bike.model.thz
            
                elif event.key == pygame.K_n:
                    if self.kbStateMgr.trickModifier:
                        self.gamestats.activeTrick = 6
                        self.bike.tricking = 1
                        self.bike.memAngle = self.bike.model.thz
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1

                    else:
                        #import pdb; pdb.set_trace()
                        self.bike.memAngle = self.bike.model.thz
                        self.gamestats.activeTrick = 15
                        self.bike.tricking = 1
                        self.gamestats.numTricks += 1
                        self.levelMgr.trickCounter = self.levelMgr.trickCounter + 1
            
                #Lean back
                elif event.key == pygame.K_q:
                    self.bike.model.children['frame'].thz = self.bike.model.children['frame'].thz - self.bike.rider.turn / 2
                    self.bike.model.children['handlebar'].thz = self.bike.model.children['handlebar'].thz - self.bike.rider.turn / 2
                
                #Lean forward
                elif event.key == pygame.K_w:
                    self.bike.model.children['frame'].thz = self.bike.model.children['frame'].thz + self.bike.rider.turn / 2
                    self.bike.model.children['handlebar'].thz = self.bike.model.children['handlebar'].thz + self.bike.rider.turn / 2
                pass

        elif event.type == pygame.KEYUP:
            if event.key in self.kbStateMgr.trickModifierKeys:
                self.kbStateMgr.trickModifier = False

            elif event.key in self.kbStateMgr.menuActionKeys:
                self.kbStateMgr.menuActionKeyPressed = True


        
    #==============================================================================
    #SUB checkRamp ()
    #Rudimentary collision detection -- test whether the bike has hit a ramp
    #==============================================================================
    def checkRamp(self, n):
        if self.bike.inAir:
            return
    
        ex = self.levelMgr.collisionGeoms[n]['launch'].p[0] + self.levelMgr.ramps[n].length * coss(self.levelMgr.ramps[n].incline)
        ey = self.levelMgr.collisionGeoms[n]['launch'].p[1] + self.levelMgr.ramps[n].length * sinn(self.levelMgr.ramps[n].incline)

        # Do some super-dirty hack-and-slash 2D line segment/circle collision testing
        # NOTE: We're using read/write references to the level manager's collision geometries. BUT DON'T WRITE
        launch_seg_p = self.levelMgr.collisionGeoms[n]['launch'].p
        launch_seg_v = vSub(Vector(ex, ey, 0), launch_seg_p)    # TODO maybe store as part of plane geom?
        launch_seg_vn = vGetNormalized( launch_seg_v )  # TODO maybe store as part of plane geom?
        launch_seg_e = vLength( vSub(Vector(ex, ey ,0), launch_seg_p) )
        launch_seg_n = self.levelMgr.collisionGeoms[n]['launch'].n
    
        print "====="
        print "Ramp entrance (plane origin): {}".format(self.levelMgr.collisionGeoms[n]['launch'].p)
        print "Ramp plane normal: {}".format(self.levelMgr.collisionGeoms[n]['launch'].n)
        print "Ramp incline: {}".format(launch_seg_vn)
        print "levelMgr y_ground: {}".format(self.levelMgr.y_ground)
        print "Front wheel lowest pt: {}".format(self.bike.model.children['handlebar'].children['wheel'].collisionGeom._minPt[1])
        print "Rear wheel lowest pt: {}".format(self.bike.model.children['frame'].children['wheel'].collisionGeom._minPt[1])
        print

        # Test front wheel collision with ramp (NOTE here, we're trying to get the bike to roll up the ramp.. Currently not working, blah)
        front_collgeom_ctr = Vector( (self.bike.model.children['handlebar'].children['wheel'].collisionGeom._minPt[0] + self.bike.model.children['handlebar'].children['wheel'].collisionGeom._maxPt[0]) / 2.0
                                   , (self.bike.model.children['handlebar'].children['wheel'].collisionGeom._minPt[1] + self.bike.model.children['handlebar'].children['wheel'].collisionGeom._maxPt[1]) / 2.0
                                   , 0.0 )
        print "Front wheel collgeom center: {}".format(front_collgeom_ctr)

        t = vDot(vSub(front_collgeom_ctr, launch_seg_p), vGetNormalized(launch_seg_v)) / launch_seg_e    # The simplicity of this function depends on n being normalized.
        if t < 0.0:     # Note: should put this clamping code in a function.. Really, all of the collision detection code should be in a function
            t = 0.0
        elif t > 1.0:
            t = 1.0

        closest_pt_on_ramp_to_front_wheel_ctr = vAdd( launch_seg_p, vGetScaled(launch_seg_v, t) )
        print "Closest pt on ramp to front wheel: {}".format(closest_pt_on_ramp_to_front_wheel_ctr)

        vec_from_closest_pt_on_ramp_to_front_wheel = vSub(front_collgeom_ctr, closest_pt_on_ramp_to_front_wheel_ctr)
        sqdist_ramp_to_front_wheel = vDot(vec_from_closest_pt_on_ramp_to_front_wheel, vec_from_closest_pt_on_ramp_to_front_wheel)
        ramp_length_along_ground = ex - self.levelMgr.collisionGeoms[n]['launch'].p[0]  # This calculation is a shortcut; normally we would dot( vSub(Vector(ex, ey),collGeom.p ), ground_vec ).. but we've already done the necessary calculations
        print "Vec from closest pt on ramp to front wheel: {}".format(vec_from_closest_pt_on_ramp_to_front_wheel)
        print "Sq dist front wheel to ramp: {}".format(sqdist_ramp_to_front_wheel)
        
        ground_vec = Vector(1,0,0)  # The "ground" is really just the x axis
        wheel_radius = self.bike.wheelAngVel['handlebar'].radius    # NOTE: We're assuming that front wheel and rear wheel have same radius. Don't make this statement false
        
        front_wheel_query_pt = vSub( front_collgeom_ctr, vGetScaled(self.levelMgr.collisionGeoms[n]['launch'].n, wheel_radius) )
        front_wheel_query_vec = vSub( front_wheel_query_pt, front_collgeom_ctr )
        print "front_wheel_query_pt: {}, front_wheel_query_vec: {}".format(front_wheel_query_pt, front_wheel_query_vec)

        # TODO cache the dot product here, to save the redundant call
        if vDot( vSub(front_collgeom_ctr, self.levelMgr.collisionGeoms[n]['launch'].p), Vector(1,0,0) ) > 0.0 and front_wheel_query_pt[0] - self.levelMgr.collisionGeoms[n]['launch'].p[0] <= ramp_length_along_ground:  # TODO test for point on plane; currently does not bound far side of ramp
                                                                        # TODO add extent check
            # If we're here, then the wheel is penetrating the ramp. We have a vector from the center of the wheel to the ramp, the length of which is less than the radius of the wheel.
            # To get the correction vector (to push the wheel back to the surface of the ramp), we'll take a copy of the vector from the wheel to the ramp, and negate it. Then, we'll scale it to the radius.
            # That will give us what we need to compute the correction vector
            #import pdb; pdb.set_trace()
            print "Front wheel is on ramp"
            if self.bike.onRamp == False:
                self.bike.onRamp = True

            bDotN = vDot(front_wheel_query_vec, vec_from_closest_pt_on_ramp_to_front_wheel)
            if bDotN < 0.0:
                pen_len = vLength(vec_from_closest_pt_on_ramp_to_front_wheel)
                if pen_len < wheel_radius:
                    # center of wheel is on + side of ramp, but wheel is intersecting
                    penetration_distance = wheel_radius - pen_len
                else:
                    penetration_distance = 0.0  # Nothing to do; wheel is not intersecting with ramp
            else:
                penetration_distance = vLength( vSub(front_wheel_query_pt, closest_pt_on_ramp_to_front_wheel_ctr) ) 
            correction_vec = vGetScaled(self.levelMgr.collisionGeoms[n]['launch'].n, penetration_distance)        # TODO clean up. collisionGeom.n is the same vector as launch_seg_n. Remove redundancies
            print "Front wheel penetration correction vec: {}".format(correction_vec)

            # Compute a new position for the tire (once we know where the tire should go, we can figure out how to rotate/inverse kinematize the bike to hit that target)
            new_front_wheel_pos = vAdd( front_collgeom_ctr, correction_vec )
        else:
            new_front_wheel_pos = front_collgeom_ctr

        print "Corrected front wheel collision geom center: {}".format(new_front_wheel_pos)
        print


        rear_collgeom_ctr = Vector( (self.bike.model.children['frame'].children['wheel'].collisionGeom._minPt[0] + self.bike.model.children['frame'].children['wheel'].collisionGeom._maxPt[0]) / 2.0
                                  , (self.bike.model.children['frame'].children['wheel'].collisionGeom._minPt[1] + self.bike.model.children['frame'].children['wheel'].collisionGeom._maxPt[1]) / 2.0
                                  , 0.0 )
        print "Rear wheel collgeom center: {}".format(rear_collgeom_ctr)

        ### TODO - Each ramp actually should have 2 planes: 1 for the launch ramp, and 1 for the landing ramp
        t = vDot(vSub(rear_collgeom_ctr, launch_seg_p), vGetNormalized(launch_seg_v)) / launch_seg_e   # The simplicity of this function depends on n being normalized.
        if t < 0.0:     # Note: should put this clamping code in a function.. Really, all of the collision detection code should be in a function
            t = 0.0
        elif t > 1.0:
            t = 1.0

        closest_pt_on_ramp_to_rear_wheel_ctr = vAdd( launch_seg_p, vGetScaled(launch_seg_v, t) )
        print "Closest pt on ramp to rear wheel: {}".format(closest_pt_on_ramp_to_rear_wheel_ctr)

        vec_from_closest_pt_on_ramp_to_rear_wheel = vSub(rear_collgeom_ctr, closest_pt_on_ramp_to_rear_wheel_ctr)
        sqdist_ramp_to_rear_wheel = vDot(vec_from_closest_pt_on_ramp_to_rear_wheel, vec_from_closest_pt_on_ramp_to_rear_wheel)
        print "Vec from closest pt on ramp to rear wheel: {}".format(vec_from_closest_pt_on_ramp_to_rear_wheel)
        print "Sq dist rear wheel to ramp: {}".format(sqdist_ramp_to_rear_wheel)

        rear_wheel_query_pt = vSub( rear_collgeom_ctr, vGetScaled(self.levelMgr.collisionGeoms[n]['launch'].n, wheel_radius) )
        rear_wheel_query_vec = vSub( rear_wheel_query_pt, rear_collgeom_ctr )
        print "rear_wheel_query_pt: {}, rear_wheel_query_vec: {}".format(rear_wheel_query_pt, rear_wheel_query_vec)

        # TODO cache the dot product here, to save the redundant call
        if vDot( vSub(rear_collgeom_ctr, self.levelMgr.collisionGeoms[n]['launch'].p), Vector(1,0,0) ) > 0.0 and rear_wheel_query_pt[0] - self.levelMgr.collisionGeoms[n]['launch'].p[0] <= ramp_length_along_ground:  # TODO test for point on plane; currently does not bound far side of ramp
            #import pdb; pdb.set_trace()
            print "Rear wheel is on ramp"
        ##  if self.bike.onRamp == False:   # NOTE we don't check the rear wheel for on-ramp state (at least, not for launch ramps)
        ##      self.bike.onRamp = True
        ##    # If we're here, then the wheel is penetrating the ramp. We have a vector from the center of the wheel to the ramp, the length of which is less than the radius of the wheel.
        ##    # To get the correction vector (to push the wheel back to the surface of the ramp), we'll take a copy of the vector from the wheel to the ramp, and negate it. Then, we'll scale it to the radius.
        ##    # That will give us what we need to compute the correction vector

            bDotN = vDot(rear_wheel_query_vec, vec_from_closest_pt_on_ramp_to_rear_wheel)
            if bDotN < 0.0:
                pen_len = vLength(vec_from_closest_pt_on_ramp_to_rear_wheel)
                if pen_len < wheel_radius:
                    # center of wheel is on + side of ramp, but wheel is intersecting
                    penetration_distance = wheel_radius - pen_len
                else:
                    penetration_distance = 0.0  # Nothing to do; wheel is not intersecting with ramp
            else:
                penetration_distance = vLength( vSub(rear_wheel_query_pt, closest_pt_on_ramp_to_rear_wheel_ctr) ) 
            correction_vec = vGetScaled(self.levelMgr.collisionGeoms[n]['launch'].n, penetration_distance)        # TODO clean up. collisionGeom.n is the same vector as launch_seg_n. Remove redundancies
            print "rear wheel penetration correction vec: {}".format(correction_vec)

            # Compute a new position for the tire (once we know where the tire should go, we can figure out how to rotate/inverse kinematize the bike to hit that target)
            new_rear_wheel_pos = vAdd( rear_collgeom_ctr, correction_vec )
        else:
            new_rear_wheel_pos = rear_collgeom_ctr

        print "Corrected rear wheel collision geom center: {}".format(new_rear_wheel_pos)
        print

        # TODO also make sure this collision detection stuff works on the down ramps


        # Now, compute the bike's new orientation angle, based on its newly-calculated wheel positions
        # we can compute the angle by comparing the vector pointing from rear wheel to front wheel, to the ground axis (i.e. the +x axis, in this game)
        bike_line = vGetNormalized( vSub(new_front_wheel_pos, new_rear_wheel_pos) )
        print "Bike line (vec from rear wheel ctr to front wheel ctr: {}".format(bike_line)
        thz = math.atan2(bike_line[1], bike_line[0]) * RADTODEG     # You could also use acos of bike_line[0].. atam2 is more useful when the angle can be 0 - 360 deg
        print "New bike z angle (in degrees): {}".format(thz)
        print
        self.bike.model.thz = thz

        print "Bike position: {}".format(self.bike._position)
        print "Bike model position: {}".format(self.bike.model.position)
        print "Known front wheel position (when zrot==0: (0, -5, 0)"
        print

        ## NOTE we know that the front wheel is an offset of (0, -5, 0) from the bike's position, when z rot == 0. We jankily maintain that vector, using hard-coded crap
        ## TODO find a way to not hardcode the computation of bike's position
        bike_pos_correction_dir = vGetNormalized( vCross(Vector(0,0,1), bike_line) )
        print "Bike pos correction vec: {}".format(bike_pos_correction_dir)
        new_bike_pos = vAdd( new_front_wheel_pos, vGetScaled(bike_pos_correction_dir, 5.0) )
        print "New bike pos: {}".format(new_bike_pos)

        self.bike._position = Vector(new_bike_pos[0], new_bike_pos[1], new_bike_pos[2], 1.0)
        self.bike.model.position = Point3D(new_bike_pos[0], new_bike_pos[1], new_bike_pos[2])


        # Adjust the bike's velocity vector
        print "Current velocity: {}".format(self.bike._velocity)
        vel_magnitude = vLength(self.bike._velocity)
        new_velocity = vGetScaled(bike_line, vel_magnitude)
        print "New velocity: {}".format(new_velocity)
        print
        self.bike._velocity = Vector(new_velocity[0], new_velocity[1], new_velocity[2])

        if rear_wheel_query_pt[0] - ex > wheel_radius:
            self.bike.inAir = True
            self.bike.onRamp = False


    #==============================================================================
    #SUB runSummary
    #==============================================================================
    def runSummary(self):
        for msg in self.runSummaryDisplayMsgs:
            textSurfaceScore = msg.getTextSurface(self.mm._font)    # Here we're using the message manager's font
            self.appRef.surface_bg.blit(textSurfaceScore, (msg._position[0], msg._position[1]))


###==============================================================================
###SUB AutoDecel
###This sub handles rolling friction
###The Physics handler will subsume this sub.
###==============================================================================
###TODO replace AutoDecel with physics. There should be whatever is necessary: coefficients of friction etc
##def AutoDecel():
### TODO add params to this function. In the QBASIC version, you made all vars global. Terrible design :-D
##    if not self.bike.inAir:       # self.bike.inAir should be part of the bike object (also TODO: make a bike object :-D)
##        self.rider.xvel = self.rider.xvel - .075
##        if self.rider.xvel <= 0:
##            self.rider.xvel = 0


#==============================================================================
#FUNCTION getBeatLevelMsg()
#This function returns a random beat-the-level phrase
#==============================================================================
def getBeatLevelMsg(successPhrases):
    i = int( random.random() * len(successPhrases) )
    return successPhrases[i]


#==============================================================================
#FUNCTION getCrashedMsg
#Returns a random crash phrase
#==============================================================================
def getCrashedMsg(crashPhrases):
    p = int(random.random() * len(crashPhrases))
    return crashPhrases[p]


#==============================================================================
#FUNCTION getDidNotClearJumpMsg
#Returns a random phrase to describe you not clearing the jump (this is rare,
#but it could happen)
#==============================================================================
def getDidNotClearJumpMsg(rampCrashPhrases):
    p = int(random.random() * len(rampCrashPhrases))
    return rampCrashPhrases[p]


#==============================================================================
#FUNCTION getLostLevelMsg()
#==============================================================================
def getLostLevelMsg(failurePhrases):
    p = int(random.random() * len(failurePhrases))
    return failurePhrases[p]
    





from pymkfgame.core.message_queue import MessageQueue
from pymkfgame.display_msg.display_msg import DisplayMessage
from pymkfgame.display_msg.display_msg_manager import DisplayMessageManager
from pymkfgame.core.game_state_base import GameStateBase
from pymkfgame.mkfmath.common import DEGTORAD, coss, sinn
from pymkfgame.mkfmath.vector import *
from pymkfgame.mkfmath.refframe import *
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

class PlayingSubstate(object):
    """ This class implements an enum that allows the Playing state to keep track of its sub-states (e.g. Load level; playing; player crashed; game over; etc. """
    uninitialized = -1
    startlevel = 0
    playing = 1
    crashed = 2
    resetlevel = 3      # TODO: remove? may not be necessary
    finishlevel = 4
    gameover = 5

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
        self.numTrophies = []   # A list, to be read from/written to file (perhaps dotaccessdict, config file)
        self.scoreToBeat = []   # A list, to be read from/written to file (perhaps dotaccessdict, config file) TODO on second thought, remove this from game stats; it should belong to a level object

        # Options/Config
        self.track3d = True     # load from config file?
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
        self.resetTrickCounters()
        self.activeTrick = 0        # Note: to be consistent the QBASIC version, we'll make activeTrick go from 1 - whatever # of tricks we want. 0 means no active trick
        self.trickMsg = ""          # Message to display while tricking (e.g. prints out the trick combo as you're performing it)

        # End-of-level summary
        self.runReport = []
        self.resetRunReport()
        # TODO make sure to use your resetXYZ helper functions when starting/restarting levels

        # Possibly used for debugging
        self.drawPoints = False

        # Misc
        self.factor = .25   # TODO figure out the purpose of this var.. it's in the original QBASIC code as a hard-coded const

    def resetTrickCounters(self):
        # TODO perhaps also add other stuff into this function, e.g. addScore, numTricks, trickCounter, etc
        if self.timesUsed:  # if list exists already, zero it out
            for i in range(0, self.trickArraySize):
                self.timesUsed[i] = 0
        else:               # if this is the first-time use, then create the list
            for i in range(0, self.trickArraySize):
                self.timesUsed.append(0)

    def resetRunReport(self):
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
    #SUB runSummary
    #==============================================================================
    # TODO make the run summary a part of the post-render stuff, e.g., in a substate, perhaps.
    # TODO hahaaaaa, also uncomment this whole function (runSummary) and implement it
    ##def runSummary:
    ##    range = 3
    ##    flag = 1
    ##    
    ##    DO
    ##        LOCATE 1, 1
    ##        PRINT STRING$(80, "-")
    ##        message 2, "Run Summary for Level " + LTRIM$(STR$(self.levelMgr.currentLevel)), 1
    ##        LOCATE 4, 1: PRINT STRING$(80, "-")
    ##        message 6, "Biker: " + RiderName$, 1
    ##        LOCATE 7: PRINT STRING$(80, "-")
    ##        LOCATE 8, 1
    ##        FOR n = flag TO flag + range        #self.levelMgr.trickCounter
    ##            PRINT TAB(3); LTRIM$(STR$(n));
    ##            PRINT TAB(10); RunReport$(n)
    ##        NEXT n
    ##        PRINT
    ##        PRINT STRING$(80, "-")
    ##        PRINT TAB(3); "Total: "; TAB(10); LTRIM$(STR$(gamestats.score)); " pts.";
    ##        PRINT TAB(30); "<I and K> scroll, <Enter> continues."
    ##        PRINT STRING$(80, "-")
    ##        
    ##        message 23, "Press <Enter> to continue.", 1
    ##        bike.draw()
    ##        self.levelMgr.drawLevel()
    ##        PCOPY 1, 0: CLS
    ##        
    ##        a$ = INKEY$
    ##        SELECT CASE UCASE$(a$)
    ##            CASE "I"
    ##                flag = flag - 1
    ##                if flag < 1 : flag = 1
    ##            CASE "K"
    ##                flag = flag + 1
    ##                if flag > self.levelMgr.trickCounter - range : flag = self.levelMgr.trickCounter - range
    ##            CASE CHR$(13)
    ##                EXIT SUB
    ##            END SELECT
    ##        
    ##    LOOP
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
        self.substate = PlayingSubstate.startlevel  # TODO decide if you prefer to have an object with constructor/methods/etc
        self.appRef = appRef
        self.kbStateMgr = KeyboardStateManager()

        self.levelMgr = LevelManager()
        self.mm = DisplayMessageManager()   # TODO - maybe make names more descriptive? DisplayMessageManager is for (and only for) event-based messages that will appear for some amount of time, then disappear

        self.staticMsg = {}            # a dict to store static DisplayMessage objects ("static" means they appear indefinitely as opposed to DisplayMessageManager messages, which expire after some time)
        self.InitializeStaticMessages()

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
        self.staticMsg['score'].create(txtStr="Score: ", position=[50, 10], color=(192, 64, 64))

        self.staticMsg['level'] = DisplayMessage()
        self.staticMsg['level'].create(txtStr="Level: ", position=[150, 10], color=(192, 64, 64))

        self.staticMsg['scoreToBeat'] = DisplayMessage()
        self.staticMsg['scoreToBeat'].create(txtStr="Score to beat: ", position=[250, 10], color=(192,64,64))

        self.staticMsg['speed'] = DisplayMessage()
        self.staticMsg['speed'].create(txtStr="Speed: ", position=[5,10], color=(192,64,64))

        self.staticMsg['info'] = DisplayMessage()   # This message will be used for crash/pass level/fail level/etc. messages
        self.staticMsg['info'].create(txtStr="", position=[320, 200], color=(192,64,64))

        self.staticMsg['presskey'] = DisplayMessage()   # This message will be used for crash/pass level/fail level/etc. messages
        self.staticMsg['presskey'].create(txtStr="", position=[320, 400], color=(192,64,64))


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
            print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                print "DEBUG Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

                # Evaluate the 'action' key to know what to do. The action dictates what other information is required to be in the message
                if msg['payload']['action'] == 'call_function':
                    # The registered listener had better have the function call available heh... otherwise, kaboom
                    objRef = listener_obj_dict['ref']
                    fn_ptr = getattr(objRef, msg['payload']['function_name'])
                    argsDict = eval("dict({})".format(msg['payload']['params']))    # params should be a comma-separated list of key=value pairs, e.g. "a = 5, b = 3"

                    print "function args: {}".format(argsDict)
                    if argsDict:
                        # In this particular gamestate, we want an argsdict to translate to kwargs. This is because the mixer class is written with kwargs (other classes in other gamestates use dicts, in which case, we pass in argsDict as-is))
                        fn_ptr(self, **argsDict)
                    else:
                        fn_ptr(self)

            msg = self._eventQueue.Dequeue()

    def Update(self, dt_s):
        # TODO put in fixed timestep updating. We want to update every cycle, but only draw when it's time to
        # TODO note: there are probably things that should ALWAYS happen in the Update function, no matter the substate (e.g. message manager updates?
        self.mm.update(dt_s)    # TODO possibly also pass in a reference to the gameplay stats object? (that's how we did it Falldown)

        if self.substate == PlayingSubstate.startlevel:
            # TODO break playingsubstates into their own functions, maybe
            # Initialize bike
            self.bike.Init()    # TODO move this out of update()? I'm not sure I like having it here # TODO evaluate -- do we need to totally reinit here (Init() loads the model from disk.. Might be overkill)
            self.bike._position = vector.Vector(320, self.levelMgr.y_ground, 0, 1)        # TODO make a function that synchronizes bike _position with bike model position
            self.bike.model.position = Point3D(320, self.levelMgr.y_ground, 0)  # Also TODO: do camera/projection model view
            self.bike._velocity = vector.Vector(0,0,0)
            self.bike._acceleration = vector.Vector(0,0,0)

            self.bike.rider.maxspd = 130.0  # TODO don't hardcode biker abilities
            self.bike.rider.pump = 12.0     # TODO don't hardcode biker abilities
            self.bike.rider.jump = 3.0      # TODO don't hardcode biker abilities
            self.bike.rider.turn = 180.0    # degrees per second # TODO don't hardcode biker abilities

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
            self.levelMgr.currentLevel = 1   # TODO don't hardcode the level here. Set self.levelMgr.currentLevel = 1 at game init, then increment
            self.levelMgr.InitLevel()
            self.mm.setMessage("Level {}!".format(self.levelMgr.currentLevel), [ 400, 300 ], (192, 64, 64), 5 )  # TODO un-hardcode the render position of the message. But otherwise, use this as a template to replace other message and doMessage calls

            self.substate = PlayingSubstate.playing # TODO maybe put a couple of seconds' delay before substate change, or maybe require a keypress
        elif self.substate == PlayingSubstate.playing:
            ## TODO note/correct - there is some redundancy between the RiderType class and the Bike class. e.g., RiderType has xvel, and Bike have velocity Vector (which has an x component)
    
            self.bike.update(dt_s)
            self.refFrame.setPosition(-self.bike._position[0], 0, 0) # Move the camera (follow the bike) (note the negative sign..)
            self.checkRamp(self.levelMgr.curRamp)    # TODO possibly move the checkRamp call into the playing substate?

            if self.bike.inAir:
                # This is rudimentary "collision detection" (more like a boundary test) for determining when the bike lands (self.levelMgr.y_ground is ground level)

                if self.bike._velocity[1] < 0 and self.bike.aabb._minPt[1] <= self.levelMgr.y_ground:  # TODO make sure that biker's yvel is 0 when on the ground; otherwise this test will trigger false positives
                    # If you're here, you've landed
                    self.bike._position[1] = self.levelMgr.y_ground# - 30
                    self.bike._velocity[1] = 0.0
                    self.gamestats.activeTrick = 0

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

                    DidNotClearRamp = self.bike.aabb._minPt[0] < land_ex    # You didn't clear the jump if you land before the lip of the landing ramp # TODO make the landing calculation more robust. Should be able to land on the ramp
            
                    #import pdb; pdb.set_trace()
                    if self.bike.tricking or DidNotClearRamp :
                        msg = ""
                        if self.bike.tricking :
                            self.staticMsg['info'].changeText(getCrashedMsg(self.gamestats.crashPhrases))
                            # NOTE: we only set the message here. The drawStatus function will render the message.  But also NOTE: we'll need to make sure to clear out the txtStr property to clear out messages (e.g. "You crashed" messages)
                        else:
                            self.staticMsg['info'].changeText(getDidNotClearJumpMsg(self.gamestats.rampCrashPhrases))
                        # Aside: I know the code is weird in this game; I'm porting from QBASIC.. give me a break
                        self.staticMsg['presskey'].changeText("Press <Enter> to continue.")
                        self.bike.crashed = True
                        self.bike._position[1] = self.levelMgr.y_ground - 15
            
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
                        self.gamestats.score = self.gamestats.score + self.gamestats.addScore
                        self.gamestats.addScore = 0
                        self.gamestats.numTricks = 0
                        self.bike.model.thz = 0                         # Set the parent transformation to 0 deg about Z
                        self.bike.model.children['frame'].thz = 0       # TODO: evaluate: is it necessary to also set child transforms after the parent transform? Probably yes
                        self.bike.model.children['handlebar'].thz = 0
                        one = 15        #Tab stops
            
                    if self.bike.crashed:
                        self.substate = PlayingSubstate.crashed
                    else:
                        self.levelMgr.curRamp += 1   # TODO manage curRamp better. Maybe take a BSP-type approach? i.e, look at all ramps, but only process a ramp is the bike's x pos < ramp's x pos
                    # NOTE the following substate change logic could just as easily go into a function (and maybe should?)

                if self.levelMgr.curRamp == len(self.levelMgr.ramps):  # You've finished the level
                    #import pdb; pdb.set_trace()
                    # TODO Make the end-of-level work without the crashing the program
                    self.staticMsg['presskey'].changeText("Press <Enter> to continue.")
            
                    if self.gamestats.score >= self.levelMgr.scoreToBeat:
                        self.levelMgr.levelFinished = True  # TODO evaluate whether this flag is necessary. If we need to stay in the level state for a while, then keep it. But if it makes more sense to increment the level counter here, and go to a new substate, then do that
                        # TODO as always, look at what function is being called here
                        self.staticMsg['info'].changeText(getBeatLevelMsg(self.gamestats.successPhrases))
                        # TODO add level increment here - level += 1; initlevel; etc
                        self.substate = PlayingSubstate.finishlevel
            
                    else:
                        self.substate = PlayingSubstate.startlevel
                        self.staticMsg['info'].changeText(getLostLevelMsg(self.gamestats.failurePhrases))
                    # TODO wait for keypress here? Should there be substates for all these little things, like a substate for game-finished-at-first, and then for game-still-finished-show-run-summary, etc?
                    #WHILE INKEY$ <> CHR$(13): WEND
            
                    if self.gamestats.doRunSummary:
                        if self.levelMgr.levelFinished:
                            self.gamestats.runSummary()

        elif self.substate == PlayingSubstate.crashed:
            # If we crashed, then wait here for user input, then go back to startLevel

            #self.bike.Init()    # TODO evaluate -- do we need to totally reinit here (Init() loads the model from disk.. Might be overkill)
            #self.levelMgr.InitLevel(self.levelMgr.currentLevel)    # TODO replace with level manager

            # TODO make sure this clearing stuff is at the end of the substate? After user has presed any key to continue or whatever?
            self.mm.clear()
            self._eventQueue.Clear()
            self._eventQueue.Initialize(64) # TOOD perhaps don't hardcode the # of events that can be handled by this queue

            self.bike.model.resetModelTransform()
    
            #self.substate = PlayingSubstate.resetlevel     # TODO remove? Probably don't need PlayingSubstate.resetlevel
            self.substate = PlayingSubstate.startlevel
            # TODO perhaps wait for user input? (put that logic into ProcessEvents)

        elif self.substate == PlayingSubstate.finishlevel:
            # TODO make sure the game switches into this substate
            if self.levelMgr.LevelFinished:		# TODO make LevelFinished a vital stat (and probably also make the LevelManager aware of it? Not exactly sure how to handle this just yet
                self.levelMgr.currentLevel = self.levelMgr.currentLevel + 1
            
                if self.levelMgr.currentLevel > self.levelMgr.finalLevel:
                    self.staticMsg['info'].changeText("GAME OVER")
                    self.staticMsg['presskey'].changeText("Press <Enter> to return to main menu.")
                 
                    # TODO still review this code. Most of it was written in QBASIC days, when you really sucked at programming
                    if self.numTrophies[BikeStyle] < 2:	# NOTE: here, BikeStyle operates like "SelectedRider"
	        			# write trophy data to file
                        self.numTrophies[BikeStyle] += 1
            
                        self.staticMsg['info'].changeText("Congratulations, you got a trophy!!!")

                        #OPEN "trophies.dat" FOR OUTPUT AS #1    # TODO don't delete this; pythonize file output
                        #    FOR n = 1 TO 13
                        #        PRINT #1, CHR$(ASC(LTRIM$(STR$(self.numTrophies[n]))) + 128)
                        #    NEXT n
                        #CLOSE
        elif self.substate == PlayingSubstate.gameover:
            #TODO high scores
            #TODO go back to main menu (state change; not a mere substate change)
            pass

    def PreRenderScene(self):
        pass

    def RenderScene(self):
        # TODO put in fixed timestep updating / some time of timer class. We want to update every cycle, but only draw when it's time to. Something like: if timer.timeToDraw: draw it else: return
        # TODO all objects should update their vertices based on view transforms here. Ideally, we should use a vertex buffer to combine all renderable vertices, and then apply the xform to the buffer.. But, we're not there yet
        self.appRef.surface_bg.fill((0,0,0))

        # Set up viewport transformation # TODO put viewport transformation into a class?
        screensize = self.appRef.surface_bg.get_size()

        xmin_vp = 0 # xmin for the viewport
        xmax_vp = screensize[0]

        ymin_vp = 0
        ymax_vp = screensize[1]

        xmin_world = -300   # world coords will be mapped into the viewport space
        xmax_world = 300

        ymin_world = -200
        ymax_world = 200

        m_x = float(xmax_vp - xmin_vp) / float(xmax_world - xmin_world)     # m for linear equation form y = mx + b
        b_x = float(xmin_vp + xmax_vp) / float(2)                           # b for linear equation form y = mx + b

        m_y = float(ymax_vp - ymin_vp) / float(ymax_world - ymin_world)
        b_y = float(ymin_vp + ymax_vp) / float(2)


        # NOTE viewport matrix defines how the already-projected gameworld will appear on the screen
        viewportMatrix = matrix.Matrix(m_x, 0, 0, 0,
                                       0, m_y, 0, 0,
                                       0, 0, 0, 0,
                                       b_x, b_y, 0, 1)

        # Get the view matrix (i.e. camera view)
        #viewMatrix = self.refFrame.getMatrix()     # This matrix works.
        #viewMatrix = self.refFrame.getLookAtMatrix(self.bike._position[0], -self.bike._position[1], 250, self.bike._position[0], self.bike._position[1], 0, 0, -1, 0)  # experimental

        #viewMatrix = self.refFrame.getLookAtMatrix(self.bike._position[0], -self.bike._position[1], 250, self.bike._position[0], -self.bike._position[1], 0, 0, -1, 0)  # Camera jumps with bike
        viewMatrix = self.refFrame.getLookAtMatrix(self.bike._position[0], 10.0, 250, self.bike._position[0], self.bike._position[1], 0, 0, -1, 0)  # Camera stays on ground, looks up at bike on jumps

        projectionMatrix = self.refFrame.getPerspectiveProjectionMatrix(28.0, screensize[0] / screensize[1], 0.5, 25.0)


        #import pdb; pdb.set_trace()
        # TODO View first, then projection, then viewport
        #composedViewportAndView = matrix.mMultmat(viewportMatrix, viewMatrix)

        composedProjAndView = matrix.mMultmat(projectionMatrix, viewMatrix)
        composedViewportAndView = matrix.mMultmat(viewportMatrix, composedProjAndView)

        self.levelMgr.drawLevel(self.appRef.surface_bg, self.gamestats, matView=composedViewportAndView)
        self.bike.draw(self.appRef.surface_bg, matView=composedViewportAndView)

        #self.levelMgr.drawLevel(self.appRef.surface_bg, self.gamestats, matView=viewMatrix)
        #self.bike.draw(self.appRef.surface_bg, matView=viewMatrix)

    def PostRenderScene(self):
        self.drawStatus(self.appRef.surface_bg)    # TODO: Pythonize. status can be an overlay on the game window
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
        
        # TODO what color are B and BF?? Maybe they're set by the bike colors?? I can't remember :-S. Pretty sure B mean bar color, and BF means bar fill color, or something like that.
        #LINE (bx - 1, by)-(bx + l + 1, by + w), BikeCol(1), B
        #LINE (bx, by + 1)-(bx + l * (self.bike._velocity[0] / self.bike.rider.maxspd), by + w - 1), BikeCol(2), BF

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

        if self.staticMsg['info']._text:   # Render info message if it exists
            textSurfaceInfo = self.staticMsg['info'].getTextSurface(self.mm._font)
            self.appRef.surface_bg.blit(textSurfaceInfo, (self.staticMsg['info']._position[0], self.staticMsg['info']._position[1]))

        if self.staticMsg['presskey']._text:   # Render info message if it exists
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
                        self.bike.memAngle = self.bike.model.children['handlebar'].thy  # Use handlebar angle because this trick is a handlebar spin
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


        
    #==============================================================================
    #SUB checkRamp ()
    #Rudimentary collision detection -- test whether the bike has hit a ramp
    #==============================================================================
    #TODO replace with collision detection and trigonometry
    def checkRamp(self, n):
        # TODO pick up from here -- fix the CheckRamp function to be Python-compliant.
        if self.bike.inAir:
            return
    
        # TODO List of Ramp objects should belong to the Level object (also TODO: make a Level object :-D)
        sx = self.levelMgr.ramps[n].x
        sy = self.levelMgr.ramps[n].y
        ex = self.levelMgr.ramps[n].x + self.levelMgr.ramps[n].length * coss(360 - self.levelMgr.ramps[n].incline)
        ey = self.levelMgr.ramps[n].y + self.levelMgr.ramps[n].length * sinn(360 - self.levelMgr.ramps[n].incline)
    
        if self.bike.aabb._maxPt[0] > sx: # remember, _maxPts is a tuple, with no .x, .y, or .z attributes
            #import pdb; pdb.set_trace()
            #self.bike.model.thz = 360 - self.levelMgr.ramps[n].incline # set the top-level rotation angle (which will be processed when we need to know where points are, for drawing/colliding)
    
            #self.bike._velocity[1] = self.bike.rider.jump * (self.bike._velocity[0] * sinn(self.bike.model.thz)) + 2.25    #1.5707 # TODO do better math than this. You came up with these numbers just through trial and error.. what looked good
            #self.bike._velocity[0] = self.bike._velocity[0] * coss(self.bike.model.thz)
            y = ey - 18 # TODO: Fix. Don't hardcode bike's y-position when jumping. Use collision detection, or otherwise math formulas to determine the bike's position on the ramp
    
            self.bike.model.thz = self.levelMgr.ramps[n].incline # set the top-level rotation angle (which will be processed when we need to know where points are, for drawing/colliding)
    
            self.bike._velocity[1] = self.bike.rider.jump * (self.bike._velocity[0] * sinn(self.bike.model.thz))    #1.5707 # TODO do better math than this. You came up with these numbers just through trial and error.. what looked good
            self.bike._velocity[0] = self.bike._velocity[0] * coss(self.bike.model.thz)
            self.bike.inAir = True




# TODO replace this level initialization stuff with something else.. In the game playing state, there should be a point at which the game loads a new level, restarts the current level, etc.
#=-=-=-=-=-=-=-=-=

# NOTE: MainMenu is the main menu. Once the main menu exits, the game begins. In QBASIC, you had put the entire game at level 0 (i.e., it's not in a function or anything).


##DO      # TODO pythonize. This is where the game loop starts. Perhaps it should be the PlayingState
##    AutoDecel()     # TODO replace AutoDecel hackery with proper physics. Should be in bike.update()
##    
##LOOP        # TODO pythonize. This is where the game loop ends


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
    





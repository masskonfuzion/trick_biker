#==============================================================================
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

        # Possibly used for debugging
        self.drawPoints = False

    def loadTrophies(self):
        ## TODO convert file i/o to Python
        ## NOTE: You did some hackage to compute a # of trophies won, using 'extended' ascii characters ( > 128)
        ## THe problem is: back in the day, QBASIC used an encoding called cp437 (a.k.a. DOS United States).
        ## Nowadays, a more common encoding is a different one: UTF-8. We'll need to re-work the i/o here
        #OPEN "trophies.dat" FOR INPUT AS #1
        #    FOR n = 1 TO 13
        #        INPUT #1, Temp$
        #        NumTrophies(n) = VAL(CHR$(ASC(Temp$) - 128))
        #    NEXT n
        #CLOSE
        
        ## TODO un-hardcode the initialization here, and make file i/o (move into GameplayStats class)
        for i in range(0, 14):  # 14 bikers with which to earn trophies (i.e., finish the game)
            NumTrophies[i] = 0
        
        
        ## TODO fix this crap -- there's no reason to loop through this; once you have trophies loaded from file, you can simply check 
        #=-=-=-=-=-=-=-=-=
        #Check to see if player has gotten secret biker #1
        #=-=-=-=-=-=-=-=-=
        StopFlag = False
        for n in range(1, 11 + 1):    #TODO: don't hardcode. Research your code - why 1 - 11?
            if NumTrophies(n) < 1:
                StopFlag = True
                break
        if not StopFlag:
            self.maxBikes = 12   # TODO Don't do this..; instead have the max be whatever it's going to be, and specify whether the bike is locked or unlocked (e.g. keep a list of biker/character objects, where the bonus characters start off with locked=True, or something)
        
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


# TODO replace this level initialization stuff with something else.. In the game playing state, there should be a point at which the game loads a new level, restarts the current level, etc.
#=-=-=-=-=-=-=-=-=

bike = Bike()   # TODO make sure variable scoping and/or function parameters are straight
bike.Init()

gamestats = GameplayStats()  # TODO make sure variable scoping and/or function parameters are straight

# TODO use game state management like from Falldown

# NOTE: MainMenu is the main menu. Once the main menu exits, the game begins. In QBASIC, you had put the entire game at level 0 (i.e., it's not in a function or anything).

# TODO: Convert the MainMenu() function call a game_state change. Put game play into a game loop.
Level = 1
bike.Init()
InitLevel(Level)

CONST AnnounceFrames = 25 # TODO replace with a timer (see Falldown x64. In QBASIC, We used to be able to rely on VSYNC, so we could specify a number of frames to wait, to use as a timer. Nowadays, it's better to use a timer
LocateRow = 12  # TODO replace with display_msg and display_msg_manager. LOCATE is a qbasic-only thing

# Note: here, you're displaying a "Level n" message at the start of the level. Use display messages
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

    if bike.crashed:					# TODO put Crash into game vital stats
        bike.Init()
        InitLevel(Level)
    
    if LevelFinished:		# TODO make LevelFinished a vital stat
        bike.Init()
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
			bike.draw()
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
    if bike.tricking:
        DoTrick(Trick)
    CALL RotateBike(Txf, Tyf + 180, Tzf)
    CALL RotateBar(Txh, Tyh + 180, Tzh)
    
    doMessage LocateRow, msg, MsgFrames
    
    Move  #Animate
    CALL CheckRamp(CurRamp)
    
    #if FPS >= 10:   #try to speed things up on slower computers
    DrawLevel()
    bike.draw()
    DrawStatus()    # TODO: status can be an overlay on the game window
    PCOPY 1, 0: CLS
    #END IF
    
    AutoDecel()     # TODO replace AutoDecel hackery with proper physics
    
LOOP        # TODO pythonize. This is where the game loop ends


#==============================================================================
#SUB AutoDecel
#This sub handles rolling friction
#The Physics handler will subsume this sub.
#==============================================================================
#TODO replace AutoDecel with physics. There should be whatever is necessary: coefficients of friction etc
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
#TODO replace with collision detection and trigonometry
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
#FUNCTION getCrashedMsg
#Returns a random crash phrase
#==============================================================================
def getCrashedMsg():
    # TODO: Perhaps crashPhrases should belong to the game object
    p = int(random.random() * len(crashPhrases)) + 1
    return crashPhrases[p]


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
                bike.tricking = 0
                msg = "360 Turn!!!"
            END IF
    
        CASE 2                #Tailwhip
            Tyf = Tyf + Biker.turn
            Tzf = Tzf + 1
            Tzh = Tzh + 1
            if Tyf MOD 360 = 0:
                bike.tricking = 0
                msg = "Tailwhip!!!"
            END IF
    
        CASE 3                #180 degree barturn
            if bike.trickPhase = 1:
                Tyh = Tyh + Biker.turn
            if bike.trickPhase = 6:
                Tyh = Tyh - Biker.turn
         
            Tzf = Tzf + 1
            Tzh = Tzh + 1
         
            if Tyh MOD 90 = 0:
                bike.trickPhase = bike.trickPhase + 1
            if Tyh = MemAngle:
                bike.tricking = 0
                MemAngle = 0
                bike.trickPhase = 1
                msg = "X-Up!!!"
            END IF
    
        CASE 4                #360 degree barspin
            Tyh = Tyh + Biker.turn
            if Tyh MOD 360 = 0:
                bike.tricking = 0
                msg = "Barspin!!!"
            END IF
            Tzf = Tzf + 1
            Tzh = Tzh + 1
    
        CASE 5                #Backflip
            tfactor = 5 / 2
            Tzf = Tzf - Biker.turn / tfactor
            Tzh = Tzh - Biker.turn / tfactor
            if Tzf <= MemAngle - 330:
                bike.tricking = 0
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
                bike.tricking = 0
                msg = "Inverted 180!!!"
            END IF
    
        CASE 7            #Corkscrew (don't try this at home)
            Txf = Txf + Biker.turn / 2
            Txh = Txh + Biker.turn / 2
            Tzf = Tzf + 1: Tzh = Tzh + 1
    
            if Txf MOD 360 = 0:
                bike.tricking = 0
                msg = "Corkscrew!!!"
            END IF
    
        CASE 8            #Double Barspin Tailwhip
            Tyf = Tyf - Biker.turn
            Tyh = Tyh + Biker.turn * 2
            Tzf = Tzf + 1
            Tzh = Tzh + 1
    
            if Tyf MOD 360 = 0:
                bike.tricking = 0
                msg = "Double Barspin/Tailwhip!!!"
            END IF
        
        CASE 9            #Wicked Tabletop
            if bike.trickPhase = 1:
                Txf = Txf + Biker.turn / 2
                Txh = Txh + Biker.turn / 2
            END IF
            if bike.trickPhase = 5:
                Txf = Txf - Biker.turn / 2
                Txh = Txh - Biker.turn / 2
            END IF
         
            Tzf = Tzf + 2
            Tzh = Tzh + 2
         
            if Txf MOD 90 = 0:
                bike.trickPhase = bike.trickPhase + 1
            if Txf MOD 360 = 0:
                bike.tricking = 0
                bike.trickPhase = 1
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
                bike.tricking = 0
                MemAngle = 0
                bike.trickPhase = 1
                msg = "Twisting Corkscrew!!!"
            END IF
    
            CASE 11             #Backflip Tailwhip
                if bike.trickPhase = 1 OR bike.trickPhase = 2 OR bike.trickPhase = 3:
                    Tzf = Tzf - Biker.turn * (1 / 3)
                    Tzh = Tzh - Biker.turn * (1 / 3)
                END IF
    
                if bike.trickPhase = 1 AND Tzf <= MemAngle - 90:
                    bike.trickPhase = 2
    
                if bike.trickPhase = 2:
                    Tyf = Tyf + Biker.turn / (3 / 2)
                END IF
    
                if bike.trickPhase = 2 AND Tyf MOD 360 = 0:
                    bike.trickPhase = 3
    
                if Tzf <= MemAngle - 330:
                    bike.tricking = 0
                    MemAngle = 0
                    bike.trickPhase = 1
                    msg = "Backflip Tailwhip!!!"
                END IF
         
            CASE 12                     #360 turn + 360 barspin
            Tzf = Tzf + 1
            Tzh = Tzh + 1
                if bike.trickPhase = 1:
                    Tyf = Tyf + Biker.turn / 2
                    Tyh = Tyh + Biker.turn / 2
                END IF
                if bike.trickPhase = 2:
                    Tyh = Tyh - Biker.turn
                END IF
                if bike.trickPhase = 3: 
                    Tyf = Tyf + Biker.turn / 2
                    Tyh = Tyh - Biker.turn
                END IF
    
                if bike.trickPhase = 1 AND Tyf MOD 180 = 0:
                    bike.trickPhase = 2
                if bike.trickPhase = 2 AND Tyh MOD 360 = 0:
                    bike.trickPhase = 3
                if bike.trickPhase = 3 AND Tyf MOD 360 = 0:
                    bike.tricking = 0
                    bike.trickPhase = 1
                    msg = "360 Turn + Barspin!!!"
                END IF
    
            CASE 13                         #Air Endo
                if bike.trickPhase = 1:
                    Tzf = Tzf + Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
                if bike.trickPhase > 4:
                    Tzf = Tzf - Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
    
                if Tzf >= MemAngle + 60:
                    bike.trickPhase = bike.trickPhase + 1
                if bike.trickPhase > 4 AND Tzf <= MemAngle + 30:
                    bike.tricking = 0
                    bike.trickPhase = 1
                    MemAngle = 0
                    msg = "Air Endo!!!"
                END IF
    
            CASE 14                         #Air Endo plus bar twist
                if bike.trickPhase = 1:
                    Tzf = Tzf + Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
             
                if bike.trickPhase = 1 AND Tzf >= MemAngle + 60:
                    bike.trickPhase = 2
                if bike.trickPhase = 3 AND Tyh MOD 360 = 0:
                    bike.trickPhase = 4
    
                if bike.trickPhase = 2:
                    Tyh = Tyh - Biker.turn / 2
                END IF
            
                if (bike.trickPhase = 2 OR bike.trickPhase = 3) AND Tyh MOD 180 = 0:
                    bike.trickPhase = bike.trickPhase + 1
    
                if bike.trickPhase = 3:
                    Tyh = Tyh + Biker.turn / 2
                END IF
    
                if bike.trickPhase = 4:
                    Tzf = Tzf - Biker.turn * (1 / 4)
                    Tzh = Tzf
                END IF
         
                
                if bike.trickPhase = 4 AND Tzf <= MemAngle + 30:
                    bike.tricking = 0
                    bike.trickPhase = 1
                    MemAngle = 0
                    msg = "Air Endo + Bar Twist!!!"
                END IF
    
            CASE 15                 #Turndown
                if bike.trickPhase = 1:
                    Tyf = Tyf - Biker.turn * (1 / 2)
                    Tzf = Tzf + Biker.turn * (1 / 2)
                    Tzh = Tzh + Biker.turn * (1 / 2)
                END IF
                
                if Tyf MOD 90 = 0:
                    bike.trickPhase = bike.trickPhase + 1
    
                if bike.trickPhase = 6:
                    Tyf = Tyf + Biker.turn * (1 / 2)
                    Tzf = Tzf - Biker.turn * (1 / 2)
                    Tzh = Tzh - Biker.turn * (1 / 2)
                END IF
    
                if bike.trickPhase = 6 AND Tyf MOD 360 = 0:
                    Tzf = Tzf + 30
                    Tzh = Tzf
                    bike.trickPhase = 1
                    bike.tricking = 0
                    msg = "Turndown!!!"
                END IF
    
                #Tzf = 80: Txf = 0
                #Tyh = 0: Tzh = Tzf: Txh = 0
    
            CASE 16             #Flair
                if bike.trickPhase = 1: #OR bike.trickPhase = 3
                    Tzf = Tzf - (Biker.turn * .4)
                    Tzh = Tzh - (Biker.turn * .4)
                END IF
    
                if bike.trickPhase = 3:
                    Tzf = Tzf - (Biker.turn * .5)
                    Tzh = Tzh - (Biker.turn * .5)
                END IF
    
                if bike.trickPhase = 1 AND Tzf <= MemAngle - 135:
                    bike.trickPhase = 2
    
                if bike.trickPhase = 2:
                    Tzf = Tzf - (Biker.turn * .25)
                    Tzh = Tzh - (Biker.turn * .25)
    
                    Tyf = Tyf + (Biker.turn * .5)
                    Tyh = Tyh + (Biker.turn * .5)
                END IF
    
                if bike.trickPhase = 2 AND Tyf MOD 360 = 0:
                    bike.trickPhase = 3
    
                if bike.trickPhase = 3 AND Tzf <= MemAngle - 330:
                    bike.tricking = 0
                    bike.trickPhase = 1
                    MemAngle = 0
                    msg = "Flair!!!"
                END IF
    
    
    END SELECT
    
     
    
        if bike.tricking = 0 :
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
    
    LOCATE 1, 25: PRINT "Score: "; LTRIM$(STR$(gamestats.score))
    LOCATE 1, 40: PRINT "Level "; LTRIM$(STR$(Level))
    LOCATE 1, 50: PRINT "Score to beat = "; LTRIM$(STR$(ScoreToBeat(Level))); " pts."
    #LOCATE 2, 1: PRINT FPS
    END SUB


#==============================================================================
#SUB InitLevel (lev)
#==============================================================================
def InitLevel(lev):
    # TODO perhaps move levels into text files? Or perhaps into a separate module?
    # TODO convert to file i/o. Score-to-beat stuff should belong in a level object, perhaps
    # TODO also, watch out for QBASIC 1-based stuff.. you were an amateur when you made this
    RESTORE ScoresToBeat
    for n = 1 TO FinalLevel
        READ ScoreToBeat(n)  # TODO move ScoreToBeat into the level manager
    NEXT n

    z = -60        			#z offset: keep this around -50 or -60
    AddScore = 0        	# AddScore appears to be the score? Belongs in a game stats class
    Scale = 120         	# Scale is used in Rotate functions. May need to substitute a camera class?
    LevelFinished = False  	# LevelFinished belongs in a game stats class or a level manager
    CurRamp = 1         	# The current ramp in the level (this probably won't be necessary once we have legit collision detection
    NumTricks = 0       	# Tracks how many tricks the player has performed (belongs in game stats class)
    MsgFrames = 0       	# Used in messaging (how many frames to leave the message up for)
    msg = ""           		# Used in messaging - the message text itself
    InAir = 0           	# True if biker is in the air (after a jump)
    TrickCounter = 0    	# Hmm, not sure how this differs from NumTricks. TODO read the code


    x = 120                 # Bike position on screen
    y = StandardY - 20 - 10

    Txf = 0                 # Bike Euler angles TODO replace bike Eulers with rotation matrices
    Txh = 0

    Tyf = 0
    Tyh = 0

    Tzf = 0
    Tzh = 0

    # TODO make sure variable scoping is correct. You went through a pass of simply converting loose variables into object-oriented objects/members/etc
    bike.reset()

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

ScoresToBeat:
DATA 1000     : #Score to beat for level 1
DATA 1350     : #Score to beat for level 2
DATA 1250
DATA 1500
DATA 1900
DATA 1000



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
        if InAir AND not bike.tricking:
            Trick = 1
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "J"
        if InAir AND not bike.tricking:
            Trick = 2
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "k"
        if InAir AND not bike.tricking:
            Trick = 3
            bike.tricking = -1
            MemAngle = Tyh
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "K"
        if InAir AND not bike.tricking:
            Trick = 4
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
        CASE "i"
        if InAir AND not bike.tricking:
            Trick = 5
            bike.tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "I"
        if InAir AND not bike.tricking:
            Trick = 16
            bike.tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "u"
        if InAir AND not bike.tricking:
            Trick = 7
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "U"
        if InAir AND not bike.tricking:
            Trick = 9
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "o"
        if InAir AND not bike.tricking: 
            Trick = 8
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
     
    CASE "O"
        if InAir AND not bike.tricking:
            Trick = 10
            bike.tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "h"
        if InAir AND not bike.tricking:
            Trick = 11
            bike.tricking = -1
            NumTricks = NumTricks + 1
            MemAngle = Tzf
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "H"
        if InAir AND not bike.tricking:
            Trick = 12
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "y"
        if InAir AND not bike.tricking:
            Trick = 13
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
            MemAngle = Tzf
        END IF
    
    CASE "Y"
        if InAir AND not bike.tricking:
            Trick = 14
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
            MemAngle = Tzf
        END IF
    
    CASE "n"
        if InAir AND not bike.tricking:
            MemAngle = Tzf
            Trick = 15
            bike.tricking = -1
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    CASE "N"
        if InAir AND not bike.tricking:
            Trick = 6
            bike.tricking = -1
            MemAngle = Tzf
            NumTricks = NumTricks + 1
            TrickCounter = TrickCounter + 1
        END IF
    
    
    #Lean back
    CASE "q"
        if InAir AND not bike.tricking:
            Tzf = Tzf - Biker.turn / 2
            Tzh = Tzh - Biker.turn / 2
    
    #Lean forward
    CASE "w"
        if InAir AND not bike.tricking:
            Tzf = Tzf + Biker.turn / 2
            Tzh = Tzh + Biker.turn / 2
    
    CASE "p", "P"
    if gamestats.paused == 0:
        doMessage LocateRow, msg, MsgFrames
        s$ = "-=* PHAT FREEZE FRAME SNAPSHOT *=-"
        LOCATE 6, 41 - LEN(s$) / 2: PRINT s$
        DrawLevel
        bike.draw()
        DrawStatus
        PCOPY 1, 0: CLS
        gamestats.paused = 1
        WHILE INKEY$ = "": WEND
        gamestats.paused = 0
    END IF
         
    
    CASE CHR$(27)
        Quit = True
        EXIT SUB
    
    END SELECT


#==============================================================================
#FUNCTION getDidNotClearJumpMsg
#Returns a random phrase to describe you not clearing the jump (this is rare,
#but it could happen)
#==============================================================================
def getDidNotClearJumpMsg():
    p = int(random.random() * len(rampCrashPhrases)) + 1
    return rampCrashPhrases[p]


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
#SUB Move
#==============================================================================
# TODO move this into a bike update function
def Move:
    FOR n = 1 TO NumRamps
        Ramp(n).x = Ramp(n).x - Biker.xvel
    NEXT n

    xAdd1 = Ramp(CurRamp).x + Ramp(CurRamp).dist
    #CIRCLE (xAdd1, StandardY - 10), 3, 3
  
    if InAir:
        y = y + Biker.yvel
        Biker.yvel = Biker.yvel + 2.1
    
        if not bike.tricking :
            Tzf = Tzf + 3: Tzh = Tzf
            #if (Tzf - 360) MOD 360 > 10 : message 5, "Lean Back!!!", 1
        END IF
    
        if Biker.yvel > 0 AND (BikePts2D(21).y > StandardY - 25 OR BarPts2D(17).y > StandardY - 25):
            DidNotClearRamp = (BikePts2D(3).x < xAdd1)
    
            y = StandardY - 30
            Biker.yvel = 0
    
            if bike.tricking OR DidNotClearRamp :
                CLS
                msg = "": MsgFrames = 0
                if bike.tricking :
                    message 12, getCrashedMsg(), 1
                else:
                    message 12, getDidNotClearJumpMsg(), 1
                END IF
    
                message 14, "Press <Enter> to continue.", 1
                bike.crashed = True
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
                bike.draw()
                PCOPY 1, 0: CLS
                WHILE INKEY$ <> CHR$(13): WEND
                Biker.xvel = 0
                EXIT SUB
            END IF
    
            if not bike.crashed:
                CurRamp = CurRamp + 1
    
            InAir = 0
            gamestats.score = gamestats.score + AddScore
            NumTricks = 0
            AddScore = 0
            Tzf = 0
            Tzh = 0
            one = 15        #Tab stops
    
            if CurRamp > NumRamps:
                CALL RotateBike(Txf, Tyf + 180, Tzf)
                CALL RotateBar(Txh, Tyh + 180, Tzh)
                DrawLevel
                bike.draw()
                DrawStatus
                message 14, "Press <Enter> to continue.", 1
    
                if gamestats.score >= ScoreToBeat(Level) :
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
#SUB RunSummary
#==============================================================================
# TODO this goes into the playing state, at the end of a run (when you finish a level (and maybe also when you crash?)
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
        PRINT TAB(3); "Total: "; TAB(10); LTRIM$(STR$(gamestats.score)); " pts.";
        PRINT TAB(30); "<I and K> scroll, <Enter> continues."
        PRINT STRING$(80, "-")
        
        message 23, "Press <Enter> to continue.", 1
        bike.draw()
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




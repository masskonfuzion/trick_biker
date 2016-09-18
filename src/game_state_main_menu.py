# System-level imports
import pygame
import sys
import os

# pymkfgame imports
from pymkfgame.core import game_state_base 

from pymkfgame.display_msg.display_msg import DisplayMessage
from pymkfgame.display_msg.display_msg_manager import DisplayMessageManager

from pymkfgame.ui import menu_form
from pymkfgame.ui import menu_item_label
from pymkfgame.core.message_queue import MessageQueue

# local imports
# TODO include the modules of any game state to be reached from the main menu



###==============================================================================
###SUB MainMenu
###This is a misnomer--it's actually the game's main menu
###==============================================================================
##def MainMenu()      #Also the Game Menu:
##ComeHere:
##    # Select a random bike style for the main menu demo
##    style = int(random.random() * 10) + 1
##    RESTORE BikeColorData       # TODO make into a python list
##    FOR n = 1 TO style
##        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
##    NEXT n
##    
##    
##    flag = 1                    # TODO possibly rename flag. It is actually the selected menu item
##    Scale = 175
##    
##    Txf = 0: Tyf = 0: Tzf = 0
##    Txh = 0: Tyh = 0: Tzh = 0
##    
##    DO  # TODO I guess change this into a while True loop?
##        for demo in range(0, 7):
##            x = 440     # NOTE: x, and y are global vars meant to hold the bike position. Replace with properties of the Bike class
##            y = 200
##            yi = -20    # yi is a y-pos increment (this approximates gravity) TODO: replace with physics-based gravity
##            for ang in range(0, 360 + 1, 15):
##                x = x - 11
##                y = y + yi: yi = yi + 1.6
##                
##                if demo == 0:           #Corkscrew (like anyone can really do this)
##                    Txf = ang
##                    Txh = ang
##                elif demo == 1:         #Horizontal 360
##                    Tyf = ang
##                    Tyh = ang
##                elif demo == 2:         #Flip
##                    Tzf = ang
##                    Tzh = ang
##                elif demo == 3:         #Flair
##                    Txf = ang
##                    Tyf = ang
##                    Txh = ang
##                    Tyh = ang
##                elif demo == 4:         #Tailwhip
##                    Tyf = ang
##                elif demo == 5:         #BarSpin
##                    Tyh = 2 * ang
##                elif demo == 6:         #Tabletop
##                    if ang <= 90:
##                        Txf = ang
##                        Txh = ang
##                    if ang >= 270:
##                        Txf = 360 - ang
##                        Txh = 360 - ang
##                
##                #PRINT "Cycle: "; demo
##                
##                
##                #==================
##                #     Do Game Menu
##                #==================
##                # TODO replace with a pygame menu -- use your menu class from falldown x64
##                message 1, STRING$(80, "-"), 1
##                message 2, "Trick Biker!!!", 1
##                message 3, STRING$(80, "-"), 1
##                message 4, "<I> and <K> navigate this menu, <Esc> quits.", 1
##                message 6, "Instructions", 1
##                message 10, "Start Game", 1
##                message 14, "Options", 1
##                message 18, "Creditz", 1
##                message 20, STRING$(80, "-"), 1
##                message 21, "By Lou Herard - (C) 2000 by Y2K Compliant Software", 1
##                message 22, STRING$(80, "-"), 1
##                
##                flagY = (flag * 4 * 14) + 14
##                LINE (200, flagY)-(440, flagY + 14), 4, B
##                
##                a$ = INKEY$
##                SELECT CASE UCASE$(a$)
##                    CASE "K"
##                        flag = flag + 1
##                        if flag > 4:
##                            flag = 1
##                    CASE "I"
##                        flag = flag - 1
##                        if flag < 1:
##                            flag = 4
##                    CASE CHR$(27)
##                        END
##                    CASE CHR$(13)
##                        SELECT CASE flag
##                            CASE 1
##                                CALL Instructions
##                                CLS
##                            CASE 2
##                                CALL SelectBike
##                                if Quit:
##                                    Quit = False
##                                    CLS
##                                    GOTO ComeHere
##                                END IF
##                                EXIT SUB
##                            CASE 3
##                                CALL OptionsMenu
##                                CLS
##                            CASE 4
##                                CALL Creditz
##                                CLS
##                        END SELECT
##                END SELECT
##                
##                #-------
##                #Rotate and Translate Points
##                #-------
##                
##                CALL RotateBike(Txf, Tyf, Tzf)
##                CALL RotateBar(Txh, Tyh, Tzh)
##                bike.draw()
##                
##                
##                PCOPY 1, 0: CLS         ## TODO: replace PCOPY calls with pygame buffer swap calls
##        NEXT demo
##    LOOP
##END SUB



class GameStateImpl(game_state_base.GameStateBase):
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
            GameStateImpl.__instance.SetName("MainMenu")
            #print "GAMESTATE Playing State creating __instance object {}".format(GameStateImpl.__instance)

        #print "GAMESTATE Playing State getting __instance {}".format(GameStateImpl.__instance)
        return GameStateImpl.__instance

    def Init(self, appRef, takeWith=None):
        # NOTE Here, the font path MUST be relative to the game executable's path. The display_msg_manager will handle all the path math to find the correct file
        self.appRef = appRef        # Get a reference to the application object, so we can access, e.g., render surfaces, etc.

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        self.dm = DisplayMessage()   # Create a message we intend to keep static
        self.dm.create(txtStr="Da Bike Game")
        #font = pygame.font.Font( 'game_font_7.ttf', 24 )

        self.dmm = DisplayMessageManager( fontPath=os.path.normpath('/'.join((os.path.dirname(sys.argv[0]), 'game_font_7.ttf'))), fontSize=20 )	# TODO!! Move fonts and stuff into proper dev directory
        self.dmm.setMessage("This message will self-destruct", [0, 100], (192, 192, 192), 5)

        # Create a simple menu
        self.ui = menu_form.UIForm()
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([20,200], self.dmm._font, "Some menu stuff"), kbSelectIdx=0, action=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([20,230], self.dmm._font, "More menu stuff"), kbSelectIdx=1, action=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([20,260], self.dmm._font, "Switch to State B"), kbSelectIdx=2, action="SwitchToB")
        self.ui.synchronize(0,2)

    def Cleanup(self):
        pass

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        pass

    def EnqueueApplicationQuitMessage(self):
        """Enqueue a message for the application to shut itself down
        """
        self._eventQueue.Enqueue( { 'topic': 'Application',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'setRunningFlagToFalse'
                                               , 'params' : ''
                                               }
                                  } )

    def ProcessEvents(self):
    # process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                action = self.ui.processKeyboardEvent(event, None)   # NOTE: action is unused in this demo; but we need to run processKeyboardEvents, so we store the result in action

                # TODO set up state transitions
                #if action == "SwitchToB":
                #    self.appRef.changeState( state_b.GameStateImpl.Instance() )

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

            msg = self._eventQueue.Dequeue()

    def Update(self, dt_s):
        # -- Update
        # Call update() on the display_msg_manager. Without calling update, the message manager will not be able to time how long to leave a message on-screen
        self.dmm.update(dt_s, None)  # Note: dmm.draw, for some reason, takes in a game stats object (Falldown artifact) but it appears to not be used anywhere
        self.ui.update(dt_s)

    def PreRenderScene(self):
        pass

    def RenderScene(self):
        self.appRef.surface_bg.fill(self.appRef.bg_col)
        # draw
        # NOTE - the DisplayMessage class has a ttl attribute that we're not using in this demo; but games/interactive software will use it
        textSurf = self.dm.getTextSurface(self.dmm._font)
        if textSurf:
            self.appRef.surface_bg.blit( textSurf, (self.dm._position[0], self.dm._position[1]) )

        self.dmm.draw(self.appRef.surface_bg)
        self.ui.render(self.appRef.surface_bg)   # TODO change function from render to draw? (or draw to render)?

    def PostRenderScene(self):
        #self.displayMessages()     # NOTE: These functions can give you an idea of what we'll do in our PostRenderScene()
        #self.displayGameStats()

        pygame.display.flip()

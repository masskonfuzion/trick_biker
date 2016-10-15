#==============================================================================
#SUB Instructions
#==============================================================================
def Instructions():
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





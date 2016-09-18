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
        
        bike.draw()
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

